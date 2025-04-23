import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static
import re
from datetime import datetime
import uuid
import json

# Theme Configuration
st.set_page_config(
    page_title="FlightWeatherPro",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "https://aviationweather.gov/api/data"
OPENFLIGHTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

# Custom CSS for Beautification with Dark Mode Support
st.markdown("""
    <style>
    /* Import Tailwind CSS via CDN */
    @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');
    
    /* CSS Variables for Theme Colors */
    :root {
        --bg-color: #f0f2f6;
        --text-color: #1e3a8a;
        --subtitle-color: #4b5563;
        --input-border: #3b82f6;
        --button-bg: #3b82f6;
        --button-hover: #1e40af;
        --tab-bg: #e5e7eb;
        --tab-hover: #d1d5db;
    }

    /* Dark mode variables */
    [data-theme="dark"] {
        --bg-color: #1a1a1a;
        --text-color: #e0e7ff;
        --subtitle-color: #9ca3af;
        --input-border: #4f46e5;
        --button-bg: #4f46e5;
        --button-hover: #4338ca;
        --tab-bg: #374151;
        --tab-hover: #4b5563;
    }

    /* Apply theme colors */
    .stApp {
        background-color: var(--bg-color);
        font-family: 'Arial', sans-serif;
        transition: all 0.3s ease;
    }
    
    .title {
        color: var(--text-color);
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        color: var(--subtitle-color);
        font-size: 1.25rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div > input {
        border: 2px solid var(--input-border);
        border-radius: 8px;
        padding: 10px;
        font-size: 1rem;
        background-color: var(--bg-color);
        color: var(--text-color);
    }
    
    .stButton > button {
        background-color: var(--button-bg);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-size: 1rem;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: var(--button-hover);
    }
    
    .section-header {
        color: var(--text-color);
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .stTabs > div > div > button {
        background-color: var(--tab-bg);
        color: var(--text-color);
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stTabs > div > div > button:hover {
        background-color: var(--tab-hover);
    }
    
    .map-container {
        border: 2px solid var(--input-border);
        border-radius: 8px;
        padding: 10px;
        background-color: var(--bg-color);
    }

    /* Dark mode toggle styles */
    .theme-toggle {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }
    </style>

    <script>
    // Add dark mode toggle functionality
    function toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
""", unsafe_allow_html=True)

# Add theme toggle button in sidebar
with st.sidebar:
    st.title("Settings")
    if st.button("Toggle Dark/Light Mode"):
        # This will trigger a rerun of the app
        current_theme = st.session_state.get('theme', 'light')
        st.session_state.theme = 'dark' if current_theme == 'light' else 'light'
        st.markdown(f"""
            <script>
                document.documentElement.setAttribute('data-theme', '{st.session_state.theme}');
                localStorage.setItem('theme', '{st.session_state.theme}');
            </script>
        """, unsafe_allow_html=True)

# Step 1: Fetch Airport Coordinates Dynamically
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

# Step 2: Parse Flight Plan
def parse_flight_plan(flight_plan, airport_coords):
    """Parse flight plan into a list of (airport_id, altitude) tuples."""
    try:
        items = flight_plan.strip().split(',')
        if len(items) % 2 != 0:
            raise ValueError("Invalid flight plan format. Must have pairs of Airport ID and Altitude.")
        waypoints = [(items[i].upper(), int(items[i+1])) for i in range(0, len(items), 2)]
        for icao, _ in waypoints:
            if icao not in airport_coords:
                raise ValueError(f"Unknown or unsupported ICAO ID: {icao}")
        return waypoints
    except Exception as e:
        return f"Error parsing flight plan: {str(e)}"

# Step 3: Fetch Real-Time Weather Data
def fetch_weather_data(icao_id):
    """Fetch METAR, TAF, PIREP, and SIGMET data for an ICAO ID."""
    try:
        weather_data = {"METAR": "", "TAF": "", "PIREP": "", "SIGMET": ""}
        
        # Fetch METAR
        metar_url = f"{API_BASE_URL}/metar?ids={icao_id}&format=json"
        metar_response = requests.get(metar_url, timeout=5)
        if metar_response.status_code == 200 and metar_response.json():
            weather_data["METAR"] = metar_response.json()[0].get("rawOb", "No METAR available")
        
        # Fetch TAF
        taf_url = f"{API_BASE_URL}/taf?ids={icao_id}&format=json"
        taf_response = requests.get(taf_url, timeout=5)
        if taf_response.status_code == 200 and taf_response.json():
            weather_data["TAF"] = taf_response.json()[0].get("rawOb", "No TAF available")
        
        # Fetch PIREP (Simplified)
        pirep_url = f"{API_BASE_URL}/pirep?format=json"
        pirep_response = requests.get(pirep_url, timeout=5)
        if pirep_response.status_code == 200:
            pireps = [p for p in pirep_response.json() if icao_id in p.get("rawOb", "")]
            weather_data["PIREP"] = pireps[0].get("rawOb", "No recent PIREP") if pireps else "No recent PIREP"
        
        # Fetch SIGMET
        sigmet_url = f"{API_BASE_URL}/sigmet?format=json"
        sigmet_response = requests.get(sigmet_url, timeout=5)
        if sigmet_response.status_code == 200:
            sigmets = [s for s in sigmet_response.json() if icao_id in s.get("rawOb", "")]
            weather_data["SIGMET"] = sigmets[0].get("rawOb", "No active SIGMET") if sigmets else "No active SIGMET"
        
        return weather_data
    except Exception as e:
        return {"Error": f"Failed to fetch weather data for {icao_id}: {str(e)}"}

# Step 4: Summarize Weather Data
def generate_summary(weather_data, icao_id, altitude):
    """Generate a concise weather summary for a waypoint."""
    summary = f"**{icao_id} (Altitude: {altitude}ft)**:\n"
    
    metar = weather_data.get("METAR", "")
    if "CLR" in metar or "SKC" in metar:
        summary += "- **Conditions**: Clear skies 🌞\n"
    elif "OVC" in metar or "BKN" in metar:
        summary += "- **Conditions**: Cloudy ☁️\n"
    else:
        summary += "- **Conditions**: Variable 🌥️\n"
    
    taf = weather_data.get("TAF", "")
    summary += "- **Forecast**: Stable conditions expected 📈\n" if taf else "- **Forecast**: Unavailable ❓\n"
    
    pirep = weather_data.get("PIREP", "")
    summary += "- **Pilot Reports**: No significant issues ✅\n" if "No recent PIREP" in pirep else f"- **Pilot Reports**: {pirep} ✈️\n"
    
    sigmet = weather_data.get("SIGMET", "")
    summary += "- **Hazards**: None reported 🟢\n" if "No active SIGMET" in sigmet else f"- **Hazards**: {sigmet} ⚠️\n"
    
    return summary

# Step 5: Classify Weather Activity (Stretch Goal)
def classify_weather(weather_data):
    """Classify weather as VFR, Significant, or Severe."""
    metar = weather_data.get("METAR", "")
    sigmet = weather_data.get("SIGMET", "")
    
    if "No active SIGMET" in sigmet and ("CLR" in metar or "SKC" in metar):
        return "VFR Conditions", "green"
    elif "TS" in metar or "SEV" in sigmet:
        return "Severe Weather Activity", "red"
    else:
        return "Significant Weather Activity", "yellow"

# Step 6: Generate Detailed Report
def generate_detailed_report(weather_data, icao_id, altitude):
    """Generate a detailed weather report for a waypoint."""
    report = f"**Detailed Weather Report for {icao_id} (Altitude: {altitude}ft)**:\n"
    report += f"- **METAR**: {weather_data.get('METAR', 'Unavailable')}\n"
    report += f"- **TAF**: {weather_data.get('TAF', 'Unavailable')}\n"
    report += f"- **PIREP**: {weather_data.get('PIREP', 'No recent PIREP')}\n"
    report += f"- **SIGMET**: {weather_data.get('SIGMET', 'No active SIGMET')}\n"
    classification, _ = classify_weather(weather_data)
    report += f"- **Weather Classification**: {classification}\n"
    return report

# Step 7: Create Graphical Overlay (Stretch Goal)
def create_weather_map(waypoints, weather_data_list, airport_coords):
    """Create a Folium map with weather overlays."""
    # Calculate map center based on waypoints
    lats = [airport_coords[icao][0] for icao, _ in waypoints]
    lons = [airport_coords[icao][1] for icao, _ in waypoints]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles="CartoDB Positron")
    
    for (icao_id, altitude), weather_data in zip(waypoints, weather_data_list):
        lat, lon = airport_coords[icao_id]
        classification, color = classify_weather(weather_data)
        folium.CircleMarker(
            location=[lat, lon],
            radius=12,
            popup=folium.Popup(f"<b>{icao_id}</b><br>Altitude: {altitude}ft<br>{classification}", max_width=300),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(m)
    
    # Add flight path with tooltip
    path = [(airport_coords[icao][0], airport_coords[icao][1]) for icao, _ in waypoints]
    folium.PolyLine(
        path,
        color="blue",
        weight=3,
        opacity=0.8,
        tooltip="Flight Path"
    ).add_to(m)
    
    return m

# Step 8: Streamlit Web Interface
def main():
    # Header
    st.markdown('<div class="title">FlightWeatherPro</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Real-Time Aviation Weather Briefings for Any Flight Plan</div>', unsafe_allow_html=True)
    
    # Load airport coordinates
    airport_coords = load_airport_coordinates()
    if not airport_coords:
        st.error("Unable to load airport coordinates. Please try again later.")
        return
    
    # Input Section
    with st.container():
        st.markdown('<div class="section-header">Enter Flight Plan</div>', unsafe_allow_html=True)
        st.write("Format: ICAO,Altitude,ICAO,Altitude,... (e.g., KPHX,1500,KLAX,35000,KJFK,39000)")
        flight_plan = st.text_input("", placeholder="Enter flight plan here", key="flight_plan")
        
        if st.button("Generate Weather Briefing", key="generate_button"):
            if not flight_plan:
                st.error("Please enter a valid flight plan.")
                return
            
            # Parse flight plan
            with st.spinner("Processing flight plan..."):
                waypoints = parse_flight_plan(flight_plan, airport_coords)
                if isinstance(waypoints, str):
                    st.error(waypoints)
                    return
                
                # Fetch and process weather data
                weather_data_list = []
                summaries = []
                detailed_reports = []
                
                for icao_id, altitude in waypoints:
                    with st.spinner(f"Fetching weather data for {icao_id}..."):
                        weather_data = fetch_weather_data(icao_id)
                        if "Error" in weather_data:
                            st.error(weather_data["Error"])
                            return
                        weather_data_list.append(weather_data)
                        summaries.append(generate_summary(weather_data, icao_id, altitude))
                        detailed_reports.append(generate_detailed_report(weather_data, icao_id, altitude))
            
            # Output Tabs
            tab1, tab2, tab3 = st.tabs(["Weather Summary", "Detailed Reports", "Weather Map"])
            
            with tab1:
                st.markdown('<div class="section-header">Weather Summary</div>', unsafe_allow_html=True)
                for summary in summaries:
                    st.markdown(summary, unsafe_allow_html=True)
            
            with tab2:
                st.markdown('<div class="section-header">Detailed Weather Reports</div>', unsafe_allow_html=True)
                for i, report in enumerate(detailed_reports, 1):
                    with st.expander(f"Report for Waypoint {i}", expanded=False):
                        st.markdown(report, unsafe_allow_html=True)
            
            with tab3:
                st.markdown('<div class="section-header">Weather Map Overlay</div>', unsafe_allow_html=True)
                with st.container():
                    weather_map = create_weather_map(waypoints, weather_data_list, airport_coords)
                    folium_static(weather_map, width=700, height=500)

if __name__ == "__main__":
    main()
