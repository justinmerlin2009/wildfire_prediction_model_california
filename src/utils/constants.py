"""
Constants for the California Wildfire Prediction Project.
"""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "Datasets"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"

# Data file paths
FIRE_PERIMETERS_PATH = DATA_DIR / "Fireperimeters" / "California_Fire_Perimeters_All_Reprojected.gpkg"
LAKES_PATH = DATA_DIR / "Lakes" / "California_Lakes_Reprojected.gpkg"

# Coordinate Reference Systems
CRS_ALBERS = "EPSG:3310"  # California Albers Equal Area (meters)
CRS_WGS84 = "EPSG:4326"   # WGS84 for Folium/web maps

# Data quality cutoff year
# Data quality significantly improved after 1993 due to GPS-based collection
HIGH_QUALITY_CUTOFF = 1993

# Analysis periods
FULL_HISTORY_START = 1900  # Start year for full historical analysis
MODERN_ERA_START = 1990    # Start year for modern era (as in PDF analysis)

# Target resolution for ML model (from collaboration proposal)
GRID_RESOLUTION_M = 800  # 800m x 800m voxels

# Figure export settings
FIGURE_DPI = 300
FIGURE_FORMAT = "png"

# Fire size thresholds (acres)
MEGA_FIRE_THRESHOLD = 100000  # 100K+ acres = mega-fire
LARGE_FIRE_THRESHOLD = 10000  # 10K+ acres = large fire
