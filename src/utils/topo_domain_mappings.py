"""
Domain value mappings for topographic analysis of California.

Defines ecological elevation zones, slope classes, aspect directions,
and topographic position index (TPI) classes used for terrain classification
and wildfire risk analysis.
"""
import numpy as np

# ── Elevation Zones ──────────────────────────────────────────────────────
# Ecologically meaningful elevation bands for California
# Based on Jepson ecoregion elevation transitions

ELEVATION_ZONE_MAP = {
    "Valley/Coast": {"min": -100, "max": 300, "description": "Central Valley, coastal plains, deserts below 300m"},
    "Foothill": {"min": 300, "max": 900, "description": "Oak woodlands, chaparral transition zone"},
    "Lower Montane": {"min": 900, "max": 1800, "description": "Mixed conifer forests, ponderosa pine zone"},
    "Upper Montane": {"min": 1800, "max": 2700, "description": "Red fir, lodgepole pine forests"},
    "Subalpine": {"min": 2700, "max": 3500, "description": "Whitebark pine, mountain hemlock, treeline zone"},
    "Alpine": {"min": 3500, "max": 5000, "description": "Above treeline, rock and meadow"},
}

ELEVATION_ZONE_ORDER = [
    "Valley/Coast", "Foothill", "Lower Montane",
    "Upper Montane", "Subalpine", "Alpine",
]

ELEVATION_ZONE_THRESHOLDS = [300, 900, 1800, 2700, 3500]  # meters

# ── Slope Classes ────────────────────────────────────────────────────────
# Slope steepness categories in degrees

SLOPE_CLASS_MAP = {
    "Flat": {"min": 0, "max": 5, "description": "Level terrain, minimal slope effect on fire"},
    "Gentle": {"min": 5, "max": 15, "description": "Mild slopes, moderate fire spread enhancement"},
    "Moderate": {"min": 15, "max": 30, "description": "Significant slopes, substantial fire acceleration"},
    "Steep": {"min": 30, "max": 45, "description": "Steep terrain, rapid uphill fire spread"},
    "Very Steep": {"min": 45, "max": 90, "description": "Cliff-like terrain, extreme fire behavior"},
}

SLOPE_CLASS_ORDER = ["Flat", "Gentle", "Moderate", "Steep", "Very Steep"]

SLOPE_CLASS_THRESHOLDS = [5, 15, 30, 45]  # degrees

# ── Aspect Classes ───────────────────────────────────────────────────────
# 8 cardinal/ordinal compass directions + Flat

ASPECT_CLASS_MAP = {
    "N": {"min": 337.5, "max": 22.5, "description": "North-facing, cooler & moister"},
    "NE": {"min": 22.5, "max": 67.5, "description": "Northeast-facing"},
    "E": {"min": 67.5, "max": 112.5, "description": "East-facing, morning sun"},
    "SE": {"min": 112.5, "max": 157.5, "description": "Southeast-facing"},
    "S": {"min": 157.5, "max": 202.5, "description": "South-facing, hottest & driest"},
    "SW": {"min": 202.5, "max": 247.5, "description": "Southwest-facing, afternoon heat"},
    "W": {"min": 247.5, "max": 292.5, "description": "West-facing, afternoon sun"},
    "NW": {"min": 292.5, "max": 337.5, "description": "Northwest-facing"},
    "Flat": {"min": None, "max": None, "description": "Flat terrain (slope < 5 deg), no dominant aspect"},
}

ASPECT_CLASS_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "Flat"]

# ── TPI Classes ──────────────────────────────────────────────────────────
# Topographic Position Index: relative elevation compared to neighborhood

TPI_CLASS_MAP = {
    "Valley": {"description": "Depression or valley bottom, moisture accumulation"},
    "Lower Slope": {"description": "Lower hillslope, transitional moisture"},
    "Flat/Mid": {"description": "Mid-slope or flat terrain"},
    "Upper Slope": {"description": "Upper hillslope, exposed and drier"},
    "Ridge": {"description": "Ridge top or crest, most exposed and driest"},
}

TPI_CLASS_ORDER = ["Valley", "Lower Slope", "Flat/Mid", "Upper Slope", "Ridge"]


# ── Classification Functions ─────────────────────────────────────────────

