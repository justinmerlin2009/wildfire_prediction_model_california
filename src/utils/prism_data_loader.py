"""
Data loading and processing utilities for PRISM climate data.

Handles the 5 TB PRISM dataset stored on external LaCie drive:
  - File discovery and drive management
  - Zip-aware GeoTIFF I/O via rasterio
  - California windowed reads (~5.5 MB per raster, ~0.5s)
  - Batch time series loading with progress bars
  - Monthly normals and anomaly computation
  - Derived fire weather variables (cumulative VPD, dry days, est. RH)
  - Temporal aggregation (daily→monthly→seasonal→annual, water year)
  - State-level zonal statistics for CONUS analysis
  - Point extraction at fire locations
  - Parquet/npz caching for precomputed summaries

File layout on LaCie drive:
  /Volumes/LaCie/PRISM/{variable}/{daily|monthly}/{year}/prism_{var}_us_30s_{date}.zip
  /Volumes/LaCie/PRISM/normals/{variable}/{daily|monthly}/prism_{var}_us_30s_{date}_avg_30y.zip

Each zip contains a GeoTIFF (~60 MB CONUS, ~5.5 MB CA window).
"""
import gc
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds as window_from_bounds

from .constants import (
    PRISM_BASE_PATH, PRISM_CRS, PRISM_NODATA, PRISM_DTYPE,
    PRISM_CONUS_SHAPE, PRISM_CA_BOUNDS, PRISM_CA_WINDOW_SHAPE,
    PRISM_VARIABLES, PRISM_SOLAR_VARIABLES,
    PRISM_MONTHLY_START_YEAR, PRISM_MONTHLY_END_YEAR,
    PRISM_DAILY_START_YEAR, PRISM_DAILY_END_YEAR,
    PRISM_CACHE_DIR,
)


# ═══════════════════════════════════════════════════════════════════════
# DRIVE MANAGEMENT & FILE DISCOVERY
# ═══════════════════════════════════════════════════════════════════════

def check_prism_drive(base_path=None):
    """
    Verify external PRISM drive is mounted and report available data.

    Parameters
    ----------
    base_path : str or Path, optional
        Root of PRISM data. Defaults to PRISM_BASE_PATH.

    Returns
    -------
    dict
        Drive status, available variables, and file counts.

    Raises
    ------
    FileNotFoundError
        If drive is not mounted.
    """
    if base_path is None:
        base_path = PRISM_BASE_PATH
    base_path = Path(base_path)

    if not base_path.exists():
        raise FileNotFoundError(
            f"PRISM drive not mounted at {base_path}. "
            "Please connect the LaCie external drive."
        )

    available = {}
    for var in PRISM_VARIABLES:
        var_path = base_path / var
        if var_path.exists():
            daily_years = sorted(d.name for d in (var_path / "daily").iterdir()
                                 if d.is_dir()) if (var_path / "daily").exists() else []
            monthly_years = sorted(d.name for d in (var_path / "monthly").iterdir()
                                   if d.is_dir()) if (var_path / "monthly").exists() else []
            available[var] = {
                "daily_years": daily_years,
                "monthly_years": monthly_years,
                "daily_year_range": (daily_years[0], daily_years[-1]) if daily_years else None,
                "monthly_year_range": (monthly_years[0], monthly_years[-1]) if monthly_years else None,
            }

    # Check normals
    normals_path = base_path / "normals"
    normals_vars = []
    if normals_path.exists():
        normals_vars = sorted(d.name for d in normals_path.iterdir() if d.is_dir())

    return {
        "mounted": True,
        "base_path": str(base_path),
        "variables": available,
        "normals_variables": normals_vars,
        "n_variables": len(available),
    }


def discover_files(variable, temporal="monthly", year=None, month=None,
                   base_path=None):
    """
    Find PRISM zip files for a given variable, temporal resolution, and date range.

    Parameters
    ----------
    variable : str
        PRISM variable name (e.g., 'ppt', 'vpdmax').
    temporal : str, default "monthly"
        'daily' or 'monthly'.
    year : int, optional
        Specific year. If None, discovers all available years.
    month : int, optional
        Specific month (1-12). Only for monthly files.
    base_path : str or Path, optional
        Root of PRISM data.

    Returns
    -------
    list of Path
        Sorted list of zip file paths.
    """
    if base_path is None:
        base_path = PRISM_BASE_PATH
    base_path = Path(base_path)

    var_dir = base_path / variable / temporal
    if not var_dir.exists():
        return []

    if year is not None:
        year_dirs = [var_dir / str(year)]
    else:
        year_dirs = sorted(d for d in var_dir.iterdir() if d.is_dir())

    files = []
    for yd in year_dirs:
        if not yd.exists():
            continue
        for f in sorted(yd.iterdir()):
            if not f.name.endswith(".zip"):
                continue
            # Skip annual summary files (e.g., prism_ppt_us_30s_2020.zip)
            # unless specifically requested
            stem = f.stem  # e.g., prism_ppt_us_30s_202001
            date_part = stem.split("_")[-1]

            if temporal == "monthly":
                if month is not None:
                    # Want specific month: YYYYMM format (6 digits)
                    expected = f"{yd.name}{month:02d}"
                    if date_part != expected:
                        continue
                else:
                    # Skip annual files (4-digit date_part = YYYY)
                    if len(date_part) == 4:
                        continue
            files.append(f)

    return files


def build_file_inventory(variables=None, temporal="monthly", year_range=None,
                         base_path=None):
    """
    Build a DataFrame inventory of all available PRISM files.

    Parameters
    ----------
    variables : list of str, optional
        Variables to inventory. Defaults to PRISM_VARIABLES.
    temporal : str, default "monthly"
        'daily' or 'monthly'.
    year_range : tuple of (int, int), optional
        (start_year, end_year) inclusive.
    base_path : str or Path, optional
        Root of PRISM data.

    Returns
    -------
    pandas.DataFrame
        Columns: variable, temporal, year, month, date_str, filepath, file_size_mb.
    """
    if variables is None:
        variables = PRISM_VARIABLES
    if base_path is None:
        base_path = PRISM_BASE_PATH

    rows = []
    for var in variables:
        files = discover_files(var, temporal, base_path=base_path)
        for f in files:
            info = parse_filename(f)
            if info is None:
                continue
            if year_range is not None:
                if info["year"] < year_range[0] or info["year"] > year_range[1]:
                    continue
            info["filepath"] = str(f)
            info["file_size_mb"] = f.stat().st_size / (1024 ** 2)
            rows.append(info)

    return pd.DataFrame(rows)


