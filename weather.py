# weather.py
import os
import sys
from dotenv import load_dotenv
import requests

# Load .env variables into the environment
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    print("Error: OPENWEATHER_API_KEY not set. Put it in a .env file.")
    sys.exit(1)

# OpenWeatherMap current weather endpoint (we'll add params)
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def fetch_weather_for_city(city_name: str, units: str = "metric"):
    """
    Fetch current weather for a city using OpenWeatherMap.
    units: "metric" (Celsius) or "imperial" (Fahrenheit) or "standard" (Kelvin)
    Returns the JSON response dict or raises an exception on error.
    """
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": units
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()  # raises HTTPError for bad HTTP status codes
    except requests.exceptions.RequestException as e:
        # Network problem, DNS failure, connection timeout, etc.
        raise RuntimeError(f"Network/API request failed: {e}")

    data = resp.json()
    # OpenWeatherMap returns codes like 200 OK or 404 with JSON containing "message"
    if data.get("cod") not in (200, "200"):
        # API-level error (like city not found or invalid API key)
        # data may contain 'message' to explain
        message = data.get("message", "Unknown error from API")
        raise RuntimeError(f"API error: {message} (cod={data.get('cod')})")

    return data

def get_temperature_from_response(data: dict):
    """
    Extracts temperature and other useful info from the API response.
    Returns (temp_value, feels_like, unit_string)
    """
    main = data.get("main", {})
    temp = main.get("temp")
    feels_like = main.get("feels_like")
    if temp is None:
        raise KeyError("Temperature field missing from API response")
    return temp, feels_like

def pretty_print_weather(data: dict, units: str = "metric"):
    name = data.get("name", "Unknown location")
    syscountry = data.get("sys", {}).get("country", "")
    weather_desc = data.get("weather", [{}])[0].get("description", "No description")
    temp, feels_like = get_temperature_from_response(data)
    unit_symbol = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
    print(f"Location: {name}, {syscountry}")
    print(f"Weather: {weather_desc}")
    print(f"Temperature: {temp}{unit_symbol}")
    if feels_like is not None:
        print(f"Feels like: {feels_like}{unit_symbol}")

def main():
    # Basic CLI: python weather.py London metric
    if len(sys.argv) < 2:
        print("Usage: python weather.py <city name> [units]")
        print("Units: metric (C), imperial (F), standard (K). Default: metric")
        sys.exit(1)

    city = sys.argv[1]
    units = sys.argv[2] if len(sys.argv) >= 3 else "metric"

    try:
        data = fetch_weather_for_city(city, units=units)
        pretty_print_weather(data, units=units)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
