import requests

def weather_api(location: str) -> dict:
    """
    Fetch current weather for a location using Open-Meteo.
    Returns:
    {
      "location": "<user input>",
      "raw": {
        "geocoding": { ... },
        "forecast": { ... }
      }
    }
    or an error dict.
    """
    location = location.strip()
    if not location:
        return {"error": "Empty location"}

    # --- Geocoding ---
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": location, "count": 1}

    try:
        geo_resp = requests.get(geo_url, params=geo_params, timeout=5)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
    except Exception as e:
        return {"error": f"Geocoding error: {e}"}

    results = geo_data.get("results") or []
    if not results:
        return {"error": f"Could not geocode location '{location}'",
                "raw": {"geocoding": geo_data}}

    first = results[0]
    lat = first.get("latitude")
    lon = first.get("longitude")

    if lat is None or lon is None:
        return {"error": f"Missing coordinates for '{location}'",
                "raw": {"geocoding": geo_data}}

    # --- Forecast ---
    forecast_url = "https://api.open-meteo.com/v1/forecast"
    forecast_params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
    }

    try:
        forecast_resp = requests.get(forecast_url, params=forecast_params, timeout=5)
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()
    except Exception as e:
        return {
            "error": f"Forecast error: {e}",
            "raw": {"geocoding": geo_data},
        }

    return {
        "location": location,
        "raw": {
            "geocoding": geo_data,
            "forecast": forecast_data,
        },
    }
