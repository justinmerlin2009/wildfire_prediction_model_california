# California Wildfire Prediction Model - Project Context

## Project Overview

**Goal**: Build a pixel-wise wildfire prediction system for California that varies with date given recent conditions.

**Collaboration Partners**:
- **Tam Air Club** (Tamalpais High School) - Student-led initiative
- **UCSF** - Research collaboration
- **UCI** - Academic partnership
- **CAL FIRE** - California Department of Forestry and Fire Protection

**Target Output**: Seasonal wildfire risk predictions at 800m × 800m resolution (voxels)

---

## GitHub Repository

**URL**: https://github.com/justinmerlin2009/wildfire_prediction_model_california

**Security Audit (January 2026)**: This repository has been audited and contains NO sensitive information:
- No passwords, API keys, or tokens
- No private SSH keys
- No personal email addresses in code
- No phone numbers or private addresses
- All data files are from public CAL FIRE, MTBS, FPA FOD, USGS, and LANDFIRE sources

**Large Files Excluded** (via `.gitignore`):
- GeoPackage data files (133 MB+) - download from CAL FIRE FRAP
- MTBS shapefile data - download from https://www.mtbs.gov/
- FPA FOD GeoPackage (885 MB) - download from https://doi.org/10.2737/RDS-2013-0009.6
- USGS DEM GeoTIFF (3.0 GB) - download from USGS National Map
- LANDFIRE CC CONUS GeoTIFF (1.5 GB) - download from https://landfire.gov/
- FVEG22 GeoTIFF (2.8 GB) - download from CAL FIRE FRAP
- Executed notebooks (40 MB+) - regenerate locally
- Interactive HTML maps (35 MB+) - regenerate locally

---

## Project Phases

### Phase 1: Exploratory Data Analysis (COMPLETE)
Analysis of CAL FIRE Historical Fire Perimeters dataset to understand:
- Temporal patterns and trends
- Spatial distribution of fires
- Fire causes and agency responses
- Seasonal patterns
- Fire size distributions

### Phase 1.5: Comprehensive Analysis Notebook v2 (COMPLETE - January 2026)
Single, publication-ready Jupyter notebook consolidating all EDA:
- **File**: `notebooks/CALFIRE_Comprehensive_Analysis_v2.ipynb`
- **Executed Version**: `notebooks/CALFIRE_Comprehensive_Analysis_v2_executed.ipynb`
- **Cells**: 62 (36 markdown, 26 code)
- **Parts**: 9 major sections
- **Figures**: 19 high-resolution visualizations
- **Interactive**: 1 Folium mega-fire map
- **Exports**: PDF and HTML versions in `outputs/`
- **Audience**: Tam Air Club website publication

### Phase 1.75: MTBS Fire Occurrence Analysis (COMPLETE - February 2026)
Comprehensive analysis of the MTBS (Monitoring Trends in Burn Severity) dataset:
- **File**: `notebooks/MTBS_FOD_Comprehensive_Analysis.ipynb`
- **Executed Version**: `notebooks/MTBS_FOD_Comprehensive_Analysis_executed.ipynb`
- **Cells**: 49 (26 markdown, 23 code)
- **Parts**: 9 major sections
- **Figures**: 16 high-resolution visualizations (300 DPI)
- **Interactive**: 1 Folium MarkerCluster map with severity popups
- **Key Differentiator**: Burn severity data (dNBR thresholds) for multi-class prediction
- **Utility Modules**: `src/utils/mtbs_domain_mappings.py`, `src/utils/mtbs_data_loader.py`

### Phase 1.875: FPA FOD Comprehensive Analysis (COMPLETE - March 2026)
Comprehensive analysis of the FPA FOD (Fire Program Analysis - Fire Occurrence Database), 6th edition:
- **File**: `notebooks/FPA_FOD_Comprehensive_Analysis.ipynb`
- **Executed Version**: `notebooks/FPA_FOD_Comprehensive_Analysis_executed.ipynb`
- **Cells**: 37 (14 markdown, 23 code)
- **Parts**: 9 major sections
- **Figures**: 17 high-resolution visualizations (300 DPI)
- **Interactive**: 1 Folium MarkerCluster map (fires >= 100 acres)
- **Key Differentiator**: Full fire size spectrum (93% under 10 acres), NWCG cause codes, fire duration, time-of-day, land ownership, county geography
- **Utility Modules**: `src/utils/fpa_domain_mappings.py`, `src/utils/fpa_data_loader.py`

### Phase 2A: Topography Comprehensive Analysis (COMPLETE - March 2026)
Comprehensive analysis of the USGS NED 1 Arc-Second DEM covering California:
- **File**: `notebooks/Topography_Comprehensive_Analysis.ipynb`
- **Executed Version**: `notebooks/Topography_Comprehensive_Analysis_executed.ipynb`
- **Cells**: 40 (12 markdown, 28 code)
- **Parts**: 9 major sections
- **Figures**: 18 high-resolution visualizations (300 DPI)
- **Interactive**: 1 Folium MarkerCluster map with terrain stats popups
- **Key Features**: Slope/aspect/TPI/TWI/HLI derivatives, fire overlay analysis (CAL FIRE + MTBS), 800m grid aggregation
- **Utility Modules**: `src/utils/topo_domain_mappings.py`, `src/utils/topo_data_loader.py`
- **Memory Strategy**: 30x downsampled visualization (~815m), full-res only for 800m aggregation

### Phase 1.9: LANDFIRE CC Comprehensive Analysis (COMPLETE - March 2026)
Comprehensive analysis of the LANDFIRE 2024 Forest Canopy Cover (CC) product:
- **File**: `notebooks/LANDFIRE_CC_Comprehensive_Analysis.ipynb`
- **Executed Version**: `notebooks/LANDFIRE_CC_Comprehensive_Analysis_executed.ipynb`
- **Cells**: 42 (12 markdown, 30 code)
- **Parts**: 9 major sections
- **Figures**: 17 high-resolution visualizations (300 DPI)
- **Interactive**: 1 Folium MarkerCluster map with CC-colored MTBS markers
- **Key Features**: CONUS→CA clip, EPSG:5070→3310 reproject, fire overlay (CAL FIRE + MTBS), 800m grid aggregation demo
- **Utility Modules**: `src/utils/landfire_domain_mappings.py`, `src/utils/landfire_data_loader.py`
- **Memory Strategy**: 27x downsampled visualization (~810m), full-res for 800m aggregation
- **First CONUS raster**: Required CRS chain EPSG:5070 → clip → EPSG:3310

### Phase 2B: FVEG22 Vegetation Comprehensive Analysis (COMPLETE - March 2026)
Comprehensive analysis of CAL FIRE FRAP's FVEG22 vegetation classification (CWHR system):
- **File**: `notebooks/FVEG22_Comprehensive_Analysis.ipynb`
- **Executed Version**: `notebooks/FVEG22_Comprehensive_Analysis_executed.ipynb`
- **Cells**: 36 (12 markdown, 24 code)
- **Parts**: 9 major sections
- **Figures**: 16 high-resolution visualizations (300 DPI)
- **Key Features**: CWHR 65-type classification, fire-prone vegetation mapping, fuel type classification, burned/unburned composition analysis
- **Utility Modules**: `src/utils/vegetation_domain_mappings.py`, `src/utils/vegetation_data_loader.py`
- **Memory Strategy**: 40x downsampled visualization (~1200m), chunked full-res scanning
- **RAT Challenge**: GeoTIFF has no embedded RAT; built local VALUE→WHRTYPE mapping via ArcGIS MapServer identify endpoint (20,390 mappings, 98.1% pixel coverage)

### Phase 3A: PRISM Climate Data Comprehensive Analysis (COMPLETE - March 2026)
Comprehensive analysis of 5 TB PRISM climate data at ~800m resolution:
- **Source**: Oregon State University PRISM Climate Group (`/Volumes/LaCie/PRISM`)
- **Variables**: 7 core (ppt, tmax, tmin, tmean, tdmean, vpdmax, vpdmin) + 4 solar normals
- **Coverage**: CONUS monthly (1895–2025), daily (1981–2026), 30-year normals
- **Resolution**: 30 arcsecond (~800m) — matches project target grid
- **CRS**: EPSG:4269 (NAD83 geographic)
- **File**: `notebooks/PRISM_Comprehensive_Analysis_Part1_CONUS.ipynb` (CONUS + All 48 States)
- **File**: `notebooks/PRISM_Comprehensive_Analysis_Part2_California.ipynb` (CA Deep Dive)
- **File**: `notebooks/PRISM_Comprehensive_Analysis_Part3_FireOverlay.ipynb` (Climate-Fire Integration)
- **Figures**: 56 total (22 + 18 + 16)
- **Utility Modules**: `src/utils/prism_domain_mappings.py`, `src/utils/prism_data_loader.py`
- **Precomputation**: `scripts/prism_precompute_state_summaries.py` (one-time, ~1 hour for CA)
- **Cache**: `outputs/cache/prism/prism_ca_monthly_stats.csv` (~2 MB)
- **Builder Scripts**: `scripts/build_notebook{1,2,3}.py` (programmatic notebook generation)
- **Key Finding**: VPD is the #1 predictor of annual burned area (R² ~0.25-0.40)

### Phase 2: Grid Creation (NEXT)
- Create 800m × 800m grid covering California
- Rasterize fire perimeters to binary burned/not-burned grid cells
- Temporal aggregation (monthly, seasonal, annual)

### Phase 3: Data Integration
Integrate additional datasets:
- **Climate/Weather**: ~~PRISM data (temperature, precipitation, VPD)~~ **DONE in Phase 3A**
- **Topography**: ~~Elevation, slope, aspect (DEM)~~ **DONE in Phase 2A**
- **Vegetation/Fuel**: ~~Cover type, density, fuel models~~ **CWHR types in Phase 2B; CC in Phase 1.9**
- **Human Activity**: Roads, population density, infrastructure

### Phase 4: ML Model Development
- CNN/LSTM architecture for temporal fire risk prediction
- Training on 1993+ high-quality data
- Validation on recent years (2020+)

---

## Key Findings from EDA (Verified from Data)

### Dataset Statistics
| Metric | Full Dataset | High-Quality (1993+) |
|--------|--------------|---------------------|
| Total Records | ~22,000+ | ~10,000 |
| Year Range | 1878-2025 | 1993-2025 |
| Total Acres Burned | ~40M | ~24.5M |
| Mega-fires (>100K acres) | 47 | 38 |

### Verified Statistics (1993-Present)
| Finding | Verified Value | Source |
|---------|----------------|--------|
| Worst fire year | 2020 with **4.2 million acres** | Yearly aggregation |
| High Risk Season burned area | **~84%** (Jun-Sep) | Seasonal analysis |
| Unknown/Unidentified causes | **~30%** of fires | Cause distribution |
| Top 1% fire concentration | **~58%** of burned area | Pareto analysis |
| Top 10% fire concentration | **~93%** of burned area | Pareto analysis |
| Data completeness (key fields) | **>97%** | Field analysis |

### Key Insights
- **Wildfires are accelerating**: Clear increase post-2000
- **Extreme concentration**: Top 1% of fires cause ~58% of damage
- **Seasonal pattern**: 84% of burned area occurs June-September
- **Cause investigation is difficult**: ~30% of fires have unknown causes
- **Data quality is excellent**: >97% completeness for key fields since 1993

---

## Dataset Information

### Primary Dataset: California Fire Perimeters
- **File**: `Datasets/Fireperimeters/California_Fire_Perimeters_All_Reprojected.gpkg`
- **Format**: GeoPackage (133 MB)
- **Records**: ~22,000+ fire perimeters (1878-2025)
- **CRS**: EPSG:3310 (California Albers projection)

### Key Attributes
| Field | Description |
|-------|-------------|
| `YEAR_` | Fire year |
| `ALARM_DATE` | Date fire was reported |
| `CONT_DATE` | Date fire was contained |
| `AGENCY` | Responding agency (CDF, USF, BLM, etc.) |
| `UNIT_ID` | CAL FIRE unit or contract county |
| `FIRE_NAME` | Name of the fire |
| `GIS_ACRES` | Calculated acres from GIS |
| `CAUSE` | Fire cause code (1-19) |
| `C_METHOD` | Perimeter collection method (1-8) |

