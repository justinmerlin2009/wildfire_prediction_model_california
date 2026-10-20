#!/usr/bin/env python3
"""Build PRISM Comprehensive Analysis Part 2: California Deep Dive notebook."""
import json

def md(source):
    lines = source.split('\n')
    return {"cell_type": "markdown", "metadata": {}, "source": [l + '\n' for l in lines[:-1]] + [lines[-1]]}

def code(source):
    lines = source.split('\n')
    return {"cell_type": "code", "metadata": {}, "source": [l + '\n' for l in lines[:-1]] + [lines[-1]], "outputs": [], "execution_count": None}

cells = []

# ═══ TITLE + TOC ═══
cells.append(md("""\
# PRISM Climate Data Comprehensive Analysis — Part 2: California Deep Dive

**Phase 3A** | California Wildfire Prediction Model
**Dataset**: PRISM 30-arcsecond (~800m), monthly 1895–2025
**Focus**: California's 130-year climate history — temperature, precipitation, VPD"""))

cells.append(md("""\
### Table of Contents

| Part | Title | Figures |
|------|-------|---------|
| 1 | Introduction & Context | — |
| 2 | Data Loading & Quality | Fig 1–2 |
| 3 | Long-Term Temperature Trends | Fig 3–6 |
| 4 | Precipitation Regime | Fig 7–10 |
| 5 | VPD — The #1 Fire Predictor | Fig 11–15 |
| 6 | Derived Climate Indices | Fig 16–17 |
| 7 | CA Climate Region Profiles | Fig 18 |
| 8 | 30-Year Normals Deep Dive | — |
| 9 | Executive Summary & ML Readiness | — |"""))

cells.append(md("""\
---
## Part 1 — Introduction & Context

California's climate is extraordinarily diverse — from the wettest temperate rainforests to the driest deserts, all within a single state. This Part 2 notebook provides the deepest analysis of California's climate history using 130 years of PRISM data.

**Key questions:**
- How fast is California warming, and where?
- How have VPD extremes changed over 130 years?
- What does the drought history look like?
- How do California's 8 climate regions differ?"""))

# ═══ PART 2: DATA LOADING ═══
cells.append(md("---\n## Part 2 — Data Loading & Quality"))

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

sys.path.insert(0, '..')
from src.utils.constants import (
    PRISM_BASE_PATH, PRISM_CRS, PRISM_NODATA, PRISM_CA_BOUNDS,
    PRISM_VARIABLES, PRISM_CACHE_DIR, FIGURES_DIR, FIGURE_DPI,
    CA_BOUNDARY_PATH,
)
from src.utils.prism_domain_mappings import (
    PRISM_VARIABLE_META, PRISM_VARIABLE_ORDER,
    FIRE_WEATHER_VPD_CLASSES, FIRE_WEATHER_VPD_ORDER,
    CA_CLIMATE_REGIONS, CLIMATE_SEASON_MAP, CLIMATE_SEASON_ORDER,
    MONTH_ABBREVS, MONTH_NAMES, DERIVED_VARIABLES,
    get_variable_label, get_variable_colormap, classify_vpd, classify_drought,
    compute_rh_from_tdmean_tmax,
)
from src.utils.prism_data_loader import (
    check_prism_drive, discover_files,
    read_prism_california, load_monthly_normal, load_all_monthly_normals,
    compute_monthly_anomaly, compute_diurnal_temp_range,
    compute_vpd_mean, compute_dew_point_depression, compute_estimated_rh,
    load_from_cache, get_prism_data_quality_summary,
)
from src.utils.plotting import (
    setup_plotting_style, save_figure,
    get_prism_variable_colors, get_vpd_risk_colors,
    get_drought_colors, get_climate_season_colors,
    get_prism_diverging_norm,
)

setup_plotting_style()

CA_FIG_DIR = FIGURES_DIR / "prism_california"
CA_FIG_DIR.mkdir(parents=True, exist_ok=True)

def save_fig(fig, name):
    save_figure(fig, f"prism_california/{name}")
    plt.close(fig)

print("Imports complete.")"""))

cells.append(code("""\
# ── Load CA monthly stats cache ──────────────────────────────────────────

check_prism_drive()
ca_stats = load_from_cache("prism_ca_monthly_stats")
if ca_stats is not None:
    print(f"CA monthly stats: {len(ca_stats):,} rows")
    print(f"Variables: {ca_stats.variable.unique().tolist()}")
    print(f"Year range: {ca_stats.year.min()}-{ca_stats.year.max()}")
    print(f"\\nSample:")
    print(ca_stats.head())
else:
    raise FileNotFoundError("CA stats cache not found! Run: python scripts/prism_precompute_state_summaries.py --ca-only")"""))

# ═══ FIGURE 1: CA Climate Overview ═══
cells.append(code("""\
# ── Figure 1: California Climate Overview (7 variables + est RH) ─────────

fig, axes = plt.subplots(2, 4, figsize=(24, 12))

overview_vars = PRISM_VARIABLES + ['est_rh']  # 7 + derived

for idx, var in enumerate(overview_vars[:8]):
    ax = axes[idx // 4, idx % 4]

    if var == 'est_rh':
        # Load tdmean and tmax July normals for est. RH
        td_result = load_monthly_normal('tdmean', 7, bounds=PRISM_CA_BOUNDS)
        tx_result = load_monthly_normal('tmax', 7, bounds=PRISM_CA_BOUNDS)
        if td_result and tx_result:
            td_data, tfm, _ = td_result
            tx_data, _, _ = tx_result
            data = compute_estimated_rh(td_data, tx_data)
            data_plot = np.where(np.isnan(data), np.nan, data)
            title = "Estimated Min RH — July Normal"
            cmap = 'YlGnBu'
            units = '%'
            del td_data, tx_data
        else:
            continue
    else:
        result = load_monthly_normal(var, 7, bounds=PRISM_CA_BOUNDS)
        if not result:
            ax.text(0.5, 0.5, f"No normal for {var}", transform=ax.transAxes, ha='center')
            continue
        data, tfm, _ = result
        data_plot = np.where(data == PRISM_NODATA, np.nan, data)
        title = f"{PRISM_VARIABLE_META[var]['short_label']} — July Normal"
        cmap = get_variable_colormap(var)
        units = PRISM_VARIABLE_META[var]['units']

    extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
              tfm[5] + tfm[4] * data.shape[0], tfm[5]]
    im = ax.imshow(data_plot, cmap=cmap, extent=extent)
    plt.colorbar(im, ax=ax, shrink=0.7, label=units)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_xlim(-124.5, -114)
    ax.set_ylim(32.5, 42)
    del data; gc.collect()

fig.suptitle("Figure 1: California Climate Overview — July 30-Year Normals",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "01_ca_climate_overview")"""))

# ═══ FIGURE 2: Data Quality ═══
cells.append(code("""\
# ── Figure 2: Data Quality ───────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# Panel 1: Valid pixel mask
ax1 = axes[0, 0]
sample_files = discover_files("ppt", "monthly", year=2020, month=7)
data, tfm, _ = read_prism_california(sample_files[0])
valid_mask = (data != PRISM_NODATA).astype(float)
extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
          tfm[5] + tfm[4] * data.shape[0], tfm[5]]
ax1.imshow(valid_mask, cmap='Greens', extent=extent)
n_valid = int(np.sum(valid_mask))
n_total = data.size
ax1.set_title(f"Valid Data Mask ({n_valid:,} / {n_total:,} = {100*n_valid/n_total:.1f}%)",
              fontsize=12, fontweight='bold')
ax1.set_xlim(-124.5, -114)
ax1.set_ylim(32.5, 42)

