"""
Data loading and processing utilities for the FPA FOD (Fire Program Analysis -
Fire Occurrence Database), 6th edition.

FPA FOD is a national compilation of 2.3 million wildfire records (1992-2020) from
federal, state, and local reporting systems. The dataset captures the full fire size
spectrum (93% of CA fires are under 10 acres), unlike MTBS (>= 1,000 acres) or
CAL FIRE perimeters.

IMPORTANT: The 885 MB GeoPackage supports SQL WHERE filtering at load time.
Always use the `state` parameter to avoid loading the full 2.3M-record dataset.
"""
import gc

import geopandas as gpd
import numpy as np
import pandas as pd
from pathlib import Path

from .constants import (
    FPA_FOD_PATH, CRS_ALBERS, CRS_NAD83,
    FPA_START_YEAR, FPA_END_YEAR,
    MEGA_FIRE_THRESHOLD, LARGE_FIRE_THRESHOLD,
)
from .fpa_domain_mappings import (
    get_nwcg_cause_label, get_general_cause_label,
    get_owner_standardized, FIRE_SEASON_MAP,
)


def load_fpa_fod(path=None, state=None, layer="Fires"):
    """
    Load the FPA FOD GeoPackage with efficient SQL WHERE filtering.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoPackage. Defaults to FPA_FOD_PATH.
    state : str, optional
        Two-letter state code to filter (e.g., 'CA'). STRONGLY recommended
        to avoid loading all 2.3M records.
    layer : str, default "Fires"
        GeoPackage layer name.

    Returns
    -------
    GeoDataFrame
        FPA FOD fire occurrence data.
    """
    if path is None:
        path = FPA_FOD_PATH

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"FPA FOD GeoPackage not found: {path}")

    where = None
    if state is not None:
        state = state.upper()
        where = f"STATE = '{state}'"

    gdf = gpd.read_file(path, layer=layer, where=where)
    return gdf


def load_fpa_national_summary(path=None, columns=None):
    """
    Load minimal national FPA FOD data for state comparison.

    Only loads specified columns to minimize memory usage on the full 2.3M dataset.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoPackage. Defaults to FPA_FOD_PATH.
    columns : list, optional
        Columns to load. Defaults to minimal set for state comparison.

    Returns
    -------
    GeoDataFrame
        National FPA FOD data with minimal columns.
    """
    if path is None:
        path = FPA_FOD_PATH

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"FPA FOD GeoPackage not found: {path}")

    if columns is None:
        columns = ["STATE", "FIRE_YEAR", "FIRE_SIZE", "FIRE_SIZE_CLASS"]

    gdf = gpd.read_file(path, layer="Fires", columns=columns)
    return gdf


def load_fpa_unit_metadata(path=None):
    """
    Load NWCG unit reference table from FPA FOD GeoPackage.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoPackage. Defaults to FPA_FOD_PATH.

    Returns
    -------
    DataFrame
        NWCG unit metadata (non-spatial table).
    """
    if path is None:
        path = FPA_FOD_PATH

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"FPA FOD GeoPackage not found: {path}")

    df = gpd.read_file(path, layer="NWCG_UnitIdActive_20200123")
    return pd.DataFrame(df.drop(columns="geometry", errors="ignore"))


