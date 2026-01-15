"""
Data loading utilities for California Fire Perimeters GeoPackage.
"""
import geopandas as gpd
import pandas as pd
from pathlib import Path

from .constants import FIRE_PERIMETERS_PATH, CRS_ALBERS, HIGH_QUALITY_CUTOFF
from .domain_mappings import (
    CAUSE_MAP, AGENCY_MAP, C_METHOD_MAP, UNIT_ID_MAP,
    get_cause_label, get_agency_label, get_c_method_label
)


def load_fire_perimeters(
    path=None,
    year_min=None,
    year_max=None,
    high_quality_only=False
):
    """
    Load fire perimeters from GeoPackage.

    Parameters
    ----------
    path : str or Path, optional
        Path to GeoPackage. Defaults to FIRE_PERIMETERS_PATH.
    year_min : int, optional
        Minimum year to include (inclusive).
    year_max : int, optional
        Maximum year to include (inclusive).
    high_quality_only : bool, default False
        If True, only load data from 1993+ (higher quality data).

    Returns
    -------
    GeoDataFrame
        Fire perimeters with geometry and attributes.
    """
    if path is None:
        path = FIRE_PERIMETERS_PATH

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"GeoPackage not found: {path}")

    # Load the GeoPackage
    gdf = gpd.read_file(path)

    # Apply year filters
    if high_quality_only:
        year_min = max(year_min or HIGH_QUALITY_CUTOFF, HIGH_QUALITY_CUTOFF)

    if year_min is not None:
        gdf = gdf[gdf["YEAR_"] >= year_min]

    if year_max is not None:
        gdf = gdf[gdf["YEAR_"] <= year_max]

    return gdf


def add_derived_columns(gdf):
    """
    Add derived columns useful for analysis.

    Parameters
    ----------
    gdf : GeoDataFrame
        Fire perimeters data.

    Returns
    -------
    GeoDataFrame
        Data with additional columns.
    """
    gdf = gdf.copy()

    # Extract month from ALARM_DATE
    if "ALARM_DATE" in gdf.columns:
        gdf["ALARM_MONTH"] = pd.to_datetime(gdf["ALARM_DATE"], errors="coerce").dt.month
        gdf["ALARM_DAY_OF_YEAR"] = pd.to_datetime(gdf["ALARM_DATE"], errors="coerce").dt.dayofyear

    # Calculate fire duration in days
    if "ALARM_DATE" in gdf.columns and "CONT_DATE" in gdf.columns:
        alarm = pd.to_datetime(gdf["ALARM_DATE"], errors="coerce")
        cont = pd.to_datetime(gdf["CONT_DATE"], errors="coerce")
        gdf["DURATION_DAYS"] = (cont - alarm).dt.days

    # Add decade column
    if "YEAR_" in gdf.columns:
        gdf["DECADE"] = (gdf["YEAR_"] // 10) * 10

    # Log-transformed acres for visualization
    if "GIS_ACRES" in gdf.columns:
        import numpy as np
        gdf["LOG10_ACRES"] = np.log10(gdf["GIS_ACRES"].clip(lower=0.1))

    # Fire size category
    if "GIS_ACRES" in gdf.columns:
        def categorize_size(acres):
            if pd.isna(acres):
                return "Unknown"
            elif acres >= 100000:
                return "Mega (100K+)"
            elif acres >= 10000:
                return "Large (10K-100K)"
            elif acres >= 1000:
                return "Medium (1K-10K)"
            elif acres >= 100:
                return "Small (100-1K)"
            else:
                return "Very Small (<100)"

        gdf["SIZE_CATEGORY"] = gdf["GIS_ACRES"].apply(categorize_size)

    return gdf


def apply_domain_labels(gdf):
    """
    Add human-readable labels for coded fields.

    Parameters
    ----------
    gdf : GeoDataFrame
        Fire perimeters data.

    Returns
    -------
    GeoDataFrame
        Data with label columns added.
    """
    gdf = gdf.copy()

    # Add cause labels
    if "CAUSE" in gdf.columns:
        gdf["CAUSE_LABEL"] = gdf["CAUSE"].apply(get_cause_label)

    # Add agency labels
    if "AGENCY" in gdf.columns:
        gdf["AGENCY_LABEL"] = gdf["AGENCY"].apply(get_agency_label)

    # Add collection method labels
    if "C_METHOD" in gdf.columns:
        gdf["C_METHOD_LABEL"] = gdf["C_METHOD"].apply(get_c_method_label)

    # Add unit labels (keep original code too as it's commonly used)
    if "UNIT_ID" in gdf.columns:
        gdf["UNIT_LABEL"] = gdf["UNIT_ID"].map(UNIT_ID_MAP).fillna(gdf["UNIT_ID"])

    return gdf


def get_data_quality_summary(gdf):
    """
    Generate a summary of data quality metrics.

    Parameters
    ----------
    gdf : GeoDataFrame
        Fire perimeters data.

    Returns
    -------
    DataFrame
        Summary statistics for data quality.
    """
    summary = {
        "Total Records": len(gdf),
        "Year Range": f"{gdf['YEAR_'].min()} - {gdf['YEAR_'].max()}",
        "Missing ALARM_DATE": gdf["ALARM_DATE"].isna().sum(),
        "Missing CONT_DATE": gdf["CONT_DATE"].isna().sum(),
        "Missing CAUSE": gdf["CAUSE"].isna().sum(),
        "Missing GIS_ACRES": gdf["GIS_ACRES"].isna().sum(),
        "Invalid Geometries": (~gdf.geometry.is_valid).sum(),
        "Empty Geometries": gdf.geometry.is_empty.sum(),
    }

    # Add C_METHOD breakdown if available
    if "C_METHOD" in gdf.columns:
        c_method_counts = gdf["C_METHOD"].value_counts()
        summary["C_METHOD Distribution"] = c_method_counts.to_dict()

    return pd.DataFrame([summary])


def split_by_quality(gdf, cutoff_year=None):
    """
    Split data into historical and high-quality subsets.

    Parameters
    ----------
    gdf : GeoDataFrame
        Fire perimeters data.
    cutoff_year : int, optional
        Year to split on. Defaults to HIGH_QUALITY_CUTOFF (1993).

    Returns
    -------
    tuple
        (historical_gdf, high_quality_gdf)
    """
    if cutoff_year is None:
        cutoff_year = HIGH_QUALITY_CUTOFF

    historical = gdf[gdf["YEAR_"] < cutoff_year].copy()
    high_quality = gdf[gdf["YEAR_"] >= cutoff_year].copy()

    return historical, high_quality