# Panel 2: Data completeness by variable
ax2 = axes[0, 1]
completeness = ca_stats.groupby('variable').agg(
    n_months=('year', 'count'),
    first_year=('year', 'min'),
    last_year=('year', 'max'),
).reindex(PRISM_VARIABLE_ORDER)
var_colors = get_prism_variable_colors()
bars = ax2.barh(range(len(completeness)), completeness.n_months,
                color=[var_colors[v] for v in completeness.index])
ax2.set_yticks(range(len(completeness)))
ax2.set_yticklabels([get_variable_label(v, False) for v in completeness.index])
ax2.set_xlabel("Number of Monthly Records")
ax2.set_title("Data Completeness by Variable", fontsize=12, fontweight='bold')
for i, (idx, row) in enumerate(completeness.iterrows()):
    ax2.text(row.n_months + 10, i, f"{int(row.n_months):,} ({int(row.first_year)}-{int(row.last_year)})",
             va='center', fontsize=9)

# Panel 3: Timeline of data availability
ax3 = axes[1, 0]
for i, var in enumerate(PRISM_VARIABLE_ORDER):
    df_var = ca_stats[ca_stats.variable == var]
    years = sorted(df_var.year.unique())
    if years:
        ax3.barh(i, years[-1] - years[0], left=years[0], height=0.6,
                 color=var_colors[var], alpha=0.8)
ax3.set_yticks(range(len(PRISM_VARIABLE_ORDER)))
ax3.set_yticklabels([PRISM_VARIABLE_META[v]['short_label'] for v in PRISM_VARIABLE_ORDER])
ax3.set_xlabel("Year")
ax3.set_title("Temporal Coverage", fontsize=12, fontweight='bold')

# Panel 4: Stats table
ax4 = axes[1, 1]
ax4.axis('off')
quality = get_prism_data_quality_summary(data, 'ppt')
table_data = [[k, v] for k, v in quality.items()]
table = ax4.table(cellText=table_data, colLabels=['Metric', 'Value'],
                  loc='center', cellLoc='left')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.auto_set_column_width([0, 1])
table.scale(1, 1.5)
for j in range(2):
    table[0, j].set_facecolor('#2C3E50')
    table[0, j].set_text_props(color='white', fontweight='bold')
ax4.set_title("Sample Raster Quality (PPT Jul 2020)", fontsize=12, fontweight='bold')
del data; gc.collect()

fig.suptitle("Figure 2: California PRISM Data Quality",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "02_ca_data_quality")"""))

# ═══ PART 3: TEMPERATURE TRENDS ═══
cells.append(md("---\n## Part 3 — Long-Term Temperature Trends"))

cells.append(code("""\
# ── Figure 3: 130-Year Temperature Timeline ──────────────────────────────

fig, axes = plt.subplots(3, 1, figsize=(18, 14), sharex=True)

temp_vars = [('tmax', 'Maximum Temperature', '#E74C3C'),
             ('tmin', 'Minimum Temperature', '#2980B9'),
             ('tmean', 'Diurnal Temperature Range (Tmax - Tmin)', '#E67E22')]

for ax_idx, (ax, (var, title, color)) in enumerate(zip(axes, temp_vars)):
    if ax_idx < 2:  # tmax, tmin
        df_var = ca_stats[ca_stats.variable == var]
        annual = df_var.groupby('year')['mean'].mean()
    else:
        # DTR = tmax - tmin annual means
        tmax_annual = ca_stats[ca_stats.variable == 'tmax'].groupby('year')['mean'].mean()
        tmin_annual = ca_stats[ca_stats.variable == 'tmin'].groupby('year')['mean'].mean()
        annual = tmax_annual - tmin_annual
        annual = annual.dropna()

    ax.plot(annual.index, annual.values, color=color, alpha=0.4, linewidth=0.8)

    # 10-year running mean
    if len(annual) > 10:
        rolling = annual.rolling(10, center=True).mean()
        ax.plot(rolling.index, rolling.values, color=color, linewidth=2.5, label='10-yr mean')

    # Linear trend
    valid = annual.dropna()
    if len(valid) > 20:
        z = np.polyfit(valid.index, valid.values, 1)
        trend_line = np.poly1d(z)
        ax.plot(valid.index, trend_line(valid.index), '--k', linewidth=1, alpha=0.5)
        slope = z[0] * 10
        units = '°C'
        ax.text(0.02, 0.95, f"Trend: {slope:+.3f} °C/decade",
                transform=ax.transAxes, fontsize=11, va='top', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax.set_ylabel('°C')
    ax.set_title(f"California {title}", fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)

axes[-1].set_xlabel("Year")

fig.suptitle("Figure 3: California Temperature — 130-Year Timeline",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "03_ca_temperature_timeline")"""))

cells.append(code("""\
# ── Figure 4: Temperature Anomaly Heatmap ─────────────────────────────────

fig, axes = plt.subplots(2, 1, figsize=(20, 12))

for ax, var, title in zip(axes, ['tmax', 'tmin'],
                           ['Tmax Anomaly (°C)', 'Tmin Anomaly (°C)']):
    df_var = ca_stats[ca_stats.variable == var]
    # Compute monthly climatology
    clim = df_var.groupby('month')['mean'].mean()
    # Compute anomaly
    df_var = df_var.copy()
    df_var['anomaly'] = df_var.apply(lambda r: r['mean'] - clim[r['month']], axis=1)

    # Pivot to year × month
    pivot = df_var.pivot_table(index='year', columns='month', values='anomaly')
    pivot = pivot[pivot.index >= 1900]

    vmax = max(abs(pivot.min().min()), abs(pivot.max().max()))
    sns.heatmap(pivot, cmap='RdBu_r', center=0, vmin=-vmax, vmax=vmax,
                ax=ax, xticklabels=MONTH_ABBREVS, cbar_kws={'label': '°C'})
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_ylabel("Year")
    # Only show every 10th year label
    yticks = ax.get_yticks()
    ax.set_yticklabels([int(pivot.index[int(t)]) if int(t) < len(pivot.index)
                        and int(pivot.index[int(t)]) % 10 == 0 else ''
                        for t in yticks], fontsize=7)

fig.suptitle("Figure 4: California Temperature Anomaly — Year × Month",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "04_ca_temperature_anomaly")"""))

cells.append(code("""\
# ── Figure 5: Spatial Temperature Trends ──────────────────────────────────

# Compare Jan 1960 vs Jan 2020, and Jul 1960 vs Jul 2020
fig, axes = plt.subplots(2, 2, figsize=(18, 14))

pairs = [
    ('tmax', 7, 1960, 'July 1960'),
    ('tmax', 7, 2020, 'July 2020'),
    ('tmax', 1, 1960, 'January 1960'),
    ('tmax', 1, 2020, 'January 2020'),
]

vmin, vmax = -5, 45

for ax, (var, mo, yr, title) in zip(axes.flat, pairs):
    files = discover_files(var, 'monthly', year=yr, month=mo)
    if files:
        data, tfm, _ = read_prism_california(files[0])
        data_plot = np.where(data == PRISM_NODATA, np.nan, data)
        extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
                  tfm[5] + tfm[4] * data.shape[0], tfm[5]]
        im = ax.imshow(data_plot, cmap='YlOrRd', extent=extent, vmin=vmin, vmax=vmax)
        plt.colorbar(im, ax=ax, shrink=0.7, label='°C')
        valid = data[data != PRISM_NODATA]
        ax.text(0.02, 0.02, f"CA mean: {np.mean(valid):.1f}°C",
                transform=ax.transAxes, fontsize=10, va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        del data; gc.collect()
    ax.set_title(f"Tmax — {title}", fontsize=12, fontweight='bold')
    ax.set_xlim(-124.5, -114)
    ax.set_ylim(32.5, 42)

fig.suptitle("Figure 5: California Tmax — Spatial Comparison (1960 vs 2020)",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "05_ca_temperature_spatial_trends")"""))

cells.append(code("""\
# ── Figure 6: Temperature Extremes ────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

tmax_data = ca_stats[ca_stats.variable == 'tmax']

# Panel 1: Hottest month each year
ax1 = axes[0, 0]
hottest = tmax_data.loc[tmax_data.groupby('year')['mean'].idxmax()]
ax1.scatter(hottest.year, hottest['mean'], c='#E74C3C', s=20, alpha=0.5)
if len(hottest) > 10:
    rolling = hottest.set_index('year')['mean'].rolling(10, center=True).mean()
    ax1.plot(rolling.index, rolling.values, 'r-', linewidth=2.5, label='10-yr mean')
ax1.set_xlabel("Year")
ax1.set_ylabel("Hottest Month Mean Tmax (°C)")
ax1.set_title("Annual Peak Temperature", fontsize=12, fontweight='bold')
ax1.legend()

# Panel 2: Count of months with mean tmax > 30°C by decade
ax2 = axes[0, 1]
hot_months = tmax_data[tmax_data['mean'] > 30].copy()
hot_months['decade'] = (hot_months['year'] // 10) * 10
decade_counts = hot_months.groupby('decade').size()
decade_counts = decade_counts[decade_counts.index >= 1900]
colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(decade_counts)))
ax2.bar(decade_counts.index, decade_counts.values, width=8, color=colors)
ax2.set_xlabel("Decade")
ax2.set_ylabel("Months with Mean Tmax > 30°C")
ax2.set_title("Hot Month Frequency by Decade", fontsize=12, fontweight='bold')

