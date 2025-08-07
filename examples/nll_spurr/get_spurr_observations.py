"""
Get earthquake events and pick data for Mt. Spurr region using ObsPy IRIS client.
Writes events in NonLinLoc observation format using ObsPy's built-in NLLOC_OBS writer.
"""

import os
import re
import urllib.parse
from datetime import datetime, timedelta
from obspy.clients.fdsn import Client
from obspy import UTCDateTime

# Mt Spurr location
SPURR_LAT = 61.2989
SPURR_LON = -152.2539
SEARCH_RADIUS_DEG = 0.5  # ~50 km at this latitude


def get_spurr_events(start_date, end_date, client_name="USGS"):
    """
    Fetch earthquake events with pick data for Mt. Spurr region using ObsPy.
    Gets events first, then retrieves pick information for each event separately.
    
    Parameters:
    -----------
    start_date : datetime or UTCDateTime
        Start time for event search
    end_date : datetime or UTCDateTime  
        End time for event search
    client_name : str
        FDSN client name (default: "USGS")
        
    Returns:
    --------
    obspy.Catalog
        Catalog containing events with pick information
    """
    client = Client(client_name)
    
    # Convert to UTCDateTime if needed
    if isinstance(start_date, datetime):
        start_date = UTCDateTime(start_date)
    if isinstance(end_date, datetime):
        end_date = UTCDateTime(end_date)
    
    print(f"Fetching events from {client_name} for Mt. Spurr region...")
    print(f"Time range: {start_date} to {end_date}")
    print(f"Search radius: {SEARCH_RADIUS_DEG:.2f} degrees around {SPURR_LAT:.4f}, {SPURR_LON:.4f}")
    
    try:
        # First, get all events in the region
        catalog_initial = client.get_events(
            starttime=start_date,
            endtime=end_date,
            latitude=SPURR_LAT,
            longitude=SPURR_LON,
            maxradius=SEARCH_RADIUS_DEG,
            mindepth=-10,
            maxdepth=100
        )
        
        print(f"Found {len(catalog_initial)} events")
        
        # Now get pick information for each event separately
        from obspy import Catalog
        catalog = Catalog()
        
        for i, event in enumerate(catalog_initial):
            print(f"Getting pick information for event {i+1}/{len(catalog_initial)}...")
            
            # Get the event ID from the resource_id
            if event.origins and len(event.origins) > 0:
                rid = event.origins[0].resource_id.id
                print(f"  Resource ID: {rid}")
                
                # Extract event ID from resource_id (e.g., 'quakeml:earthquake.usgs.gov/product/origin/uw61501708/uw/1624049054710/product.xml')
                eventid = rid.split("/")[3]  # e.g., "uw61501708"
                print(f"  Event ID: {eventid}")
                
                # Get the event with pick information using the event ID
                try:
                    tmp_cat = client.get_events(eventid=eventid)
                    if len(tmp_cat) > 0:
                        catalog.append(tmp_cat[0])
                        print(f"  Added event with {len(tmp_cat[0].picks)} picks")
                    else:
                        print(f"  No event found for ID: {eventid}")
                except Exception as e:
                    print(f"  Error getting picks for event {eventid}: {e}")
                    # Add the original event without picks
                    catalog.append(event)
            else:
                print(f"  No origin information for event {i+1}")
                catalog.append(event)
        
        # Debug: Check final catalog
        total_picks = 0
        events_with_picks = 0
        for i, event in enumerate(catalog):
            pick_count = len(event.picks)
            total_picks += pick_count
            if pick_count > 0:
                events_with_picks += 1
                print(f"  Final Event {i+1}: {pick_count} picks")
                # Show first few picks
                for j, pick in enumerate(event.picks[:3]):
                    print(f"    Pick {j+1}: {pick.time} {pick.phase_hint} {pick.waveform_id}")
        
        print(f"Final catalog - Events with picks: {events_with_picks}/{len(catalog)}")
        print(f"Total picks: {total_picks}")
        
        return catalog
        
    except Exception as e:
        print(f"Error fetching events: {e}")
        return None


def clean_event_id(event_id):
    """
    Clean event ID to create a valid filename.
    Keeps query parameters and replaces special characters with underscores.
    """
    if not event_id:
        return None
    
    # Keep everything including query parameters
    # Replace any URL encoding or special characters that aren't valid in filenames
    event_id = re.sub(r'[^\w\-_.?=&]', '_', event_id)
    
    # Remove multiple consecutive underscores
    event_id = re.sub(r'_+', '_', event_id)
    
    # Remove leading/trailing underscores
    event_id = event_id.strip('_')
    
    # Ensure it's not empty
    if not event_id:
        return None
    
    return event_id


