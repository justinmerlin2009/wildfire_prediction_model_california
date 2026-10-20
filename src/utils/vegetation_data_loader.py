"""
Data loading and processing utilities for FVEG22 California vegetation raster.

Handles the 2.8 GB FRAP CWHR classification raster (39,623 x 38,094 px,
uint16, EPSG:3310) with memory-efficient chunked reads, downsampled
visualization, RAT (Raster Attribute Table) resolution, and fire overlay
extraction.

RAT Strategy:
  1. Load cached local RAT CSV (fveg22_local_rat.csv) — primary
  2. Load ImageServer RAT CSV (fveg22_rat.csv) — fallback reference
  3. Download from ArcGIS ImageServer — last resort
  4. Graceful degradation — raw value analysis only
"""
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from collections import Counter
from pathlib import Path
import warnings

from .constants import (
    FVEG22_PATH, FVEG22_NODATA, FVEG22_NATIVE_RES_M,
    FVEG22_VIZ_DOWNSAMPLE, FVEG22_RAT_CSV_PATH,
    CRS_ALBERS, GRID_RESOLUTION_M,
)
from .vegetation_domain_mappings import (
    WHRTYPE_MAP, WHRTYPE_TO_LIFEFORM, WHRTYPE_TO_WHR13,
    FIRE_PRONE_WHRTYPE, get_whrtype_name, get_lifeform, get_whr13_class,
)


# ── Path for the local VALUE → attributes mapping ────────────────────

_LOCAL_RAT_PATH = FVEG22_RAT_CSV_PATH.parent / "fveg22_local_rat.csv"


# ── Raster Metadata ──────────────────────────────────────────────────

def load_vegetation_metadata(path=None):
    """
    Load FVEG22 raster metadata without reading pixel data.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoTIFF. Defaults to FVEG22_PATH.

    Returns
    -------
    dict
        Raster metadata: crs, shape, resolution, bounds, nodata, transform, dtype.
    """
    if path is None:
        path = FVEG22_PATH
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"FVEG22 raster not found: {path}")

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


# ── Downsampled Visualization ────────────────────────────────────────

def load_vegetation_downsampled(path=None, factor=None):
    """
    Load FVEG22 at reduced resolution using decimated read.

    Uses nearest-neighbor resampling (categorical data — no interpolation).

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoTIFF. Defaults to FVEG22_PATH.
    factor : int, optional
        Downsample factor. Defaults to FVEG22_VIZ_DOWNSAMPLE (40).

    Returns
    -------
    tuple (values, transform, metadata)
        values : numpy.ndarray (float32)
            Downsampled values with NoData replaced by NaN.
        transform : Affine
            Transform for the downsampled raster.
        metadata : dict
            Original and downsampled shape info.
    """
    if path is None:
        path = FVEG22_PATH
    if factor is None:
        factor = FVEG22_VIZ_DOWNSAMPLE

    path = Path(path)
    with rasterio.open(path) as src:
        out_height = src.height // factor
        out_width = src.width // factor

        values = src.read(
            1,
            out_shape=(out_height, out_width),
            resampling=Resampling.nearest,
        ).astype(np.float32)

        transform = from_bounds(*src.bounds, out_width, out_height)

        nodata = src.nodata if src.nodata is not None else FVEG22_NODATA
        values[values == nodata] = np.nan

        metadata = {
            "original_shape": (src.height, src.width),
            "downsampled_shape": (out_height, out_width),
            "downsample_factor": factor,
            "effective_resolution_m": src.res[0] * factor,
            "crs": str(src.crs),
            "bounds": src.bounds,
        }

    return values, transform, metadata


# ── Windowed Read ─────────────────────────────────────────────────────

def load_vegetation_window(path=None, bounds=None, window=None):
    """
    Load a spatial subset of the FVEG22 raster.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoTIFF. Defaults to FVEG22_PATH.
    bounds : tuple, optional
        (left, bottom, right, top) in raster CRS.
    window : rasterio.windows.Window, optional
        Explicit pixel window.

    Returns
    -------
    tuple (values, transform)
        values : numpy.ndarray (uint16)
        transform : Affine
    """
    if path is None:
        path = FVEG22_PATH
    path = Path(path)

    with rasterio.open(path) as src:
        if window is None and bounds is not None:
            window = rasterio.windows.from_bounds(*bounds, src.transform)
        values = src.read(1, window=window)
        transform = src.window_transform(window)

    return values, transform