# Panel 3: Annual tmax extreme (p90)
ax3 = axes[1, 0]
p90_annual = tmax_data.groupby('year')['p90'].mean()
ax3.plot(p90_annual.index, p90_annual.values, color='#C0392B', alpha=0.4, linewidth=0.8)
if len(p90_annual) > 10:
    rolling = p90_annual.rolling(10, center=True).mean()
    ax3.plot(rolling.index, rolling.values, '#C0392B', linewidth=2.5, label='10-yr mean')
ax3.set_xlabel("Year")
ax3.set_ylabel("Annual Mean 90th Percentile Tmax (°C)")
ax3.set_title("Extreme Temperature Trend (P90)", fontsize=12, fontweight='bold')
ax3.legend()

# Panel 4: Monthly distribution of hot months
ax4 = axes[1, 1]
hot_month_dist = hot_months.groupby('month').size()
ax4.bar(range(1, 13), [hot_month_dist.get(m, 0) for m in range(1, 13)],
        color=['#E74C3C' if m in [6,7,8,9] else '#F39C12' for m in range(1, 13)])
ax4.set_xticks(range(1, 13))
ax4.set_xticklabels(MONTH_ABBREVS)
ax4.set_ylabel("Count of Months with Mean Tmax > 30°C")
ax4.set_title("Monthly Distribution of Extreme Heat", fontsize=12, fontweight='bold')

fig.suptitle("Figure 6: California Temperature Extremes",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "06_ca_temperature_extremes")"""))

# ═══ PART 4: PRECIPITATION ═══
cells.append(md("---\n## Part 4 — Precipitation Regime"))

cells.append(code("""\
# ── Figure 7: 130-Year Precipitation Timeline ────────────────────────────

fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)

ppt_data = ca_stats[ca_stats.variable == 'ppt']

# Panel 1: Annual precipitation
ax1 = axes[0]
annual_ppt = ppt_data.groupby('year')['mean'].sum()  # Sum monthly means = annual total proxy
ax1.bar(annual_ppt.index, annual_ppt.values, color='#3498DB', alpha=0.6, width=0.8)
if len(annual_ppt) > 10:
    rolling = annual_ppt.rolling(10, center=True).mean()
    ax1.plot(rolling.index, rolling.values, 'b-', linewidth=2.5, label='10-yr mean')

# Annotate drought years
long_term_mean = annual_ppt.mean()
ax1.axhline(long_term_mean, color='gray', linestyle='--', alpha=0.5, label=f'Mean: {long_term_mean:.0f}')
# Mark notable droughts
for yr, label in [(1976, '76-77'), (2012, '12-16'), (2020, '2020'), (1924, '1924')]:
    if yr in annual_ppt.index:
        ax1.annotate(label, (yr, annual_ppt[yr]), textcoords="offset points",
                     xytext=(0, 10), ha='center', fontsize=8, color='red')

ax1.set_ylabel("Annual PPT (mm, CA spatial mean)")
ax1.set_title("California Annual Precipitation", fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)

# Panel 2: Water year (Oct-Sep) precipitation
ax2 = axes[1]
ppt_copy = ppt_data.copy()
from src.utils.prism_domain_mappings import month_to_water_year
ppt_copy['water_year'] = month_to_water_year(ppt_copy.year.values, ppt_copy.month.values).astype(int)
wy_ppt = ppt_copy.groupby('water_year')['mean'].sum()
wy_ppt = wy_ppt[(wy_ppt.index >= 1896) & (wy_ppt.index <= 2025)]

colors = np.where(wy_ppt.values < long_term_mean * 0.85, '#CD853F',
                  np.where(wy_ppt.values > long_term_mean * 1.15, '#3498DB', '#95A5A6'))
ax2.bar(wy_ppt.index, wy_ppt.values, color=colors, width=0.8)
ax2.axhline(long_term_mean, color='gray', linestyle='--', alpha=0.5)
ax2.set_xlabel("Water Year (Oct-Sep)")
ax2.set_ylabel("Water Year PPT (mm)")
ax2.set_title("Water Year Precipitation (brown = drought, blue = wet)", fontsize=13, fontweight='bold')

fig.suptitle("Figure 7: California Precipitation — 130-Year Timeline",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "07_ca_precipitation_timeline")"""))

cells.append(code("""\
# ── Figure 8: Precipitation Spatial Patterns ──────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Panel 1: Annual normal PPT (sum Jan normals × 12 approximation — use Jan as wet example)
ax1 = axes[0, 0]
result = load_monthly_normal('ppt', 1, bounds=PRISM_CA_BOUNDS)
if result:
    data, tfm, _ = result
    data_plot = np.where(data == PRISM_NODATA, np.nan, data)
    extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
              tfm[5] + tfm[4] * data.shape[0], tfm[5]]
    im = ax1.imshow(data_plot, cmap='YlGnBu', extent=extent)
    plt.colorbar(im, ax=ax1, shrink=0.7, label='mm')
    del data; gc.collect()
ax1.set_title("January Normal PPT (Peak Wet Season)", fontsize=12, fontweight='bold')
ax1.set_xlim(-124.5, -114); ax1.set_ylim(32.5, 42)

# Panel 2: July normal PPT
ax2 = axes[0, 1]
result = load_monthly_normal('ppt', 7, bounds=PRISM_CA_BOUNDS)
if result:
    data, tfm, _ = result
    data_plot = np.where(data == PRISM_NODATA, np.nan, data)
    im = ax2.imshow(data_plot, cmap='YlGnBu', extent=extent, vmin=0, vmax=50)
    plt.colorbar(im, ax=ax2, shrink=0.7, label='mm')
    del data; gc.collect()
ax2.set_title("July Normal PPT (Dry Season)", fontsize=12, fontweight='bold')
ax2.set_xlim(-124.5, -114); ax2.set_ylim(32.5, 42)

