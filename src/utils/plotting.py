"""
Plotting utilities for consistent visualization across notebooks.
"""
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from pathlib import Path

from .constants import FIGURES_DIR, FIGURE_DPI, FIGURE_FORMAT


def setup_plotting_style():
    """
    Set up consistent matplotlib/seaborn style for all notebooks.
    """
    # Use seaborn style with some customizations
    sns.set_theme(style="whitegrid", palette="muted")

    # Customize matplotlib rcParams
    plt.rcParams.update({
        "figure.figsize": (12, 8),
        "figure.dpi": 100,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "font.family": "sans-serif",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save_figure(fig, filename, dpi=None, format=None, tight=True):
    """
    Save figure to outputs/figures directory.

    Parameters
    ----------
    fig : Figure
        Matplotlib figure to save.
    filename : str
        Filename (without directory path).
    dpi : int, optional
        Resolution. Defaults to FIGURE_DPI (300).
    format : str, optional
        File format. Defaults to FIGURE_FORMAT (png).
    tight : bool, default True
        Use tight bounding box.
    """
    if dpi is None:
        dpi = FIGURE_DPI
    if format is None:
        format = FIGURE_FORMAT

    # Ensure figures directory exists
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Add extension if not present
    if not filename.endswith(f".{format}"):
        filename = f"{filename}.{format}"

    filepath = FIGURES_DIR / filename

    bbox = "tight" if tight else None
    fig.savefig(filepath, dpi=dpi, format=format, bbox_inches=bbox, facecolor="white")
    print(f"Figure saved: {filepath}")


def get_agency_colors():
    """
    Get consistent color mapping for agencies.

    Returns
    -------
    dict
        Agency code to color mapping.
    """
    return {
        "CDF": "#E63946",      # CAL FIRE - Red
        "USF": "#457B9D",      # USDA Forest Service - Blue
        "BLM": "#F4A261",      # Bureau of Land Management - Orange
        "NPS": "#2A9D8F",      # National Park Service - Teal
        "LRA": "#E9C46A",      # Local Responsibility Area - Yellow
        "BIA": "#9B59B6",      # Bureau of Indian Affairs - Purple
        "CSP": "#1ABC9C",      # California State Parks - Cyan
        "DOD": "#34495E",      # Department of Defense - Dark Gray
        "FWS": "#8E44AD",      # Fish and Wildlife Service - Violet
        "CCO": "#27AE60",      # Contract County - Green
        "OTH": "#95A5A6",      # Other - Gray
    }


def get_cause_colors():
    """
    Get consistent color mapping for fire causes.

    Returns
    -------
    dict
        Cause code to color mapping.
    """
    return {
        1: "#F39C12",    # Lightning - Gold
        2: "#3498DB",    # Equipment Use - Blue
        3: "#9B59B6",    # Smoking - Purple
        4: "#E67E22",    # Campfire - Orange
        5: "#1ABC9C",    # Debris - Teal
        6: "#34495E",    # Railroad - Dark
        7: "#E74C3C",    # Arson - Red
        8: "#F1C40F",    # Playing with Fire - Yellow
        9: "#95A5A6",    # Miscellaneous - Gray
        10: "#2ECC71",   # Vehicle - Green
        11: "#8E44AD",   # Powerline - Violet
        14: "#BDC3C7",   # Unknown - Light Gray
    }


def get_month_labels():
    """Get month abbreviations for x-axis labels."""
    return ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def create_dual_analysis_figure(title_all, title_hq):
    """
    Create a figure with two subplots for dual analysis (all vs high-quality).

    Parameters
    ----------
    title_all : str
        Title for the "all years" subplot.
    title_hq : str
        Title for the "1993+" subplot.

    Returns
    -------
    tuple
        (fig, ax_all, ax_hq)
    """
    fig, (ax_all, ax_hq) = plt.subplots(1, 2, figsize=(16, 6))
    ax_all.set_title(title_all)
    ax_hq.set_title(title_hq)
    return fig, ax_all, ax_hq


def add_data_period_annotation(ax, start_year, end_year, n_records):
    """
    Add annotation showing data period and record count.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes.
    start_year : int
        Start year of data.
    end_year : int
        End year of data.
    n_records : int
        Number of records.
    """
    text = f"Period: {start_year}-{end_year} | Records: {n_records:,}"
    ax.annotate(
        text,
        xy=(0.02, 0.98),
        xycoords="axes fraction",
        fontsize=9,
        ha="left",
        va="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8)
    )


def format_acres(value):
    """Format acres with appropriate units."""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return f"{value:.0f}"


def get_severity_colors():
    """
    Get consistent color mapping for MTBS burn severity classes.

    Returns
    -------
    dict
        Severity class to color mapping (Green -> Yellow -> Orange -> Red).
    """
    return {
        "Increased Greenness": "#2ECC71",  # Green
        "Unburned/Low": "#F1C40F",          # Yellow
        "Low": "#F39C12",                    # Orange-Yellow
        "Moderate": "#E67E22",               # Orange
        "High": "#E74C3C",                   # Red
    }


def get_incid_type_colors():
    """
    Get consistent color mapping for MTBS incident types.

    Returns
    -------
    dict
        Incident type to color mapping.
    """
    return {
        "Wildfire": "#E63946",            # Red
        "Prescribed Fire": "#457B9D",     # Blue
        "Wildland Fire Use": "#2A9D8F",   # Teal
        "Unknown": "#95A5A6",             # Gray
    }


def get_asmnt_type_colors():
    """
    Get consistent color mapping for MTBS assessment types.

    Returns
    -------
    dict
        Assessment type to color mapping (SS variants lighter).
    """
    return {
        "Initial": "#2980B9",             # Blue
        "Initial (SS)": "#85C1E9",        # Light Blue
        "Extended": "#E74C3C",            # Red
        "Extended (SS)": "#F1948A",       # Light Red
        "Emergency": "#F39C12",           # Orange
        "Emergency (SS)": "#F8C471",      # Light Orange
    }


# ── FPA FOD Color Palettes ───────────────────────────────────────────────


def get_nwcg_cause_colors():
    """
    Get consistent color mapping for NWCG cause classification (3 categories).

    Returns
    -------
    dict
        Cause classification to color mapping.
    """
    return {
        "Human": "#E74C3C",      # Red
        "Natural": "#2ECC71",    # Green
        "Missing": "#95A5A6",    # Gray
    }


def get_general_cause_colors():
    """
    Get consistent color mapping for NWCG general cause (13 categories).

    Returns
    -------
    dict
        General cause short label to color mapping.
    """
    return {
        "Lightning": "#F1C40F",           # Gold
        "Debris Burning": "#E67E22",      # Orange
        "Equipment Use": "#3498DB",       # Blue
        "Arson": "#E74C3C",              # Red
        "Smoking": "#9B59B6",            # Purple
        "Children": "#F39C12",           # Amber
        "Railroad": "#34495E",           # Dark Gray
        "Powerline": "#8E44AD",          # Violet
        "Fireworks": "#E91E63",          # Pink
        "Firearms/Explosives": "#795548", # Brown
        "Recreation": "#1ABC9C",         # Teal
        "Other": "#BDC3C7",             # Light Gray
        "Missing/Unknown": "#95A5A6",    # Gray
    }


def get_fire_size_class_colors():
    """
    Get consistent color mapping for NWCG fire size classes A-G.

    Sequential green-to-red palette reflecting increasing fire size.

    Returns
    -------
    dict
        Size class letter to color mapping.
    """
    return {
        "A": "#2ECC71",   # Green (smallest)
        "B": "#82E0AA",   # Light Green
        "C": "#F9E79F",   # Yellow
        "D": "#F5B041",   # Orange-Yellow
        "E": "#EB984E",   # Orange
        "F": "#E74C3C",   # Red
        "G": "#922B21",   # Dark Red (largest)
    }


def get_source_system_colors():
    """
    Get consistent color mapping for FPA FOD source system types.

    Returns
    -------
    dict
        Source system type to color mapping.
    """
    return {
        "FED": "#3498DB",       # Blue
        "NONFED": "#E74C3C",    # Red
        "INTERAGCY": "#2ECC71", # Green
    }


# ── Topography Color Palettes ─────────────────────────────────────────────


def get_elevation_zone_colors():
    """
    Get consistent color mapping for elevation zones.

    Returns
    -------
    dict
        Elevation zone name to color mapping (green lowlands to white alpine).
    """
    return {
        "Valley/Coast": "#2ECC71",    # Green
        "Foothill": "#F1C40F",         # Yellow
        "Lower Montane": "#E67E22",    # Orange
        "Upper Montane": "#E74C3C",    # Red
        "Subalpine": "#9B59B6",        # Purple
        "Alpine": "#ECF0F1",           # Near-white
    }


def get_slope_class_colors():
    """
    Get consistent color mapping for slope classes.

    Returns
    -------
    dict
        Slope class to color mapping (green=flat to red=very steep).
    """
    return {
        "Flat": "#2ECC71",        # Green
        "Gentle": "#82E0AA",      # Light Green
        "Moderate": "#F9E79F",    # Yellow
        "Steep": "#E74C3C",       # Red
        "Very Steep": "#922B21",  # Dark Red
    }


def get_aspect_colors():
    """
    Get consistent color mapping for aspect directions.

    Returns
    -------
    dict
        Aspect direction to color mapping (cool blues for N, warm reds for S).
    """
    return {
        "N": "#2980B9",     # Blue (coolest)
        "NE": "#5DADE2",    # Light Blue
        "E": "#1ABC9C",     # Teal
        "SE": "#F39C12",    # Orange
        "S": "#E74C3C",     # Red (warmest)
        "SW": "#C0392B",    # Dark Red
        "W": "#8E44AD",     # Purple
        "NW": "#3498DB",    # Medium Blue
        "Flat": "#BDC3C7",  # Gray
    }


def get_tpi_colors():
    """
    Get consistent color mapping for TPI classes.

    Returns
    -------
    dict
        TPI class to color mapping (blue=valley, red=ridge).
    """
    return {
        "Valley": "#2980B9",       # Blue
        "Lower Slope": "#85C1E9",  # Light Blue
        "Flat/Mid": "#F9E79F",     # Yellow
        "Upper Slope": "#EB984E",  # Orange
        "Ridge": "#E74C3C",        # Red
    }


def get_owner_colors():
    """
    Get consistent color mapping for land ownership categories.

    Returns
    -------
    dict
        Standardized owner to color mapping.
    """
    return {
        "USFS": "#2E86C1",          # Blue
        "BLM": "#F4A261",           # Orange
        "NPS": "#2A9D8F",           # Teal
        "BIA": "#9B59B6",           # Purple
        "BOR": "#1ABC9C",           # Cyan
        "FWS": "#8E44AD",           # Violet
        "Private": "#E74C3C",       # Red
        "State": "#F1C40F",         # Yellow
        "State/Private": "#F39C12", # Amber
        "County": "#27AE60",        # Green
        "Municipal/Local": "#2ECC71", # Light Green
        "Tribal": "#D35400",        # Rust
        "Other Federal": "#34495E", # Dark
        "Other": "#BDC3C7",         # Light Gray
        "Missing": "#95A5A6",       # Gray
    }


# ── LANDFIRE CC Color Palettes ─────────────────────────────────────────


def get_canopy_cover_colors():
    """
    Get consistent color mapping for CC classes (gray → light green → dark green).

    Returns
    -------
    dict
        CC value (int) to hex color mapping.
    """
    return {
        0:  "#B0B0B0",   # Non-Forested: gray
        15: "#EAFFBF",   # 10-20%: very light green
        25: "#BBE695",   # 20-30%: light green
        35: "#8CC96D",   # 30-40%: medium-light green
        45: "#62B04A",   # 40-50%: medium green
        55: "#3B992B",   # 50-60%: green
        65: "#008000",   # 60-70%: forest green
        75: "#0F5C0B",   # 70-80%: dark green
        85: "#113D0C",   # 80-90%: very dark green
        95: "#10240C",   # 90-100%: darkest green
    }


def get_canopy_broad_colors():
    """
    Get consistent color mapping for broad CC categories (5 groups).

    Returns
    -------
    dict
        Broad category name to hex color mapping.
    """
    return {
        "Non-Forested":         "#B0B0B0",
        "Open (10-30%)":        "#BFEE9F",
        "Moderate (30-60%)":    "#62B34A",
        "Dense (60-80%)":       "#0E5C0B",
        "Very Dense (80-100%)": "#103008",
    }


# ── FVEG22 Vegetation Color Palettes ──────────────────────────────────


def get_lifeform_colors():
    """
    Get consistent color mapping for CWHR lifeform categories (8 classes).

    Returns
    -------
    dict
        Lifeform name to hex color mapping.
    """
    return {
        "CONIFER":      "#1B7837",  # Dark green
        "HARDWOOD":     "#7FBC41",  # Medium green
        "SHRUB":        "#D9A441",  # Amber
        "HERBACEOUS":   "#F7E353",  # Yellow
        "AGRICULTURE":  "#F4A261",  # Orange
        "URBAN":        "#95A5A6",  # Gray
        "WATER":        "#3498DB",  # Blue
        "BARREN/OTHER": "#BDC3C7",  # Light gray
    }


def get_whr13_colors():
    """
    Get consistent color mapping for WHR13 aggregated classes (13 classes).

    Returns
    -------
    dict
        WHR13 name to hex color mapping.
    """
    return {
        "Conifer Forest":     "#1B7837",  # Dark green
        "Conifer Woodland":   "#41AB5D",  # Medium green
        "Hardwood Forest":    "#78C679",  # Light green
        "Hardwood Woodland":  "#ADDD8E",  # Pale green
        "Desert Woodland":    "#C2B280",  # Tan
        "Shrub":              "#D9A441",  # Amber
        "Desert Shrub":       "#E8C36A",  # Light amber
        "Herbaceous":         "#F7E353",  # Yellow
        "Wetland":            "#1ABC9C",  # Teal
        "Agriculture":        "#F4A261",  # Orange
        "Urban":              "#95A5A6",  # Gray
        "Water":              "#3498DB",  # Blue
        "Barren/Other":       "#BDC3C7",  # Light gray
    }


def get_fire_risk_colors():
    """
    Get consistent color mapping for fire risk levels (4 levels).

    Returns
    -------
    dict
        Fire risk level to hex color mapping.
    """
    return {
        "High":       "#E74C3C",  # Red
        "Moderate":   "#F39C12",  # Orange
        "Low":        "#2ECC71",  # Green
        "Negligible": "#3498DB",  # Blue
    }


# ── PRISM Climate Color Palettes ─────────────────────────────────────


def get_prism_variable_colors():
    """
    Get consistent color mapping for PRISM climate variables (7 variables).

    Returns
    -------
    dict
        Variable name to hex color mapping.
    """
    return {
        "ppt":    "#3498DB",  # Blue (precipitation)
        "tmax":   "#E74C3C",  # Red (hot)
        "tmin":   "#2980B9",  # Medium Blue (cool)
        "tmean":  "#E67E22",  # Orange (mean temp)
        "tdmean": "#1ABC9C",  # Teal (dew point)
        "vpdmax": "#C0392B",  # Dark Red (max VPD)
        "vpdmin": "#D4A574",  # Tan (min VPD)
    }


def get_vpd_risk_colors():
    """
    Get consistent color mapping for VPD fire weather risk classes (6 classes).

    Returns
    -------
    dict
        VPD risk class to hex color mapping (green→red scale).
    """
    return {
        "Minimal":     "#2ECC71",  # Green
        "Low":         "#82E0AA",  # Light Green
        "Moderate":    "#F9E79F",  # Yellow
        "High":        "#F5B041",  # Orange
        "Extreme":     "#E74C3C",  # Red
        "Exceptional": "#922B21",  # Dark Red
    }


def get_drought_colors():
    """
    Get consistent color mapping for drought severity classes (7 classes).

    Returns
    -------
    dict
        Drought class to hex color mapping (brown→blue scale).
    """
    return {
        "Extreme Drought":  "#8B4513",  # Brown
        "Severe Drought":   "#CD853F",  # Peru
        "Moderate Drought":  "#DEB887",  # Burlywood
        "Near Normal":      "#F5F5DC",  # Beige
        "Moderately Wet":   "#87CEEB",  # Sky Blue
        "Very Wet":         "#4682B4",  # Steel Blue
        "Extremely Wet":    "#191970",  # Midnight Blue
    }


def get_climate_season_colors():
    """
    Get consistent color mapping for meteorological seasons (4 seasons).

    Returns
    -------
    dict
        Season name to hex color mapping.
    """
    return {
        "Winter": "#3498DB",  # Blue
        "Spring": "#2ECC71",  # Green
        "Summer": "#E74C3C",  # Red
        "Fall":   "#F39C12",  # Orange
    }


def get_prism_diverging_norm(vmin, vcenter, vmax):
    """
    Create a TwoSlopeNorm for diverging PRISM anomaly maps.

    Parameters
    ----------
    vmin : float
        Minimum value.
    vcenter : float
        Center value (typically 0 for difference anomalies, 100 for % of normal).
    vmax : float
        Maximum value.

    Returns
    -------
    matplotlib.colors.TwoSlopeNorm
    """
    return mcolors.TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
