# utils/flight_history.py
import streamlit as st

def get_recent_flights():
    """Get the list of recent flights from session state."""
    if 'flight_history' not in st.session_state:
        st.session_state.flight_history = []
    return st.session_state.flight_history

def save_flight_to_history(flight_plan):
    """Save a flight plan to the history in session state."""
    if 'flight_history' not in st.session_state:
        st.session_state.flight_history = []
    
    # Add to history if not already there
    if flight_plan not in st.session_state.flight_history:
        st.session_state.flight_history.append(flight_plan)
        # Keep only the 5 most recent flights
        if len(st.session_state.flight_history) > 5:
            st.session_state.flight_history.pop(0)