"""
Data loading and processing utilities for the MTBS Fire Occurrence Dataset.

MTBS (Monitoring Trends in Burn Severity) is a USGS/USDA Forest Service program
that maps all large fires (>= 1,000 acres western US, >= 500 acres eastern US)
using Landsat/Sentinel satellite imagery from 1984-present.

IMPORTANT: The point geometries in this dataset represent burned-area centroids,
NOT ignition points.
"""
import geopandas as gpd
import numpy as np
import pandas as pd
from pathlib import Path

from .constants import (
    MTBS_FOD_PATH, CRS_ALBERS, CRS_NAD83,
    MTBS_NODATA_SENTINEL, MTBS_START_YEAR, MTBS_END_YEAR,
    MEGA_FIRE_THRESHOLD, LARGE_FIRE_THRESHOLD,
)
from .mtbs_domain_mappings import get_state_from_event_id


def load_mtbs_fod(path=None, state=None):
    """
    Load the MTBS Fire Occurrence Database shapefile.

    Parameters
    ----------
    path : str or Path, optional
        Path to shapefile. Defaults to MTBS_FOD_PATH.
    state : str, optional
        Two-letter state code to filter (e.g., 'CA'). If None, loads all states.

    Returns
    -------
    GeoDataFrame
        MTBS fire occurrence data with State column added.
    """
    if path is None:
        path = MTBS_FOD_PATH

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"MTBS shapefile not found: {path}")

    gdf = gpd.read_file(path)

    # Extract State from Event_ID prefix
    gdf["State"] = gdf["Event_ID"].apply(get_state_from_event_id)

    # Filter by state if requested
    if state is not None:
        state = state.upper()
        gdf = gdf[gdf["State"] == state].copy()

    return gdf


def add_mtbs_derived_columns(gdf):
    """
    Add derived columns useful for MTBS analysis.

    Adds: Ig_Date (datetime), Ig_Year, Ig_Month, Ig_DayOfYear, Ig_Decade,
    Log10_BurnBndAc, Size_Category, Fire_Season, severity-cleaned columns,
    has_severity flag, severity_range.

    Parameters
    ----------
    gdf : GeoDataFrame
        MTBS fire occurrence data.

    Returns
    -------
    GeoDataFrame
        Data with additional derived columns.
    """
    gdf = gdf.copy()

    # Parse ignition date
    if "Ig_Date" in gdf.columns:
        gdf["Ig_Date"] = pd.to_datetime(gdf["Ig_Date"], errors="coerce")
        gdf["Ig_Year"] = gdf["Ig_Date"].dt.year
        gdf["Ig_Month"] = gdf["Ig_Date"].dt.month
        gdf["Ig_DayOfYear"] = gdf["Ig_Date"].dt.dayofyear

    # Add decade
    if "Ig_Year" in gdf.columns:
        gdf["Ig_Decade"] = (gdf["Ig_Year"] // 10) * 10

    # Log-transformed burned area
    if "BurnBndAc" in gdf.columns:
        gdf["Log10_BurnBndAc"] = np.log10(gdf["BurnBndAc"].clip(lower=0.1))

    # Fire size category
    if "BurnBndAc" in gdf.columns:
        def _categorize_size(acres):
            if pd.isna(acres):
                return "Unknown"
            elif acres >= MEGA_FIRE_THRESHOLD:
                return "Mega (100K+)"
            elif acres >= LARGE_FIRE_THRESHOLD:
                return "Large (10K-100K)"
            elif acres >= 1000:
                return "Medium (1K-10K)"
            else:
                return "Small (<1K)"
        gdf["Size_Category"] = gdf["BurnBndAc"].apply(_categorize_size)

    # Fire season classification
    if "Ig_Month" in gdf.columns:
        def _classify_season(month):
            if pd.isna(month):
                return "Unknown"
            month = int(month)
            if month in (6, 7, 8, 9):
                return "High Risk"
            elif month in (10, 11, 12, 1):
                return "Transition"
            else:
                return "Low Risk"
        gdf["Fire_Season"] = gdf["Ig_Month"].apply(_classify_season)

    # Clean severity threshold fields (replace sentinels with NaN)
    severity_cols = ["dNBR_offst", "dNBR_stdDv", "NoData_T",
                     "IncGreen_T", "Low_T", "Mod_T", "High_T"]
    for col in severity_cols:
        if col in gdf.columns:
            clean_col = f"{col}_clean"
            gdf[clean_col] = gdf[col].copy()
            gdf.loc[gdf[clean_col].isin(MTBS_NODATA_SENTINEL), clean_col] = np.nan

    # Has severity flag
    if "High_T" in gdf.columns:
        gdf["has_severity"] = ~gdf["High_T_clean"].isna()

    # Severity range (High_T - Low_T)
    if "High_T_clean" in gdf.columns and "Low_T_clean" in gdf.columns:
        gdf["severity_range"] = gdf["High_T_clean"] - gdf["Low_T_clean"]

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


def get_mtbs_data_quality_summary(gdf):
    """
    Generate a summary of MTBS data quality metrics.

    Parameters
    ----------
    gdf : GeoDataFrame
        MTBS fire occurrence data (with derived columns).

    Returns
    -------
    dict
        Quality metrics including completeness, severity availability, etc.
    """
    n = len(gdf)

    summary = {
        "Total Records": n,
        "Year Range": f"{gdf['Ig_Year'].min():.0f} - {gdf['Ig_Year'].max():.0f}" if "Ig_Year" in gdf.columns else "N/A",
        "States": gdf["State"].nunique() if "State" in gdf.columns else "N/A",
    }

    # Field completeness
    key_fields = ["Event_ID", "Ig_Date", "BurnBndAc", "Incid_Name",
                  "Incid_Type", "Asmnt_Type"]
    for field in key_fields:
        if field in gdf.columns:
            non_null = gdf[field].notna().sum()
            summary[f"{field} populated"] = f"{non_null:,} ({100*non_null/n:.1f}%)"

    # Severity data availability
    if "has_severity" in gdf.columns:
        sev_count = gdf["has_severity"].sum()
        summary["Has severity data"] = f"{sev_count:,} ({100*sev_count/n:.1f}%)"

    # Geometry validity
    summary["Invalid geometries"] = (~gdf.geometry.is_valid).sum()
    summary["Empty geometries"] = gdf.geometry.is_empty.sum()

    return summary
