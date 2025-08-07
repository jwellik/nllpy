# =============================================================================
# nllpy/cli/main.py
# =============================================================================
"""
Command line interface for NLLPy
"""

import argparse
import math
import sys
from pathlib import Path

from ..core.config import NLLocConfig
from ..templates.volcano import create_volcano_config
from ..templates.regional import create_regional_config


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Generate NLLoc control file components")

    subparsers = parser.add_subparsers(dest='command', help='Command to generate')

    # Shared inventory arguments for GTSRCE and EQSTA
    inventory_group = argparse.ArgumentParser(add_help=False)
    inventory_group.add_argument('inventory', help='Station inventory file or FDSN URL')
    inventory_group.add_argument('--lat', type=float, help='Center latitude for FDSN search')
    inventory_group.add_argument('--lon', type=float, help='Center longitude for FDSN search')
    inventory_group.add_argument('--rad_km', type=float, help='Search radius in km for FDSN')
    inventory_group.add_argument('--sta-fmt', choices=['STA', 'NET.STA', 'NET_STA'], default='STA',
                               help='Station code format (default: STA)')

    # GTSRCE command
    gtsrce_parser = subparsers.add_parser('gtsrce', help='Generate GTSRCE commands', 
                                        parents=[inventory_group])

    # EQSTA command
    eqsta_parser = subparsers.add_parser('eqsta', help='Generate EQSTA commands',
                                       parents=[inventory_group])
    eqsta_parser.add_argument('--p-error', type=float, default=0.0,
                             help='P phase timing error in seconds (default: 0.0)')
    eqsta_parser.add_argument('--s-error', type=float, default=0.0,
                             help='S phase timing error in seconds (default: 0.0)')
    eqsta_parser.add_argument('--phases', choices=['P', 'S', 'PS'], default='PS',
                             help='Phases to generate errors for (default: PS)')
    eqsta_parser.add_argument('--error-type', choices=['GAU', 'EXP'], default='GAU',
                             help='Error type (default: GAU)')
    eqsta_parser.add_argument('--prob-active', type=float, default=1.0,
                             help='Probability active (default: 1.0)')

    # LOCGRID command
    grid_parser = subparsers.add_parser('locgrid', help='Generate LOCGRID command')
    grid_parser.add_argument('--nx', type=int, help='Number of grid points in X direction')
    grid_parser.add_argument('--ny', type=int, help='Number of grid points in Y direction')
    grid_parser.add_argument('--nz', type=int, help='Number of grid points in Z direction')
    grid_parser.add_argument('--dx', type=float, default=1.0, help='Grid spacing in X direction (km)')
    grid_parser.add_argument('--dy', type=float, default=1.0, help='Grid spacing in Y direction (km)')
    grid_parser.add_argument('--dz', type=float, default=1.0, help='Grid spacing in Z direction (km)')
    grid_parser.add_argument('--dxy', type=float, help='Grid spacing for both X and Y directions (km)')
    grid_parser.add_argument('--dxyz', type=float, help='Grid spacing for all X, Y, and Z directions (km)')
    grid_parser.add_argument('--kmx', type=float, help='Grid size in X direction (km)')
    grid_parser.add_argument('--kmy', type=float, help='Grid size in Y direction (km)')
    grid_parser.add_argument('--kmz', type=float, help='Grid size in Z direction (km)')

    # VGGRID command
    vggrid_parser = subparsers.add_parser('vggrid', help='Generate VGGRID command')
    vggrid_parser.add_argument('--nx', type=int, help='Number of grid points in X direction')
    vggrid_parser.add_argument('--ny', type=int, help='Number of grid points in Y direction')
    vggrid_parser.add_argument('--nz', type=int, help='Number of grid points in Z direction')
    vggrid_parser.add_argument('--dx', type=float, default=1.0, help='Grid spacing in X direction (km)')
    vggrid_parser.add_argument('--dy', type=float, default=1.0, help='Grid spacing in Y direction (km)')
    vggrid_parser.add_argument('--dz', type=float, default=1.0, help='Grid spacing in Z direction (km)')
    vggrid_parser.add_argument('--dxy', type=float, help='Grid spacing for both X and Y directions (km)')
    vggrid_parser.add_argument('--dxyz', type=float, help='Grid spacing for all X, Y, and Z directions (km)')
    vggrid_parser.add_argument('--kmx', type=float, help='Grid size in X direction (km)')
    vggrid_parser.add_argument('--kmy', type=float, help='Grid size in Y direction (km)')
    vggrid_parser.add_argument('--kmz', type=float, help='Grid size in Z direction (km)')
    vggrid_parser.add_argument('--grid-type', choices=['SLOW_LEN', 'SLOW_LEN_NOCORR'], default='SLOW_LEN', 
                              help='Grid type (default: SLOW_LEN)')

    # Complete control file
    control_parser = subparsers.add_parser('control', help='Generate complete control file')
    control_parser.add_argument('--output', '-o', default='nll_control.in')
    control_parser.add_argument('--template', help='Template file or predefined template (volcano, regional)')
    control_parser.add_argument('--inventory', help='Station inventory file or FDSN URL')
    control_parser.add_argument('--lat', type=float, help='Origin latitude')
    control_parser.add_argument('--lon', type=float, help='Origin longitude')
    control_parser.add_argument('--elev', type=float, help='Origin elevation')
    control_parser.add_argument('--rad_km', type=float, help='Search radius in km for FDSN')
    control_parser.add_argument('--gridkm', help='Grid size in km (width,height,spacing)')
    control_parser.add_argument('--depthkm', help='Depth range in km (depth,spacing)')
    control_parser.add_argument('--sig', help='LOCSIG signature')
    control_parser.add_argument('--com', help='LOCCOM comment')
    control_parser.add_argument('--prefix', help='Output prefix for location files')
    control_parser.add_argument('--trans', help='Transform type (SDC, etc.)')
    control_parser.add_argument('--model', help='Velocity model name (vdap_stratovolcano, basic_crust)')
    control_parser.add_argument('--sta-fmt', choices=['STA', 'NET.STA', 'NET_STA'], default='STA',
                                help='Station code format (default: STA)')
    control_parser.add_argument('--p-error', type=float, default=0.0,
                             help='P phase timing error in seconds (default: 0.0)')
    control_parser.add_argument('--s-error', type=float, default=0.0,
                             help='S phase timing error in seconds (default: 0.0)')
    control_parser.add_argument('--phases', choices=['P', 'S', 'PS'], default='PS',
                             help='Phases to generate errors for (default: PS)')
    control_parser.add_argument('--error-type', choices=['GAU', 'EXP'], default='GAU',
                             help='Error type (default: GAU)')
    control_parser.add_argument('--prob-active', type=float, default=1.0,
                             help='Probability active (default: 1.0)')

    # FDSN event fetching parser
    fdsn_parser = subparsers.add_parser('getfdsnevents', help='Fetch events with picks from FDSN services')
    fdsn_parser.add_argument('--lat', type=float, required=True, help='Center latitude')
    fdsn_parser.add_argument('--lon', type=float, required=True, help='Center longitude')
    fdsn_parser.add_argument('--radiuskm', type=float, required=True, help='Search radius in kilometers')
    fdsn_parser.add_argument('--start', required=True, help='Start time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)')
    fdsn_parser.add_argument('--end', required=True, help='End time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)')
    fdsn_parser.add_argument('--client', default='USGS', help='FDSN client name (default: USGS)')
    fdsn_parser.add_argument('--mindepth', type=float, default=-10, help='Minimum depth in km (default: -10)')
    fdsn_parser.add_argument('--maxdepth', type=float, default=100, help='Maximum depth in km (default: 100)')
    fdsn_parser.add_argument('--output', default='events.xml', help='Output QuakeML file (default: events.xml)')
    fdsn_parser.add_argument('--convert', action='store_true', help='Also convert to NonLinLoc .obs files')
    fdsn_parser.add_argument('--obs-dir', default='obs_files', help='Output directory for .obs files (if --convert)')
    fdsn_parser.add_argument('--obs-pattern', help='Filename pattern for .obs files (if --convert)')
    fdsn_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')

    # QuakeML to NonLinLoc conversion
    quakeml_parser = subparsers.add_parser('quakeml2obs', help='Convert QuakeML file to NonLinLoc .obs files')
    quakeml_parser.add_argument('input', help='Input QuakeML file')
    quakeml_parser.add_argument('--output-dir', '-o', default='obs', help='Output directory for .obs files (default: obs)')
    quakeml_parser.add_argument('--pattern', help='Filename pattern (e.g., "event_{event_id}.obs")')
    quakeml_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    quakeml_parser.add_argument('--event-index', type=int, help='Convert only specific event by index (0-based)')
    quakeml_parser.add_argument('--single-output', help='Output filename for single event conversion')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'gtsrce':
        gtsrce_command(args)
    elif args.command == 'eqsta':
        eqsta_command(args)
    elif args.command == 'locgrid':
        locgrid_command(args)
    elif args.command == 'vggrid':
        vggrid_command(args)
    elif args.command == 'control':
        control_command(args)
    elif args.command == 'getfdsnevents':
        getfdsnevents_command(args)
    elif args.command == 'quakeml2obs':
        quakeml2obs_command(args)


