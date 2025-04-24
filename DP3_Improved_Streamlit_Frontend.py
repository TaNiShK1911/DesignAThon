import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

# Configuration
st.set_page_config(
    page_title="FlightWeatherPro",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "https://aviationweather.gov/api/data"
OPENFLIGHTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

# Custom CSS for Light Theme with Dark Fonts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    .stApp {
        background-color: #f8fbff;
        font-family: 'Inter', sans-serif;
        color: #1f2937;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #1e3a8a;
        font-weight: 700;
    }

    .stTextInput > div > div > input {
        border: 1.5px solid #60a5fa;
        border-radius: 8px;
        padding: 0.6rem;
        font-size: 1rem;
        color: #1f2937;
        background-color: #ffffff;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    .stButton > button {
        background-color: #2563eb;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease-in-out;
    }

    .stButton > button:hover {
        background-color: #1d4ed8;
        transform: scale(1.02);
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #e0ecff;
        color: #1e3a8a;
        padding: 10px 20px;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }

    .sidebar .sidebar-content {
        background-color: #e5efff;
        padding: 1rem;
        border-right: 2px solid #93c5fd;
    }

    .stMarkdown, .stText, .stDataFrame {
        color: #1f2937;
    }

    .folium-map {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, #60a5fa, #2563eb);
        margin: 1rem 0;
    }

    /* Tooltip overrides */
    .leaflet-tooltip {
        background-color: #ffffff;
        color: #111827;
        border-radius: 4px;
        border: 1px solid #d1d5db;
        padding: 6px 10px;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)


# Load Airport Coordinates
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

# Parse Flight Plan with Enhanced Validation
def parse_flight_plan(flight_plan, airport_coords):
    """Parse flight plan into a list of (airport_id, altitude) tuples."""
    try:
        items = flight_plan.strip().split(',')
        if len(items) % 2 != 0:
            raise ValueError("Invalid flight plan format. Must have pairs of Airport ID and Altitude.")
        waypoints = []
        for i in range(0, len(items), 2):
            icao = items[i].upper()
            altitude_str = items[i+1]
            if icao not in airport_coords:
                raise ValueError(f"Unknown or unsupported ICAO ID: {icao}")
            try:
                altitude = int(altitude_str)
                if altitude < 0:
                    raise ValueError(f"Altitude must be a positive integer: {altitude_str}")
            except ValueError:
                raise ValueError(f"Invalid altitude value: {altitude_str}. Must be a positive integer.")
            waypoints.append((icao, altitude))
        return waypoints
    except Exception as e:
        return f"Error parsing flight plan: {str(e)}"

# Fetch Weather Data
def fetch_weather_data(icao_id):
    """Fetch METAR, TAF, PIREP, and SIGMET data for an ICAO ID."""
    try:
        weather_data = {"METAR": "", "TAF": "", "PIREP": "", "SIGMET": ""}
        metar_url = f"{API_BASE_URL}/metar?ids={icao_id}&format=json"
        metar_response = requests.get(metar_url, timeout=5)
        if metar_response.status_code == 200 and metar_response.json():
            weather_data["METAR"] = metar_response.json()[0].get("rawOb", "No METAR available")
        
        taf_url = f"{API_BASE_URL}/taf?ids={icao_id}&format=json"
        taf_response = requests.get(taf_url, timeout=5)
        if taf_response.status_code == 200 and taf_response.json():
            weather_data["TAF"] = taf_response.json()[0].get("rawOb", "No TAF available")
        
        pirep_url = f"{API_BASE_URL}/pirep?format=json"
        pirep_response = requests.get(pirep_url, timeout=5)
        if pirep_response.status_code == 200:
            pireps = [p for p in pirep_response.json() if icao_id in p.get("rawOb", "")]
            weather_data["PIREP"] = pireps[0].get("rawOb", "No recent PIREP") if pireps else "No recent PIREP"
        
        sigmet_url = f"{API_BASE_URL}/sigmet?format=json"
        sigmet_response = requests.get(sigmet_url, timeout=5)
        if sigmet_response.status_code == 200:
            sigmets = [s for s in sigmet_response.json() if icao_id in s.get("rawOb", "")]
            weather_data["SIGMET"] = sigmets[0].get("rawOb", "No active SIGMET") if sigmets else "No active SIGMET"
        
        return weather_data
    except Exception as e:
        return {"Error": f"Unable to fetch weather data for {icao_id}. Please try again later."}

