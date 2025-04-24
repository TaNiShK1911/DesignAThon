# services/report_service.py
import datetime
import streamlit as st
import base64
import io
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def generate_weather_report(flight_plan, waypoints, weather_data_list, airport_coords):
    """Generate a comprehensive weather report for the flight plan."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    report = io.StringIO()
    report.write(f"""
# Flight Weather Briefing
## {flight_plan}
Generated on: {now}

## Flight Summary
""")
    
    # Flight summary information
    total_distance = calculate_distance(waypoints, airport_coords)
    report.write(f"* **Route**: {' → '.join([icao for icao, _ in waypoints])}\n")
    report.write(f"* **Distance**: {total_distance:.1f} NM\n")
    report.write(f"* **Waypoints**: {len(waypoints)}\n")
    
    # Weather overview
    report.write("\n## Weather Overview\n")
    conditions = [classify_conditions(weather_data) for weather_data in weather_data_list]
    report.write(f"* **Overall Conditions**: {get_overall_conditions(conditions)}\n")
    report.write(f"* **Hazard Areas**: {count_hazards(weather_data_list)}\n")
    
    # Detailed waypoint information
    report.write("\n## Waypoint Details\n")
    for i, ((icao, altitude), weather_data) in enumerate(zip(waypoints, weather_data_list)):
        report.write(f"\n### {i+1}. {icao} at {altitude}ft\n")
        report.write(f"* **METAR**: {weather_data.get('METAR', 'Unavailable')}\n")
        report.write(f"* **TAF**: {weather_data.get('TAF', 'Unavailable')}\n")
        if weather_data.get('PIREP') and weather_data.get('PIREP') != "No recent PIREP":
            report.write(f"* **PIREP**: {weather_data.get('PIREP')}\n")
        if weather_data.get('SIGMET') and weather_data.get('SIGMET') != "No active SIGMET":
            report.write(f"* **SIGMET**: {weather_data.get('SIGMET')}\n")
    
    # Recommendations
    report.write("\n## Recommendations\n")
    report.write(generate_recommendations(weather_data_list, waypoints))
    
    return report.getvalue()

def generate_weather_report_html(flight_plan, waypoints, weather_data_list, airport_coords):
    """Generate an HTML version of the weather report."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2563eb; }}
            h2 {{ color: #1e3a8a; border-bottom: 1px solid #93c5fd; padding-bottom: 5px; }}
            h3 {{ color: #1e40af; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .warning {{ color: #b91c1c; font-weight: bold; }}
            .safe {{ color: #15803d; }}
            .caution {{ color: #b45309; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #e0ecff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Flight Weather Briefing</h1>
            <h2>{flight_plan}</h2>
            <p>Generated on: {now}</p>
            
            <h2>Flight Summary</h2>
    """
    
    # Flight summary information
    total_distance = calculate_distance(waypoints, airport_coords)
    html += f"<p><strong>Route</strong>: {' → '.join([icao for icao, _ in waypoints])}</p>"
    html += f"<p><strong>Distance</strong>: {total_distance:.1f} NM</p>"
    html += f"<p><strong>Waypoints</strong>: {len(waypoints)}</p>"
    
    # Weather overview
    html += "<h2>Weather Overview</h2>"
    conditions = [classify_conditions(weather_data) for weather_data in weather_data_list]
    overall = get_overall_conditions(conditions)
    css_class = "safe" if "Good" in overall else "caution" if "Marginal" in overall else "warning"
    html += f"<p><strong>Overall Conditions</strong>: <span class='{css_class}'>{overall}</span></p>"
    
    hazards = count_hazards(weather_data_list)
    css_class = "safe" if "None" in hazards else "warning"
    html += f"<p><strong>Hazard Areas</strong>: <span class='{css_class}'>{hazards}</span></p>"
    
    # Detailed waypoint information
    html += "<h2>Waypoint Details</h2>"
    html += "<table>"
    html += "<tr><th>Waypoint</th><th>Altitude</th><th>Conditions</th><th>Details</th></tr>"
    
    for i, ((icao, altitude), weather_data) in enumerate(zip(waypoints, weather_data_list)):
        condition = classify_conditions(weather_data)
        css_class = "safe" if condition == "VFR" else "caution" if condition == "MVFR" else "warning"
        
        details = ""
        if "SIGMET" in weather_data and weather_data["SIGMET"] != "No active SIGMET":
            details += f"<span class='warning'>SIGMET</span>: {weather_data['SIGMET']}<br>"
        if "PIREP" in weather_data and weather_data["PIREP"] != "No recent PIREP":
            details += f"PIREP: {weather_data['PIREP']}<br>"
        
        html += f"<tr>"
        html += f"<td>{icao}</td>"
        html += f"<td>{altitude}ft</td>"
        html += f"<td class='{css_class}'>{condition}</td>"
        html += f"<td>{details}</td>"
        html += f"</tr>"
    
    html += "</table>"
    
    # Recommendations
    html += "<h2>Recommendations</h2>"
    html += f"<p>{generate_recommendations(weather_data_list, waypoints).replace('\n', '<br>')}</p>"
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

def get_download_link(report, filename, format_type="markdown"):
    """Generate a download link for the report."""
    if format_type == "html":
        b64 = base64.b64encode(report.encode()).decode()
        mime = "text/html"
        ext = "html"
    else:  # markdown
        b64 = base64.b64encode(report.encode()).decode()
        mime = "text/markdown"
        ext = "md"
    
    href = f'<a href="data:{mime};base64,{b64}" download="{filename}.{ext}" class="download-button">Download {format_type.upper()} Report</a>'
    return href

def classify_conditions(weather_data):
    """Classify weather conditions as VFR, MVFR, or IFR."""
    metar = weather_data.get("METAR", "")
    if not metar:
        return "Unknown"
    
    if "OVC" in metar and any(cloud_height <= 500 for cloud_height in extract_cloud_heights(metar)):
        return "IFR"
    elif "BKN" in metar and any(cloud_height <= 1000 for cloud_height in extract_cloud_heights(metar)):
        return "MVFR"
    else:
        return "VFR"

def extract_cloud_heights(metar):
    """Extract cloud heights from METAR."""
    import re
    # Look for patterns like "OVC050" (overcast at 5000 feet)
    cloud_layers = re.findall(r'(OVC|BKN|SCT|FEW)(\d{3})', metar)
    heights = [int(height) * 100 for _, height in cloud_layers]
    return heights if heights else [10000]  # Default to high ceiling if none found

def get_overall_conditions(conditions):
    """Get overall flight conditions assessment."""
    if "IFR" in conditions:
        return "Challenging - IFR conditions present"
    elif "MVFR" in conditions:
        return "Marginal - Mixed VFR/IFR conditions"
    else:
        return "Good - VFR conditions throughout"

def count_hazards(weather_data_list):
    """Count hazardous weather areas in the flight path."""
    hazard_count = sum(1 for data in weather_data_list 
                     if data.get("SIGMET") and data.get("SIGMET") != "No active SIGMET")
    if hazard_count == 0:
        return "None reported"
    else:
        return f"{hazard_count} area{'s' if hazard_count > 1 else ''} with active SIGMETs"

def calculate_distance(waypoints, airport_coords):
    """Calculate total distance of flight path in nautical miles."""
    import math
    
    def haversine(lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in NM."""
        R = 3440.065  # Earth radius in NM
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    total_distance = 0
    for i in range(len(waypoints) - 1):
        icao1, _ = waypoints[i]
        icao2, _ = waypoints[i+1]
        lat1, lon1 = airport_coords[icao1]
        lat2, lon2 = airport_coords[icao2]
        distance = haversine(lat1, lon1, lat2, lon2)
        total_distance += distance
    
    return total_distance

def generate_recommendations(weather_data_list, waypoints):
    """Generate flight recommendations based on weather data."""
    conditions = [classify_conditions(data) for data in weather_data_list]
    
    recommendations = ""
    
    # Check for IFR conditions
    ifr_waypoints = [waypoints[i][0] for i, cond in enumerate(conditions) if cond == "IFR"]
    if ifr_waypoints:
        recommendations += f"- IFR conditions at {', '.join(ifr_waypoints)}. File an IFR flight plan.\n"
    
    # Check for SIGMETs
    sigmet_waypoints = [waypoints[i][0] for i, data in enumerate(weather_data_list) 
                        if data.get("SIGMET") and data.get("SIGMET") != "No active SIGMET"]
    if sigmet_waypoints:
        recommendations += f"- Active SIGMETs near {', '.join(sigmet_waypoints)}. Consider route deviation.\n"
    
    # Check for cloud layers
    high_cloud_waypoints = [waypoints[i][0] for i, data in enumerate(weather_data_list)
                           if data.get("METAR") and ("OVC" in data["METAR"] or "BKN" in data["METAR"])]
    if high_cloud_waypoints:
        recommendations += f"- Significant cloud coverage at {', '.join(high_cloud_waypoints)}. Review ceiling heights.\n"
    
    # General recommendations
    if "IFR" in conditions:
        recommendations += "- Ensure IFR currency and equipment requirements are met.\n"
    
    if not recommendations:
        recommendations += "- Good VFR conditions throughout. Standard precautions advised.\n"
    
    return recommendations

def create_route_profile_chart(waypoints, weather_data_list, airport_coords):
    """Create a matplotlib figure showing the flight profile with weather severity."""
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract data for plotting
    icao_labels = [icao for icao, _ in waypoints]
    altitudes = [alt for _, alt in waypoints]
    
    # Calculate distances
    distances = [0]
    total_distance = 0
    for i in range(len(waypoints) - 1):
        icao1, _ = waypoints[i]
        icao2, _ = waypoints[i+1]
        lat1, lon1 = airport_coords[icao1]
        lat2, lon2 = airport_coords[icao2]
        
        # Simple distance calculation (not accurate for long distances)
        import math
        R = 3440.065  # Earth radius in NM
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        total_distance += distance
        distances.append(total_distance)
    
    # Create x points for smooth curve
    x_smooth = np.linspace(0, total_distance, 100)
    
    # Interpolate altitudes
    from scipy.interpolate import interp1d
    if len(waypoints) > 1:
        altitude_curve = interp1d(distances, altitudes, kind='linear')
        y_smooth = altitude_curve(x_smooth)
    else:
        y_smooth = np.array([altitudes[0]] * 100)
        
    # Get weather severity
    severity = []
    for data in weather_data_list:
        if data.get("SIGMET") and data.get("SIGMET") != "No active SIGMET":
            severity.append(2)  # High severity
        elif data.get("METAR") and ("OVC" in data["METAR"] or "BKN" in data["METAR"]):
            severity.append(1)  # Medium severity
        else:
            severity.append(0)  # Low severity
    
    # Plot flight path
    ax.plot(distances, altitudes, 'o-', color='blue', markersize=8)
    
    # Create color segments for the smoothed curve
    if len(waypoints) > 1:
        color_map = LinearSegmentedColormap.from_list("", ["green", "yellow", "red"])
        severity_interp = interp1d(distances, severity, kind='linear')
        severity_smooth = severity_interp(x_smooth)
        
        # Plot the smooth curve with colors
        for i in range(len(x_smooth)-1):
            sev = severity_smooth[i]
            color = color_map(sev/2)  # Normalize to [0, 1]
            ax.plot(x_smooth[i:i+2], y_smooth[i:i+2], color=color, linewidth=3)
    
    # Add labels and formatting
    ax.set_xlabel('Distance (NM)')
    ax.set_ylabel('Altitude (ft)')
    ax.set_title('Flight Profile with Weather Conditions')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add airport labels
    for i, icao in enumerate(icao_labels):
        ax.text(distances[i], altitudes[i], f" {icao}", verticalalignment='bottom')
    
    # Add legend
    import matplotlib.patches as mpatches
    legend_elements = [
        mpatches.Patch(color='green', label='Good Conditions'),
        mpatches.Patch(color='yellow', label='Marginal Conditions'),
        mpatches.Patch(color='red', label='Hazardous Conditions')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    return fig