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

# MTBS Dataset
MTBS_FOD_PATH = DATA_DIR / "Fireignition_points" / "mtbs_fod_pts_data" / "mtbs_FODpoints_DD.shp"
CRS_NAD83 = "EPSG:4269"  # NAD83 (MTBS native CRS)
MTBS_WESTERN_MIN_ACRES = 1000
MTBS_EASTERN_MIN_ACRES = 500
MTBS_NODATA_SENTINEL = {-9999, 9999}
MTBS_START_YEAR = 1984
MTBS_END_YEAR = 2024

# FPA FOD Dataset (Fire Program Analysis - Fire Occurrence Database, 6th edition)
FPA_FOD_PATH = DATA_DIR / "WildfireOccurenceData" / "Data" / "FPA_FOD_20221014.gpkg"
FPA_START_YEAR = 1992
FPA_END_YEAR = 2020

# Topography Dataset (USGS NED 1 arc-second DEM, reprojected to EPSG:3310)
TOPOGRAPHY_PATH = DATA_DIR / "Topography" / "Topography_Reprojected_Clipped.tif"
TOPO_NODATA = -32768
TOPO_NATIVE_RES_M = 27.19  # ~27m native resolution
TOPO_VIZ_DOWNSAMPLE = 30   # 30x downsample for visualization (~815m)
TPI_WINDOW_RADIUS = 10     # Pixel radius for TPI computation

# LANDFIRE 2024 Forest Canopy Cover (CC)
LANDFIRE_CC_PATH = DATA_DIR / "Vegetation_CONUS" / "LF2024_CC_CONUS" / "Tif" / "LF2024_CC_CONUS.tif"
LANDFIRE_CC_CSV_PATH = DATA_DIR / "Vegetation_CONUS" / "LF2024_CC_CONUS" / "CSV_Data" / "LF2024_CC.csv"
CRS_CONUS_ALBERS = "EPSG:5070"         # NAD83 / Conus Albers (LANDFIRE native)
LANDFIRE_CC_NODATA = -9999             # Sentinel for Fill-NoData
LANDFIRE_CC_RESOLUTION_M = 30          # Native pixel size
LANDFIRE_CC_VIZ_DOWNSAMPLE = 27        # 27x ≈ 810m for visualization
CA_BOUNDARY_PATH = Path("/Users/olivier/Documents/MyQGIS/WildfireAnalysis/DeepLearning/INPUTS_EPSG3310/California_State_Boundary_Reprojected.gpkg")

# FVEG22 Vegetation (FRAP CWHR, 2022 compilation)
FVEG22_PATH = DATA_DIR / "Vegetation" / "Vegetation_fveg22_1.tif"
FVEG22_NODATA = 65535
FVEG22_NATIVE_RES_M = 30.0
FVEG22_VIZ_DOWNSAMPLE = 40        # 40x → ~1200m for visualization
FVEG22_RAT_CSV_PATH = DATA_DIR / "Vegetation" / "fveg22_rat.csv"

# PRISM Climate Data (Oregon State University, 30-arcsecond ~800m)
PRISM_BASE_PATH = Path("/Volumes/LaCie/PRISM")
PRISM_CRS = "EPSG:4269"                         # NAD83 geographic
PRISM_NODATA = -9999.0
PRISM_RESOLUTION_ARCSEC = 30
PRISM_RESOLUTION_DEG = 1 / 120                   # 0.008333...°
PRISM_CONUS_SHAPE = (3105, 7025)
PRISM_DTYPE = "float32"
PRISM_CA_BOUNDS = (-124.5, 32.5, -114.0, 42.0)  # west, south, east, north
PRISM_CA_WINDOW_SHAPE = (1140, 1260)
PRISM_DAILY_START_YEAR = 1981
PRISM_DAILY_END_YEAR = 2026
PRISM_MONTHLY_START_YEAR = 1895
PRISM_MONTHLY_END_YEAR = 2025
PRISM_VARIABLES = ["ppt", "tmax", "tmin", "tmean", "tdmean", "vpdmax", "vpdmin"]
PRISM_SOLAR_VARIABLES = ["solclear", "solslope", "soltotal", "soltrans"]
PRISM_CACHE_DIR = OUTPUT_DIR / "cache" / "prism"
PRISM_VPD_CRITICAL_HPA = 45.0                    # Red Flag fire weather threshold
