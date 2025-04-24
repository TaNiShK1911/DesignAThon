# services/weather_service.py
import requests

# Constants
API_BASE_URL = "https://aviationweather.gov/api/data"

def fetch_weather_data(icao_id):
    """Fetch METAR, TAF, PIREP, and SIGMET data for an ICAO ID."""
    try:
        weather_data = {"METAR": "", "TAF": "", "PIREP": "", "SIGMET": ""}
        metar_url = f"{API_BASE_URL}/metar?ids={icao_id}&format=json"
        metar_response = requests.get(metar_url, timeout=5)
        if metar_response.status_code == 200 and metar_response.json():
            weather_data["METAR"] = metar_response.json()[0].get("rawOb", "No METAR available")
        
        taf_url = f"{API_BASE_URL}/taf?ids={icao_id}&format=json"
        taf_response = requests.get(taf_url, timeout=5)
        if taf_response.status_code == 200 and taf_response.json():
            weather_data["TAF"] = taf_response.json()[0].get("rawOb", "No TAF available")
        
        pirep_url = f"{API_BASE_URL}/pirep?format=json"
        pirep_response = requests.get(pirep_url, timeout=5)
        if pirep_response.status_code == 200:
            pireps = [p for p in pirep_response.json() if icao_id in p.get("rawOb", "")]
            weather_data["PIREP"] = pireps[0].get("rawOb", "No recent PIREP") if pireps else "No recent PIREP"
        
        sigmet_url = f"{API_BASE_URL}/sigmet?format=json"
        sigmet_response = requests.get(sigmet_url, timeout=5)
        if sigmet_response.status_code == 200:
            sigmets = [s for s in sigmet_response.json() if icao_id in s.get("rawOb", "")]
            weather_data["SIGMET"] = sigmets[0].get("rawOb", "No active SIGMET") if sigmets else "No active SIGMET"
        
        return weather_data
    except Exception as e:
        return {"Error": f"Unable to fetch weather data for {icao_id}. Please try again later."}

def classify_weather(weather_data):
    """Classify weather as VFR, Significant, or Severe."""
    metar = weather_data.get("METAR", "")
    sigmet = weather_data.get("SIGMET", "")
    if "No active SIGMET" in sigmet and ("CLR" in metar or "SKC" in metar):
        return "VFR Conditions", "green"
    elif "TS" in metar or "SEV" in sigmet:
        return "Severe Weather Activity", "red"
    else:
        return "Significant Weather Activity", "yellow"
    
def get_weather_summary(departure, destination, flight_date):
    """Generate a weather summary for the flight route."""
    try:
        departure_weather = fetch_weather_data(departure)
        destination_weather = fetch_weather_data(destination)
        
        if "Error" in departure_weather or "Error" in destination_weather:
            return None
            
        summary = []
        
        # Departure weather
        summary.append(f"### Departure ({departure})")
        summary.append(f"*Current Conditions:* {departure_weather['METAR']}")
        summary.append(f"*Forecast:* {departure_weather['TAF']}")
        summary.append(f"*Recent Reports:* {departure_weather['PIREP']}")
        summary.append(f"*SIGMETs:* {departure_weather['SIGMET']}")
        
        # Destination weather
        summary.append(f"\n### Destination ({destination})")
        summary.append(f"*Current Conditions:* {destination_weather['METAR']}")
        summary.append(f"*Forecast:* {destination_weather['TAF']}")
        summary.append(f"*Recent Reports:* {destination_weather['PIREP']}")
        summary.append(f"*SIGMETs:* {destination_weather['SIGMET']}")
        
        return "\n".join(summary)
    except Exception as e:
        return None