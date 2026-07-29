import requests

def weather_api(location: str = "", lat: float = None, lon: float = None):
    """
    Real weather tool using Open-Meteo.
    Accepts either a location string or explicit lat/lon.
    """

    # If lat/lon not provided, geocode the location
    if lat is None or lon is None:
        try:
            geo = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": location, "count": 1},
                timeout=10
            ).json()

            if "results" not in geo or not geo["results"]:
                return {"error": f"Could not geocode location '{location}'"}

            lat = geo["results"][0]["latitude"]
            lon = geo["results"][0]["longitude"]

        except Exception as e:
            return {"error": f"Geocoding failed: {e}"}

    # Fetch weather
    try:
        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True
            },
            timeout=10
        ).json()

        if "current_weather" not in weather:
            return {"error": "No current weather data returned"}

        return {
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": weather["current_weather"]["temperature"],
            "windspeed": weather["current_weather"]["windspeed"],
            "weathercode": weather["current_weather"]["weathercode"],
            "time": weather["current_weather"]["time"]
        }

    except Exception as e:
        return {"error": f"Weather API failed: {e}"}