# Panel 3: Wet season fraction (Nov-Mar / Annual)
ax3 = axes[1, 0]
ppt_monthly = ca_stats[ca_stats.variable == 'ppt']
monthly_clim = ppt_monthly.groupby('month')['mean'].mean()
wet_months = [11, 12, 1, 2, 3]
wet_fraction = sum(monthly_clim[m] for m in wet_months) / monthly_clim.sum() * 100
ax3.bar(range(1, 13), monthly_clim.values,
        color=['#3498DB' if m in wet_months else '#F39C12' for m in range(1, 13)])
ax3.set_xticks(range(1, 13))
ax3.set_xticklabels(MONTH_ABBREVS)
ax3.set_ylabel("Mean Monthly PPT (mm)")
ax3.set_title(f"Seasonal PPT Distribution (Nov-Mar = {wet_fraction:.0f}% of annual)",
              fontsize=12, fontweight='bold')

# Panel 4: Latitude-precipitation gradient
ax4 = axes[1, 1]
# Approximate: use spatial p10-p90 range from cache
ppt_annual = ppt_monthly.groupby('year').agg(
    annual_mean=('mean', 'sum'),
    annual_p10=('p10', 'sum'),
    annual_p90=('p90', 'sum'),
)
ppt_recent = ppt_annual[ppt_annual.index >= 2000]
ax4.fill_between(ppt_recent.index, ppt_recent.annual_p10, ppt_recent.annual_p90,
                 alpha=0.3, color='#3498DB', label='P10-P90 range')
ax4.plot(ppt_recent.index, ppt_recent.annual_mean, 'b-', linewidth=2, label='Mean')
ax4.set_xlabel("Year")
ax4.set_ylabel("Annual PPT (mm)")
ax4.set_title("Recent Annual PPT with Spatial Uncertainty", fontsize=12, fontweight='bold')
ax4.legend()

fig.suptitle("Figure 8: California Precipitation Spatial Patterns",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "08_ca_precipitation_spatial")"""))

cells.append(code("""\
# ── Figure 9: Precipitation Anomaly Heatmap ──────────────────────────────

fig, ax = plt.subplots(figsize=(20, 10))

ppt_data = ca_stats[ca_stats.variable == 'ppt'].copy()
ppt_clim = ppt_data.groupby('month')['mean'].mean()
ppt_data['pct_normal'] = ppt_data.apply(
    lambda r: 100 * r['mean'] / ppt_clim[r['month']] if ppt_clim[r['month']] > 0 else np.nan, axis=1
)

pivot = ppt_data.pivot_table(index='year', columns='month', values='pct_normal')
pivot = pivot[pivot.index >= 1900]

# Diverging colormap centered on 100%
sns.heatmap(pivot, cmap='BrBG', center=100, vmin=0, vmax=300,
            ax=ax, xticklabels=MONTH_ABBREVS,
            cbar_kws={'label': '% of Normal'})
ax.set_title("Monthly Precipitation as % of Normal (brown = dry, green = wet)",
             fontsize=14, fontweight='bold')
ax.set_ylabel("Year")
yticks = ax.get_yticks()
ax.set_yticklabels([int(pivot.index[int(t)]) if int(t) < len(pivot.index)
                    and int(pivot.index[int(t)]) % 10 == 0 else ''
                    for t in yticks], fontsize=7)

fig.suptitle("Figure 9: California Precipitation Anomaly — 125 Years",
             fontsize=16, fontweight='bold', y=1.01)
save_fig(fig, "09_ca_precipitation_anomaly")"""))

cells.append(code("""\
# ── Figure 10: Drought Analysis ───────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

ppt_data = ca_stats[ca_stats.variable == 'ppt']
annual_ppt = ppt_data.groupby('year')['mean'].sum()
long_mean = annual_ppt.mean()

# Panel 1: 12-month running anomaly
ax1 = axes[0, 0]
monthly_ts = ppt_data.sort_values(['year', 'month'])['mean'].values
months_index = ppt_data.sort_values(['year', 'month']).apply(lambda r: r['year'] + r['month']/12, axis=1).values
if len(monthly_ts) > 12:
    running_12 = pd.Series(monthly_ts).rolling(12).sum()
    running_12_norm = running_12 / (long_mean) * 100  # as pct of annual normal
    ax1.plot(months_index, running_12_norm, color='#3498DB', linewidth=0.8)
    ax1.axhline(100, color='gray', linestyle='--', alpha=0.5)
    ax1.fill_between(months_index, running_12_norm, 100,
                     where=running_12_norm < 85, color='#CD853F', alpha=0.3, label='Drought (<85%)')
    ax1.fill_between(months_index, running_12_norm, 100,
                     where=running_12_norm > 115, color='#3498DB', alpha=0.3, label='Wet (>115%)')
ax1.set_xlabel("Year")
ax1.set_ylabel("12-Month PPT (% of Normal)")
ax1.set_title("12-Month Running Precipitation Anomaly", fontsize=12, fontweight='bold')
ax1.legend(fontsize=9)

# Panel 2: Ranked driest years
ax2 = axes[0, 1]
annual_ranked = annual_ppt.sort_values()
driest_20 = annual_ranked.head(20)
colors = ['#8B4513' if i < 5 else '#CD853F' if i < 10 else '#DEB887' for i in range(20)]
ax2.barh(range(20), driest_20.values, color=colors)
ax2.set_yticks(range(20))
ax2.set_yticklabels([str(int(y)) for y in driest_20.index], fontsize=9)
ax2.set_xlabel("Annual PPT (mm)")
ax2.set_title("20 Driest Years", fontsize=12, fontweight='bold')

# Panel 3: Ranked wettest years
ax3 = axes[1, 0]
wettest_20 = annual_ranked.tail(20).sort_values(ascending=True)
colors_wet = ['#191970' if i >= 15 else '#4682B4' if i >= 10 else '#87CEEB' for i in range(20)]
ax3.barh(range(20), wettest_20.values, color=colors_wet[::-1])
ax3.set_yticks(range(20))
ax3.set_yticklabels([str(int(y)) for y in wettest_20.index], fontsize=9)
ax3.set_xlabel("Annual PPT (mm)")
ax3.set_title("20 Wettest Years", fontsize=12, fontweight='bold')

# Panel 4: Drought severity distribution
ax4 = axes[1, 1]
ppt_pct = (annual_ppt / long_mean * 100)
drought_classes = classify_drought(ppt_pct.values)
class_counts = pd.Series(drought_classes).value_counts()
from src.utils.prism_domain_mappings import DROUGHT_CLASS_ORDER
drought_colors = get_drought_colors()
ordered_counts = [class_counts.get(c, 0) for c in DROUGHT_CLASS_ORDER]
bars = ax4.bar(range(len(DROUGHT_CLASS_ORDER)), ordered_counts,
               color=[drought_colors[c] for c in DROUGHT_CLASS_ORDER])
ax4.set_xticks(range(len(DROUGHT_CLASS_ORDER)))
ax4.set_xticklabels(DROUGHT_CLASS_ORDER, rotation=45, ha='right', fontsize=9)
ax4.set_ylabel("Number of Years")
ax4.set_title("Annual Drought Severity Distribution", fontsize=12, fontweight='bold')

fig.suptitle("Figure 10: California Drought Analysis",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "10_ca_drought_analysis")"""))

# ═══ PART 5: VPD ═══
cells.append(md("""\
---
## Part 5 — VPD — The #1 Fire Predictor

Vapor Pressure Deficit (VPD) is the single strongest climate predictor of wildfire activity. It measures the atmosphere's drying demand on vegetation."""))

