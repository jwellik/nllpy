# =============================================================================
# nllpy/utils/config_helpers.py
# =============================================================================
"""
Helper utilities for NLLoc configuration setup
"""

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import nllpy


def create_volcano_monitoring_config(latitude: float, longitude: float, radius: float,
                                   fdsn_url: str, sta_fmt: str = "NET.STA",
                                   **fdsn_kwargs) -> tuple:
    """
    Create a complete volcano monitoring configuration
    
    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius: Search radius in degrees
        fdsn_url: FDSN server URL
        sta_fmt: Station code format
        **fdsn_kwargs: Additional FDSN parameters
        
    Returns:
        Tuple of (config, result_dict)
    """
    from ..core.config import NLLocConfig
    config = NLLocConfig()
    
    # Download stations
    result = config.create_from_fdsn_stations(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        fdsn_url=fdsn_url,
        sta_fmt=sta_fmt,
        **fdsn_kwargs
    )
    
    # Set up grid for volcano monitoring (shallow, high resolution)
    config.setup_basic_grid(
        grid_size=50.0,
        grid_spacing=0.5,
        depth_range=10.0,  # 10km depth range for volcano monitoring
        depth_spacing=0.25,
        center_lat=latitude,
        center_lon=longitude
    )
    
    # Set basic velocity model
    config.setup_basic_velocity_model()
    
    # Add EQSTA commands for all stations
    for station in result['station_codes']:
        config._add_eqsta_for_station(station, p_error=0.0, s_error=0.0)
    
    return config, result


def create_regional_monitoring_config(latitude: float, longitude: float, radius: float,
                                    fdsn_url: str, sta_fmt: str = "NET.STA",
                                    **fdsn_kwargs) -> tuple:
    """
    Create a complete regional monitoring configuration
    
    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius: Search radius in degrees
        fdsn_url: FDSN server URL
        sta_fmt: Station code format
        **fdsn_kwargs: Additional FDSN parameters
        
    Returns:
        Tuple of (config, result_dict)
    """
    from ..core.config import NLLocConfig
    config = NLLocConfig()
    
    # Download stations
    result = config.create_from_fdsn_stations(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        fdsn_url=fdsn_url,
        sta_fmt=sta_fmt,
        **fdsn_kwargs
    )
    
    # Set up grid for regional monitoring (deeper, coarser resolution)
    config.setup_basic_grid(
        grid_size=100.0,
        grid_spacing=1.0,
        depth_range=50.0,  # 50km depth range for regional monitoring
        depth_spacing=0.5,
        center_lat=latitude,
        center_lon=longitude
    )
    
    # Set basic velocity model
    config.setup_basic_velocity_model()
    
    # Add EQSTA commands for all stations
    for station in result['station_codes']:
        config._add_eqsta_for_station(station, p_error=0.0, s_error=0.0)
    
    return config, result


def print_config_summary(config: 'nllpy.NLLocConfig', result: Dict, 
                        show_stations: bool = False, max_stations: int = 10):
    """
    Print a summary of the configuration
    
    Args:
        config: NLLocConfig object
        result: Result dictionary from station download
        show_stations: Whether to show station codes
        max_stations: Maximum number of stations to show
    """
    print(f"\n=== Configuration Summary ===")
    print(f"Total stations: {len(config.gtsrce_stations)}")
    print(f"Total EQSTA commands: {len(config.eqsta_commands)}")
    print(f"FDSN URL: {result.get('fdsn_url', 'N/A')}")
    print(f"Search center: {result.get('search_center', 'N/A')}")
    print(f"Search radius: {result.get('search_radius', 'N/A')} degrees")
    
    if show_stations and result.get('station_codes'):
        print(f"\nStations:")
        station_codes = result['station_codes']
        for code in station_codes[:max_stations]:
            print(f"  {code}")
        if len(station_codes) > max_stations:
            print(f"  ... and {len(station_codes) - max_stations} more")
    print()


def save_config_with_stations(config: 'nllpy.NLLocConfig', 
                            control_file: str, station_file: Optional[str] = None,
                            latitude: float = None, longitude: float = None,
                            radius: float = None, fdsn_url: str = None,
                            sta_fmt: str = "STA", **fdsn_kwargs) -> Dict:
    """
    Save configuration and optionally station list
    
    Args:
        config: NLLocConfig object
        control_file: Output NLLoc control file
        station_file: Optional station list file
        latitude: Center latitude (required if saving stations)
        longitude: Center longitude (required if saving stations)
        radius: Search radius (required if saving stations)
        fdsn_url: FDSN URL (required if saving stations)
        sta_fmt: Station code format
        **fdsn_kwargs: Additional FDSN parameters
        
    Returns:
        Dictionary with save results
    """
    result = {}
    
    # Write control file
    config.write_complete_control_file(control_file)
    result['control_file'] = control_file
    
    # Save station list if requested
    if station_file and all([latitude, longitude, radius, fdsn_url]):
        save_result = config.save_fdsn_stations_to_file(
            filename=station_file,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            fdsn_url=fdsn_url,
            sta_fmt=sta_fmt,
            **fdsn_kwargs
        )
        result['station_file'] = station_file
        result['station_save_result'] = save_result
    
    return result 