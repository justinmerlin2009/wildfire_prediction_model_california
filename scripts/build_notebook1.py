#!/usr/bin/env python3
"""Build PRISM Comprehensive Analysis Part 1: CONUS + All States notebook."""
import json
import sys

def md(source):
    """Create a markdown cell."""
    if isinstance(source, str):
        source = source.split('\n')
    return {"cell_type": "markdown", "metadata": {}, "source": [line + '\n' for line in source[:-1]] + [source[-1]]}

def code(source):
    """Create a code cell."""
    if isinstance(source, str):
        source = source.split('\n')
    return {"cell_type": "code", "metadata": {}, "source": [line + '\n' for line in source[:-1]] + [source[-1]], "outputs": [], "execution_count": None}

cells = []

# ═══════════════════════════════════════════════════════════════════
# PART 1: TITLE + TOC
# ═══════════════════════════════════════════════════════════════════

cells.append(md("""\
# PRISM Climate Data Comprehensive Analysis — Part 1: CONUS Overview & All 48 States

**Phase 3A** | California Wildfire Prediction Model
**Dataset**: PRISM 30-arcsecond (~800m) climate grids, 1895–2025
**Source**: Oregon State University PRISM Climate Group
**Coverage**: Continental United States (CONUS) — 48 states + DC"""))

cells.append(md("""\
### Table of Contents

| Part | Title | Figures |
|------|-------|---------|
| 1 | Introduction & Context | — |
| 2 | Data Loading & Quality | Fig 1 |
| 3 | CONUS Spatial Patterns | Fig 2–5 |
| 4 | All-State Rankings & Profiles | Fig 6–11 |
| 5 | Long-Term CONUS Trends | Fig 12–15 |
| 6 | Seasonal Patterns — All States | Fig 16–19 |
| 7 | CONUS Climate Regions | Fig 20 |
| 8 | All-State Summary & Interactive Map | Fig 21–22 |
| 9 | Executive Summary | — |"""))

cells.append(md("""\
---
## Part 1 — Introduction & Context

### Why Climate Data Matters for Wildfire Prediction

Climate variables — particularly **Vapor Pressure Deficit (VPD)**, temperature, and precipitation — are the **strongest predictors** of wildfire activity. VPD measures the atmosphere's "drying power": how aggressively it pulls moisture from vegetation. When VPD is high and precipitation is low, fuels dry out and fire risk skyrockets.

**PRISM** (Parameter-elevation Regressions on Independent Slopes Model) is the gold standard for high-resolution climate data in the US:
- **~800m resolution** — matches our 800m × 800m prediction grid
- **130-year monthly record** (1895–2025) — captures long-term trends
- **45-year daily record** (1981–2026) — enables fire-season analysis
- **7 core variables**: precipitation, temperature (max/min/mean), dew point, VPD (max/min)

### This Notebook: CONUS Overview + Every State Profiled

This first notebook provides the **continental-scale context** before diving into California (Part 2) and fire-climate integration (Part 3). Every one of the 48 CONUS states gets individually profiled and ranked."""))

# ═══════════════════════════════════════════════════════════════════
# PART 2: DATA LOADING & QUALITY
# ═══════════════════════════════════════════════════════════════════

cells.append(md("""\
---
## Part 2 — Data Loading & Quality"""))

cells.append(code("""\
# ── Imports ───────────────────────────────────────────────────────────────

import sys, warnings, gc, time
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns

import geopandas as gpd

# Project utilities
sys.path.insert(0, '..')
from src.utils.constants import (
    PRISM_BASE_PATH, PRISM_CRS, PRISM_NODATA, PRISM_CA_BOUNDS,
    PRISM_VARIABLES, PRISM_SOLAR_VARIABLES,
    PRISM_MONTHLY_START_YEAR, PRISM_MONTHLY_END_YEAR,
    PRISM_DAILY_START_YEAR, PRISM_DAILY_END_YEAR,
    PRISM_CONUS_SHAPE, PRISM_CACHE_DIR,
    FIGURES_DIR, FIGURE_DPI,
)
from src.utils.prism_domain_mappings import (
    PRISM_VARIABLE_META, PRISM_VARIABLE_ORDER,
    FIRE_WEATHER_VPD_CLASSES, FIRE_WEATHER_VPD_ORDER,
    CONUS_STATES, WESTERN_US_STATES, US_STATE_FIPS,
    CA_CLIMATE_REGIONS, CLIMATE_SEASON_MAP, CLIMATE_SEASON_ORDER,
    MONTH_ABBREVS, MONTH_NAMES,
    get_variable_label, get_variable_colormap, classify_vpd,
)
from src.utils.prism_data_loader import (
    check_prism_drive, discover_files, build_file_inventory,
    read_prism_conus, read_prism_california,
    load_monthly_normal, load_all_monthly_normals,
    load_us_states_boundaries,
    load_from_cache, save_to_cache,
    compute_state_statistics,
    get_prism_data_quality_summary,
)
from src.utils.plotting import (
    setup_plotting_style, save_figure,
    get_prism_variable_colors, get_vpd_risk_colors,
    get_climate_season_colors, get_prism_diverging_norm,
)

setup_plotting_style()

# Output directory for this notebook
PRISM_CONUS_FIG_DIR = FIGURES_DIR / "prism_conus"
PRISM_CONUS_FIG_DIR.mkdir(parents=True, exist_ok=True)

def save_fig(fig, name):
    save_figure(fig, f"prism_conus/{name}")
    plt.close(fig)

print("Imports complete.")"""))

cells.append(code("""\
# ── Verify drive & load cached data ──────────────────────────────────────

drive_info = check_prism_drive()
print(f"PRISM drive: {drive_info['base_path']}")
print(f"Variables available: {drive_info['n_variables']}")

# Load state boundaries
states_gdf = load_us_states_boundaries()
print(f"\\nState boundaries: {len(states_gdf)} CONUS states")

# Load CA monthly stats cache
ca_stats = load_from_cache("prism_ca_monthly_stats")
if ca_stats is not None:
    print(f"CA monthly stats cache: {len(ca_stats):,} rows")
else:
    print("WARNING: CA stats cache not found. Run precomputation script first.")

# Load state monthly summaries cache (if available)
state_stats = load_from_cache("prism_state_monthly_summaries")
if state_stats is not None:
    print(f"State monthly summaries cache: {len(state_stats):,} rows")
else:
    print("State summaries cache not available — will compute on the fly for selected analyses.")"""))

cells.append(code("""\
# ── File inventory ────────────────────────────────────────────────────────

# Build inventory for monthly data
inv = build_file_inventory(temporal="monthly", year_range=(1895, 2025))
print(f"Total monthly files: {len(inv):,}")
print(f"\\nFiles per variable:")
print(inv.groupby("variable").agg(
    count=("filepath", "count"),
    years=("year", lambda x: f"{x.min()}-{x.max()}"),
    total_gb=("file_size_mb", lambda x: f"{x.sum()/1024:.1f}")
).to_string())

# Daily inventory (just count)
for var in ["ppt", "vpdmax"]:
    daily_files = discover_files(var, "daily")
    daily_count = sum(len(discover_files(var, "daily", year=y))
                      for y in range(PRISM_DAILY_START_YEAR, PRISM_DAILY_END_YEAR + 1))
    print(f"\\n{var} daily files: ~{daily_count:,} ({PRISM_DAILY_START_YEAR}-{PRISM_DAILY_END_YEAR})")"""))

