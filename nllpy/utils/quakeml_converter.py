# =============================================================================
# nllpy/utils/quakeml_converter.py
# =============================================================================
"""
Utilities for converting QuakeML files to NonLinLoc observation format
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from obspy import read_events, Catalog
from obspy.core.event import Event


def clean_event_id(event_id: str) -> str:
    """
    Clean event ID to create a valid filename.
    Replaces special characters with underscores.
    
    Args:
        event_id: Original event ID
        
    Returns:
        Cleaned event ID suitable for filenames
    """
    if not event_id:
        return "unknown_event"
    
    # Replace any special characters that aren't valid in filenames
    cleaned = re.sub(r'[^\w\-_.]', '_', event_id)
    
    # Remove multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    
    # Ensure it's not empty
    if not cleaned:
        return "unknown_event"
    
    return cleaned


def extract_event_id(event: Event) -> str:
    """
    Extract a unique event ID from an ObsPy Event object.
    
    Args:
        event: ObsPy Event object
        
    Returns:
        Event ID string
    """
    # Try to get ID from origin resource_id first
    if event.origins and len(event.origins) > 0:
        rid = event.origins[0].resource_id.id
        if rid:
            # Extract event ID from resource_id (e.g., 'quakeml:earthquake.usgs.gov/product/origin/uw61501708/uw/1624049054710/product.xml')
            parts = rid.split("/")
            if len(parts) >= 4:
                return parts[3]  # e.g., "uw61501708"
    
    # Try to get ID from event resource_id
    if event.resource_id:
        rid = str(event.resource_id)
        if rid:
            # Extract last part of the resource_id
            parts = rid.split("/")
            if len(parts) > 0:
                return parts[-1]
    
    # Fallback to timestamp-based ID
    if event.preferred_origin():
        origin = event.preferred_origin()
        return f"evt_{origin.time.strftime('%Y%m%d_%H%M%S')}"
    
    # Last resort
    return "unknown_event"


def convert_quakeml_to_obs_files(quakeml_file: str, output_dir: str, 
                                event_id_pattern: Optional[str] = None,
                                overwrite: bool = False) -> Dict[str, Any]:
    """
    Convert a QuakeML file containing multiple events to individual NonLinLoc .obs files.
    
    Args:
        quakeml_file: Path to input QuakeML file
        output_dir: Directory to write .obs files
        event_id_pattern: Optional pattern to extract event IDs (e.g., "{event_id}")
        overwrite: Whether to overwrite existing files
        
    Returns:
        Dictionary with conversion statistics
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Read QuakeML file
    try:
        catalog = read_events(quakeml_file)
        print(f"Read {len(catalog)} events from {quakeml_file}")
    except Exception as e:
        raise ValueError(f"Error reading QuakeML file {quakeml_file}: {e}")
    
    if len(catalog) == 0:
        return {
            "input_file": quakeml_file,
            "output_dir": str(output_path),
            "total_events": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "total_picks": 0,
            "output_files": []
        }
    
    # Process each event
    successful = 0
    failed = 0
    total_picks = 0
    output_files = []
    
    for i, event in enumerate(catalog):
        try:
            # Extract event ID
            event_id = extract_event_id(event)
            
            # Clean event ID for filename
            clean_id = clean_event_id(event_id)
            
            # Generate output filename
            if event_id_pattern:
                # Use custom pattern
                filename = event_id_pattern.format(
                    event_id=clean_id,
                    index=i+1,
                    total=len(catalog)
                )
            else:
                # Use default pattern
                filename = f"{clean_id}.obs"
            
            output_file = output_path / filename
            
            # Check if file exists
            if output_file.exists() and not overwrite:
                print(f"Skipping event {i+1} - file exists: {filename}")
                continue
            
            # Write event to .obs file using safe writer
            from .quakeml import safe_write_nlloc_obs, create_nlloc_obs_file
            if safe_write_nlloc_obs(event, str(output_file)):
                # Count picks
                pick_count = len(event.picks)
                total_picks += pick_count
                
                print(f"Event {i+1}/{len(catalog)}: {filename} ({pick_count} picks)")
                output_files.append(str(output_file))
                successful += 1
            else:
                print(f"Failed to write event {i+1} to {filename}")
                failed += 1
            
        except Exception as e:
            print(f"Error converting event {i+1}: {e}")
            failed += 1
            continue
    
    # Return statistics
    return {
        "input_file": quakeml_file,
        "output_dir": str(output_path),
        "total_events": len(catalog),
        "successful_conversions": successful,
        "failed_conversions": failed,
        "total_picks": total_picks,
        "output_files": output_files
    }


def convert_quakeml_to_obs_file(quakeml_file: str, output_file: str, 
                               event_index: int = 0) -> Dict[str, Any]:
    """
    Convert a single event from a QuakeML file to a NonLinLoc .obs file.
    
    Args:
        quakeml_file: Path to input QuakeML file
        output_file: Path to output .obs file
        event_index: Index of event to convert (default: 0, first event)
        
    Returns:
        Dictionary with conversion information
    """
    # Read QuakeML file
    try:
        catalog = read_events(quakeml_file)
    except Exception as e:
        raise ValueError(f"Error reading QuakeML file {quakeml_file}: {e}")
    
    if len(catalog) == 0:
        raise ValueError(f"No events found in {quakeml_file}")
    
    if event_index >= len(catalog):
        raise ValueError(f"Event index {event_index} out of range (0-{len(catalog)-1})")
    
    # Get the specified event
    event = catalog[event_index]
    
    # Create output directory if needed
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write event to .obs file using safe writer
    from .quakeml import safe_write_nlloc_obs, create_nlloc_obs_file
    if not safe_write_nlloc_obs(event, str(output_path)):
        raise ValueError(f"Failed to write event to {output_path}")
    
    # Extract event information
    event_id = extract_event_id(event)
    pick_count = len(event.picks)
    
    return {
        "input_file": quakeml_file,
        "output_file": str(output_path),
        "event_index": event_index,
        "event_id": event_id,
        "pick_count": pick_count,
        "total_events_in_file": len(catalog)
    }


def print_conversion_summary(stats: Dict[str, Any]) -> None:
    """
    Print a summary of the conversion results.
    
    Args:
        stats: Statistics dictionary from conversion functions
    """
    print("\n" + "="*60)
    print("QUAKEML TO NONLINLOC CONVERSION SUMMARY")
    print("="*60)
    print(f"Input file: {stats['input_file']}")
    print(f"Output directory: {stats['output_dir']}")
    print(f"Total events in file: {stats['total_events']}")
    print(f"Successful conversions: {stats['successful_conversions']}")
    print(f"Failed conversions: {stats['failed_conversions']}")
    print(f"Total picks: {stats['total_picks']}")
    
    if stats['total_events'] > 0:
        avg_picks = stats['total_picks'] / stats['successful_conversions']
        print(f"Average picks per event: {avg_picks:.1f}")
    
    if stats['output_files']:
        print(f"\nOutput files ({len(stats['output_files'])}):")
        for filename in sorted(stats['output_files'])[:5]:  # Show first 5
            print(f"  {Path(filename).name}")
        if len(stats['output_files']) > 5:
            print(f"  ... and {len(stats['output_files'])-5} more")
    
    print("="*60) 