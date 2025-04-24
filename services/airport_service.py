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