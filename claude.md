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
- All data files are from public CAL FIRE sources

**Large Files Excluded** (via `.gitignore`):
- GeoPackage data files (133 MB+) - download from CAL FIRE FRAP
- Executed notebooks (40 MB) - regenerate locally
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

### Secondary Dataset: California State Boundary
- **File**: `/Users/olivier/Documents/MyQGIS/WildfireAnalysis/DeepLearning/INPUTS_EPSG3310/California_State_Boundary_Reprojected.gpkg`
- **CRS**: EPSG:3310 (California Albers)
- **Use**: Geographic context for maps

---

## Code Architecture

### Directory Structure
```
wildfire_prediction_model_california/
├── Datasets/
│   └── Fireperimeters/
│       └── California_Fire_Perimeters_All_Reprojected.gpkg
├── src/
│   └── utils/
│       ├── __init__.py
│       ├── constants.py               # Paths, CRS, thresholds
│       ├── domain_mappings.py         # CAUSE, AGENCY, C_METHOD lookups
│       ├── data_loader.py             # GeoPackage loading utilities
│       └── plotting.py                # Visualization helpers
├── notebooks/
│   ├── CALFIRE_Comprehensive_Analysis_v2.ipynb           # Main notebook
│   └── CALFIRE_Comprehensive_Analysis_v2_executed.ipynb  # With outputs
├── outputs/
│   ├── figures/
│   │   └── comprehensive/             # 19 high-res figures (300 DPI)
│   ├── interactive/                   # Folium maps
│   ├── CALFIRE_Comprehensive_Analysis_v2.pdf   # PDF export
│   └── CALFIRE_Comprehensive_Analysis_v2.html  # HTML export
├── environment.yml                    # Conda environment
└── CLAUDE.md                          # This file
```

### Key Constants (src/utils/constants.py)
```python
FIRE_PERIMETERS_PATH = DATA_DIR / "Fireperimeters" / "California_Fire_Perimeters_All_Reprojected.gpkg"
HIGH_QUALITY_CUTOFF = 1993      # Year threshold for high-quality data
MEGA_FIRE_THRESHOLD = 100000    # Acres threshold for mega-fires
GRID_RESOLUTION_M = 800         # Target grid cell size in meters
CRS_ALBERS = "EPSG:3310"        # California Albers (metric)
CRS_WGS84 = "EPSG:4326"         # For web maps (Folium)
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

---

## Comprehensive Notebook v2 Structure

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
**From Fire Perimeter Data:**
- Historical burn frequency (cumulative risk map)
- Time since last fire at location
- Fire season (High Risk / Transition / Low Risk)
- Month and day of year
- Agency jurisdiction
- Unit ID (administrative region)

**To Add in Phase 3:**
- Climate: Temperature, precipitation, VPD, drought indices
- Topography: Elevation, slope, aspect
- Fuel: Vegetation type, density, fuel moisture
- Human: Roads, population density

### Model Architecture
| Component | Recommendation |
|-----------|---------------|
| Grid Resolution | 800m × 800m |
| Target Variable | Binary (burned/not-burned) |
| Temporal Unit | Monthly or seasonal |
| Architecture | CNN + LSTM |
| Loss Function | Focal Loss (for class imbalance) |
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
4. Create temporal aggregations (monthly, seasonal, annual)

### Phase 3: Data Integration
1. Acquire PRISM climate data
2. Acquire DEM for topography
3. Acquire fuel/vegetation data
4. Align all datasets to common grid

### Phase 4: ML Development
1. Design CNN/LSTM architecture
2. Implement data pipeline
3. Train initial models
4. Evaluate and iterate

---

## Reference Documents

Located in `Datasets/`:
- `Data_Dictionary_California_Fire_Perimeters.pdf` - Field definitions
- `CAL_Fire_Data_Analysis_Summary.pdf` - Previous analysis
- `CA_Fire_Proposal__Tam_Air_Club__UCI__UCSF__CAL_FIRE_.pdf` - Collaboration proposal

---

## Contact and Collaboration

- **Project Lead**: Olivier (Tam Air Club)
- **Data Source**: CAL FIRE FRAP (Fire and Resource Assessment Program)
- **Data Portal**: https://frap.fire.ca.gov/

---

*Last Updated: January 2026*
*Phase 1 (EDA) Status: COMPLETE*
*Phase 1.5 (Comprehensive Notebook v2): COMPLETE*