def add_fpa_derived_columns(gdf):
    """
    Add derived columns useful for FPA FOD analysis.

    Adds: Discovery_Date (datetime), Discovery_Year, Discovery_Month,
    Discovery_DayOfYear, Discovery_Hour, Decade, Log10_FireSize,
    Size_Category, Fire_Season, Duration_Days, has_containment,
    has_county, has_mtbs_linkage, Cause_Label, General_Cause_Label,
    Owner_Std.

    Parameters
    ----------
    gdf : GeoDataFrame
        FPA FOD fire occurrence data.

    Returns
    -------
    GeoDataFrame
        Data with additional derived columns.
    """
    gdf = gdf.copy()

    # Parse discovery date
    if "DISCOVERY_DATE" in gdf.columns:
        gdf["Discovery_Date"] = pd.to_datetime(
            gdf["DISCOVERY_DATE"], format="mixed", errors="coerce"
        )
        gdf["Discovery_Year"] = gdf["FIRE_YEAR"]  # Use FIRE_YEAR (more reliable)
        gdf["Discovery_Month"] = gdf["Discovery_Date"].dt.month
        gdf["Discovery_DayOfYear"] = gdf["DISCOVERY_DOY"]

    # Parse discovery time to hour (HHMM format string)
    if "DISCOVERY_TIME" in gdf.columns:
        def _parse_time_to_hour(t):
            if pd.isna(t) or t is None:
                return np.nan
            t_str = str(t).strip()
            if len(t_str) == 4 and t_str.isdigit():
                return int(t_str[:2])
            if len(t_str) == 3 and t_str.isdigit():
                return int(t_str[0])
            return np.nan
        gdf["Discovery_Hour"] = gdf["DISCOVERY_TIME"].apply(_parse_time_to_hour)

    # Parse containment date
    if "CONT_DATE" in gdf.columns:
        gdf["Cont_Date"] = pd.to_datetime(
            gdf["CONT_DATE"], format="mixed", errors="coerce"
        )

    # Duration in days (discovery to containment)
    if "Discovery_Date" in gdf.columns and "Cont_Date" in gdf.columns:
        duration = (gdf["Cont_Date"] - gdf["Discovery_Date"]).dt.total_seconds() / 86400
        gdf["Duration_Days"] = duration.where(duration >= 0)

    # Decade
    if "FIRE_YEAR" in gdf.columns:
        gdf["Decade"] = (gdf["FIRE_YEAR"] // 10) * 10

    # Log-transformed fire size
    if "FIRE_SIZE" in gdf.columns:
        gdf["Log10_FireSize"] = np.log10(gdf["FIRE_SIZE"].clip(lower=0.01))

    # Fire size category (compatible with MTBS categories)
    if "FIRE_SIZE" in gdf.columns:
        def _categorize_size(acres):
            if pd.isna(acres):
                return "Unknown"
            elif acres >= MEGA_FIRE_THRESHOLD:
                return "Mega (100K+)"
            elif acres >= LARGE_FIRE_THRESHOLD:
                return "Large (10K-100K)"
            elif acres >= 1000:
                return "Medium (1K-10K)"
            elif acres >= 100:
                return "Small (100-1K)"
            elif acres >= 10:
                return "Minor (10-100)"
            else:
                return "Tiny (<10)"
        gdf["Size_Category"] = gdf["FIRE_SIZE"].apply(_categorize_size)

    # Fire season classification
    if "Discovery_Month" in gdf.columns:
        gdf["Fire_Season"] = gdf["Discovery_Month"].map(FIRE_SEASON_MAP).fillna("Unknown")

    # Data availability flags
    if "CONT_DATE" in gdf.columns:
        gdf["has_containment"] = gdf["CONT_DATE"].notna()

    if "COUNTY" in gdf.columns:
        gdf["has_county"] = gdf["COUNTY"].notna()

    if "MTBS_ID" in gdf.columns:
        gdf["has_mtbs_linkage"] = gdf["MTBS_ID"].notna()

    # Domain labels
    if "NWCG_CAUSE_CLASSIFICATION" in gdf.columns:
        gdf["Cause_Label"] = gdf["NWCG_CAUSE_CLASSIFICATION"].apply(get_nwcg_cause_label)

    if "NWCG_GENERAL_CAUSE" in gdf.columns:
        gdf["General_Cause_Label"] = gdf["NWCG_GENERAL_CAUSE"].apply(get_general_cause_label)

    if "OWNER_DESCR" in gdf.columns:
        gdf["Owner_Std"] = gdf["OWNER_DESCR"].apply(get_owner_standardized)

    return gdf


def reproject_to_albers(gdf):
    """
    Reproject GeoDataFrame from NAD83 to California Albers (EPSG:3310).

    Parameters
    ----------
    gdf : GeoDataFrame
        Data in NAD83 or other CRS.

    Returns
    -------
    GeoDataFrame
        Data reprojected to EPSG:3310.
    """
    return gdf.to_crs(CRS_ALBERS)


def get_fpa_data_quality_summary(gdf):
    """
    Generate a summary of FPA FOD data quality metrics.

    Parameters
    ----------
    gdf : GeoDataFrame
        FPA FOD fire occurrence data (with derived columns).

    Returns
    -------
    dict
        Quality metrics including completeness, availability flags, etc.
    """
    n = len(gdf)

    summary = {
        "Total Records": n,
        "Year Range": (
            f"{gdf['FIRE_YEAR'].min()} - {gdf['FIRE_YEAR'].max()}"
            if "FIRE_YEAR" in gdf.columns else "N/A"
        ),
        "Total Acres": f"{gdf['FIRE_SIZE'].sum():,.0f}" if "FIRE_SIZE" in gdf.columns else "N/A",
    }

    # Field completeness
    key_fields = [
        "FOD_ID", "FIRE_YEAR", "DISCOVERY_DATE", "FIRE_SIZE", "FIRE_SIZE_CLASS",
        "NWCG_CAUSE_CLASSIFICATION", "NWCG_GENERAL_CAUSE", "NWCG_REPORTING_AGENCY",
        "OWNER_DESCR", "STATE", "COUNTY", "FIPS_CODE", "CONT_DATE",
        "DISCOVERY_TIME", "MTBS_ID", "FIRE_NAME",
    ]
    for field in key_fields:
        if field in gdf.columns:
            non_null = gdf[field].notna().sum()
            summary[f"{field} populated"] = f"{non_null:,} ({100 * non_null / n:.1f}%)"

    # Derived flags
    if "has_containment" in gdf.columns:
        cnt = gdf["has_containment"].sum()
        summary["Has containment date"] = f"{cnt:,} ({100 * cnt / n:.1f}%)"

    if "has_county" in gdf.columns:
        cnt = gdf["has_county"].sum()
        summary["Has county info"] = f"{cnt:,} ({100 * cnt / n:.1f}%)"

    if "has_mtbs_linkage" in gdf.columns:
        cnt = gdf["has_mtbs_linkage"].sum()
        summary["Has MTBS linkage"] = f"{cnt:,} ({100 * cnt / n:.1f}%)"

    # Geometry validity
    if gdf.geometry is not None and not gdf.geometry.isna().all():
        summary["Invalid geometries"] = int((~gdf.geometry.is_valid).sum())
        summary["Empty geometries"] = int(gdf.geometry.is_empty.sum())

    return summary