def load_stations_from_inventory(args):
    """
    Shared function to load stations from inventory (file or FDSN)
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        tuple: (config, station_codes, result_dict)
    """
    config = NLLocConfig()
    station_codes = []
    result = None
    
    if args.inventory.startswith('http'):
        # FDSN URL
        if not all([args.lat, args.lon, args.rad_km]):
            print("Error: --lat, --lon, and --rad_km required for FDSN URLs")
            sys.exit(1)
        
        radius = args.rad_km / 111.0  # Convert km to degrees
        result = config.create_from_fdsn_stations(
            latitude=args.lat,
            longitude=args.lon,
            radius=radius,
            fdsn_url=args.inventory,
            sta_fmt=args.sta_fmt
        )
        station_codes = result['station_codes']
        print(f"Downloaded {result['stations_downloaded']} stations from {args.inventory}")
    else:
        # Local file
        config.add_station_from_inventory(args.inventory, sta_fmt=args.sta_fmt)
        station_codes = [station.label for station in config.gtsrce_stations]
        print(f"Loaded {len(station_codes)} stations from {args.inventory}")
    
    return config, station_codes, result


def gtsrce_command(args):
    """Generate GTSRCE commands"""
    config, station_codes, result = load_stations_from_inventory(args)
    print(config.get_gtsrce_section())


