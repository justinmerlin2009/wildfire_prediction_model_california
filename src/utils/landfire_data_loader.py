"""
Data loading and processing utilities for LANDFIRE 2024 Forest Canopy Cover (CC).

Handles the CONUS-wide LANDFIRE CC raster:
  - Clips to California using a state boundary polygon
  - Reprojects from EPSG:5070 (NAD83/Conus Albers) to EPSG:3310 (CA Albers)
  - Provides downsampled visualization at ~810m
  - Extracts CC values at fire points and within fire perimeters

Temporal caveat: LANDFIRE CC 2024 is a snapshot incorporating 2015-2024
disturbances. Historical fires (pre-2015) occurred under different canopy
conditions.
"""
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask as rasterio_mask
from rasterio.transform import from_bounds
from rasterio.warp import calculate_default_transform, reproject
from pathlib import Path

from .constants import (
    LANDFIRE_CC_PATH, LANDFIRE_CC_NODATA, LANDFIRE_CC_RESOLUTION_M,
    LANDFIRE_CC_VIZ_DOWNSAMPLE, CRS_CONUS_ALBERS, CRS_ALBERS,
    CA_BOUNDARY_PATH, GRID_RESOLUTION_M,
)
from .landfire_domain_mappings import (
    CC_VALUE_MAP, CC_MIDPOINT_MAP, CC_ORDERED_VALUES,
    CC_BROAD_CATEGORIES, get_cc_label, get_cc_broad_category,
)


# ── Metadata ──────────────────────────────────────────────────────────

def load_landfire_cc_metadata(path=None):
    """
    Load LANDFIRE CC raster metadata without reading pixel data.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoTIFF. Defaults to LANDFIRE_CC_PATH.

    Returns
    -------
    dict
        Raster metadata: crs, shape, resolution, bounds, nodata, transform, dtype.
    """
    if path is None:
        path = LANDFIRE_CC_PATH
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"LANDFIRE CC raster not found: {path}")

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


# ── CONUS → California Clip ─────────────────────────────────────────

def clip_cc_to_california(path=None, ca_boundary_path=None, buffer_m=5000):
    """
    Clip CONUS-wide LANDFIRE CC raster to California extent.

    Memory-efficient: uses rasterio.mask.mask which performs a windowed read
    rather than loading the entire CONUS raster.

    Parameters
    ----------
    path : str or Path, optional
        Path to CONUS GeoTIFF. Defaults to LANDFIRE_CC_PATH.
    ca_boundary_path : str or Path, optional
        Path to California state boundary (GeoPackage). Defaults to CA_BOUNDARY_PATH.
    buffer_m : float, default 5000
        Buffer around CA boundary in meters (to avoid edge clipping).

    Returns
    -------
    tuple (cc_array, transform, crs)
        cc_array : numpy.ndarray (int16)
            Clipped CC values in native CRS (EPSG:5070).
        transform : Affine
            Transform for the clipped raster.
        crs : str
            CRS string (EPSG:5070).
    """
    import geopandas as gpd

    if path is None:
        path = LANDFIRE_CC_PATH
    if ca_boundary_path is None:
        ca_boundary_path = CA_BOUNDARY_PATH

    path = Path(path)
    ca_boundary_path = Path(ca_boundary_path)

    # Load CA boundary and reproject to LANDFIRE CRS (EPSG:5070)
    ca_gdf = gpd.read_file(ca_boundary_path)
    ca_gdf = ca_gdf.to_crs(CRS_CONUS_ALBERS)

    # Buffer to avoid edge effects
    if buffer_m > 0:
        ca_gdf["geometry"] = ca_gdf.geometry.buffer(buffer_m)

    shapes = ca_gdf.geometry.values

    with rasterio.open(path) as src:
        cc_array, out_transform = rasterio_mask(
            src, shapes, crop=True, nodata=LANDFIRE_CC_NODATA,
            filled=True
        )
        # mask returns (bands, height, width) — squeeze to 2D
        cc_array = cc_array[0].astype(np.int16)
        crs = str(src.crs)

    return cc_array, out_transform, crs