def parse_filename(filepath):
    """
    Extract variable, date, and temporal type from a PRISM filename.

    Parameters
    ----------
    filepath : str or Path
        Path to a PRISM zip file.

    Returns
    -------
    dict or None
        Keys: variable, temporal, year, month (or None), date_str.
    """
    filepath = Path(filepath)
    stem = filepath.stem  # e.g., prism_ppt_us_30s_202001

    # Remove _avg_30y suffix for normals
    is_normal = "_avg_30y" in stem
    if is_normal:
        stem = stem.replace("_avg_30y", "")

    parts = stem.split("_")
    if len(parts) < 5:
        return None

    variable = parts[1]
    date_str = parts[-1]

    if len(date_str) == 8:      # YYYYMMDD → daily
        temporal = "daily"
        year = int(date_str[:4])
        month = int(date_str[4:6])
    elif len(date_str) == 6:    # YYYYMM → monthly
        temporal = "monthly"
        year = int(date_str[:4])
        month = int(date_str[4:6])
    elif len(date_str) == 4:    # YYYY → annual
        temporal = "annual"
        year = int(date_str)
        month = None
    else:
        return None

    if is_normal:
        temporal = f"normal_{temporal}"

    return {
        "variable": variable,
        "temporal": temporal,
        "year": year,
        "month": month,
        "date_str": date_str,
        "is_normal": is_normal,
    }


# ═══════════════════════════════════════════════════════════════════════
# ZIP-AWARE RASTER I/O
# ═══════════════════════════════════════════════════════════════════════

def _zip_tif_path(zip_path):
    """
    Construct rasterio-compatible URI for a GeoTIFF inside a zip.

    Parameters
    ----------
    zip_path : str or Path
        Path to the .zip file.

    Returns
    -------
    str
        URI like 'zip:///path/to/file.zip!/inner.tif'
    """
    zip_path = Path(zip_path)
    # Inner tif name = zip name with .tif extension
    tif_name = zip_path.stem + ".tif"
    return f"zip://{zip_path}!/{tif_name}"


def load_prism_metadata(zip_path):
    """
    Load PRISM raster metadata without reading pixel data.

    Parameters
    ----------
    zip_path : str or Path
        Path to a PRISM zip file.

    Returns
    -------
    dict
        Raster metadata: crs, shape, bounds, nodata, transform, dtype.
    """
    uri = _zip_tif_path(zip_path)
    with rasterio.open(uri) as src:
        return {
            "crs": str(src.crs),
            "height": src.height,
            "width": src.width,
            "bounds": src.bounds,
            "nodata": src.nodata,
            "transform": src.transform,
            "dtype": src.dtypes[0],
            "res": src.res,
        }


def read_prism_raster(zip_path, bounds=None, window=None):
    """
    Read a PRISM raster from a zip file, optionally with spatial subsetting.

    Parameters
    ----------
    zip_path : str or Path
        Path to a PRISM zip file.
    bounds : tuple, optional
        (west, south, east, north) in EPSG:4269 to subset.
    window : rasterio.windows.Window, optional
        Explicit rasterio Window to read.

    Returns
    -------
    tuple (data, transform, metadata)
        data : numpy.ndarray (float32)
            2D raster values. NoData pixels = PRISM_NODATA (-9999).
        transform : Affine
            Raster transform for the returned extent.
        metadata : dict
            Shape, bounds, source file info.
    """
    uri = _zip_tif_path(zip_path)

    with rasterio.open(uri) as src:
        if bounds is not None:
            window = window_from_bounds(*bounds, transform=src.transform)

        if window is not None:
            data = src.read(1, window=window)
            transform = src.window_transform(window)
        else:
            data = src.read(1)
            transform = src.transform

        metadata = {
            "shape": data.shape,
            "bounds": bounds if bounds else src.bounds,
            "source": str(zip_path),
            "crs": str(src.crs),
        }

    return data.astype(np.float32), transform, metadata


def read_prism_california(zip_path, ca_bounds=None):
    """
    Read a PRISM raster windowed to California extent.

    Efficient: reads only ~5.5 MB from the ~60 MB CONUS zip (~0.5s).

    Parameters
    ----------
    zip_path : str or Path
        Path to a PRISM zip file.
    ca_bounds : tuple, optional
        (west, south, east, north). Defaults to PRISM_CA_BOUNDS.

    Returns
    -------
    tuple (data, transform, metadata)
        data : numpy.ndarray (float32)
            CA-extent raster (1140 × 1260).
        transform : Affine
            Transform for the CA window.
        metadata : dict
            Shape, source info.
    """
    if ca_bounds is None:
        ca_bounds = PRISM_CA_BOUNDS
    return read_prism_raster(zip_path, bounds=ca_bounds)


def read_prism_conus(zip_path):
    """
    Read a full CONUS PRISM raster from a zip file.

    Warning: ~83 MB per raster. Use sparingly.

    Parameters
    ----------
    zip_path : str or Path
        Path to a PRISM zip file.

    Returns
    -------
    tuple (data, transform, metadata)
    """
    return read_prism_raster(zip_path)


# ═══════════════════════════════════════════════════════════════════════
# BATCH / TIME SERIES LOADING
# ═══════════════════════════════════════════════════════════════════════

