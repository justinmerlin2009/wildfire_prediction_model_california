"""
Data loading and processing utilities for topographic analysis.

Handles the 3 GB USGS NED DEM (37,312 x 42,463 px, int16, EPSG:3310)
with memory-efficient downsampled reads for visualization and full-resolution
800m aggregation for ML grid creation.
"""
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.warp import reproject
from scipy.ndimage import uniform_filter
from pathlib import Path

from .constants import (
    TOPOGRAPHY_PATH, TOPO_NODATA, TOPO_NATIVE_RES_M,
    TOPO_VIZ_DOWNSAMPLE, TPI_WINDOW_RADIUS,
    GRID_RESOLUTION_M, CRS_ALBERS,
)


# ── Raster Loading ───────────────────────────────────────────────────────

def load_topography_metadata(path=None):
    """
    Load DEM metadata without reading pixel data.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoTIFF. Defaults to TOPOGRAPHY_PATH.

    Returns
    -------
    dict
        Raster metadata: crs, shape, resolution, bounds, nodata, transform, dtype.
    """
    if path is None:
        path = TOPOGRAPHY_PATH
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Topography raster not found: {path}")

    with rasterio.open(path) as src:
        return {
            "crs": str(src.crs),
            "height": src.height,
            "width": src.width,
            "resolution_m": src.res[0],
            "bounds": src.bounds,
            "nodata": src.nodata,
            "transform": src.transform,
            "dtype": src.dtypes[0],
            "file_size_gb": path.stat().st_size / (1024**3),
        }


def load_topography_downsampled(path=None, factor=None):
    """
    Load DEM at reduced resolution using decimated read.

    Uses rasterio's built-in decimation (out_shape) for memory-efficient
    downsampling without loading the full raster.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoTIFF. Defaults to TOPOGRAPHY_PATH.
    factor : int, optional
        Downsample factor. Defaults to TOPO_VIZ_DOWNSAMPLE (30).

    Returns
    -------
    tuple (elevation, transform, metadata)
        elevation : numpy.ndarray (float32)
            Downsampled elevation with nodata replaced by NaN.
        transform : Affine
            Transform for the downsampled raster.
        metadata : dict
            Original and downsampled shape info.
    """
    if path is None:
        path = TOPOGRAPHY_PATH
    if factor is None:
        factor = TOPO_VIZ_DOWNSAMPLE

    path = Path(path)
    with rasterio.open(path) as src:
        out_height = src.height // factor
        out_width = src.width // factor

        elevation = src.read(
            1,
            out_shape=(out_height, out_width),
            resampling=Resampling.average,
        ).astype(np.float32)

        # Compute transform for downsampled grid
        transform = from_bounds(
            *src.bounds, out_width, out_height
        )

        # Replace nodata with NaN
        nodata = src.nodata if src.nodata is not None else TOPO_NODATA
        elevation[elevation == nodata] = np.nan

        metadata = {
            "original_shape": (src.height, src.width),
            "downsampled_shape": (out_height, out_width),
            "downsample_factor": factor,
            "effective_resolution_m": src.res[0] * factor,
            "crs": str(src.crs),
            "bounds": src.bounds,
        }

    return elevation, transform, metadata


def load_topography_window(path=None, bounds=None, window=None):
    """
    Load a spatial subset of the DEM.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoTIFF. Defaults to TOPOGRAPHY_PATH.
    bounds : tuple, optional
        (left, bottom, right, top) in raster CRS.
    window : rasterio.windows.Window, optional
        Pixel window to read. Overrides bounds.

    Returns
    -------
    tuple (elevation, transform)
    """
    if path is None:
        path = TOPOGRAPHY_PATH

    with rasterio.open(path) as src:
        if window is None and bounds is not None:
            window = rasterio.windows.from_bounds(*bounds, src.transform)

        elevation = src.read(1, window=window).astype(np.float32)
        transform = src.window_transform(window)

        nodata = src.nodata if src.nodata is not None else TOPO_NODATA
        elevation[elevation == nodata] = np.nan

    return elevation, transform


# ── Terrain Derivatives ──────────────────────────────────────────────────

def compute_slope_aspect(elevation, transform):
    """
    Compute slope (degrees) and aspect (degrees, 0=N clockwise) from elevation.

    Uses numpy gradient for efficient computation on the downsampled array.

    Parameters
    ----------
    elevation : numpy.ndarray
        2D elevation array (NaN for nodata).
    transform : Affine
        Raster transform for pixel size.

    Returns
    -------
    tuple (slope_deg, aspect_deg)
        slope_deg : numpy.ndarray, slope in degrees (0-90)
        aspect_deg : numpy.ndarray, aspect in degrees (0=N, CW, 0-360)
    """
    cell_size_x = abs(transform[0])
    cell_size_y = abs(transform[4])

    # Replace NaN with local mean for gradient computation at edges
    filled = elevation.copy()
    mask = np.isnan(filled)
    if mask.any():
        filled[mask] = np.nanmean(elevation)

    # Compute gradients (dy is negative because row index increases downward)
    dy, dx = np.gradient(filled, cell_size_y, cell_size_x)

    # Slope in degrees
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)

    # Aspect: 0=North, clockwise
    # np.arctan2(-dy, dx) gives angle from East, CCW
    # Convert to geographic: North=0, CW
    aspect_rad = np.arctan2(-dy, dx)
    aspect_deg = (90.0 - np.degrees(aspect_rad)) % 360.0

    # Apply nodata mask
    slope_deg[mask] = np.nan
    aspect_deg[mask] = np.nan

    return slope_deg, aspect_deg


