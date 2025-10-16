#!/usr/bin/env python3
"""
Script to find the nearest metro station for each pandal and calculate the distance.
"""

import json
import math
from typing import Dict, List, Tuple, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of first point in decimal degrees
        lat2, lon2: Latitude and longitude of second point in decimal degrees
    
    Returns:
        Distance in meters
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    return c * r

def find_nearest_metro_station(pandal_lat: float, pandal_lon: float, metro_stations: List[Dict]) -> Tuple[Dict, float]:
    """
    Find the nearest metro station to a given pandal location.
    
    Args:
        pandal_lat: Pandal latitude
        pandal_lon: Pandal longitude
        metro_stations: List of metro station dictionaries
    
    Returns:
        Tuple of (nearest_metro_station, distance_in_meters)
    """
    min_distance = float('inf')
    nearest_station = None
    
    for station in metro_stations:
        distance = haversine_distance(
            pandal_lat, pandal_lon,
            station['latitude'], station['longitude']
        )
        
        if distance < min_distance:
            min_distance = distance
            nearest_station = station
    
    return nearest_station, min_distance

def process_pandals_with_metro_data():
    """
    Process all pandals and find their nearest metro stations.
    """
    print("Loading pandals data...")
    with open('/Users/shubhayu/Documents/opensource/pujogone/pandals_data.json', 'r', encoding='utf-8') as f:
        pandals_data = json.load(f)
    
    print("Loading metro stations data...")
    with open('/Users/shubhayu/Documents/opensource/pujogone/kolkata_metro_stations.json', 'r', encoding='utf-8') as f:
        metro_stations = json.load(f)
    
    print(f"Processing {len(pandals_data['data'])} pandals...")
    
    # Process each pandal
    updated_pandals = []
    for i, pandal in enumerate(pandals_data['data']):
        if i % 100 == 0:
            print(f"Processing pandal {i+1}/{len(pandals_data['data'])}")
        
        # Find nearest metro station
        nearest_station, distance = find_nearest_metro_station(
            pandal['latitude'], 
            pandal['longitude'], 
            metro_stations
        )
        
        # Update pandal data with metro information
        updated_pandal = pandal.copy()
        updated_pandal['nearest_metro_id'] = nearest_station['short_code']
        updated_pandal['nearest_metro_name'] = nearest_station['name']
        updated_pandal['nearest_metro_location'] = nearest_station['location']
        updated_pandal['nearest_metro_lines'] = nearest_station['lines']
        updated_pandal['nearest_metro_latitude'] = nearest_station['latitude']
        updated_pandal['nearest_metro_longitude'] = nearest_station['longitude']
        updated_pandal['nearest_metro_distance_meters'] = round(distance, 2)
        
        updated_pandals.append(updated_pandal)
    
    # Create the output structure
    output_data = {
        "statusCode": 200,
        "data": updated_pandals,
        "metadata": {
            "total_pandals": len(updated_pandals),
            "metro_stations_used": len(metro_stations),
            "processing_completed": True
        }
    }
    
    # Save the updated data
    output_file = '/Users/shubhayu/Documents/opensource/pujogone/pandals_with_metro_data.json'
    print(f"Saving updated data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully processed {len(updated_pandals)} pandals!")
    print(f"Updated data saved to: {output_file}")
    
    # Print some statistics
    distances = [pandal['nearest_metro_distance_meters'] for pandal in updated_pandals]
    print(f"\nDistance Statistics:")
    print(f"Minimum distance: {min(distances):.2f} meters")
    print(f"Maximum distance: {max(distances):.2f} meters")
    print(f"Average distance: {sum(distances)/len(distances):.2f} meters")

if __name__ == "__main__":
    process_pandals_with_metro_data()
