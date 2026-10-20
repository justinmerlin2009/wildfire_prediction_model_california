# Utility modules for wildfire prediction project
from .constants import *
from .domain_mappings import *
from .data_loader import load_fire_perimeters, add_derived_columns, apply_domain_labels
from .plotting import (
    setup_plotting_style, save_figure, get_agency_colors, get_cause_colors,
    get_severity_colors, get_incid_type_colors, get_asmnt_type_colors,
    get_nwcg_cause_colors, get_general_cause_colors, get_fire_size_class_colors,
    get_source_system_colors, get_owner_colors,
    get_elevation_zone_colors, get_slope_class_colors, get_aspect_colors,
    get_tpi_colors,
    get_canopy_cover_colors, get_canopy_broad_colors,
    get_lifeform_colors, get_whr13_colors, get_fire_risk_colors,
    get_prism_variable_colors, get_vpd_risk_colors, get_drought_colors,
    get_climate_season_colors, get_prism_diverging_norm,
)
from .mtbs_domain_mappings import *
from .mtbs_data_loader import load_mtbs_fod, add_mtbs_derived_columns, reproject_to_albers
from .fpa_domain_mappings import *
from .fpa_data_loader import (
    load_fpa_fod, load_fpa_national_summary, load_fpa_unit_metadata,
    add_fpa_derived_columns,
)
from .topo_domain_mappings import (
    ELEVATION_ZONE_MAP, ELEVATION_ZONE_ORDER, ELEVATION_ZONE_THRESHOLDS,
    SLOPE_CLASS_MAP, SLOPE_CLASS_ORDER, SLOPE_CLASS_THRESHOLDS,
    ASPECT_CLASS_MAP, ASPECT_CLASS_ORDER,
    TPI_CLASS_MAP, TPI_CLASS_ORDER,
    classify_elevation, classify_slope, classify_aspect, classify_tpi,
)
from .topo_data_loader import (
    load_topography_metadata, load_topography_downsampled, load_topography_window,
    compute_slope_aspect, compute_tpi, compute_twi, compute_heat_load_index,
    aggregate_to_grid, extract_terrain_at_points, extract_terrain_for_polygons,
    get_topo_data_quality_summary,
)
from .landfire_domain_mappings import (
    CC_VALUE_MAP, CC_MIDPOINT_MAP, CC_ORDERED_VALUES, CC_RGB_MAP,
    CC_BROAD_CATEGORIES, CC_BROAD_CATEGORY_ORDER, CC_BROAD_CATEGORY_COLORS,
    get_cc_label, get_cc_color, get_cc_broad_category,
    build_cc_colormap, build_cc_norm, classify_canopy_cover,
)
from .landfire_data_loader import (
    load_landfire_cc_metadata, clip_cc_to_california,
    reproject_cc_to_albers, load_cc_california,
    load_cc_downsampled, extract_cc_at_points, extract_cc_for_polygons,
    get_cc_class_distribution, get_cc_data_quality_summary,
)
from .vegetation_domain_mappings import (
    WHRTYPE_MAP, LIFEFORM_MAP, LIFEFORM_ORDER, WHR13_MAP, WHR13_ORDER,
    WHRTYPE_TO_LIFEFORM, WHRTYPE_TO_WHR13,
    WHRSIZE_MAP, WHRSIZE_ORDER, WHRDENSITY_MAP, WHRDENSITY_ORDER,
    FIRE_PRONE_WHRTYPE, FIRE_RISK_ORDER,
    get_whrtype_name, get_lifeform, get_whr13_class, get_fire_risk_level,
    parse_whrall, classify_fire_fuel_type,
)
from .vegetation_data_loader import (
    load_vegetation_metadata, load_vegetation_downsampled,
    load_vegetation_window, get_unique_values_and_counts,
    load_local_rat, load_imageserver_rat, download_rat_csv,
    get_value_to_attributes, merge_values_with_rat,
    extract_vegetation_at_points, get_vegetation_data_quality_summary,
)
from .prism_domain_mappings import (
    PRISM_VARIABLE_META, PRISM_SOLAR_META, PRISM_VARIABLE_ORDER,
    FIRE_WEATHER_VPD_CLASSES, FIRE_WEATHER_VPD_ORDER, FIRE_WEATHER_THRESHOLDS,
    DROUGHT_CLASSES, DROUGHT_CLASS_ORDER,
    CLIMATE_SEASON_MAP, CLIMATE_SEASON_ORDER,
    WATER_YEAR_START_MONTH, FIRE_WEATHER_SEASON_MONTHS,
    CA_CLIMATE_REGIONS, CONUS_STATES, US_STATE_FIPS, WESTERN_US_STATES,
    DERIVED_VARIABLES, MONTH_ABBREVS, MONTH_NAMES,
    get_variable_meta, get_variable_label, get_variable_colormap,
    classify_vpd, classify_drought, month_to_water_year,
    compute_rh_from_tdmean_tmax,
)
from .prism_data_loader import (
    check_prism_drive, discover_files, build_file_inventory, parse_filename,
    load_prism_metadata, read_prism_raster, read_prism_california, read_prism_conus,
    load_monthly_series, load_daily_series, load_monthly_stats_ca,
    load_monthly_normal, load_all_monthly_normals,
    compute_monthly_anomaly, compute_anomaly_series,
    compute_diurnal_temp_range, compute_vpd_mean, compute_dew_point_depression,
    compute_estimated_rh, compute_cumulative_vpd, compute_dry_day_count,
    aggregate_daily_to_monthly, aggregate_monthly_to_seasonal,
    aggregate_monthly_to_annual, aggregate_to_water_year,
    load_us_states_boundaries, compute_state_statistics,
    extract_climate_at_points, extract_monthly_climate_at_fires,
    save_to_cache, load_from_cache, precompute_state_monthly_summaries,
    get_prism_data_quality_summary,
)