def eqsta_command(args):
    """Generate EQSTA commands"""
    config, station_codes, result = load_stations_from_inventory(args)
    
    # Generate EQSTA commands for each station
    for station in station_codes:
        if 'P' in args.phases:
            config.add_eqsta_single(
                label=station,
                phase="P",
                error_type=args.error_type,
                error=args.p_error,
                error_report_type=args.error_type,
                error_report=args.p_error,
                prob_active=args.prob_active
            )
        if 'S' in args.phases:
            config.add_eqsta_single(
                label=station,
                phase="S",
                error_type=args.error_type,
                error=args.s_error,
                error_report_type=args.error_type,
                error_report=args.s_error,
                prob_active=args.prob_active
            )
    
    print(config.get_eqsta_section())


def locgrid_command(args):
    """Generate LOCGRID command"""
    config = NLLocConfig()
    
    # Handle dxy and dxyz arguments
    dx = args.dx
    dy = args.dy
    dz = args.dz
    
    if args.dxyz is not None:
        if any([args.dx != 1.0, args.dy != 1.0, args.dz != 1.0]):
            print("Warning: --dxyz specified along with individual --dx, --dy, or --dz. Using --dxyz value.")
        dx = dy = dz = args.dxyz
    elif args.dxy is not None:
        if args.dx != 1.0 or args.dy != 1.0:
            print("Warning: --dxy specified along with individual --dx or --dy. Using --dxy value.")
        dx = dy = args.dxy
    
    # Calculate nx, ny, nz from kmx, kmy, kmz if provided
    nx = args.nx
    ny = args.ny
    nz = args.nz
    km_conversion_comment = ""
    
    if args.kmx is not None:
        if args.nx is not None:
            print("Warning: Both --nx and --kmx specified. Using --nx value.")
        else:
            nx = int(math.ceil(args.kmx / dx))
            km_conversion_comment = f"# nx={nx} calculated from kmx={args.kmx}km / dx={dx}km\n"
    
    if args.kmy is not None:
        if args.ny is not None:
            print("Warning: Both --ny and --kmy specified. Using --ny value.")
        else:
            ny = int(math.ceil(args.kmy / dy))
            km_conversion_comment += f"# ny={ny} calculated from kmy={args.kmy}km / dy={dy}km\n"
    
    if args.kmz is not None:
        if args.nz is not None:
            print("Warning: Both --nz and --kmz specified. Using --nz value.")
        else:
            nz = int(math.ceil(args.kmz / dz))
            km_conversion_comment += f"# nz={nz} calculated from kmz={args.kmz}km / dz={dz}km\n"
    
    # Set default values if none provided
    if nx is None:
        nx = 100
    if ny is None:
        ny = 100
    if nz is None:
        nz = 50
    
    # Create a new LocGridCommand to trigger automatic origin calculation
    from ..core.commands import LocGridCommand
    locgrid = LocGridCommand(
        num_grid_x=nx,
        num_grid_y=ny,
        num_grid_z=nz,
        d_grid_x=dx,
        d_grid_y=dy,
        d_grid_z=dz
    )
    
    # Print the conversion comment if any km values were used
    if km_conversion_comment:
        print(km_conversion_comment.rstrip())
    
    print("# Location grid")
    print(str(locgrid))


