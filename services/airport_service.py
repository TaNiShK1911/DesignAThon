# services/airport_service.py

import streamlit as st
import requests

# Constants
OPENFLIGHTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

@st.cache_data
def load_airport_coordinates():
    """Load airport coordinates from OpenFlights dataset."""
    try:
        response = requests.get(OPENFLIGHTS_URL, timeout=10)
        response.raise_for_status()
        airports = {}
        for line in response.text.splitlines():
            fields = line.split(',')
            if len(fields) < 11:
                continue
            icao = fields[5].strip('"')
            lat = fields[6].strip('"')
            lon = fields[7].strip('"')
            if icao and lat and lon and icao != "\\N":
                try:
                    airports[icao] = (float(lat), float(lon))
                except ValueError:
                    continue
        return airports
    except Exception as e:
        st.error(f"Failed to load airport coordinates: {str(e)}")
        return {}
    
def get_airport_info(icao_id):
    """Get detailed information about an airport."""
    try:
        airports = load_airport_coordinates()
        if icao_id not in airports:
            return None
            
        # Get airport data from OpenFlights
        response = requests.get(OPENFLIGHTS_URL, timeout=10)
        response.raise_for_status()
        
        for line in response.text.splitlines():
            fields = line.split(',')
            if len(fields) < 11:
                continue
            icao = fields[5].strip('"')
            if icao == icao_id:
                name = fields[1].strip('"')
                city = fields[2].strip('"')
                country = fields[3].strip('"')
                lat = fields[6].strip('"')
                lon = fields[7].strip('"')
                
                info = []
                info.append(f"*Name:* {name}")
                info.append(f"*Location:* {city}, {country}")
                info.append(f"*Coordinates:* {lat}°N, {lon}°E")
                info.append(f"*Elevation:* {fields[8].strip('"')} ft")
                
                return "\n".join(info)
        return None
    except Exception as e:
        return None