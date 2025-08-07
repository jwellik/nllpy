# =============================================================================
# nllpy/templates/regional.py
# =============================================================================
"""
Template configurations for regional earthquake location
"""

from ..core.config import NLLocConfig


def create_regional_config(lat_orig: float, lon_orig: float, **kwargs) -> NLLocConfig:
    """
    Create configuration optimized for regional earthquake location

    Args:
        lat_orig: Origin latitude for coordinate system
        lon_orig: Origin longitude for coordinate system
        **kwargs: Additional parameters to override defaults

    Returns:
        Configured NLLocConfig object
    """
    config = NLLocConfig()

    # Regional coordinate system
    config.trans.transformation = "LAMBERT"
    config.trans.lat_orig = lat_orig
    config.trans.lon_orig = lon_orig

    # Search parameters for regional events
    config.locsearch.search_type = "OCT"
    config.locsearch.min_node_size = 0.1  # Coarser resolution
    config.locsearch.max_num_nodes = 20000

    # Regional grid - covers larger area
    config.locgrid.num_grid_x = 201
    config.locgrid.num_grid_y = 201
    config.locgrid.num_grid_z = 61
    config.locgrid.orig_grid_x = -100.0  # 200km x 200km x 60km
    config.locgrid.orig_grid_y = -100.0
    config.locgrid.orig_grid_z = 0.0
    config.locgrid.d_grid_x = 1.0  # 1km spacing
    config.locgrid.d_grid_y = 1.0
    config.locgrid.d_grid_z = 1.0

    # Regional crustal model
    config.gtlevels.layers = [
        (0.0, 6.0),
        (15.0, 6.5),
        (25.0, 7.8),
        (35.0, 8.1)
    ]

    config.locmethod.max_dist_sta_grid = 300.0  # 300km max distance
    config.locmethod.min_num_phases = 8
    config.locmethod.min_num_s_phases = 4

    config.locsig = "Regional Seismic Network"
    config.loccom = "Regional earthquake location"

    # Apply any overrides
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            print(f"Warning: Unknown parameter {key}")

    return config