def load_monthly_series(variable, start_year, end_year, months=None,
                        bounds=None, base_path=None, progress=True):
    """
    Load a stack of monthly PRISM rasters as a 3D array.

    Parameters
    ----------
    variable : str
        PRISM variable name.
    start_year, end_year : int
        Year range (inclusive).
    months : list of int, optional
        Specific months to load (1-12). None = all 12.
    bounds : tuple, optional
        Spatial subset bounds. None = full CONUS.
    base_path : str or Path, optional
        PRISM root.
    progress : bool, default True
        Show tqdm progress bar.

    Returns
    -------
    tuple (data_3d, dates, transform)
        data_3d : numpy.ndarray (n_months, rows, cols)
        dates : list of (year, month) tuples
        transform : Affine for the spatial extent
    """
    if base_path is None:
        base_path = PRISM_BASE_PATH

    # Collect all files
    file_list = []
    date_list = []
    for year in range(start_year, end_year + 1):
        month_range = months if months else range(1, 13)
        for month in month_range:
            files = discover_files(variable, "monthly", year=year, month=month,
                                   base_path=base_path)
            if files:
                file_list.append(files[0])
                date_list.append((year, month))

    if not file_list:
        raise FileNotFoundError(
            f"No monthly {variable} files found for {start_year}-{end_year}"
        )

    # Read first to get shape
    first_data, transform, _ = read_prism_raster(file_list[0], bounds=bounds)
    h, w = first_data.shape

    data_3d = np.full((len(file_list), h, w), PRISM_NODATA, dtype=np.float32)
    data_3d[0] = first_data

    iterator = range(1, len(file_list))
    if progress:
        try:
            from tqdm import tqdm
            iterator = tqdm(iterator, desc=f"Loading {variable} monthly",
                            total=len(file_list), initial=1)
        except ImportError:
            pass

    for i in iterator:
        data_3d[i], _, _ = read_prism_raster(file_list[i], bounds=bounds)

    return data_3d, date_list, transform


def load_daily_series(variable, start_date, end_date, bounds=None,
                      base_path=None, progress=True):
    """
    Load a stack of daily PRISM rasters as a 3D array.

    Warning: ~5.5 MB per day for CA, ~2 GB per year. Use targeted date ranges.

    Parameters
    ----------
    variable : str
        PRISM variable name.
    start_date, end_date : str
        Date strings 'YYYY-MM-DD'.
    bounds : tuple, optional
        Spatial subset bounds. None = full CONUS.
    base_path : str or Path, optional
        PRISM root.
    progress : bool, default True
        Show tqdm progress bar.

    Returns
    -------
    tuple (data_3d, dates, transform)
        data_3d : numpy.ndarray (n_days, rows, cols)
        dates : list of datetime.date
        transform : Affine
    """
    import datetime

    if base_path is None:
        base_path = PRISM_BASE_PATH

    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)

    file_list = []
    date_list = []
    current = start
    while current <= end:
        date_str = current.strftime("%Y%m%d")
        zip_name = f"prism_{variable}_us_30s_{date_str}.zip"
        zip_path = Path(base_path) / variable / "daily" / str(current.year) / zip_name
        if zip_path.exists():
            file_list.append(zip_path)
            date_list.append(current)
        current += datetime.timedelta(days=1)

    if not file_list:
        raise FileNotFoundError(
            f"No daily {variable} files found for {start_date} to {end_date}"
        )

    first_data, transform, _ = read_prism_raster(file_list[0], bounds=bounds)
    h, w = first_data.shape

    data_3d = np.full((len(file_list), h, w), PRISM_NODATA, dtype=np.float32)
    data_3d[0] = first_data

    iterator = range(1, len(file_list))
    if progress:
        try:
            from tqdm import tqdm
            iterator = tqdm(iterator, desc=f"Loading {variable} daily",
                            total=len(file_list), initial=1)
        except ImportError:
            pass

    for i in iterator:
        data_3d[i], _, _ = read_prism_raster(file_list[i], bounds=bounds)

    return data_3d, date_list, transform


def load_monthly_stats_ca(variable, start_year, end_year, base_path=None,
                          progress=True):
    """
    Load monthly CA-wide spatial statistics without retaining full rasters.

    Memory-efficient: computes stats on each raster then discards it.
    Returns a lightweight DataFrame (~1 KB per month).

    Parameters
    ----------
    variable : str
        PRISM variable name.
    start_year, end_year : int
        Year range (inclusive).
    base_path : str or Path, optional
        PRISM root.
    progress : bool, default True
        Show tqdm progress bar.

    Returns
    -------
    pandas.DataFrame
        Columns: year, month, mean, median, std, p10, p90, min, max, n_valid.
    """
    if base_path is None:
        base_path = PRISM_BASE_PATH
    ca_bounds = PRISM_CA_BOUNDS

    rows = []
    year_range = range(start_year, end_year + 1)

    total = sum(12 for _ in year_range)
    counter = 0

    if progress:
        try:
            from tqdm import tqdm
            pbar = tqdm(total=total, desc=f"CA stats {variable}")
        except ImportError:
            pbar = None
    else:
        pbar = None

    for year in year_range:
        for month in range(1, 13):
            files = discover_files(variable, "monthly", year=year, month=month,
                                   base_path=base_path)
            if not files:
                if pbar:
                    pbar.update(1)
                continue

            try:
                data, _, _ = read_prism_california(files[0], ca_bounds)
            except Exception as e:
                import warnings
                warnings.warn(f"Skipping {files[0].name}: {e}")
                if pbar:
                    pbar.update(1)
                continue

            valid = data[data != PRISM_NODATA]

            if len(valid) > 0:
                rows.append({
                    "year": year,
                    "month": month,
                    "mean": float(np.mean(valid)),
                    "median": float(np.median(valid)),
                    "std": float(np.std(valid)),
                    "p10": float(np.percentile(valid, 10)),
                    "p90": float(np.percentile(valid, 90)),
                    "min": float(np.min(valid)),
                    "max": float(np.max(valid)),
                    "n_valid": int(len(valid)),
                })

            if pbar:
                pbar.update(1)

    if pbar:
        pbar.close()

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════
# NORMALS & ANOMALIES
# ═══════════════════════════════════════════════════════════════════════

def _find_normal_file(variable, month=None, temporal="monthly", base_path=None):
    """
    Find the 30-year normal file for a variable/month.

    Parameters
    ----------
    variable : str
        PRISM variable.
    month : int, optional
        Month (1-12) for monthly normals. None for annual.
    temporal : str, default "monthly"
        'daily' or 'monthly'.
    base_path : Path, optional

    Returns
    -------
    Path or None
    """
    if base_path is None:
        base_path = PRISM_BASE_PATH
    base_path = Path(base_path)

    normals_dir = base_path / "normals" / variable / temporal

    if not normals_dir.exists():
        return None

    if month is not None:
        # Monthly normal: look for pattern *_YYYYMM_avg_30y.zip
        # The year prefix varies; search by month suffix
        for f in normals_dir.iterdir():
            if not f.name.endswith("_avg_30y.zip"):
                continue
            # Parse date part
            stem = f.stem.replace("_avg_30y", "")
            date_part = stem.split("_")[-1]
            if len(date_part) == 6 and date_part.endswith(f"{month:02d}"):
                return f
    else:
        # Annual normal
        for f in normals_dir.iterdir():
            if not f.name.endswith("_avg_30y.zip"):
                continue
            stem = f.stem.replace("_avg_30y", "")
            date_part = stem.split("_")[-1]
            if len(date_part) == 4:  # YYYY
                return f

    return None