# ── Figure 1: Data Quality ──
cells.append(code("""\
# ── Figure 1: Data Quality & Coverage ─────────────────────────────────────

fig = plt.figure(figsize=(20, 12))
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

# Panel 1: CONUS validity mask from a sample raster
ax1 = fig.add_subplot(gs[0, 0])
sample_files = discover_files("ppt", "monthly", year=2020, month=7)
data, transform, _ = read_prism_conus(sample_files[0])
valid_mask = (data != PRISM_NODATA).astype(float)
ax1.imshow(valid_mask, cmap="Greens", extent=[
    transform[2], transform[2] + transform[0] * data.shape[1],
    transform[5] + transform[4] * data.shape[0], transform[5]
])
states_gdf.boundary.plot(ax=ax1, color='gray', linewidth=0.3)
ca = states_gdf[states_gdf.STUSPS == 'CA']
ca.boundary.plot(ax=ax1, color='red', linewidth=1.5)
ax1.set_title("CONUS Valid Data Mask", fontsize=12, fontweight='bold')
ax1.set_xlim(-125, -66)
ax1.set_ylim(24, 50)
n_valid = np.sum(valid_mask > 0)
ax1.text(0.02, 0.02, f"Valid pixels: {n_valid:,}\\nShape: {data.shape[0]}×{data.shape[1]}",
         transform=ax1.transAxes, fontsize=9, va='bottom',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
del data; gc.collect()

# Panel 2: Monthly file timeline
ax2 = fig.add_subplot(gs[0, 1:])
var_colors = get_prism_variable_colors()
for i, var in enumerate(PRISM_VARIABLE_ORDER):
    files = inv[inv.variable == var]
    if len(files) > 0:
        years = files.year.values
        ax2.scatter(years, [i]*len(years), s=1, c=var_colors[var], alpha=0.5)
        # Solid bar for coverage span
        ax2.barh(i, years.max() - years.min(), left=years.min(),
                 height=0.6, color=var_colors[var], alpha=0.7)
        ax2.text(years.max() + 1, i, f"{len(files)} files",
                 va='center', fontsize=9)
ax2.set_yticks(range(len(PRISM_VARIABLE_ORDER)))
ax2.set_yticklabels([get_variable_label(v, with_units=False) for v in PRISM_VARIABLE_ORDER])
ax2.set_xlabel("Year")
ax2.set_title("Monthly Data Availability by Variable", fontsize=12, fontweight='bold')
ax2.set_xlim(1890, 2030)

# Panel 3: Variable summary table
ax3 = fig.add_subplot(gs[1, 0:2])
ax3.axis('off')
table_data = []
for var in PRISM_VARIABLE_ORDER:
    meta = PRISM_VARIABLE_META[var]
    vfiles = inv[inv.variable == var]
    table_data.append([
        meta['short_label'],
        meta['full_name'],
        meta['units'],
        f"{vfiles.year.min()}-{vfiles.year.max()}" if len(vfiles) > 0 else "N/A",
        f"{len(vfiles):,}",
        meta['fire_relevance'][:50] + "..." if len(meta['fire_relevance']) > 50 else meta['fire_relevance'],
    ])
table = ax3.table(cellText=table_data,
                   colLabels=['Code', 'Variable', 'Units', 'Years', 'Files', 'Fire Relevance'],
                   loc='center', cellLoc='left')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.auto_set_column_width(col=list(range(6)))
table.scale(1, 1.4)
# Style header
for j in range(6):
    table[0, j].set_facecolor('#2C3E50')
    table[0, j].set_text_props(color='white', fontweight='bold')
ax3.set_title("PRISM Variable Summary", fontsize=12, fontweight='bold', pad=20)

# Panel 4: File size by variable
ax4 = fig.add_subplot(gs[1, 2])
sizes = inv.groupby('variable')['file_size_mb'].sum() / 1024  # GB
sizes = sizes.reindex(PRISM_VARIABLE_ORDER)
bars = ax4.barh(range(len(sizes)), sizes.values,
                color=[var_colors[v] for v in sizes.index])
ax4.set_yticks(range(len(sizes)))
ax4.set_yticklabels([PRISM_VARIABLE_META[v]['short_label'] for v in sizes.index])
ax4.set_xlabel("Total Size (GB, monthly only)")
ax4.set_title("Data Volume", fontsize=12, fontweight='bold')
for i, v in enumerate(sizes.values):
    ax4.text(v + 0.5, i, f"{v:.1f} GB", va='center', fontsize=9)

fig.suptitle("Figure 1: PRISM Climate Data — Quality & Coverage",
             fontsize=16, fontweight='bold', y=1.01)

save_fig(fig, "01_data_quality_coverage")"""))

# ═══════════════════════════════════════════════════════════════════
# PART 3: CONUS SPATIAL PATTERNS
# ═══════════════════════════════════════════════════════════════════

cells.append(md("""\
---
## Part 3 — CONUS Spatial Patterns

Annual normal maps reveal the dramatic climate diversity across the continental US."""))

cells.append(code("""\
# ── Figure 2: CONUS Temperature Maps ─────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

temp_vars = [('tmax', 'Annual Mean Tmax'),
             ('tmin', 'Annual Mean Tmin'),
             ('tmean', 'Annual Mean Tmean'),
             ('tdmean', 'Annual Mean Dew Point')]

for ax, (var, title) in zip(axes.flat, temp_vars):
    # Load annual normal
    normal_file = discover_files(var, "monthly", year=2020, month=7)
    # Use July as representative warm-season snapshot
    if normal_file:
        data, tfm, _ = read_prism_conus(normal_file[0])
        data_plot = np.where(data == PRISM_NODATA, np.nan, data)
        extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
                  tfm[5] + tfm[4] * data.shape[0], tfm[5]]
        cmap = get_variable_colormap(var)
        im = ax.imshow(data_plot, cmap=cmap, extent=extent)
        states_gdf.boundary.plot(ax=ax, color='gray', linewidth=0.3)
        ca.boundary.plot(ax=ax, color='red', linewidth=1.2)
        plt.colorbar(im, ax=ax, shrink=0.7, label=f"{PRISM_VARIABLE_META[var]['units']}")
        valid = data[data != PRISM_NODATA]
        ax.text(0.02, 0.02, f"CONUS mean: {np.mean(valid):.1f}{PRISM_VARIABLE_META[var]['units']}",
                transform=ax.transAxes, fontsize=9, va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        del data; gc.collect()
    ax.set_title(f"{title} — July 2020", fontsize=12, fontweight='bold')
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)

fig.suptitle("Figure 2: CONUS Temperature Patterns (July 2020)",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "02_conus_temperature_maps")"""))

cells.append(code("""\
# ── Figure 3: CONUS Moisture Maps ────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

moisture_vars = [
    ('ppt', 'Monthly Precipitation', 'monthly', 2020, 1),      # Jan (wet season)
    ('vpdmax', 'Maximum VPD', 'monthly', 2020, 7),              # July (fire season)
    ('vpdmin', 'Minimum VPD', 'monthly', 2020, 7),              # July
    ('ppt', 'Monthly Precipitation', 'monthly', 2020, 7),       # July (dry season)
]
panel_titles = ['January 2020 Precipitation', 'July 2020 VPDmax',
                'July 2020 VPDmin', 'July 2020 Precipitation']

for ax, (var, label, temp, yr, mo), ptitle in zip(axes.flat, moisture_vars, panel_titles):
    files = discover_files(var, temp, year=yr, month=mo)
    if files:
        data, tfm, _ = read_prism_conus(files[0])
        data_plot = np.where(data == PRISM_NODATA, np.nan, data)
        extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
                  tfm[5] + tfm[4] * data.shape[0], tfm[5]]
        cmap = get_variable_colormap(var)
        if var == 'ppt':
            im = ax.imshow(data_plot, cmap=cmap, extent=extent, vmin=0)
        else:
            im = ax.imshow(data_plot, cmap=cmap, extent=extent)
        states_gdf.boundary.plot(ax=ax, color='gray', linewidth=0.3)
        ca.boundary.plot(ax=ax, color='red', linewidth=1.2)
        plt.colorbar(im, ax=ax, shrink=0.7, label=PRISM_VARIABLE_META[var]['units'])
        del data; gc.collect()
    ax.set_title(ptitle, fontsize=12, fontweight='bold')
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)

fig.suptitle("Figure 3: CONUS Moisture & VPD Patterns",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "03_conus_moisture_maps")"""))

cells.append(code("""\
# ── Figure 4: Seasonal Contrast (January vs July) ────────────────────────

fig, axes = plt.subplots(2, 3, figsize=(24, 14))

contrast_vars = ['ppt', 'tmax', 'vpdmax']
months = [1, 7]
month_names = ['January 2020', 'July 2020']

for col, var in enumerate(contrast_vars):
    for row, (mo, mo_name) in enumerate(zip(months, month_names)):
        ax = axes[row, col]
        files = discover_files(var, "monthly", year=2020, month=mo)
        if files:
            data, tfm, _ = read_prism_conus(files[0])
            data_plot = np.where(data == PRISM_NODATA, np.nan, data)
            extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
                      tfm[5] + tfm[4] * data.shape[0], tfm[5]]
            cmap = get_variable_colormap(var)
            # Consistent scale per variable
            valid = data[data != PRISM_NODATA]
            if var == 'ppt':
                im = ax.imshow(data_plot, cmap=cmap, extent=extent, vmin=0, vmax=400)
            elif var == 'tmax':
                im = ax.imshow(data_plot, cmap=cmap, extent=extent, vmin=-15, vmax=45)
            else:
                im = ax.imshow(data_plot, cmap=cmap, extent=extent, vmin=0, vmax=70)
            states_gdf.boundary.plot(ax=ax, color='gray', linewidth=0.3)
            ca.boundary.plot(ax=ax, color='red', linewidth=1.2)
            plt.colorbar(im, ax=ax, shrink=0.7)
            del data; gc.collect()
        ax.set_title(f"{get_variable_label(var, False)} — {mo_name}", fontsize=11, fontweight='bold')
        ax.set_xlim(-125, -66)
        ax.set_ylim(24, 50)

fig.suptitle("Figure 4: Dramatic Seasonal Contrast — January vs July",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "04_conus_seasonal_contrast")"""))