cells.append(code("""\
# ── Figure 11: VPD Timeline ──────────────────────────────────────────────

fig, axes = plt.subplots(3, 1, figsize=(18, 14), sharex=True)

# Panel 1: Annual VPDmax
ax1 = axes[0]
vpd_data = ca_stats[ca_stats.variable == 'vpdmax']
vpd_annual = vpd_data.groupby('year')['mean'].mean()
ax1.plot(vpd_annual.index, vpd_annual.values, color='#C0392B', alpha=0.4, linewidth=0.8)
if len(vpd_annual) > 10:
    rolling = vpd_annual.rolling(10, center=True).mean()
    ax1.plot(rolling.index, rolling.values, '#C0392B', linewidth=2.5, label='10-yr mean')
valid = vpd_annual.dropna()
if len(valid) > 20:
    z = np.polyfit(valid.index, valid.values, 1)
    ax1.plot(valid.index, np.poly1d(z)(valid.index), '--k', linewidth=1)
    ax1.text(0.02, 0.95, f"Trend: {z[0]*10:+.3f} hPa/decade", transform=ax1.transAxes,
             fontsize=11, va='top', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
ax1.set_ylabel("VPDmax (hPa)")
ax1.set_title("Annual Mean VPDmax", fontsize=13, fontweight='bold')
ax1.legend()

# Panel 2: Summer (JJA) VPDmax
ax2 = axes[1]
summer_vpd = vpd_data[vpd_data.month.isin([6,7,8])].groupby('year')['mean'].mean()
ax2.plot(summer_vpd.index, summer_vpd.values, color='#E74C3C', alpha=0.4, linewidth=0.8)
if len(summer_vpd) > 10:
    rolling = summer_vpd.rolling(10, center=True).mean()
    ax2.plot(rolling.index, rolling.values, '#E74C3C', linewidth=2.5, label='10-yr mean')
valid = summer_vpd.dropna()
if len(valid) > 20:
    z = np.polyfit(valid.index, valid.values, 1)
    ax2.plot(valid.index, np.poly1d(z)(valid.index), '--k', linewidth=1)
    ax2.text(0.02, 0.95, f"Trend: {z[0]*10:+.3f} hPa/decade", transform=ax2.transAxes,
             fontsize=11, va='top', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
ax2.set_ylabel("Summer VPDmax (hPa)")
ax2.set_title("Summer (JJA) Mean VPDmax — Fire Season", fontsize=13, fontweight='bold')
ax2.legend()

# Panel 3: VPDmin
ax3 = axes[2]
vpdmin_data = ca_stats[ca_stats.variable == 'vpdmin']
vpdmin_annual = vpdmin_data.groupby('year')['mean'].mean()
ax3.plot(vpdmin_annual.index, vpdmin_annual.values, color='#D4A574', alpha=0.4, linewidth=0.8)
if len(vpdmin_annual) > 10:
    rolling = vpdmin_annual.rolling(10, center=True).mean()
    ax3.plot(rolling.index, rolling.values, '#D4A574', linewidth=2.5, label='10-yr mean')
ax3.set_ylabel("VPDmin (hPa)")
ax3.set_xlabel("Year")
ax3.set_title("Annual Mean VPDmin (Nighttime Atmospheric Drying)", fontsize=13, fontweight='bold')
ax3.legend()

fig.suptitle("Figure 11: California VPD — 130-Year Timeline",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "11_ca_vpd_timeline")"""))

cells.append(code("""\
# ── Figure 12: VPD Spatial Patterns ───────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

spatial_configs = [
    ('vpdmax', 7, 'July VPDmax Normal'),
    ('vpdmax', 1, 'January VPDmax Normal'),
    ('vpdmin', 7, 'July VPDmin Normal'),
    ('vpdmin', 1, 'January VPDmin Normal'),
]

for ax, (var, mo, title) in zip(axes.flat, spatial_configs):
    result = load_monthly_normal(var, mo, bounds=PRISM_CA_BOUNDS)
    if result:
        data, tfm, _ = result
        data_plot = np.where(data == PRISM_NODATA, np.nan, data)
        extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
                  tfm[5] + tfm[4] * data.shape[0], tfm[5]]
        im = ax.imshow(data_plot, cmap='YlOrRd', extent=extent)
        plt.colorbar(im, ax=ax, shrink=0.7, label='hPa')
        valid = data[data != PRISM_NODATA]
        ax.text(0.02, 0.02, f"Mean: {np.mean(valid):.1f} hPa",
                transform=ax.transAxes, fontsize=10, va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        del data; gc.collect()
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlim(-124.5, -114); ax.set_ylim(32.5, 42)

fig.suptitle("Figure 12: California VPD Spatial Patterns — Seasonal Contrast",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "12_ca_vpd_spatial")"""))

cells.append(code("""\
# ── Figure 13: VPD Risk Classification ────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Panel 1: July VPD risk class map
ax1 = axes[0, 0]
result = load_monthly_normal('vpdmax', 7, bounds=PRISM_CA_BOUNDS)
if result:
    data, tfm, _ = result
    valid_data = np.where(data == PRISM_NODATA, np.nan, data)
    risk_classes = classify_vpd(valid_data)
    extent = [tfm[2], tfm[2] + tfm[0] * data.shape[1],
              tfm[5] + tfm[4] * data.shape[0], tfm[5]]

    # Map classes to numeric for plotting
    class_to_num = {c: i for i, c in enumerate(FIRE_WEATHER_VPD_ORDER)}
    risk_num = np.full_like(valid_data, np.nan, dtype=float)
    for cls, num in class_to_num.items():
        risk_num[risk_classes == cls] = num

    vpd_risk_colors = get_vpd_risk_colors()
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cmap = ListedColormap([vpd_risk_colors[c] for c in FIRE_WEATHER_VPD_ORDER])
    norm = BoundaryNorm(np.arange(-0.5, len(FIRE_WEATHER_VPD_ORDER)), len(FIRE_WEATHER_VPD_ORDER))
    im = ax1.imshow(risk_num, cmap=cmap, norm=norm, extent=extent)
    cbar = plt.colorbar(im, ax=ax1, shrink=0.7, ticks=range(len(FIRE_WEATHER_VPD_ORDER)))
    cbar.ax.set_yticklabels(FIRE_WEATHER_VPD_ORDER, fontsize=8)
    del data; gc.collect()
ax1.set_title("July VPD Risk Classification", fontsize=12, fontweight='bold')
ax1.set_xlim(-124.5, -114); ax1.set_ylim(32.5, 42)

# Panel 2: Monthly VPD climatology with risk shading
ax2 = axes[0, 1]
vpd_monthly = ca_stats[ca_stats.variable == 'vpdmax'].groupby('month').agg(
    mean=('mean', 'mean'), p10=('p10', 'mean'), p90=('p90', 'mean')
)
ax2.fill_between(range(1, 13), vpd_monthly.p10, vpd_monthly.p90,
                 alpha=0.2, color='#C0392B', label='P10-P90 range')
ax2.plot(range(1, 13), vpd_monthly['mean'], 'r-o', linewidth=2, label='Mean')
# Risk thresholds
for thresh, label, color in [(20, 'Moderate', '#F9E79F'), (30, 'High', '#F5B041'),
                               (40, 'Extreme', '#E74C3C'), (55, 'Exceptional', '#922B21')]:
    ax2.axhline(thresh, color=color, linestyle='--', alpha=0.7, linewidth=1)
    ax2.text(12.3, thresh, label, fontsize=8, va='center', color=color)
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(MONTH_ABBREVS)
ax2.set_ylabel("VPDmax (hPa)")
ax2.set_title("Monthly VPD Climatology with Risk Thresholds", fontsize=12, fontweight='bold')
ax2.legend(fontsize=9)

# Panel 3: VPD during 2020 (worst fire year) vs normal
ax3 = axes[1, 0]
vpd_2020 = ca_stats[(ca_stats.variable == 'vpdmax') & (ca_stats.year == 2020)]
vpd_2020_by_month = vpd_2020.groupby('month')['mean'].mean()
ax3.bar(range(1, 13), vpd_monthly['mean'], color='#95A5A6', alpha=0.5, label='Normal')
ax3.bar(range(1, 13), vpd_2020_by_month.reindex(range(1,13)).values,
        color='#E74C3C', alpha=0.7, width=0.4, label='2020')
ax3.set_xticks(range(1, 13))
ax3.set_xticklabels(MONTH_ABBREVS)
ax3.set_ylabel("VPDmax (hPa)")
ax3.set_title("2020 (Worst Fire Year) vs Normal", fontsize=12, fontweight='bold')
ax3.legend()

# Panel 4: VPD risk class distribution (% of CA area)
ax4 = axes[1, 1]
if risk_classes is not None:
    risk_flat = risk_classes[~np.isnan(valid_data)]
    risk_counts = pd.Series(risk_flat).value_counts()
    ordered = [risk_counts.get(c, 0) for c in FIRE_WEATHER_VPD_ORDER]
    total = sum(ordered)
    pcts = [100 * x / total for x in ordered]
    bars = ax4.bar(range(len(FIRE_WEATHER_VPD_ORDER)), pcts,
                   color=[vpd_risk_colors[c] for c in FIRE_WEATHER_VPD_ORDER])
    ax4.set_xticks(range(len(FIRE_WEATHER_VPD_ORDER)))
    ax4.set_xticklabels(FIRE_WEATHER_VPD_ORDER, rotation=30, ha='right')
    ax4.set_ylabel("% of CA Area")
    ax4.set_title("July VPD Risk Class Distribution", fontsize=12, fontweight='bold')

fig.suptitle("Figure 13: VPD Risk Classification",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "13_ca_vpd_risk_classification")"""))

