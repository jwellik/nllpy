# =============================================================================
# nllpy/core/config.py
# =============================================================================
"""
Main configuration class for NLLoc
"""

from typing import List, Dict, Optional
from pathlib import Path

from .commands import *
from ..utils.inventory import parse_inventory


class NLLocConfig:
    """Main class for generating NLLoc control files"""

    def __init__(self):
        self.control = ControlCommand()
        self.trans = TransCommand()
        self.vgtype = ['P']  # TODO Make this a command?
        self.eqvpvs = 1.73  # TODO Make this a command?
        self.velocity_path = "./model/layer"  # TODO Make this a command?
        self.time_path = "./time/layer"  # TODO Make this a command?
        self.synth_path = "./obs_synth/synth.obs"  # TODO Make this a command?
        self.input_obs = ("./obs/*.obs", "NLLOC_OBS")  # TODO Make this a command?
        self.output_obs = "./loc/volcano"  # TODO Make this a command?
        self.lochypout = ["SAVE_NLLOC_ALL", "SAVE_NLLOC_SUM", "SAVE_HYPO71_SUM"]  # TODO Make this a command?
        self.vggrid = VelGridCommand()
        self.locgrid = LocGridCommand()
        self.locsearch = LocSearchCommand()
        self.locmethod = LocMethodCommand()
        self.layer = LayerCommand()
        self.gtsrce_stations: List[GTSrceCommand] = []
        self.eqsta_commands: List[EQSTACommand] = []

        # Other parameters
        self.locsig = "NLLPy - Python NLLoc Control Generator"
        self.loccom = "Generated automatically"
        self.locphaseid = {
            'P': ['P', 'p', 'Pn', 'Pg', 'P1'],
            'S': ['S', 's', 'Sn', 'Sg', 'S1']
        }
        self.locqual2err = LocQual2ErrCommand()

    def _add_station_to_gtsrce(self, station_data: Dict, sta_fmt: str = "STA"):
        """
        Helper method to add a station to GTSRCE commands
        
        Args:
            station_data: Dictionary with station information (code, latitude, longitude, depth)
            sta_fmt: Station code format
        """
        self.gtsrce_stations.append(
            GTSrceCommand(
                label=station_data['code'],
                lat_sta=station_data['latitude'],
                lon_sta=station_data['longitude'],
                elev=station_data['depth'] * -1.0,  # Elevation positive
                depth_corr=0.0,
                sta_fmt=sta_fmt
            )
        )

    def _add_eqsta_for_station(self, station_code: str, p_error: float = 0.0, s_error: float = 0.0):
        """
        Helper method to add EQSTA commands for a station (P and S phases)
        
        Args:
            station_code: Station code
            p_error: P phase timing error in seconds
            s_error: S phase timing error in seconds
        """
        # P phase
        self.add_eqsta_single(
            label=station_code,
            phase="P",
            error=p_error,
            error_report=p_error
        )
        # S phase
        self.add_eqsta_single(
            label=station_code,
            phase="S",
            error=s_error,
            error_report=s_error
        )

    def setup_basic_grid(self, grid_size: float = 50.0, grid_spacing: float = 0.5, 
                        depth_range: float = 20.0, depth_spacing: float = 0.25,
                        center_lat: Optional[float] = None, center_lon: Optional[float] = None):
        """
        Set up basic grid parameters for location
        
        Args:
            grid_size: Grid size in km
            grid_spacing: Grid spacing in km
            depth_range: Depth range in km
            depth_spacing: Depth spacing in km
            center_lat: Center latitude for coordinate system (optional)
            center_lon: Center longitude for coordinate system (optional)
        """
        num_grid_points = int(grid_size / grid_spacing) + 1
        num_depth_points = int(depth_range / depth_spacing) + 1
        
        # Set number of grid points
        self.locgrid.num_grid_x = num_grid_points
        self.locgrid.num_grid_y = num_grid_points
        self.locgrid.num_grid_z = num_depth_points
        
        # Set grid spacing
        self.locgrid.d_grid_x = grid_spacing
        self.locgrid.d_grid_y = grid_spacing
        self.locgrid.d_grid_z = depth_spacing
        
        # Grid origins will be automatically calculated by LocGridCommand.__post_init__()
        # based on num_grid_x * d_grid_x and num_grid_y * d_grid_y
        
        # Set coordinate system origin if provided
        if center_lat is not None:
            self.trans.orig_lat = center_lat
        if center_lon is not None:
            self.trans.orig_lon = center_lon

    def setup_basic_velocity_model(self):
        """Set up a basic layered velocity model"""
        self.layer.layers = [
            (0.0, 2.0),    # Surface layer
            (2.0, 4.0),    # Upper crust
            (8.0, 5.5),    # Lower crust
            (20.0, 6.8),   # Upper mantle
        ]

    def setup_grid_from_km(self, kmx: float, kmy: float, kmz: float, 
                           dx: float = 1.0, dy: float = 1.0, dz: float = 1.0,
                           d_xy: Optional[float] = None, d_xyz: Optional[float] = None,
                           center_lat: Optional[float] = None, center_lon: Optional[float] = None):
        """
        Set up grid using km dimensions (similar to CLI --kmx, --kmy, --kmz)
        
        Args:
            kmx: Grid size in X direction (km)
            kmy: Grid size in Y direction (km)
            kmz: Grid size in Z direction (km)
            dx: Grid spacing in X direction (km)
            dy: Grid spacing in Y direction (km)
            dz: Grid spacing in Z direction (km)
            d_xy: Convenience parameter to set both dx and dy to the same value
            d_xyz: Convenience parameter to set dx, dy, and dz all to the same value
            center_lat: Center latitude for coordinate system (optional)
            center_lon: Center longitude for coordinate system (optional)
        """
        import math
        
        # Handle convenience spacing parameters
        if d_xyz is not None:
            dx = dy = dz = d_xyz
        elif d_xy is not None:
            dx = dy = d_xy
        
        # Calculate number of grid points (round up to nearest integer)
        nx = int(math.ceil(kmx / dx))
        ny = int(math.ceil(kmy / dy))
        nz = int(math.ceil(kmz / dz))
        
        # Create a new LocGridCommand to trigger automatic origin calculation
        from .commands import LocGridCommand
        self.locgrid = LocGridCommand(
            num_grid_x=nx,
            num_grid_y=ny,
            num_grid_z=nz,
            d_grid_x=dx,
            d_grid_y=dy,
            d_grid_z=dz
        )
        
        # Set coordinate system origin if provided
        if center_lat is not None:
            self.trans.orig_lat = center_lat
        if center_lon is not None:
            self.trans.orig_lon = center_lon

    def create_from_fdsn_stations(self, latitude: float, longitude: float, radius: float, 
                                 fdsn_url: str, sta_fmt: str = "STA", 
                                 min_elevation: Optional[float] = None,
                                 max_elevation: Optional[float] = None,
                                 networks: Optional[List[str]] = None,
                                 stations: Optional[List[str]] = None,
                                 channels: Optional[List[str]] = None,
                                 starttime: Optional[str] = None,
                                 endtime: Optional[str] = None,
                                 level: str = "station") -> Dict:
        """
        Create configuration by downloading stations from FDSN URL
        
        Args:
            latitude: Center latitude for station search
            longitude: Center longitude for station search  
            radius: Search radius in degrees
            fdsn_url: FDSN server URL (e.g., "IRIS", "USGS", "http://service.iris.edu")
            sta_fmt: Station code format - "STA" for station only, "NET.STA" for network.station, "NET_STA" for network_station
            min_elevation: Minimum station elevation in meters (optional)
            max_elevation: Maximum station elevation in meters (optional)
            networks: List of network codes to include (optional)
            stations: List of station codes to include (optional)
            channels: List of channel codes to include (optional)
            starttime: Start time for station availability (optional, format: "YYYY-MM-DD")
            endtime: End time for station availability (optional, format: "YYYY-MM-DD")
            level: Inventory level ("network", "station", "channel", "response")
            
        Returns:
            Dictionary with download results and station count
        """
        try:
            from obspy.clients.fdsn import Client
            from obspy import UTCDateTime
        except ImportError:
            raise ImportError("ObsPy is required for FDSN station downloads. Install with: pip install obspy")
        
        # Create FDSN client
        client = Client(fdsn_url)
        
        # Prepare time parameters
        start = UTCDateTime(starttime) if starttime else None
        end = UTCDateTime(endtime) if endtime else None
        
        # Download station inventory
        try:
            inventory = client.get_stations(
                latitude=latitude,
                longitude=longitude,
                minradius=0.0,
                maxradius=radius,
                minlatitude=latitude - radius,
                maxlatitude=latitude + radius,
                minlongitude=longitude - radius,
                maxlongitude=longitude + radius,
                min_elevation=min_elevation,
                max_elevation=max_elevation,
                network=','.join(networks) if networks else None,
                station=','.join(stations) if stations else None,
                channel=','.join(channels) if channels else None,
                starttime=start,
                endtime=end,
                level=level
            )
        except Exception as e:
            raise RuntimeError(f"Failed to download stations from {fdsn_url}: {str(e)}")
        
        # Convert ObsPy inventory to station list
        from ..utils.inventory import parse_obspy_inventory
        station_list = parse_obspy_inventory(inventory, sta_fmt=sta_fmt)
        
        # Add stations to configuration using helper method
        for station_data in station_list:
            self._add_station_to_gtsrce(station_data, sta_fmt=sta_fmt)
        
        # Create result summary
        result = {
            'fdsn_url': fdsn_url,
            'search_center': (latitude, longitude),
            'search_radius': radius,
            'stations_downloaded': len(station_list),
            'station_codes': [s['code'] for s in station_list],
            'inventory': inventory
        }
        
        return result

    def save_fdsn_stations_to_file(self, filename: str, latitude: float, longitude: float, 
                                  radius: float, fdsn_url: str, sta_fmt: str = "STA",
                                  **kwargs) -> Dict:
        """
        Download stations from FDSN and save to file in FDSN format
        
        Args:
            filename: Output filename for station list
            latitude: Center latitude for station search
            longitude: Center longitude for station search
            radius: Search radius in degrees
            fdsn_url: FDSN server URL
            sta_fmt: Station code format
            **kwargs: Additional arguments passed to create_from_fdsn_stations
            
        Returns:
            Dictionary with download results
        """
        # Download stations
        result = self.create_from_fdsn_stations(
            latitude=latitude, 
            longitude=longitude, 
            radius=radius, 
            fdsn_url=fdsn_url, 
            sta_fmt=sta_fmt,
            **kwargs
        )
        
        # Save to file in FDSN format
        with open(filename, 'w') as f:
            f.write("# FDSN Station List\n")
            f.write("# NET|STA|LAT|LON|ELEV|SITENAME|START|END\n")
            
            for station in result['inventory']:
                for sta in station:
                    # Format: NET|STA|LAT|LON|ELEV|SITENAME|START|END
                    net_code = station.code
                    sta_code = sta.code
                    lat = sta.latitude
                    lon = sta.longitude
                    elev = sta.elevation
                    site_name = sta.site.name if sta.site and sta.site.name else ""
                    start_date = sta.start_date.strftime("%Y-%m-%d") if sta.start_date else ""
                    end_date = sta.end_date.strftime("%Y-%m-%d") if sta.end_date else ""
                    
                    f.write(f"{net_code}|{sta_code}|{lat:.6f}|{lon:.6f}|{elev:.1f}|{site_name}|{start_date}|{end_date}\n")
        
        result['output_file'] = filename
        return result

    def add_eqsta_errors(self, station_errors: Dict[str, Dict[str, tuple]]):
        """
        Add EQSTA error definitions for stations

        Args:
            station_errors: Dictionary with station codes as keys and phase dictionaries as values
                           e.g., {
                               'R6DB7': {'P': (0.0, 0.0), 'S': (0.0, 0.0)},
                               'R6E02': {'P': (0.0, 0.0)},  # Only P phase
                               'SBLS': {'P': (0.1, 0.1), 'S': (0.2, 0.2)}
                           }
                           Each tuple is (error, error_report)
        """
        for station, phases in station_errors.items():
            for phase, error_tuple in phases.items():
                error, error_report = error_tuple
                self.eqsta_commands.append(
                    EQSTACommand(
                        label=station,
                        phase=phase,
                        error=error,
                        error_report=error_report
                    )
                )

    def add_eqsta_simple(self, station_errors: Dict[str, tuple], phase: str = "P"):
        """
        Add EQSTA error definitions for a single phase type across multiple stations

        Args:
            station_errors: Dictionary with station codes as keys and (error, error_report) tuples as values
                           e.g., {'R6DB7': (0.0, 0.0), 'R6E02': (0.0, 0.0)}
            phase: Phase type to apply to all stations (default "P")
        """
        for station, error_tuple in station_errors.items():
            error, error_report = error_tuple
            self.eqsta_commands.append(
                EQSTACommand(
                    label=station,
                    phase=phase,
                    error=error,
                    error_report=error_report
                )
            )

    def add_eqsta_single(self, label: str, phase: str = "P", error_type: str = "GAU",
                         error: float = 0.0, error_report_type: str = "GAU",
                         error_report: float = 0.0, prob_active: float = 1.0):
        """
        Add a single EQSTA error definition

        Args:
            label: Station label
            phase: Phase type (default "P")
            error_type: Error type (default "GAU")
            error: Error value
            error_report_type: Error report type (default "GAU")
            error_report: Error report value
            prob_active: Probability active (default 1.0)
        """
        self.eqsta_commands.append(
            EQSTACommand(
                label=label,
                phase=phase,
                error_type=error_type,
                error=error,
                error_report_type=error_report_type,
                error_report=error_report,
                prob_active=prob_active
            )
        )

    def add_station(self, code: str, lat: float, lon: float, elev: float, depth_corr: float = 0.0):
        """Add a single station"""

        self.gtsrce_stations.append(GTSrceCommand(
            label=code,
            lat_sta=lat,
            lon_sta=lon,
            elev=elev,
            depth_corr=depth_corr
        ))

        # Add default EQSTA command for P phase
        self.eqsta_commands.append(
            EQSTACommand(
                label=code,
                phase="P",
                error_type="GAU",
                error=0.0,
                error_report_type="GAU",
                error_report=0.0,
                prob_active=1.0
            )
        )

    def get_eqsta_section(self) -> str:
        """Get EQSTA commands for all stations"""
        if not self.eqsta_commands:
            return "# No EQSTA error definitions"

        lines = ["# Station-specific error definitions"]
        for eqsta in self.eqsta_commands:
            lines.append(str(eqsta))
        return "\n".join(lines)

    def add_station_from_inventory(self, inventory_file: str, sta_fmt: str = "STA"):
        """
        Add stations from inventory file
        
        Args:
            inventory_file: Path to inventory file
            sta_fmt: Station code format - "STA" for station only, "NET.STA" for network.station, "NET_STA" for network_station
        """
        stations = parse_inventory(inventory_file, sta_fmt=sta_fmt)
        for station_data in stations:
            self._add_station_to_gtsrce(station_data, sta_fmt=sta_fmt)

    def add_station_from_fdsn(self, fdsn_file: str, sta_fmt: str = "STA"):
        """
        Add stations from FDSN format file
        
        Args:
            fdsn_file: Path to FDSN format file (NET|STA|LAT|LON|ELEV|SITENAME|START|END)
            sta_fmt: Station code format - "STA" for station only, "NET.STA" for network.station, "NET_STA" for network_station
        """
        from ..utils.inventory import _parse_fdsn_inventory
        
        stations = _parse_fdsn_inventory(fdsn_file, sta_fmt=sta_fmt)
        for station_data in stations:
            self._add_station_to_gtsrce(station_data, sta_fmt=sta_fmt)

    def get_gtsrce_section(self) -> str:
        """Get GTSRCE commands for all stations"""
        if not self.gtsrce_stations:
            return "# No stations defined"

        lines = ["# Station definitions"]
        for station in self.gtsrce_stations:
            lines.append(str(station))
        return "\n".join(lines)

    def get_layer_section(self) -> str:
        """Get LAYER velocity model"""
        return f"# Velocity model\n{str(self.layer)}"

    def get_vgtype_section(self) -> str:
        """Get VGTYPE command"""
        lines = [f"VGTYPE  {type}" for type in self.vgtype]
        return "\n".join(lines)

    def get_vggrid_section(self) -> str:
        """Get VGGRID command"""
        return f"# Velocity grid\n{str(self.vggrid)}"

    def get_locgrid_section(self) -> str:
        """Get LOCGRID command"""
        return f"# Location grid\n{str(self.locgrid)}"

    def get_lochypout_section(self) -> str:
        """Get LOCHYPOUT command"""
        return "LOCHYPOUT  " + " ".join(self.lochypout)

    def get_basic_commands(self) -> str:
        """Get basic control commands"""
        lines = [
            "# Basic control parameters",
            str(self.control),
        ]
        return "\n".join(lines)

    def get_trans_commands(self) -> str:
        """Get basic control commands"""
        lines = [
            "# Transform command",
            str(self.trans),
        ]
        return "\n".join(lines)

    def get_comment_commands(self) -> str:
        """Get basic control commands"""
        lines = [
            "# Signature and comments",
            f"LOCSIG {self.locsig}",
            f"LOCCOM {self.loccom}",
        ]
        return "\n".join(lines)

    def get_phase_definitions(self) -> str:
        """Get phase ID definitions"""
        lines = ["# Phase definitions"]
        for phase_type, phases in self.locphaseid.items():
            phase_cmd = LocPhaseIDCommand(phase_type, phases)
            lines.append(str(phase_cmd))

        lines.append(str(self.locqual2err))
        return "\n".join(lines)

    def get_io_sections(self):
        """Get all lines that contain input/output paths"""
        lines = [
            f"VGOUT    {self.velocity_path}",
            f"GTFILES  {self.velocity_path}  {self.time_path}  P",  # STUB
            f"EQFILES  {self.time_path}  {self.synth_path}",
            f"LOCFILES {self.input_obs[0]}  {self.input_obs[1]}  {self.time_path} {self.output_obs}",
            self.get_lochypout_section()
        ]
        return '\n'.join(lines)

    def write_complete_control_file(self, filename: str):
        """Write complete control file"""
        sections = [

            # Basic commands
            self.get_basic_commands(),
            self.get_trans_commands(),
            self.get_comment_commands(),

            # I/O
            self.get_io_sections(),

            # GT---
            "GTMODE   GRID3D  ANGLES_YES",
            "GT_PLFD  1.0e-3  0",

            # EQ---
            "EQMECH  DOUBLE 0.0 90.0 0.0",
            "EQMODE SRCE_TO_STA",
            "EQEVENT  EQ001   0.0 0.0 10.0  0.0",
            "EQQUAL2ERR 0.1 0.2 0.4 0.8 99999.9",

            # Velocity grid phases & velocity ratios
            self.get_vgtype_section(),
            f"EQVPVS  {self.eqvpvs}",

            # Velocity and location grid
            self.get_vggrid_section(),
            self.get_locgrid_section(),

            # Search methods
            str(self.locsearch),
            str(self.locmethod),

            # Velocity model
            self.get_layer_section(),

            # LOC---
            "LOCGAU 0.2 0.0",
            "LOCGAU2 0.01 0.05 2.0",
            "LOCANGLES ANGLES_YES 5",
            "LOCMAG ML_HB 1.0 1.110 0.00189",
            "LOCPHSTAT 9999.0 -1 9999.0 1.0 1.0 9999.9 -9999.9 9999.9",

            self.get_phase_definitions(),

            # Station info
            self.get_gtsrce_section(),  # Station locations
            self.get_eqsta_section(),   # Station corrections
            ""
        ]

        with open(filename, 'w') as f:
            f.write("\n\n".join(sections))

    def write_scp_control_file(self, filename: str):
        """Write control file for usage in SeisComP
        (https://www.seiscomp.de/doc/apps/global_nonlinloc.html)"""
        sections = [
            # Basic commands
            self.get_basic_commands(),
            self.get_trans_commands(),
            self.get_comment_commands(),

            "GTMODE   GRID3D  ANGLES_YES",
            "GT_PLFD  1.0e-3  0",
            str(self.locsearch),
            self.get_locgrid_section(),
            str(self.locmethod),
            "LOCGAU 0.001 0.0",
            # "LOCPHASEID  P   P p G Pn Pg P1",
            # "LOCPHASEID  S   S s G Sn Sg S1",
            self.get_phase_definitions(),
            "LOCQUAL2ERR 0.1 0.5 1.0 2.0 99999.9",
            "LOCANGLES ANGLES_YES 5",
        ]

        with open(filename, 'w') as f:
            f.write("\n\n".join(sections))

    def load_from_file(self, filename: str) -> bool:
        """
        Load configuration from an existing NLLoc control file
        
        Args:
            filename: Path to existing NLLoc control file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            # Parse the control file content
            self._parse_control_file_content(content)
            return True
            
        except Exception as e:
            print(f"Error loading configuration from {filename}: {e}")
            return False
    
    def _parse_control_file_content(self, content: str):
        """
        Parse NLLoc control file content and update configuration
        
        Args:
            content: Control file content as string
        """
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split()
            if not parts:
                continue
                
            command = parts[0].upper()
            
            # Parse TRANS command
            if command == 'TRANS':
                if len(parts) >= 4:
                    self.trans.orig_lat = float(parts[1])
                    self.trans.orig_lon = float(parts[2])
                    self.trans.orig_elev = float(parts[3])
            
            # Parse LOCGRID command
            elif command == 'LOCGRID':
                if len(parts) >= 10:
                    self.locgrid.orig_grid_x = float(parts[1])
                    self.locgrid.orig_grid_y = float(parts[2])
                    self.locgrid.orig_grid_z = float(parts[3])
                    self.locgrid.num_grid_x = int(parts[4])
                    self.locgrid.num_grid_y = int(parts[5])
                    self.locgrid.num_grid_z = int(parts[6])
                    self.locgrid.d_grid_x = float(parts[7])
                    self.locgrid.d_grid_y = float(parts[8])
                    self.locgrid.d_grid_z = float(parts[9])
            
            # Parse LAYER command
            elif command == 'LAYER':
                if len(parts) >= 3:
                    depth = float(parts[1])
                    velocity = float(parts[2])
                    self.layer.layers.append((depth, velocity))
            
            # Parse LOCSIG command
            elif command == 'LOCSIG':
                if len(parts) >= 2:
                    self.locsig = ' '.join(parts[1:])
            
            # Parse LOCCOM command
            elif command == 'LOCCOM':
                if len(parts) >= 2:
                    self.loccom = ' '.join(parts[1:])
            
            # Parse GTSRCE commands
            elif command == 'GTSRCE':
                if len(parts) >= 5:
                    label = parts[1]
                    lat = float(parts[2])
                    lon = float(parts[3])
                    elev = float(parts[4])
                    depth_corr = float(parts[5]) if len(parts) > 5 else 0.0
                    self.add_station(label, lat, lon, elev, depth_corr)
            
            # Parse EQSTA commands
            elif command == 'EQSTA':
                if len(parts) >= 5:
                    label = parts[1]
                    phase = parts[2]
                    error = float(parts[3])
                    error_report = float(parts[4])
                    self.add_eqsta_single(
                        label=label,
                        phase=phase,
                        error=error,
                        error_report=error_report
                    )

    def modify_from_args(self, **kwargs):
        """
        Modify configuration from keyword arguments
        
        Args:
            **kwargs: Configuration parameters to modify
        """
        # Location parameters
        if 'lat' in kwargs and kwargs['lat'] is not None:
            self.trans.lat_orig = kwargs['lat']
        if 'lon' in kwargs and kwargs['lon'] is not None:
            self.trans.lon_orig = kwargs['lon']
        if 'elev' in kwargs and kwargs['elev'] is not None:
            # Note: TransCommand doesn't have elev_orig, so we'll skip this for now
            pass
        
        # Grid parameters
        if 'gridkm' in kwargs and kwargs['gridkm']:
            grid_parts = kwargs['gridkm'].split(',')
            if len(grid_parts) >= 3:
                grid_width = float(grid_parts[0])
                grid_height = float(grid_parts[1])
                grid_spacing = float(grid_parts[2])
                
                # Calculate number of grid points
                nx = int(grid_width / grid_spacing) + 1
                ny = int(grid_height / grid_spacing) + 1
                
                # Create a new LocGridCommand to trigger automatic origin calculation
                from .commands import LocGridCommand
                self.locgrid = LocGridCommand(
                    num_grid_x=nx,
                    num_grid_y=ny,
                    num_grid_z=self.locgrid.num_grid_z,  # Keep existing depth settings
                    d_grid_x=grid_spacing,
                    d_grid_y=grid_spacing,
                    d_grid_z=self.locgrid.d_grid_z,  # Keep existing depth spacing
                    orig_grid_z=self.locgrid.orig_grid_z  # Keep existing depth origin
                )
                
                # Also update VGGRID with the same grid parameters
                from .commands import VelGridCommand
                self.vggrid = VelGridCommand(
                    num_grid_x=nx,
                    num_grid_y=ny,
                    num_grid_z=self.vggrid.num_grid_z,  # Keep existing depth settings
                    d_grid_x=grid_spacing,
                    d_grid_y=grid_spacing,
                    d_grid_z=self.vggrid.d_grid_z,  # Keep existing depth spacing
                    orig_grid_z=self.vggrid.orig_grid_z  # Keep existing depth origin
                )
        
        if 'depthkm' in kwargs and kwargs['depthkm']:
            depth_parts = kwargs['depthkm'].split(',')
            if len(depth_parts) >= 2:
                depth_range = float(depth_parts[0])
                depth_spacing = float(depth_parts[1])
                
                # Calculate number of depth points
                nz = int(depth_range / depth_spacing) + 1
                
                # Create a new LocGridCommand to trigger automatic origin calculation
                from .commands import LocGridCommand
                self.locgrid = LocGridCommand(
                    num_grid_x=self.locgrid.num_grid_x,  # Keep existing grid settings
                    num_grid_y=self.locgrid.num_grid_y,
                    num_grid_z=nz,
                    d_grid_x=self.locgrid.d_grid_x,  # Keep existing grid spacing
                    d_grid_y=self.locgrid.d_grid_y,
                    d_grid_z=depth_spacing,
                    orig_grid_z=-5.0  # Start 5km above sea level
                )
                
                # Also update VGGRID with the same depth parameters
                from .commands import VelGridCommand
                self.vggrid = VelGridCommand(
                    num_grid_x=self.vggrid.num_grid_x,  # Keep existing grid settings
                    num_grid_y=self.vggrid.num_grid_y,
                    num_grid_z=nz,
                    d_grid_x=self.vggrid.d_grid_x,  # Keep existing grid spacing
                    d_grid_y=self.vggrid.d_grid_y,
                    d_grid_z=depth_spacing,
                    orig_grid_z=-5.0  # Start 5km above sea level
                )
        
        # Signature and comments
        if 'sig' in kwargs and kwargs['sig']:
            self.locsig = kwargs['sig']
        if 'com' in kwargs and kwargs['com']:
            self.loccom = kwargs['com']
        
        # Output prefix
        if 'prefix' in kwargs and kwargs['prefix']:
            self.output_obs = f"./loc/{kwargs['prefix']}"
        
        # Transform type
        if 'trans' in kwargs and kwargs['trans']:
            self.trans.transformation = kwargs['trans']
        
        # Velocity model
        if 'model' in kwargs and kwargs['model']:
            self._set_velocity_model_by_name(kwargs['model'])
        
        # Station inventory
        if 'inventory' in kwargs and kwargs['inventory']:
            sta_fmt = kwargs.get('sta_fmt', 'STA')
            p_error = kwargs.get('p_error', 0.0)
            s_error = kwargs.get('s_error', 0.0)
            phases = kwargs.get('phases', 'PS')
            error_type = kwargs.get('error_type', 'GAU')
            prob_active = kwargs.get('prob_active', 1.0)
            
            if kwargs['inventory'].startswith('http'):
                # FDSN URL
                radius = kwargs.get('rad_km', 50.0) / 111.0  # Convert km to degrees
                result = self.create_from_fdsn_stations(
                    latitude=self.trans.lat_orig,
                    longitude=self.trans.lon_orig,
                    radius=radius,
                    fdsn_url=kwargs['inventory'],
                    sta_fmt=sta_fmt
                )
                # Add EQSTA commands for all stations
                if result and 'station_codes' in result:
                    for station_code in result['station_codes']:
                        if 'P' in phases:
                            self.add_eqsta_single(
                                label=station_code,
                                phase="P",
                                error_type=error_type,
                                error=p_error,
                                error_report_type=error_type,
                                error_report=p_error,
                                prob_active=prob_active
                            )
                        if 'S' in phases:
                            self.add_eqsta_single(
                                label=station_code,
                                phase="S",
                                error_type=error_type,
                                error=s_error,
                                error_report_type=error_type,
                                error_report=s_error,
                                prob_active=prob_active
                            )
            else:
                # Local file
                self.add_station_from_inventory(kwargs['inventory'], sta_fmt=sta_fmt)
                # Add EQSTA commands for all stations
                for station in self.gtsrce_stations:
                    if 'P' in phases:
                        self.add_eqsta_single(
                            label=station.label,
                            phase="P",
                            error_type=error_type,
                            error=p_error,
                            error_report_type=error_type,
                            error_report=p_error,
                            prob_active=prob_active
                        )
                    if 'S' in phases:
                        self.add_eqsta_single(
                            label=station.label,
                            phase="S",
                            error_type=error_type,
                            error=s_error,
                            error_report_type=error_type,
                            error_report=s_error,
                            prob_active=prob_active
                        )

    def _set_velocity_model_by_name(self, model_name: str):
        """
        Set velocity model by predefined name
        
        Args:
            model_name: Name of the velocity model
        """
        if model_name == 'vdap_stratovolcano':
            self.layer.layers = [
                (0.0, 2.0),    # Surface layer
                (0.5, 3.0),    # Pyroclastic deposits
                (1.0, 3.8),    # Volcanic edifice
                (2.0, 4.8),    # Lava flows and consolidated volcanics
                (4.0, 5.8),    # Basement sediments
                (8.0, 6.2),    # Crystalline basement
                (15.0, 6.8),   # Lower crust
                (30.0, 8.0)    # Upper mantle
            ]
        elif model_name == 'basic_crust':
            self.layer.layers = [
                (0.0, 2.0),    # Surface layer
                (2.0, 4.0),    # Upper crust
                (8.0, 5.5),    # Lower crust
                (20.0, 6.8),   # Upper mantle
            ]
        else:
            # Default to basic model
            self.setup_basic_velocity_model()
