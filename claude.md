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
- All data files are from public CAL FIRE and MTBS sources

**Large Files Excluded** (via `.gitignore`):
- GeoPackage data files (133 MB+) - download from CAL FIRE FRAP
- MTBS shapefile data - download from https://www.mtbs.gov/
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

### Phase 2: Grid Creation (NEXT)
- Create 800m × 800m grid covering California
- Rasterize fire perimeters to binary burned/not-burned grid cells
- Temporal aggregation (monthly, seasonal, annual)

### Phase 3: Data Integration
Integrate additional datasets:
- **Climate/Weather**: PRISM data (temperature, precipitation, VPD)
- **Topography**: Elevation, slope, aspect (DEM)
- **Vegetation/Fuel**: Cover type, density, fuel models
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

### Tertiary Dataset: California State Boundary
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
│   └── Fireignition_points/
│       └── mtbs_fod_pts_data/
│           └── mtbs_FODpoints_DD.shp   # + .dbf, .shx, .prj, etc.
├── src/
│   └── utils/
│       ├── __init__.py
│       ├── constants.py               # Paths, CRS, thresholds (CAL FIRE + MTBS)
│       ├── domain_mappings.py         # CAUSE, AGENCY, C_METHOD lookups
│       ├── mtbs_domain_mappings.py    # MTBS incident/assessment/severity mappings
│       ├── data_loader.py             # CAL FIRE GeoPackage loading utilities
│       ├── mtbs_data_loader.py        # MTBS shapefile loading & processing
│       └── plotting.py                # Visualization helpers (+ severity colors)
├── notebooks/
│   ├── CALFIRE_Comprehensive_Analysis_v2.ipynb           # CAL FIRE EDA
│   ├── CALFIRE_Comprehensive_Analysis_v2_executed.ipynb  # With outputs
│   ├── MTBS_FOD_Comprehensive_Analysis.ipynb             # MTBS EDA
│   └── MTBS_FOD_Comprehensive_Analysis_executed.ipynb    # With outputs
├── outputs/
│   ├── figures/
│   │   ├── comprehensive/             # 19 CAL FIRE figures (300 DPI)
│   │   └── mtbs/                      # 16 MTBS figures (300 DPI)
│   ├── interactive/                   # Folium maps
│   │   ├── mega_fires_interactive.html
│   │   └── mtbs_fires_interactive.html
│   ├── CALFIRE_Comprehensive_Analysis_v2.pdf   # PDF export
│   └── CALFIRE_Comprehensive_Analysis_v2.html  # HTML export
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
├── CALFIRE_Comprehensive_Analysis_v2.pdf   # 3.4 MB - printable
├── CALFIRE_Comprehensive_Analysis_v2.html  # 40 MB - web viewing
├── figures/comprehensive/                   # 19 PNG figures (300 DPI)
└── interactive/
    └── mega_fires_interactive.html          # Folium map
```

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
- `jupyterlab>=4.0` - Notebook environment

### Run Notebook
```bash
conda activate wildfire
jupyter lab notebooks/CALFIRE_Comprehensive_Analysis_v2.ipynb
```

### Export to PDF
```bash
# Execute notebook first
jupyter nbconvert --execute --to notebook notebooks/CALFIRE_Comprehensive_Analysis_v2.ipynb

# Convert to HTML
jupyter nbconvert --to html --no-input notebooks/CALFIRE_Comprehensive_Analysis_v2_executed.ipynb

# Use Chrome for PDF (if available)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --print-to-pdf="output.pdf" file://path/to/html
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

**To Add in Phase 3:**
- Climate: Temperature, precipitation, VPD, drought indices
- Topography: Elevation, slope, aspect
- Fuel: Vegetation type, density, fuel moisture
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
5. Create temporal aggregations (monthly, seasonal, annual)

### Phase 3: Data Integration
1. Merge MTBS severity data with CAL FIRE perimeters for comprehensive fire characterization
2. Acquire PRISM climate data
3. Acquire DEM for topography
4. Acquire fuel/vegetation data
5. Align all datasets to common grid

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

---

## Contact and Collaboration

- **Project Lead**: Olivier (Tam Air Club)
- **Data Sources**: CAL FIRE FRAP, USGS/USDA Forest Service MTBS
- **Data Portals**: https://frap.fire.ca.gov/ | https://www.mtbs.gov/

---

*Last Updated: February 2026*
*Phase 1 (EDA) Status: COMPLETE*
*Phase 1.5 (CAL FIRE Comprehensive Notebook v2): COMPLETE*
*Phase 1.75 (MTBS Comprehensive Analysis): COMPLETE*
