"""
Domain value mappings for LANDFIRE 2024 Forest Canopy Cover (CC) analysis.

Defines CC value labels, RGB colors (from LANDFIRE CSV), broad categories,
and helper functions for classification and colormap construction.

LANDFIRE CC values represent tree canopy cover percentage at 30m resolution.
Values are class midpoints: 0 (Non-Forested), 15 (10-20%), 25 (20-30%), etc.
"""
import numpy as np
import matplotlib.colors as mcolors

# ── CC Value Mappings ──────────────────────────────────────────────────

CC_VALUE_MAP = {
    -9999: "Fill-NoData",
    0: "Non-Forested",
    15: "10-20%",
    25: "20-30%",
    35: "30-40%",
    45: "40-50%",
    55: "50-60%",
    65: "60-70%",
    75: "70-80%",
    85: "80-90%",
    95: "90-100%",
}

# Midpoint percentages for continuous conversion
CC_MIDPOINT_MAP = {
    0: 0,
    15: 15,
    25: 25,
    35: 35,
    45: 45,
    55: 55,
    65: 65,
    75: 75,
    85: 85,
    95: 95,
}

# Ordered list of valid CC values (excluding NoData)
CC_ORDERED_VALUES = [0, 15, 25, 35, 45, 55, 65, 75, 85, 95]

# ── RGB Color Map (from LANDFIRE CSV, normalized 0-1) ─────────────────

CC_RGB_MAP = {
    -9999: (1.000, 1.000, 1.000),  # Fill-NoData: white
    0:     (0.690, 0.690, 0.690),  # Non-Forested: gray
    15:    (0.918, 1.000, 0.749),  # 10-20%: very light green
    25:    (0.733, 0.902, 0.584),  # 20-30%: light green
    35:    (0.549, 0.788, 0.427),  # 30-40%: medium-light green
    45:    (0.384, 0.690, 0.290),  # 40-50%: medium green
    55:    (0.231, 0.600, 0.169),  # 50-60%: green
    65:    (0.000, 0.502, 0.000),  # 60-70%: forest green
    75:    (0.059, 0.361, 0.043),  # 70-80%: dark green
    85:    (0.067, 0.239, 0.047),  # 80-90%: very dark green
    95:    (0.063, 0.141, 0.047),  # 90-100%: darkest green
}

# ── Broad Categories ──────────────────────────────────────────────────

CC_BROAD_CATEGORIES = {
    0:  "Non-Forested",
    15: "Open (10-30%)",
    25: "Open (10-30%)",
    35: "Moderate (30-60%)",
    45: "Moderate (30-60%)",
    55: "Moderate (30-60%)",
    65: "Dense (60-80%)",
    75: "Dense (60-80%)",
    85: "Very Dense (80-100%)",
    95: "Very Dense (80-100%)",
}

CC_BROAD_CATEGORY_ORDER = [
    "Non-Forested",
    "Open (10-30%)",
    "Moderate (30-60%)",
    "Dense (60-80%)",
    "Very Dense (80-100%)",
]

CC_BROAD_CATEGORY_COLORS = {
    "Non-Forested":       "#B0B0B0",  # Gray
    "Open (10-30%)":      "#BFEE9F",  # Light green
    "Moderate (30-60%)":  "#62B34A",  # Medium green
    "Dense (60-80%)":     "#0E5C0B",  # Dark green
    "Very Dense (80-100%)": "#103008",  # Very dark green
}


# ── Helper Functions ───────────────────────────────────────────────────

def get_cc_label(value):
    """
    Get descriptive label for a CC value.

    Parameters
    ----------
    value : int
        CC pixel value (-9999, 0, 15, 25, ..., 95).

    Returns
    -------
    str
        Descriptive label.
    """
    return CC_VALUE_MAP.get(value, f"Unknown ({value})")


def get_cc_color(value):
    """
    Get RGB color tuple for a CC value.

    Parameters
    ----------
    value : int
        CC pixel value.

    Returns
    -------
    tuple
        (R, G, B) normalized to 0-1.
    """
    return CC_RGB_MAP.get(value, (0.5, 0.5, 0.5))


def get_cc_broad_category(value):
    """
    Get broad category for a CC value.

    Parameters
    ----------
    value : int
        CC pixel value (0, 15, 25, ..., 95).

    Returns
    -------
    str
        Broad category name.
    """
    return CC_BROAD_CATEGORIES.get(value, "Unknown")


def build_cc_colormap():
    """
    Build a matplotlib ListedColormap from LANDFIRE CC RGB values.

    Returns
    -------
    matplotlib.colors.ListedColormap
        Colormap for CC values (10 classes, excluding NoData).
    """
    colors = [CC_RGB_MAP[v] for v in CC_ORDERED_VALUES]
    return mcolors.ListedColormap(colors, name="landfire_cc")


def build_cc_norm():
    """
    Build a matplotlib BoundaryNorm for CC values.

    Returns
    -------
    matplotlib.colors.BoundaryNorm
        Norm mapping CC values to colormap indices.
    """
    # Boundaries between classes: midpoints between consecutive CC values
    boundaries = [
        -0.5,   # below 0
        7.5,    # between 0 and 15
        20.0,   # between 15 and 25
        30.0,   # between 25 and 35
        40.0,   # between 35 and 45
        50.0,   # between 45 and 55
        60.0,   # between 55 and 65
        70.0,   # between 65 and 75
        80.0,   # between 75 and 85
        90.0,   # between 85 and 95
        100.5,  # above 95
    ]
    return mcolors.BoundaryNorm(boundaries, len(CC_ORDERED_VALUES))


def classify_canopy_cover(cc_values):
    """
    Classify CC pixel values into broad categories.

    Parameters
    ----------
    cc_values : array-like or scalar
        CC pixel values (0, 15, 25, ..., 95).

    Returns
    -------
    numpy.ndarray or str
        Broad category labels.
    """
    arr = np.asarray(cc_values)
    scalar = arr.ndim == 0
    arr = np.atleast_1d(arr)

    result = np.full(arr.shape, "Unknown", dtype=object)
    result[arr == 0] = "Non-Forested"
    result[(arr >= 10) & (arr < 30)] = "Open (10-30%)"
    result[(arr >= 30) & (arr < 60)] = "Moderate (30-60%)"
    result[(arr >= 60) & (arr < 80)] = "Dense (60-80%)"
    result[(arr >= 80) & (arr <= 100)] = "Very Dense (80-100%)"

    return result.item() if scalar else result
