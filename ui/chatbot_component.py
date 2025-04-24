# ui/chatbot_component.py
import streamlit as st
from services.chatbot_service import WeatherChatbot

def setup_chatbot():
    """Initialize the chatbot if not already in session state."""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = WeatherChatbot()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def display_chatbot(weather_data=None):
    """Display the chatbot interface."""
    setup_chatbot()
    
    st.markdown('<h3 class="text-2xl font-bold text-blue-600 mb-4">Flight Weather Assistant</h3>', unsafe_allow_html=True)
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="p-3 mb-2 rounded-lg bg-blue-100 text-right">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="p-3 mb-2 rounded-lg bg-gray-100">{message["content"]}</div>', unsafe_allow_html=True)
    
    # User input
    user_input = st.text_input("Ask me about flight weather...", key="chatbot_input")
    
    if st.button("Send", key="send_chat") or user_input:
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get chatbot response
            response = st.session_state.chatbot.process_message(user_input, weather_data)
            
            # Add chatbot response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Clear input and rerun to update display
            st.session_state.chatbot_input = ""
            st.experimental_rerun()