import streamlit as st
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from services.flight_plan_service import parse_flight_plan
from services.weather_service import fetch_weather_data, classify_weather
from utils.flight_history import save_flight_to_history
from ui.weather_components import generate_summary, generate_detailed_report, create_weather_map
from services.pilot_briefing_service import generate_pilot_briefing_from_route, export_briefing_to_pdf
from ui.about_help import display_about_section, display_help_section
from datetime import date
import os
from services.report_service import (
    generate_weather_report, 
    generate_weather_report_html,
    get_download_link,
    create_route_profile_chart
)

def display_main_content(airport_coords):
    """Display the main content of the application."""
    st.markdown('<h1 class="text-4xl font-bold text-blue-600 text-center mb-4">FlightWeatherPro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-xl text-gray-600 text-center mb-8">Real-Time Aviation Weather Briefings for Any Flight Plan</p>', unsafe_allow_html=True)

    main_tab1, main_tab2 = st.tabs(["Enter Flight Plan", "Pilot Briefing"])

    with main_tab1:
        st.markdown('<h2 class="text-2xl font-bold text-blue-600 mb-4" id="enter-flight-plan">Enter Flight Plan</h2>', unsafe_allow_html=True)
        st.write("Format: ICAO,Altitude,ICAO,Altitude,... (e.g., KPHX,1500,KLAX,35000,KJFK,39000)")
        
        flight_plan = st.text_input("", placeholder="Enter flight plan here", key="flight_plan", value=st.session_state.get('flight_plan', ''))
        submit = st.button("Generate Weather Briefing", key="generate_button")

        if 'weather_data_dict' not in st.session_state:
            st.session_state.weather_data_dict = {}

        if submit:
            if not flight_plan:
                st.error("Please enter a valid flight plan.")
                return

            save_flight_to_history(flight_plan)

            with st.spinner("Processing flight plan..."):
                waypoints = parse_flight_plan(flight_plan, airport_coords)
                if isinstance(waypoints, str):
                    st.error(waypoints)
                    return

                weather_data_list = []
                weather_data_dict = {}
                summaries = []
                detailed_reports = []

                for icao_id, altitude in waypoints:
                    with st.spinner(f"Fetching weather data for {icao_id}..."):
                        weather_data = fetch_weather_data(icao_id)
                        if "Error" in weather_data:
                            st.error(weather_data["Error"])
                            return

                        classification, color = classify_weather(weather_data)
                        weather_data["classification"] = (classification, color)

                        weather_data_list.append(weather_data)
                        weather_data_dict[icao_id] = weather_data
                        summaries.append(generate_summary(weather_data, icao_id, altitude))
                        detailed_reports.append(generate_detailed_report(weather_data, icao_id, altitude))

                st.session_state.weather_data_dict = weather_data_dict

            st.markdown("<hr>", unsafe_allow_html=True)

            tab1, tab2, tab3, tab4 = st.tabs([
                "Weather Summary", 
                "Detailed Reports", 
                "Weather Map", 
                "Generate Report"
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
                st.markdown('<h3 class="text-2xl font-bold text-blue-600 mb-4">Flight Weather Profile</h3>', unsafe_allow_html=True)
                
                with st.spinner("Generating flight profile chart..."):
                    fig = create_route_profile_chart(waypoints, weather_data_list, airport_coords)
                    st.pyplot(fig)

    with main_tab2:
        st.title("Pilot Briefing")
        st.markdown("This section provides a concise weather and airport briefing for your upcoming flight.")

        route_input = st.text_input("Flight Route", placeholder="Enter route as ICAO,Altitude,ICAO,Altitude,... (e.g., KPHX,1500,KLAX,35000)")
        flight_date = st.date_input("Flight Date", date.today())

        if st.button("Generate Briefing"):
            if not route_input:
                st.warning("Please enter a valid flight route.")
            else:
                with st.spinner("Fetching pilot briefing..."):
                    briefing = generate_pilot_briefing_from_route(route_input, flight_date)
                    st.markdown(briefing, unsafe_allow_html=True)

                    route = route_input.split(',')
                    departure = route[0].strip().upper()
                    destination = route[-2].strip().upper() if len(route) > 2 else route[0].strip().upper()

                    pdf_path = export_briefing_to_pdf(departure, destination, flight_date, briefing)
                    with open(pdf_path, "rb") as f:
                        st.download_button("Download Briefing as PDF", f, file_name=os.path.basename(pdf_path))

    st.markdown("<hr>", unsafe_allow_html=True)
    display_about_section()
    display_help_section()
