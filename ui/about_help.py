import streamlit as st

def display_about_section():
    """Display the About section."""
    st.markdown('<h2 class="text-2xl font-bold text-blue-600 mb-4" id="about">About</h2>', unsafe_allow_html=True)
    st.markdown("""
    **FlightWeatherPro** is a comprehensive aviation weather briefing tool designed for pilots and flight dispatchers. 
    It provides real-time weather data for any flight path, helping users make informed decisions about their routes.
    
    The application retrieves data from the Aviation Weather Center's API and integrates it with airport location data
    from the OpenFlights database.
    """)

def display_help_section():
    """Display the Help section."""
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