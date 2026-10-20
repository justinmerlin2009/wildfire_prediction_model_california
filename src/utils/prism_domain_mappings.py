"""
Domain value mappings for PRISM climate data analysis.

Defines variable metadata (units, ranges, colormaps), fire weather thresholds,
VPD risk classes, drought severity classes, California climate regions,
US state metadata, derived variable definitions, and helper functions.

PRISM (Parameter-elevation Regressions on Independent Slopes Model) provides
gridded climate data at ~800m resolution from Oregon State University.
"""
import numpy as np

# ── Variable Metadata ─────────────────────────────────────────────────

PRISM_VARIABLE_META = {
    "ppt": {
        "full_name": "Precipitation",
        "short_label": "Precip",
        "units": "mm",
        "units_daily": "mm/day",
        "units_monthly": "mm/month",
        "units_annual": "mm/year",
        "ca_range_annual": (50, 3500),       # Extreme desert to NW coast
        "ca_range_monthly": (0, 600),
        "fire_relevance": "Fuel moisture; antecedent drought; wet season recharge",
        "is_cumulative": True,
        "colormap": "YlGnBu",
        "colormap_anomaly": "BrBG",
    },
    "tmax": {
        "full_name": "Maximum Temperature",
        "short_label": "Tmax",
        "units": "°C",
        "units_daily": "°C",
        "units_monthly": "°C",
        "units_annual": "°C",
        "ca_range_annual": (0, 35),
        "ca_range_monthly": (-15, 50),
        "fire_relevance": "Fuel drying rate; heat stress on vegetation; fire weather",
        "is_cumulative": False,
        "colormap": "YlOrRd",
        "colormap_anomaly": "RdBu_r",
    },
    "tmin": {
        "full_name": "Minimum Temperature",
        "short_label": "Tmin",
        "units": "°C",
        "units_daily": "°C",
        "units_monthly": "°C",
        "units_annual": "°C",
        "ca_range_annual": (-10, 20),
        "ca_range_monthly": (-25, 30),
        "fire_relevance": "Nighttime recovery; frost effects; fuel moisture overnight",
        "is_cumulative": False,
        "colormap": "YlOrRd",
        "colormap_anomaly": "RdBu_r",
    },
    "tmean": {
        "full_name": "Mean Temperature",
        "short_label": "Tmean",
        "units": "°C",
        "units_daily": "°C",
        "units_monthly": "°C",
        "units_annual": "°C",
        "ca_range_annual": (-5, 25),
        "ca_range_monthly": (-20, 40),
        "fire_relevance": "Overall thermal regime; evapotranspiration driver",
        "is_cumulative": False,
        "colormap": "YlOrRd",
        "colormap_anomaly": "RdBu_r",
    },
    "tdmean": {
        "full_name": "Mean Dew Point Temperature",
        "short_label": "Tdmean",
        "units": "°C",
        "units_daily": "°C",
        "units_monthly": "°C",
        "units_annual": "°C",
        "ca_range_annual": (-15, 15),
        "ca_range_monthly": (-30, 25),
        "fire_relevance": "Atmospheric moisture; RH estimation; fuel moisture proxy",
        "is_cumulative": False,
        "colormap": "YlGnBu",
        "colormap_anomaly": "BrBG",
    },
    "vpdmax": {
        "full_name": "Maximum Vapor Pressure Deficit",
        "short_label": "VPDmax",
        "units": "hPa",
        "units_daily": "hPa",
        "units_monthly": "hPa",
        "units_annual": "hPa",
        "ca_range_annual": (2, 50),
        "ca_range_monthly": (0, 80),
        "fire_relevance": "#1 fire predictor: atmospheric drying demand on fuels",
        "is_cumulative": False,
        "colormap": "YlOrRd",
        "colormap_anomaly": "RdBu_r",
    },
    "vpdmin": {
        "full_name": "Minimum Vapor Pressure Deficit",
        "short_label": "VPDmin",
        "units": "hPa",
        "units_daily": "hPa",
        "units_monthly": "hPa",
        "units_annual": "hPa",
        "ca_range_annual": (0, 30),
        "ca_range_monthly": (0, 50),
        "fire_relevance": "Nighttime atmospheric drying; sustained fuel stress",
        "is_cumulative": False,
        "colormap": "YlOrRd",
        "colormap_anomaly": "RdBu_r",
    },
}

