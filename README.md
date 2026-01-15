# California Wildfire Prediction Model

A pixel-wise wildfire prediction system for California that predicts fire risk based on recent conditions, developed in collaboration with **Tam Air Club**, **UCSF**, **UCI**, and **CAL FIRE**.

## Project Overview

**Goal**: Build a machine learning model to predict seasonal wildfire risk at 800m × 800m resolution across California.

**Target Output**: Voxel-based fire risk predictions that vary with date and environmental conditions.

## Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Exploratory Data Analysis | Complete |
| Phase 1.5 | Comprehensive Analysis Notebook | Complete |
| Phase 2 | Grid Creation (800m × 800m) | Next |
| Phase 3 | Data Integration (Climate, Topography, Fuel) | Planned |
| Phase 4 | ML Model Development (CNN/LSTM) | Planned |

## Key Findings (1993-Present)

| Metric | Value |
|--------|-------|
| Worst fire year | 2020 (4.2 million acres) |
| High-risk season | June-September (84% of burned area) |
| Fire concentration | Top 1% of fires cause ~58% of damage |
| Data completeness | >97% for key fields since 1993 |
| Total records (high-quality) | ~10,000 fires |

## Repository Structure

```
wildfire_prediction_model_california/
├── src/
│   └── utils/
│       ├── constants.py          # Paths, CRS, thresholds
│       ├── domain_mappings.py    # CAUSE, AGENCY, C_METHOD lookups
│       ├── data_loader.py        # GeoPackage loading utilities
│       └── plotting.py           # Visualization helpers
├── notebooks/
│   └── CALFIRE_Comprehensive_Analysis_v2.ipynb  # Main analysis
├── outputs/
│   ├── figures/comprehensive/    # 19 high-res figures (300 DPI)
│   └── CALFIRE_Comprehensive_Analysis_v2.pdf
├── Datasets/                     # Data files (not in repo - see below)
├── environment.yml               # Conda environment
├── CLAUDE.md                     # Detailed project documentation
└── README.md                     # This file
```

## Data Sources

### Primary Dataset: CAL FIRE Historical Fire Perimeters
- **Source**: [CAL FIRE FRAP](https://frap.fire.ca.gov/)
- **Format**: GeoPackage (133 MB)
- **Coverage**: 22,000+ fire perimeters (1878-2025)
- **CRS**: EPSG:3310 (California Albers projection)

**Note**: Large data files are not included in this repository due to size limits. Download from CAL FIRE FRAP or contact the maintainers.

### Data Quality
- **Pre-1993**: Variable quality, hand-drawn perimeters
- **1993+**: High-quality GPS-based collection (recommended for ML training)

## Installation

### Prerequisites
- [Conda](https://docs.conda.io/en/latest/miniconda.html) or [Mamba](https://mamba.readthedocs.io/)
- Python 3.11+

### Setup

```bash
# Clone the repository
git clone https://github.com/justinmerlin2009/wildfire_prediction_model_california.git
cd wildfire_prediction_model_california

# Create conda environment
conda env create -f environment.yml
conda activate wildfire

# Launch Jupyter Lab
jupyter lab notebooks/CALFIRE_Comprehensive_Analysis_v2.ipynb
```

### Data Setup

1. Download fire perimeter data from [CAL FIRE FRAP](https://frap.fire.ca.gov/frap-projects/fire-perimeters/)
2. Place in `Datasets/Fireperimeters/`
3. Ensure file is named `California_Fire_Perimeters_All_Reprojected.gpkg`
4. Verify CRS is EPSG:3310 (reproject if necessary)

## Analysis Outputs

### Comprehensive Notebook (62 cells, 9 sections)

| Part | Content |
|------|---------|
| 1 | Introduction & Context |
| 2 | Data Loading & Quality Assessment |
| 3 | Temporal Analysis (1900-present) |
| 4 | Seasonal Patterns (Fire Clock) |
| 5 | Fire Size Analysis (Pareto) |
| 6 | Spatial Analysis (Maps) |
| 7 | Fire Causes Investigation |
| 8 | Agency & Unit Analysis |
| 9 | Executive Summary & ML Readiness |

### Generated Figures (19 publication-ready visualizations)

- Data completeness comparison
- Collection method evolution
- 125-year temporal timeline
- Fire clock (polar visualization)
- Seasonal heatmaps
- Pareto analysis
- Cumulative fire risk maps
- Agency and unit breakdowns

## Key Constants

```python
HIGH_QUALITY_CUTOFF = 1993      # Use data from 1993+ for ML
MEGA_FIRE_THRESHOLD = 100000    # Acres for mega-fire classification
GRID_RESOLUTION_M = 800         # Target grid cell size
CRS_ALBERS = "EPSG:3310"        # California Albers (metric)
```

## ML Model Recommendations

### Architecture
- **Grid Resolution**: 800m × 800m
- **Target Variable**: Binary (burned/not-burned)
- **Architecture**: CNN + LSTM for spatiotemporal patterns
- **Validation**: Temporal split (Train: 1993-2019, Test: 2020+)

### Known Challenges
1. **Class Imbalance**: ~99% of grid cells never burn
2. **Non-Stationarity**: Climate change affects patterns
3. **Rare Events**: Mega-fires cause most damage but are rare

## Dependencies

Key packages (see `environment.yml` for full list):
- `geopandas >= 0.14`
- `rasterio >= 1.3`
- `folium >= 0.14`
- `matplotlib >= 3.7`
- `scikit-learn >= 1.3`

## Collaboration

- **Tam Air Club** (Tamalpais High School)
- **UCSF** - Research collaboration
- **UCI** - Academic partnership
- **CAL FIRE** - California Department of Forestry and Fire Protection

## License

This project is for educational and research purposes in collaboration with CAL FIRE.

## Contact

For questions about the data or collaboration opportunities, contact through the project repository.

---

*Phase 1 (EDA): Complete | Phase 1.5 (Comprehensive Notebook): Complete | Phase 2 (Grid Creation): In Progress*