def load_monthly_normal(variable, month, bounds=None, base_path=None):
    """
    Load a single month's 30-year normal raster.

    Parameters
    ----------
    variable : str
        PRISM variable.
    month : int
        Month (1-12).
    bounds : tuple, optional
        Spatial subset.
    base_path : Path, optional

    Returns
    -------
    tuple (data, transform, metadata) or None if not found.
    """
    normal_file = _find_normal_file(variable, month=month, base_path=base_path)
    if normal_file is None:
        return None
    return read_prism_raster(normal_file, bounds=bounds)


def load_all_monthly_normals(variable, bounds=None, base_path=None):
    """
    Load all 12 monthly normals as a 3D stack.

    Parameters
    ----------
    variable : str
        PRISM variable.
    bounds : tuple, optional
        Spatial subset.
    base_path : Path, optional

    Returns
    -------
    tuple (normals_3d, months, transform)
        normals_3d : numpy.ndarray (12, rows, cols)
        months : list [1, 2, ..., 12]
        transform : Affine
    """
    normals = []
    months = []
    transform = None

    for m in range(1, 13):
        result = load_monthly_normal(variable, m, bounds=bounds, base_path=base_path)
        if result is not None:
            data, tfm, _ = result
            normals.append(data)
            months.append(m)
            if transform is None:
                transform = tfm

    if not normals:
        raise FileNotFoundError(f"No monthly normals found for {variable}")

    return np.stack(normals), months, transform


def compute_monthly_anomaly(observed, normal, variable=None):
    """
    Compute anomaly from observed and normal values.

    For cumulative variables (ppt): returns percentage of normal.
    For non-cumulative (temperature, VPD): returns difference.

    Parameters
    ----------
    observed : numpy.ndarray
        Observed values.
    normal : numpy.ndarray
        Normal (climatological) values.
    variable : str, optional
        Variable name to determine anomaly type.

    Returns
    -------
    numpy.ndarray
        Anomaly values. NaN where either input is NoData.
    """
    from .prism_domain_mappings import PRISM_VARIABLE_META

    obs = np.where(observed == PRISM_NODATA, np.nan, observed.astype(np.float64))
    nrm = np.where(normal == PRISM_NODATA, np.nan, normal.astype(np.float64))

    is_cumulative = False
    if variable and variable in PRISM_VARIABLE_META:
        is_cumulative = PRISM_VARIABLE_META[variable].get("is_cumulative", False)

    if is_cumulative:
        # Percentage of normal (avoid division by zero)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            anomaly = np.where(nrm > 0, 100.0 * obs / nrm, np.nan)
    else:
        anomaly = obs - nrm

    return anomaly.astype(np.float32)


def compute_anomaly_series(observed_3d, normals_3d, months, variable=None):
    """
    Compute anomaly time series from observed stack and normals.

    Parameters
    ----------
    observed_3d : numpy.ndarray (n_months, rows, cols)
        Observed monthly values.
    normals_3d : numpy.ndarray (12, rows, cols)
        Monthly normals (index 0 = January).
    months : list of int
        Month for each slice in observed_3d (1-12).
    variable : str, optional
        Variable name.

    Returns
    -------
    numpy.ndarray (n_months, rows, cols)
        Anomaly values.
    """
    anomalies = np.full_like(observed_3d, np.nan, dtype=np.float32)

    for i, m in enumerate(months):
        normal_idx = m - 1  # 0-indexed
        anomalies[i] = compute_monthly_anomaly(
            observed_3d[i], normals_3d[normal_idx], variable
        )

    return anomalies


# ═══════════════════════════════════════════════════════════════════════
# DERIVED FIRE WEATHER VARIABLES
# ═══════════════════════════════════════════════════════════════════════

def compute_diurnal_temp_range(tmax, tmin):
    """Compute diurnal temperature range (DTR = tmax - tmin)."""
    result = np.where(
        (tmax == PRISM_NODATA) | (tmin == PRISM_NODATA),
        np.nan,
        tmax.astype(np.float64) - tmin.astype(np.float64)
    )
    return result.astype(np.float32)


def compute_vpd_mean(vpdmax, vpdmin):
    """Compute mean VPD from max and min."""
    result = np.where(
        (vpdmax == PRISM_NODATA) | (vpdmin == PRISM_NODATA),
        np.nan,
        (vpdmax.astype(np.float64) + vpdmin.astype(np.float64)) / 2.0
    )
    return result.astype(np.float32)


def compute_dew_point_depression(tmean, tdmean):
    """Compute dew point depression (DPD = tmean - tdmean)."""
    result = np.where(
        (tmean == PRISM_NODATA) | (tdmean == PRISM_NODATA),
        np.nan,
        tmean.astype(np.float64) - tdmean.astype(np.float64)
    )
    return result.astype(np.float32)


def compute_estimated_rh(tdmean, tmax):
    """
    Estimate minimum RH from dew point and max temperature (Magnus formula).

    Parameters
    ----------
    tdmean, tmax : numpy.ndarray
        Temperature arrays in °C.

    Returns
    -------
    numpy.ndarray
        Estimated minimum RH (%).
    """
    from .prism_domain_mappings import compute_rh_from_tdmean_tmax

    td = np.where(tdmean == PRISM_NODATA, np.nan, tdmean.astype(np.float64))
    t = np.where(tmax == PRISM_NODATA, np.nan, tmax.astype(np.float64))
    return compute_rh_from_tdmean_tmax(td, t).astype(np.float32)