# Generate Weather Summary
def generate_summary(weather_data, icao_id, altitude):
    """Generate a concise weather summary for a waypoint using an HTML list."""
    summary = f"<b>{icao_id} (Altitude: {altitude}ft)</b>:<ul>"
    metar = weather_data.get("METAR", "")
    if "CLR" in metar or "SKC" in metar:
        summary += "<li><b>Conditions</b>: Clear skies 🌞</li>"
    elif "OVC" in metar or "BKN" in metar:
        summary += "<li><b>Conditions</b>: Cloudy ☁️</li>"
    else:
        summary += "<li><b>Conditions</b>: Variable 🌥️</li>"
    taf = weather_data.get("TAF", "")
    summary += "<li><b>Forecast</b>: Stable conditions expected 📈</li>" if taf else "<li><b>Forecast</b>: Unavailable ❓</li>"
    pirep = weather_data.get("PIREP", "")
    summary += "<li><b>Pilot Reports</b>: No significant issues ✅</li>" if "No recent PIREP" in pirep else f"<li><b>Pilot Reports</b>: {pirep} ✈️</li>"
    sigmet = weather_data.get("SIGMET", "")
    summary += "<li><b>Hazards</b>: None reported 🟢</li>" if "No active SIGMET" in sigmet else f"<li><b>Hazards</b>: {sigmet} ⚠️</li>"
    summary += "</ul>"
    return summary

# Classify Weather
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

# Generate Detailed Report
def generate_detailed_report(weather_data, icao_id, altitude):
    """Generate a detailed weather report for a waypoint with line breaks."""
    report = f"<b>Detailed Weather Report for {icao_id} (Altitude: {altitude}ft)</b>:<br>"
    report += f"- <b>METAR</b>: {weather_data.get('METAR', 'Unavailable')}<br>"
    report += f"- <b>TAF</b>: {weather_data.get('TAF', 'Unavailable')}<br>"
    report += f"- <b>PIREP</b>: {weather_data.get('PIREP', 'No recent PIREP')}<br>"
    report += f"- <b>SIGMET</b>: {weather_data.get('SIGMET', 'No active SIGMET') if weather_data.get('SIGMET') else "No Activate SIGMET"}<br>"
    print(weather_data.get('SIGMET'))
    classification, _ = classify_weather(weather_data)
    report += f"- <b>Weather Classification</b>: {classification}<br>"
    return report

# Create Weather Map
def create_weather_map(waypoints, weather_data_list, airport_coords):
    """Create a Folium map with weather overlays."""
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
    
    path = [(airport_coords[icao][0], airport_coords[icao][1]) for icao, _ in waypoints]
    folium.PolyLine(
        path,
        color="blue",
        weight=3,
        opacity=0.8,
        tooltip="Flight Path"
    ).add_to(m)
    
    return m

# Function to get recent flights from history
def get_recent_flights():
    if 'flight_history' not in st.session_state:
        st.session_state.flight_history = []
    return st.session_state.flight_history

# Function to save flight to history
def save_flight_to_history(flight_plan):
    if 'flight_history' not in st.session_state:
        st.session_state.flight_history = []
    
    # Add to history if not already there
    if flight_plan not in st.session_state.flight_history:
        st.session_state.flight_history.append(flight_plan)
        # Keep only the 5 most recent flights
        if len(st.session_state.flight_history) > 5:
            st.session_state.flight_history.pop(0)