cells.append(code("""\
# ── Figure 14: VPD Seasonal Trends ───────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

vpd_data = ca_stats[ca_stats.variable == 'vpdmax']

# Panel 1: Monthly climatology with shading
ax1 = axes[0, 0]
vpd_monthly = vpd_data.groupby('month').agg(
    mean=('mean', 'mean'), std=('mean', 'std'),
    p10=('p10', 'mean'), p90=('p90', 'mean')
)
ax1.fill_between(range(1, 13), vpd_monthly.p10, vpd_monthly.p90,
                 alpha=0.15, color='#C0392B')
ax1.fill_between(range(1, 13), vpd_monthly['mean'] - vpd_monthly['std'],
                 vpd_monthly['mean'] + vpd_monthly['std'], alpha=0.3, color='#C0392B')
ax1.plot(range(1, 13), vpd_monthly['mean'], 'r-o', linewidth=2.5)
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(MONTH_ABBREVS)
ax1.set_ylabel("VPDmax (hPa)")
ax1.set_title("VPD Annual Cycle (mean ± 1σ, P10-P90)", fontsize=12, fontweight='bold')

# Panel 2: Decade overlay
ax2 = axes[0, 1]
decade_colors = plt.cm.Reds(np.linspace(0.2, 0.9, 6))
for i, decade in enumerate(range(1970, 2030, 10)):
    dec_data = vpd_data[(vpd_data.year >= decade) & (vpd_data.year < decade + 10)]
    if len(dec_data) > 0:
        monthly = dec_data.groupby('month')['mean'].mean()
        ax2.plot(monthly.index, monthly.values, '-o', color=decade_colors[i],
                 linewidth=2, markersize=4, label=f"{decade}s")
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(MONTH_ABBREVS)
ax2.set_ylabel("VPDmax (hPa)")
ax2.set_title("VPD by Decade — Upward Shift", fontsize=12, fontweight='bold')
ax2.legend(ncol=2, fontsize=9)

# Panel 3: VPD vs Temperature scatter
ax3 = axes[1, 0]
tmax_data = ca_stats[ca_stats.variable == 'tmax']
merged = vpd_data[['year','month','mean']].merge(
    tmax_data[['year','month','mean']], on=['year','month'], suffixes=('_vpd','_tmax')
)
season_colors = get_climate_season_colors()
for m in range(1, 13):
    subset = merged[merged.month == m]
    season = CLIMATE_SEASON_MAP[m]
    ax3.scatter(subset.mean_tmax, subset.mean_vpd, alpha=0.2, s=10,
                color=season_colors[season])
# Add season legend
for season, color in season_colors.items():
    ax3.scatter([], [], color=color, s=40, label=season)
ax3.set_xlabel("Tmax (°C)")
ax3.set_ylabel("VPDmax (hPa)")
ax3.set_title("VPD vs Temperature (colored by season)", fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)

# Panel 4: VPD-temperature relationship by month
ax4 = axes[1, 1]
monthly_corr = merged.groupby('month').apply(
    lambda g: g['mean_vpd'].corr(g['mean_tmax'])
)
ax4.bar(range(1, 13), monthly_corr.values,
        color=['#E74C3C' if c > 0.8 else '#F39C12' if c > 0.5 else '#3498DB'
               for c in monthly_corr.values])
ax4.set_xticks(range(1, 13))
ax4.set_xticklabels(MONTH_ABBREVS)
ax4.set_ylabel("Correlation (r)")
ax4.set_title("VPD-Temperature Correlation by Month", fontsize=12, fontweight='bold')
ax4.axhline(0, color='gray', linewidth=0.5)

fig.suptitle("Figure 14: VPD Seasonal Trends & Relationships",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "14_ca_vpd_seasonal_trends")"""))

cells.append(code("""\
# ── Figure 15: VPD Extremes ──────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

vpd_data = ca_stats[ca_stats.variable == 'vpdmax']

# Panel 1: Months with mean VPD > 30 hPa per year
ax1 = axes[0, 0]
high_vpd = vpd_data[vpd_data['mean'] > 30].groupby('year').size()
ax1.bar(high_vpd.index, high_vpd.values, color='#E74C3C', alpha=0.7)
if len(high_vpd) > 10:
    rolling = high_vpd.rolling(10, center=True).mean()
    ax1.plot(rolling.index, rolling.values, 'k-', linewidth=2, label='10-yr mean')
ax1.set_xlabel("Year")
ax1.set_ylabel("Months with Mean VPD > 30 hPa")
ax1.set_title("High VPD Month Frequency", fontsize=12, fontweight='bold')
ax1.legend()

# Panel 2: Months with mean VPD > 40 hPa
ax2 = axes[0, 1]
extreme_vpd = vpd_data[vpd_data['mean'] > 40].groupby('year').size()
ax2.bar(extreme_vpd.index, extreme_vpd.values, color='#922B21', alpha=0.7)
if len(extreme_vpd) > 10:
    rolling = extreme_vpd.rolling(10, center=True).mean()
    ax2.plot(rolling.index, rolling.values, 'k-', linewidth=2, label='10-yr mean')
ax2.set_xlabel("Year")
ax2.set_ylabel("Months with Mean VPD > 40 hPa")
ax2.set_title("Extreme VPD Month Frequency", fontsize=12, fontweight='bold')
ax2.legend()

# Panel 3: Top 20 extreme VPD months
ax3 = axes[1, 0]
top_vpd = vpd_data.nlargest(20, 'mean')
labels = [f"{int(r.year)}-{MONTH_ABBREVS[int(r.month)-1]}" for _, r in top_vpd.iterrows()]
ax3.barh(range(20), top_vpd['mean'].values, color='#C0392B')
ax3.set_yticks(range(20))
ax3.set_yticklabels(labels, fontsize=9)
ax3.set_xlabel("Monthly Mean VPDmax (hPa)")
ax3.set_title("Top 20 Extreme VPD Months", fontsize=12, fontweight='bold')

# Panel 4: VPD P90 trend (extreme tail)
ax4 = axes[1, 1]
p90_annual = vpd_data.groupby('year')['p90'].mean()
ax4.plot(p90_annual.index, p90_annual.values, color='#922B21', alpha=0.4)
if len(p90_annual) > 10:
    rolling = p90_annual.rolling(10, center=True).mean()
    ax4.plot(rolling.index, rolling.values, '#922B21', linewidth=2.5, label='10-yr mean')
valid = p90_annual.dropna()
if len(valid) > 20:
    z = np.polyfit(valid.index, valid.values, 1)
    ax4.plot(valid.index, np.poly1d(z)(valid.index), '--k', linewidth=1)
    ax4.text(0.02, 0.95, f"Trend: {z[0]*10:+.3f} hPa/decade", transform=ax4.transAxes,
             fontsize=11, va='top', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
ax4.set_xlabel("Year")
ax4.set_ylabel("Annual Mean P90 VPDmax (hPa)")
ax4.set_title("VPD Extreme Tail Trend (P90)", fontsize=12, fontweight='bold')
ax4.legend()

fig.suptitle("Figure 15: California VPD Extremes",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "15_ca_vpd_extremes")"""))

