# ui/styles.py
import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the application."""
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
        
        /* Chat interface styling */
        .chat-message {
            padding: 0.75rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            display: flex;
            flex-direction: column;
        }
        
        .user-message {
            background-color: #e0f2fe;
            border-right: 3px solid #60a5fa;
            text-align: right;
        }
        
        .assistant-message {
            background-color: #f3f4f6;
            border-left: 3px solid #9ca3af;
        }
        
        /* Download button */
        .download-button {
            display: inline-block;
            padding: 0.6rem 1.2rem;
            background-color: #2563eb;
            color: white !important;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: 600;
            margin: 1rem 0;
            text-align: center;
            transition: all 0.2s ease-in-out;
        }
        
        .download-button:hover {
            background-color: #1d4ed8;
            transform: scale(1.02);
        }
        </style>
    """, unsafe_allow_html=True)