def vggrid_command(args):
    """Generate VGGRID command"""
    config = NLLocConfig()
    
    # Handle dxy and dxyz arguments
    dx = args.dx
    dy = args.dy
    dz = args.dz
    
    if args.dxyz is not None:
        if any([args.dx != 1.0, args.dy != 1.0, args.dz != 1.0]):
            print("Warning: --dxyz specified along with individual --dx, --dy, or --dz. Using --dxyz value.")
        dx = dy = dz = args.dxyz
    elif args.dxy is not None:
        if args.dx != 1.0 or args.dy != 1.0:
            print("Warning: --dxy specified along with individual --dx or --dy. Using --dxy value.")
        dx = dy = args.dxy
    
    # Calculate nx, ny, nz from kmx, kmy, kmz if provided
    nx = args.nx
    ny = args.ny
    nz = args.nz
    km_conversion_comment = ""
    
    if args.kmx is not None:
        if args.nx is not None:
            print("Warning: Both --nx and --kmx specified. Using --nx value.")
        else:
            nx = int(math.ceil(args.kmx / dx))
            km_conversion_comment = f"# nx={nx} calculated from kmx={args.kmx}km / dx={dx}km\n"
    
    if args.kmy is not None:
        if args.ny is not None:
            print("Warning: Both --ny and --kmy specified. Using --ny value.")
        else:
            ny = int(math.ceil(args.kmy / dy))
            km_conversion_comment += f"# ny={ny} calculated from kmy={args.kmy}km / dy={dy}km\n"
    
    if args.kmz is not None:
        if args.nz is not None:
            print("Warning: Both --nz and --kmz specified. Using --nz value.")
        else:
            nz = int(math.ceil(args.kmz / dz))
            km_conversion_comment += f"# nz={nz} calculated from kmz={args.kmz}km / dz={dz}km\n"
    
    # Set default values if none provided
    if nx is None:
        nx = 200
    if ny is None:
        ny = 200
    if nz is None:
        nz = 50
    
    # Create a new VelGridCommand to trigger automatic origin calculation
    from ..core.commands import VelGridCommand
    vggrid = VelGridCommand(
        num_grid_x=nx,
        num_grid_y=ny,
        num_grid_z=nz,
        d_grid_x=dx,
        d_grid_y=dy,
        d_grid_z=dz,
        grid_type=args.grid_type
    )
    
    # Print the conversion comment if any km values were used
    if km_conversion_comment:
        print(km_conversion_comment.rstrip())
    
    print("# Velocity grid")
    print(str(vggrid))


