FlightWeatherPro is a Streamlit app that serves to offer pilots, flight dispatchers, and aviation enthusiasts real-time weather details of any flight plan specified. By entering a series of ICAO airport codes and preferred altitudes, users have instant access to METAR, TAF, PIREP, and SIGMET information, in addition to a visual display of the flight track and weather conditions on an interactive map.

Features

Intuitive Flight Plan Entry: Simply enter your flight plan as a list of ICAO airport codes and altitudes separated by commas (e.g., `KPHX,1500,KLAX,35000,KJFK,39000`).
Detailed Weather Information: Fetches and displays METARs (Meteorological Terminal Aviation Routine Reports), TAFs (Terminal Aerodrome Forecasts), PIREPs (Pilot Reports), and SIGMETs (Significant Meteorological Information) for every waypoint.
Brief Weather Summaries: Gives a brief summary of the weather, forecasts, pilot reports, and hazards for every point along your flight plan.
Detailed Weather Reports: Presents the raw weather data with simple formatting for detailed analysis.
Interactive Weather Map: Graphically represents the flight path on a map with color-coded markers denoting the general weather category (VFR, Significant, Severe) for each airport.
Recent Flight History: Remembers your previous five flight plans for easy access and reuse.
Customizable Map Style: Select various map tile styles (CartoDB Positron, OpenStreetMap, Stamen Terrain).
Display Unit Options: Switch between Imperial and Metric units (currently impacts altitude display in summaries and reports).
Clear and User-Friendly Interface: Built with a clean and accessible design for simple navigation.

Getting Started

1.  Installation: If you haven't, install Streamlit and the libraries you need:
    ```bash
    pip install streamlit requests folium streamlit-folium
    ```

2.  Running the Application: Save the given Python script as a `.py` file (e.g., `flight_weather_pro.py`) and run it with Streamlit:
    ```bash
    streamlit run flight_weather_pro.py
    ```

3.  Utilizing the Application:
    - Go to the URL shown in your terminal.
    - In the sidebar, you can view recent flights, customize map styles, and choose your desired display units.
    - In the main area, input your flight plan in the prescribed format (e.g., `ICAO1,Altitude1,ICAO2,Altitude2,.`).
    - Press the "Generate Weather Briefing" button.
- See the weather summary, detailed report, and interactive weather map in their respective tabs.

Flight Plan format

Input your flight plan as a comma-delimited string with each waypoint being an ICAO airport code followed by the intended altitude in feet.

Example: `KPHX,1500,KLAX,35000,KJFK,39000`

-   ICAO Codes: Should be legitimate International Civil Aviation Organization airport codes.
-   Altitude: Include the altitude in feet for every waypoint.

Data Sources

-   Aviation Weather Center (AWC): Offers real-time METAR, TAF, PIREP, and SIGMET data via their API.
-   OpenFlights Database: Offers airport location information (latitude and longitude) employed in mapping.

Disclaimer

FlightWeatherPro is for informational use only and cannot be used as the sole source of flight planning or operating decisions. Always refer to official air traffic weather services and regulations prior to performing any flight operations. The data accuracy and availability are subject to the external APIs and databases utilized.


## License

Project is open-sourced and uses [Specify License Here] licensing.

## Contact

If there are any inquiries or recommendations, do not hesitate to contact us at [Your Contact Information/Email].