PRISM_SOLAR_META = {
    "solclear": {
        "full_name": "Clear-Sky Solar Radiation",
        "short_label": "SolClear",
        "units": "W/m²",
        "fire_relevance": "Maximum potential solar heating (no cloud attenuation)",
        "colormap": "YlOrRd",
    },
    "solslope": {
        "full_name": "Slope-Adjusted Solar Radiation",
        "short_label": "SolSlope",
        "units": "W/m²",
        "fire_relevance": "Terrain-modified insolation; aspect/slope effects on fuel drying",
        "colormap": "YlOrRd",
    },
    "soltotal": {
        "full_name": "Total Incoming Solar Radiation",
        "short_label": "SolTotal",
        "units": "W/m²",
        "fire_relevance": "Actual solar energy reaching surface (cloud-adjusted)",
        "colormap": "YlOrRd",
    },
    "soltrans": {
        "full_name": "Atmospheric Transmittance",
        "short_label": "SolTrans",
        "units": "fraction",
        "fire_relevance": "Cloud cover proxy; ratio of actual to clear-sky radiation",
        "colormap": "YlGnBu",
    },
}

PRISM_VARIABLE_ORDER = ["ppt", "tmax", "tmin", "tmean", "tdmean", "vpdmax", "vpdmin"]

# ── Fire Weather Thresholds ──────────────────────────────────────────

FIRE_WEATHER_VPD_CLASSES = {
    "Minimal": {"range": (0, 10), "color": "#2ECC71", "description": "Low drying demand"},
    "Low": {"range": (10, 20), "color": "#82E0AA", "description": "Moderate drying"},
    "Moderate": {"range": (20, 30), "color": "#F9E79F", "description": "Significant drying"},
    "High": {"range": (30, 40), "color": "#F5B041", "description": "Rapid fuel drying"},
    "Extreme": {"range": (40, 55), "color": "#E74C3C", "description": "Critical fire weather"},
    "Exceptional": {"range": (55, 100), "color": "#922B21", "description": "Record atmospheric drying"},
}

FIRE_WEATHER_VPD_ORDER = ["Minimal", "Low", "Moderate", "High", "Extreme", "Exceptional"]

FIRE_WEATHER_THRESHOLDS = {
    "vpd_moderate_hpa": 20,
    "vpd_high_hpa": 30,
    "vpd_extreme_hpa": 40,
    "vpd_critical_hpa": 45,     # Red Flag Warning threshold
    "vpd_exceptional_hpa": 55,
    "tmax_hot_c": 35,           # Hot day
    "tmax_extreme_c": 40,       # Extreme heat
    "tmax_record_c": 45,        # Record heat
    "ppt_trace_mm": 0.2,        # Trace precipitation
    "ppt_light_mm": 2.5,        # Light rain
    "ppt_moderate_mm": 7.5,     # Moderate rain
    "ppt_heavy_mm": 25.0,       # Heavy rain
    "ppt_ar_mm": 75.0,          # Atmospheric river event
}

# ── Drought Classification ───────────────────────────────────────────

DROUGHT_CLASSES = {
    "Extreme Drought": {"pct_range": (0, 50), "color": "#8B4513"},
    "Severe Drought": {"pct_range": (50, 70), "color": "#CD853F"},
    "Moderate Drought": {"pct_range": (70, 85), "color": "#DEB887"},
    "Near Normal": {"pct_range": (85, 115), "color": "#F5F5DC"},
    "Moderately Wet": {"pct_range": (115, 130), "color": "#87CEEB"},
    "Very Wet": {"pct_range": (130, 150), "color": "#4682B4"},
    "Extremely Wet": {"pct_range": (150, 999), "color": "#191970"},
}

DROUGHT_CLASS_ORDER = [
    "Extreme Drought", "Severe Drought", "Moderate Drought",
    "Near Normal",
    "Moderately Wet", "Very Wet", "Extremely Wet",
]

# ── Seasons ──────────────────────────────────────────────────────────

CLIMATE_SEASON_MAP = {
    1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring",
    5: "Spring", 6: "Summer", 7: "Summer", 8: "Summer",
    9: "Fall", 10: "Fall", 11: "Fall", 12: "Winter",
}

CLIMATE_SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]

WATER_YEAR_START_MONTH = 10  # October (western US hydrology standard)

FIRE_WEATHER_SEASON_MONTHS = [5, 6, 7, 8, 9, 10, 11]  # May-November

# ── California Climate Regions ───────────────────────────────────────