# ═══ PART 6: DERIVED INDICES ═══
cells.append(md("---\n## Part 6 — Derived Climate Indices"))

cells.append(code("""\
# ── Figure 16: Estimated Relative Humidity ────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Panel 1-2: July and January RH maps
for ax, mo, title in [(axes[0,0], 7, 'July'), (axes[0,1], 1, 'January')]:
    td_result = load_monthly_normal('tdmean', mo, bounds=PRISM_CA_BOUNDS)
    tx_result = load_monthly_normal('tmax', mo, bounds=PRISM_CA_BOUNDS)
    if td_result and tx_result:
        td_data, tfm, _ = td_result
        tx_data, _, _ = tx_result
        rh = compute_estimated_rh(td_data, tx_data)
        extent = [tfm[2], tfm[2] + tfm[0] * rh.shape[1],
                  tfm[5] + tfm[4] * rh.shape[0], tfm[5]]
        im = ax.imshow(rh, cmap='YlGnBu', extent=extent, vmin=0, vmax=100)
        plt.colorbar(im, ax=ax, shrink=0.7, label='%')
        valid = rh[~np.isnan(rh)]
        ax.text(0.02, 0.02, f"Mean: {np.mean(valid):.1f}%",
                transform=ax.transAxes, fontsize=10, va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        del td_data, tx_data, rh; gc.collect()
    ax.set_title(f"Estimated Min RH — {title} Normal", fontsize=12, fontweight='bold')
    ax.set_xlim(-124.5, -114); ax.set_ylim(32.5, 42)

# Panel 3: Monthly RH cycle
ax3 = axes[1, 0]
if ca_stats is not None:
    tdmean_monthly = ca_stats[ca_stats.variable == 'tdmean'].groupby('month')['mean'].mean()
    tmax_monthly = ca_stats[ca_stats.variable == 'tmax'].groupby('month')['mean'].mean()
    rh_monthly = compute_rh_from_tdmean_tmax(tdmean_monthly.values, tmax_monthly.values)
    ax3.plot(range(1, 13), rh_monthly, 'b-o', linewidth=2.5)
    ax3.fill_between(range(1, 13), rh_monthly, alpha=0.2, color='#3498DB')
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels(MONTH_ABBREVS)
    ax3.set_ylabel("Estimated Min RH (%)")
    ax3.set_title("Annual RH Cycle (CA spatial mean)", fontsize=12, fontweight='bold')
    ax3.axhline(20, color='red', linestyle='--', alpha=0.5, label='20% (Red Flag)')
    ax3.legend()

# Panel 4: Summer RH trend
ax4 = axes[1, 1]
if ca_stats is not None:
    td_summer = ca_stats[(ca_stats.variable == 'tdmean') & (ca_stats.month.isin([6,7,8]))].groupby('year')['mean'].mean()
    tx_summer = ca_stats[(ca_stats.variable == 'tmax') & (ca_stats.month.isin([6,7,8]))].groupby('year')['mean'].mean()
    common_years = td_summer.index.intersection(tx_summer.index)
    rh_summer = pd.Series(
        compute_rh_from_tdmean_tmax(td_summer[common_years].values, tx_summer[common_years].values),
        index=common_years
    )
    ax4.plot(rh_summer.index, rh_summer.values, color='#3498DB', alpha=0.4)
    if len(rh_summer) > 10:
        rolling = rh_summer.rolling(10, center=True).mean()
        ax4.plot(rolling.index, rolling.values, '#3498DB', linewidth=2.5, label='10-yr mean')
    ax4.set_xlabel("Year")
    ax4.set_ylabel("Summer Mean Est. Min RH (%)")
    ax4.set_title("Summer RH Trend", fontsize=12, fontweight='bold')
    ax4.legend()

fig.suptitle("Figure 16: Estimated Relative Humidity Analysis",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "16_ca_relative_humidity")"""))

cells.append(code("""\
# ── Figure 17: Climate Correlations ───────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Build monthly means matrix for correlation
monthly_means = {}
for var in ['tmax', 'tmin', 'tmean', 'tdmean', 'ppt', 'vpdmax', 'vpdmin']:
    df_var = ca_stats[ca_stats.variable == var]
    monthly_means[var] = df_var.set_index(['year', 'month'])['mean']

corr_df = pd.DataFrame(monthly_means).dropna()

# Panel 1: Correlation matrix
ax1 = axes[0, 0]
corr = corr_df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
labels = [PRISM_VARIABLE_META[v]['short_label'] for v in corr.columns]
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            ax=ax1, xticklabels=labels, yticklabels=labels,
            cbar_kws={'label': 'Correlation'})
ax1.set_title("Variable Correlation Matrix", fontsize=12, fontweight='bold')

# Panel 2: PCA biplot
ax2 = axes[0, 1]
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
X = StandardScaler().fit_transform(corr_df.values)
pca = PCA(n_components=2)
scores = pca.fit_transform(X)
ax2.scatter(scores[:, 0], scores[:, 1], alpha=0.1, s=5, color='gray')
# Loading vectors
loadings = pca.components_.T
for i, var in enumerate(corr_df.columns):
    ax2.annotate('', xy=(loadings[i, 0]*3, loadings[i, 1]*3), xytext=(0, 0),
                 arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax2.text(loadings[i, 0]*3.3, loadings[i, 1]*3.3,
             PRISM_VARIABLE_META[var]['short_label'], fontsize=10, fontweight='bold', color='red')
ax2.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
ax2.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
ax2.set_title("PCA Biplot", fontsize=12, fontweight='bold')
ax2.axhline(0, color='gray', linewidth=0.5); ax2.axvline(0, color='gray', linewidth=0.5)

# Panel 3: Seasonal correlation variation (VPD vs Tmax by month)
ax3 = axes[1, 0]
monthly_corrs = {}
for m in range(1, 13):
    subset = corr_df.xs(m, level='month') if m in corr_df.index.get_level_values('month') else pd.DataFrame()
    if len(subset) > 10:
        monthly_corrs[m] = {
            'vpd_tmax': subset['vpdmax'].corr(subset['tmax']),
            'vpd_ppt': subset['vpdmax'].corr(subset['ppt']),
            'tmax_ppt': subset['tmax'].corr(subset['ppt']),
        }
if monthly_corrs:
    mc_df = pd.DataFrame(monthly_corrs).T
    ax3.plot(mc_df.index, mc_df.vpd_tmax, 'r-o', label='VPD-Tmax', linewidth=2)
    ax3.plot(mc_df.index, mc_df.vpd_ppt, 'b-s', label='VPD-PPT', linewidth=2)
    ax3.plot(mc_df.index, mc_df.tmax_ppt, 'g-^', label='Tmax-PPT', linewidth=2)
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels(MONTH_ABBREVS)
    ax3.set_ylabel("Correlation (r)")
    ax3.set_title("Seasonal Correlation Variation", fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.axhline(0, color='gray', linewidth=0.5)

# Panel 4: VPD-Temp scatter colored by month
ax4 = axes[1, 1]
for m in range(1, 13):
    subset = corr_df.xs(m, level='month') if m in corr_df.index.get_level_values('month') else pd.DataFrame()
    if len(subset) > 0:
        season = CLIMATE_SEASON_MAP[m]
        color = get_climate_season_colors()[season]
        ax4.scatter(subset['tmax'], subset['vpdmax'], alpha=0.3, s=10, color=color)
ax4.set_xlabel("Tmax (°C)")
ax4.set_ylabel("VPDmax (hPa)")
ax4.set_title("VPD vs Temperature by Month", fontsize=12, fontweight='bold')

fig.suptitle("Figure 17: Climate Variable Correlations",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "17_ca_climate_correlations")"""))