def compute_cumulative_vpd(vpdmax_3d, window_days):
    """
    Compute rolling cumulative VPD over a time window.

    Parameters
    ----------
    vpdmax_3d : numpy.ndarray (n_days, rows, cols)
        Daily VPD max values.
    window_days : int
        Rolling window size in days.

    Returns
    -------
    numpy.ndarray (n_days, rows, cols)
        Cumulative VPD. First (window_days - 1) slices are NaN.
    """
    n, h, w = vpdmax_3d.shape
    vpd = np.where(vpdmax_3d == PRISM_NODATA, np.nan, vpdmax_3d.astype(np.float64))

    result = np.full_like(vpd, np.nan)

    # Use cumsum trick for efficiency
    vpd_filled = np.nan_to_num(vpd, nan=0.0)
    cumsum = np.cumsum(vpd_filled, axis=0)

    for i in range(window_days - 1, n):
        if i == window_days - 1:
            result[i] = cumsum[i]
        else:
            result[i] = cumsum[i] - cumsum[i - window_days]

    # Mask where any input in window was NaN
    valid_count = np.cumsum(~np.isnan(vpd), axis=0).astype(np.float64)
    for i in range(window_days - 1, n):
        if i == window_days - 1:
            expected = valid_count[i]
        else:
            expected = valid_count[i] - valid_count[i - window_days]
        result[i] = np.where(expected >= window_days * 0.8, result[i], np.nan)

    return result.astype(np.float32)


def compute_dry_day_count(ppt_3d, window_days, threshold_mm=0.2):
    """
    Count dry days (precip < threshold) in a rolling window.

    Parameters
    ----------
    ppt_3d : numpy.ndarray (n_days, rows, cols)
        Daily precipitation.
    window_days : int
        Rolling window.
    threshold_mm : float, default 0.2
        Precipitation threshold for "dry day".

    Returns
    -------
    numpy.ndarray (n_days, rows, cols)
        Count of dry days in trailing window. First (window-1) slices = NaN.
    """
    n, h, w = ppt_3d.shape
    ppt = np.where(ppt_3d == PRISM_NODATA, np.nan, ppt_3d.astype(np.float64))

    is_dry = (ppt < threshold_mm).astype(np.float64)
    is_dry[np.isnan(ppt)] = np.nan

    dry_filled = np.nan_to_num(is_dry, nan=0.0)
    cumsum = np.cumsum(dry_filled, axis=0)

    result = np.full((n, h, w), np.nan, dtype=np.float32)
    for i in range(window_days - 1, n):
        if i == window_days - 1:
            result[i] = cumsum[i]
        else:
            result[i] = cumsum[i] - cumsum[i - window_days]

    return result


# ═══════════════════════════════════════════════════════════════════════
# TEMPORAL AGGREGATION
# ═══════════════════════════════════════════════════════════════════════

def aggregate_daily_to_monthly(daily_3d, dates, variable=None):
    """
    Aggregate daily rasters to monthly.

    Sum for precipitation, mean for all other variables.

    Parameters
    ----------
    daily_3d : numpy.ndarray (n_days, rows, cols)
        Daily values.
    dates : list of datetime.date
        Date for each daily slice.
    variable : str, optional
        Variable name (determines sum vs mean).

    Returns
    -------
    tuple (monthly_3d, year_months)
        monthly_3d : numpy.ndarray (n_months, rows, cols)
        year_months : list of (year, month) tuples
    """
    from .prism_domain_mappings import PRISM_VARIABLE_META

    is_cumulative = False
    if variable and variable in PRISM_VARIABLE_META:
        is_cumulative = PRISM_VARIABLE_META[variable].get("is_cumulative", False)

    # Group by (year, month)
    ym_groups = {}
    for i, d in enumerate(dates):
        key = (d.year, d.month)
        if key not in ym_groups:
            ym_groups[key] = []
        ym_groups[key].append(i)

    year_months = sorted(ym_groups.keys())
    _, h, w = daily_3d.shape
    monthly_3d = np.full((len(year_months), h, w), np.nan, dtype=np.float32)

    for j, ym in enumerate(year_months):
        indices = ym_groups[ym]
        chunk = daily_3d[indices].astype(np.float64)
        chunk[chunk == PRISM_NODATA] = np.nan

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            if is_cumulative:
                monthly_3d[j] = np.nansum(chunk, axis=0)
            else:
                monthly_3d[j] = np.nanmean(chunk, axis=0)

    return monthly_3d, year_months


def aggregate_monthly_to_seasonal(monthly_3d, year_months, variable=None):
    """
    Aggregate monthly rasters to meteorological seasons.

    Parameters
    ----------
    monthly_3d : numpy.ndarray (n_months, rows, cols)
    year_months : list of (year, month) tuples
    variable : str, optional

    Returns
    -------
    tuple (seasonal_3d, season_labels)
        seasonal_3d : numpy.ndarray (n_seasons, rows, cols)
        season_labels : list of (year, season_name) tuples
    """
    from .prism_domain_mappings import CLIMATE_SEASON_MAP, PRISM_VARIABLE_META

    is_cumulative = False
    if variable and variable in PRISM_VARIABLE_META:
        is_cumulative = PRISM_VARIABLE_META[variable].get("is_cumulative", False)

    # Group by (year, season)
    groups = {}
    for i, (y, m) in enumerate(year_months):
        season = CLIMATE_SEASON_MAP[m]
        # For winter: Dec belongs to next year's winter
        season_year = y + 1 if m == 12 else y
        key = (season_year, season)
        if key not in groups:
            groups[key] = []
        groups[key].append(i)

    season_labels = sorted(groups.keys())
    _, h, w = monthly_3d.shape
    seasonal_3d = np.full((len(season_labels), h, w), np.nan, dtype=np.float32)

    for j, key in enumerate(season_labels):
        indices = groups[key]
        if len(indices) < 3:
            continue  # Incomplete season
        chunk = monthly_3d[indices].astype(np.float64)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            if is_cumulative:
                seasonal_3d[j] = np.nansum(chunk, axis=0)
            else:
                seasonal_3d[j] = np.nanmean(chunk, axis=0)

    return seasonal_3d, season_labels


