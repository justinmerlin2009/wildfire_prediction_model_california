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
