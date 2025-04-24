# ui/weather_components.py
import folium
from folium.plugins import HeatMap
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
    summary += "<li><b>Hazards</b>: None reported 🟢</li>" if (("No active SIGMET" in sigmet) or (not sigmet)) else f"<li><b>Hazards</b>: {sigmet} ⚠️</li>"
    summary += "</ul>"
    return summary

def generate_detailed_report(weather_data, icao_id, altitude):
    """Generate a detailed weather report for a waypoint with line breaks."""
    report = f"<b>Detailed Weather Report for {icao_id} (Altitude: {altitude}ft)</b>:<br>"
    report += f"- <b>METAR</b>: {weather_data.get('METAR', 'Unavailable')}<br>"
    report += f"- <b>TAF</b>: {weather_data.get('TAF', 'Unavailable')}<br>"
    report += f"- <b>PIREP</b>: {weather_data.get('PIREP', 'No recent PIREP')}<br>"
    report += f"- <b>SIGMET</b>: {weather_data.get('SIGMET') if weather_data.get('SIGMET') else "No activate SIGMET"}<br>"
    classification, _ = classify_weather(weather_data)
    report += f"- <b>Weather Classification</b>: {classification}<br>"
    return report

def create_weather_map(waypoints, weather_data_list, airport_coords):
    """Create a Folium map with weather overlays and heatmap."""
    lats = [airport_coords[icao][0] for icao, _ in waypoints]
    lons = [airport_coords[icao][1] for icao, _ in waypoints]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles="CartoDB Positron")
    
    # Add waypoint markers
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

    # Prepare heatmap data
    heat_data = []
    for i in range(len(waypoints)-1):
        start_lat, start_lon = airport_coords[waypoints[i][0]]
        end_lat, end_lon = airport_coords[waypoints[i+1][0]]
        _, color = classify_weather(weather_data_list[i])
        intensity = 0.3 if color == "green" else 0.6 if color == "yellow" else 1.0
        steps = 10
        for step in range(steps + 1):
            factor = step / steps
            lat = start_lat + factor * (end_lat - start_lat)
            lon = start_lon + factor * (end_lon - start_lon)
            heat_data.append([lat, lon, intensity])
    
    # Add heatmap layer
    HeatMap(
        heat_data,
        radius=15,
        blur=10,
        gradient={'0.3': 'blue', '0.6': 'yellow', '1': 'red'},
        name='Weather Heatmap'
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m