# ── Reprojection ─────────────────────────────────────────────────────

def reproject_cc_to_albers(cc_array, src_transform, src_crs=None):
    """
    Reproject clipped CC array from EPSG:5070 to EPSG:3310.

    Uses nearest-neighbor resampling (categorical data — no interpolation).

    Parameters
    ----------
    cc_array : numpy.ndarray (int16)
        2D CC array in source CRS.
    src_transform : Affine
        Transform for the source array.
    src_crs : str, optional
        Source CRS. Defaults to CRS_CONUS_ALBERS (EPSG:5070).

    Returns
    -------
    tuple (dst_array, dst_transform)
        dst_array : numpy.ndarray (int16)
            Reprojected CC array in EPSG:3310.
        dst_transform : Affine
            Transform for the reprojected raster.
    """
    if src_crs is None:
        src_crs = CRS_CONUS_ALBERS

    h, w = cc_array.shape
    dst_transform, dst_width, dst_height = calculate_default_transform(
        src_crs, CRS_ALBERS, w, h,
        left=src_transform[2],
        bottom=src_transform[5] + src_transform[4] * h,
        right=src_transform[2] + src_transform[0] * w,
        top=src_transform[5],
    )

    dst_array = np.full((dst_height, dst_width), LANDFIRE_CC_NODATA, dtype=np.int16)

    reproject(
        source=cc_array,
        destination=dst_array,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=CRS_ALBERS,
        resampling=Resampling.nearest,
        src_nodata=LANDFIRE_CC_NODATA,
        dst_nodata=LANDFIRE_CC_NODATA,
    )

    return dst_array, dst_transform


# ── Convenience Loader ──────────────────────────────────────────────

def load_cc_california(path=None, ca_boundary_path=None):
    """
    Load LANDFIRE CC clipped to California and reprojected to EPSG:3310.

    Combines clip_cc_to_california + reproject_cc_to_albers.
    Replaces NoData sentinels (-9999, 32767) with a single -9999 value.

    Parameters
    ----------
    path : str or Path, optional
        Path to CONUS GeoTIFF. Defaults to LANDFIRE_CC_PATH.
    ca_boundary_path : str or Path, optional
        Path to CA boundary. Defaults to CA_BOUNDARY_PATH.

    Returns
    -------
    tuple (cc_array, transform, metadata)
        cc_array : numpy.ndarray (int16)
            CC values in EPSG:3310, -9999 for NoData.
        transform : Affine
            Raster transform.
        metadata : dict
            Processing metadata.
    """
    print("Clipping CONUS raster to California...")
    cc_clipped, clip_transform, clip_crs = clip_cc_to_california(
        path, ca_boundary_path
    )
    print(f"  Clipped shape: {cc_clipped.shape}")

    print("Reprojecting EPSG:5070 → EPSG:3310...")
    cc_albers, albers_transform = reproject_cc_to_albers(
        cc_clipped, clip_transform, clip_crs
    )
    print(f"  Reprojected shape: {cc_albers.shape}")

    # Unify NoData values (32767 sometimes appears from reprojection)
    cc_albers[(cc_albers == 32767) | (cc_albers < -9999)] = LANDFIRE_CC_NODATA

    # Free clipped array
    del cc_clipped

    metadata = {
        "crs": CRS_ALBERS,
        "shape": cc_albers.shape,
        "transform": albers_transform,
        "nodata": LANDFIRE_CC_NODATA,
        "resolution_m": abs(albers_transform[0]),
    }

    return cc_albers, albers_transform, metadata


# ── Downsampled Visualization ────────────────────────────────────────

