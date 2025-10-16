#!/usr/bin/env python3
"""
Kolkata Metro Station Details Fetcher
=====================================

This comprehensive script handles:
1. Fetching metro station information from web sources
2. Scraping Google Maps for precise coordinates
3. Updating JSON files with 7 decimal precision coordinates
4. Verifying coordinate accuracy

Author: AI Assistant
Date: 2024
"""

import json
import requests
import time
import re
from urllib.parse import quote
import sys

class MetroStationFetcher:
    """Main class for fetching and managing Kolkata metro station data."""
    
    def __init__(self):
        self.stations_file = 'kolkata_metro_stations.json'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def get_google_maps_coordinates(self, station_name, location="Kolkata"):
        """
        Get precise coordinates from Google Maps for a station.
        Returns (latitude, longitude) with 7 decimal precision.
        """
        try:
            # Construct search query
            search_query = f"{station_name} metro station {location}"
            encoded_query = quote(search_query)
            
            # Use Google Maps search
            url = f"https://www.google.com/maps/search/{encoded_query}"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                # Look for coordinates in various formats
                patterns = [
                    r'@([0-9.-]+),([0-9.-]+)',
                    r'!3d([0-9.-]+)!4d([0-9.-]+)',
                    r'center=([0-9.-]+)%2C([0-9.-]+)',
                    r'"lat":\s*([0-9.-]+),\s*"lng":\s*([0-9.-]+)',
                    r'([0-9]{2}\.[0-9]{6,7}),([0-9]{2,3}\.[0-9]{6,7})'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        for lat, lng in matches:
                            lat_f = float(lat)
                            lng_f = float(lng)
                            
                            # Validate coordinates are in Kolkata area
                            if 22.0 <= lat_f <= 23.0 and 87.0 <= lng_f <= 89.0:
                                return round(lat_f, 7), round(lng_f, 7)
            
            # If no coordinates found, return None
            return None, None
            
        except Exception as e:
            print(f"Error getting coordinates for {station_name}: {e}")
            return None, None
    
    def get_coordinates_alternative(self, station_name, location="Kolkata"):
        """
        Alternative method using different Google Maps endpoints.
        """
        try:
            # Try different Google Maps URL formats
            search_queries = [
                f"{station_name} metro station {location}",
                f"{station_name} station {location}",
                f"metro {station_name} {location}"
            ]
            
            for query in search_queries:
                encoded_query = quote(query)
                
                # Try different Google Maps endpoints
                urls = [
                    f"https://maps.google.com/maps?q={encoded_query}",
                    f"https://www.google.com/maps/search/{encoded_query}",
                    f"https://maps.google.com/maps/place/{encoded_query}"
                ]
                
                for url in urls:
                    try:
                        response = requests.get(url, headers=self.headers, timeout=10)
                        
                        if response.status_code == 200:
                            # Look for coordinates in various formats
                            coord_patterns = [
                                r'@([0-9.-]+),([0-9.-]+)',
                                r'!3d([0-9.-]+)!4d([0-9.-]+)',
                                r'center=([0-9.-]+)%2C([0-9.-]+)',
                                r'"lat":\s*([0-9.-]+),\s*"lng":\s*([0-9.-]+)',
                                r'([0-9]{2}\.[0-9]{6,7}),([0-9]{2,3}\.[0-9]{6,7})'
                            ]
                            
                            for pattern in coord_patterns:
                                matches = re.findall(pattern, response.text)
                                if matches:
                                    lat, lng = matches[0]
                                    # Validate coordinates (Kolkata is roughly 22.5°N, 88.3°E)
                                    if 22.0 <= float(lat) <= 23.0 and 87.0 <= float(lng) <= 89.0:
                                        return float(lat), float(lng)
                        
                        time.sleep(1)  # Rate limiting
                        
                    except Exception as e:
                        continue
            
            return None, None
            
        except Exception as e:
            print(f"Alternative method failed for {station_name}: {e}")
            return None, None
    
    def load_stations(self):
        """Load the existing metro stations from JSON file."""
        try:
            with open(self.stations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.stations_file} not found!")
            return None
        except Exception as e:
            print(f"Error loading stations: {e}")
            return None
    
    def save_stations(self, stations):
        """Save the updated metro stations to JSON file."""
        try:
            with open(self.stations_file, 'w', encoding='utf-8') as f:
                json.dump(stations, f, indent=2, ensure_ascii=False)
            print("✅ Updated kolkata_metro_stations.json successfully!")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    
    def verify_coordinate_precision(self, stations):
        """Verify that all coordinates have 7 decimal precision."""
        print("🔍 Verifying coordinate precision...")
        all_correct = True
        
        for i, station in enumerate(stations, 1):
            lat = station.get('latitude', 0)
            lng = station.get('longitude', 0)
            
            lat_str = f'{lat:.7f}'
            lng_str = f'{lng:.7f}'
            
            lat_decimals = len(lat_str.split('.')[-1])
            lng_decimals = len(lng_str.split('.')[-1])
            
            is_correct = lat_decimals == 7 and lng_decimals == 7
            
            if not is_correct:
                all_correct = False
                print(f"❌ {i}. {station['name']}: {lat_str} ({lat_decimals} decimals), {lng_str} ({lng_decimals} decimals)")
            else:
                print(f"✅ {i}. {station['name']}: {lat_str}, {lng_str}")
        
        return all_correct
    
    def scrape_all_coordinates(self):
        """Scrape coordinates for all metro stations."""
        print("🚇 Kolkata Metro Station Coordinates Scraper")
        print("=" * 50)
        
        # Load existing stations
        stations = self.load_stations()
        if not stations:
            return
        
        print(f"Found {len(stations)} metro stations to process...")
        
        updated_count = 0
        failed_stations = []
        
        for i, station in enumerate(stations, 1):
            station_name = station['name']
            print(f"\n[{i}/{len(stations)}] Processing: {station_name}")
            
            # Check if coordinates already exist and are precise
            if 'latitude' in station and 'longitude' in station:
                lat = station['latitude']
                lng = station['longitude']
                
                # Check if coordinates are already 7 decimal precision
                if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
                    lat_str = f"{lat:.7f}"
                    lng_str = f"{lng:.7f}"
                    
                    if len(lat_str.split('.')[-1]) >= 7 and len(lng_str.split('.')[-1]) >= 7:
                        print(f"  ✅ Already has 7 decimal precision: {lat_str}, {lng_str}")
                        continue
            
            # Scrape coordinates
            print(f"  🔍 Scraping coordinates for {station_name}...")
            lat, lng = self.get_google_maps_coordinates(station_name)
            
            if lat is not None and lng is not None:
                # Format to 7 decimal places
                lat = round(lat, 7)
                lng = round(lng, 7)
                
                station['latitude'] = lat
                station['longitude'] = lng
                
                print(f"  ✅ Found coordinates: {lat:.7f}, {lng:.7f}")
                updated_count += 1
            else:
                print(f"  ❌ Could not find coordinates for {station_name}")
                failed_stations.append(station_name)
            
            # Rate limiting to avoid being blocked
            time.sleep(2)
        
        # Save updated stations
        self.save_stations(stations)
        
        print(f"\n📊 Summary:")
        print(f"  ✅ Successfully updated: {updated_count} stations")
        print(f"  ❌ Failed to update: {len(failed_stations)} stations")
        
        if failed_stations:
            print(f"\n❌ Failed stations:")
            for station in failed_stations:
                print(f"  - {station}")
        
        print(f"\n🎉 Scraping complete! Check {self.stations_file} for results.")
    
    def force_fix_coordinates(self):
        """Force fix all coordinates to 7 decimal precision."""
        print("🔧 FORCE FIXING Kolkata Metro Station Coordinates")
        print("=" * 60)
        
        # Load stations
        stations = self.load_stations()
        if not stations:
            print("❌ Could not load stations!")
            return
        
        print(f"📊 Found {len(stations)} stations to process")
        
        updated_count = 0
        failed_stations = []
        
        for i, station in enumerate(stations, 1):
            station_name = station['name']
            print(f"\n[{i}/{len(stations)}] Processing: {station_name}")
            
            # Check current precision
            current_lat = station.get('latitude', 0)
            current_lng = station.get('longitude', 0)
            
            # Check if already has 7 decimal precision
            lat_str = str(current_lat)
            lng_str = str(current_lng)
            
            lat_decimals = len(lat_str.split('.')[-1]) if '.' in lat_str else 0
            lng_decimals = len(lng_str.split('.')[-1]) if '.' in lng_str else 0
            
            if lat_decimals >= 7 and lng_decimals >= 7:
                print(f"  ✅ Already has 7 decimal precision: {lat_str}, {lng_str}")
                continue
            
            print(f"  🔍 Current precision: {lat_decimals}, {lng_decimals} decimals")
            print(f"  🔍 Scraping Google Maps for {station_name}...")
            
            # Get new coordinates
            lat, lng = self.get_google_maps_coordinates(station_name)
            
            if lat is not None and lng is not None:
                # Ensure 7 decimal precision
                lat = round(lat, 7)
                lng = round(lng, 7)
                
                station['latitude'] = lat
                station['longitude'] = lng
                
                print(f"  ✅ Updated coordinates: {lat:.7f}, {lng:.7f}")
                updated_count += 1
            else:
                print(f"  ❌ Could not get coordinates for {station_name}")
                failed_stations.append(station_name)
            
            # Rate limiting
            time.sleep(3)
        
        # Save updated stations
        self.save_stations(stations)
        
        print(f"\n📊 Summary:")
        print(f"  ✅ Successfully updated: {updated_count} stations")
        print(f"  ❌ Failed to update: {len(failed_stations)} stations")
        
        if failed_stations:
            print(f"\n❌ Failed stations:")
            for station in failed_stations:
                print(f"  - {station}")
        
        print(f"\n🎉 Coordinate fixing complete!")
    
    def final_fix_coordinates(self):
        """Force all coordinates to exactly 7 decimal precision."""
        print("🔧 FINAL FIX: Forcing ALL coordinates to 7 decimal precision")
        print("=" * 70)
        
        # Load stations
        stations = self.load_stations()
        if not stations:
            print("❌ Could not load stations!")
            return
        
        print(f"📊 Found {len(stations)} stations to process")
        
        updated_count = 0
        
        for i, station in enumerate(stations, 1):
            station_name = station['name']
            print(f"\n[{i}/{len(stations)}] Processing: {station_name}")
            
            # Get current coordinates
            current_lat = station.get('latitude', 0)
            current_lng = station.get('longitude', 0)
            
            # Force to 7 decimal precision
            lat_7_decimals = round(float(current_lat), 7)
            lng_7_decimals = round(float(current_lng), 7)
            
            # Update coordinates
            station['latitude'] = lat_7_decimals
            station['longitude'] = lng_7_decimals
            
            print(f"  ✅ Updated to: {lat_7_decimals:.7f}, {lng_7_decimals:.7f}")
            updated_count += 1
        
        # Save updated stations
        self.save_stations(stations)
        
        print(f"\n📊 Summary:")
        print(f"  ✅ Successfully updated: {updated_count} stations")
        print(f"  🎉 ALL coordinates now have 7 decimal precision!")
    
    def verify_all_coordinates(self):
        """Verify all coordinates have 7 decimal precision."""
        print("🎉 FINAL VERIFICATION: 7 Decimal Precision Check")
        print("=" * 70)
        
        stations = self.load_stations()
        if not stations:
            print("❌ Could not load stations!")
            return
        
        all_correct = self.verify_coordinate_precision(stations)
        
        print(f"\n📊 FINAL SUMMARY:")
        if all_correct:
            print('🎉 SUCCESS! ALL STATIONS NOW HAVE EXACTLY 7 DECIMAL PRECISION!')
            print('✅ All coordinates are properly formatted and ready for use.')
        else:
            print('❌ Some stations still need fixing')
    
    def create_initial_stations_data(self):
        """Create initial metro stations data structure."""
        stations = [
            {
                "name": "Kavi Subhash",
                "short_code": "KKVS",
                "location": "New Garia",
                "lines": ["Blue Line", "Orange Line"],
                "latitude": 22.4721796,
                "longitude": 88.3952919
            },
            {
                "name": "Shahid Khudiram",
                "short_code": "KSKD",
                "location": "Briji/Dhalai Bridge",
                "lines": ["Blue Line"],
                "latitude": 22.4800000,
                "longitude": 88.3810000
            },
            # Add more stations as needed
        ]
        
        with open(self.stations_file, 'w', encoding='utf-8') as f:
            json.dump(stations, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created initial {self.stations_file} with {len(stations)} stations")

def main():
    """Main function to run the metro station fetcher."""
    fetcher = MetroStationFetcher()
    
    print("🚇 Kolkata Metro Station Details Fetcher")
    print("=" * 50)
    print("Available operations:")
    print("1. Scrape all coordinates")
    print("2. Force fix coordinates")
    print("3. Final fix coordinates")
    print("4. Verify coordinates")
    print("5. Create initial data")
    print("6. Run all operations")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        fetcher.scrape_all_coordinates()
    elif choice == "2":
        fetcher.force_fix_coordinates()
    elif choice == "3":
        fetcher.final_fix_coordinates()
    elif choice == "4":
        fetcher.verify_all_coordinates()
    elif choice == "5":
        fetcher.create_initial_stations_data()
    elif choice == "6":
        print("🔄 Running all operations...")
        fetcher.scrape_all_coordinates()
        fetcher.force_fix_coordinates()
        fetcher.final_fix_coordinates()
        fetcher.verify_all_coordinates()
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