CA_CLIMATE_REGIONS = {
    "North Coast": {
        "bounds": (-124.5, 39.5, -122.5, 42.0),
        "description": "Wet, mild; redwood belt; highest CA precipitation",
        "color": "#1B7837",
    },
    "Sacramento Valley": {
        "bounds": (-122.5, 38.2, -121.0, 40.5),
        "description": "Hot dry summers; mild wet winters; rain shadow",
        "color": "#F4A261",
    },
    "San Joaquin Valley": {
        "bounds": (-121.5, 34.8, -118.5, 38.2),
        "description": "Hot arid summers; tule fog winters; extreme heat",
        "color": "#E76F51",
    },
    "Sierra Nevada": {
        "bounds": (-121.0, 35.5, -118.0, 42.0),
        "description": "Elevation-driven; heavy snowpack; alpine",
        "color": "#2A9D8F",
    },
    "Central Coast": {
        "bounds": (-122.5, 34.3, -119.5, 38.2),
        "description": "Mediterranean; marine fog influence; moderate",
        "color": "#457B9D",
    },
    "South Coast": {
        "bounds": (-120.5, 32.5, -117.0, 34.8),
        "description": "Mediterranean; Santa Ana winds; fire-prone",
        "color": "#E63946",
    },
    "Mojave Desert": {
        "bounds": (-118.0, 34.0, -114.0, 36.5),
        "description": "Hot arid; extreme VPD; minimal precipitation",
        "color": "#D4A574",
    },
    "Klamath/NE Plateau": {
        "bounds": (-124.0, 40.5, -120.0, 42.0),
        "description": "Continental; cold winters; dry east side",
        "color": "#6A5ACD",
    },
}

# ── US State Metadata (48 CONUS + DC) ────────────────────────────────