def compute_tpi(elevation, radius_px=None):
    """
    Compute Topographic Position Index (TPI).

    TPI = elevation - mean(neighborhood elevation)
    Positive = ridges/hilltops, Negative = valleys/depressions.

    Parameters
    ----------
    elevation : numpy.ndarray
        2D elevation array.
    radius_px : int, optional
        Neighborhood radius in pixels. Defaults to TPI_WINDOW_RADIUS.

    Returns
    -------
    numpy.ndarray
        TPI values (positive = ridge, negative = valley).
    """
    if radius_px is None:
        radius_px = TPI_WINDOW_RADIUS

    window_size = 2 * radius_px + 1
    mask = np.isnan(elevation)

    # Fill NaN for filter
    filled = elevation.copy()
    filled[mask] = np.nanmean(elevation)

    neighborhood_mean = uniform_filter(filled, size=window_size, mode="nearest")
    tpi = elevation - neighborhood_mean
    tpi[mask] = np.nan

    return tpi


def compute_twi(slope_deg, cell_size_m):
    """
    Compute simplified Topographic Wetness Index (slope-only approximation).

    TWI = ln(a / tan(beta)) where a = upslope contributing area per unit contour.
    Simplified: uses cell area / tan(slope), since true flow accumulation requires
    full-resolution hydrological routing.

    Parameters
    ----------
    slope_deg : numpy.ndarray
        Slope in degrees.
    cell_size_m : float
        Cell size in meters.

    Returns
    -------
    numpy.ndarray
        Simplified TWI values. Higher = wetter/flatter.
    """
    slope_rad = np.radians(np.clip(slope_deg, 0.1, 89.9))  # Avoid log(0)
    cell_area = cell_size_m ** 2
    # Approximate contributing area as cell area (single-cell approximation)
    twi = np.log(cell_area / np.tan(slope_rad))
    twi[np.isnan(slope_deg)] = np.nan
    return twi


def compute_heat_load_index(slope_deg, aspect_deg):
    """
    Compute Heat Load Index (McCune & Keon, 2002).

    Transforms aspect into a continuous heat-loading index where
    SW-facing slopes (warmest/driest in Northern Hemisphere) receive
    the highest values.

    HLI = 0.339 + 0.808 * cos(L) * cos(S)
        - 0.196 * sin(L) * sin(S)
        - 0.482 * cos(A_folded) * sin(S)

    Simplified version using California's central latitude (~37 deg N):
    cos(A_folded) where A_folded = |180 - |aspect - 225||

    Parameters
    ----------
    slope_deg : numpy.ndarray
        Slope in degrees.
    aspect_deg : numpy.ndarray
        Aspect in degrees (0=N, CW).

    Returns
    -------
    numpy.ndarray
        HLI values (0-1, higher = hotter/drier).
    """
    # Use central California latitude (37 deg N)
    lat_rad = np.radians(37.0)
    slope_rad = np.radians(slope_deg)

    # Fold aspect so that 225 deg (SW) = 0 (warmest)
    aspect_folded = np.abs(180.0 - np.abs(aspect_deg - 225.0))
    aspect_folded_rad = np.radians(aspect_folded)

    hli = (
        0.339
        + 0.808 * np.cos(lat_rad) * np.cos(slope_rad)
        - 0.196 * np.sin(lat_rad) * np.sin(slope_rad)
        - 0.482 * np.cos(aspect_folded_rad) * np.sin(slope_rad)
    )

    hli = np.clip(hli, 0, 1)
    hli[np.isnan(slope_deg)] = np.nan
    return hli


# ── Aggregation ──────────────────────────────────────────────────────────

def aggregate_to_grid(path=None, target_res_m=None):
    """
    Aggregate DEM to target resolution (e.g., 800m) using rasterio reproject.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoTIFF. Defaults to TOPOGRAPHY_PATH.
    target_res_m : float, optional
        Target resolution in meters. Defaults to GRID_RESOLUTION_M (800).

    Returns
    -------
    tuple (elevation_800m, transform_800m, shape)
        elevation_800m : numpy.ndarray (float32)
        transform_800m : Affine
        shape : tuple (height, width)
    """
    if path is None:
        path = TOPOGRAPHY_PATH
    if target_res_m is None:
        target_res_m = GRID_RESOLUTION_M

    with rasterio.open(path) as src:
        bounds = src.bounds
        out_width = int((bounds.right - bounds.left) / target_res_m)
        out_height = int((bounds.top - bounds.bottom) / target_res_m)

        dst_transform = from_bounds(
            bounds.left, bounds.bottom, bounds.right, bounds.top,
            out_width, out_height,
        )

        dst_elevation = np.empty((out_height, out_width), dtype=np.float32)

        reproject(
            source=rasterio.band(src, 1),
            destination=dst_elevation,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=dst_transform,
            dst_crs=src.crs,
            resampling=Resampling.average,
            src_nodata=src.nodata,
            dst_nodata=np.nan,
        )

    return dst_elevation, dst_transform, (out_height, out_width)