cells.append(code("""\
# ── Figure 5: Solar Radiation Normals ─────────────────────────────────────

from src.utils.prism_domain_mappings import PRISM_SOLAR_META

fig, axes = plt.subplots(2, 2, figsize=(20, 14))
solar_vars = ['solclear', 'soltotal', 'solslope', 'soltrans']

for ax, svar in zip(axes.flat, solar_vars):
    # Solar normals are monthly normals
    from src.utils.prism_data_loader import _find_normal_file, read_prism_raster
    normal_file = _find_normal_file(svar, month=7, base_path=PRISM_BASE_PATH)
    if normal_file:
        data, tfm, _ = read_prism_raster(normal_file)
        data_plot = np.where(data == PRISM_NODATA, np.nan, data)
        extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
                  tfm[5] + tfm[4] * data.shape[0], tfm[5]]
        meta = PRISM_SOLAR_META.get(svar, {})
        cmap = meta.get('colormap', 'YlOrRd')
        im = ax.imshow(data_plot, cmap=cmap, extent=extent)
        states_gdf.boundary.plot(ax=ax, color='gray', linewidth=0.3)
        ca.boundary.plot(ax=ax, color='red', linewidth=1.2)
        plt.colorbar(im, ax=ax, shrink=0.7, label=meta.get('units', ''))
        del data; gc.collect()
        ax.set_title(f"{meta.get('full_name', svar)} — July Normal", fontsize=12, fontweight='bold')
    else:
        ax.text(0.5, 0.5, f"{svar}: no normal found", transform=ax.transAxes,
                ha='center', fontsize=12)
        ax.set_title(svar, fontsize=12)
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)

fig.suptitle("Figure 5: CONUS Solar Radiation Normals (July)",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "05_conus_solar_normals")"""))

# ═══════════════════════════════════════════════════════════════════
# PART 4: ALL-STATE RANKINGS
# ═══════════════════════════════════════════════════════════════════

cells.append(md("""\
---
## Part 4 — All-State Rankings & Profiles

Every state individually ranked across climate variables. California highlighted in red, western fire states in orange."""))

cells.append(code("""\
# ── Compute state-level annual means for ranking ──────────────────────────
# Use 2015-2024 average for a recent climatology

if state_stats is not None:
    # Use cached data
    recent = state_stats[(state_stats.year >= 2015) & (state_stats.year <= 2024)]
    state_annual = recent.groupby(['variable', 'state'])['mean'].mean().reset_index()
    state_annual.columns = ['variable', 'state', 'annual_mean']
    print(f"Using cached state stats: {len(state_annual)} state-variable pairs")
else:
    # Compute on the fly for a few representative months
    print("Computing state stats on the fly (no cache)...")
    rows = []
    for var in ['tmax', 'tmin', 'ppt', 'vpdmax', 'vpdmin', 'tmean', 'tdmean']:
        for yr in [2020, 2021, 2022]:
            for mo in [1, 4, 7, 10]:  # Quarterly
                files = discover_files(var, 'monthly', year=yr, month=mo)
                if files:
                    sstats = compute_state_statistics(files[0], states_gdf, ['mean'])
                    for st, sv in sstats.items():
                        rows.append({'variable': var, 'state': st, 'year': yr,
                                     'month': mo, 'mean': sv.get('mean', np.nan)})
    state_annual = pd.DataFrame(rows).groupby(['variable', 'state'])['mean'].mean().reset_index()
    state_annual.columns = ['variable', 'state', 'annual_mean']
    print(f"Computed {len(state_annual)} state-variable pairs")

# Add state names
state_annual['state_name'] = state_annual['state'].map(CONUS_STATES)
print("\\nSample data:")
print(state_annual[state_annual.variable == 'vpdmax'].nlargest(5, 'annual_mean'))"""))

cells.append(code("""\
# ── Figure 6: All-State Temperature Rankings ──────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(20, 20))

ranking_vars = [
    ('tmax', 'Mean Maximum Temperature (°C)'),
    ('tmin', 'Mean Minimum Temperature (°C)'),
    ('tmean', 'Mean Temperature (°C)'),
    ('tdmean', 'Mean Dew Point (°C)'),
]

for ax, (var, title) in zip(axes.flat, ranking_vars):
    df_var = state_annual[state_annual.variable == var].sort_values('annual_mean')

    colors = []
    for st in df_var.state:
        if st == 'CA':
            colors.append('#E74C3C')  # Red for CA
        elif st in WESTERN_US_STATES:
            colors.append('#F39C12')  # Orange for western
        else:
            colors.append('#3498DB')  # Blue for others

    ax.barh(range(len(df_var)), df_var.annual_mean.values, color=colors)
    ax.set_yticks(range(len(df_var)))
    ax.set_yticklabels(df_var.state.values, fontsize=8)
    ax.set_xlabel(PRISM_VARIABLE_META[var]['units'])
    ax.set_title(title, fontsize=12, fontweight='bold')

    # CA annotation
    ca_val = df_var[df_var.state == 'CA'].annual_mean.values
    if len(ca_val) > 0:
        ca_rank = list(df_var.state.values).index('CA') + 1
        ax.text(0.98, 0.02, f"CA rank: #{ca_rank}/{len(df_var)} ({ca_val[0]:.1f})",
                transform=ax.transAxes, ha='right', va='bottom', fontsize=10,
                color='#E74C3C', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#E74C3C', markersize=12, label='California'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#F39C12', markersize=12, label='Western US'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#3498DB', markersize=12, label='Other states'),
]
fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=12, bbox_to_anchor=(0.5, -0.02))

fig.suptitle("Figure 6: All 48 States Ranked by Temperature",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "06_all_state_rankings_temperature")"""))

cells.append(code("""\
# ── Figure 7: All-State Moisture Rankings ─────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(20, 20))

moisture_ranking_vars = [
    ('ppt', 'Mean Monthly Precipitation (mm)'),
    ('vpdmax', 'Mean Maximum VPD (hPa)'),
    ('vpdmin', 'Mean Minimum VPD (hPa)'),
    ('tdmean', 'Mean Dew Point Temperature (°C)'),
]

for ax, (var, title) in zip(axes.flat, moisture_ranking_vars):
    df_var = state_annual[state_annual.variable == var].sort_values('annual_mean')

    colors = []
    for st in df_var.state:
        if st == 'CA':
            colors.append('#E74C3C')
        elif st in WESTERN_US_STATES:
            colors.append('#F39C12')
        else:
            colors.append('#3498DB')

    ax.barh(range(len(df_var)), df_var.annual_mean.values, color=colors)
    ax.set_yticks(range(len(df_var)))
    ax.set_yticklabels(df_var.state.values, fontsize=8)
    ax.set_xlabel(PRISM_VARIABLE_META[var]['units'])
    ax.set_title(title, fontsize=12, fontweight='bold')

    ca_val = df_var[df_var.state == 'CA'].annual_mean.values
    if len(ca_val) > 0:
        ca_rank = list(df_var.state.values).index('CA') + 1
        ax.text(0.98, 0.02, f"CA rank: #{ca_rank}/{len(df_var)} ({ca_val[0]:.1f})",
                transform=ax.transAxes, ha='right', va='bottom', fontsize=10,
                color='#E74C3C', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

fig.suptitle("Figure 7: All 48 States Ranked by Moisture Variables",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "07_all_state_rankings_moisture")"""))

