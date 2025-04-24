# ui/main_content.py
import streamlit as st
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from services.flight_plan_service import parse_flight_plan
from services.weather_service import fetch_weather_data, classify_weather
from utils.flight_history import save_flight_to_history
from ui.weather_components import generate_summary, generate_detailed_report, create_weather_map
from ui.about_help import display_about_section, display_help_section
from ui.chatbot_component import display_chatbot
from services.report_service import (
    generate_weather_report, 
    generate_weather_report_html,
    get_download_link,
    create_route_profile_chart
)

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
    
    # Store collected weather data for use in the chatbot
    if 'weather_data_dict' not in st.session_state:
        st.session_state.weather_data_dict = {}
    
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
            weather_data_dict = {}  # For use in chatbot
            summaries = []
            detailed_reports = []
            for icao_id, altitude in waypoints:
                with st.spinner(f"Fetching weather data for {icao_id}..."):
                    weather_data = fetch_weather_data(icao_id)
                    # print(weather_data)  # Debugging line
                    if "Error" in weather_data:
                        st.error(weather_data["Error"])
                        return
                    
                    # Store classification with weather data
                    classification, color = classify_weather(weather_data)
                    weather_data["classification"] = (classification, color)
                    
                    weather_data_list.append(weather_data)
                    weather_data_dict[icao_id] = weather_data
                    summaries.append(generate_summary(weather_data, icao_id, altitude))
                    detailed_reports.append(generate_detailed_report(weather_data, icao_id, altitude))
            
            # Store for chatbot use
            st.session_state.weather_data_dict = weather_data_dict
        
        # Optional divider for visual separation
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Output Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Weather Summary", 
            "Detailed Reports", 
            "Weather Map", 
            "Generate Report",
            "Weather Assistant"
        ])
        
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
                - Heat Map: Shows intensity of weather conditions along route
            """)
            
            st.checkbox("Show/Hide Heatmap Layer", value=True, key="heatmap_visible")
        
        with tab4:
            st.markdown('<h3 class="text-2xl font-bold text-blue-600 mb-4">Flight Weather Report</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                report_format = st.selectbox(
                    "Report Format",
                    ["Markdown", "HTML"],
                    index=0
                )
            
            with col2:
                report_detail = st.selectbox(
                    "Detail Level",
                    ["Standard", "Detailed"],
                    index=0
                )
            
            if st.button("Generate Report", key="generate_report"):
                with st.spinner("Generating comprehensive weather report..."):
                    if report_format == "Markdown":
                        report = generate_weather_report(flight_plan, waypoints, weather_data_list, airport_coords)
                        st.markdown(get_download_link(report, f"flight_weather_{waypoints[0][0]}_to_{waypoints[-1][0]}", "markdown"), unsafe_allow_html=True)
                        st.markdown("### Report Preview")
                        st.markdown(report)
                    else:  # HTML
                        report_html = generate_weather_report_html(flight_plan, waypoints, weather_data_list, airport_coords)
                        st.markdown(get_download_link(report_html, f"flight_weather_{waypoints[0][0]}_to_{waypoints[-1][0]}", "html"), unsafe_allow_html=True)
                        st.markdown("### Report Preview")
                        st.components.v1.html(report_html, height=500, scrolling=True)
            
            # Flight profile chart
            st.markdown("### Flight Profile with Weather Conditions")
            fig = create_route_profile_chart(waypoints, weather_data_list, airport_coords)
            st.pyplot(fig)
        
        with tab5:
            display_chatbot(st.session_state.weather_data_dict)
    
    # About and Help sections
    st.markdown("<hr>", unsafe_allow_html=True)
    display_about_section()
    display_help_section()