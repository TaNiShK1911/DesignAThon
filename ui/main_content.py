import streamlit as st
from streamlit_folium import folium_static
from services.flight_plan_service import parse_flight_plan
from services.weather_service import fetch_weather_data, classify_weather
from utils.flight_history import save_flight_to_history
from ui.weather_components import generate_summary, generate_detailed_report, create_weather_map
from ui.about_help import display_about_section, display_help_section

def display_main_content(airport_coords):
    """Display the main content of the application."""
    # Header
    st.markdown('<h1 class="text-4xl font-bold text-blue-600 text-center mb-4">FlightWeatherPro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-xl text-gray-600 text-center mb-8">Real-Time Aviation Weather Briefings for Any Flight Plan</p>', unsafe_allow_html=True)
    
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
    display_about_section()
    display_help_section()