"""
Domain value mappings for the MTBS (Monitoring Trends in Burn Severity) dataset.
Based on MTBS metadata and the Fire Occurrence Database (FOD) schema.

MTBS is a joint program of USGS and USDA Forest Service that maps burn severity
for all large fires (>= 1,000 acres western US, >= 500 acres eastern US) using
Landsat/Sentinel satellite imagery from 1984-present.
"""

# Incident Type — type of fire event
INCID_TYPE_MAP = {
    "Wildfire": "Wildfire",
    "Prescribed Fire": "Prescribed Fire",
    "Wildland Fire Use": "Wildland Fire Use",
    "Unknown": "Unknown",
}

# Assessment Type — how severity was assessed
ASMNT_TYPE_MAP = {
    "Initial": "Initial Assessment",
    "Initial (SS)": "Initial Assessment (Single Scene)",
    "Extended": "Extended Assessment",
    "Extended (SS)": "Extended Assessment (Single Scene)",
    "Emergency": "Emergency Assessment",
    "Emergency (SS)": "Emergency Assessment (Single Scene)",
}

# Severity threshold fields and their descriptions
SEVERITY_FIELDS = {
    "dNBR_offst": "dNBR offset value applied to the thresholds",
    "dNBR_stdDv": "Standard deviation of dNBR values",
    "NoData_T": "Threshold for NoData classification",
    "IncGreen_T": "Threshold for Increased Greenness (negative dNBR)",
    "Low_T": "Threshold separating Unburned/Low from Low severity",
    "Mod_T": "Threshold separating Low from Moderate severity",
    "High_T": "Threshold separating Moderate from High severity",
}

# Severity classes and their ecological meaning
SEVERITY_CLASSES = {
    "Increased Greenness": "Vegetation growth post-fire (negative dNBR)",
    "Unburned/Low": "Minimal or no detectable change in vegetation",
    "Low": "Low severity - surface burn with limited canopy damage",
    "Moderate": "Moderate severity - significant canopy damage",
    "High": "High severity - complete canopy consumption/mortality",
}

# US State codes (2-letter FIPS used as Event_ID prefix in MTBS)
STATE_CODES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
    "PR": "Puerto Rico", "VI": "Virgin Islands", "GU": "Guam",
    "AS": "American Samoa", "MP": "Northern Mariana Islands",
}

# Western US states that share California's 1,000-acre minimum threshold
WESTERN_US_STATES = {
    "AK", "AZ", "CA", "CO", "HI", "ID", "MT", "NV", "NM",
    "OR", "UT", "WA", "WY",
}

# Mapping program codes
MAP_PROG_MAP = {
    "MTBS": "Monitoring Trends in Burn Severity",
    "RAVG": "Rapid Assessment of Vegetation Condition",
    "BAER": "Burned Area Emergency Response",
    "NPS": "National Park Service",
    "Prairie": "Prairie Fire Mapping",
}


def get_state_from_event_id(event_id):
    """
    Extract state abbreviation from MTBS Event_ID.

    MTBS Event_IDs follow the pattern: SS########YYYYMMDD
    where SS is the 2-letter state code.

    Parameters
    ----------
    event_id : str
        MTBS Event_ID string.

    Returns
    -------
    str
        Two-letter state abbreviation, or 'Unknown' if extraction fails.
    """
    if isinstance(event_id, str) and len(event_id) >= 2:
        state = event_id[:2].upper()
        if state in STATE_CODES:
            return state
    return "Unknown"


def get_incid_type_label(incid_type):
    """Get human-readable incident type label."""
    return INCID_TYPE_MAP.get(incid_type, f"Unknown ({incid_type})")


def get_asmnt_type_label(asmnt_type):
    """Get human-readable assessment type label."""
    return ASMNT_TYPE_MAP.get(asmnt_type, f"Unknown ({asmnt_type})")


def get_state_name(state_code):
    """Get full state name from 2-letter code."""
    return STATE_CODES.get(state_code, f"Unknown ({state_code})")
