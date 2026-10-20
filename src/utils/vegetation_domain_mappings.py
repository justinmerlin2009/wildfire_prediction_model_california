"""
Domain value mappings for FVEG22 California vegetation analysis (CWHR system).

Defines WHRTYPE (65 types), WHR13 (13 classes), LIFEFORM (8 categories),
size/density codes, fire-prone type ratings, and helper functions.

The California Wildlife Habitat Relationships (CWHR) system classifies
vegetation into types based on species composition, structure, and density.
FVEG22 is CAL FIRE FRAP's 2022 statewide compilation at 30m resolution.
"""
import numpy as np

# ── WHRTYPE: 65 Vegetation Types ─────────────────────────────────────

WHRTYPE_MAP = {
    # Conifer (27 types including undetermined)
    "CPC": "Closed-Cone Pine-Cypress",
    "DFR": "Douglas Fir",
    "EPN": "Eastside Pine",
    "JPN": "Jeffrey Pine",
    "KMC": "Klamath Mixed Conifer",
    "LPN": "Lodgepole Pine",
    "MHC": "Montane Hardwood-Conifer",
    "PPN": "Ponderosa Pine",
    "RFR": "Red Fir",
    "RDW": "Redwood",
    "SMC": "Sierran Mixed Conifer",
    "SCN": "Subalpine Conifer",
    "WFR": "White Fir",
    "CON": "Undetermined Conifer",
    # Conifer Woodland
    "JUN": "Juniper",
    "PJN": "Pinyon-Juniper",
    # Hardwood Forest
    "ASP": "Aspen",
    "MHW": "Montane Hardwood",
    "MRI": "Montane Riparian",
    # Hardwood Woodland
    "BOW": "Blue Oak Woodland",
    "BOP": "Blue Oak-Foothill Pine",
    "COW": "Coastal Oak Woodland",
    "EUC": "Eucalyptus",
    "HDW": "Undetermined Hardwood",
    "VOW": "Valley Oak Woodland",
    "VRI": "Valley Foothill Riparian",
    # Desert Woodland
    "DRI": "Desert Riparian",
    "JST": "Joshua Tree",
    "POS": "Palm Oasis",
    # Shrub
    "ADS": "Alpine-Dwarf Shrub",
    "BBR": "Bitterbrush",
    "CRC": "Chamise-Redshank Chaparral",
    "CSC": "Coastal Scrub",
    "LSG": "Low Sage",
    "MCH": "Mixed Chaparral",
    "MCP": "Montane Chaparral",
    "SGB": "Sagebrush",
    "CHP": "Undetermined Shrub",
    # Desert Shrub
    "ASC": "Alkali Desert Scrub",
    "DSC": "Desert Scrub",
    "DSS": "Desert Succulent Shrub",
    "DSW": "Desert Wash",
    # Herbaceous
    "AGS": "Annual Grassland",
    "PGS": "Perennial Grassland",
    "PAS": "Pasture",
    # Wetland (herbaceous)
    "FEW": "Fresh Emergent Wetland",
    "SEW": "Saline Emergent Wetland",
    "WTM": "Wet Meadow",
    # Water
    "EST": "Estuarine",
    "LAC": "Lacustrine",
    "MAR": "Marsh",
    "RIV": "Riverine",
    "WAT": "Water",
    # Urban / Barren
    "URB": "Urban",
    "BAR": "Barren",
    # Agriculture
    "CRP": "Cropland",
    "DGR": "Dryland Grain Crops",
    "DOR": "Deciduous Orchard",
    "EOR": "Evergreen Orchard",
    "IGR": "Irrigated Grain Crops",
    "IRF": "Irrigated Row and Field Crops",
    "IRH": "Irrigated Hayfield",
    "OVN": "Orchard - Vineyard",
    "RIC": "Rice",
    "VIN": "Vineyard",
}

# ── LIFEFORM: 8 Categories ───────────────────────────────────────────

LIFEFORM_MAP = {
    "CONIFER": "Conifer",
    "HARDWOOD": "Hardwood",
    "SHRUB": "Shrub",
    "HERBACEOUS": "Herbaceous",
    "AGRICULTURE": "Agriculture",
    "URBAN": "Urban",
    "WATER": "Water",
    "BARREN/OTHER": "Barren/Other",
}