# ── Chunked Unique Value Scanner ─────────────────────────────────────

def get_unique_values_and_counts(path=None, chunk_rows=1024):
    """
    Scan raster for unique pixel values and their counts.

    Memory-efficient: reads in horizontal strips.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoTIFF. Defaults to FVEG22_PATH.
    chunk_rows : int, default 1024
        Number of rows per read chunk.

    Returns
    -------
    pandas.DataFrame
        Columns: VALUE, COUNT, sorted by COUNT descending.
    """
    if path is None:
        path = FVEG22_PATH
    path = Path(path)

    counter = Counter()
    with rasterio.open(path) as src:
        h, w = src.height, src.width
        nodata = src.nodata if src.nodata is not None else FVEG22_NODATA

        for row_start in range(0, h, chunk_rows):
            rows_to_read = min(chunk_rows, h - row_start)
            data = src.read(
                1, window=rasterio.windows.Window(0, row_start, w, rows_to_read)
            )
            valid = data[data != nodata]
            if len(valid) > 0:
                unique, counts = np.unique(valid, return_counts=True)
                for u, c in zip(unique, counts):
                    counter[int(u)] += int(c)

    df = pd.DataFrame(
        [(v, c) for v, c in counter.items()],
        columns=["VALUE", "COUNT"],
    ).sort_values("COUNT", ascending=False).reset_index(drop=True)

    return df


# ── RAT Loading ──────────────────────────────────────────────────────

def load_local_rat(path=None):
    """
    Load the local VALUE → CWHR attributes mapping CSV.

    This CSV maps the pixel values in the local GeoTIFF to WHRTYPE,
    WHRNAME, LIFEFORM, WHR13NAME, WHRALL, WHRSIZE, WHRDENSITY.

    Parameters
    ----------
    path : str or Path, optional
        Path to local RAT CSV. Defaults to fveg22_local_rat.csv.

    Returns
    -------
    pandas.DataFrame or None
        DataFrame with VALUE as index, or None if not found.
    """
    if path is None:
        path = _LOCAL_RAT_PATH
    path = Path(path)

    if not path.exists():
        return None

    df = pd.read_csv(path)
    if "VALUE" not in df.columns:
        return None

    return df.set_index("VALUE")


def load_imageserver_rat(path=None):
    """
    Load the ImageServer RAT CSV (reference only — different VALUE numbering).

    Useful for WHRTYPE reference tables even if VALUE mapping differs.

    Parameters
    ----------
    path : str or Path, optional
        Path to RAT CSV. Defaults to FVEG22_RAT_CSV_PATH.

    Returns
    -------
    pandas.DataFrame or None
        DataFrame or None if not found.
    """
    if path is None:
        path = FVEG22_RAT_CSV_PATH
    path = Path(path)

    if not path.exists():
        return None

    return pd.read_csv(path)


def download_rat_csv(dest_path=None):
    """
    Download RAT from ArcGIS ImageServer rasterAttributeTable endpoint.

    Parameters
    ----------
    dest_path : str or Path, optional
        Destination path. Defaults to FVEG22_RAT_CSV_PATH.

    Returns
    -------
    pandas.DataFrame or None
        Downloaded RAT DataFrame, or None on failure.
    """
    import json
    import urllib.request
    import csv

    if dest_path is None:
        dest_path = FVEG22_RAT_CSV_PATH
    dest_path = Path(dest_path)

    url = ("https://egis.fire.ca.gov/arcgis/rest/services/FRAP/fveg/"
           "ImageServer/rasterAttributeTable?f=json")

    try:
        print(f"Downloading RAT from ArcGIS ImageServer...")
        with urllib.request.urlopen(url, timeout=120) as response:
            data = json.loads(response.read())

        features = data.get("features", [])
        if not features:
            warnings.warn("No features in ImageServer RAT response")
            return None

        fields = [f["name"] for f in data.get("fields", [])]

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for feat in features:
                writer.writerow(feat["attributes"])

        print(f"Saved {len(features)} RAT entries to {dest_path}")
        return pd.read_csv(dest_path)

    except Exception as e:
        warnings.warn(f"Failed to download RAT: {e}")
        return None