def write_catalog_summary(catalog, output_dir):
    """Write a summary of the catalog to a text file."""
    summary_file = os.path.join(output_dir, "catalog_summary.txt")
    
    with open(summary_file, 'w') as f:
        f.write("Mt. Spurr Earthquake Catalog Summary\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total events: {len(catalog)}\n")
        
        if len(catalog) > 0:
            # Time range
            times = [event.preferred_origin().time for event in catalog if event.preferred_origin()]
            if times:
                f.write(f"Time range: {min(times)} to {max(times)}\n")
            
            # Magnitude range
            mags = []
            for event in catalog:
                mag = event.preferred_magnitude()
                if mag and mag.mag is not None:
                    mags.append(mag.mag)
            if mags:
                f.write(f"Magnitude range: {min(mags):.1f} to {max(mags):.1f}\n")
            
            # Depth range
            depths = []
            for event in catalog:
                origin = event.preferred_origin()
                if origin and origin.depth is not None:
                    depths.append(origin.depth / 1000.0)  # Convert to km
            if depths:
                f.write(f"Depth range: {min(depths):.1f} to {max(depths):.1f} km\n")
        
        f.write("\nIndividual Events:\n")
        f.write("-" * 30 + "\n")
        
        for i, event in enumerate(catalog):
            origin = event.preferred_origin()
            if not origin:
                continue
                
            mag = event.preferred_magnitude()
            mag_str = f"M{mag.mag:.1f}" if mag and mag.mag else "M?"
            
            event_id = str(event.resource_id).split('/')[-1] if event.resource_id else f"Event_{i+1}"
            
            f.write(f"{event_id}: {origin.time} {mag_str} ")
            f.write(f"({origin.latitude:.4f}, {origin.longitude:.4f}) ")
            f.write(f"depth={origin.depth/1000.0:.1f}km " if origin.depth else "depth=?km ")
            f.write(f"picks={len(event.picks)}\n")


def main():
    """Main function to fetch Mt. Spurr events and write NLL_OBS files."""
    
    # Create output directory
    output_dir = "nll_spurr/obs/"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define time range for October 14, 2024
    start_time = UTCDateTime("2024-10-14T00:00:00")
    end_time = UTCDateTime("2024-10-14T23:59:59")
    
    # Alternative: try a longer time range to find events with picks
    # start_time = UTCDateTime("2024-01-01")
    # end_time = UTCDateTime("2024-12-31")
    
    # For testing with known data, try a longer time range
    # start_time = UTCDateTime("2023-01-01")
    # end_time = UTCDateTime("2024-12-31")
    
    # Get events from USGS with pick information
    catalog = get_spurr_events(start_time, end_time, client_name="USGS")
    
    if catalog is None or len(catalog) == 0:
        print("No events found or error occurred.")
        print("Try expanding the time range or search radius.")
        return
    
    print(f"\nProcessing {len(catalog)} events...")
    
    # Write each event as NLL_OBS file using ObsPy's built-in writer
    for i, event in enumerate(catalog):
        try:
            # Generate filename from event ID or timestamp
            origin = event.preferred_origin()
            if not origin:
                print(f"Skipping event {i+1} - no origin information")
                continue
                
            # Set phase_hint based on channel ending if it's None
            picks_modified = 0
            for pick in event.picks:
                if pick.phase_hint is None and pick.waveform_id and pick.waveform_id.channel_code:
                    if pick.waveform_id.channel_code.endswith('Z'):
                        pick.phase_hint = 'P'
                        print(f"  Set phase_hint for {pick.waveform_id.channel_code} to P")
                    else:
                        pick.phase_hint = 'S'
                        print(f"  Set phase_hint for {pick.waveform_id.channel_code} to S")
                    picks_modified += 1
            
            if picks_modified > 0:
                print(f"  Set phase_hint for {picks_modified} picks based on channel ending")
            
            # Create filename using event ID from origin resource_id
            if event.origins and len(event.origins) > 0:
                rid = event.origins[0].resource_id.id
                # Extract event ID from resource_id (e.g., 'quakeml:earthquake.usgs.gov/product/origin/uw61501708/uw/1624049054710/product.xml')
                event_id = rid.split("/")[3]  # e.g., "uw61501708"
                print(f"  Using event ID: {event_id}")
            else:
                # Fallback to timestamp-based ID
                event_id = f"evt_{origin.time.strftime('%Y%m%d_%H%M%S')}"
                print(f"  Using fallback event ID: {event_id}")
            
            filename = os.path.join(output_dir, f"{event_id}.obs")
            
            print(f"Writing event {i+1}/{len(catalog)}: {filename}")
            print(f"  Event has {len(event.picks)} picks")
            
            # Debug: Show pick details
            if len(event.picks) > 0:
                print(f"  First few picks:")
                for j, pick in enumerate(event.picks[:3]):
                    print(f"    {pick.time} {pick.phase_hint} {pick.waveform_id}")
            else:
                print(f"  No picks found for this event")
            
            # Write using ObsPy's NLLOC_OBS format
            event.write(filename, format="NLLOC_OBS")
            
        except Exception as e:
            print(f"Error writing event {i+1}: {e}")
            continue
    
    # Write catalog summary
    write_catalog_summary(catalog, output_dir)
    
    print(f"\nComplete! Files written to {output_dir}/")
    print(f"- {len(catalog)} .obs files")
    print(f"- 1 catalog_summary.txt file")
    
    # Print some statistics
    total_picks = sum(len(event.picks) for event in catalog)
    if len(catalog) > 0:
        print(f"\nStatistics:")
        print(f"- Total events: {len(catalog)}")
        print(f"- Total picks: {total_picks}")
        print(f"- Average picks per event: {total_picks/len(catalog):.1f}")
    
    # Print first few filenames as examples
    obs_files = [f for f in os.listdir(output_dir) if f.endswith('.obs')]
    if obs_files:
        print(f"\nExample files created:")
        for filename in sorted(obs_files)[:3]:
            print(f"  {filename}")
        if len(obs_files) > 3:
            print(f"  ... and {len(obs_files)-3} more")


if __name__ == "__main__":
    main()
    