LIFEFORM_ORDER = [
    "CONIFER", "HARDWOOD", "SHRUB", "HERBACEOUS",
    "AGRICULTURE", "URBAN", "WATER", "BARREN/OTHER",
]

# ── WHR13: 13 Aggregated Classes ─────────────────────────────────────

WHR13_MAP = {
    31: "Conifer Forest",
    32: "Conifer Woodland",
    41: "Hardwood Forest",
    42: "Hardwood Woodland",
    43: "Desert Woodland",
    50: "Shrub",
    51: "Desert Shrub",
    60: "Herbaceous",
    61: "Wetland",
    70: "Agriculture",
    80: "Urban",
    90: "Water",
    99: "Barren/Other",
}

WHR13_ORDER = [
    "Conifer Forest", "Conifer Woodland",
    "Hardwood Forest", "Hardwood Woodland", "Desert Woodland",
    "Shrub", "Desert Shrub",
    "Herbaceous", "Wetland",
    "Agriculture", "Urban", "Water", "Barren/Other",
]

# ── WHRTYPE → LIFEFORM lookup ────────────────────────────────────────

WHRTYPE_TO_LIFEFORM = {
    # Conifer
    "CPC": "CONIFER", "DFR": "CONIFER", "EPN": "CONIFER", "JPN": "CONIFER",
    "KMC": "CONIFER", "LPN": "CONIFER", "MHC": "CONIFER", "PPN": "CONIFER",
    "RFR": "CONIFER", "RDW": "CONIFER", "SMC": "CONIFER", "SCN": "CONIFER",
    "WFR": "CONIFER", "CON": "CONIFER", "JUN": "CONIFER", "PJN": "CONIFER",
    # Hardwood
    "ASP": "HARDWOOD", "MHW": "HARDWOOD", "MRI": "HARDWOOD",
    "BOW": "HARDWOOD", "BOP": "HARDWOOD", "COW": "HARDWOOD",
    "EUC": "HARDWOOD", "HDW": "HARDWOOD", "VOW": "HARDWOOD",
    "VRI": "HARDWOOD", "DRI": "HARDWOOD", "JST": "HARDWOOD", "POS": "HARDWOOD",
    # Shrub
    "ADS": "SHRUB", "BBR": "SHRUB", "CRC": "SHRUB", "CSC": "SHRUB",
    "LSG": "SHRUB", "MCH": "SHRUB", "MCP": "SHRUB", "SGB": "SHRUB",
    "CHP": "SHRUB", "ASC": "SHRUB", "DSC": "SHRUB", "DSS": "SHRUB", "DSW": "SHRUB",
    # Herbaceous
    "AGS": "HERBACEOUS", "PGS": "HERBACEOUS", "PAS": "HERBACEOUS",
    "FEW": "HERBACEOUS", "SEW": "HERBACEOUS", "WTM": "HERBACEOUS",
    # Water
    "EST": "WATER", "LAC": "WATER", "MAR": "WATER", "RIV": "WATER", "WAT": "WATER",
    # Urban / Barren
    "URB": "URBAN", "BAR": "BARREN/OTHER",
    # Agriculture
    "CRP": "AGRICULTURE", "DGR": "AGRICULTURE", "DOR": "AGRICULTURE",
    "EOR": "AGRICULTURE", "IGR": "AGRICULTURE", "IRF": "AGRICULTURE",
    "IRH": "AGRICULTURE", "OVN": "AGRICULTURE", "RIC": "AGRICULTURE",
    "VIN": "AGRICULTURE",
}

# ── WHRTYPE → WHR13 lookup ───────────────────────────────────────────