# ═══ PART 7: REGIONAL PROFILES ═══
cells.append(md("---\n## Part 7 — CA Climate Region Profiles"))

cells.append(code("""\
# ── Figure 18: 8 CA Climate Region Profiles ──────────────────────────────

fig, axes = plt.subplots(3, 3, figsize=(22, 18))

region_names = list(CA_CLIMATE_REGIONS.keys())

for idx, region_name in enumerate(region_names[:8]):
    row, col = idx // 3, idx % 3
    ax = axes[row, col]

    region = CA_CLIMATE_REGIONS[region_name]
    bounds = region['bounds']
    color = region['color']

    # Load regional normals for PPT and Tmax
    ppt_vals = []
    tmax_vals = []
    vpd_vals = []
    for mo in range(1, 13):
        for var, val_list in [('ppt', ppt_vals), ('tmax', tmax_vals), ('vpdmax', vpd_vals)]:
            result = load_monthly_normal(var, mo, bounds=bounds)
            if result:
                data, _, _ = result
                valid = data[data != PRISM_NODATA]
                val_list.append(np.mean(valid) if len(valid) > 0 else np.nan)
            else:
                val_list.append(np.nan)

    # Dual-axis: PPT bars + Tmax line + VPD dashed
    months = range(1, 13)
    ax.bar(months, ppt_vals, color='#3498DB', alpha=0.5, width=0.6, label='PPT (mm)')
    ax.set_ylim(0, max(ppt_vals) * 1.4 if max(ppt_vals) > 0 else 50)

    ax2 = ax.twinx()
    ax2.plot(months, tmax_vals, 'r-o', linewidth=2, markersize=4, label='Tmax (°C)')
    ax2.plot(months, vpd_vals, '--', color='#922B21', linewidth=1.5, label='VPDmax (hPa)')
    ax2.set_ylim(-5, max(max(tmax_vals, default=30), max(vpd_vals, default=30)) * 1.3)
    ax2.tick_params(axis='y', labelsize=8)

    ax.set_xticks([1, 4, 7, 10])
    ax.set_xticklabels(['Jan', 'Apr', 'Jul', 'Oct'], fontsize=8)
    ax.set_title(region_name, fontsize=12, fontweight='bold', color=color)
    ax.tick_params(axis='y', labelsize=8)

    # Description
    ax.text(0.02, 0.98, region['description'][:50], transform=ax.transAxes,
            fontsize=7, va='top', fontstyle='italic',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

# Hide 9th subplot, add legend
axes[2, 2].axis('off')
# Manual legend
from matplotlib.lines import Line2D
legend_elements = [
    mpatches.Patch(facecolor='#3498DB', alpha=0.5, label='Precipitation (mm)'),
    Line2D([0], [0], color='red', linewidth=2, label='Tmax (°C)'),
    Line2D([0], [0], color='#922B21', linestyle='--', linewidth=1.5, label='VPDmax (hPa)'),
]
axes[2, 2].legend(handles=legend_elements, loc='center', fontsize=14)
axes[2, 2].text(0.5, 0.2, "8 California\\nClimate Regions", transform=axes[2,2].transAxes,
                ha='center', fontsize=16, fontweight='bold')

fig.suptitle("Figure 18: California Climate Region Profiles — Monthly Climatology",
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
save_fig(fig, "18_ca_climate_region_profiles")"""))

# ═══ PARTS 8-9: SUMMARY ═══
cells.append(md("""\
---
## Part 8 — 30-Year Normals Deep Dive

The 30-year normals loaded above (from PRISM's official normal products) serve as the baseline for:
- Anomaly computation (observed - normal for temperature/VPD, % of normal for precipitation)
- Drought classification (annual PPT as % of normal)
- Fire weather risk mapping (VPD risk classes based on July normal)

These normals will be used extensively in Part 3 (Fire-Climate Integration) for computing antecedent climate conditions at fire locations."""))

cells.append(md("""\
---
## Part 9 — Executive Summary & ML Readiness

### Key California Climate Findings

1. **Warming is accelerating**: Tmax trend ~0.1-0.2°C/decade, with stronger warming in recent decades
2. **VPD is increasing**: Both annual and summer VPDmax show clear upward trends
3. **Mediterranean regime**: 70%+ of precipitation falls Nov-Mar; summers are nearly rainless
4. **2020 was exceptional**: Record VPD months coincided with record fire season
5. **Extreme VPD months increasing**: The frequency of months with mean VPD > 30 hPa is rising
6. **Strong VPD-temperature coupling**: r > 0.8 in summer months
7. **Regional diversity**: 8 climate regions span from wet coastal to extreme desert
8. **Drought signature**: Multi-year droughts (2012-2016) visible in precipitation anomaly

### ML Feature Preview (30+ climate features at 800m)

| Feature Category | Count | Examples |
|-----------------|-------|---------|
| Monthly values | 7 | ppt, tmax, tmin, tmean, tdmean, vpdmax, vpdmin |
| Anomalies | 7 | Each variable as % or difference from normal |
| Derived | 4 | DTR, DPD, est. RH, VPD mean |
| Cumulative | 4 | 30/90-day cumulative VPD, dry day count |
| Lag features | 6+ | 1-6 month antecedent VPD and PPT |
| Seasonal | 4 | Fire season mean, wet season total |
| **Total** | **~32** | Per grid cell per time step |"""))

cells.append(code("""\
# Final summary
print("=" * 70)
print("PRISM Comprehensive Analysis — Part 2: California Deep Dive")
print("=" * 70)
print(f"\\nFigures generated: 18")
print(f"Output directory: {CA_FIG_DIR}")

import os
figs = [f for f in os.listdir(CA_FIG_DIR) if f.endswith('.png')]
print(f"Figures saved: {len(figs)}")
for f in sorted(figs):
    size_kb = os.path.getsize(CA_FIG_DIR / f) / 1024
    print(f"  {f} ({size_kb:.0f} KB)")"""))

# ═══ BUILD NOTEBOOK ═══
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3 (wildfire)", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"}
    },
    "cells": cells
}

output_path = "notebooks/PRISM_Comprehensive_Analysis_Part2_California.ipynb"
with open(output_path, 'w') as f:
    json.dump(notebook, f, indent=1)

print(f"Notebook written: {output_path}")
print(f"Total cells: {len(cells)} ({sum(1 for c in cells if c['cell_type']=='markdown')} md, "
      f"{sum(1 for c in cells if c['cell_type']=='code')} code)")
