# ============================================================
# INTELLIVOICE AI - LIVE WEATHER TOOL
# ============================================================

import requests


# ============================================================
# API URLS
# ============================================================

GEOCODING_API_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_API_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


# ============================================================
# WEATHER CODE DESCRIPTION
# ============================================================

WEATHER_CODES = {

    0: "Clear sky",

    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",

    45: "Fog",
    48: "Depositing rime fog",

    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",

    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",

    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",

    66: "Light freezing rain",
    67: "Heavy freezing rain",

    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",

    77: "Snow grains",

    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",

    85: "Slight snow showers",
    86: "Heavy snow showers",

    95: "Thunderstorm",

    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


# ============================================================
# GET LOCATION COORDINATES
# ============================================================

def get_coordinates(city: str):

    city = city.strip()

    if not city:
        return None

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:

        response = requests.get(
            GEOCODING_API_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as error:

        print(
            "GEOCODING API ERROR:",
            error
        )

        return None

    results = data.get(
        "results"
    )

    if not results:
        return None

    location = results[0]

    return {
        "name": location.get("name"),
        "country": location.get("country"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "timezone": location.get("timezone")
    }


# ============================================================
# GET LIVE CURRENT WEATHER
# ============================================================

def get_weather(city: str):

    city = city.strip()

    if not city:

        return {
            "success": False,
            "message": "Please provide a city name."
        }

    # --------------------------------------------------------
    # STEP 1: GEOCODING
    # --------------------------------------------------------

    location = get_coordinates(
        city
    )

    if not location:

        return {
            "success": False,
            "message": (
                f"I couldn't find weather data for "
                f"'{city}'. Please check the city name."
            )
        }

    latitude = location["latitude"]
    longitude = location["longitude"]

    # --------------------------------------------------------
    # STEP 2: LIVE WEATHER API
    # --------------------------------------------------------

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "rain,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "timezone": "auto",

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh"
    }

    try:

        response = requests.get(
            WEATHER_API_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as error:

        print(
            "WEATHER API ERROR:",
            error
        )

        return {
            "success": False,
            "message": (
                "Unable to retrieve live weather "
                "information right now."
            )
        }

    # --------------------------------------------------------
    # STEP 3: CURRENT DATA
    # --------------------------------------------------------

    current = data.get(
        "current"
    )

    if not current:

        return {
            "success": False,
            "message": (
                "Live weather information "
                "was not available."
            )
        }

    temperature = current.get(
        "temperature_2m"
    )

    humidity = current.get(
        "relative_humidity_2m"
    )

    apparent_temperature = current.get(
        "apparent_temperature"
    )

    precipitation = current.get(
        "precipitation"
    )

    rain = current.get(
        "rain"
    )

    weather_code = current.get(
        "weather_code"
    )

    wind_speed = current.get(
        "wind_speed_10m"
    )

    description = WEATHER_CODES.get(
        weather_code,
        "Unknown weather condition"
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "success": True,

        "city": location["name"],

        "country": location["country"],

        "temperature": temperature,

        "humidity": humidity,

        "apparent_temperature": apparent_temperature,

        "precipitation": precipitation,

        "rain": rain,

        "weather_code": weather_code,

        "description": description,

        "wind_speed": wind_speed,

        "timezone": location["timezone"],

        "time": current.get("time")
    }


# ============================================================
# FORMAT WEATHER RESPONSE
# ============================================================

def format_weather_response(weather_data):

    if not weather_data.get("success"):

        return weather_data.get(
            "message",
            "Unable to get live weather information."
        )

    city = weather_data["city"]
    country = weather_data["country"]

    temperature = weather_data["temperature"]

    humidity = weather_data["humidity"]

    apparent_temperature = (
        weather_data["apparent_temperature"]
    )

    description = weather_data["description"]

    wind_speed = weather_data["wind_speed"]

    rain = weather_data["rain"]

    time = weather_data["time"]

    return (
        f"🌤️ Live weather in {city}, {country}\n"
        f"🌡️ Temperature: {temperature}°C\n"
        f"🤗 Feels like: {apparent_temperature}°C\n"
        f"☁️ Condition: {description}\n"
        f"💧 Humidity: {humidity}%\n"
        f"💨 Wind speed: {wind_speed} km/h\n"
        f"🌧️ Rain: {rain} mm\n"
        f"🕒 Updated: {time}"
    )


# ============================================================
# MAIN WEATHER TOOL
# ============================================================

def weather(city: str):

    weather_data = get_weather(
        city
    )

    return format_weather_response(
        weather_data
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("INTELLIVOICE AI - LIVE WEATHER TOOL TEST")
    print("=" * 60)

    test_city = "Vijayawada"

    print()
    print(
        f"Testing live weather for: {test_city}"
    )

    print()

    result = weather(
        test_city
    )

    print(result)

    print()
    print("=" * 60)
    print("LIVE WEATHER TEST COMPLETED")
    print("=" * 60)