def load_cc_downsampled(cc_array, transform, factor=None):
    """
    Downsample CC array for visualization.

    Uses nearest-neighbor resampling (categorical data).

    Parameters
    ----------
    cc_array : numpy.ndarray
        Full-resolution CC array.
    transform : Affine
        Raster transform.
    factor : int, optional
        Downsample factor. Defaults to LANDFIRE_CC_VIZ_DOWNSAMPLE (27).

    Returns
    -------
    tuple (cc_ds, transform_ds, metadata)
        cc_ds : numpy.ndarray (float32)
            Downsampled array with NoData as NaN.
        transform_ds : Affine
            Transform for the downsampled raster.
        metadata : dict
            Shape and resolution info.
    """
    if factor is None:
        factor = LANDFIRE_CC_VIZ_DOWNSAMPLE

    h, w = cc_array.shape
    out_h = h // factor
    out_w = w // factor

    # Slice to exact multiple of factor for clean downsampling
    trimmed = cc_array[:out_h * factor, :out_w * factor]

    # Reshape and take element at [0,0] of each block (nearest)
    cc_ds = trimmed.reshape(out_h, factor, out_w, factor)[:, 0, :, 0]
    cc_ds = cc_ds.astype(np.float32)

    # Replace NoData with NaN
    cc_ds[cc_ds == LANDFIRE_CC_NODATA] = np.nan

    # Bounds from original transform
    left = transform[2]
    top = transform[5]
    right = left + w * abs(transform[0])
    bottom = top + h * transform[4]  # transform[4] is negative

    transform_ds = from_bounds(left, bottom, right, top, out_w, out_h)

    metadata = {
        "original_shape": (h, w),
        "downsampled_shape": (out_h, out_w),
        "downsample_factor": factor,
        "effective_resolution_m": abs(transform[0]) * factor,
        "crs": CRS_ALBERS,
    }

    return cc_ds, transform_ds, metadata


# ── Fire Overlay Extraction ──────────────────────────────────────────