CONUS_STATES = {
    "AL": "Alabama", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida",
    "GA": "Georgia", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana",
    "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}

US_STATE_FIPS = {
    "AL": "01", "AZ": "04", "AR": "05", "CA": "06", "CO": "08",
    "CT": "09", "DE": "10", "FL": "12", "GA": "13", "ID": "16",
    "IL": "17", "IN": "18", "IA": "19", "KS": "20", "KY": "21",
    "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26",
    "MN": "27", "MS": "28", "MO": "29", "MT": "30", "NE": "31",
    "NV": "32", "NH": "33", "NJ": "34", "NM": "35", "NY": "36",
    "NC": "37", "ND": "38", "OH": "39", "OK": "40", "OR": "41",
    "PA": "42", "RI": "44", "SC": "45", "SD": "46", "TN": "47",
    "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53",
    "WV": "54", "WI": "55", "WY": "56", "DC": "11",
}

WESTERN_US_STATES = ["CA", "OR", "WA", "NV", "AZ", "NM", "CO", "UT", "ID", "MT", "WY"]

# ── Derived Variable Definitions ─────────────────────────────────────

DERIVED_VARIABLES = {
    "dtr": {
        "full_name": "Diurnal Temperature Range",
        "short_label": "DTR",
        "units": "°C",
        "formula": "tmax - tmin",
        "fire_relevance": "Greater range = drier conditions, lower RH at peak",
    },
    "vpd_mean": {
        "full_name": "Mean VPD",
        "short_label": "VPDmean",
        "units": "hPa",
        "formula": "(vpdmax + vpdmin) / 2",
        "fire_relevance": "Integrated daily atmospheric drying demand",
    },
    "dew_point_depression": {
        "full_name": "Dew Point Depression",
        "short_label": "DPD",
        "units": "°C",
        "formula": "tmean - tdmean",
        "fire_relevance": "Higher = drier air; proxy for low RH",
    },
    "estimated_rh_min": {
        "full_name": "Estimated Minimum Relative Humidity",
        "short_label": "RHmin",
        "units": "%",
        "formula": "100 * exp(17.27*tdmean/(237.3+tdmean)) / exp(17.27*tmax/(237.3+tmax))",
        "fire_relevance": "Low RH at peak temperature drives fire spread",
    },
    "cumulative_vpd_30d": {
        "full_name": "30-Day Cumulative VPD",
        "short_label": "CumVPD30",
        "units": "hPa·days",
        "formula": "rolling_sum(vpdmax, 30)",
        "fire_relevance": "Integrated fuel drying over prior month",
    },
    "cumulative_vpd_90d": {
        "full_name": "90-Day Cumulative VPD",
        "short_label": "CumVPD90",
        "units": "hPa·days",
        "formula": "rolling_sum(vpdmax, 90)",
        "fire_relevance": "Seasonal-scale fuel conditioning",
    },
    "ppt_anomaly_pct": {
        "full_name": "Precipitation Anomaly (% of Normal)",
        "short_label": "PPT Anom%",
        "units": "%",
        "formula": "100 * observed / normal",
        "fire_relevance": "Below 70% = drought conditions",
    },
}

# ── Month Labels ─────────────────────────────────────────────────────

MONTH_ABBREVS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


# ── Helper Functions ─────────────────────────────────────────────────

def get_variable_meta(var):
    """
    Get metadata dictionary for a PRISM variable.

    Parameters
    ----------
    var : str
        Variable name (e.g., 'ppt', 'vpdmax').

    Returns
    -------
    dict
        Variable metadata, or empty dict if not found.
    """
    return PRISM_VARIABLE_META.get(var, PRISM_SOLAR_META.get(var, {}))


def get_variable_label(var, with_units=True):
    """
    Get display label for a PRISM variable.

    Parameters
    ----------
    var : str
        Variable name.
    with_units : bool, default True
        Include units in parentheses.

    Returns
    -------
    str
        Display label, e.g., "Maximum Temperature (°C)".
    """
    meta = get_variable_meta(var)
    if not meta:
        return var
    label = meta["full_name"]
    if with_units and "units" in meta:
        label += f" ({meta['units']})"
    return label


def get_variable_colormap(var, anomaly=False):
    """
    Get matplotlib colormap name for a PRISM variable.

    Parameters
    ----------
    var : str
        Variable name.
    anomaly : bool, default False
        If True, return the anomaly/diverging colormap.

    Returns
    -------
    str
        Colormap name.
    """
    meta = get_variable_meta(var)
    if not meta:
        return "viridis"
    if anomaly and "colormap_anomaly" in meta:
        return meta["colormap_anomaly"]
    return meta.get("colormap", "viridis")


def classify_vpd(vpd_values):
    """
    Classify VPD values into fire weather risk classes.

    Parameters
    ----------
    vpd_values : array-like
        VPD values in hPa.

    Returns
    -------
    numpy.ndarray
        String labels for VPD risk classes.
    """
    arr = np.asarray(vpd_values, dtype=np.float64)
    scalar = arr.ndim == 0
    arr = np.atleast_1d(arr)

    result = np.full(arr.shape, "Unknown", dtype=object)
    for cls_name, cls_info in FIRE_WEATHER_VPD_CLASSES.items():
        lo, hi = cls_info["range"]
        mask = (arr >= lo) & (arr < hi)
        result[mask] = cls_name

    return result.item() if scalar else result


def classify_drought(precip_pct_normal):
    """
    Classify precipitation as percentage of normal into drought classes.

    Parameters
    ----------
    precip_pct_normal : array-like
        Precipitation as percentage of 30-year normal (100 = normal).

    Returns
    -------
    numpy.ndarray
        String labels for drought classes.
    """
    arr = np.asarray(precip_pct_normal, dtype=np.float64)
    scalar = arr.ndim == 0
    arr = np.atleast_1d(arr)

    result = np.full(arr.shape, "Near Normal", dtype=object)
    for cls_name, cls_info in DROUGHT_CLASSES.items():
        lo, hi = cls_info["pct_range"]
        mask = (arr >= lo) & (arr < hi)
        result[mask] = cls_name

    return result.item() if scalar else result


def month_to_water_year(year, month):
    """
    Convert calendar year/month to water year.

    Water year runs October-September. Oct 2019 → WY 2020.

    Parameters
    ----------
    year : int or array-like
        Calendar year.
    month : int or array-like
        Calendar month (1-12).

    Returns
    -------
    int or numpy.ndarray
        Water year.
    """
    year = np.asarray(year)
    month = np.asarray(month)
    return np.where(month >= WATER_YEAR_START_MONTH, year + 1, year)


def compute_rh_from_tdmean_tmax(tdmean, tmax):
    """
    Estimate minimum relative humidity from dew point and max temperature.

    Uses the Magnus formula approximation:
        RH_min ≈ 100 * exp(17.27 * Td / (237.3 + Td)) / exp(17.27 * T / (237.3 + T))

    Parameters
    ----------
    tdmean : array-like
        Mean dew point temperature (°C).
    tmax : array-like
        Maximum temperature (°C).

    Returns
    -------
    numpy.ndarray
        Estimated minimum RH in percent (0-100).
    """
    td = np.asarray(tdmean, dtype=np.float64)
    t = np.asarray(tmax, dtype=np.float64)

    # Magnus formula coefficients
    a, b = 17.27, 237.3
    rh = 100.0 * np.exp(a * td / (b + td)) / np.exp(a * t / (b + t))

    return np.clip(rh, 0, 100)
