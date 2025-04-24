# services/flight_plan_service.py

def parse_flight_plan(flight_plan, airport_coords):
    """Parse flight plan into a list of (airport_id, altitude) tuples."""
    try:
        items = flight_plan.strip().split(',')
        if len(items) % 2 != 0:
            raise ValueError("Invalid flight plan format. Must have pairs of Airport ID and Altitude.")
        waypoints = []
        for i in range(0, len(items), 2):
            icao = items[i].upper()
            altitude_str = items[i+1]
            if icao not in airport_coords:
                raise ValueError(f"Unknown or unsupported ICAO ID: {icao}")
            try:
                altitude = int(altitude_str)
                if altitude < 0:
                    raise ValueError(f"Altitude must be a positive integer: {altitude_str}")
            except ValueError:
                raise ValueError(f"Invalid altitude value: {altitude_str}. Must be a positive integer.")
            waypoints.append((icao, altitude))
        return waypoints
    except Exception as e:
        return f"Error parsing flight plan: {str(e)}"
    
def get_flight_plan_summary(departure, destination, flight_date):
    """Generate a summary of the flight plan."""
    try:
        summary = []
        summary.append(f"### Route Summary")
        summary.append(f"*Departure:* {departure}")
        summary.append(f"*Destination:* {destination}")
        summary.append(f"*Flight Date:* {flight_date}")
        
        # Add estimated flight time (placeholder)
        summary.append("\n### Estimated Flight Time")
        summary.append("Note: This is a placeholder. Actual flight time would be calculated based on aircraft performance and weather conditions.")
        
        # Add route description
        summary.append("\n### Route Description")
        summary.append(f"Direct route from {departure} to {destination}.")
        
        return "\n".join(summary)
    except Exception as e:
        return None