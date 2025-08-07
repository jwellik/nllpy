# =============================================================================
# examples/volcano_monitoring.py
# =============================================================================
"""
Example configuration for volcano monitoring
"""


import nllpy


def create_volcano_monitoring_setup():
    """Create a complete volcano monitoring setup"""

    # Use volcano template as starting point
    config = nllpy.create_volcano_config(
        lat_orig=61.299,  # Example: coordinate system origin
        lon_orig=-152.2551,
        # elev=3734,
    )

    config.control.message_flag = 2  # This is the default

    # Customize for specific volcano
    config.locsig = "Alaska Volcano Observatory - Mt Spurr"
    config.loccom = "October 14, 2024"

    # config.vgtype = "P"

    # Grid for the velocity model
    config.vggrid.num_grid_x = 200
    config.vggrid.num_grid_y = 200
    config.vggrid.num_grid_z = 50
    config.vggrid.orig_grid_x = -100.0
    config.vggrid.orig_grid_y = -100.0
    config.vggrid.orig_grid_z = -4.0
    config.vggrid.d_grid_x = 1.0
    config.vggrid.d_grid_y = 1.0
    config.vggrid.d_grid_z = 1.0

    # Grid for location area
    config.locgrid.num_grid_x = 100
    config.locgrid.num_grid_y = 100
    config.locgrid.num_grid_z = 30
    config.locgrid.orig_grid_x = -50.0
    config.locgrid.orig_grid_y = -50.0
    config.locgrid.orig_grid_z = -4.0
    config.locgrid.d_grid_x = 1.0
    config.locgrid.d_grid_y = 1.0
    config.locgrid.d_grid_z = 1.0

    # Custom volcano velocity model (typical stratovolcano)
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
    # Strict requirements for volcano monitoring
    config.locmethod.min_num_phases = 8  # Need good coverage
    config.locmethod.min_num_s_phases = 4  # Important for depth resolution
    config.locmethod.max_dist_sta_grid = 30.0  # Focus on local events

    # Tighter quality control
    config.locqual2err.error_values = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2]

    # Add example stations (would normally come from inventory)
    stations = [
        ("SPBG", 61.2591, -152.3722, 1.0870),  # Barrier Glacier
        ("SPBL", 61.3764, -151.8947, 9.270),   # Spurr Beluga Lake
        ("SPCG", 61.2913, -152.0228, 1.3290),  # Capps Glacier
        ("SPCL", 61.1956, -152.3399, 1.2740),  # Chakachamna Lake
        ("SPCN", 61.223675, -152.18403, .7333), # Chakachatna North
        ("SPCP", 61.265465, -152.155495, 1.6400), # Crater Peak
        ("SPCR", 61.2003, -152.2091, .9840),   # Chakachatna River
    ]

    for code, lat, lon, elev in stations:
        config.add_station(code, lat, lon, elev)

    return config


if __name__ == "__main__":
    print("Volcano Monitoring Example")
    print("=" * 50)

    # Create complete configuration
    config = create_volcano_monitoring_setup()
    config.write_complete_control_file("spurr.in")
    print("Complete volcano monitoring configuration written to 'spurr.in'")
    print()
