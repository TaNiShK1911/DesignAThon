# ui/sidebar.py
import streamlit as st
from utils.flight_history import get_recent_flights

def setup_sidebar():
    """Setup the sidebar with navigation, recent flights, and settings."""
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