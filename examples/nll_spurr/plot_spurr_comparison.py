#!/usr/bin/env python3
"""
Plot comparison between USGS earthquake locations (obs/) and NLLOC locations (loc/).

This script creates a two-panel figure:
1. Top panel: Latitude vs Longitude (map view)
2. Bottom panel: Longitude vs Depth (cross-section view)

USGS locations are plotted in black, NLLOC locations in red.
"""

import matplotlib.pyplot as plt
import numpy as np
from obspy import read_events
import re
from pathlib import Path

def parse_usgs_catalog(catalog_file):
    """
    Parse the USGS catalog summary file to extract earthquake locations.
    
    Returns:
        list of tuples: (lat, lon, depth, magnitude, time)
    """
    events = []
    
    with open(catalog_file, 'r') as f:
        lines = f.readlines()
    
    # Find the "Individual Events" section
    start_idx = None
    for i, line in enumerate(lines):
        if "Individual Events:" in line:
            start_idx = i + 2  # Skip the header line
            break
    
    if start_idx is None:
        print("Could not find 'Individual Events' section in catalog file")
        return events
    
    # Parse each event line
    for line in lines[start_idx:]:
        line = line.strip()
        if not line or line.startswith('---'):
            continue
            
        # Parse lines like: "93317148: 2024-10-14T22:58:54.890000Z M-0.5 (61.3130, -152.2540) depth=1.7km picks=16"
        # or: "query?eventid=ak024d8ishgn&format=quakeml: 2024-10-14T13:46:18.335000Z M1.5 (60.8527, -151.8335) depth=81.9km picks=0"
        
        # Extract coordinates using regex
        coord_match = re.search(r'\(([-\d.]+),\s*([-\d.]+)\)', line)
        if not coord_match:
            continue
            
        lat = float(coord_match.group(1))
        lon = float(coord_match.group(2))
        
        # Extract depth
        depth_match = re.search(r'depth=([-\d.]+)km', line)
        if not depth_match:
            continue
        depth = float(depth_match.group(1))
        
        # Extract magnitude
        mag_match = re.search(r'M([-\d.]+)', line)
        if not mag_match:
            continue
        magnitude = float(mag_match.group(1))
        
        # Extract time (simplified - just use the timestamp)
        time_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)', line)
        if not time_match:
            continue
        time_str = time_match.group(1)
        
        events.append((lat, lon, depth, magnitude, time_str))
    
    return events

def read_nlloc_events(hyp_file):
    """
    Read NLLOC events using ObsPy.
    
    Returns:
        list of tuples: (lat, lon, depth, magnitude, time)
    """
    events = []
    
    try:
        # Read the NLLOC hyp file
        cat = read_events(hyp_file, format="NLLOC_HYP")
        
        for event in cat:
            origin = event.origins[0]
            magnitude = event.magnitudes[0].mag if event.magnitudes else None
            
            events.append((
                origin.latitude,
                origin.longitude,
                origin.depth / 1000.0,  # Convert from m to km
                magnitude,
                origin.time.isoformat()
            ))
            
    except Exception as e:
        print(f"Error reading NLLOC file: {e}")
    
    return events

def plot_comparison(usgs_events, nlloc_events, output_file=None):
    """
    Create comparison plot with two subplots.
    
    Args:
        usgs_events: List of USGS event tuples (lat, lon, depth, mag, time)
        nlloc_events: List of NLLOC event tuples (lat, lon, depth, mag, time)
        output_file: Optional output file path
    """
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Extract coordinates
    usgs_lats = [e[0] for e in usgs_events]
    usgs_lons = [e[1] for e in usgs_events]
    usgs_depths = [e[2] for e in usgs_events]
    
    nlloc_lats = [e[0] for e in nlloc_events]
    nlloc_lons = [e[1] for e in nlloc_events]
    nlloc_depths = [e[2] for e in nlloc_events]
    
    # Top panel: Latitude vs Longitude (map view)
    ax1.scatter(usgs_lons, usgs_lats, c='black', s=50, alpha=0.7, 
                edgecolors='black', linewidth=1, label='USGS Locations')
    ax1.scatter(nlloc_lons, nlloc_lats, c='red', s=50, alpha=0.7,
                edgecolors='red', linewidth=1, label='NLLOC Locations')
    
    ax1.set_xlabel('Longitude (°)')
    ax1.set_ylabel('Latitude (°)')
    ax1.set_title('Earthquake Locations: USGS vs NLLOC')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Set reasonable axis limits and make the plot square
    all_lons = usgs_lons + nlloc_lons
    all_lats = usgs_lats + nlloc_lats
    lon_margin = (max(all_lons) - min(all_lons)) * 0.1
    lat_margin = (max(all_lats) - min(all_lats)) * 0.1
    
    ax1.set_xlim(min(all_lons) - lon_margin, max(all_lons) + lon_margin)
    ax1.set_ylim(min(all_lats) - lat_margin, max(all_lats) + lat_margin)
    
    # Make the top plot square
    ax1.set_aspect('equal')
    
    # Bottom panel: Longitude vs Depth (cross-section)
    ax2.scatter(usgs_lons, usgs_depths, c='black', s=50, alpha=0.7,
                edgecolors='black', linewidth=1, label='USGS Locations')
    ax2.scatter(nlloc_lons, nlloc_depths, c='red', s=50, alpha=0.7,
                edgecolors='red', linewidth=1, label='NLLOC Locations')
    
    ax2.set_xlabel('Longitude (°)')
    ax2.set_ylabel('Depth (km)')
    ax2.set_title('Depth Cross-Section: USGS vs NLLOC')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Invert y-axis so depths below sea level are positive
    ax2.invert_yaxis()
    
    # Set reasonable axis limits for depth plot
    all_depths = usgs_depths + nlloc_depths
    depth_margin = (max(all_depths) - min(all_depths)) * 0.1 if len(all_depths) > 1 else 1.0
    
    ax2.set_xlim(min(all_lons) - lon_margin, max(all_lons) + lon_margin)
    ax2.set_ylim(max(all_depths) + depth_margin, min(all_depths) - depth_margin)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_file}")
    
    plt.show()

def main():
    """Main function to run the comparison."""
    
    # File paths
    base_dir = Path(__file__).parent
    usgs_catalog = base_dir / "obs" / "catalog_summary.txt"
    nlloc_hyp = base_dir / "loc" / "volcano.sum.grid0.loc.hyp"
    
    print("Reading USGS catalog...")
    usgs_events = parse_usgs_catalog(usgs_catalog)
    print(f"Found {len(usgs_events)} USGS events")
    
    print("Reading NLLOC results...")
    nlloc_events = read_nlloc_events(nlloc_hyp)
    print(f"Found {len(nlloc_events)} NLLOC events")
    
    # Print summary
    print("\nUSGS Events:")
    for i, (lat, lon, depth, mag, time) in enumerate(usgs_events):
        print(f"  {i+1}: ({lat:.4f}, {lon:.4f}) depth={depth:.1f}km M{mag}")
    
    print("\nNLLOC Events:")
    for i, (lat, lon, depth, mag, time) in enumerate(nlloc_events):
        mag_str = f"M{mag}" if mag is not None else "M?"
        print(f"  {i+1}: ({lat:.4f}, {lon:.4f}) depth={depth:.1f}km {mag_str}")
    
    # Create comparison plot
    print("\nCreating comparison plot...")
    plot_comparison(usgs_events, nlloc_events, 
                   output_file=base_dir / "spurr_comparison.png")

if __name__ == "__main__":
    main() 