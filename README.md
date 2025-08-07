# NLLPy

A Python package for generating NonLinLoc earthquake location control files, with special focus on volcano seismology applications.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

NLLPy provides a Python interface for generating control files for the [NonLinLoc](http://alomax.free.fr/nlloc/) earthquake location software. It's designed to simplify the process of setting up earthquake location workflows, particularly for volcano monitoring and regional seismology applications.

### Key Features

- **Modular Design**: Generate individual command sections or complete control files
- **Template System**: Pre-configured setups for volcano monitoring and regional earthquake location
- **ObsPy Integration**: Easy integration with existing ObsPy workflows
- **Command Line Interface**: Unix-style command line tools for quick operations
- **Flexible Configuration**: Dataclass-based configuration with sensible defaults
- **Station Inventory Support**: Parse FDSN StationXML and simple text formats, or download from an FDSN url

## Installation

We recommend installing nllpy in a virtual environment. To install with Conda, follow these instructions:

```bash
# Create a new conda environment
conda create -n nllpy python=3.8
conda activate nllpy

# Install scientific computing packages
conda install numpy pandas matplotlib scipy obspy

# Install nllpy from source files
cd nllpy
pip install -e .
```

## Quick Start

### Command Line Usage

Generate GTSRCE commands from a station inventory:
```bash
# From StationXML file
nllpy gtsrce stations.xml > gtsrce.in

# From FDSN format file
nllpy gtsrce stations.txt > gtsrce.in

# Use network.station format if needed
nllpy gtsrce stations.xml --sta-fmt NET.STA > gtsrce.in

# Use network_station format (underscore separator)
nllpy gtsrce stations.txt --sta-fmt NET_STA > gtsrce.in
```

Generate LOCGRID with custom parameters:
```bash
# Using traditional nx, ny, nz parameters
nllpy locgrid --nx 151 --ny 151 --nz 71 --dx 0.2 --dy 0.2 --dz 0.3

# Using kmx, kmy, kmz parameters (automatically calculates nx, ny, nz)
nllpy locgrid --kmx 30 --kmy 30 --kmz 20 --dx 0.2 --dy 0.2 --dz 0.3

# Mixed usage (kmx with traditional ny, nz)
nllpy locgrid --kmx 25 --ny 101 --nz 51 --dx 0.5 --dy 0.5 --dz 0.5
```

Generate VGGRID with custom parameters:
```bash
# Using traditional nx, ny, nz parameters
nllpy vggrid --nx 200 --ny 200 --nz 50 --dx 1.0 --dy 1.0 --dz 1.0

# Using kmx, kmy, kmz parameters (automatically calculates nx, ny, nz)
nllpy vggrid --kmx 100 --kmy 100 --kmz 50 --dx 0.5 --dy 0.5 --dz 1.0

# With custom grid type
nllpy vggrid --kmx 50 --kmy 50 --kmz 25 --dx 0.5 --dy 0.5 --dz 0.5 --grid-type SLOW_LEN_NOCORR
```

Generate a complete volcano monitoring configuration:
```bash
nllpy control --template volcano --lat 46.51 --lon 8.48 --inventory stations.xml --output volcano.in

# Use network.station format if needed
nllpy control --template volcano --lat 46.51 --lon 8.48 --inventory stations.xml --sta-fmt NET.STA --output volcano.in

# Use network_station format (underscore separator)
nllpy control --template volcano --lat 46.51 --lon 8.48 --inventory stations.xml --sta-fmt NET_STA --output volcano.in

# Customize EQSTA error values when using inventory
nllpy control --template volcano --lat 46.51 --lon 8.48 --inventory stations.xml --p-error 0.15 --s-error 0.25 --output volcano.in

# Generate only P phase errors
nllpy control --template volcano --lat 46.51 --lon 8.48 --inventory stations.xml --phases P --p-error 0.1 --output volcano.in
```

### Python API

Basic usage with templates:
```python
import nllpy

# Create volcano monitoring configuration
config = nllpy.create_volcano_config(lat_orig=46.51, lon_orig=8.48)
config.add_station_from_inventory("stations.xml")  # Uses station codes only
# Note: EQSTA commands are automatically generated when using inventory files
config.write_complete_control_file("volcano_location.in")

# Use network.station format if needed
config.add_station_from_inventory("stations.xml", sta_fmt="NET.STA")

# Use network_station format (underscore separator)
config.add_station_from_inventory("stations.xml", sta_fmt="NET_STA")

# Add stations from FDSN format file
config.add_station_from_fdsn("stations.txt", sta_fmt="NET.STA")
```

Detailed configuration:
```python
from nllpy import NLLocConfig

# Create configuration
config = NLLocConfig()

# Set coordinate system
config.trans.transformation = "SDC" 
config.trans.lat_orig = 46.51037
config.trans.lon_orig = 8.47576

# Configure high-resolution grid for volcano monitoring
config.locgrid.d_grid_x = 0.2  # 200m resolution
config.locgrid.d_grid_y = 0.2
config.locgrid.d_grid_z = 0.3

# Add stations
config.add_station("VT01", 46.510, 8.475, -1.5)
config.add_station_from_inventory("network_stations.xml")

# Generate specific sections
print(config.get_gtsrce_section())
print(config.get_locgrid_section())

# Write complete control file
config.write_complete_control_file("my_location.in")
```

### ObsPy Integration

```python
from obspy import read_inventory
import nllpy

# Read inventory with ObsPy
inv = read_inventory("station_metadata.xml")

# Create configuration
config = nllpy.create_volcano_config(lat_orig=46.51, lon_orig=8.48)

# Add stations from ObsPy inventory  
from nllpy.utils.inventory import parse_obspy_inventory
stations = parse_obspy_inventory(inv)
for station in stations:
    config.add_station(**station)

config.write_complete_control_file("volcano.in")
```

## Templates

### Volcano Monitoring Template

Optimized for local volcano seismology with high-resolution grids and shallow velocity models:

```python
config = nllpy.create_volcano_config(lat_orig=46.51, lon_orig=8.48)
```

**Features:**
- High-resolution grid (200m spacing)
- Shallow velocity model with low-velocity surface layers
- Fine search parameters for small events
- Requires minimum 6 phases with 3 S-phases
- Optimized for depths 0-15 km

### Regional Template

Optimized for regional earthquake location with larger coverage areas:

```python
config = nllpy.create_regional_config(lat_orig=46.0, lon_orig=8.0)
```

**Features:**
- Large-area grid (200km x 200km)
- Regional crustal velocity model
- Coarser resolution for computational efficiency
- Requires minimum 8 phases with 4 S-phases
- Optimized for depths 0-50 km

## Configuration Options

### Grid Configuration

```python
# Method 1: Direct parameter setting
config.locgrid.num_grid_x = 101      # Number of X grid points
config.locgrid.num_grid_y = 101      # Number of Y grid points  
config.locgrid.num_grid_z = 51       # Number of Z grid points
config.locgrid.d_grid_x = 0.2        # X spacing (km)
config.locgrid.d_grid_y = 0.2        # Y spacing (km)
config.locgrid.d_grid_z = 0.3        # Z spacing (km)
config.locgrid.orig_grid_x = -10.0   # X origin (km)
config.locgrid.orig_grid_y = -10.0   # Y origin (km)
config.locgrid.orig_grid_z = -2.0    # Z origin (km)

# Method 1b: Direct command creation with convenience parameters
from nllpy.core.commands import LocGridCommand, VelGridCommand

# Location grid with d_xy convenience parameter
locgrid = LocGridCommand(
    num_grid_x=100,
    num_grid_y=100,
    num_grid_z=50,
    d_xy=0.5  # Sets both d_grid_x and d_grid_y to 0.5
)

# Velocity grid with d_xyz convenience parameter
vggrid = VelGridCommand(
    num_grid_x=200,
    num_grid_y=200,
    num_grid_z=50,
    d_xyz=0.5  # Sets d_grid_x, d_grid_y, and d_grid_z all to 0.5
)

# Method 2: Using km dimensions (similar to CLI --kmx, --kmy, --kmz)
config.setup_grid_from_km(
    kmx=50.0,    # Grid size in X direction (km)
    kmy=30.0,    # Grid size in Y direction (km)
    kmz=20.0,    # Grid size in Z direction (km)
    dx=0.5,      # Grid spacing in X direction (km)
    dy=0.5,      # Grid spacing in Y direction (km)
    dz=0.25      # Grid spacing in Z direction (km)
)

# Method 2b: Using convenience spacing parameters
config.setup_grid_from_km(
    kmx=50.0,    # Grid size in X direction (km)
    kmy=30.0,    # Grid size in Y direction (km)
    kmz=20.0,    # Grid size in Z direction (km)
    d_xy=0.5,    # Set both dx and dy to 0.5 km
    dz=0.25      # Z spacing (km)
)

config.setup_grid_from_km(
    kmx=100.0,   # Grid size in X direction (km)
    kmy=100.0,   # Grid size in Y direction (km)
    kmz=50.0,    # Grid size in Z direction (km)
    d_xyz=0.5    # Set dx, dy, and dz all to 0.5 km
)

# Method 3: Basic grid setup (simplified)
config.setup_basic_grid(
    grid_size=50.0,      # Grid size in km (applies to X and Y)
    grid_spacing=0.5,    # Grid spacing in km (applies to X and Y)
    depth_range=20.0,    # Depth range in km
    depth_spacing=0.25   # Depth spacing in km
)
```

### Velocity Model

```python
# Layer-based velocity model
config.layer.layers = [
    (0.0, 3.5, 0.0, 2.0, 0.0, 2.7, 0.0),   # (depth, vp, vs, density, etc.)
    (1.0, 4.5, 0.0, 2.6, 0.0, 2.7, 0.0),
    (3.0, 6.0, 0.0, 3.5, 0.0, 2.8, 0.0),
    (10.0, 7.5, 0.0, 4.3, 0.0, 3.0, 0.0),
    (30.0, 8.1, 0.0, 4.7, 0.0, 3.3, 0.0)
]
```

### Search Parameters

```python
# Location search configuration
config.locsearch.search_type = "OCT"
config.locsearch.min_node_size = 0.001      # Fine resolution
config.locsearch.max_num_nodes = 50000

# Location method requirements
config.locmethod.min_num_phases = 6
config.locmethod.min_num_s_phases = 3
config.locmethod.max_dist_sta_grid = 30.0
```

## Station Inventory Formats

### StationXML (FDSN Standard)

```xml
<?xml version="1.0"?>
<FDSNStationXML>
  <Network code="XX">
    <Station code="STA1">
      <Latitude>46.5103</Latitude>
      <Longitude>8.4758</Longitude>
      <Elevation>1500.0</Elevation>
    </Station>
  </Network>
</FDSNStationXML>
```

### Simple Text Format

```
# CODE LAT LON ELEV(m)
VT01 46.5103 8.4758 1500.0
VT02 46.5150 8.4800 1200.0
VT03 46.5050 8.4700 1800.0
```

### FDSN Format

```
# NET|STA|LAT|LON|ELEV|SITENAME|START|END
AV|SPBG|61.2591|-152.3722|1087.0|Barrier Glacier, Mount Spurr, Alaska|2004-09-09T00:00:00|2599-12-31T23:59:59
AV|SPBL|61.3764|-151.8947|927.0|Spurr Beluga Lake, Mount Spurr, Alaska|2018-09-05T00:00:00|2599-12-31T23:59:59
```

## Station Error Definitions (EQSTA)

NLLPy automatically generates EQSTA commands for station error definitions when using the `control` command with an inventory. EQSTA commands define timing errors for P and S phases at each station.

### Command Line Usage

```bash
# Generate EQSTA commands separately (with custom error values)
nllpy eqsta stations.xml --p-error 0.1 --s-error 0.2 > eqsta.in

# Generate EQSTA commands from FDSN (with custom error values)
nllpy eqsta https://service.iris.washington.edu --lat 46.51 --lon 8.48 --rad_km 50.0 --p-error 0.1 --s-error 0.2

# Generate only P phase errors (with custom error value)
nllpy eqsta stations.xml --phases P --p-error 0.1

# Generate only S phase errors (with custom error value)
nllpy eqsta stations.xml --phases S --s-error 0.2

# Use exponential error distribution (with custom error values)
nllpy eqsta stations.xml --p-error 0.1 --s-error 0.2 --error-type EXP
```

### Automatic EQSTA Generation

When using the `control` command with an inventory, EQSTA commands are automatically generated:

```bash
# EQSTA commands automatically included with default values (P: 0.0s, S: 0.0s)
nllpy control --template volcano --lat 46.51 --lon 8.48 --inventory stations.xml --output volcano.in

# Customize EQSTA error values
nllpy control --template volcano --lat 46.51 --lon 8.48 --inventory stations.xml --p-error 0.15 --s-error 0.25 --output volcano.in

# Generate only P phase errors
nllpy control --template volcano --lat 46.51 --lon 8.48 --inventory stations.xml --phases P --p-error 0.1 --output volcano.in
```

### Python API

```python
from nllpy import NLLocConfig

config = NLLocConfig()

# Add stations
config.add_station("VT01", 46.51, 8.47, 1500.0)
config.add_station("VT02", 46.52, 8.48, 1200.0)

# Add EQSTA commands manually (with custom error values)
config.add_eqsta_single("VT01", phase="P", error=0.1, error_report=0.1)
config.add_eqsta_single("VT01", phase="S", error=0.2, error_report=0.2)
config.add_eqsta_single("VT02", phase="P", error=0.1, error_report=0.1)
config.add_eqsta_single("VT02", phase="S", error=0.2, error_report=0.2)

# Or use helper method for both P and S phases (with custom error values)
config._add_eqsta_for_station("VT01", p_error=0.1, s_error=0.2)

# Get EQSTA section
print(config.get_eqsta_section())
```

## FDSN Event Fetching and QuakeML Conversion

NLLPy provides utilities to fetch earthquake events with picks from FDSN services and convert QuakeML files to NonLinLoc observation format (.obs files).

### Command Line Usage

#### Fetch Events from FDSN

```bash
# Fetch events from Mt. Spurr region
nllpy getfdsnevents --lat 61.2989 --lon -152.2539 --radiuskm 50.0 \
    --start 2024-10-14 --end 2024-10-15 --output spurr_events.xml

# Fetch events and convert to .obs files in one step
nllpy getfdsnevents --lat 61.2989 --lon -152.2539 --radiuskm 50.0 \
    --start 2024-10-14 --end 2024-10-15 --convert --obs-dir spurr_obs

# Use different FDSN client
nllpy getfdsnevents --lat 51.873 --lon -178.006 --radiuskm 50.0 \
    --start 2023-02-13 --end 2023-02-14 --client IRIS --output taka_events.xml

# Specify depth range
nllpy getfdsnevents --lat 61.2989 --lon -152.2539 --radiuskm 50.0 \
    --start 2024-10-14 --end 2024-10-15 --mindepth 0 --maxdepth 50
```

#### Convert QuakeML to NonLinLoc

```bash
# Convert all events in a QuakeML file
nllpy quakeml2obs events.xml --output-dir obs_files

# Convert with custom filename pattern
nllpy quakeml2obs events.xml --pattern "event_{event_id}.obs" --output-dir obs_files

# Convert single event
nllpy quakeml2obs events.xml --event-index 0 --single-output first_event.obs
```

### Python API

```python
from nllpy.utils.quakeml import get_fdsn_events, convert_quakeml_to_obs_files
from datetime import datetime

# Fetch events with picks from FDSN
catalog = get_fdsn_events(
    lat=61.2989,           # Center latitude
    lon=-152.2539,         # Center longitude
    maxradius_km=50.0,     # Search radius in km
    t1=datetime(2024, 10, 14, 0, 0, 0),  # Start time
    t2=datetime(2024, 10, 14, 23, 59, 59), # End time
    client_name="USGS"     # FDSN client
)

# Save to QuakeML file
catalog.write("events.xml", format="QUAKEML")

# Convert all events
result = convert_quakeml_to_obs_files(
    quakeml_file="events.xml",
    output_dir="obs_files",
    overwrite=True
)

# Convert with custom pattern
result = convert_quakeml_to_obs_files(
    quakeml_file="events.xml",
    output_dir="obs_files",
    event_id_pattern="event_{event_id}_obs.obs"
)

# Convert single event
from nllpy.utils.quakeml import convert_quakeml_to_obs_file

result = convert_quakeml_to_obs_file(
    quakeml_file="events.xml",
    output_file="single_event.obs",
    event_index=0
)

# Assign phase hints to picks based on channel endings
from nllpy.utils.quakeml import assign_picks

catalog = assign_picks(catalog, verbose=True)
```

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py` - Basic configuration and usage patterns
- `volcano_monitoring.py` - Complete volcano monitoring setup
- `spurr_alaska.py` - Earthquake location example at Mt Spurr volcano, Alaska
- `quakeml_conversion_example.py` - QuakeML to NonLinLoc conversion examples
- `fdsn_events_example.py` - FDSN event fetching and conversion examples

## Command Line Reference

### Main Commands

```bash
nllpy gtsrce <inventory>           # Generate GTSRCE commands
nllpy locgrid [options]            # Generate LOCGRID command
nllpy vggrid [options]             # Generate VGGRID command
nllpy control [options]            # Generate complete control file
nllpy getfdsnevents [options]      # Fetch events with picks from FDSN services
nllpy quakeml2obs <file> [options] # Convert QuakeML to NonLinLoc .obs files
```

### Options

**gtsrce options:**
- `--sta-fmt`: Station code format - "STA" (default), "NET.STA", or "NET_STA"

**Supported inventory formats:**
- StationXML (FDSN standard)
- FDSN pipe-delimited format (NET|STA|LAT|LON|ELEV|...)
- Simple text format (CODE LAT LON ELEV)
- FDSN url (provide url, lat, lon, radius) -- stations downloaded to FDSN pipe-delimitted file

**locgrid options:**
- `--nx, --ny, --nz`: Grid dimensions (default: 101, 101, 51)

**getfdsnevents options:**
- `--lat, --lon`: Center coordinates (required)
- `--radiuskm`: Search radius in kilometers (required)
- `--start, --end`: Time range in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format (required)
- `--client`: FDSN client name (default: USGS)
- `--mindepth, --maxdepth`: Depth range in km (default: -10, 100)
- `--output`: Output QuakeML file (default: events.xml)
- `--convert`: Also convert to NonLinLoc .obs files
- `--obs-dir`: Output directory for .obs files (if --convert, default: obs_files)
- `--obs-pattern`: Filename pattern for .obs files (if --convert)
- `--overwrite`: Overwrite existing files
- `--dx, --dy, --dz`: Grid spacing in km (default: 1.0, 1.0, 1.0)

**control options:**
- `--template`: Use predefined template (`volcano` or `regional`)
- `--lat, --lon`: Origin coordinates (required for templates)
- `--inventory`: Station inventory file
- `--output, -o`: Output filename (default: `loc.in`)
- `--sta-fmt`: Station code format - "STA" (default), "NET.STA", or "NET_STA"

**quakeml2obs options:**
- `--output-dir, -o`: Output directory for .obs files (default: `obs`)
- `--pattern`: Filename pattern (e.g., `"event_{event_id}.obs"`)
- `--overwrite`: Overwrite existing files
- `--event-index`: Convert only specific event by index (0-based)
- `--single-output`: Output filename for single event conversion

## Development

### Setup Development Environment

```bash
git clone https://github.com/jwellik/nllpy
cd nllpy
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black nllpy/
flake8 nllpy/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [NonLinLoc](http://alomax.free.fr/nlloc/) by Anthony Lomax for the underlying location software
- [ObsPy](https://docs.obspy.org/) for seismological data handling capabilities

## References

- [NonLinLoc Documentation](http://alomax.free.fr/nlloc/)
- [ObsPy Documentation](https://docs.obspy.org/)
- [FDSN StationXML Format](https://www.fdsn.org/xml/station/)

## Support

For questions, issues, or feature requests, please:

1. Check the [documentation](https://pynlloc.readthedocs.io/)
2. Search existing [issues](https://github.com/jwellik/pynlloc/issues)
3. Create a new issue with a clear description of your problem

---

**Author:** Jay Wellik (jwellik@usgs.gov)  
**Version:** 0.1.0  
**Python:** 3.8+