### Data Quality Threshold
- **Pre-1993**: Variable quality, hand-drawn perimeters, incomplete attribution
- **1993+**: High-quality GPS-based collection, >97% completeness
- **Recommendation**: Use 1993+ data for ML model training

### Secondary Dataset: MTBS Fire Occurrence Database
- **File**: `Datasets/Fireignition_points/mtbs_fod_pts_data/mtbs_FODpoints_DD.shp`
- **Format**: Shapefile (with .dbf, .shx, .prj, .sbn, .sbx, .cpg)
- **Records**: 30,730 nationally; **2,051 California fires**
- **CRS**: EPSG:4269 (NAD83)
- **Year Range**: 1984-2024
- **Geometry**: Point (burned-area centroids, NOT ignition points)
- **Source**: USGS/USDA Forest Service MTBS program (https://www.mtbs.gov/)
- **Size Threshold**: >= 1,000 acres (western US), >= 500 acres (eastern US)

#### MTBS Key Attributes
| Field | Description |
|-------|-------------|
| `Event_ID` | Unique identifier (state prefix + date) |
| `Incid_Name` | Fire incident name |
| `Incid_Type` | Wildfire, Prescribed Fire, Wildland Fire Use, Unknown |
| `Ig_Date` | Ignition/discovery date |
| `BurnBndAc` | Burned area in acres |
| `Asmnt_Type` | Assessment type (Initial, Extended, Emergency + SS variants) |
| `Map_Prog` | Mapping program (MTBS, RAVG, BAER, NPS, Prairie) |
| `dNBR_offst` | dNBR offset applied to thresholds |
| `dNBR_stdDv` | Standard deviation of dNBR values |
| `Low_T` | dNBR threshold: Unburned/Low → Low severity |
| `Mod_T` | dNBR threshold: Low → Moderate severity |
| `High_T` | dNBR threshold: Moderate → High severity |
| `NoData_T` | dNBR threshold for NoData classification |
| `IncGreen_T` | dNBR threshold for Increased Greenness |

#### MTBS Data Quality
- **Severity data available**: 77.1% of CA records (1,581 / 2,051)
- **Sentinel values**: -9999 and 9999 indicate missing severity data
- **Incident type**: ~88% Wildfire, remainder Prescribed/WFU/Unknown
- **Total CA burned area**: 25.6M acres

### Tertiary Dataset: FPA FOD (Fire Program Analysis - Fire Occurrence Database)
- **File**: `Datasets/WildfireOccurenceData/Data/FPA_FOD_20221014.gpkg`
- **Format**: GeoPackage (885 MB)
- **Records**: 2.3 million nationally; **251,881 California fires**
- **CRS**: EPSG:4269 (NAD83)
- **Year Range**: 1992-2020
- **Geometry**: Point (fire locations)
- **Source**: Karen C. Short, USDA Forest Service (2022), DOI: 10.2737/RDS-2013-0009.6
- **Size Threshold**: None (all sizes from 0.01+ acres)
- **Layers**: `Fires` (main), `NWCG_UnitIdActive_20200123` (unit metadata)

#### FPA FOD Key Attributes
| Field | Description |
|-------|-------------|
| `FOD_ID` | Unique numeric record identifier |
| `FIRE_YEAR` | Calendar year of fire discovery |
| `DISCOVERY_DATE` | Date fire discovered (m/d/yyyy) |
| `DISCOVERY_DOY` | Day of year of discovery |
| `DISCOVERY_TIME` | Time of discovery (HHMM) |
| `CONT_DATE` | Containment date (m/d/yyyy) |
| `FIRE_SIZE` | Estimated acres within final perimeter |
| `FIRE_SIZE_CLASS` | Size class A-G (NWCG standard) |
| `NWCG_CAUSE_CLASSIFICATION` | Broad cause: Human / Natural / Missing |
| `NWCG_GENERAL_CAUSE` | 13-category cause (Arson, Lightning, etc.) |
| `NWCG_REPORTING_AGENCY` | Reporting agency (FS, BLM, NPS, ST/C&L, etc.) |
| `SOURCE_SYSTEM_TYPE` | Data provenance (FED / NONFED / INTERAGCY) |
| `OWNER_DESCR` | Land ownership at point of origin |
| `STATE` | Two-letter state code |
| `COUNTY` | County name |
| `FIPS_CODE` | Five-digit FIPS county code |
| `MTBS_ID` | MTBS incident identifier (for cross-reference) |
| `FIRE_NAME` | Incident name |

#### FPA FOD Data Quality (California)
- **Core fields**: 100% populated (FOD_ID, FIRE_YEAR, FIRE_SIZE, causes, agency, owner, state)
- **Discovery time**: 82.1% (206,816 records)
- **Fire name**: 81.2% (204,514 records)
- **County/FIPS**: 62.4% (157,156 records)
- **Containment date**: 53.2% (134,002 records)
- **MTBS linkage**: 0.6% (1,447 records — large fires only)
- **Total CA burned area**: 20.9M acres

### Topography Dataset: USGS NED 1 Arc-Second DEM
- **File**: `Datasets/Topography/Topography_Reprojected_Clipped.tif`
- **Format**: GeoTIFF (3.0 GB, int16)
- **Shape**: 42,463 x 37,312 pixels
- **CRS**: EPSG:3310 (California Albers)
- **Resolution**: ~27.19m native
- **NoData**: -32768
- **Elevation Range**: ~-86m (Death Valley) to ~4,421m (Mt. Whitney)
- **Source**: USGS National Elevation Dataset
- **Memory Strategy**: 30x downsample for visualization (~815m), full-res for 800m aggregation

### Vegetation Dataset: LANDFIRE 2024 Forest Canopy Cover (CC)
- **File**: `Datasets/Vegetation_CONUS/LF2024_CC_CONUS/Tif/LF2024_CC_CONUS.tif`
- **CSV Metadata**: `Datasets/Vegetation_CONUS/LF2024_CC_CONUS/CSV_Data/LF2024_CC.csv`
- **Format**: GeoTIFF (1.5 GB, int16), CONUS-wide
- **Shape**: 101,538 x 156,336 pixels (CONUS)
- **CRS**: EPSG:5070 (NAD83/Conus Albers)
- **Resolution**: 30m native
- **NoData**: 32767 (raster), -9999 (Fill-NoData in CSV)
- **Source**: USGS/USDA Forest Service LANDFIRE program (https://landfire.gov/)
- **Temporal**: 2024 snapshot incorporating 2015-2024 disturbances
- **Values**: Categorical — 0 (Non-Forested), 15 (10-20%), 25 (20-30%), ..., 95 (90-100%)
- **Processing**: Clip to CA boundary → reproject EPSG:5070 → EPSG:3310 → 27x downsample for viz

#### LANDFIRE CC Key Attributes
| CC Value | Label | Broad Category |
|----------|-------|---------------|
| 0 | Non-Forested | Non-Forested |
| 15 | 10-20% | Open (10-30%) |
| 25 | 20-30% | Open (10-30%) |
| 35 | 30-40% | Moderate (30-60%) |
| 45 | 40-50% | Moderate (30-60%) |
| 55 | 50-60% | Moderate (30-60%) |
| 65 | 60-70% | Dense (60-80%) |
| 75 | 70-80% | Dense (60-80%) |
| 85 | 80-90% | Very Dense (80-100%) |
| 95 | 90-100% | Very Dense (80-100%) |

### Vegetation Dataset: FVEG22 (FRAP CWHR Classification, 2022)
- **File**: `Datasets/Vegetation/Vegetation_fveg22_1.tif`
- **RAT CSV (local)**: `Datasets/Vegetation/fveg22_local_rat.csv` (20,390 VALUE→WHRTYPE mappings)
- **RAT CSV (ImageServer)**: `Datasets/Vegetation/fveg22_rat.csv` (14,350 reference entries)
- **Format**: GeoTIFF (2.8 GB, uint16), California-only
- **Shape**: 39,623 × 38,094 pixels (~1.5 billion)
- **CRS**: EPSG:3310 (California Albers)
- **Resolution**: 30m native
- **NoData**: 65535
- **Valid data**: ~30.56% of pixels (~462M valid)
- **Unique values**: 42,032 (range 1–42,032)
- **Source**: CAL FIRE FRAP + CDFW VegCAMP (~1990–2022 compilation)
- **Classification**: CWHR — 65 WHRTYPE → 13 WHR13 → 8 LIFEFORM
- **RAT Challenge**: No embedded RAT; local mapping built via ArcGIS MapServer identify endpoint (98.1% pixel coverage)
- **Processing**: 40x downsample for visualization (~1200m), chunked reads for full-res scanning

#### FVEG22 Key LIFEFORM Categories
| LIFEFORM | Example WHRTYPEs | Fire Relevance |
|----------|-----------------|----------------|
| CONIFER | SMC, DFR, PPN, JPN | Crown fire under drought |
| HARDWOOD | MHW, BOW, COW | Moderate fire risk |
| SHRUB | MCH, CRC, CSC, SGB | Chaparral — highest fire risk |
| HERBACEOUS | AGS, PGS | Fast-spreading surface fire |
| AGRICULTURE | CRP, DOR, IRF | Negligible wildfire risk |
| URBAN | URB | Negligible wildfire risk |
| WATER | WAT, LAC, RIV | Non-fuel |
| BARREN/OTHER | BAR | Non-fuel |

### Climate Dataset: PRISM (Oregon State University)
- **Location**: `/Volumes/LaCie/PRISM` (external LaCie drive, 5.0 TB)
- **Format**: Zipped GeoTIFFs (`.zip` → `.tif` + metadata)
- **Resolution**: 30 arcsecond (~800m)
- **CRS**: EPSG:4269 (NAD83 geographic lat/lon)
- **CONUS Shape**: 7,025 × 3,105 pixels per raster
- **CA Window**: 1,140 × 1,260 pixels from bounds (-124.5, 32.5, -114.0, 42.0)
- **CA Valid Pixels**: 1,086,516 (75.6% of window)
- **NoData**: -9999.0
- **Dtype**: float32
- **Source**: https://prism.oregonstate.edu/

#### PRISM Variables
| Variable | Description | Daily (1981-2026) | Monthly (1895-2025) | Normals |
|----------|-------------|-------------------|---------------------|---------|
| **ppt** | Precipitation (mm) | 16,733 files | 1,703 files | Yes |
| **tmax** | Max temperature (°C) | 16,445 files | 1,703 files | Yes |
| **tmin** | Min temperature (°C) | 16,576 files | 1,703 files | Yes |
| **tmean** | Mean temperature (°C) | 16,445 files | 1,703 files | Yes |
| **tdmean** | Mean dew point (°C) | 16,445 files | 1,703 files | Yes |
| **vpdmax** | Max VPD (hPa) | 16,445 files | 1,703 files | Yes |
| **vpdmin** | Min VPD (hPa) | 16,445 files | 1,703 files | Yes |
| **Solar** (4 vars) | Radiation normals | — | — | Yes |

#### PRISM File Naming Convention
- Daily: `prism_{var}_us_30s_{YYYYMMDD}.zip`
- Monthly: `prism_{var}_us_30s_{YYYYMM}.zip`
- Normals: `prism_{var}_us_30s_{YYYYMM}_avg_30y.zip`

### Quaternary Dataset: California State Boundary
- **File**: `/Users/olivier/Documents/MyQGIS/WildfireAnalysis/DeepLearning/INPUTS_EPSG3310/California_State_Boundary_Reprojected.gpkg`
- **CRS**: EPSG:3310 (California Albers)
- **Use**: Geographic context for maps

---

## Code Architecture

### Directory Structure
```
wildfire_prediction_model_california/
├── Datasets/
│   ├── Fireperimeters/
│   │   └── California_Fire_Perimeters_All_Reprojected.gpkg
│   ├── Fireignition_points/
│   │   └── mtbs_fod_pts_data/
│   │       └── mtbs_FODpoints_DD.shp   # + .dbf, .shx, .prj, etc.
│   ├── Topography/
│   │   └── Topography_Reprojected_Clipped.tif  # 3.0 GB DEM
│   ├── Vegetation/
│   │   ├── Vegetation_fveg22_1.tif        # 2.8 GB FVEG22 raster
│   │   ├── fveg22_local_rat.csv           # Local VALUE→WHRTYPE mapping
│   │   └── fveg22_rat.csv                 # ImageServer reference RAT
│   ├── Vegetation_CONUS/
│   │   └── LF2024_CC_CONUS/               # LANDFIRE 2024 Canopy Cover
│   │       ├── Tif/LF2024_CC_CONUS.tif    # 1.5 GB CONUS raster
│   │       └── CSV_Data/LF2024_CC.csv     # Class metadata + RGB colors
│   └── WildfireOccurenceData/
│       └── Data/
│           └── FPA_FOD_20221014.gpkg   # 885 MB - FPA FOD 6th edition
├── src/
│   └── utils/
│       ├── __init__.py
│       ├── constants.py               # Paths, CRS, thresholds (all datasets)
│       ├── domain_mappings.py         # CAUSE, AGENCY, C_METHOD lookups
│       ├── mtbs_domain_mappings.py    # MTBS incident/assessment/severity mappings
│       ├── fpa_domain_mappings.py     # FPA FOD NWCG cause/size/owner mappings
│       ├── data_loader.py             # CAL FIRE GeoPackage loading utilities
│       ├── mtbs_data_loader.py        # MTBS shapefile loading & processing
│       ├── fpa_data_loader.py         # FPA FOD GeoPackage loading & processing
│       ├── topo_domain_mappings.py    # Elevation/slope/aspect/TPI classification
│       ├── topo_data_loader.py        # DEM loading, derivatives, 800m aggregation
│       ├── landfire_domain_mappings.py # CC value labels, RGB colors, broad categories
│       ├── landfire_data_loader.py    # CONUS clip, reproject, fire overlay extraction
│       ├── vegetation_domain_mappings.py # CWHR types, lifeforms, fire-prone ratings
│       ├── vegetation_data_loader.py  # FVEG22 raster loading, RAT cascade, fire overlay
│       ├── prism_domain_mappings.py   # PRISM variable metadata, VPD/drought classes, CA regions
│       ├── prism_data_loader.py       # PRISM zip I/O, CA windowing, batch loading, state stats
│       └── plotting.py                # Visualization helpers (all dataset color palettes)
├── scripts/
│   ├── prism_precompute_state_summaries.py  # One-time PRISM batch precomputation
│   ├── build_notebook1.py                   # PRISM CONUS notebook builder
│   ├── build_notebook2.py                   # PRISM California notebook builder
│   └── build_notebook3.py                   # PRISM Fire Overlay notebook builder
├── notebooks/
│   ├── CALFIRE_Comprehensive_Analysis_v2.ipynb           # CAL FIRE EDA
│   ├── CALFIRE_Comprehensive_Analysis_v2_executed.ipynb  # With outputs
│   ├── MTBS_FOD_Comprehensive_Analysis.ipynb             # MTBS EDA
│   ├── MTBS_FOD_Comprehensive_Analysis_executed.ipynb    # With outputs
│   ├── FPA_FOD_Comprehensive_Analysis.ipynb              # FPA FOD EDA
│   ├── FPA_FOD_Comprehensive_Analysis_executed.ipynb     # With outputs
│   ├── Topography_Comprehensive_Analysis.ipynb           # Topography EDA
│   ├── Topography_Comprehensive_Analysis_executed.ipynb  # With outputs
│   ├── LANDFIRE_CC_Comprehensive_Analysis.ipynb          # LANDFIRE CC EDA
│   ├── LANDFIRE_CC_Comprehensive_Analysis_executed.ipynb  # With outputs
│   ├── FVEG22_Comprehensive_Analysis.ipynb               # FVEG22 vegetation EDA
│   ├── FVEG22_Comprehensive_Analysis_executed.ipynb      # With outputs
│   ├── PRISM_Comprehensive_Analysis_Part1_CONUS.ipynb         # PRISM CONUS + 48 States
│   ├── PRISM_Comprehensive_Analysis_Part2_California.ipynb    # PRISM CA Deep Dive
│   └── PRISM_Comprehensive_Analysis_Part3_FireOverlay.ipynb   # PRISM Fire-Climate Integration
├── outputs/
│   ├── figures/
│   │   ├── comprehensive/             # 19 CAL FIRE v2 figures + legacy files (needs cleanup)
│   │   ├── mtbs/                      # 16 MTBS figures (300 DPI)
│   │   ├── fpa/                       # 17 FPA FOD figures (300 DPI)
│   │   ├── topography/                # 18 Topography figures (300 DPI)
│   │   ├── landfire_cc/              # 17 LANDFIRE CC figures (300 DPI)
│   │   ├── vegetation/               # 16 FVEG22 figures (300 DPI)
│   │   ├── prism_conus/              # 22 PRISM CONUS figures (300 DPI)
│   │   ├── prism_california/         # 18 PRISM California figures (300 DPI)
│   │   └── prism_fire/               # 16 PRISM Fire Overlay figures (300 DPI)
│   ├── interactive/                   # Folium maps
│   │   ├── mega_fires_interactive.html  # CAL FIRE mega-fires
│   │   ├── mega_fires_map.html          # CAL FIRE (alternate filename)
│   │   ├── fire_density_heatmap.html    # CAL FIRE density
│   │   ├── mtbs_fires_interactive.html  # MTBS severity markers
│   │   ├── fpa_fires_interactive.html   # FPA FOD fires >= 100 ac
│   │   ├── topo_fires_interactive.html  # Terrain stats popups
│   │   └── landfire_cc_interactive.html # CC-colored MTBS markers
│   ├── cache/
│   │   └── prism/                        # PRISM precomputed caches
│   │       ├── prism_ca_monthly_stats.csv   # CA monthly stats (~2 MB)
│   │       └── us_states_conus.gpkg         # US Census state boundaries
│   ├── CALFIRE_Comprehensive_Analysis_v2.pdf              # PDF export
│   ├── CALFIRE_Comprehensive_Analysis_v2.html             # HTML export (original)
│   ├── CALFIRE_Comprehensive_Analysis_v2_executed.html    # HTML with code + outputs
│   ├── MTBS_FOD_Comprehensive_Analysis_executed.html      # HTML with code + outputs
│   ├── FPA_FOD_Comprehensive_Analysis_executed.html       # HTML with code + outputs
│   ├── Topography_Comprehensive_Analysis_executed.html    # HTML with code + outputs
│   ├── LANDFIRE_CC_Comprehensive_Analysis_executed.html   # HTML with code + outputs
│   └── FVEG22_Comprehensive_Analysis_executed.html        # HTML with code + outputs
├── environment.yml                    # Conda environment
└── CLAUDE.md                          # This file
```

### Key Constants (src/utils/constants.py)
```python
# CAL FIRE
FIRE_PERIMETERS_PATH = DATA_DIR / "Fireperimeters" / "California_Fire_Perimeters_All_Reprojected.gpkg"
HIGH_QUALITY_CUTOFF = 1993      # Year threshold for high-quality data
MEGA_FIRE_THRESHOLD = 100000    # Acres threshold for mega-fires
GRID_RESOLUTION_M = 800         # Target grid cell size in meters
CRS_ALBERS = "EPSG:3310"        # California Albers (metric)
CRS_WGS84 = "EPSG:4326"         # For web maps (Folium)

# MTBS
MTBS_FOD_PATH = DATA_DIR / "Fireignition_points" / "mtbs_fod_pts_data" / "mtbs_FODpoints_DD.shp"
CRS_NAD83 = "EPSG:4269"         # NAD83 (MTBS native CRS)
MTBS_WESTERN_MIN_ACRES = 1000   # Minimum fire size for western US
MTBS_EASTERN_MIN_ACRES = 500    # Minimum fire size for eastern US
MTBS_NODATA_SENTINEL = {-9999, 9999}  # Sentinel values for missing severity
MTBS_START_YEAR = 1984
MTBS_END_YEAR = 2024

# FPA FOD
FPA_FOD_PATH = DATA_DIR / "WildfireOccurenceData" / "Data" / "FPA_FOD_20221014.gpkg"
FPA_START_YEAR = 1992
FPA_END_YEAR = 2020

# Topography
TOPOGRAPHY_PATH = DATA_DIR / "Topography" / "Topography_Reprojected_Clipped.tif"
TOPO_NODATA = -32768
TOPO_NATIVE_RES_M = 27.19      # ~27m native resolution
TOPO_VIZ_DOWNSAMPLE = 30       # 30x downsample for visualization (~815m)
TPI_WINDOW_RADIUS = 10         # Pixel radius for TPI computation

# LANDFIRE 2024 Forest Canopy Cover (CC)
LANDFIRE_CC_PATH = DATA_DIR / "Vegetation_CONUS" / "LF2024_CC_CONUS" / "Tif" / "LF2024_CC_CONUS.tif"
LANDFIRE_CC_CSV_PATH = DATA_DIR / "Vegetation_CONUS" / "LF2024_CC_CONUS" / "CSV_Data" / "LF2024_CC.csv"
CRS_CONUS_ALBERS = "EPSG:5070"        # NAD83 / Conus Albers (LANDFIRE native)
LANDFIRE_CC_NODATA = -9999            # Sentinel for Fill-NoData
LANDFIRE_CC_RESOLUTION_M = 30         # Native pixel size
LANDFIRE_CC_VIZ_DOWNSAMPLE = 27       # 27x ≈ 810m for visualization
CA_BOUNDARY_PATH = Path("/Users/olivier/Documents/MyQGIS/WildfireAnalysis/DeepLearning/INPUTS_EPSG3310/California_State_Boundary_Reprojected.gpkg")

# FVEG22 Vegetation (FRAP CWHR, 2022 compilation)
FVEG22_PATH = DATA_DIR / "Vegetation" / "Vegetation_fveg22_1.tif"
FVEG22_NODATA = 65535
FVEG22_NATIVE_RES_M = 30.0
FVEG22_VIZ_DOWNSAMPLE = 40           # 40x → ~1200m for visualization
FVEG22_RAT_CSV_PATH = DATA_DIR / "Vegetation" / "fveg22_rat.csv"

# PRISM Climate Data (Oregon State University, 30-arcsecond ~800m)
PRISM_BASE_PATH = Path("/Volumes/LaCie/PRISM")
PRISM_CRS = "EPSG:4269"                         # NAD83 geographic
PRISM_NODATA = -9999.0
PRISM_RESOLUTION_DEG = 1 / 120                   # 0.008333° (~800m)
PRISM_CONUS_SHAPE = (3105, 7025)
PRISM_CA_BOUNDS = (-124.5, 32.5, -114.0, 42.0)  # west, south, east, north
PRISM_CA_WINDOW_SHAPE = (1140, 1260)
PRISM_DAILY_START_YEAR = 1981
PRISM_DAILY_END_YEAR = 2026
PRISM_MONTHLY_START_YEAR = 1895
PRISM_MONTHLY_END_YEAR = 2025
PRISM_VARIABLES = ["ppt", "tmax", "tmin", "tmean", "tdmean", "vpdmax", "vpdmin"]
PRISM_CACHE_DIR = OUTPUT_DIR / "cache" / "prism"
PRISM_VPD_CRITICAL_HPA = 45.0                    # Red Flag fire weather threshold
```

### Domain Value Mappings

**AGENCY Codes**:
| Code | Agency |
|------|--------|
| CDF | CAL FIRE (California Dept of Forestry & Fire Protection) |
| USF | USDA Forest Service |
| BLM | Bureau of Land Management |
| NPS | National Park Service |
| LRA | Local Responsibility Area |
| CCO | Contract County Organization |

**CAUSE Codes** (Top categories):
| Code | Description | % of Fires |
|------|-------------|------------|
| 14 | Unknown/Unidentified | ~30% |
| 1 | Lightning | ~20% |
| 9 | Miscellaneous | ~11% |
| 2 | Equipment Use | ~11% |
| 7 | Arson | ~7% |

**Unit ID Codes** (Examples):
| Code | Unit Name | Region |
|------|-----------|--------|
| SHU | Shasta-Trinity Unit | Northern CA |
| TUU | Tuolumne-Calaveras Unit | Sierra Nevada |
| LNU | Sonoma-Lake-Napa Unit | North Bay |
| RRU | Riverside Unit | Southern CA |

### MTBS Domain Mappings (src/utils/mtbs_domain_mappings.py)

**Incident Types**:
| Type | Description | % of CA Fires |
|------|-------------|---------------|
| Wildfire | Unplanned wildfire | ~88% |
| Prescribed Fire | Planned/managed burn | ~8% |
| Wildland Fire Use | Managed for resource benefit | ~3% |
| Unknown | Undetermined | ~1% |

**Assessment Types**: Initial, Initial (SS), Extended, Extended (SS), Emergency, Emergency (SS)
- "SS" = Single Scene (only post-fire imagery available)

**Severity Classes** (from dNBR thresholds):
| Class | Ecological Meaning |
|-------|-------------------|
| Increased Greenness | Vegetation growth post-fire (negative dNBR) |
| Unburned/Low | Minimal or no detectable change |
| Low | Surface burn with limited canopy damage |
| Moderate | Significant canopy damage |
| High | Complete canopy consumption/mortality |

### MTBS Data Loader (src/utils/mtbs_data_loader.py)

**Functions**:
- `load_mtbs_fod(path=None, state=None)` — Load shapefile, extract State from Event_ID, optional state filter
- `add_mtbs_derived_columns(gdf)` — Parse dates, add Ig_Year/Month/DayOfYear/Decade, Log10_BurnBndAc, Size_Category, Fire_Season, cleaned severity columns (*_clean), has_severity flag, severity_range
- `reproject_to_albers(gdf)` — NAD83 → EPSG:3310
- `get_mtbs_data_quality_summary(gdf)` — Quality metrics dict

### FPA FOD Domain Mappings (src/utils/fpa_domain_mappings.py)

**Mapping Dictionaries**:
- `NWCG_CAUSE_CLASSIFICATION_MAP` — Human / Natural / Missing
- `NWCG_GENERAL_CAUSE_MAP` — 13 cause categories with short labels
- `NWCG_REPORTING_AGENCY_MAP` — BIA, BLM, FS, NPS, ST/C&L, etc.
- `SOURCE_SYSTEM_TYPE_MAP` — FED / NONFED / INTERAGCY
- `FIRE_SIZE_CLASS_MAP` — A-G with descriptions and acre bounds
- `FIRE_SIZE_CLASS_ORDER` — Ordered list ["A", "B", ..., "G"]
- `OWNER_DESCR_MAP` — Raw ownership descriptions
- `OWNER_DESCR_STANDARDIZED` — Cleaned ownership categories for plotting
- `FIRE_SEASON_MAP` — Month → season (same as MTBS/CAL FIRE)

**Helper Functions**:
- `get_nwcg_cause_label(cause)` — Short label for 3-category classification
- `get_general_cause_label(cause)` — Short label for 13-category cause
- `get_fire_size_class_label(cls)` — Descriptive label for size class A-G
- `get_reporting_agency_label(code)` — Full agency name
- `get_source_system_label(type)` — Source system description
- `get_owner_standardized(owner)` — Standardized owner category

### FPA FOD Data Loader (src/utils/fpa_data_loader.py)

**Functions**:
- `load_fpa_fod(path=None, state=None, layer="Fires")` — Load GeoPackage with SQL WHERE for efficient state filtering
- `load_fpa_national_summary(path=None, columns=None)` — Load minimal national data for state comparison
- `load_fpa_unit_metadata(path=None)` — Load NWCG unit reference table
- `add_fpa_derived_columns(gdf)` — Parse dates, add Discovery_Year/Month/DayOfYear/Hour, Decade, Log10_FireSize, Size_Category, Fire_Season, Duration_Days, has_containment/county/mtbs_linkage flags, domain labels
- `reproject_to_albers(gdf)` — NAD83 → EPSG:3310
- `get_fpa_data_quality_summary(gdf)` — Completeness metrics dict

---

## CAL FIRE Comprehensive Notebook v2 Structure

### Parts Overview
| Part | Title | Key Visualizations |
|------|-------|-------------------|
| 1 | Introduction & Context | Table of contents, learning objectives |
| 2 | Data Loading & Quality | Completeness comparison, collection methods |
| 3 | Temporal Analysis | 125-year timeline, trends, decade comparison |
| 4 | Seasonal Patterns | Fire Clock (polar), heatmaps, season stats |
| 5 | Fire Size Analysis | Distribution, Pareto, size categories |
| 6 | Spatial Analysis | Overview map, interactive map, cumulative risk |
| 7 | Fire Causes | Cause breakdown, investigation challenges |
| 8 | Agency & Unit Analysis | Agency trends, unit activity, time series |
| 9 | Executive Summary & ML Readiness | Key findings, recommendations |

### Generated Figures (19 total)
| # | Figure | Description |
|---|--------|-------------|
| 1 | Data Completeness Comparison | Pre-1993 vs 1993+ quality |
| 2 | Collection Method Evolution | Stacked bar by decade |
| 3 | Temporal Timeline (Dual) | Fire count + burned acres 1900-present |
| 4 | Trend Analysis | 1950-present regression |
| 5 | Decade Comparison | 4-panel decade breakdown |
| 6 | Monthly Distribution | Fire count + acres by month |
| 7 | Fire Clock | Polar visualization with dual rings |
| 8 | Seasonal Heatmap | Year × Month matrix |
| 9 | Fire Season Statistics | Season comparison bars |
| 10 | Fire Size Distribution | Raw + log scale |
| 11 | Pareto Analysis | Cumulative burned area |
| 12 | Size Categories | Category breakdown |
| 13 | California Overview Map | All fires on basemap |
| 14 | Cumulative Fire Risk Map | Burn frequency on CartoDB basemap |
| 15 | Fire Causes | Dual panel by count/acres |
| 16 | Agency Response | Agency breakdown |
| 17 | Agency Trends | Time series by agency |
| 18 | Unit Activity | Top 15 units |
| 19 | Unit Trends | Time series by unit |

### Output Files
```
outputs/
├── CALFIRE_Comprehensive_Analysis_v2.pdf              # 3.4 MB - printable
├── CALFIRE_Comprehensive_Analysis_v2_executed.html    # 40 MB - web viewing (code + outputs)
├── figures/comprehensive/                              # 19 v2 figures + legacy (needs cleanup)
└── interactive/
    ├── mega_fires_interactive.html                    # Folium mega-fire map
    ├── mega_fires_map.html                            # Folium (alternate name)
    └── fire_density_heatmap.html                      # Fire density heatmap
```

**Note**: The `figures/comprehensive/` directory contains 48 files total: 19 current v2 figures (named `01_data_completeness_comparison.png` through `19_unit_trends_over_time.png`), plus 21 figures from an older notebook version (different naming, e.g., `01_data_quality_overview.png`), 3 extra versioned figures (`03b_`, `03c_`, `03d_`), and 4 test files (`test_*.png`). The legacy files should be cleaned up.

---

## MTBS Comprehensive Notebook Structure

### Parts Overview
| Part | Title | Key Visualizations |
|------|-------|-------------------|
| 1 | Introduction & Context | MTBS vs CAL FIRE comparison, learning objectives |
| 2 | Data Loading & Quality | Field completeness, severity availability by decade |
| 3 | National Context | State comparison (count/acres/median), western US trends |
| 4 | Temporal Analysis | 40-year timeline by incident type, decade comparison |
| 5 | Seasonal Patterns | Monthly distribution, month vs fire size |
| 6 | Fire Size & Incident Type | Distribution, Pareto/Lorenz, incident type breakdown |
| 7 | Burn Severity Deep Dive | Threshold distributions, size-severity, trends, season effects |
| 8 | Spatial Analysis | Overview map, interactive map, severity spatial patterns |
| 9 | Cross-Reference & ML Readiness | CAL FIRE comparison, feature engineering, model enhancement |

### Generated Figures (16 total)
| # | Figure | Description |
|---|--------|-------------|
| 1 | Data Quality Completeness | Field population rates + severity availability by decade |
| 2 | State Comparison | Top 15 states by count/acres/median size (CA highlighted) |
| 3 | Western US Trends | Fire count + acres by year for top 5 western states |
| 4 | Temporal Timeline | Annual fire count by incident type + burned acres with trend |
| 5 | Decade Comparison | 2x2 grid: count/acres/mean size/mega-fire count |
| 6 | Monthly Distribution | Fire count + acres colored by fire season |
| 7 | Month vs Fire Size | Box/violin log10(acres) by month + day-of-year scatter |
| 8 | Fire Size Distribution | Raw + log histogram + Pareto/Lorenz curve |
| 9 | Incident Type Analysis | Count + acres + size boxplot by incident type |
| 10 | Severity Threshold Distributions | KDE overlay + boxplots + Low vs High by decade |
| 11 | Severity vs Fire Size | Scatter acres vs High_T + boxplot by size category |
| 12 | Severity Trends Over Time | Mean High_T by year with CI + thresholds by decade |
| 13 | Severity by Season & Assessment | High_T by fire season + by assessment type |
| 14 | Spatial Overview Map | Centroids sized by acres, colored by decade, top 10 labeled |
| 15 | Severity Spatial Patterns | Centroids colored by High_T (RdYlGn_r), sized by acres |
| 16 | CAL FIRE Cross-Reference | Annual acres scatter + difference histogram + count comparison |

### Output Files
```
outputs/
├── figures/mtbs/                            # 16 PNG figures (300 DPI)
│   ├── 01_data_quality_completeness.png
│   ├── 02_state_comparison.png
│   ├── ...
│   └── 16_calfire_crossref_comparison.png
└── interactive/
    └── mtbs_fires_interactive.html          # Folium MarkerCluster map
```

---

## Key Findings from MTBS Analysis (Verified from Data)

### MTBS Dataset Statistics
| Metric | Full US | California |
|--------|---------|------------|
| Total Records | 30,730 | 2,051 |
| Year Range | 1984-2024 | 1984-2024 |
| States | 47 | 1 |
| Total Acres Burned | N/A | 25.6M |
| Severity Data Available | N/A | 77.1% (1,581 records) |

### Key MTBS Insights
- **Independent confirmation**: 2020 worst fire year, confirmed by satellite data
- **Wildfire dominance**: ~88% of MTBS records are wildfires
- **Severity data**: 77% of CA fires have dNBR severity thresholds
- **Temporal trend**: Clear post-2000 acceleration in both fire count and burned area
- **Seasonal pattern**: June-September peak matches CAL FIRE (84% of burned area)
- **Extreme concentration**: Heavy-tailed distribution — top fires dominate total area
- **Size-severity relationship**: Modest positive correlation between fire size and severity
- **Cross-reference**: Strong correlation between MTBS and CAL FIRE annual burned area

---

## Key Findings from FPA FOD Analysis (Verified from Data)

### FPA FOD Dataset Statistics
| Metric | Full US | California |
|--------|---------|------------|
| Total Records | 2,303,566 | 251,881 |
| Year Range | 1992-2020 | 1992-2020 |
| Total Acres Burned | N/A | 20.9M |
| Fires < 10 acres | N/A | 93.2% (234,651) |
| MTBS-linked records | N/A | 1,447 |
| Counties covered | N/A | 58 |

### Key FPA FOD Insights
- **Small fire dominance**: 93.2% of CA fires are under 10 acres — invisible to MTBS
- **Extreme concentration**: Top 0.6% of fires (>= 1,000 ac) account for 92.1% of burned area
- **Human-caused majority**: ~77% human-caused, ~16% lightning, ~7% missing/unknown
- **Diurnal patterns**: Human fires peak afternoon (13-15h), lightning fires peak late afternoon/evening
- **Duration available**: 53.2% of records have containment dates for duration analysis
- **Land ownership diversity**: 17 ownership categories; USFS and Private dominate
- **County geography**: 62.4% of records have county/FIPS codes for sub-state analysis
- **MTBS cross-reference**: 1,447 records link directly to MTBS via MTBS_ID field
- **Worst year confirmed**: 2020 worst fire year, consistent across all three datasets
- **Seasonal consistency**: June-September peak matches CAL FIRE and MTBS patterns

---

## Key Findings from Topography Analysis (Verified from Data)

### Topography Dataset Statistics
| Metric | Value |
|--------|-------|
| Raster Shape | 42,463 x 37,312 pixels (1.58 billion) |
| Native Resolution | 27.19m |
| File Size | 2.95 GB |
| Valid Pixels (downsampled) | 909,423 (51.7% — CA land vs ocean/border NoData) |
| Elevation Range | -84m to 4,207m |
| Mean Elevation | 763m |
| Median Elevation | 576m |
| Std Elevation | 749m |
| Mean Slope | 3.7° (at ~815m resolution) |
| Median Slope | 2.0° |
| Max Slope | 58.7° |
| Mean HLI | 0.970 |
| TPI Range | -1,084m to 1,877m |
| 800m Grid Shape | 1,443 x 1,268 (1.83M cells, 946K valid) |

### Elevation Zone Distribution (Verified)
| Zone | % of CA Land | Mean Elevation |
|------|-------------|----------------|
| Valley/Coast (<300m) | 38.1% | 65m |
| Foothill (300-900m) | 24.5% | 590m |
| Lower Montane (900-1800m) | 27.1% | 1,333m |
| Upper Montane (1800-2700m) | 8.6% | 2,108m |
| Subalpine (2700-3500m) | 1.5% | 3,021m |
| Alpine (>3500m) | 0.2% | 3,665m |

### Key Topography Insights
- **Fire-terrain relationship**: 13.5% of CA land burned (1993+); fires cluster at 300-1,800m (Foothill to Lower Montane)
- **KS tests highly significant**: Both elevation and slope distributions differ significantly between burned and unburned areas (KS=0.35/0.45, p≈0)
- **Slope effect**: Burned areas have steeper slopes than background California terrain
- **Aspect effect**: South/southwest-facing slopes (higher solar radiation) overrepresented in burned areas
- **Terrain correlations**: Slope-TWI strongly anticorrelated (r=-0.80); Elevation-TWI (r=-0.61); Slope-HLI (r=-0.50); Elevation-Slope (r=0.50)
- **800m aggregation**: Successfully computed all 7 terrain features (946K valid grid cells)
- **All MTBS centroids matched**: 2,051/2,051 CA fires have valid terrain data

---

## Key Findings from LANDFIRE CC Analysis (Verified from Data)

### LANDFIRE CC Dataset Statistics (California)
| Metric | Value |
|--------|-------|
| CONUS Raster Shape | 101,538 x 156,336 pixels |
| CA Clipped Shape | 45,027 x 33,671 pixels |
| CA Array Memory | 3.03 GB |
| Native Resolution | 30m |
| Valid Pixels (CA) | 479,437,858 (31.6% of clipped extent) |
| NoData Pixels | 1,036,666,259 (68.4% — ocean/buffer) |
| Non-Forested | 343,159,104 (71.6% of valid) |
| Forested | 136,278,754 (28.4% of valid) |
| 800m Grid Cells | 2,130,256 (1,688 x 1,262) |

### Key LANDFIRE CC Insights
- **California is predominantly non-forested**: 71.6% of valid pixels have 0% tree canopy (Central Valley, deserts, urban)
- **Dense forest is rare**: Only 5.3% of valid pixels have CC ≥ 60% (Dense + Very Dense categories)
- **Very Dense (80-100%) almost absent**: Just 0.17% of valid pixels; 90-100% class has only 520 pixels statewide
- **Burned areas have higher CC than statewide average**: Mean CC in burned areas = 17.9% vs 11.2% unburned — fires preferentially occur in forested areas
- **Strong elevation relationship**: Canopy cover peaks in Lower Montane (900-1,800m) and Upper Montane (1,800-2,700m) zones
- **Clear N-S gradient**: Northern California (Klamath, NW coast) has highest forest density; Southern CA/desert lowest
- **800m aggregation verified**: Mean CC at 800m = 12.4%, median = 1.5% (reflects dominant non-forested land)
- **Temporal caveat**: LANDFIRE CC 2024 is a snapshot — post-fire CC for 2015-2024 fires, pre-disturbance baseline for older fires

---

## Key Findings from FVEG22 Vegetation Analysis (Verified from Data)

### FVEG22 Dataset Statistics (California)
| Metric | Value |
|--------|-------|
| Raster Shape | 39,623 x 38,094 pixels (~1.5 billion) |
| Native Resolution | 30m |
| Valid Pixels | 462,177,661 (30.6% of raster extent) |
| NoData Pixels | ~1.05 billion (69.4% — ocean/buffer) |
| Unique Pixel Values | 42,032 |
| RAT Mappings Built | 20,390 (98.1% pixel coverage) |
| WHRTYPEs Represented | 62 of 65 defined types |
| Lifeform Categories | 8 |
| WHR13 Classes | 13 |

### FVEG22 Vegetation Composition
| Lifeform | % of Valid Pixels | Description |
|----------|-------------------|-------------|
| Shrub | 35.4% | Chaparral, scrub, desert shrub |
| Conifer | 17.8% | Pine, fir, mixed conifer forests |
| Hardwood | 13.0% | Oak, riparian, mixed hardwood |
| Agriculture | 12.1% | Cropland, orchard, vineyard |
| Herbaceous | 10.5% | Annual/perennial grassland |
| Urban | 6.3% | Developed areas |
| Water | 3.2% | Lakes, reservoirs, wetlands |
| Barren/Other | 1.7% | Rock, sand, barren |

### Top WHRTYPEs by Area
| WHRTYPE | Name | % of Pixels |
|---------|------|-------------|
| DSC | Desert Scrub | 18.8% |
| AGS | Annual Grassland | 8.7% |
| URB | Urban | 6.3% |
| MCH | Mixed Chaparral | 5.4% |
| CRC | Cropland | 5.2% |

### Fire Risk Classification
| Risk Level | % of Land | Key Types |
|------------|-----------|-----------|
| High | 33.7% | Chaparral, annual grassland, dry conifer, sage |
| Moderate | 16.0% | Oak woodland, mixed hardwood, perennial grass |
| Low | 27.1% | Dense conifer forest, riparian, wetland |
| Negligible | 23.3% | Urban, water, agriculture, barren |

### Fuel Type Classification
| Fuel Type | % of Land |
|-----------|-----------|
| Brush/Shrub | 42.8% |
| Non-Fuel | 24.2% |
| Timber | 23.4% |
| Grass | 9.6% |

### Key FVEG22 Insights
- **Shrub-dominated landscape**: 35.4% of California is shrub cover (chaparral, desert scrub), the most fire-prone lifeform
- **Desert Scrub is #1 WHRTYPE**: DSC covers 18.8% of the state, making it the single largest vegetation class
- **One-third is high fire risk**: 33.7% of California classified as High fire risk (chaparral, grassland, dry conifer)
- **Brush/Shrub dominates fuel types**: 42.8% of land area, driving fire behavior in much of the state
- **Forests are predominantly mature**: Size class 4 (Large trees) at 37.3% of forested pixels; Dense canopy (D) at 37.2%
- **Agricultural footprint**: 12.1% (Central Valley), effectively non-flammable for wildfire prediction
- **Urban-wildland interface**: 6.3% urban — boundary with adjacent high-risk vegetation is a key risk factor
- **RAT resolution challenge**: Local GeoTIFF uses different VALUE numbering than ArcGIS servers; required custom MapServer-based mapping (20,390 entries, 98.1% coverage)
- **62 of 65 WHRTYPEs present**: Near-complete representation of California's vegetation diversity

---

## Key Findings from PRISM Climate Analysis (Verified from Data)

### PRISM Dataset Statistics (California)
| Metric | Value |
|--------|-------|
| Total PRISM Archive | 5.0 TB, 112,612 files |
| Core Variables | 7 (ppt, tmax, tmin, tmean, tdmean, vpdmax, vpdmin) |
| Monthly Coverage | 1895–2025 (130 years, ~1,572 months per variable) |
| Daily Coverage | 1981–2026 (45 years) |
| CA Window Shape | 1,140 × 1,260 pixels |
| CA Valid Pixels | 1,086,516 (75.6% of window) |
| Resolution | 30 arcsecond (~800m) — matches project target grid |
| Precomputed CA Stats | 11,001 rows (7 vars × ~1,572 months), 1.5 MB CSV |

### Temperature Findings (130-Year Record)
| Finding | Verified Value | Source |
|---------|----------------|--------|
| CA mean annual Tmax | 21.6°C | Monthly stats |
| CA mean annual Tmin | 5.8°C | Monthly stats |
| CA mean annual Tmean | 13.7°C | Monthly stats |
| Tmin warming rate | +1.8°C over 130 years | Mann-Kendall trend |
| Tmax warming rate | +0.6°C over 130 years | Mann-Kendall trend |
| Nighttime vs daytime warming | Tmin warming 3× faster than Tmax | Trend comparison |
| Diurnal temperature range (DTR) | Decreasing (narrowing) | Derived from Tmax − Tmin |
| Hottest year on record (CA Tmax) | 2020 | Annual stats |
| Post-2000 warming acceleration | Visible step-change | Decadal analysis |

### Precipitation Findings (130-Year Record)
| Finding | Verified Value | Source |
|---------|----------------|--------|
| CA mean annual precipitation | 446 mm | Monthly stats |
| Wet season fraction (Oct–Mar) | ~71% of annual total | Seasonal analysis |
| Inter-annual variability (CV) | 24% | Standard deviation / mean |
| Driest month | July (8.2 mm normal) | 30-year normals |
| Wettest month | January (77.1 mm normal) | 30-year normals |
| Mediterranean climate pattern | Classic: wet winter, dry summer | Seasonal analysis |
| Long-term precipitation trend | No significant trend (stationary) | Mann-Kendall |
| Drought-wet oscillation | High year-to-year variability, no directional change | Time series |

### VPD Findings — The #1 Fire Predictor
| Finding | Verified Value | Source |
|---------|----------------|--------|
| CA mean annual VPDmax | ~19.5 hPa | Monthly stats |
| CA summer (JJA) mean VPDmax | ~37 hPa | Seasonal aggregation |
| July 2020 CA VPDmax | mean=42.4 hPa, p90=68.6 hPa | Monthly spatial stats |
| July VPDmax normal | mean=40.7 hPa | 30-year normals |
| Annual VPDmax trend | +0.13 hPa/decade | Mann-Kendall |
| Fire season VPDmax trend | +0.25 hPa/decade | Mann-Kendall |
| Post-2000 VPD step-change | +1.5 hPa jump in 2000s decade | Decadal analysis |
| CA national VPD ranking | #3 among CONUS states | State comparison |
| VPD critical threshold (Red Flag) | 45.0 hPa | Literature / fire weather |
| Estimated July RH (2020) | 17.9% (extreme fire weather) | Magnus formula from Tdmean & Tmax |

### Climate-Fire Integration Findings
| Finding | Verified Value | Source |
|---------|----------------|--------|
| 2020 fire year climate signature | #1 VPD, #2 drought, #3 heat | Multi-variable ranking |
| VPD–burned area correlation | R² ~0.25–0.40 | Annual scatter analysis |
| Fire season VPD trend significance | p = 0.007 | Mann-Kendall test |
| Burned vs unburned VPD | Significantly higher VPD at fire locations | KS test |
| Burned vs unburned PPT | Lower precipitation at fire locations | KS test |
| Pre-fire drought signal | Spring PPT deficit correlates with summer fire | Lag analysis |
| Antecedent VPD signal | 1–3 month VPD lags predict fire occurrence | Lag correlation |
| Severity–climate relationship | Higher VPD → higher burn severity (MTBS dNBR) | Severity overlay |
| Fire season lengthening | Earlier spring VPD rise, later fall decline | Seasonal trend |

### Key PRISM Insights
- **VPD is the strongest single climate predictor** of annual burned area in California (R² ~0.25–0.40)
- **Asymmetric warming**: Nighttime temperatures (Tmin) warming 3× faster than daytime (Tmax), reducing nighttime fire recovery
- **VPD acceleration**: Fire season VPD increasing at +0.25 hPa/decade with a step-change post-2000
- **Precipitation stationary**: Unlike temperature/VPD, precipitation shows no significant long-term trend — fire risk increase driven by temperature/VPD, not drought
- **2020 was a climate outlier**: Simultaneous #1 VPD, #2 drought, #3 heat produced the worst fire year (4.2M acres)
- **Mediterranean seasonality dominates**: 71% of precipitation falls Oct–Mar; fire season (Jun–Sep) is inherently moisture-limited
- **Spring drought → summer fire**: Antecedent precipitation deficit 1–6 months before fire season correlates with burned area
- **CA ranks #3 nationally for VPD**: Only Arizona and Nevada have higher atmospheric drying demand
- **30+ ML features identified**: Monthly VPD, temperature, precipitation (current + 1–6 month lags), anomalies, rolling sums, fire weather indices, VPD risk classes
- **CONUS state-level figures incomplete**: Only CA-only precomputation was run; full 48-state zonal stats (~2–3 hours) needed for complete CONUS figures

---

### LANDFIRE CC Notebook Structure

| Part | Title | Figures | Key Content |
|------|-------|---------|-------------|
| 1 | Introduction & Context | — | CC fire behavior relevance, temporal caveat |
| 2 | Data Loading & Quality | Fig 1 | CONUS metadata, CA clip, class distribution |
| 3 | Statewide Distribution | Fig 2-4 | Histogram, statewide map, elevation relationship |
| 4 | Regional Patterns | Fig 5-7 | Regional comparison, N-S gradient, E-W profiles |
| 5 | CC × Fire Perimeters | Fig 8-10 | Burned vs unburned, by fire size, temporal |
| 6 | CC × Burn Severity | Fig 11-13 | MTBS severity vs CC, by season, by decade |
| 7 | CC × Fire Size/Frequency | Fig 14-15 | Frequency by CC class, size distribution |
| 8 | Spatial Visualization | Fig 16-17 | Regional detail map, CC + fire overlay, Folium |
| 9 | ML Features & Summary | — | 800m aggregation demo, feature table, next steps |

### LANDFIRE CC Output Files
```
outputs/
├── figures/landfire_cc/                     # 17 PNG figures (300 DPI)
│   ├── 01_data_quality_class_distribution.png
│   ├── 02_canopy_cover_distribution.png
│   ├── ...
│   └── 17_cc_fire_overlay_map.png
└── interactive/
    └── landfire_cc_interactive.html         # Folium MarkerCluster map
```

---

### FPA FOD Notebook Structure

| Part | Title | Figures | Unique Value |
|------|-------|---------|-------------|
| 1 | Introduction & Context | — | 3-dataset comparison table |
| 2 | Data Loading & Quality | Fig 1 | Field completeness by decade |
| 3 | National Context | Fig 2-3 | All-size state comparison + size class |
| 4 | Temporal Analysis | Fig 4-5 | 29-year timeline by cause + decade grid |
| 5 | Seasonal Patterns & Duration | Fig 6-8 | Fire duration + discovery time-of-day |
| 6 | Fire Size Spectrum | Fig 9-10 | Full size spectrum + small fire dominance |
| 7 | Cause Attribution | Fig 11-13 | NWCG cause deep dive + trends |
| 8 | Spatial Analysis | Fig 14-16 | Land ownership + county geography + map |
| 9 | Cross-Ref & ML Readiness | Fig 17 | 3-dataset cross-reference via MTBS_ID |

### FPA FOD Output Files
```
outputs/
├── figures/fpa/                             # 17 PNG figures (300 DPI)
│   ├── 01_data_quality_completeness.png
│   ├── 02_state_comparison.png
│   ├── ...
│   └── 17_cross_reference.png
└── interactive/
    └── fpa_fires_interactive.html           # Folium MarkerCluster map (>= 100 ac)
```

---

## Topography Comprehensive Notebook Structure

### Topography Domain Mappings (src/utils/topo_domain_mappings.py)

**Elevation Zones**: Valley/Coast (<300m), Foothill (300-900m), Lower Montane (900-1800m), Upper Montane (1800-2700m), Subalpine (2700-3500m), Alpine (>3500m)

**Slope Classes**: Flat (0-5°), Gentle (5-15°), Moderate (15-30°), Steep (30-45°), Very Steep (>45°)

**Aspect Classes**: N, NE, E, SE, S, SW, W, NW, Flat (slope < 5°)

**TPI Classes**: Valley, Lower Slope, Flat/Mid, Upper Slope, Ridge (std-based thresholds)

**Classification Functions**: `classify_elevation()`, `classify_slope()`, `classify_aspect()`, `classify_tpi()`

### Topography Data Loader (src/utils/topo_data_loader.py)

**Functions**:
- `load_topography_metadata(path)` — Metadata without pixel read
- `load_topography_downsampled(path, factor)` — Decimated read (30x → ~815m)
- `load_topography_window(path, bounds/window)` — Spatial subset
- `compute_slope_aspect(elevation, transform)` — Slope (°) + aspect (°, 0=N CW)
- `compute_tpi(elevation, radius_px)` — Topographic Position Index
- `compute_twi(slope_deg, cell_size_m)` — Simplified Topographic Wetness Index
- `compute_heat_load_index(slope_deg, aspect_deg)` — McCune & Keon (2002) HLI
- `aggregate_to_grid(path, target_res_m)` — 800m aggregation via rasterio reproject
- `extract_terrain_at_points(raster, transform, points_gdf)` — Sample at MTBS centroids
- `extract_terrain_for_polygons(raster, transform, polygons_gdf)` — Zonal stats for perimeters
- `get_topo_data_quality_summary(elevation)` — Quality metrics

### Topography Parts Overview
| Part | Title | Key Visualizations |
|------|-------|-------------------|
| 1 | Introduction & Context | Why topography matters for fire |
| 2 | Data Loading & Quality | Fig 01: data mask, histogram, CDF, stats table |
| 3 | Elevation Analysis | Fig 02-04: elevation map, distribution, zone map |
| 4 | Slope Analysis | Fig 05-06: slope map, classification, slope-by-zone |
| 5 | Aspect Analysis | Fig 07-08: aspect map, polar plot, HLI map |
| 6 | Advanced Derivatives | Fig 09-11: TPI, TWI, correlation matrix |
| 7 | Fire Overlay | Fig 12-14: burned vs unburned, severity-terrain |
| 8 | Spatial Analysis | Fig 15-16: transects, composite susceptibility |
| 9 | 800m Grid & ML | Fig 17-18: 800m preview, feature dashboard |

### Topography Generated Figures (18 total)
| # | Figure | Description |
|---|--------|-------------|
| 1 | Data Quality Overview | 2x2: valid mask, histogram, CDF, stats table |
| 2 | Elevation Map | California terrain with geographic labels |
| 3 | Elevation Distribution | Histogram with zone boundaries + area proportions |
| 4 | Elevation Zones Map | 6-class ecological zone classification |
| 5 | Slope Map | Continuous slope in degrees |
| 6 | Slope Distribution | 2x2: histogram, class bar, slope-by-zone, classified map |
| 7 | Aspect Map | 8-direction classified aspect |
| 8 | Aspect Analysis | 2x2: polar plot, aspect-by-zone, HLI map, HLI distribution |
| 9 | TPI Analysis | TPI map (diverging) + class distribution |
| 10 | TWI Map | Simplified topographic wetness index |
| 11 | Terrain Correlation Matrix | Heatmap of all terrain variable correlations |
| 12 | Fire-Terrain Distributions | 2x3: burned vs unburned elevation/slope/aspect |
| 13 | Burned vs Unburned CDFs | 2x2: KS tests, burn frequency by elevation/slope |
| 14 | Severity-Terrain | 2x2: elevation/slope/HLI by MTBS severity + stats table |
| 15 | Regional Terrain Profiles | E-W and N-S transects with fire overlay |
| 16 | Terrain Susceptibility | Composite: 50% slope + 30% HLI + 20% TPI |
| 17 | 800m Grid Preview | 2x2: elevation, slope, aspect, heterogeneity at 800m |
| 18 | ML Feature Summary | 7-feature dashboard with distributions and statistics |

### Topography Output Files
```
outputs/
├── figures/topography/                     # 18 PNG figures (300 DPI)
│   ├── 01_data_quality_overview.png
│   ├── 02_elevation_map.png
│   ├── ...
│   └── 18_ml_feature_summary.png
└── interactive/
    └── topo_fires_interactive.html         # Folium map with terrain stats popups
```

---

## LANDFIRE CC Utility Module Documentation

### LANDFIRE Domain Mappings (src/utils/landfire_domain_mappings.py)

**Mapping Dictionaries**:
- `CC_VALUE_MAP` — CC value (0, 15, 25, ..., 95) → descriptive label
- `CC_MIDPOINT_MAP` — CC value → midpoint percentage for continuous conversion
- `CC_ORDERED_VALUES` — Ordered list [0, 15, 25, ..., 95]
- `CC_RGB_MAP` — CC value → (R, G, B) normalized tuple (from LANDFIRE CSV)
- `CC_BROAD_CATEGORIES` — CC value → broad category (5 groups)
- `CC_BROAD_CATEGORY_ORDER` — Ordered list of broad category names
- `CC_BROAD_CATEGORY_COLORS` — Broad category → hex color

**Helper Functions**:
- `get_cc_label(value)` — Descriptive label for CC value
- `get_cc_color(value)` — RGB color tuple for CC value
- `get_cc_broad_category(value)` — Broad category name
- `build_cc_colormap()` — matplotlib ListedColormap for CC classes
- `build_cc_norm()` — matplotlib BoundaryNorm for CC values
- `classify_canopy_cover(cc_values)` — Array classification into broad categories

### LANDFIRE Data Loader (src/utils/landfire_data_loader.py)

**Functions**:
- `load_landfire_cc_metadata(path)` — Raster metadata without pixel read
- `clip_cc_to_california(path, ca_boundary_path, buffer_m)` — CONUS → CA clip via rasterio.mask
- `reproject_cc_to_albers(cc_array, src_transform, src_crs)` — EPSG:5070 → EPSG:3310 (nearest-neighbor)
- `load_cc_california(path, ca_boundary_path)` — Convenience: clip + reproject in one call
- `load_cc_downsampled(cc_array, transform, factor)` — Downsample for visualization (27x → ~810m)
- `extract_cc_at_points(cc_array, transform, points_gdf)` — Sample CC at fire points
- `extract_cc_for_polygons(cc_array, transform, polygons_gdf)` — Zonal stats (mean_cc_pct, dominant_cc, forested_fraction)
- `get_cc_class_distribution(cc_array, resolution_m)` — DataFrame of pixel counts + area per class
- `get_cc_data_quality_summary(cc_array)` — Quality metrics dict

**Processing Pipeline**:
1. `clip_cc_to_california()` — Windowed read of CONUS raster using CA boundary (memory-efficient)
2. `reproject_cc_to_albers()` — Nearest-neighbor reprojection (categorical data)
3. `load_cc_downsampled()` — Block subsample for visualization

**Temporal Caveat**: LANDFIRE CC 2024 is a snapshot incorporating 2015-2024 disturbances. Historical fires (pre-2015) occurred under different canopy conditions.

---

## FVEG22 Vegetation Utility Module Documentation

### Vegetation Domain Mappings (src/utils/vegetation_domain_mappings.py)

**Mapping Dictionaries**:
- `WHRTYPE_MAP` — 65 WHRTYPE codes → descriptive names
- `LIFEFORM_MAP` — 8 lifeform categories with display labels
- `LIFEFORM_ORDER` — Ordered list for consistent plotting
- `WHR13_MAP` — 13 WHR13 class numbers → names
- `WHR13_ORDER` — Ordered list for consistent plotting
- `WHRTYPE_TO_LIFEFORM` — 65-entry WHRTYPE → LIFEFORM lookup
- `WHRTYPE_TO_WHR13` — 65-entry WHRTYPE → WHR13 lookup
- `WHRSIZE_MAP` — Size codes (1–6, X) → descriptions with DBH ranges
- `WHRDENSITY_MAP` — Density codes (S, P, M, D, X) → cover percentages
- `FIRE_PRONE_WHRTYPE` — Fire risk ratings (High/Moderate/Low/Negligible) for each type
- `FIRE_RISK_ORDER` — Ordered list for consistent plotting

**Helper Functions**:
- `get_whrtype_name(code)` — Descriptive name for WHRTYPE code
- `get_lifeform(code)` — Lifeform category for WHRTYPE code
- `get_whr13_class(code)` — WHR13 class for WHRTYPE code
- `get_fire_risk_level(code)` — Fire risk rating for WHRTYPE code
- `parse_whrall(whrall)` — Parse 5-char WHRALL code into components
- `classify_fire_fuel_type(whrtype_codes)` — Classify into Timber/Brush/Grass/Non-Fuel

### Vegetation Data Loader (src/utils/vegetation_data_loader.py)

**Functions**:
- `load_vegetation_metadata(path)` — Raster metadata without pixel read
- `load_vegetation_downsampled(path, factor)` — Decimated read with nearest resampling (40x → ~1200m)
- `load_vegetation_window(path, bounds, window)` — Spatial subset read
- `get_unique_values_and_counts(path, chunk_rows)` — Chunked scan for unique values (~75 MB/chunk)
- `load_local_rat(path)` — Load local VALUE→WHRTYPE mapping CSV
- `load_imageserver_rat(path)` — Load ImageServer reference RAT CSV
- `download_rat_csv(dest_path)` — Download RAT from ArcGIS ImageServer endpoint
- `get_value_to_attributes(local_rat_path, imageserver_rat_path)` — Cascade: local → ImageServer → download
- `merge_values_with_rat(value_counts_df, local_rat)` — Join values with CWHR attributes
- `extract_vegetation_at_points(values, transform, points_gdf)` — Sample vegetation at fire points
- `get_vegetation_data_quality_summary(values, nodata)` — Quality metrics dict

**RAT Cascade Strategy**:
1. Load `fveg22_local_rat.csv` — local VALUE→WHRTYPE mapping (primary, 98.1% pixel coverage)
2. Load `fveg22_rat.csv` — ImageServer reference RAT (for WHRTYPE reference tables)
3. Download from ArcGIS ImageServer — last resort
4. Graceful degradation — raw value analysis only

**Key Difference from Other Loaders**: Uses `Resampling.nearest` (not `.average`) because FVEG22 is categorical. The local GeoTIFF uses different VALUE numbering than the ImageServer, requiring a separate local RAT built via the MapServer identify endpoint.

### FVEG22 Notebook Structure

| Part | Title | Figures | Key Content |
|------|-------|---------|-------------|
| 1 | Introduction & Context | — | CWHR system, FVEG22 vs LANDFIRE CC |
| 2 | Data Loading & Quality | Fig 1 | Metadata, valid/NoData coverage, RAT resolution |
| 3 | Value Distribution | Fig 2–3 | Raw value distribution, WHRTYPE breakdown |
| 4 | Lifeform & WHR13 | Fig 4–5 | Lifeform composition, WHR13 classification |
| 5 | Spatial Analysis | Fig 6–8 | CA vegetation map, regional composition, coverage |
| 6 | Fire-Relevant Vegetation | Fig 9–11 | Fire-prone types, fire-prone map, fuel classification |
| 7 | Vegetation Structure | Fig 12–13 | Tree size class, canopy density analysis |
| 8 | Fire Overlay | Fig 14–15 | Burned vs unburned composition, fire-vegetation crosstab |
| 9 | 800m Grid & ML Readiness | Fig 16 | Resolution comparison, ML feature summary |

### FVEG22 Generated Figures (16 total)

| # | Figure | Description |
|---|--------|-------------|
| 01 | `01_data_quality_overview.png` | Valid/NoData coverage + value histogram + quality table |
| 02 | `02_value_distribution.png` | Raw value histogram + CDF + top 30 values |
| 03 | `03_whrtype_classification.png` | Top 30 WHRTYPEs by pixel count, colored by lifeform |
| 04 | `04_lifeform_composition.png` | 8 lifeform categories pie + bar |
| 05 | `05_whr13_classification.png` | 13 WHR13 classes horizontal bar |
| 06 | `06_california_vegetation_map.png` | Full state map colored by lifeform |
| 07 | `07_regional_vegetation_composition.png` | N/Central/S CA comparison pies |
| 08 | `08_spatial_coverage_map.png` | Valid data coverage mask |
| 09 | `09_fire_prone_vegetation.png` | Fire risk proportions + top fire-prone types |
| 10 | `10_fire_prone_map.png` | Spatial map colored by fire risk level |
| 11 | `11_fuel_type_classification.png` | Fuel type distribution + map |
| 12 | `12_size_structure_analysis.png` | Tree size class distribution + by lifeform |
| 13 | `13_density_structure_analysis.png` | Canopy density distribution + by WHR13 |
| 14 | `14_vegetation_burned_areas.png` | Burned vs unburned lifeform composition |
| 15 | `15_vegetation_fire_crosstab.png` | Burn rate by WHR13 + composition comparison |
| 16 | `16_800m_grid_preview.png` | Resolution comparison + ML feature table |

### FVEG22 Output Files
```
outputs/
├── figures/vegetation/                     # 16 PNG figures (300 DPI)
│   ├── 01_data_quality_overview.png
│   ├── 02_value_distribution.png
│   ├── ...
│   └── 16_800m_grid_preview.png
```

---

## PRISM Climate Utility Module Documentation

### PRISM Domain Mappings (src/utils/prism_domain_mappings.py)

**Mapping Dictionaries**:
- `PRISM_VARIABLE_META` — 7-variable dict with full_name, short_label, units, CA ranges, fire_relevance, is_cumulative, colormap, colormap_anomaly
- `FIRE_WEATHER_VPD_CLASSES` — 6-class VPD risk: Minimal (<10), Low (10-20), Moderate (20-30), High (30-40), Extreme (40-50), Exceptional (>50)
- `DROUGHT_CLASSES` — 7-class drought severity based on % of normal precipitation
- `CA_CLIMATE_REGIONS` — 8 geographic regions with lat/lon bounding boxes
- `CONUS_STATES` — 49 entries (48 CONUS + DC), state abbreviation → full name
- `WESTERN_US_STATES` — 11 western fire-prone states
- `DERIVED_VARIABLES` — 7 derived variable definitions (DTR, VPD mean, DPD, est. RH, etc.)
- `CLIMATE_SEASON_MAP` — Month → meteorological season

**Helper Functions**:
- `get_variable_meta(var)`, `get_variable_label(var)`, `get_variable_colormap(var, anomaly=False)`
- `classify_vpd(vpd_values)` — Fire weather VPD class
- `classify_drought(precip_pct_normal)` — Drought severity class
- `month_to_water_year(year, month)` — Calendar → water year conversion
- `compute_rh_from_tdmean_tmax(tdmean, tmax)` — Estimate minimum RH (Magnus formula)

### PRISM Data Loader (src/utils/prism_data_loader.py)

~1,700 lines covering:

**Drive Management & File Discovery**:
- `check_prism_drive(base_path)` — Verify external drive mounted
- `discover_files(variable, temporal, year, month)` — List available zip files
- `build_file_inventory(variables, temporal, year_range)` — Complete inventory DataFrame
- `parse_filename(filepath)` — Extract variable, date, temporal type

**Zip-Aware Raster I/O**:
- `read_prism_raster(zip_path, bounds, window)` — Generic windowed read from zip
- `read_prism_california(zip_path)` — CA-only read (~5.5 MB, ~0.3s)
- `read_prism_conus(zip_path)` — Full CONUS read

**Batch Loading**:
- `load_monthly_series(variable, start_year, end_year, months)` — 3D monthly stack
- `load_daily_series(variable, start_date, end_date, bounds)` — 3D daily stack
- `load_monthly_stats_ca(variable, start_year, end_year)` — Memory-efficient stats-only DataFrame

**Normals & Anomalies**:
- `load_monthly_normal(variable, month, bounds)` — 30-year normal
- `load_all_monthly_normals(variable, bounds)` — All 12 months
- `compute_monthly_anomaly(observed, normal, variable)` — Anomaly + pct_normal

**Derived Fire Weather Variables**:
- `compute_diurnal_temp_range()`, `compute_vpd_mean()`, `compute_dew_point_depression()`
- `compute_estimated_rh()`, `compute_cumulative_vpd()`, `compute_dry_day_count()`

**State-Level Extraction**:
- `load_us_states_boundaries()` — Download/cache Census TIGER/Line shapefile
- `compute_state_statistics(zip_path, states_gdf)` — Per-state zonal stats
- `precompute_state_monthly_summaries()` — Main batch function

**Caching**:
- `save_to_cache(data, name)` / `load_from_cache(name)` — CSV fallback (no pyarrow)

### PRISM Precomputation Script (scripts/prism_precompute_state_summaries.py)

Standalone batch script with CLI args:
- `--ca-only` — Only CA monthly stats (~45-60 min)
- `--resume-from` — Resume from specific variable
- `--year-start`, `--year-end` — Custom year range

Output: `outputs/cache/prism/prism_ca_monthly_stats.csv` (~2 MB, 7 vars × 1572 months)

### PRISM Notebook Structure

#### Part 1: CONUS + All 48 States (22 figures)
| Part | Title | Figures |
|------|-------|---------|
| 1 | Introduction & Context | — |
| 2 | Data Loading & Quality | Fig 1 |
| 3 | CONUS Spatial Patterns | Fig 2-5 |
| 4 | All-State Rankings & Profiles | Fig 6-11 |
| 5 | Long-Term CONUS Trends | Fig 12-15 |
| 6 | Seasonal Patterns — All States | Fig 16-19 |
| 7 | CONUS Climate Regions | Fig 20 |
| 8 | All-State Summary & Interactive Map | Fig 21-22 |
| 9 | Executive Summary | — |

#### Part 2: California Deep Dive (18 figures)
| Part | Title | Figures |
|------|-------|---------|
| 1 | Introduction & Context | — |
| 2 | Data Loading & Quality | Fig 1-2 |
| 3 | Long-Term Temperature Trends | Fig 3-6 |
| 4 | Precipitation Regime | Fig 7-10 |
| 5 | VPD — The #1 Fire Predictor | Fig 11-15 |
| 6 | Derived Climate Indices | Fig 16-17 |
| 7 | CA Climate Region Profiles | Fig 18 |
| 8 | 30-Year Normals Deep Dive | — |
| 9 | Executive Summary & ML Readiness | — |

#### Part 3: Climate-Fire Integration (16 figures)
| Part | Title | Figures |
|------|-------|---------|
| 1 | Introduction & Context | — |
| 2 | Data Loading & Alignment | Fig 1 |
| 3 | Climate at Fire Locations | Fig 2-4 |
| 4 | Fire Year Climate Conditions | Fig 5-7 |
| 5 | Seasonal Fire-Climate Coupling | Fig 8-10 |
| 6 | Pre-Fire Climate Signals | Fig 11-13 |
| 7 | Fire Severity × Climate | Fig 14-15 |
| 8 | Spatial Climate-Fire Patterns | Fig 16 |
| 9 | ML Feature Summary | — |

---

## Notebook Execution Verification (March 2026)

All 9 notebooks have been verified to execute successfully with zero errors:

| Notebook | Phase | Cells (MD/Code) | Figures | Errors | Exec Size |
|----------|-------|-----------------|---------|--------|-----------|
| CAL FIRE v2 | 1.5 | 62 (36/26) | 20 | 0 | 39.7 MB |
| MTBS FOD | 1.75 | 49 (26/23) | 18 | 0 | 6.9 MB |
| FPA FOD | 1.875 | 37 (14/23) | 17 | 0 | 11.9 MB |
| Topography | 2A | 40 (12/28) | 18 | 0 | 16.8 MB |
| LANDFIRE CC | 1.9 | 42 (12/30) | 17 | 0 | 6.4 MB |
| FVEG22 | 2B | 36 (12/24) | 16 | 0 | 2.4 MB |
| PRISM CONUS | 3A | 38 (11/27) | 22 | 0 | — |
| PRISM California | 3A | 32 (11/21) | 18 | 0 | — |
| PRISM Fire Overlay | 3A | 31 (11/20) | 16 | 0 | — |

**Total**: 367 cells, 162 figures, 0 errors across all notebooks.

### Known Issues
- **CAL FIRE v2**: Oldest notebook; does not use `save_figure()` or `setup_plotting_style()` utilities (predates them). Uses inline color dicts instead of `get_agency_colors()` etc. Part 7 (Fire Causes) is thinner than other parts.
- **FPA FOD & FVEG22**: Source notebooks had missing trailing newlines in cell source lists (nbformat quirk from programmatic creation). Fixed March 2026 — does not affect interactive use, only `nbconvert --execute`.
- **Missing cell IDs**: MTBS, Topography, LANDFIRE CC, FVEG22 notebooks lack nbformat v5 cell IDs (cosmetic warning, does not affect execution).
- **Kernel name**: Older notebooks reference `wildfire` kernel, newer ones use `python3`. Both resolve to the same Python in the wildfire conda env.
- **Stale figures**: `outputs/figures/comprehensive/` has 48 files (19 current + 29 legacy). Other figure directories are clean.
- **PRISM CONUS figures**: Many state-level figures in Notebook 1 are incomplete because only CA-only precomputation was run. Full CONUS state zonal stats (~2-3 hours on external drive) needed to populate all 48-state visualizations.
- **PRISM precomputation**: Script has incremental save + resume capability after crash fixes. Bad zip files (e.g., `vpdmin 196107`) caught and skipped gracefully. Cache: `prism_ca_monthly_stats.csv` (11,001 rows, 1.5 MB).

---

## Environment Setup

### Create Conda Environment
```bash
cd /Users/olivier/Documents/CLAUDE/wildfire_prediction_model_california
conda env create -f environment.yml
conda activate wildfire
```

### Key Dependencies
- `geopandas>=0.14` - Geospatial data handling
- `pandas>=2.0` - Data manipulation
- `numpy>=1.24` - Numerical operations
- `matplotlib>=3.7` - Static visualizations
- `seaborn>=0.12` - Statistical visualizations
- `folium>=0.14` - Interactive maps
- `contextily>=1.3` - Basemap tiles
- `rasterio>=1.3` - Raster operations
- `scipy>=1.11` - Statistical functions
- `ipykernel` - Jupyter kernel (in wildfire env)

**Note**: JupyterLab is installed in the base conda environment (v4.3.4), NOT in the wildfire env. The wildfire env provides the `wildfire` and `python3` kernels. Use base conda `jupyter lab` to launch, then select the wildfire kernel.

### Run Notebooks
```bash
# Launch JupyterLab (from base conda, which has jupyterlab installed)
jupyter lab notebooks/

# Or execute a notebook headlessly with the wildfire kernel
conda run -n wildfire jupyter nbconvert --execute --to notebook \
  notebooks/FVEG22_Comprehensive_Analysis.ipynb \
  --ExecutePreprocessor.timeout=600
```

### Export to HTML
```bash
# Convert executed notebook to HTML (with code visible)
conda run -n wildfire jupyter nbconvert --to html \
  notebooks/CALFIRE_Comprehensive_Analysis_v2_executed.ipynb --output-dir outputs/

# Convert without code (results only)
conda run -n wildfire jupyter nbconvert --to html --no-input \
  notebooks/CALFIRE_Comprehensive_Analysis_v2_executed.ipynb --output-dir outputs/
```

---

## ML Model Recommendations

### Training Data
- Use **1993+ data** as primary training dataset
- >97% completeness for key fields
- 30+ years provides sufficient temporal range

### Feature Engineering Opportunities
**From CAL FIRE Perimeter Data:**
- Historical burn frequency (cumulative risk map)
- Time since last fire at location
- Fire season (High Risk / Transition / Low Risk)
- Month and day of year
- Agency jurisdiction
- Unit ID (administrative region)

**From MTBS Severity Data:**
- Historical burn severity at grid cell (dNBR High_T, Mod_T, Low_T)
- Regional severity baseline (spatial aggregation of nearby fires)
- Severity trend over time (is severity increasing in a region?)
- Cross-validated burned area (MTBS BurnBndAc vs CAL FIRE GIS_ACRES)
- Time since last severe fire at location

**From FPA FOD Point Data:**
- Fire count density (historical ignition frequency per grid cell)
- Cause probability (P(human) vs P(lightning) per cell)
- Time-of-day risk profile (from DISCOVERY_TIME)
- Fire duration prediction (from Duration_Days)
- Land ownership features (from OWNER_DESCR)
- Small fire frequency (Class A-C density per cell)
- County-level statistics (from COUNTY/FIPS)
- MTBS severity linkage (connect point data to severity rasters via MTBS_ID)

**From Topography Data (Phase 2A - COMPLETE):**
- Elevation at grid cell (mean, min, max, heterogeneity)
- Slope (mean degrees, classified: Flat/Gentle/Moderate/Steep/Very Steep)
- Aspect (classified: N/NE/E/SE/S/SW/W/NW, plus Heat Load Index)
- Topographic Position Index (TPI: Valley/Lower Slope/Flat/Upper Slope/Ridge)
- Topographic Wetness Index (TWI: moisture accumulation proxy)
- Heat Load Index (HLI: solar radiation proxy, McCune & Keon 2002)
- Terrain susceptibility composite (50% slope + 30% HLI + 20% TPI)

**From LANDFIRE Canopy Cover Data (Phase 1.9 - COMPLETE):**
- Forest canopy cover percentage at grid cell (mean CC %, verified: statewide mean 12.4%)
- Forested fraction (proportion of cell with CC > 0%, 28.4% statewide)
- Dominant CC class (mode within grid cell)
- Broad category (Non-Forested / Open / Moderate / Dense / Very Dense)
- CC heterogeneity (std deviation of CC within 800m cell)
- CC edge density (proportion of cells with mixed forest/non-forest)
- Canopy-fire interaction (CC × slope, CC × HLI)

**From FVEG22 Vegetation Data (Phase 2B - COMPLETE):**
- Dominant WHRTYPE at grid cell (mode of 65 vegetation types)
- Dominant lifeform category (Conifer/Hardwood/Shrub/Herbaceous/etc.)
- Dominant WHR13 class (13 aggregated land cover classes)
- Fire risk level of dominant type (High/Moderate/Low/Negligible)
- Timber fuel fraction (proportion of timber-fuel pixels in cell)
- Brush/shrub fuel fraction (proportion of brush-fuel pixels)
- Grass fuel fraction (proportion of grass-fuel pixels)
- Vegetation diversity (count of unique WHRTYPEs per cell)
- Mean tree size class (average WHRSIZE 1–6 for forested pixels)
- Mean canopy density (ordinal mean of WHRDENSITY S/P/M/D)
- Vegetation × topography interactions (chaparral × slope, conifer × elevation)

**From PRISM Climate Data (Phase 3A - IN PROGRESS):**
- Monthly VPD at grid cell (VPDmax, VPDmin — current month + 1-6 month lags)
- Monthly temperature (Tmax, Tmin, Tmean, DTR — current + lags)
- Monthly precipitation (PPT — current + cumulative 3/6/12 month)
- Monthly moisture (Tdmean, estimated RH, dew point depression)
- All-variable anomalies vs 30-year normals (current + lags)
- Seasonal aggregations (fire season VPD, winter PPT total, water year PPT)
- Cumulative stress indices (rolling VPD sum 30/60/90 day, dry day count, PPT deficit)
- Fire Weather Index composite (simplified FWI 0-1)
- VPD fire risk class (6-class: Minimal → Exceptional)
- Climate × topography interactions (VPD × slope, VPD × elevation)
- Climate × vegetation interactions (VPD × chaparral fraction, PPT × conifer fraction)

**To Add:**
- Human: Roads, population density

### Model Architecture
| Component | Recommendation |
|-----------|---------------|
| Grid Resolution | 800m × 800m |
| Target Variable | Binary (burned/not-burned) OR multi-class severity |
| Temporal Unit | Monthly or seasonal |
| Architecture | CNN + LSTM |
| Loss Function | Focal Loss (binary) or Weighted CE / Ordinal Regression (severity) |
| Validation | Temporal split (Train: 1993-2019, Test: 2020+) |

### Known Challenges
1. **Class Imbalance**: ~99% of grid cells never burn
2. **Non-Stationarity**: Climate change affects patterns
3. **Rare Events**: Mega-fires cause most damage but are rare
4. **Cause Attribution**: ~30% of fires have unknown causes

---

## Next Steps for Development

### Phase 2: Grid Creation
1. Generate 800m × 800m grid in EPSG:3310
2. Create California state mask (exclude water, ocean)
3. Rasterize fire perimeters to binary grid cells
4. Assign MTBS centroids to grid cells for severity integration
5. Assign FPA FOD points to grid cells for ignition density, cause, duration features
6. Aggregate topography derivatives to 800m grid (elevation, slope, aspect, TPI, TWI, HLI — already computed in Phase 2A)
7. Aggregate LANDFIRE CC to 800m grid (mean CC%, forested fraction, dominant class — demo in Phase 1.9)
8. Aggregate FVEG22 vegetation to 800m grid (dominant WHRTYPE, lifeform, fuel type, diversity — utility modules in Phase 2B)
9. Create temporal aggregations (monthly, seasonal, annual)

### Phase 3: Data Integration
1. Merge MTBS severity data with CAL FIRE perimeters for comprehensive fire characterization
2. Acquire PRISM climate data
3. ~~Acquire fuel/vegetation data~~ **LANDFIRE CC complete (Phase 1.9); consider EVT for species-level fuel characterization**
4. Align all datasets to common 800m grid (topography already aligned in Phase 2A)

### Phase 4: ML Development
1. Design CNN/LSTM architecture
2. Implement data pipeline
3. Train initial models
4. Evaluate and iterate

---

## Reference Documents

Located in `Datasets/`:
- `Data_Dictionary_California_Fire_Perimeters.pdf` - CAL FIRE field definitions
- `CAL_Fire_Data_Analysis_Summary.pdf` - Previous analysis
- `CA_Fire_Proposal__Tam_Air_Club__UCI__UCSF__CAL_FIRE_.pdf` - Collaboration proposal
- `Fireignition_points/mtbs_fod_pts_data/mtbs_FODpoints_DD_metadata.xml` - MTBS metadata
- `WildfireOccurenceData/Data/_variable_descriptions.csv` - FPA FOD field descriptions

---

## Contact and Collaboration

- **Project Lead**: Olivier (Tam Air Club)
- **Data Sources**: CAL FIRE FRAP, USGS/USDA Forest Service MTBS, USDA Forest Service FPA FOD, USGS National Map, LANDFIRE, Oregon State University PRISM
- **Data Portals**: https://frap.fire.ca.gov/ | https://www.mtbs.gov/ | https://doi.org/10.2737/RDS-2013-0009.6 | https://landfire.gov/ | https://prism.oregonstate.edu/

---

*Last Updated: March 2026*
*Phase 1 (EDA) Status: COMPLETE*
*Phase 1.5 (CAL FIRE Comprehensive Notebook v2): COMPLETE*
*Phase 1.75 (MTBS Comprehensive Analysis): COMPLETE*
*Phase 1.875 (FPA FOD Comprehensive Analysis): COMPLETE*
*Phase 1.9 (LANDFIRE CC Comprehensive Analysis): COMPLETE*
*Phase 2A (Topography Comprehensive Analysis): COMPLETE*
*Phase 2B (FVEG22 Vegetation Comprehensive Analysis): COMPLETE*
*Phase 3A (PRISM Climate Data Comprehensive Analysis): COMPLETE*