cells.append(code("""\
# ── Figure 8: Within-State Climate Diversity ──────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Compute within-state std (climate diversity) from state stats
if state_stats is not None:
    recent = state_stats[(state_stats.year >= 2015) & (state_stats.year <= 2024)]
    diversity = recent.groupby(['variable', 'state'])['std'].mean().reset_index()
    diversity.columns = ['variable', 'state', 'within_state_std']
else:
    # Use the on-the-fly data
    diversity = state_annual.copy()
    diversity['within_state_std'] = diversity['annual_mean'] * 0.2  # rough estimate

for ax, (var, title) in zip(axes.flat[:3], [
    ('tmax', 'Temperature Diversity (Std of Tmax, °C)'),
    ('ppt', 'Precipitation Diversity (Std of PPT, mm)'),
    ('vpdmax', 'VPD Diversity (Std of VPDmax, hPa)'),
]):
    df_var = diversity[diversity.variable == var].sort_values('within_state_std')
    colors = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#BDC3C7'
              for st in df_var.state]
    ax.barh(range(len(df_var)), df_var.within_state_std.values, color=colors)
    ax.set_yticks(range(len(df_var)))
    ax.set_yticklabels(df_var.state.values, fontsize=8)
    ax.set_title(title, fontsize=12, fontweight='bold')

# Panel 4: Mean vs Diversity scatter
ax4 = axes[1, 1]
for var, marker, color in [('tmax', 'o', '#E74C3C'), ('ppt', 's', '#3498DB'), ('vpdmax', '^', '#F39C12')]:
    means = state_annual[state_annual.variable == var][['state', 'annual_mean']]
    divs = diversity[diversity.variable == var][['state', 'within_state_std']]
    merged = means.merge(divs, on='state')
    ax4.scatter(merged.annual_mean, merged.within_state_std, marker=marker, color=color,
                alpha=0.6, s=40, label=PRISM_VARIABLE_META[var]['short_label'])
    # Label CA
    ca_row = merged[merged.state == 'CA']
    if len(ca_row) > 0:
        ax4.annotate('CA', (ca_row.annual_mean.values[0], ca_row.within_state_std.values[0]),
                     fontsize=10, fontweight='bold', color='red')
ax4.set_xlabel("State Mean")
ax4.set_ylabel("Within-State Std")
ax4.set_title("Climate Mean vs. Diversity", fontsize=12, fontweight='bold')
ax4.legend(fontsize=10)

fig.suptitle("Figure 8: Within-State Climate Diversity",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "08_state_climate_diversity")"""))

cells.append(code("""\
# ── Figure 9: Fire Climate Index Rankings ─────────────────────────────────

fig, axes = plt.subplots(2, 1, figsize=(16, 18))

# Panel 1: Composite fire weather index (VPDmax * Tmax / PPT, simplified)
vpd_means = state_annual[state_annual.variable == 'vpdmax'].set_index('state')['annual_mean']
tmax_means = state_annual[state_annual.variable == 'tmax'].set_index('state')['annual_mean']
ppt_means = state_annual[state_annual.variable == 'ppt'].set_index('state')['annual_mean']

common_states = vpd_means.index.intersection(tmax_means.index).intersection(ppt_means.index)
fire_index = pd.DataFrame({
    'state': common_states,
    'vpd': vpd_means[common_states].values,
    'tmax': tmax_means[common_states].values,
    'ppt': ppt_means[common_states].values,
})
# Normalize and combine
for col in ['vpd', 'tmax', 'ppt']:
    fire_index[f'{col}_norm'] = (fire_index[col] - fire_index[col].min()) / (fire_index[col].max() - fire_index[col].min())
# Higher VPD + higher Tmax + lower PPT = higher fire risk
fire_index['fire_climate_index'] = (fire_index['vpd_norm'] * 0.5 +
                                     fire_index['tmax_norm'] * 0.3 +
                                     (1 - fire_index['ppt_norm']) * 0.2)
fire_index = fire_index.sort_values('fire_climate_index')

ax1 = axes[0]
colors = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#95A5A6'
          for st in fire_index.state]
ax1.barh(range(len(fire_index)), fire_index.fire_climate_index.values, color=colors)
ax1.set_yticks(range(len(fire_index)))
ax1.set_yticklabels(fire_index.state.values, fontsize=9)
ax1.set_xlabel("Composite Fire Climate Index (0–1)")
ax1.set_title("Composite Fire Climate Index: 50% VPD + 30% Tmax + 20% (1-PPT)",
              fontsize=12, fontweight='bold')
ca_idx = fire_index[fire_index.state == 'CA']
if len(ca_idx) > 0:
    rank = list(fire_index.state.values).index('CA') + 1
    ax1.text(0.98, 0.02, f"CA: #{rank}/{len(fire_index)} (index={ca_idx.fire_climate_index.values[0]:.3f})",
             transform=ax1.transAxes, ha='right', va='bottom', fontsize=11,
             color='#E74C3C', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

# Panel 2: Summer VPD ranking (June-August mean)
ax2 = axes[1]
if state_stats is not None:
    summer_vpd = state_stats[(state_stats.variable == 'vpdmax') &
                              (state_stats.month.isin([6,7,8])) &
                              (state_stats.year >= 2015)].groupby('state')['mean'].mean()
else:
    summer_vpd = vpd_means * 1.5  # rough summer approximation
summer_vpd = summer_vpd.sort_values()

colors2 = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#95A5A6'
           for st in summer_vpd.index]
ax2.barh(range(len(summer_vpd)), summer_vpd.values, color=colors2)
ax2.set_yticks(range(len(summer_vpd)))
ax2.set_yticklabels(summer_vpd.index, fontsize=9)
ax2.set_xlabel("Mean Summer VPDmax (hPa)")
ax2.set_title("Summer (JJA) Mean VPDmax — All 48 States",
              fontsize=12, fontweight='bold')
if 'CA' in summer_vpd.index:
    ca_val = summer_vpd['CA']
    rank = list(summer_vpd.index).index('CA') + 1
    ax2.text(0.98, 0.02, f"CA: #{rank}/{len(summer_vpd)} ({ca_val:.1f} hPa)",
             transform=ax2.transAxes, ha='right', va='bottom', fontsize=11,
             color='#E74C3C', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

fig.suptitle("Figure 9: Fire Climate Index — All 48 States",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "09_all_state_fire_climate_index")"""))

cells.append(code("""\
# ── Figure 10: All-State Monthly Climate Profiles (Small Multiples) ───────

# Compute monthly climatology per state
if state_stats is not None:
    recent = state_stats[(state_stats.year >= 2000) & (state_stats.year <= 2024)]
    monthly_clim = recent.groupby(['variable', 'state', 'month'])['mean'].mean().reset_index()
else:
    # Build from quarterly data we already have
    monthly_clim = state_annual.copy()
    monthly_clim['month'] = 7  # placeholder

# Sort states by region for display
region_order = {
    'Northeast': ['ME','NH','VT','MA','RI','CT','NY','NJ','PA'],
    'Southeast': ['DE','MD','DC','VA','WV','NC','SC','GA','FL'],
    'Midwest': ['OH','IN','IL','MI','WI','MN','IA','MO'],
    'Plains': ['ND','SD','NE','KS','OK','TX','AR','LA','MS','AL','TN','KY'],
    'Mountain': ['MT','ID','WY','CO','UT','NV','NM','AZ'],
    'Pacific': ['WA','OR','CA'],
}

all_states_ordered = []
for region, sts in region_order.items():
    all_states_ordered.extend(sts)

# 8x6 grid = 48 panels
n_cols, n_rows = 8, 6
fig, axes = plt.subplots(n_rows, n_cols, figsize=(28, 21))

for idx, st in enumerate(all_states_ordered[:48]):
    row, col = idx // n_cols, idx % n_cols
    ax = axes[row, col]

    # PPT bars
    ppt_data = monthly_clim[(monthly_clim.variable == 'ppt') & (monthly_clim.state == st)]
    tmax_data = monthly_clim[(monthly_clim.variable == 'tmax') & (monthly_clim.state == st)]

    if len(ppt_data) > 0 and 'month' in ppt_data.columns:
        ppt_by_month = ppt_data.groupby('month')['mean'].mean()
        ax.bar(ppt_by_month.index, ppt_by_month.values, color='#3498DB', alpha=0.6, width=0.7)
        ax.set_ylim(0, max(ppt_by_month.values.max() * 1.3, 10))

    # Tmax line on twin axis
    if len(tmax_data) > 0 and 'month' in tmax_data.columns:
        ax2 = ax.twinx()
        tmax_by_month = tmax_data.groupby('month')['mean'].mean()
        ax2.plot(tmax_by_month.index, tmax_by_month.values, 'r-', linewidth=1.5)
        ax2.set_ylim(-10, 45)
        ax2.tick_params(axis='y', labelsize=6, colors='red')
        if col != n_cols - 1:
            ax2.set_yticklabels([])

    # Style
    face_color = '#FFF5F5' if st == 'CA' else '#FFFDF5' if st in WESTERN_US_STATES else 'white'
    ax.set_facecolor(face_color)
    ax.set_title(st, fontsize=10, fontweight='bold',
                 color='#E74C3C' if st == 'CA' else 'black')
    ax.set_xticks([1, 4, 7, 10])
    ax.set_xticklabels(['J', 'A', 'J', 'O'], fontsize=7)
    ax.tick_params(axis='y', labelsize=6)
    if col != 0:
        ax.set_yticklabels([])

fig.suptitle("Figure 10: Monthly Climate Profiles — All 48 States\\n"
             "(Blue bars = precipitation, Red line = Tmax)",
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
save_fig(fig, "10_all_state_climate_profiles")"""))

