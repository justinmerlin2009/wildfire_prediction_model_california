"""
Domain value mappings for the FPA FOD (Fire Program Analysis - Fire Occurrence Database).

FPA FOD is a national compilation of 2.3 million wildfire records (1992-2020) from
federal, state, and local reporting systems. 6th edition by Karen C. Short,
USDA Forest Service (2022). DOI: 10.2737/RDS-2013-0009.6

Key advantages over CAL FIRE/MTBS: full fire size spectrum (93% of CA fires < 10 acres),
standardized NWCG cause codes, land ownership, county geography, and fire duration.
"""

# NWCG Cause Classification — broad 3-category cause grouping
NWCG_CAUSE_CLASSIFICATION_MAP = {
    "Human": "Human-caused fire",
    "Natural": "Natural cause (lightning)",
    "Missing data/not specified/undetermined": "Missing or undetermined cause",
}

# NWCG General Cause — 13-category standardized cause taxonomy
NWCG_GENERAL_CAUSE_MAP = {
    "Arson/incendiarism": "Arson",
    "Debris and open burning": "Debris Burning",
    "Equipment and vehicle use": "Equipment Use",
    "Firearms and explosives use": "Firearms/Explosives",
    "Fireworks": "Fireworks",
    "Misuse of fire by a minor": "Children",
    "Natural": "Lightning",
    "Other causes": "Other",
    "Power generation/transmission/distribution": "Powerline",
    "Railroad operations and maintenance": "Railroad",
    "Recreation and ceremony": "Recreation",
    "Smoking": "Smoking",
    "Missing data/not specified/undetermined": "Missing/Unknown",
}

# NWCG Reporting Agency codes
NWCG_REPORTING_AGENCY_MAP = {
    "BIA": "Bureau of Indian Affairs",
    "BLM": "Bureau of Land Management",
    "BOR": "Bureau of Reclamation",
    "DOD": "Department of Defense",
    "DOE": "Department of Energy",
    "FS": "Forest Service",
    "FWS": "Fish and Wildlife Service",
    "IA": "Interagency Organization",
    "NPS": "National Park Service",
    "ST/C&L": "State, County, or Local",
    "TRIBE": "Tribal Organization",
}

# Source System Type — data provenance
SOURCE_SYSTEM_TYPE_MAP = {
    "FED": "Federal reporting system",
    "NONFED": "Non-federal reporting system",
    "INTERAGCY": "Interagency reporting system",
}

# Fire Size Class (NWCG standard) — acre bounds and descriptions
FIRE_SIZE_CLASS_MAP = {
    "A": {"label": "A (0-0.25 ac)", "description": "Class A", "min_acres": 0, "max_acres": 0.25},
    "B": {"label": "B (0.26-9.9 ac)", "description": "Class B", "min_acres": 0.26, "max_acres": 9.9},
    "C": {"label": "C (10-99 ac)", "description": "Class C", "min_acres": 10, "max_acres": 99.9},
    "D": {"label": "D (100-299 ac)", "description": "Class D", "min_acres": 100, "max_acres": 299},
    "E": {"label": "E (300-999 ac)", "description": "Class E", "min_acres": 300, "max_acres": 999},
    "F": {"label": "F (1K-5K ac)", "description": "Class F", "min_acres": 1000, "max_acres": 4999},
    "G": {"label": "G (5K+ ac)", "description": "Class G", "min_acres": 5000, "max_acres": None},
}

# Ordered list of size classes for consistent plotting
FIRE_SIZE_CLASS_ORDER = ["A", "B", "C", "D", "E", "F", "G"]

# Common land ownership categories (with standardization for duplicates)
OWNER_DESCR_MAP = {
    "USFS": "USFS (Forest Service)",
    "BLM": "BLM",
    "NPS": "National Park Service",
    "BIA": "Bureau of Indian Affairs",
    "BOR": "Bureau of Reclamation",
    "FWS": "Fish and Wildlife Service",
    "PRIVATE": "Private",
    "Private": "Private",
    "STATE": "State",
    "STATE OR PRIVATE": "State or Private",
    "COUNTY": "County",
    "MUNICIPAL/LOCAL": "Municipal/Local",
    "TRIBAL": "Tribal",
    "OTHER FEDERAL": "Other Federal",
    "UNDEFINED FEDERAL": "Undefined Federal",
    "FOREIGN": "Foreign",
    "MISSING/NOT SPECIFIED": "Missing/Not Specified",
}

# Standardized owner categories for cleaner plotting (merge duplicates)
OWNER_DESCR_STANDARDIZED = {
    "USFS": "USFS",
    "BLM": "BLM",
    "NPS": "NPS",
    "BIA": "BIA",
    "BOR": "BOR",
    "FWS": "FWS",
    "PRIVATE": "Private",
    "Private": "Private",
    "STATE": "State",
    "STATE OR PRIVATE": "State/Private",
    "COUNTY": "County",
    "MUNICIPAL/LOCAL": "Municipal/Local",
    "TRIBAL": "Tribal",
    "OTHER FEDERAL": "Other Federal",
    "UNDEFINED FEDERAL": "Other Federal",
    "FOREIGN": "Other",
    "MISSING/NOT SPECIFIED": "Missing",
}

# Fire season classification (same as MTBS/CAL FIRE for consistency)
FIRE_SEASON_MAP = {
    6: "High Risk", 7: "High Risk", 8: "High Risk", 9: "High Risk",
    10: "Transition", 11: "Transition", 12: "Transition", 1: "Transition",
    2: "Low Risk", 3: "Low Risk", 4: "Low Risk", 5: "Low Risk",
}


def get_nwcg_cause_label(cause_classification):
    """Get short label for NWCG cause classification."""
    mapping = {
        "Human": "Human",
        "Natural": "Natural",
        "Missing data/not specified/undetermined": "Missing",
    }
    return mapping.get(cause_classification, f"Unknown ({cause_classification})")


def get_general_cause_label(general_cause):
    """Get short label for NWCG general cause."""
    return NWCG_GENERAL_CAUSE_MAP.get(general_cause, f"Unknown ({general_cause})")


def get_fire_size_class_label(size_class):
    """Get descriptive label for fire size class (A-G)."""
    info = FIRE_SIZE_CLASS_MAP.get(size_class)
    if info:
        return info["label"]
    return f"Unknown ({size_class})"


def get_reporting_agency_label(agency_code):
    """Get full name for NWCG reporting agency code."""
    return NWCG_REPORTING_AGENCY_MAP.get(agency_code, f"Unknown ({agency_code})")


def get_source_system_label(source_type):
    """Get description for source system type."""
    return SOURCE_SYSTEM_TYPE_MAP.get(source_type, f"Unknown ({source_type})")


def get_owner_standardized(owner_descr):
    """Get standardized owner category for cleaner plotting."""
    return OWNER_DESCR_STANDARDIZED.get(owner_descr, "Other")