def get_value_to_attributes(local_rat_path=None, imageserver_rat_path=None):
    """
    Get the VALUE → CWHR attributes mapping using cascade strategy.

    1. Load local RAT (fveg22_local_rat.csv) — primary
    2. Load ImageServer RAT (fveg22_rat.csv) — reference only
    3. Download ImageServer RAT — last resort reference

    Returns
    -------
    tuple (local_rat, ref_rat, rat_available)
        local_rat : pandas.DataFrame or None
            Local VALUE → attributes mapping (index = VALUE).
        ref_rat : pandas.DataFrame or None
            ImageServer reference RAT (different VALUE numbering).
        rat_available : bool
            True if local_rat is available for pixel value lookup.
    """
    # Try local RAT first
    local_rat = load_local_rat(local_rat_path)
    if local_rat is not None and len(local_rat) > 0:
        print(f"Loaded local RAT: {len(local_rat)} value mappings")
        rat_available = True
    else:
        local_rat = None
        rat_available = False
        print("Local RAT (fveg22_local_rat.csv) not found — "
              "pixel values cannot be decoded to WHRTYPE.")

    # Load reference RAT (for WHRTYPE reference tables)
    ref_rat = load_imageserver_rat(imageserver_rat_path)
    if ref_rat is None:
        ref_rat = download_rat_csv()
    if ref_rat is not None:
        print(f"Loaded reference RAT: {len(ref_rat)} entries, "
              f"{ref_rat['WHRTYPE'].nunique()} WHRTYPEs")

    return local_rat, ref_rat, rat_available


# ── Value-to-Attribute Merge ─────────────────────────────────────────

def merge_values_with_rat(value_counts_df, local_rat):
    """
    Join raster value counts with RAT attributes.

    Parameters
    ----------
    value_counts_df : pandas.DataFrame
        Must have VALUE, COUNT columns.
    local_rat : pandas.DataFrame
        Local RAT with VALUE as index, WHRTYPE/WHRNAME/LIFEFORM/WHR13NAME columns.

    Returns
    -------
    pandas.DataFrame
        Merged DataFrame with CWHR attributes, sorted by COUNT descending.
    """
    if local_rat is None:
        return value_counts_df

    merged = value_counts_df.merge(
        local_rat.reset_index(),
        on="VALUE",
        how="left",
    )
    merged = merged.sort_values("COUNT", ascending=False).reset_index(drop=True)
    return merged


# ── Fire Overlay Extraction ──────────────────────────────────────────

def extract_vegetation_at_points(values, transform, points_gdf, crs=None):
    """
    Sample vegetation values at point locations.

    Parameters
    ----------
    values : numpy.ndarray
        2D vegetation array.
    transform : Affine
        Raster transform.
    points_gdf : GeoDataFrame
        Point geometries.
    crs : str, optional
        CRS of the raster. If different from points_gdf, reprojects.

    Returns
    -------
    numpy.ndarray
        Vegetation pixel values at each point (NaN if outside or NoData).
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

    h, w = values.shape
    valid = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)

    result = np.full(len(points_gdf), np.nan)
    sampled = values[rows[valid], cols[valid]].astype(np.float64)
    nodata_val = FVEG22_NODATA
    # Handle both int nodata and NaN
    if not np.isnan(nodata_val):
        sampled[sampled == nodata_val] = np.nan
    result[valid] = sampled

    return result


# ── Data Quality Summary ─────────────────────────────────────────────

def get_vegetation_data_quality_summary(values, nodata=None):
    """
    Generate quality summary for vegetation data.

    Parameters
    ----------
    values : numpy.ndarray
        2D vegetation array.
    nodata : int, optional
        NoData value. Defaults to FVEG22_NODATA.

    Returns
    -------
    dict
        Quality metrics.
    """
    if nodata is None:
        nodata = FVEG22_NODATA

    total = values.size
    # Handle NaN for float arrays
    if np.issubdtype(values.dtype, np.floating):
        nodata_count = int(np.sum(np.isnan(values)))
        valid_vals = values[~np.isnan(values)]
    else:
        nodata_count = int(np.sum(values == nodata))
        valid_vals = values[values != nodata]

    valid = total - nodata_count
    n_unique = len(np.unique(valid_vals)) if len(valid_vals) > 0 else 0

    return {
        "Total pixels": f"{total:,}",
        "Valid pixels": f"{valid:,} ({100 * valid / total:.1f}%)",
        "NoData pixels": f"{nodata_count:,} ({100 * nodata_count / total:.1f}%)",
        "Unique values": f"{n_unique:,}",
        "Value range": f"{int(valid_vals.min())}–{int(valid_vals.max())}" if len(valid_vals) > 0 else "N/A",
    }