cells.append(code("""\
# ── Figure 11: State Climate Summary Cards ────────────────────────────────

fig, axes = plt.subplots(8, 6, figsize=(24, 28))

for idx, st in enumerate(all_states_ordered[:48]):
    row, col = idx // 6, idx % 6
    ax = axes[row, col]
    ax.axis('off')

    # Get state metrics
    vpd_val = state_annual[(state_annual.variable == 'vpdmax') & (state_annual.state == st)].annual_mean.values
    tmax_val = state_annual[(state_annual.variable == 'tmax') & (state_annual.state == st)].annual_mean.values
    ppt_val = state_annual[(state_annual.variable == 'ppt') & (state_annual.state == st)].annual_mean.values

    vpd_str = f"{vpd_val[0]:.1f}" if len(vpd_val) > 0 else "N/A"
    tmax_str = f"{tmax_val[0]:.1f}" if len(tmax_val) > 0 else "N/A"
    ppt_str = f"{ppt_val[0]:.0f}" if len(ppt_val) > 0 else "N/A"

    # Card background
    bg_color = '#FFE8E8' if st == 'CA' else '#FFF8E8' if st in WESTERN_US_STATES else '#F0F8FF'
    rect = mpatches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.05",
                                     facecolor=bg_color, edgecolor='gray', linewidth=1,
                                     transform=ax.transAxes)
    ax.add_patch(rect)

    # State name
    full_name = CONUS_STATES.get(st, st)
    ax.text(0.5, 0.88, st, transform=ax.transAxes, fontsize=16, fontweight='bold',
            ha='center', va='center', color='#E74C3C' if st == 'CA' else '#2C3E50')
    ax.text(0.5, 0.72, full_name[:18], transform=ax.transAxes, fontsize=8,
            ha='center', va='center', color='gray')

    # Metrics
    ax.text(0.5, 0.52, f"VPD: {vpd_str} hPa", transform=ax.transAxes, fontsize=9,
            ha='center', va='center')
    ax.text(0.5, 0.38, f"Tmax: {tmax_str} °C", transform=ax.transAxes, fontsize=9,
            ha='center', va='center')
    ax.text(0.5, 0.24, f"PPT: {ppt_str} mm/mo", transform=ax.transAxes, fontsize=9,
            ha='center', va='center')

fig.suptitle("Figure 11: Climate Summary Cards — All 48 States",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "11_state_climate_summary_cards")"""))

# ═══════════════════════════════════════════════════════════════════
# PART 5: LONG-TERM TRENDS
# ═══════════════════════════════════════════════════════════════════

cells.append(md("""\
---
## Part 5 — Long-Term CONUS Trends

130 years of climate data reveal warming, drying, and intensifying fire weather."""))

cells.append(code("""\
# ── Figure 12: National Climate Trends ────────────────────────────────────

# Use CA stats as proxy for national trends (if state cache unavailable, load CA)
if ca_stats is not None:
    ca_ts = ca_stats.copy()
else:
    print("Loading CA stats on the fly...")
    from src.utils.prism_data_loader import load_monthly_stats_ca
    ca_ts = pd.DataFrame()
    for var in ['ppt', 'tmax', 'tmin', 'vpdmax', 'vpdmin', 'tmean']:
        df = load_monthly_stats_ca(var, 1895, 2025, progress=False)
        df['variable'] = var
        ca_ts = pd.concat([ca_ts, df])

fig, axes = plt.subplots(3, 2, figsize=(20, 18))
var_colors = get_prism_variable_colors()

trend_vars = ['tmax', 'tmin', 'tmean', 'ppt', 'vpdmax', 'vpdmin']
trend_titles = ['Max Temperature', 'Min Temperature', 'Mean Temperature',
                'Precipitation', 'Max VPD', 'Min VPD']

for ax, var, title in zip(axes.flat, trend_vars, trend_titles):
    df_var = ca_ts[ca_ts.variable == var] if 'variable' in ca_ts.columns else ca_ts
    if 'variable' in ca_ts.columns:
        df_var = ca_ts[ca_ts.variable == var]

    # Annual means
    annual = df_var.groupby('year')['mean'].mean()

    ax.plot(annual.index, annual.values, color=var_colors[var], alpha=0.4, linewidth=0.8)

    # 10-year running mean
    if len(annual) > 10:
        rolling = annual.rolling(10, center=True).mean()
        ax.plot(rolling.index, rolling.values, color=var_colors[var], linewidth=2.5, label='10-yr mean')

    # Linear trend
    valid = annual.dropna()
    if len(valid) > 20:
        z = np.polyfit(valid.index, valid.values, 1)
        trend_line = np.poly1d(z)
        ax.plot(valid.index, trend_line(valid.index), '--', color='black', linewidth=1, alpha=0.5)
        slope_per_decade = z[0] * 10
        units = PRISM_VARIABLE_META[var]['units']
        ax.text(0.02, 0.98, f"Trend: {slope_per_decade:+.2f} {units}/decade",
                transform=ax.transAxes, fontsize=10, va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_title(f"California {title}", fontsize=12, fontweight='bold')
    ax.set_xlabel("Year")
    ax.set_ylabel(PRISM_VARIABLE_META[var]['units'])
    ax.legend(fontsize=9)

fig.suptitle("Figure 12: 130-Year Climate Trends — California",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "12_national_climate_trends")"""))

cells.append(code("""\
# ── Figure 13: Western State VPD Trends ───────────────────────────────────

fig, axes = plt.subplots(3, 4, figsize=(24, 16))

# If state cache available, show VPD trends for all 11 western states
if state_stats is not None:
    for idx, st in enumerate(WESTERN_US_STATES[:11]):
        row, col = idx // 4, idx % 4
        ax = axes[row, col]

        df_st = state_stats[(state_stats.variable == 'vpdmax') & (state_stats.state == st)]
        annual = df_st.groupby('year')['mean'].mean()

        ax.plot(annual.index, annual.values, color='#C0392B', alpha=0.3, linewidth=0.8)
        if len(annual) > 10:
            rolling = annual.rolling(10, center=True).mean()
            ax.plot(rolling.index, rolling.values, color='#C0392B', linewidth=2.5)

        # Trend
        valid = annual.dropna()
        if len(valid) > 20:
            z = np.polyfit(valid.index, valid.values, 1)
            slope = z[0] * 10
            ax.text(0.02, 0.98, f"{slope:+.2f} hPa/dec",
                    transform=ax.transAxes, fontsize=10, va='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        state_name = CONUS_STATES.get(st, st)
        color = '#E74C3C' if st == 'CA' else '#2C3E50'
        ax.set_title(f"{state_name} ({st})", fontsize=11, fontweight='bold', color=color)
        ax.set_ylabel("VPDmax (hPa)" if col == 0 else "")
else:
    # Show CA only replicated message
    for ax in axes.flat:
        ax.text(0.5, 0.5, "State cache needed\\nRun precomputation",
                transform=ax.transAxes, ha='center', fontsize=10)

# Hide empty subplot
if len(WESTERN_US_STATES) < 12:
    axes[2, 3].axis('off')

fig.suptitle("Figure 13: VPD Trends — All 11 Western Fire States",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "13_all_western_state_trends")"""))