def aggregate_monthly_to_annual(monthly_3d, year_months, variable=None):
    """
    Aggregate monthly rasters to annual.

    Parameters
    ----------
    monthly_3d : numpy.ndarray (n_months, rows, cols)
    year_months : list of (year, month) tuples
    variable : str, optional

    Returns
    -------
    tuple (annual_3d, years)
    """
    from .prism_domain_mappings import PRISM_VARIABLE_META

    is_cumulative = False
    if variable and variable in PRISM_VARIABLE_META:
        is_cumulative = PRISM_VARIABLE_META[variable].get("is_cumulative", False)

    groups = {}
    for i, (y, m) in enumerate(year_months):
        if y not in groups:
            groups[y] = []
        groups[y].append(i)

    years = sorted(groups.keys())
    _, h, w = monthly_3d.shape
    annual_3d = np.full((len(years), h, w), np.nan, dtype=np.float32)

    for j, year in enumerate(years):
        indices = groups[year]
        if len(indices) < 12:
            continue  # Incomplete year
        chunk = monthly_3d[indices].astype(np.float64)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            if is_cumulative:
                annual_3d[j] = np.nansum(chunk, axis=0)
            else:
                annual_3d[j] = np.nanmean(chunk, axis=0)

    return annual_3d, years


def aggregate_to_water_year(monthly_3d, year_months, variable=None):
    """
    Aggregate monthly rasters to water year (Oct-Sep).

    Parameters
    ----------
    monthly_3d : numpy.ndarray (n_months, rows, cols)
    year_months : list of (year, month) tuples
    variable : str, optional

    Returns
    -------
    tuple (wy_3d, water_years)
    """
    from .prism_domain_mappings import (
        PRISM_VARIABLE_META, WATER_YEAR_START_MONTH, month_to_water_year,
    )

    is_cumulative = False
    if variable and variable in PRISM_VARIABLE_META:
        is_cumulative = PRISM_VARIABLE_META[variable].get("is_cumulative", False)

    groups = {}
    for i, (y, m) in enumerate(year_months):
        wy = int(month_to_water_year(y, m))
        if wy not in groups:
            groups[wy] = []
        groups[wy].append(i)

    water_years = sorted(groups.keys())
    _, h, w = monthly_3d.shape
    wy_3d = np.full((len(water_years), h, w), np.nan, dtype=np.float32)

    for j, wy in enumerate(water_years):
        indices = groups[wy]
        if len(indices) < 12:
            continue
        chunk = monthly_3d[indices].astype(np.float64)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            if is_cumulative:
                wy_3d[j] = np.nansum(chunk, axis=0)
            else:
                wy_3d[j] = np.nanmean(chunk, axis=0)

    return wy_3d, water_years


# ═══════════════════════════════════════════════════════════════════════
# STATE-LEVEL ZONAL STATISTICS
# ═══════════════════════════════════════════════════════════════════════

def load_us_states_boundaries(cache_dir=None):
    """
    Load US Census TIGER/Line state boundaries.

    Downloads and caches the cb_2022_us_state_500k shapefile.

    Parameters
    ----------
    cache_dir : str or Path, optional
        Directory to cache downloaded shapefile. Defaults to PRISM_CACHE_DIR.

    Returns
    -------
    geopandas.GeoDataFrame
        48 CONUS states + DC with STUSPS, NAME, STATEFP, geometry.
    """
    import geopandas as gpd

    if cache_dir is None:
        cache_dir = PRISM_CACHE_DIR
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    cached_file = cache_dir / "us_states_conus.gpkg"
    if cached_file.exists():
        return gpd.read_file(cached_file)

    # Download Census TIGER/Line
    url = (
        "https://www2.census.gov/geo/tiger/GENZ2022/shp/"
        "cb_2022_us_state_500k.zip"
    )
    print(f"Downloading US state boundaries from Census Bureau...")
    states = gpd.read_file(url)

    # Filter to CONUS (exclude AK=02, HI=15, territories)
    from .prism_domain_mappings import US_STATE_FIPS
    conus_fips = set(US_STATE_FIPS.values())
    states = states[states["STATEFP"].isin(conus_fips)].copy()

    # Ensure CRS is NAD83 (matching PRISM)
    if str(states.crs) != PRISM_CRS:
        states = states.to_crs(PRISM_CRS)

    # Keep minimal columns
    states = states[["STUSPS", "NAME", "STATEFP", "geometry"]].copy()
    states = states.sort_values("STUSPS").reset_index(drop=True)

    # Cache
    states.to_file(cached_file, driver="GPKG")
    print(f"Cached {len(states)} CONUS states to {cached_file}")

    return states


def compute_state_statistics(zip_path, states_gdf, statistic="mean"):
    """
    Compute per-state zonal statistics from a single CONUS raster.

    Parameters
    ----------
    zip_path : str or Path
        Path to PRISM zip file (full CONUS).
    states_gdf : geopandas.GeoDataFrame
        State boundaries with STUSPS column and geometry.
    statistic : str or list, default "mean"
        Statistics to compute: 'mean', 'median', 'std', 'min', 'max', 'p10', 'p90'.

    Returns
    -------
    dict
        {state_abbrev: {statistic: value, ...}} for each state.
    """
    if isinstance(statistic, str):
        statistics = [statistic]
    else:
        statistics = statistic

    data, transform, _ = read_prism_conus(zip_path)

    results = {}
    for _, row in states_gdf.iterrows():
        state = row["STUSPS"]
        geom = row["geometry"]

        try:
            from rasterio.features import geometry_mask
            mask = geometry_mask(
                [geom], out_shape=data.shape, transform=transform, invert=True
            )
            vals = data[mask]
            vals = vals[vals != PRISM_NODATA]

            if len(vals) == 0:
                results[state] = {s: np.nan for s in statistics}
                continue

            state_stats = {}
            for s in statistics:
                if s == "mean":
                    state_stats[s] = float(np.mean(vals))
                elif s == "median":
                    state_stats[s] = float(np.median(vals))
                elif s == "std":
                    state_stats[s] = float(np.std(vals))
                elif s == "min":
                    state_stats[s] = float(np.min(vals))
                elif s == "max":
                    state_stats[s] = float(np.max(vals))
                elif s == "p10":
                    state_stats[s] = float(np.percentile(vals, 10))
                elif s == "p90":
                    state_stats[s] = float(np.percentile(vals, 90))
                elif s == "n_valid":
                    state_stats[s] = int(len(vals))

            results[state] = state_stats

        except Exception as e:
            results[state] = {s: np.nan for s in statistics}

    return results