# Main Interface
def main():
    # Setup sidebar
    with st.sidebar:
        st.markdown('<h2 class="text-xl font-bold text-blue-600 mb-4">Flight Weather Pro</h2>', unsafe_allow_html=True)
        st.markdown("### Navigation")
        st.markdown("- [Weather Briefing](#enter-flight-plan)")
        st.markdown("- [About](#about)")
        st.markdown("- [Help](#help)")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("### Recent Flights")
        recent_flights = get_recent_flights()
        if recent_flights:
            for flight in recent_flights:
                if st.button(f"📋 {flight}", key=f"history_{flight}"):
                    st.session_state.flight_plan = flight
        else:
            st.write("No recent flights found")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("### Settings")
        map_style = st.selectbox(
            "Map Style",
            ["CartoDB Positron", "OpenStreetMap", "Stamen Terrain"],
            index=0
        )
        
        display_units = st.radio(
            "Display Units",
            ["Imperial", "Metric"],
            index=0
        )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("### About")
        st.markdown("""
        FlightWeatherPro provides real-time aviation weather data for flight planning.
        
        Data sources:
        - Aviation Weather Center
        - OpenFlights Database
        """)
    
    # Main content
    # Header
    st.markdown('<h1 class="text-4xl font-bold text-blue-600 text-center mb-4">FlightWeatherPro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-xl text-gray-600 text-center mb-8">Real-Time Aviation Weather Briefings for Any Flight Plan</p>', unsafe_allow_html=True)
    
    # Load airport coordinates
    airport_coords = load_airport_coordinates()
    if not airport_coords:
        st.error("Unable to load airport coordinates. Please try again later.")
        return
    
    # Input Section
    st.markdown('<h2 class="text-2xl font-bold text-blue-600 mb-4" id="enter-flight-plan">Enter Flight Plan</h2>', unsafe_allow_html=True)
    st.write("Format: ICAO,Altitude,ICAO,Altitude,... (e.g., KPHX,1500,KLAX,35000,KJFK,39000)")
    
    flight_plan = st.text_input("", placeholder="Enter flight plan here", key="flight_plan", value=st.session_state.get('flight_plan', ''))
    submit = st.button("Generate Weather Briefing", key="generate_button")
    
    # Results Section
    if submit:
        if not flight_plan:
            st.error("Please enter a valid flight plan.")
            return
            
        # Save to history
        save_flight_to_history(flight_plan)
        
        # Parse flight plan
        with st.spinner("Processing flight plan..."):
            waypoints = parse_flight_plan(flight_plan, airport_coords)
            if isinstance(waypoints, str):
                st.error(waypoints)
                return
            
            # Fetch weather data
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
        
        # Optional divider for visual separation
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Output Tabs
        tab1, tab2, tab3 = st.tabs(["Weather Summary", "Detailed Reports", "Weather Map"])
        
        with tab1:
            st.markdown('<h3 class="text-2xl font-bold text-blue-600 mb-4">Weather Summary</h3>', unsafe_allow_html=True)
            for summary in summaries:
                st.markdown(f'<div class="p-4 mb-4 border border-gray-300 rounded-lg bg-white">{summary}</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<h3 class="text-2xl font-bold text-blue-600 mb-4">Detailed Weather Reports</h3>', unsafe_allow_html=True)
            for i, (icao_id, altitude) in enumerate(waypoints, 1):
                with st.expander(f"Report for {icao_id} (Altitude: {altitude}ft)", expanded=False):
                    st.markdown(detailed_reports[i-1], unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<h3 class="text-2xl font-bold text-blue-600 mb-4">Weather Map Overlay</h3>', unsafe_allow_html=True)
            weather_map = create_weather_map(waypoints, weather_data_list, airport_coords)
            folium_static(weather_map, width=700, height=500)
            st.markdown("""
                ### Legend
                - 🟢 Green: VFR Conditions
                - 🟡 Yellow: Significant Weather Activity
                - 🔴 Red: Severe Weather Activity
            """, unsafe_allow_html=True)
    
    # About and Help sections
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<h2 class="text-2xl font-bold text-blue-600 mb-4" id="about">About</h2>', unsafe_allow_html=True)
    st.markdown("""
    **FlightWeatherPro** is a comprehensive aviation weather briefing tool designed for pilots and flight dispatchers. 
    It provides real-time weather data for any flight path, helping users make informed decisions about their routes.
    
    The application retrieves data from the Aviation Weather Center's API and integrates it with airport location data
    from the OpenFlights database.
    """)
    
    st.markdown('<h2 class="text-2xl font-bold text-blue-600 mb-4 mt-6" id="help">Help</h2>', unsafe_allow_html=True)
    st.markdown("""
    ### How to Use FlightWeatherPro
    
    1. **Enter your flight plan** in the format: `ICAO,Altitude,ICAO,Altitude,...`
       - Example: `KPHX,1500,KLAX,35000,KJFK,39000`
       - ICAO codes must be valid airport identifiers
       - Altitude must be specified in feet
    
    2. **Click "Generate Weather Briefing"** to process your flight plan
    
    3. **View results** in three tabs:
       - **Weather Summary**: Quick overview of conditions at each waypoint
       - **Detailed Reports**: Complete METAR, TAF, PIREP, and SIGMET information
       - **Weather Map**: Visual representation of your flight path with weather conditions
    
    4. **Use the sidebar** to access:
       - Recent flights for quick reuse
       - Map style settings
       - Unit preferences
    """)
    
    # Attribution
    st.markdown('<p class="text-center text-gray-500 mt-8">Data provided by the Aviation Weather Center</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()