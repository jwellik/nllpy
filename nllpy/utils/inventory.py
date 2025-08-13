# =============================================================================
# nllpy/utils/inventory.py
# =============================================================================
"""
Station inventory parsing utilities
"""

import xml.etree.ElementTree as ET
from typing import List, Dict
from pathlib import Path


def parse_inventory(inventory, sta_fmt: str = "STA") -> List[Dict]:
    """
    Parse station inventory from various formats (non-XML files only)
    
    For XML files, use ObsPy's read_inventory() directly or pass an ObsPy Inventory object
    to add_station_from_inventory().

    Args:
        inventory: Path to inventory file (text formats only, not XML)
        sta_fmt: Station code format - "STA" for station only, "NET.STA" for network.station, "NET_STA" for network_station

    Returns:
        List of station dictionaries with keys: code, latitude, longitude, depth
    """
    inventory_path = Path(inventory)

    if not inventory_path.exists():
        raise FileNotFoundError(f"Inventory file not found: {inventory}")

    # Try to parse as FDSN format first
    try:
        return _parse_fdsn_inventory(inventory, sta_fmt=sta_fmt)
    except ValueError:
        # Fall back to simple text format
        return _parse_simple_inventory(inventory)


def _parse_stationxml(inventory_file: str, sta_fmt: str = "STA") -> List[Dict]:
    """Parse StationXML format"""
    tree = ET.parse(inventory_file)
    root = tree.getroot()

    # Handle namespace
    namespace = {'': 'http://www.fdsn.org/xml/station/1'}
    if root.tag.startswith('{'):
        namespace = {'': root.tag.split('}')[0][1:]}

    stations = []
    for network in root.findall('.//Network', namespace):
        net_code = network.get('code', '')
        for station in network.findall('.//Station', namespace):
            sta_code = station.get('code')
            lat = float(station.find('Latitude', namespace).text)
            lon = float(station.find('Longitude', namespace).text)
            elev = float(station.find('Elevation', namespace).text)

            # Convert elevation to depth (NLLoc uses depth below sea level)
            depth = -elev / 1000.0  # Convert m to km, flip sign

            # Choose station code format based on preference
            if sta_fmt == "NET.STA":
                code = f"{net_code}.{sta_code}"
            elif sta_fmt == "NET_STA":
                code = f"{net_code}_{sta_code}"
            elif sta_fmt == "NET.STA.LOC":
                code = f"{net_code}.{sta_code}."
            elif sta_fmt == "NET_STA_LOC":
                code = f"{net_code}_{sta_code}_"
            else:
                code = sta_code

            stations.append({
                'code': code,
                'latitude': lat,
                'longitude': lon,
                'depth': depth,
                'elevation': elev
            })

    return stations


def _parse_simple_inventory(inventory_file: str) -> List[Dict]:
    """Parse simple text format: CODE LAT LON ELEV"""
    stations = []

    with open(inventory_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) < 4:
                    print(f"Warning: Line {line_num} has insufficient columns, skipping")
                    continue

                try:
                    code = parts[0]
                    lat = float(parts[1])
                    lon = float(parts[2])
                    elev = float(parts[3])
                    depth = -elev / 1000.0  # Convert to km depth

                    stations.append({
                        'code': code,
                        'latitude': lat,
                        'longitude': lon,
                        'depth': depth,
                        'elevation': elev
                    })
                except ValueError as e:
                    print(f"Warning: Error parsing line {line_num}: {e}")
                    continue

    return stations


def _parse_fdsn_inventory(inventory_file: str, sta_fmt: str = "STA") -> List[Dict]:
    """
    Parse FDSN station format: NET|STA|LAT|LON|ELEV|SITENAME|START|END
    
    Args:
        inventory_file: Path to FDSN format file
        sta_fmt: Station code format - "STA" for station only, "NET.STA" for network.station, "NET_STA" for network_station
        
    Returns:
        List of station dictionaries with keys: code, latitude, longitude, depth
    """
    stations = []
    
    with open(inventory_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('|')
                if len(parts) < 5:
                    print(f"Warning: Line {line_num} has insufficient columns, skipping")
                    continue
                
                try:
                    net_code = parts[0].strip()
                    sta_code = parts[1].strip()
                    lat = float(parts[2])
                    lon = float(parts[3])
                    elev = float(parts[4])
                    depth = -elev / 1000.0  # Convert to km depth
                    
                    # Choose station code format based on preference
                    if sta_fmt == "NET.STA":
                        code = f"{net_code}.{sta_code}"
                    elif sta_fmt == "NET_STA":
                        code = f"{net_code}_{sta_code}"
                    elif sta_fmt == "NET.STA.LOC":
                        code = f"{net_code}.{sta_code}."
                    elif sta_fmt == "NET_STA_LOC":
                        code = f"{net_code}_{sta_code}_"
                    else:
                        code = sta_code
                    
                    stations.append({
                        'code': code,
                        'latitude': lat,
                        'longitude': lon,
                        'depth': depth,
                        'elevation': elev
                    })
                except ValueError as e:
                    print(f"Warning: Error parsing line {line_num}: {e}")
                    continue
    
    if not stations:
        raise ValueError("No valid stations found in FDSN format")
    
    return stations


def parse_obspy_inventory(inventory, sta_fmt: str = "STA"):
    """
    Parse ObsPy inventory object

    Args:
        inventory: ObsPy Inventory object
        sta_fmt: Station code format - "STA" for station only, "NET.STA" for network.station, "NET_STA" for network_station

    Returns:
        List of station dictionaries
    """
    stations = []

    for network in inventory:
        for station in network:
            lat = station.latitude
            lon = station.longitude
            elev = station.elevation
            
            # Choose station code format based on preference
            if sta_fmt == "NET.STA":
                code = f"{network.code}.{station.code}"
            elif sta_fmt == "NET_STA":
                code = f"{network.code}_{station.code}"
            elif sta_fmt == "NET.STA.LOC":
                code = f"{network.code}.{station.code}."
            elif sta_fmt == "NET_STA_LOC":
                code = f"{network.code}_{station.code}_"
            else:
                code = station.code
                
            depth = -elev / 1000.0  # Convert to km depth

            stations.append({
                'code': code,
                'latitude': lat,
                'longitude': lon,
                'depth': depth,
                'elevation': elev
            })

    return stations
