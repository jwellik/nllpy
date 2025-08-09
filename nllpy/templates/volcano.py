# =============================================================================
# nllpy/templates/volcano.py
# =============================================================================
"""
Template configurations for volcano monitoring
"""

from ..core.config import NLLocConfig

# TODO Add elevation for the purposes of setting the top of the grid
def create_volcano_config(lat_orig: float, lon_orig: float, **kwargs) -> NLLocConfig:
    """
    Create configuration optimized for volcano monitoring

    Args:
        lat_orig: Origin latitude for coordinate system
        lon_orig: Origin longitude for coordinate system
        **kwargs: Additional parameters to override defaults

    Returns:
        Configured NLLocConfig object
    """
    config = NLLocConfig()

    config.filename = "volcano.in"

    # Coordinate system
    config.trans.transformation = "SDC"
    config.trans.lat_orig = lat_orig
    config.trans.lon_orig = lon_orig
    config.trans.rotation = 0.0

    # Search parameters for local events
    config.locsearch.search_type = "OCT"
    config.locsearch.num_cells_x = 20
    config.locsearch.num_cells_y = 20
    config.locsearch.num_cells_z = 11
    config.locsearch.min_node_size = 0.01
    config.locsearch.max_num_nodes = 20000
    config.locsearch.num_scatter = 5000

    # Location method for picks at volcanoes
    config.locmethod.method = "EDT_OT_WT"
    config.locmethod.max_dist_sta_grid = 50.0
    config.locmethod.min_num_phases = 5
    config.locmethod.min_num_s_phases = 1
    config.locmethod.v_p_vs_ratio = 1.73

    # Grid for the velocity model
    config.vggrid.num_grid_x = 200
    config.vggrid.num_grid_y = 200
    config.vggrid.num_grid_z = 50
    config.vggrid.orig_grid_x = -100.0
    config.vggrid.orig_grid_y = -100.0
    config.vggrid.orig_grid_z = -5.0
    config.vggrid.d_grid_x = 1.0
    config.vggrid.d_grid_y = 1.0
    config.vggrid.d_grid_z = 1.0

    # Grid for location area
    config.locgrid.num_grid_x = 100
    config.locgrid.num_grid_y = 100
    config.locgrid.num_grid_z = 30
    config.locgrid.orig_grid_x = -50.0
    config.locgrid.orig_grid_y = -50.0
    config.locgrid.orig_grid_z = -5.0
    config.locgrid.d_grid_x = 1.0
    config.locgrid.d_grid_y = 1.0
    config.locgrid.d_grid_z = 1.0

    # Volcano-specific velocity model
    # TODO Make this read from utils/model_stratovolcano.txt
    config.layer.layers = [
        (-6.00, 2.5487, 0.00, 1.4732, 0.00, 2.7, 0.0),
        (-5.00, 2.8855, 0.00, 1.6679, 0.00, 2.7, 0.0),
        (-4.00, 3.2036, 0.00, 1.8518, 0.00, 2.7, 0.0),
        (-3.00, 3.5037, 0.00, 2.0253, 0.00, 2.7, 0.0),
        (-2.00, 3.7864, 0.00, 2.1887, 0.00, 2.7, 0.0),
        (-1.00, 4.0523, 0.00, 2.3424, 0.00, 2.7, 0.0),
        (0.00, 4.3020, 0.00, 2.4867, 0.00, 2.7, 0.0),
        (1.00, 4.5361, 0.00, 2.6220, 0.00, 2.7, 0.0),
        (2.00, 4.7552, 0.00, 2.7487, 0.00, 2.7, 0.0),
        (3.00, 4.9599, 0.00, 2.8670, 0.00, 2.7, 0.0),
        (4.00, 5.1508, 0.00, 2.9773, 0.00, 2.7, 0.0),
        (5.00, 5.3286, 0.00, 3.0801, 0.00, 2.7, 0.0),
        (6.00, 5.4937, 0.00, 3.1756, 0.00, 2.7, 0.0),
        (7.00, 5.6470, 0.00, 3.2641, 0.00, 2.7, 0.0),
        (8.00, 5.7888, 0.00, 3.3462, 0.00, 2.7, 0.0),
        (9.00, 5.9200, 0.00, 3.4219, 0.00, 2.7, 0.0),
        (10.00, 6.0409, 0.00, 3.4919, 0.00, 2.7, 0.0),
        (11.00, 6.1524, 0.00, 3.5563, 0.00, 2.7, 0.0),
        (12.00, 6.2549, 0.00, 3.6155, 0.00, 2.7, 0.0),
        (13.00, 6.3491, 0.00, 3.6700, 0.00, 2.7, 0.0),
        (14.00, 6.4355, 0.00, 3.7199, 0.00, 2.7, 0.0),
        (15.00, 6.5149, 0.00, 3.7658, 0.00, 2.7, 0.0),
        (16.00, 6.5877, 0.00, 3.8079, 0.00, 2.7, 0.0),
        (17.00, 6.6546, 0.00, 3.8466, 0.00, 2.7, 0.0),
        (18.00, 6.7163, 0.00, 3.8822, 0.00, 2.7, 0.0),
        (19.00, 6.7732, 0.00, 3.9151, 0.00, 2.7, 0.0),
        (20.00, 6.8261, 0.00, 3.9457, 0.00, 2.7, 0.0),
        (21.00, 6.8755, 0.00, 3.9743, 0.00, 2.7, 0.0),
        (22.00, 6.9220, 0.00, 4.0011, 0.00, 2.7, 0.0),
        (23.00, 6.9662, 0.00, 4.0267, 0.00, 2.7, 0.0),
        (24.00, 7.0088, 0.00, 4.0513, 0.00, 2.7, 0.0),
        (25.00, 7.0503, 0.00, 4.0753, 0.00, 2.7, 0.0),
        (26.00, 7.0914, 0.00, 4.0991, 0.00, 2.7, 0.0),
        (27.00, 7.1327, 0.00, 4.1229, 0.00, 2.7, 0.0),
        (28.00, 7.1747, 0.00, 4.1472, 0.00, 2.7, 0.0),
        (29.00, 7.2181, 0.00, 4.1723, 0.00, 2.7, 0.0),
        (30.00, 7.2634, 0.00, 4.1985, 0.00, 2.7, 0.0),
    ]

    # Location method settings
    config.locmethod.method = "EDT_OT_WT"
    config.locmethod.max_dist_sta_grid = 50.0
    config.locmethod.min_num_phases = 6
    config.locmethod.min_num_s_phases = 3

    # Volcano-specific phase definitions
    config.locphaseid = {
        'P': ['P', 'p', 'Pn', 'Pg'],
        'S': ['S', 's', 'Sn', 'Sg']
    }

    # Tighter quality control
    config.locqual2err.error_values = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5]

    config.locsig = "USGS Volcano Disaster Assistance Program"
    config.loccom = "NonLinLoc template for volcano monitoring"

    # Apply any overrides
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            print(f"Warning: Unknown parameter {key}")

    return config