WHRTYPE_TO_WHR13 = {
    # Conifer Forest (31)
    "CPC": "Conifer Forest", "DFR": "Conifer Forest", "EPN": "Conifer Forest",
    "JPN": "Conifer Forest", "KMC": "Conifer Forest", "LPN": "Conifer Forest",
    "MHC": "Conifer Forest", "PPN": "Conifer Forest", "RFR": "Conifer Forest",
    "RDW": "Conifer Forest", "SMC": "Conifer Forest", "SCN": "Conifer Forest",
    "WFR": "Conifer Forest", "CON": "Conifer Forest",
    # Conifer Woodland (32)
    "JUN": "Conifer Woodland", "PJN": "Conifer Woodland",
    # Hardwood Forest (41)
    "ASP": "Hardwood Forest", "MHW": "Hardwood Forest", "MRI": "Hardwood Forest",
    # Hardwood Woodland (42)
    "BOW": "Hardwood Woodland", "BOP": "Hardwood Woodland",
    "COW": "Hardwood Woodland", "EUC": "Hardwood Woodland",
    "HDW": "Hardwood Woodland", "VOW": "Hardwood Woodland",
    "VRI": "Hardwood Woodland",
    # Desert Woodland (43)
    "DRI": "Desert Woodland", "JST": "Desert Woodland", "POS": "Desert Woodland",
    # Shrub (50)
    "ADS": "Shrub", "BBR": "Shrub", "CRC": "Shrub", "CSC": "Shrub",
    "LSG": "Shrub", "MCH": "Shrub", "MCP": "Shrub", "SGB": "Shrub", "CHP": "Shrub",
    # Desert Shrub (51)
    "ASC": "Desert Shrub", "DSC": "Desert Shrub",
    "DSS": "Desert Shrub", "DSW": "Desert Shrub",
    # Herbaceous (60)
    "AGS": "Herbaceous", "PGS": "Herbaceous", "PAS": "Herbaceous",
    # Wetland (61)
    "FEW": "Wetland", "SEW": "Wetland", "WTM": "Wetland",
    # Agriculture (70)
    "CRP": "Agriculture", "DGR": "Agriculture", "DOR": "Agriculture",
    "EOR": "Agriculture", "IGR": "Agriculture", "IRF": "Agriculture",
    "IRH": "Agriculture", "OVN": "Agriculture", "RIC": "Agriculture",
    "VIN": "Agriculture",
    # Urban (80)
    "URB": "Urban",
    # Water (90)
    "EST": "Water", "LAC": "Water", "MAR": "Water", "RIV": "Water", "WAT": "Water",
    # Barren/Other (99)
    "BAR": "Barren/Other",
}

# ── WHRSIZE: Tree Size Classes ───────────────────────────────────────

WHRSIZE_MAP = {
    "1": "Seedling (<1\" DBH)",
    "2": "Sapling (1-6\" DBH)",
    "3": "Pole (6-11\" DBH)",
    "4": "Small Tree (11-24\" DBH)",
    "5": "Medium/Large Tree (>24\" DBH)",
    "6": "Multi-layered (size 5 over size 3)",
    "X": "Not applicable (non-tree)",
}

WHRSIZE_ORDER = ["1", "2", "3", "4", "5", "6", "X"]

# ── WHRDENSITY: Canopy Density Classes ───────────────────────────────

WHRDENSITY_MAP = {
    "S": "Sparse (10-24%)",
    "P": "Open (25-39%)",
    "M": "Moderate (40-59%)",
    "D": "Dense (60-100%)",
    "X": "Not applicable (non-tree)",
}

WHRDENSITY_ORDER = ["S", "P", "M", "D", "X"]

# ── Fire Risk Ratings by WHRTYPE ─────────────────────────────────────

FIRE_PRONE_WHRTYPE = {
    # High fire risk — chaparral, dry conifer, grassland
    "CRC": "High", "MCH": "High", "MCP": "High", "CSC": "High",
    "AGS": "High", "PGS": "High",
    "PPN": "High", "EPN": "High", "JPN": "High",
    "SMC": "High", "KMC": "High", "MHC": "High",
    "DFR": "High",
    "BOW": "High", "BOP": "High",
    # Moderate fire risk
    "SGB": "Moderate", "BBR": "Moderate", "LSG": "Moderate",
    "CPC": "Moderate", "WFR": "Moderate", "RFR": "Moderate",
    "MHW": "Moderate", "COW": "Moderate", "VOW": "Moderate",
    "JUN": "Moderate", "PJN": "Moderate",
    "VRI": "Moderate", "MRI": "Moderate",
    "EUC": "Moderate",
    "ADS": "Moderate",
    "PAS": "Moderate",
    # Low fire risk
    "RDW": "Low", "LPN": "Low", "SCN": "Low",
    "ASP": "Low",
    "DRI": "Low", "JST": "Low", "POS": "Low",
    "ASC": "Low", "DSC": "Low", "DSS": "Low", "DSW": "Low",
    "FEW": "Low", "SEW": "Low", "WTM": "Low",
    "HDW": "Low", "CON": "Low", "CHP": "Low",
    # Negligible fire risk
    "URB": "Negligible", "BAR": "Negligible",
    "WAT": "Negligible", "LAC": "Negligible", "RIV": "Negligible",
    "EST": "Negligible", "MAR": "Negligible",
    "CRP": "Negligible", "DGR": "Negligible", "DOR": "Negligible",
    "EOR": "Negligible", "IGR": "Negligible", "IRF": "Negligible",
    "IRH": "Negligible", "OVN": "Negligible", "RIC": "Negligible",
    "VIN": "Negligible",
}