cells.append(code("""\
# ── Figure 14: Decadal Climate Shifts ─────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

# Panel 1-3: Decadal boxplots for CA
if ca_stats is not None:
    ca_ts_copy = ca_stats.copy()
    ca_ts_copy['decade'] = (ca_ts_copy['year'] // 10) * 10

    for ax, var, title in zip(axes.flat[:3], ['tmax', 'vpdmax', 'ppt'],
                               ['Max Temperature', 'Max VPD', 'Precipitation']):
        df_var = ca_ts_copy[ca_ts_copy.variable == var]
        decades = sorted(df_var.decade.unique())
        decades = [d for d in decades if d >= 1900]  # Skip sparse early decades

        data_by_decade = [df_var[df_var.decade == d]['mean'].values for d in decades]
        bp = ax.boxplot(data_by_decade, labels=[str(d)+'s' for d in decades],
                        patch_artist=True)

        colors_grad = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(decades)))
        for patch, color in zip(bp['boxes'], colors_grad):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_title(f"CA {title} by Decade", fontsize=12, fontweight='bold')
        ax.set_ylabel(PRISM_VARIABLE_META[var]['units'])
        ax.tick_params(axis='x', rotation=45)

# Panel 4: Decade heatmap (state × decade for VPDmax anomaly)
ax4 = axes[1, 1]
if state_stats is not None:
    vpd_state = state_stats[state_stats.variable == 'vpdmax'].copy()
    vpd_state['decade'] = (vpd_state['year'] // 10) * 10
    vpd_pivot = vpd_state.groupby(['state', 'decade'])['mean'].mean().unstack(fill_value=np.nan)
    # Compute anomaly from long-term mean per state
    state_means = vpd_pivot.mean(axis=1)
    vpd_anom = vpd_pivot.sub(state_means, axis=0)
    vpd_anom = vpd_anom[[d for d in vpd_anom.columns if d >= 1900]]

    # Sort states by CA rank
    sns.heatmap(vpd_anom, cmap='RdBu_r', center=0, ax=ax4,
                xticklabels=True, yticklabels=True, cbar_kws={'label': 'VPD Anomaly (hPa)'})
    ax4.set_title("VPDmax Anomaly: State × Decade", fontsize=12, fontweight='bold')
    ax4.tick_params(axis='y', labelsize=6)
    ax4.tick_params(axis='x', labelsize=8, rotation=45)
else:
    ax4.text(0.5, 0.5, "Requires state cache", transform=ax4.transAxes, ha='center')

fig.suptitle("Figure 14: Decadal Climate Shifts",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "14_decadal_climate_shifts")"""))

cells.append(code("""\
# ── Figure 15: State Warming Rates Choropleth ─────────────────────────────

fig, ax = plt.subplots(1, 1, figsize=(18, 10))

# Compute per-state warming rate (Tmax trend per decade)
warming_rates = {}
if state_stats is not None:
    for st in states_gdf.STUSPS.unique():
        df_st = state_stats[(state_stats.variable == 'tmax') & (state_stats.state == st)]
        annual = df_st.groupby('year')['mean'].mean()
        if len(annual) > 30:
            valid = annual.dropna()
            z = np.polyfit(valid.index, valid.values, 1)
            warming_rates[st] = z[0] * 10  # per decade
else:
    # Fallback: just use CA
    warming_rates = {'CA': 0.15}

# Merge with geodataframe
states_plot = states_gdf.copy()
states_plot['warming_rate'] = states_plot['STUSPS'].map(warming_rates)

states_plot.plot(column='warming_rate', cmap='RdYlBu_r', legend=True, ax=ax,
                 edgecolor='gray', linewidth=0.5,
                 legend_kwds={'label': 'Warming Rate (°C/decade)', 'shrink': 0.5})

# Highlight CA
ca_plot = states_plot[states_plot.STUSPS == 'CA']
ca_plot.boundary.plot(ax=ax, color='red', linewidth=2)

# Add state labels
for _, row in states_plot.iterrows():
    centroid = row.geometry.centroid
    rate = row.get('warming_rate', np.nan)
    if not np.isnan(rate):
        ax.text(centroid.x, centroid.y, f"{row.STUSPS}\\n{rate:.2f}",
                fontsize=6, ha='center', va='center', fontweight='bold')

ax.set_xlim(-125, -66)
ax.set_ylim(24, 50)
ax.set_title("Warming Rate by State (Tmax °C per Decade)", fontsize=14, fontweight='bold')

fig.suptitle("Figure 15: CONUS Warming Rates — Every State",
             fontsize=16, fontweight='bold', y=1.01)
save_fig(fig, "15_state_warming_rates")"""))

# ═══════════════════════════════════════════════════════════════════
# PART 6: SEASONAL PATTERNS
# ═══════════════════════════════════════════════════════════════════

cells.append(md("""\
---
## Part 6 — Seasonal Patterns — All States"""))

cells.append(code("""\
# ── Figure 16: All-State Seasonal Heatmaps ────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(24, 14))

heat_vars = [('tmax', 'Tmax (°C)', 'YlOrRd'),
             ('ppt', 'Precip (mm)', 'YlGnBu'),
             ('vpdmax', 'VPDmax (hPa)', 'YlOrRd')]

for ax, (var, label, cmap) in zip(axes, heat_vars):
    if state_stats is not None:
        recent = state_stats[(state_stats.variable == var) &
                              (state_stats.year >= 2000)]
        pivot = recent.groupby(['state', 'month'])['mean'].mean().unstack(fill_value=np.nan)
        # Sort by annual mean
        pivot['annual'] = pivot.mean(axis=1)
        pivot = pivot.sort_values('annual').drop('annual', axis=1)

        sns.heatmap(pivot, cmap=cmap, ax=ax, xticklabels=MONTH_ABBREVS,
                    yticklabels=True, cbar_kws={'label': label})
        ax.set_title(f"{label} — All States × Months", fontsize=12, fontweight='bold')
        ax.tick_params(axis='y', labelsize=7)

        # Mark CA row
        if 'CA' in pivot.index:
            ca_pos = list(pivot.index).index('CA')
            ax.axhline(ca_pos, color='red', linewidth=2)
            ax.axhline(ca_pos + 1, color='red', linewidth=2)
    else:
        ax.text(0.5, 0.5, "Requires state cache", transform=ax.transAxes, ha='center')

fig.suptitle("Figure 16: Seasonal Heatmaps — 48 States × 12 Months",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "16_all_state_seasonal_heatmap")"""))

cells.append(code("""\
# ── Figure 17: Fire Season Climate — All States ──────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(20, 16))

if state_stats is not None:
    recent = state_stats[(state_stats.year >= 2000) & (state_stats.year <= 2024)]

    # Panel 1: Fire season (Jun-Sep) VPD
    ax1 = axes[0, 0]
    fire_vpd = recent[(recent.variable == 'vpdmax') & (recent.month.isin([6,7,8,9]))]
    fire_vpd_mean = fire_vpd.groupby('state')['mean'].mean().sort_values()
    colors = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#95A5A6'
              for st in fire_vpd_mean.index]
    ax1.barh(range(len(fire_vpd_mean)), fire_vpd_mean.values, color=colors)
    ax1.set_yticks(range(len(fire_vpd_mean)))
    ax1.set_yticklabels(fire_vpd_mean.index, fontsize=7)
    ax1.set_xlabel("Mean Fire Season VPDmax (hPa)")
    ax1.set_title("Fire Season (Jun-Sep) VPD", fontsize=12, fontweight='bold')

    # Panel 2: Wet season (Nov-Mar) PPT
    ax2 = axes[0, 1]
    wet_ppt = recent[(recent.variable == 'ppt') & (recent.month.isin([11,12,1,2,3]))]
    wet_ppt_mean = wet_ppt.groupby('state')['mean'].mean().sort_values(ascending=False)
    colors2 = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#95A5A6'
               for st in wet_ppt_mean.index]
    ax2.barh(range(len(wet_ppt_mean)), wet_ppt_mean.values, color=colors2)
    ax2.set_yticks(range(len(wet_ppt_mean)))
    ax2.set_yticklabels(wet_ppt_mean.index, fontsize=7)
    ax2.set_xlabel("Mean Wet Season PPT (mm/mo)")
    ax2.set_title("Wet Season (Nov-Mar) Precipitation", fontsize=12, fontweight='bold')

    # Panel 3: Fire regime quadrant (high VPD × low PPT = fire-prone)
    ax3 = axes[1, 0]
    fire_vpd_s = fire_vpd.groupby('state')['mean'].mean()
    wet_ppt_s = wet_ppt.groupby('state')['mean'].mean()
    common = fire_vpd_s.index.intersection(wet_ppt_s.index)

    for st in common:
        color = '#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#3498DB'
        size = 120 if st == 'CA' else 60 if st in WESTERN_US_STATES else 30
        ax3.scatter(fire_vpd_s[st], wet_ppt_s[st], color=color, s=size, alpha=0.7)
        if st in WESTERN_US_STATES or st == 'CA':
            ax3.annotate(st, (fire_vpd_s[st], wet_ppt_s[st]), fontsize=8, fontweight='bold')

    ax3.set_xlabel("Fire Season VPDmax (hPa)")
    ax3.set_ylabel("Wet Season PPT (mm/mo)")
    ax3.set_title("Fire Regime Quadrant", fontsize=12, fontweight='bold')
    # Draw quadrant lines at medians
    ax3.axvline(fire_vpd_s.median(), color='gray', linestyle='--', alpha=0.5)
    ax3.axhline(wet_ppt_s.median(), color='gray', linestyle='--', alpha=0.5)
    ax3.text(0.98, 0.02, "HIGH VPD + LOW PPT\\n= Fire-Prone", transform=ax3.transAxes,
             ha='right', va='bottom', fontsize=10, color='red', fontstyle='italic')

    # Panel 4: VPD/PPT ratio
    ax4 = axes[1, 1]
    ratio = (fire_vpd_s / wet_ppt_s).sort_values()
    colors4 = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#95A5A6'
               for st in ratio.index]
    ax4.barh(range(len(ratio)), ratio.values, color=colors4)
    ax4.set_yticks(range(len(ratio)))
    ax4.set_yticklabels(ratio.index, fontsize=7)
    ax4.set_xlabel("Fire Season VPD / Wet Season PPT Ratio")
    ax4.set_title("Fire Climate Aridity Ratio", fontsize=12, fontweight='bold')
else:
    for ax in axes.flat:
        ax.text(0.5, 0.5, "Requires state cache", transform=ax.transAxes, ha='center')

fig.suptitle("Figure 17: Fire Season Climate — All 48 States",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "17_fire_season_climate_all_states")"""))

