"""
Domain value mappings from the CAL FIRE Data Dictionary (April 2025).
These convert coded values to human-readable labels.
"""

# CAUSE domain - Reason fire ignited
CAUSE_MAP = {
    1: "Lightning",
    2: "Equipment Use",
    3: "Smoking",
    4: "Campfire",
    5: "Debris",
    6: "Railroad",
    7: "Arson",
    8: "Playing with Fire",
    9: "Miscellaneous",
    10: "Vehicle",
    11: "Powerline",
    12: "Firefighter Training",
    13: "Non-Firefighter Training",
    14: "Unknown/Unidentified",
    15: "Structure",
    16: "Aircraft",
    17: "Volcanic",
    18: "Escaped Prescribed Burn",
    19: "Illegal Alien Campfire",
}

# AGENCY domain - Direct protection agency responsible
AGENCY_MAP = {
    "BIA": "Bureau of Indian Affairs",
    "BLM": "Bureau of Land Management",
    "CDF": "CAL FIRE",
    "CCO": "Contract County",
    "CSP": "California State Parks",
    "DOD": "Department of Defense",
    "FWS": "Fish and Wildlife Service",
    "LRA": "Local Responsibility Area",
    "NOP": "No Protection",
    "NPS": "National Park Service",
    "PVT": "Private",
    "USF": "USDA Forest Service",
    "OTH": "Other",
}

# C_METHOD domain - Collection method for perimeter data
C_METHOD_MAP = {
    1: "GPS Ground",
    2: "GPS Air",
    3: "Infrared",
    4: "Other Imagery",
    5: "Photo Interpretation",
    6: "Hand Drawn",
    7: "Mixed Collection Methods",
    8: "Unknown",
}

# OBJECTIVE domain - Tactic for fire response
OBJECTIVE_MAP = {
    1: "Suppression (Wildfire)",
    2: "Resource Benefit (WFU)",
}

# STATE domain
STATE_MAP = {
    "AZ": "Arizona",
    "CA": "California",
    "NV": "Nevada",
    "OR": "Oregon",
}

# UNIT_ID domain - Top responding units (most common)
# Full mapping available but these are the most frequent
UNIT_ID_MAP = {
    "AEU": "Amador - El Dorado CAL FIRE",
    "ANF": "Angeles National Forest",
    "BDF": "San Bernardino National Forest",
    "BDU": "San Bernardino CAL FIRE",
    "BEU": "Monterey - San Benito CAL FIRE",
    "BTU": "Butte CAL FIRE",
    "CZU": "San Mateo - Santa Cruz CAL FIRE",
    "ENF": "Eldorado National Forest",
    "FKU": "Fresno-Kings CAL FIRE",
    "HUU": "Humboldt - Del Norte CAL FIRE",
    "KNF": "Klamath National Forest",
    "KNP": "Sequoia - Kings Canyon NP",
    "KRN": "Kern County",
    "LAC": "Los Angeles County",
    "LMU": "Lassen - Modoc CAL FIRE",
    "LNF": "Lassen National Forest",
    "LNU": "Sonoma - Lake - Napa CAL FIRE",
    "LPF": "Los Padres National Forest",
    "MEU": "Mendocino CAL FIRE",
    "MMU": "Madera - Mariposa CAL FIRE",
    "MNF": "Mendocino National Forest",
    "MVU": "San Diego CAL FIRE (retired code)",
    "NEU": "Nevada - Yuba - Placer CAL FIRE",
    "ORC": "Orange County",
    "PNF": "Plumas National Forest",
    "RRU": "Riverside CAL FIRE",
    "SCU": "Santa Clara CAL FIRE",
    "SDU": "San Diego CAL FIRE",
    "SHF": "Shasta-Trinity National Forest",
    "SHU": "Shasta - Trinity CAL FIRE",
    "SKU": "Siskiyou CAL FIRE",
    "SLU": "San Luis Obispo CAL FIRE",
    "SNF": "Sierra National Forest",
    "SQF": "Sequoia National Forest",
    "SRF": "Six Rivers National Forest",
    "TCU": "Tuolumne - Calaveras CAL FIRE",
    "TGU": "Tehama - Glenn CAL FIRE",
    "TNF": "Tahoe National Forest",
    "TUU": "Tulare CAL FIRE",
    "VNC": "Ventura County",
    "YNP": "Yosemite National Park",
}


def get_cause_label(code):
    """Get human-readable cause label from code."""
    return CAUSE_MAP.get(code, f"Unknown ({code})")


def get_agency_label(code):
    """Get human-readable agency label from code."""
    return AGENCY_MAP.get(code, f"Unknown ({code})")


def get_c_method_label(code):
    """Get human-readable collection method label from code."""
    return C_METHOD_MAP.get(code, f"Unknown ({code})")


def get_unit_label(code):
    """Get human-readable unit label from code."""
    return UNIT_ID_MAP.get(code, code)  # Return code if not in mapping