def control_command(args):
    """Generate complete control file"""
    config = NLLocConfig()
    
    # Check if template is a file or predefined template
    if args.template:
        if Path(args.template).exists():
            # Load from existing file
            if not config.load_from_file(args.template):
                print(f"Error: Could not load template file {args.template}")
                sys.exit(1)
            print(f"Loaded template from {args.template}")
        elif args.template == 'volcano':
            # Use predefined volcano template
            if not args.lat or not args.lon:
                print("Error: --lat and --lon required for volcano template")
                sys.exit(1)
            config = create_volcano_config(args.lat, args.lon)
        elif args.template == 'regional':
            # Use predefined regional template
            if not args.lat or not args.lon:
                print("Error: --lat and --lon required for regional template")
                sys.exit(1)
            config = create_regional_config(args.lat, args.lon)
        else:
            print(f"Error: Template '{args.template}' not found")
            sys.exit(1)
    
    # Modify configuration from command line arguments
    config.modify_from_args(
        lat=args.lat,
        lon=args.lon,
        elev=args.elev,
        rad_km=args.rad_km,
        gridkm=args.gridkm,
        depthkm=args.depthkm,
        sig=args.sig,
        com=args.com,
        prefix=args.prefix,
        trans=args.trans,
        model=args.model,
        inventory=args.inventory,
        sta_fmt=args.sta_fmt,
        p_error=args.p_error,
        s_error=args.s_error,
        phases=args.phases,
        error_type=args.error_type,
        prob_active=args.prob_active
    )

    # Write control file
    config.write_complete_control_file(args.output)
    print(f"Control file written to {args.output}")


def getfdsnevents_command(args):
    """Fetch events with picks from FDSN services"""
    from datetime import datetime
    from ..utils.quakeml import (
        get_fdsn_events,
        convert_quakeml_to_obs_files,
        print_conversion_summary
    )
    
    # Parse time arguments
    try:
        # Try parsing as datetime first
        if 'T' in args.start:
            start_time = datetime.fromisoformat(args.start.replace('Z', '+00:00'))
        else:
            start_time = datetime.fromisoformat(args.start)
            
        if 'T' in args.end:
            end_time = datetime.fromisoformat(args.end.replace('Z', '+00:00'))
        else:
            end_time = datetime.fromisoformat(args.end)
    except ValueError as e:
        print(f"Error parsing time format: {e}")
        print("Use format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
        return
    
    print(f"Fetching events from {args.client}...")
    print(f"Location: {args.lat:.4f}, {args.lon:.4f}")
    print(f"Radius: {args.radiuskm:.1f} km")
    print(f"Time range: {start_time} to {end_time}")
    print(f"Output file: {args.output}")
    
    # Fetch events
    catalog = get_fdsn_events(
        lat=args.lat,
        lon=args.lon,
        maxradius_km=args.radiuskm,
        t1=start_time,
        t2=end_time,
        client_name=args.client,
        mindepth=args.mindepth,
        maxdepth=args.maxdepth
    )
    
    if catalog is None:
        print("Error fetching events")
        return
    
    if len(catalog) == 0:
        print("No events found in the specified region and time range.")
        return
    
    # Save to QuakeML file
    try:
        catalog.write(args.output, format="QUAKEML")
        print(f"Saved {len(catalog)} events to {args.output}")
    except Exception as e:
        print(f"Error saving QuakeML file: {e}")
        return
    
    # Convert to .obs files if requested
    if args.convert:
        print(f"\nConverting to NonLinLoc .obs files...")
        result = convert_quakeml_to_obs_files(
            quakeml_file=args.output,
            output_dir=args.obs_dir,
            event_id_pattern=args.obs_pattern,
            overwrite=args.overwrite
        )
        print_conversion_summary(result)


def quakeml2obs_command(args):
    """Convert QuakeML file to NonLinLoc .obs files"""
    from ..utils.quakeml import (
        convert_quakeml_to_obs_files, 
        convert_quakeml_to_obs_file,
        print_conversion_summary
    )
    
    try:
        if args.event_index is not None:
            # Convert single event
            if not args.single_output:
                print("Error: --single-output required when using --event-index")
                sys.exit(1)
            
            result = convert_quakeml_to_obs_file(
                quakeml_file=args.input,
                output_file=args.single_output,
                event_index=args.event_index
            )
            
            print(f"Converted event {args.event_index} to {args.single_output}")
            print(f"Event ID: {result['event_id']}")
            print(f"Picks: {result['pick_count']}")
            
        else:
            # Convert all events
            result = convert_quakeml_to_obs_files(
                quakeml_file=args.input,
                output_dir=args.output_dir,
                event_id_pattern=args.pattern,
                overwrite=args.overwrite
            )
            
            print_conversion_summary(result)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()