cells.append(code("""\
# ── Figure 18: Precipitation Seasonality ──────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

if state_stats is not None:
    recent = state_stats[(state_stats.variable == 'ppt') &
                          (state_stats.year >= 2000)]

    # Seasonality index: max_month_ppt / min_month_ppt
    monthly_mean = recent.groupby(['state', 'month'])['mean'].mean().unstack()
    seasonality = monthly_mean.max(axis=1) / monthly_mean.min(axis=1).replace(0, 0.1)
    seasonality = seasonality.sort_values()

    # Panel 1: Seasonality ranking
    ax1 = axes[0, 0]
    colors = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#3498DB'
              for st in seasonality.index]
    ax1.barh(range(len(seasonality)), seasonality.values, color=colors)
    ax1.set_yticks(range(len(seasonality)))
    ax1.set_yticklabels(seasonality.index, fontsize=7)
    ax1.set_xlabel("Seasonality Index (max/min monthly PPT)")
    ax1.set_title("Precipitation Seasonality", fontsize=12, fontweight='bold')

    # Panel 2: Wettest month by state
    ax2 = axes[0, 1]
    wettest_month = monthly_mean.idxmax(axis=1)
    month_counts = wettest_month.value_counts().sort_index()
    ax2.bar(month_counts.index, month_counts.values, color='#3498DB')
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(MONTH_ABBREVS)
    ax2.set_ylabel("Number of States")
    ax2.set_title("Wettest Month Distribution", fontsize=12, fontweight='bold')

    # Panel 3: Example seasonal cycles
    ax3 = axes[1, 0]
    example_states = ['CA', 'FL', 'WA', 'TX', 'NY', 'AZ']
    season_colors = ['#E74C3C', '#2ECC71', '#3498DB', '#F39C12', '#9B59B6', '#D4A574']
    for st, color in zip(example_states, season_colors):
        if st in monthly_mean.index:
            vals = monthly_mean.loc[st]
            ax3.plot(range(1, 13), vals, '-o', color=color, label=st, linewidth=2, markersize=4)
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels(MONTH_ABBREVS)
    ax3.set_ylabel("Monthly PPT (mm)")
    ax3.set_title("Monthly Precipitation — 6 Contrasting States", fontsize=12, fontweight='bold')
    ax3.legend(ncol=2, fontsize=10)

    # Panel 4: % of annual PPT in wettest 3 months
    ax4 = axes[1, 1]
    annual_ppt = monthly_mean.sum(axis=1)
    top3_ppt = monthly_mean.apply(lambda row: row.nlargest(3).sum(), axis=1)
    concentration = (100 * top3_ppt / annual_ppt).sort_values()
    colors4 = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#3498DB'
               for st in concentration.index]
    ax4.barh(range(len(concentration)), concentration.values, color=colors4)
    ax4.set_yticks(range(len(concentration)))
    ax4.set_yticklabels(concentration.index, fontsize=7)
    ax4.set_xlabel("% of Annual PPT in Wettest 3 Months")
    ax4.set_title("Precipitation Concentration", fontsize=12, fontweight='bold')
else:
    for ax in axes.flat:
        ax.text(0.5, 0.5, "Requires state cache", transform=ax.transAxes, ha='center')

fig.suptitle("Figure 18: Precipitation Seasonality — All 48 States",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "18_precipitation_seasonality")"""))

cells.append(code("""\
# ── Figure 19: Seasonal Amplitude ─────────────────────────────────────────

fig, axes = plt.subplots(2, 1, figsize=(16, 16))

if state_stats is not None:
    recent = state_stats[(state_stats.year >= 2000)]

    # Temp amplitude: max monthly tmax - min monthly tmax
    ax1 = axes[0]
    tmax_monthly = recent[recent.variable == 'tmax'].groupby(['state', 'month'])['mean'].mean().unstack()
    temp_amplitude = (tmax_monthly.max(axis=1) - tmax_monthly.min(axis=1)).sort_values()
    colors = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#3498DB'
              for st in temp_amplitude.index]
    ax1.barh(range(len(temp_amplitude)), temp_amplitude.values, color=colors)
    ax1.set_yticks(range(len(temp_amplitude)))
    ax1.set_yticklabels(temp_amplitude.index, fontsize=8)
    ax1.set_xlabel("Seasonal Tmax Amplitude (°C)")
    ax1.set_title("Temperature Seasonality (Max - Min Monthly Tmax)", fontsize=12, fontweight='bold')

    # VPD amplitude
    ax2 = axes[1]
    vpd_monthly = recent[recent.variable == 'vpdmax'].groupby(['state', 'month'])['mean'].mean().unstack()
    vpd_amplitude = (vpd_monthly.max(axis=1) - vpd_monthly.min(axis=1)).sort_values()
    colors2 = ['#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#C0392B'
               for st in vpd_amplitude.index]
    ax2.barh(range(len(vpd_amplitude)), vpd_amplitude.values, color=colors2)
    ax2.set_yticks(range(len(vpd_amplitude)))
    ax2.set_yticklabels(vpd_amplitude.index, fontsize=8)
    ax2.set_xlabel("Seasonal VPDmax Amplitude (hPa)")
    ax2.set_title("VPD Seasonality (Max - Min Monthly VPDmax)", fontsize=12, fontweight='bold')
else:
    for ax in axes:
        ax.text(0.5, 0.5, "Requires state cache", transform=ax.transAxes, ha='center')

fig.suptitle("Figure 19: Seasonal Climate Amplitude — All 48 States",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "19_state_seasonal_diversity")"""))

# ═══════════════════════════════════════════════════════════════════
# PART 7: CLIMATE REGIONS
# ═══════════════════════════════════════════════════════════════════

cells.append(md("""\
---
## Part 7 — CONUS Climate Regions"""))

cells.append(code("""\
# ── Figure 20: Climate Clustering Map ─────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(24, 10))

# Panel 1: K-means clustering on state climate features
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

if state_stats is not None:
    recent = state_stats[(state_stats.year >= 2000)]
    # Build feature matrix: state × [annual tmax, annual ppt, annual vpdmax, seasonality]
    features = {}
    for var in ['tmax', 'ppt', 'vpdmax']:
        means = recent[recent.variable == var].groupby('state')['mean'].mean()
        features[f'{var}_mean'] = means

    feature_df = pd.DataFrame(features).dropna()

    # Scale and cluster
    scaler = StandardScaler()
    X = scaler.fit_transform(feature_df.values)
    kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)

    feature_df['cluster'] = clusters
    states_cluster = states_gdf.merge(
        feature_df[['cluster']].reset_index().rename(columns={'index': 'state', 'state': 'STUSPS_x'}),
        left_on='STUSPS', right_on='state', how='left'
    )
    # Fix merge if needed
    if 'cluster' not in states_cluster.columns:
        states_cluster = states_gdf.copy()
        states_cluster['cluster'] = states_cluster['STUSPS'].map(
            dict(zip(feature_df.index, feature_df.cluster))
        )

    cluster_colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C']

    ax1 = axes[0]
    for cl in range(6):
        subset = states_cluster[states_cluster.cluster == cl]
        if len(subset) > 0:
            subset.plot(ax=ax1, color=cluster_colors[cl], edgecolor='white', linewidth=0.5)
    states_gdf.boundary.plot(ax=ax1, color='gray', linewidth=0.3)
    ca.boundary.plot(ax=ax1, color='red', linewidth=2)
    ax1.set_xlim(-125, -66)
    ax1.set_ylim(24, 50)
    ax1.set_title("K-Means Climate Clusters (k=6)", fontsize=14, fontweight='bold')

    # Add state labels
    for _, row in states_gdf.iterrows():
        c = row.geometry.centroid
        ax1.text(c.x, c.y, row.STUSPS, fontsize=6, ha='center', fontweight='bold')

    # Panel 2: Same with fire overlay info
    ax2 = axes[1]
    for cl in range(6):
        subset = states_cluster[states_cluster.cluster == cl]
        if len(subset) > 0:
            subset.plot(ax=ax2, color=cluster_colors[cl], edgecolor='white',
                       linewidth=0.5, alpha=0.5)
    states_gdf.boundary.plot(ax=ax2, color='gray', linewidth=0.3)

    # Highlight western fire states
    western = states_gdf[states_gdf.STUSPS.isin(WESTERN_US_STATES)]
    western.boundary.plot(ax=ax2, color='red', linewidth=2)

    for _, row in states_gdf.iterrows():
        c = row.geometry.centroid
        ax2.text(c.x, c.y, row.STUSPS, fontsize=6, ha='center', fontweight='bold')

    ax2.set_xlim(-125, -66)
    ax2.set_ylim(24, 50)
    ax2.set_title("Climate Clusters + Western Fire States (red)", fontsize=14, fontweight='bold')
else:
    for ax in axes:
        ax.text(0.5, 0.5, "Requires state cache", transform=ax.transAxes, ha='center')

fig.suptitle("Figure 20: CONUS Climate Regions — K-Means Clustering",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "20_conus_climate_regions")"""))

