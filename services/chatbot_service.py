# services/chatbot_service.py
import re
import random

class WeatherChatbot:
    """A simple rule-based chatbot for aviation weather queries."""
    
    def __init__(self):
        self.greetings = ["hello", "hi", "hey", "greetings"]
        self.farewells = ["bye", "goodbye", "see you", "farewell"]
        self.weather_keywords = ["weather", "conditions", "forecast", "metar", "taf"]
        self.flight_keywords = ["flight", "plan", "route", "path"]
        self.help_keywords = ["help", "how", "what", "guide", "instructions"]
        
        # Response templates
        self.templates = {
            "greeting": [
                "Hello! How can I help with your flight weather today?",
                "Hi there! Need aviation weather information?",
                "Welcome to FlightWeatherPro! How can I assist you?"
            ],
            "farewell": [
                "Goodbye! Safe flights!",
                "Farewell! Come back for your next flight planning.",
                "See you later! Blue skies and tailwinds!"
            ],
            "weather_general": [
                "I can provide weather information for any airport in your flight plan. Just specify the ICAO code.",
                "Would you like me to explain a particular weather condition or term?",
                "For detailed weather, please enter a flight plan in the format: ICAO,Altitude,ICAO,Altitude,..."
            ],
            "flight_plan": [
                "To create a flight plan, enter airport codes and altitudes in the format: ICAO,Altitude,ICAO,Altitude,...",
                "Your flight plan should include waypoints as ICAO codes with corresponding altitudes in feet.",
                "For example, try: KPHX,1500,KLAX,35000,KJFK,39000"
            ],
            "help": [
                "I can help with flight weather information. Try asking about specific airports or how to enter a flight plan.",
                "Need help with something specific? Try asking about METARs, TAFs, or how to interpret weather symbols.",
                "You can ask about weather conditions, flight planning, or specific aviation weather terms."
            ],
            "fallback": [
                "I'm not sure I understand. Try asking about weather conditions or flight planning.",
                "Could you rephrase your question? I'm here to help with aviation weather.",
                "I didn't catch that. Ask me about weather reports, flight plans, or specific airports."
            ]
        }
        
        # Context tracking
        self.context = {
            "last_icao": None,
            "discussed_weather": False
        }
    
    def process_message(self, message, weather_data=None):
        """Process user message and return a response."""
        message = message.lower().strip()
        
        # Check for greetings
        if any(greeting in message for greeting in self.greetings):
            return random.choice(self.templates["greeting"])
        
        # Check for farewells
        if any(farewell in message for farewell in self.farewells):
            return random.choice(self.templates["farewell"])
        
        # Check for ICAO codes
        icao_match = re.search(r'\b([A-Z]{4})\b', message, re.IGNORECASE)
        if icao_match:
            icao = icao_match.group(1).upper()
            self.context["last_icao"] = icao
            if weather_data and icao in weather_data:
                self.context["discussed_weather"] = True
                classification, _ = weather_data[icao]["classification"]
                return f"For {icao}, the current weather classification is {classification}. Would you like more details?"
            else:
                return f"I recognized airport code {icao}. Please generate a weather briefing to see conditions."
        
        # Check for weather queries
        if any(keyword in message for keyword in self.weather_keywords):
            return random.choice(self.templates["weather_general"])
        
        # Check for flight plan queries
        if any(keyword in message for keyword in self.flight_keywords):
            return random.choice(self.templates["flight_plan"])
        
        # Check for help requests
        if any(keyword in message for keyword in self.help_keywords):
            return random.choice(self.templates["help"])
        
        # Fallback response
        return random.choice(self.templates["fallback"])

    def get_additional_info(self, icao, weather_data):
        """Get additional information about weather at a specific location."""
        if not weather_data or icao not in weather_data:
            return f"I don't have weather data for {icao} yet. Please generate a weather briefing first."
        
        data = weather_data[icao]
        metar = data.get("METAR", "No METAR available")
        taf = data.get("TAF", "No TAF available")
        
        response = f"Here's more information about {icao}:\n\n"
        response += f"METAR: {metar}\n\n"
        response += f"TAF: {taf}\n\n"
        
        if "CLR" in metar or "SKC" in metar:
            response += "Conditions appear to be clear. Good visibility expected."
        elif "OVC" in metar or "BKN" in metar:
            response += "Significant cloud cover reported. Check ceiling heights."
        
        return response