def extract_cc_at_points(cc_array, transform, points_gdf, crs=None):
    """
    Sample CC values at point locations (e.g., MTBS centroids, FPA FOD points).

    Parameters
    ----------
    cc_array : numpy.ndarray
        2D CC array.
    transform : Affine
        Raster transform.
    points_gdf : GeoDataFrame
        Point geometries.
    crs : str, optional
        CRS of the raster. If provided and different from points_gdf, reprojects.

    Returns
    -------
    numpy.ndarray
        CC values at each point (NaN if outside raster or NoData).
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

    h, w = cc_array.shape
    valid = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)

    values = np.full(len(points_gdf), np.nan)
    sampled = cc_array[rows[valid], cols[valid]].astype(np.float64)
    sampled[sampled == LANDFIRE_CC_NODATA] = np.nan
    values[valid] = sampled

    return values


def extract_cc_for_polygons(cc_array, transform, polygons_gdf, crs=None):
    """
    Extract CC statistics for polygon geometries (e.g., CAL FIRE perimeters).

    Parameters
    ----------
    cc_array : numpy.ndarray
        2D CC array.
    transform : Affine
        Raster transform.
    polygons_gdf : GeoDataFrame
        Polygon geometries.
    crs : str, optional
        CRS of the raster.

    Returns
    -------
    dict of numpy.ndarray
        Keys: 'mean_cc_pct', 'dominant_cc', 'forested_fraction', 'pixel_count'.
    """
    from rasterio.features import geometry_mask

    if crs is not None and polygons_gdf.crs and str(polygons_gdf.crs) != crs:
        polygons_gdf = polygons_gdf.to_crs(crs)

    h, w = cc_array.shape
    n = len(polygons_gdf)
    mean_cc = np.full(n, np.nan)
    dominant = np.full(n, np.nan)
    forested_frac = np.full(n, np.nan)
    pixel_count = np.zeros(n, dtype=int)

    for i, geom in enumerate(polygons_gdf.geometry):
        if geom is None or geom.is_empty:
            continue
        try:
            gmask = geometry_mask(
                [geom], out_shape=(h, w), transform=transform, invert=True
            )
            vals = cc_array[gmask]
            # Remove NoData
            vals = vals[vals != LANDFIRE_CC_NODATA]
            if len(vals) == 0:
                continue

            pixel_count[i] = len(vals)

            # Convert to midpoint percentages for mean
            midpoints = np.array([CC_MIDPOINT_MAP.get(v, np.nan) for v in vals],
                                 dtype=np.float64)
            valid_mid = midpoints[~np.isnan(midpoints)]
            if len(valid_mid) > 0:
                mean_cc[i] = np.mean(valid_mid)

            # Dominant class (mode)
            unique, counts = np.unique(vals, return_counts=True)
            dominant[i] = unique[np.argmax(counts)]

            # Forested fraction (CC > 0)
            forested_frac[i] = np.sum(vals > 0) / len(vals)

        except Exception:
            continue

    return {
        "mean_cc_pct": mean_cc,
        "dominant_cc": dominant,
        "forested_fraction": forested_frac,
        "pixel_count": pixel_count,
    }


# ── Class Distribution ───────────────────────────────────────────────

def get_cc_class_distribution(cc_array, resolution_m=None):
    """
    Count pixels per CC class and compute area.

    Parameters
    ----------
    cc_array : numpy.ndarray
        2D CC array.
    resolution_m : float, optional
        Pixel size in meters. Defaults to LANDFIRE_CC_RESOLUTION_M.

    Returns
    -------
    pandas.DataFrame
        Columns: value, label, broad_category, pixel_count, area_km2, pct_of_valid.
    """
    if resolution_m is None:
        resolution_m = LANDFIRE_CC_RESOLUTION_M

    pixel_area_km2 = (resolution_m ** 2) / 1e6

    # Count all values
    unique, counts = np.unique(cc_array, return_counts=True)
    count_dict = dict(zip(unique, counts))

    # Build DataFrame for valid CC values only
    rows = []
    for v in CC_ORDERED_VALUES:
        c = count_dict.get(v, 0)
        rows.append({
            "value": v,
            "label": get_cc_label(v),
            "broad_category": get_cc_broad_category(v),
            "pixel_count": c,
            "area_km2": c * pixel_area_km2,
        })

    df = pd.DataFrame(rows)
    total_valid = df["pixel_count"].sum()
    df["pct_of_valid"] = 100.0 * df["pixel_count"] / total_valid if total_valid > 0 else 0.0

    # Add NoData count as metadata
    nodata_count = count_dict.get(LANDFIRE_CC_NODATA, 0)
    df.attrs["nodata_count"] = nodata_count
    df.attrs["total_pixels"] = cc_array.size

    return df


# ── Data Quality ─────────────────────────────────────────────────────

def get_cc_data_quality_summary(cc_array):
    """
    Generate quality summary for CC data.

    Parameters
    ----------
    cc_array : numpy.ndarray
        CC array.

    Returns
    -------
    dict
        Quality metrics.
    """
    total = cc_array.size
    nodata = np.sum(cc_array == LANDFIRE_CC_NODATA)
    valid = total - nodata
    valid_vals = cc_array[(cc_array != LANDFIRE_CC_NODATA)]

    forested = np.sum(valid_vals > 0)
    non_forested = np.sum(valid_vals == 0)

    unique_vals = np.unique(valid_vals)

    return {
        "Total pixels": f"{total:,}",
        "Valid pixels": f"{valid:,} ({100 * valid / total:.1f}%)",
        "NoData pixels": f"{nodata:,} ({100 * nodata / total:.1f}%)",
        "Non-Forested pixels": f"{non_forested:,} ({100 * non_forested / valid:.1f}%)",
        "Forested pixels": f"{forested:,} ({100 * forested / valid:.1f}%)",
        "Unique CC values": str(sorted(unique_vals.tolist())),
    }
