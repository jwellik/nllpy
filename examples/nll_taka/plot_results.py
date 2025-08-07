import matplotlib.pyplot as plt
import numpy as np
from obspy import read_events


def main():
    print("Comparing USGS Catalog to NonLinLoc Catalog")

    # Read catalogs
    catalog_usgs = read_events("./obs/events.xml")
    catalog_nll = read_events("./loc/taka.sum.grid0.loc.hyp")
    
    print(f"USGS Catalog: {len(catalog_usgs)} events")
    print(f"NonLinLoc Catalog: {len(catalog_nll)} events")
    print()

    # Extract coordinates from catalogs
    usgs_lons = []
    usgs_lats = []
    usgs_depths = []
    
    nll_lons = []
    nll_lats = []
    nll_depths = []
    
    # Extract USGS catalog coordinates
    for event in catalog_usgs:
        origin = event.preferred_origin() or event.origins[0]
        usgs_lons.append(origin.longitude)
        usgs_lats.append(origin.latitude)
        usgs_depths.append(origin.depth / 1000.0)  # Convert to km
    
    # Extract NonLinLoc catalog coordinates
    for event in catalog_nll:
        origin = event.preferred_origin() or event.origins[0]
        nll_lons.append(origin.longitude)
        nll_lats.append(origin.latitude)
        nll_depths.append(origin.depth / 1000.0)  # Convert to km
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), 
                                   gridspec_kw={'height_ratios': [2, 1]})
    
    # Top plot: Latitude vs Longitude (map view)
    ax1.scatter(usgs_lons, usgs_lats, c='blue', alpha=0.5, s=30, 
                label=f'USGS Catalog ({len(usgs_lons)} events)')
    ax1.scatter(nll_lons, nll_lats, c='red', alpha=0.5, s=30, 
                label=f'NonLinLoc Catalog ({len(nll_lons)} events)')
    
    ax1.set_xlabel('Longitude (°)')
    ax1.set_ylabel('Latitude (°)')
    ax1.set_title('Event Locations - Map View')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    
    # Bottom plot: Depth vs Longitude (cross section)
    ax2.scatter(usgs_lons, usgs_depths, c='blue', alpha=0.5, s=30, 
                label=f'USGS Catalog ({len(usgs_lons)} events)')
    ax2.scatter(nll_lons, nll_depths, c='red', alpha=0.5, s=30, 
                label=f'NonLinLoc Catalog ({len(nll_lons)} events)')
    
    ax2.set_xlabel('Longitude (°)')
    ax2.set_ylabel('Depth (km)')
    ax2.set_title('Event Locations - Cross Section')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.invert_yaxis()  # Positive depth down
    
    # Print statistics
    print("=== CATALOG STATISTICS ===")
    print(f"USGS Catalog:")
    print(f"  Number of events: {len(usgs_lons)}")
    if usgs_lons:
        print(f"  Longitude range: {min(usgs_lons):.3f}° to {max(usgs_lons):.3f}°")
        print(f"  Latitude range: {min(usgs_lats):.3f}° to {max(usgs_lats):.3f}°")
        print(f"  Depth range: {min(usgs_depths):.1f} to {max(usgs_depths):.1f} km")
    
    print(f"\nNonLinLoc Catalog:")
    print(f"  Number of events: {len(nll_lons)}")
    if nll_lons:
        print(f"  Longitude range: {min(nll_lons):.3f}° to {max(nll_lons):.3f}°")
        print(f"  Latitude range: {min(nll_lats):.3f}° to {max(nll_lats):.3f}°")
        print(f"  Depth range: {min(nll_depths):.1f} to {max(nll_depths):.1f} km")
    
    # Adjust layout and display
    plt.tight_layout()
    plt.savefig("./taka_results.png", dpi=300)
    
    print("\nDone.")


if __name__ == "__main__":
    main()
