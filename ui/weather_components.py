import folium
from services.weather_service import classify_weather

def generate_summary(weather_data, icao_id, altitude):
    """Generate a concise weather summary for a waypoint using an HTML list."""
    summary = f"<b>{icao_id} (Altitude: {altitude}ft)</b>:<ul>"
    metar = weather_data.get("METAR", "")
    if "CLR" in metar or "SKC" in metar:
        summary += "<li><b>Conditions</b>: Clear skies 🌞</li>"
    elif "OVC" in metar or "BKN" in metar:
        summary += "<li><b>Conditions</b>: Cloudy ☁️</li>"
    else:
        summary += "<li><b>Conditions</b>: Variable 🌥️</li>"
    taf = weather_data.get("TAF", "")
    summary += "<li><b>Forecast</b>: Stable conditions expected 📈</li>" if taf else "<li><b>Forecast</b>: Unavailable ❓</li>"
    pirep = weather_data.get("PIREP", "")
    summary += "<li><b>Pilot Reports</b>: No significant issues ✅</li>" if "No recent PIREP" in pirep else f"<li><b>Pilot Reports</b>: {pirep} ✈️</li>"
    sigmet = weather_data.get("SIGMET", "")
    summary += "<li><b>Hazards</b>: None reported 🟢</li>" if "No active SIGMET" in sigmet else f"<li><b>Hazards</b>: {sigmet} ⚠️</li>"
    summary += "</ul>"
    return summary

def generate_detailed_report(weather_data, icao_id, altitude):
    """Generate a detailed weather report for a waypoint with line breaks."""
    report = f"<b>Detailed Weather Report for {icao_id} (Altitude: {altitude}ft)</b>:<br>"
    report += f"- <b>METAR</b>: {weather_data.get('METAR', 'Unavailable')}<br>"
    report += f"- <b>TAF</b>: {weather_data.get('TAF', 'Unavailable')}<br>"
    report += f"- <b>PIREP</b>: {weather_data.get('PIREP', 'No recent PIREP')}<br>"
    report += f"- <b>SIGMET</b>: {weather_data.get('SIGMET', 'No active SIGMET')}<br>"
    classification, _ = classify_weather(weather_data)
    report += f"- <b>Weather Classification</b>: {classification}<br>"
    return report

def create_weather_map(waypoints, weather_data_list, airport_coords):
    """Create a Folium map with weather overlays."""
    lats = [airport_coords[icao][0] for icao, _ in waypoints]
    lons = [airport_coords[icao][1] for icao, _ in waypoints]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles="CartoDB Positron")
    
    for (icao_id, altitude), weather_data in zip(waypoints, weather_data_list):
        lat, lon = airport_coords[icao_id]
        classification, color = classify_weather(weather_data)
        folium.CircleMarker(
            location=[lat, lon],
            radius=12,
            popup=folium.Popup(f"<b>{icao_id}</b><br>Altitude: {altitude}ft<br>{classification}", max_width=300),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(m)
    
    path = [(airport_coords[icao][0], airport_coords[icao][1]) for icao, _ in waypoints]
    folium.PolyLine(
        path,
        color="blue",
        weight=3,
        opacity=0.8,
        tooltip="Flight Path"
    ).add_to(m)
    
    return m