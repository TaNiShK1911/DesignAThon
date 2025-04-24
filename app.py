# app.py
import streamlit as st
from ui.styles import apply_custom_styles
from ui.sidebar import setup_sidebar
from ui.main_content import display_main_content
from services.airport_service import load_airport_coordinates

# Configuration
st.set_page_config(
    page_title="FlightWeatherPro",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

def main():
    # Load airport coordinates
    airport_coords = load_airport_coordinates()
    if not airport_coords:
        st.error("Unable to load airport coordinates. Please try again later.")
        return

    # Setup sidebar
    setup_sidebar()
    
    # Display main content
    display_main_content(airport_coords)
    
    # Attribution
    st.markdown('<p class="text-center text-gray-500 mt-8">Data provided by the Aviation Weather Center</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()