def compute_state_timeseries(variable, temporal, year_range, states_gdf,
                             statistics=None, base_path=None, progress=True):
    """
    Build full state × time series DataFrame by reading CONUS rasters
    and computing per-state zonal statistics.

    Parameters
    ----------
    variable : str
        PRISM variable.
    temporal : str
        'monthly' or 'annual'.
    year_range : tuple of (int, int)
        (start_year, end_year) inclusive.
    states_gdf : geopandas.GeoDataFrame
        State boundaries.
    statistics : list of str, optional
        Stats to compute. Defaults to ['mean', 'median', 'p10', 'p90', 'std'].
    base_path : Path, optional
    progress : bool, default True

    Returns
    -------
    pandas.DataFrame
        Columns: variable, year, month, state, mean, median, p10, p90, std.
    """
    if statistics is None:
        statistics = ["mean", "median", "p10", "p90", "std"]
    if base_path is None:
        base_path = PRISM_BASE_PATH

    files = discover_files(variable, temporal, base_path=base_path)

    # Filter by year range
    filtered = []
    for f in files:
        info = parse_filename(f)
        if info and year_range[0] <= info["year"] <= year_range[1]:
            filtered.append((f, info))

    rows = []
    iterator = filtered
    if progress:
        try:
            from tqdm import tqdm
            iterator = tqdm(filtered, desc=f"State stats {variable}")
        except ImportError:
            pass

    for f, info in iterator:
        state_stats = compute_state_statistics(f, states_gdf, statistics)

        for state, stats in state_stats.items():
            row = {
                "variable": variable,
                "year": info["year"],
                "month": info.get("month"),
                "state": state,
            }
            row.update(stats)
            rows.append(row)

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════
# FIRE OVERLAY EXTRACTION
# ═══════════════════════════════════════════════════════════════════════