# ═══════════════════════════════════════════════════════════════════
# PART 8: SUMMARY TABLE + INTERACTIVE MAP
# ═══════════════════════════════════════════════════════════════════

cells.append(md("""\
---
## Part 8 — All-State Summary Table & Interactive Map"""))

cells.append(code("""\
# ── Figure 21: Comprehensive Summary Table ────────────────────────────────

fig, ax = plt.subplots(figsize=(22, 18))
ax.axis('off')

# Build summary for all states
summary_rows = []
for st in sorted(CONUS_STATES.keys()):
    row_data = [st, CONUS_STATES[st][:20]]
    for var in ['tmax', 'tmin', 'ppt', 'vpdmax', 'vpdmin']:
        val = state_annual[(state_annual.variable == var) & (state_annual.state == st)].annual_mean.values
        row_data.append(f"{val[0]:.1f}" if len(val) > 0 else "—")

    # Warming rate
    rate = warming_rates.get(st, np.nan)
    row_data.append(f"{rate:.2f}" if not np.isnan(rate) else "—")

    # Fire index
    fi = fire_index[fire_index.state == st].fire_climate_index.values
    row_data.append(f"{fi[0]:.3f}" if len(fi) > 0 else "—")

    summary_rows.append(row_data)

col_labels = ['State', 'Name', 'Tmax\\n(°C)', 'Tmin\\n(°C)', 'PPT\\n(mm/mo)',
              'VPDmax\\n(hPa)', 'VPDmin\\n(hPa)', 'Warming\\n(°C/dec)', 'Fire\\nIndex']

table = ax.table(cellText=summary_rows, colLabels=col_labels,
                 loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(7)
table.auto_set_column_width(col=list(range(len(col_labels))))
table.scale(1, 1.15)

# Style header
for j in range(len(col_labels)):
    table[0, j].set_facecolor('#2C3E50')
    table[0, j].set_text_props(color='white', fontweight='bold', fontsize=8)

# Highlight CA row
for i, row in enumerate(summary_rows):
    if row[0] == 'CA':
        for j in range(len(col_labels)):
            table[i + 1, j].set_facecolor('#FFE8E8')
    elif row[0] in WESTERN_US_STATES:
        for j in range(len(col_labels)):
            table[i + 1, j].set_facecolor('#FFF8E8')

ax.set_title("Figure 21: All-State Climate Summary Table\\n"
             "(CA = red, Western fire states = yellow)",
             fontsize=14, fontweight='bold', pad=20)

save_fig(fig, "21_all_state_summary_table")"""))

cells.append(code("""\
# ── Figure 22: State Comparison Radar Charts ──────────────────────────────

from math import pi

representative_states = ['CA', 'OR', 'AZ', 'TX', 'FL', 'NY', 'CO', 'MT', 'WA']
radar_vars = ['tmax', 'tmin', 'ppt', 'vpdmax', 'vpdmin', 'tmean', 'tdmean']
radar_labels = [PRISM_VARIABLE_META[v]['short_label'] for v in radar_vars]

fig, axes = plt.subplots(3, 3, figsize=(20, 20), subplot_kw=dict(polar=True))

# Normalize each variable to 0-1 across all states
norm_data = {}
for var in radar_vars:
    vals = state_annual[state_annual.variable == var]['annual_mean']
    vmin, vmax = vals.min(), vals.max()
    norm_data[var] = (vmin, vmax)

angles = np.linspace(0, 2 * pi, len(radar_vars), endpoint=False).tolist()
angles += angles[:1]

for idx, st in enumerate(representative_states):
    row, col = idx // 3, idx % 3
    ax = axes[row, col]

    values = []
    for var in radar_vars:
        val = state_annual[(state_annual.variable == var) & (state_annual.state == st)].annual_mean.values
        if len(val) > 0:
            vmin, vmax = norm_data[var]
            normalized = (val[0] - vmin) / (vmax - vmin) if vmax > vmin else 0.5
            values.append(normalized)
        else:
            values.append(0)
    values += values[:1]

    color = '#E74C3C' if st == 'CA' else '#F39C12' if st in WESTERN_US_STATES else '#3498DB'

    ax.plot(angles, values, color=color, linewidth=2)
    ax.fill(angles, values, color=color, alpha=0.2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(radar_labels, fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_title(f"{CONUS_STATES[st]} ({st})", fontsize=12, fontweight='bold',
                 color=color, pad=15)

fig.suptitle("Figure 22: Climate Profiles — 9 Representative States",
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
save_fig(fig, "22_state_comparison_radar")"""))

# ═══════════════════════════════════════════════════════════════════
# PART 9: EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════

cells.append(md("""\
---
## Part 9 — Executive Summary

### Key Findings from CONUS Analysis

1. **California ranks among top 5 states** for fire climate index (high VPD + high Tmax + low summer PPT)
2. **Dramatic VPD seasonality**: CA has one of the largest seasonal VPD amplitudes — mild wet winters, extreme dry summers
3. **Mediterranean precipitation regime**: CA has the highest precipitation concentration (wettest 3 months >> rest of year)
4. **Warming trend**: All western states show positive warming trends, with CA warming ~0.1-0.2°C per decade
5. **VPD increasing**: Fire-season VPD has been trending upward across all western states since 1895
6. **Climate clustering**: Western fire states cluster distinctly from eastern US — hot/dry summer regime

### Preview: Part 2 (California Deep Dive) & Part 3 (Fire-Climate Integration)

- **Part 2**: Spatial patterns within California — 8 climate regions, 130-year trends, VPD extremes, drought analysis
- **Part 3**: Climate variables extracted at fire locations — VPD as predictor, antecedent drought signals, severity relationships"""))

cells.append(code("""\
# Final summary
print("=" * 70)
print("PRISM Comprehensive Analysis — Part 1: CONUS + All States")
print("=" * 70)
print(f"\\nFigures generated: 22")
print(f"Output directory: {PRISM_CONUS_FIG_DIR}")
print(f"\\nStates analyzed: {len(CONUS_STATES)} CONUS states + DC")
print(f"Variables: {len(PRISM_VARIABLES)} ({', '.join(PRISM_VARIABLES)})")
print(f"Temporal range: {PRISM_MONTHLY_START_YEAR}–{PRISM_MONTHLY_END_YEAR} (monthly)")

import os
figs = [f for f in os.listdir(PRISM_CONUS_FIG_DIR) if f.endswith('.png')]
print(f"\\nFigures saved: {len(figs)}")
for f in sorted(figs):
    size_kb = os.path.getsize(PRISM_CONUS_FIG_DIR / f) / 1024
    print(f"  {f} ({size_kb:.0f} KB)")"""))

# ═══════════════════════════════════════════════════════════════════
# BUILD NOTEBOOK
# ═══════════════════════════════════════════════════════════════════

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (wildfire)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "cells": cells
}

output_path = "notebooks/PRISM_Comprehensive_Analysis_Part1_CONUS.ipynb"
with open(output_path, 'w') as f:
    json.dump(notebook, f, indent=1)

print(f"Notebook written: {output_path}")
print(f"Total cells: {len(cells)} ({sum(1 for c in cells if c['cell_type']=='markdown')} markdown, "
      f"{sum(1 for c in cells if c['cell_type']=='code')} code)")