FIRE_RISK_ORDER = ["High", "Moderate", "Low", "Negligible"]


# ── Helper Functions ─────────────────────────────────────────────────

def get_whrtype_name(code):
    """Get descriptive name for a 3-character WHRTYPE code."""
    return WHRTYPE_MAP.get(code, f"Unknown ({code})")


def get_lifeform(code):
    """Get lifeform category for a WHRTYPE code."""
    return WHRTYPE_TO_LIFEFORM.get(code, "Unknown")


def get_whr13_class(code):
    """Get WHR13 aggregated class for a WHRTYPE code."""
    return WHRTYPE_TO_WHR13.get(code, "Unknown")


def get_fire_risk_level(code):
    """Get fire risk rating for a WHRTYPE code."""
    return FIRE_PRONE_WHRTYPE.get(code, "Unknown")


def parse_whrall(whrall):
    """
    Parse a 5-character WHRALL code into components.

    Parameters
    ----------
    whrall : str
        5-character code like "SMC4M" (TYPE + SIZE + DENSITY).

    Returns
    -------
    dict
        Keys: whrtype, whrsize, whrdensity, whrname, lifeform, whr13.
    """
    if not whrall or len(whrall) < 5:
        return {"whrtype": None, "whrsize": None, "whrdensity": None,
                "whrname": None, "lifeform": None, "whr13": None}

    whrtype = whrall[:3]
    whrsize = whrall[3]
    whrdensity = whrall[4]

    return {
        "whrtype": whrtype,
        "whrsize": whrsize,
        "whrdensity": whrdensity,
        "whrname": get_whrtype_name(whrtype),
        "lifeform": get_lifeform(whrtype),
        "whr13": get_whr13_class(whrtype),
    }


def classify_fire_fuel_type(whrtype_codes):
    """
    Classify vegetation into fire fuel behavior categories.

    Parameters
    ----------
    whrtype_codes : array-like
        WHRTYPE 3-character codes.

    Returns
    -------
    numpy.ndarray
        Fuel type labels: "Timber", "Brush/Shrub", "Grass", "Slash",
        "Non-Fuel", or "Unknown".
    """
    arr = np.asarray(whrtype_codes, dtype=object)
    scalar = arr.ndim == 0
    arr = np.atleast_1d(arr)

    result = np.full(arr.shape, "Unknown", dtype=object)

    # Timber fuels — conifer and hardwood forests
    timber = {"CPC", "DFR", "EPN", "JPN", "KMC", "LPN", "MHC", "PPN",
              "RFR", "RDW", "SMC", "SCN", "WFR", "CON",
              "ASP", "MHW", "MRI", "JUN", "PJN"}
    # Brush/Shrub fuels
    brush = {"CRC", "MCH", "MCP", "CSC", "SGB", "BBR", "LSG", "ADS",
             "CHP", "ASC", "DSC", "DSS", "DSW",
             "BOW", "BOP", "COW", "EUC", "HDW", "VOW", "VRI",
             "DRI", "JST", "POS"}
    # Grass fuels
    grass = {"AGS", "PGS", "PAS"}
    # Non-fuel
    nonfuel = {"URB", "BAR", "WAT", "LAC", "RIV", "EST", "MAR",
               "CRP", "DGR", "DOR", "EOR", "IGR", "IRF", "IRH",
               "OVN", "RIC", "VIN", "FEW", "SEW", "WTM"}

    for i, code in enumerate(arr):
        if code in timber:
            result[i] = "Timber"
        elif code in brush:
            result[i] = "Brush/Shrub"
        elif code in grass:
            result[i] = "Grass"
        elif code in nonfuel:
            result[i] = "Non-Fuel"

    return result.item() if scalar else result
