import requests

def get_metar(icao_id):
    """Fetch METAR data for an ICAO ID."""
    try:
        url = f"https://aviationweather.gov/api/data/metar?ids={icao_id}&format=json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.json():
            return response.json()[0].get("rawOb", "No METAR available")
        return "No METAR available"
    except Exception:
        return "Error fetching METAR"

def get_taf(icao_id):
    """Fetch TAF data for an ICAO ID."""
    try:
        url = f"https://aviationweather.gov/api/data/taf?ids={icao_id}&format=json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.json():
            return response.json()[0].get("rawOb", "No TAF available")
        return "No TAF available"
    except Exception:
        return "Error fetching TAF" 