def extract_climate_at_points(data, transform, points_gdf, crs=None):
    """
    Sample PRISM raster values at point locations.

    Parameters
    ----------
    data : numpy.ndarray (2D)
        Raster values.
    transform : Affine
        Raster transform.
    points_gdf : geopandas.GeoDataFrame
        Point geometries.
    crs : str, optional
        CRS of the raster. If different from points, reprojects.

    Returns
    -------
    numpy.ndarray
        Values at each point (NaN if outside or NoData).
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

    h, w = data.shape
    valid = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)

    values = np.full(len(points_gdf), np.nan, dtype=np.float64)
    sampled = data[rows[valid], cols[valid]].astype(np.float64)
    sampled[sampled == PRISM_NODATA] = np.nan
    values[valid] = sampled

    return values


def extract_monthly_climate_at_fires(variable, fire_gdf, date_column="Ig_Date",
                                     months_before=0, bounds=None,
                                     base_path=None, progress=True):
    """
    Extract climate values at fire locations for the month of each fire.

    Parameters
    ----------
    variable : str
        PRISM variable.
    fire_gdf : geopandas.GeoDataFrame
        Fire points with a date column.
    date_column : str, default "Ig_Date"
        Column containing fire dates.
    months_before : int, default 0
        Offset: 0 = month of fire, 1 = one month before, etc.
    bounds : tuple, optional
        Spatial bounds for windowed read.
    base_path : Path, optional
    progress : bool, default True

    Returns
    -------
    numpy.ndarray
        Climate values for each fire point.
    """
    if base_path is None:
        base_path = PRISM_BASE_PATH
    if bounds is None:
        bounds = PRISM_CA_BOUNDS

    # Parse dates and compute target year/month
    dates = pd.to_datetime(fire_gdf[date_column])
    target_ym = dates - pd.DateOffset(months=months_before)

    # Group fires by (year, month)
    ym_groups = {}
    for i, dt in enumerate(target_ym):
        if pd.isna(dt):
            continue
        key = (dt.year, dt.month)
        if key not in ym_groups:
            ym_groups[key] = []
        ym_groups[key].append(i)

    values = np.full(len(fire_gdf), np.nan, dtype=np.float64)

    iterator = ym_groups.items()
    if progress:
        try:
            from tqdm import tqdm
            iterator = tqdm(list(iterator), desc=f"Fire {variable}")
        except ImportError:
            pass

    for (year, month), indices in iterator:
        files = discover_files(variable, "monthly", year=year, month=month,
                               base_path=base_path)
        if not files:
            continue

        data, transform, _ = read_prism_raster(files[0], bounds=bounds)

        # Extract for this batch of fires
        subset = fire_gdf.iloc[indices]
        if str(subset.crs) != PRISM_CRS:
            subset = subset.to_crs(PRISM_CRS)

        rows, cols = rasterio.transform.rowcol(
            transform,
            subset.geometry.x.values,
            subset.geometry.y.values,
        )
        rows = np.asarray(rows)
        cols = np.asarray(cols)
        h, w = data.shape
        valid = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)

        for j, idx in enumerate(indices):
            if valid[j]:
                v = float(data[rows[j], cols[j]])
                if v != PRISM_NODATA:
                    values[idx] = v

    return values


# ═══════════════════════════════════════════════════════════════════════
# CACHING
# ═══════════════════════════════════════════════════════════════════════

def _has_parquet():
    """Check if parquet engine (pyarrow or fastparquet) is available."""
    try:
        import pyarrow  # noqa: F401
        return True
    except ImportError:
        pass
    try:
        import fastparquet  # noqa: F401
        return True
    except ImportError:
        return False


def save_to_cache(data, name, cache_dir=None):
    """
    Save data to cache directory.

    DataFrames: parquet if available, else CSV.
    Arrays: npz (compressed).

    Parameters
    ----------
    data : pandas.DataFrame or numpy.ndarray
        Data to cache.
    name : str
        Cache file name (without extension).
    cache_dir : Path, optional
        Defaults to PRISM_CACHE_DIR.
    """
    if cache_dir is None:
        cache_dir = PRISM_CACHE_DIR
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    if isinstance(data, pd.DataFrame):
        if _has_parquet():
            path = cache_dir / f"{name}.parquet"
            data.to_parquet(path, index=False)
        else:
            path = cache_dir / f"{name}.csv"
            data.to_csv(path, index=False)
        print(f"Cached DataFrame to {path} ({path.stat().st_size / 1024:.0f} KB)")
    elif isinstance(data, np.ndarray):
        path = cache_dir / f"{name}.npz"
        np.savez_compressed(path, data=data)
        print(f"Cached array to {path} ({path.stat().st_size / 1024:.0f} KB)")
    else:
        raise TypeError(f"Cannot cache type {type(data)}")


def load_from_cache(name, cache_dir=None):
    """
    Load data from cache.

    Parameters
    ----------
    name : str
        Cache file name (without extension).
    cache_dir : Path, optional

    Returns
    -------
    pandas.DataFrame or numpy.ndarray or None
        Cached data, or None if not found.
    """
    if cache_dir is None:
        cache_dir = PRISM_CACHE_DIR
    cache_dir = Path(cache_dir)

    parquet_path = cache_dir / f"{name}.parquet"
    csv_path = cache_dir / f"{name}.csv"
    npz_path = cache_dir / f"{name}.npz"

    if parquet_path.exists() and _has_parquet():
        return pd.read_parquet(parquet_path)
    elif csv_path.exists():
        return pd.read_csv(csv_path)
    elif npz_path.exists():
        return np.load(npz_path)["data"]
    else:
        return None


def precompute_state_monthly_summaries(variables=None, year_range=None,
                                       states_gdf=None, output_path=None,
                                       base_path=None):
    """
    One-time batch: read CONUS monthly rasters, compute per-state statistics,
    and save to a single parquet file.

    This is the main function called by scripts/prism_precompute_state_summaries.py.

    Parameters
    ----------
    variables : list of str, optional
        Defaults to PRISM_VARIABLES.
    year_range : tuple of (int, int), optional
        Defaults to (PRISM_MONTHLY_START_YEAR, PRISM_MONTHLY_END_YEAR).
    states_gdf : GeoDataFrame, optional
        State boundaries. Will be loaded if None.
    output_path : Path, optional
        Output parquet path. Defaults to PRISM_CACHE_DIR/prism_state_monthly_summaries.parquet.
    base_path : Path, optional
        PRISM root.

    Returns
    -------
    pandas.DataFrame
        The complete state × month × variable summary.
    """
    from rasterio.features import geometry_mask

    if variables is None:
        variables = PRISM_VARIABLES
    if year_range is None:
        year_range = (PRISM_MONTHLY_START_YEAR, PRISM_MONTHLY_END_YEAR)
    if states_gdf is None:
        states_gdf = load_us_states_boundaries()
    if output_path is None:
        ext = "parquet" if _has_parquet() else "csv"
        output_path = PRISM_CACHE_DIR / f"prism_state_monthly_summaries.{ext}"
    if base_path is None:
        base_path = PRISM_BASE_PATH

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Pre-rasterize state masks for efficiency
    # Read a sample raster to get CONUS shape and transform
    sample_files = discover_files(variables[0], "monthly", year=2020, month=1,
                                  base_path=base_path)
    if not sample_files:
        raise FileNotFoundError("Cannot find sample PRISM raster for mask creation")

    with rasterio.open(_zip_tif_path(sample_files[0])) as src:
        conus_shape = (src.height, src.width)
        conus_transform = src.transform

    print(f"Pre-computing state masks for {len(states_gdf)} states "
          f"on {conus_shape} grid...")
    state_masks = {}
    for _, row in states_gdf.iterrows():
        state = row["STUSPS"]
        try:
            mask = geometry_mask(
                [row["geometry"]], out_shape=conus_shape,
                transform=conus_transform, invert=True
            )
            state_masks[state] = mask
        except Exception as e:
            print(f"  Warning: failed to create mask for {state}: {e}")

    print(f"Created masks for {len(state_masks)} states")

    all_rows = []

    for var in variables:
        files = discover_files(var, "monthly", base_path=base_path)

        # Filter by year range
        filtered = []
        for f in files:
            info = parse_filename(f)
            if info and year_range[0] <= info["year"] <= year_range[1]:
                filtered.append((f, info))

        print(f"\n{var}: {len(filtered)} monthly files to process")

        try:
            from tqdm import tqdm
            iterator = tqdm(filtered, desc=f"  {var}")
        except ImportError:
            iterator = filtered

        for f, info in iterator:
            try:
                data, _, _ = read_prism_conus(f)
            except Exception as e:
                print(f"  Error reading {f}: {e}")
                continue

            for state, mask in state_masks.items():
                vals = data[mask]
                vals = vals[vals != PRISM_NODATA]

                if len(vals) == 0:
                    continue

                all_rows.append({
                    "variable": var,
                    "year": info["year"],
                    "month": info["month"],
                    "state": state,
                    "mean": float(np.mean(vals)),
                    "median": float(np.median(vals)),
                    "std": float(np.std(vals)),
                    "p10": float(np.percentile(vals, 10)),
                    "p90": float(np.percentile(vals, 90)),
                    "min": float(np.min(vals)),
                    "max": float(np.max(vals)),
                    "n_valid": int(len(vals)),
                })

            # Free memory
            del data
            gc.collect()

    df = pd.DataFrame(all_rows)
    if str(output_path).endswith(".parquet") and _has_parquet():
        df.to_parquet(output_path, index=False)
    else:
        if not str(output_path).endswith(".csv"):
            output_path = output_path.with_suffix(".csv")
        df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df):,} rows to {output_path}")
    print(f"File size: {output_path.stat().st_size / (1024**2):.1f} MB")

    return df


# ═══════════════════════════════════════════════════════════════════════
# DATA QUALITY
# ═══════════════════════════════════════════════════════════════════════

def get_prism_data_quality_summary(data, variable=None):
    """
    Generate quality summary for a PRISM raster.

    Parameters
    ----------
    data : numpy.ndarray
        2D or 3D raster data.
    variable : str, optional
        Variable name for context.

    Returns
    -------
    dict
        Quality metrics.
    """
    total = data.size
    nodata = np.sum(data == PRISM_NODATA)
    valid = total - nodata
    valid_vals = data[data != PRISM_NODATA]

    summary = {
        "Variable": variable or "unknown",
        "Shape": str(data.shape),
        "Total pixels": f"{total:,}",
        "Valid pixels": f"{valid:,} ({100 * valid / total:.1f}%)",
        "NoData pixels": f"{nodata:,} ({100 * nodata / total:.1f}%)",
    }

    if len(valid_vals) > 0:
        summary["Mean"] = f"{np.mean(valid_vals):.2f}"
        summary["Median"] = f"{np.median(valid_vals):.2f}"
        summary["Std"] = f"{np.std(valid_vals):.2f}"
        summary["Min"] = f"{np.min(valid_vals):.2f}"
        summary["Max"] = f"{np.max(valid_vals):.2f}"

    return summary
