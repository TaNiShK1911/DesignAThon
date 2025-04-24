# File: services/pilot_briefing_service.py
from services.weather_service import get_weather_summary
from services.airport_service import get_airport_info
from services.flight_plan_service import get_flight_plan_summary
from services.avwx_service import get_metar, get_taf
from fpdf import FPDF
import os

def safe_fetch(func, *args, default="_Data not available._"):
    try:
        result = func(*args)
        return result if result else default
    except Exception as e:
        return f"_Error fetching data: {e}_"

def determine_vfr_safety(metar_text):
    if any(x in metar_text for x in ["1SM", "1/2SM", "OVC", "BKN"]):
        return "V-F-R NOT RECOMMENDED due to low visibility or ceiling conditions."
    return "V-F-R conditions appear acceptable based on current METAR."

def parse_route_input(route_input):
    items = route_input.split(',')
    route = []
    for i in range(0, len(items), 2):
        icao = items[i].strip().upper()
        altitude = items[i+1].strip() if i+1 < len(items) else "Unknown"
        route.append((icao, altitude))
    return route

def generate_pilot_briefing_from_route(route_input, flight_date):
    route = parse_route_input(route_input)
    if len(route) < 2:
        return "Invalid route input. Please provide at least departure and destination."

    departure = route[0][0]
    destination = route[-1][0]
    briefing = []

    briefing.append(f"Date of Flight: {flight_date}")
    briefing.append(f"From: {departure} → To: {destination}\n")

    briefing.append("\n---\n\nSECTION 1: DEPARTURE AIRPORT INFO")
    briefing.append(safe_fetch(get_airport_info, departure))

    briefing.append("\n---\n\nSECTION 2: DESTINATION AIRPORT INFO")
    briefing.append(safe_fetch(get_airport_info, destination))

    briefing.append("\n---\n\nSECTION 3: WEATHER BRIEFING")
    briefing.append(safe_fetch(get_weather_summary, departure, destination, flight_date))

    briefing.append("\n---\n\nSECTION 4: CURRENT METAR & TAF")
    dep_metar = get_metar(departure)
    briefing.append(f"METAR for {departure}:\n{dep_metar}\n")
    briefing.append(f"TAF for {departure}:\n{get_taf(departure)}\n")
    briefing.append(f"TAF for {destination}:\n{get_taf(destination)}")

    briefing.append("\n---\n\nSECTION 5: VFR FLIGHT ADVISORY")
    briefing.append(determine_vfr_safety(dep_metar))

    briefing.append("\n---\n\nSECTION 6: FLIGHT PLAN SUMMARY")
    for leg in route:
        icao, altitude = leg
        briefing.append(f"Waypoint: {icao} | Planned Altitude: {altitude} ft")

    briefing.append("\n---\n\nSECTION 7: FAA FORM RECORD")
    briefing.append(f"""
FAA Form 7233-2 (Preflight Briefing Log)
----------------------------------------
Date: {flight_date}
Departure: {departure}
Destination: {destination}
Type of Briefing: Standard
Specialist ID: [AUTO]
Time Issued: [AUTO]
VNR: {determine_vfr_safety(dep_metar)}
""")

    return "\n".join(briefing)

def export_briefing_to_pdf(departure, destination, flight_date, briefing_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "PILOT WEATHER BRIEFING - FAA FORM 7233-2", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"DATE OF FLIGHT: {flight_date}", ln=True)
    pdf.cell(0, 10, f"ROUTE: {departure} -> {destination}", ln=True)
    pdf.ln(5)

    # Define FAA-style section headers
    section_titles = [
        "DEPARTURE AIRPORT INFORMATION",
        "DESTINATION AIRPORT INFORMATION",
        "WEATHER BRIEFING",
        "CURRENT METAR AND TAF",
        "VFR FLIGHT ADVISORY",
        "FLIGHT PLAN SUMMARY",
        "FAA FORM LOG ENTRY"
    ]

    # Clean up the briefing text by removing markdown characters
    briefing_text = briefing_text.replace("#", "").replace("*", "").replace("_", "")

    # Break into sections and render cleanly
    sections = briefing_text.split("\n---\n\n")
    for i, section in enumerate(sections[1:], start=0):  # Skip general info
        title = section_titles[i] if i < len(section_titles) else f"SECTION {i+1}"
        lines = section.strip().split("\n", 1)
        body = lines[1] if len(lines) == 2 else lines[0]

        # Add section header with underline
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 8, title.upper())
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        # Add section content
        pdf.set_font("Arial", "", 11)
        
        # Check if body is empty or contains error messages
        if not body.strip() or "Error fetching data" in body or "Data not available" in body:
            pdf.set_text_color(128, 128, 128)  # Gray color for unavailable data
            pdf.multi_cell(0, 8, "INFORMATION NOT AVAILABLE")
            pdf.set_text_color(0, 0, 0)  # Reset to black
        else:
            # Split body into paragraphs and add proper spacing
            paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
            for para in paragraphs:
                if "Error fetching data" in para or "Data not available" in para:
                    pdf.set_text_color(128, 128, 128)  # Gray color for unavailable data
                    pdf.multi_cell(0, 8, "INFORMATION NOT AVAILABLE")
                    pdf.set_text_color(0, 0, 0)  # Reset to black
                else:
                    pdf.multi_cell(0, 8, para)
                pdf.ln(3)
        pdf.ln(5)

    # Footer
    pdf.set_y(-25)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 10, "Generated per FAA Order JO 7110.10 and FAA Form 7233-2 briefing standards.", ln=True, align="C")

    output_path = f"briefings/{departure}_{destination}_{flight_date}.pdf"
    os.makedirs("briefings", exist_ok=True)
    pdf.output(output_path)
    return output_path