# ── Fire Overlay Extraction ─────────────────────────────────────────────

def extract_terrain_at_points(elevation, transform, points_gdf, crs=None):
    """
    Sample terrain values at point locations (e.g., MTBS centroids).

    Parameters
    ----------
    elevation : numpy.ndarray
        2D elevation array.
    transform : Affine
        Raster transform.
    points_gdf : GeoDataFrame
        Point geometries (must be in same CRS as raster).
    crs : str, optional
        CRS of the raster. If provided and different from points_gdf, reprojects points.

    Returns
    -------
    numpy.ndarray
        Elevation values at each point (NaN if outside raster).
    """
    if crs is not None and points_gdf.crs and str(points_gdf.crs) != crs:
        points_gdf = points_gdf.to_crs(crs)

    rows, cols = rasterio.transform.rowcol(
        transform,
        points_gdf.geometry.x.values,
        points_gdf.geometry.y.values,
    )
    rows = np.asarray(rows)
    cols = np.asarray(cols)

    h, w = elevation.shape
    valid = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)

    values = np.full(len(points_gdf), np.nan)
    values[valid] = elevation[rows[valid], cols[valid]]

    return values


def extract_terrain_for_polygons(elevation, transform, polygons_gdf, crs=None):
    """
    Extract terrain statistics for polygon geometries (e.g., CAL FIRE perimeters).

    Uses rasterized polygon masks at the raster resolution.

    Parameters
    ----------
    elevation : numpy.ndarray
        2D elevation array.
    transform : Affine
        Raster transform.
    polygons_gdf : GeoDataFrame
        Polygon geometries.
    crs : str, optional
        CRS of the raster.

    Returns
    -------
    dict of numpy.ndarray
        Keys: 'mean_elevation', 'median_elevation', 'std_elevation',
              'min_elevation', 'max_elevation'.
    """
    from rasterio.features import geometry_mask

    if crs is not None and polygons_gdf.crs and str(polygons_gdf.crs) != crs:
        polygons_gdf = polygons_gdf.to_crs(crs)

    h, w = elevation.shape
    means = np.full(len(polygons_gdf), np.nan)
    medians = np.full(len(polygons_gdf), np.nan)
    stds = np.full(len(polygons_gdf), np.nan)
    mins = np.full(len(polygons_gdf), np.nan)
    maxs = np.full(len(polygons_gdf), np.nan)

    for i, geom in enumerate(polygons_gdf.geometry):
        if geom is None or geom.is_empty:
            continue
        try:
            mask = geometry_mask(
                [geom], out_shape=(h, w), transform=transform, invert=True
            )
            vals = elevation[mask & ~np.isnan(elevation)]
            if len(vals) > 0:
                means[i] = np.mean(vals)
                medians[i] = np.median(vals)
                stds[i] = np.std(vals)
                mins[i] = np.min(vals)
                maxs[i] = np.max(vals)
        except Exception:
            continue

    return {
        "mean_elevation": means,
        "median_elevation": medians,
        "std_elevation": stds,
        "min_elevation": mins,
        "max_elevation": maxs,
    }


# ── Data Quality ─────────────────────────────────────────────────────────

def get_topo_data_quality_summary(elevation, nodata=None):
    """
    Generate quality summary for topographic data.

    Parameters
    ----------
    elevation : numpy.ndarray
        Elevation array (NaN for nodata).
    nodata : float, optional
        Nodata value (if not already NaN-masked).

    Returns
    -------
    dict
        Quality metrics.
    """
    total_pixels = elevation.size
    if nodata is not None:
        nan_count = np.sum(elevation == nodata) + np.sum(np.isnan(elevation))
    else:
        nan_count = np.sum(np.isnan(elevation))

    valid_count = total_pixels - nan_count
    valid = elevation[np.isfinite(elevation)]

    return {
        "Total pixels": f"{total_pixels:,}",
        "Valid pixels": f"{valid_count:,} ({100 * valid_count / total_pixels:.1f}%)",
        "NoData pixels": f"{nan_count:,} ({100 * nan_count / total_pixels:.1f}%)",
        "Min elevation (m)": f"{np.min(valid):.1f}",
        "Max elevation (m)": f"{np.max(valid):.1f}",
        "Mean elevation (m)": f"{np.mean(valid):.1f}",
        "Median elevation (m)": f"{np.median(valid):.1f}",
        "Std elevation (m)": f"{np.std(valid):.1f}",
    }