def classify_elevation(elevation_m):
    """
    Classify elevation values into ecological zones.

    Parameters
    ----------
    elevation_m : array-like or scalar
        Elevation in meters.

    Returns
    -------
    numpy.ndarray or str
        Zone labels.
    """
    arr = np.asarray(elevation_m, dtype=float)
    scalar = arr.ndim == 0
    arr = np.atleast_1d(arr)

    result = np.full(arr.shape, "Valley/Coast", dtype=object)
    result[arr >= 300] = "Foothill"
    result[arr >= 900] = "Lower Montane"
    result[arr >= 1800] = "Upper Montane"
    result[arr >= 2700] = "Subalpine"
    result[arr >= 3500] = "Alpine"

    return result.item() if scalar else result


def classify_slope(slope_deg):
    """
    Classify slope values into steepness classes.

    Parameters
    ----------
    slope_deg : array-like or scalar
        Slope in degrees.

    Returns
    -------
    numpy.ndarray or str
        Class labels.
    """
    arr = np.asarray(slope_deg, dtype=float)
    scalar = arr.ndim == 0
    arr = np.atleast_1d(arr)

    result = np.full(arr.shape, "Flat", dtype=object)
    result[arr >= 5] = "Gentle"
    result[arr >= 15] = "Moderate"
    result[arr >= 30] = "Steep"
    result[arr >= 45] = "Very Steep"

    return result.item() if scalar else result


def classify_aspect(aspect_deg, slope_deg=None, flat_threshold=5.0):
    """
    Classify aspect values into 8 cardinal/ordinal directions.

    Pixels with slope < flat_threshold are classified as "Flat" regardless
    of aspect, since flat terrain has no meaningful aspect.

    Parameters
    ----------
    aspect_deg : array-like or scalar
        Aspect in degrees (0=North, clockwise).
    slope_deg : array-like or scalar, optional
        Slope in degrees. If provided, flat areas are classified as "Flat".
    flat_threshold : float, default 5.0
        Slope threshold below which aspect is "Flat".

    Returns
    -------
    numpy.ndarray or str
        Direction labels.
    """
    arr = np.asarray(aspect_deg, dtype=float)
    scalar = arr.ndim == 0
    arr = np.atleast_1d(arr)

    # Normalize to 0-360
    arr = arr % 360

    result = np.full(arr.shape, "N", dtype=object)
    result[(arr >= 22.5) & (arr < 67.5)] = "NE"
    result[(arr >= 67.5) & (arr < 112.5)] = "E"
    result[(arr >= 112.5) & (arr < 157.5)] = "SE"
    result[(arr >= 157.5) & (arr < 202.5)] = "S"
    result[(arr >= 202.5) & (arr < 247.5)] = "SW"
    result[(arr >= 247.5) & (arr < 292.5)] = "W"
    result[(arr >= 292.5) & (arr < 337.5)] = "NW"

    if slope_deg is not None:
        slope_arr = np.atleast_1d(np.asarray(slope_deg, dtype=float))
        result[slope_arr < flat_threshold] = "Flat"

    return result.item() if scalar else result


def classify_tpi(tpi_values, std_multiplier=1.0):
    """
    Classify Topographic Position Index into landform classes.

    Uses standard deviation-based thresholds:
    - Valley:      TPI < -1 * std
    - Lower Slope: -1 * std <= TPI < -0.5 * std
    - Flat/Mid:    -0.5 * std <= TPI < 0.5 * std
    - Upper Slope: 0.5 * std <= TPI < 1 * std
    - Ridge:       TPI >= 1 * std

    Parameters
    ----------
    tpi_values : array-like
        TPI values.
    std_multiplier : float, default 1.0
        Scale factor for the standard deviation thresholds.

    Returns
    -------
    numpy.ndarray
        TPI class labels.
    """
    arr = np.asarray(tpi_values, dtype=float)
    scalar = arr.ndim == 0
    arr = np.atleast_1d(arr)

    valid = np.isfinite(arr)
    std = np.nanstd(arr[valid]) * std_multiplier

    result = np.full(arr.shape, "Flat/Mid", dtype=object)
    result[arr < -std] = "Valley"
    result[(arr >= -std) & (arr < -0.5 * std)] = "Lower Slope"
    result[(arr >= 0.5 * std) & (arr < std)] = "Upper Slope"
    result[arr >= std] = "Ridge"

    return result.item() if scalar else result
