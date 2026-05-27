# ── Step 3: Imports ────────────────────────────────────────────────────────
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP

# ── Step 4: Create the MCP server instance ────────────────────────────────
mcp = FastMCP("Weather Server")

# ── Step 5: Weather API helper ─────────────────────────────────────────────
async def get_coordinates(city: str) -> dict:
    """
    Convert city name → latitude/longitude using Open-Meteo geocoding API.
    Free, no API key needed.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    if not data.get("results"):
        return None  # city not found

    result = data["results"][0]
    return {
        "lat": result["latitude"],
        "lon": result["longitude"],
        "name": result["name"],
        "country": result.get("country", ""),
    }
# ── Tool 1: Current Weather ────────────────────────────────────────────────
@mcp.tool()
async def get_current_weather(city: str) -> str:
    """
    Get current weather for any city.
    Returns temperature, humidity, wind speed, and weather condition.
    """
    # Corner case: empty input
    if not city.strip():
        return "❌ Please provide a city name."

    coords = await get_coordinates(city)

    # Corner case: city not found
    if not coords:
        return f"❌ City '{city}' not found. Please check the spelling."

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": ["temperature_2m", "relative_humidity_2m",
                    "wind_speed_10m", "weather_code"],
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    current = data["current"]
    weather_desc = get_weather_description(current["weather_code"])

    return (
        f"🌍 Weather in {coords['name']}, {coords['country']}\n"
        f"🌡️  Temperature : {current['temperature_2m']}°C\n"
        f"💧 Humidity    : {current['relative_humidity_2m']}%\n"
        f"💨 Wind Speed  : {current['wind_speed_10m']} km/h\n"
        f"☁️  Condition   : {weather_desc}"
    )


# ── Tool 2: 5-Day Forecast ─────────────────────────────────────────────────
@mcp.tool()
async def get_forecast(city: str, days: int = 5) -> str:
    """
    Get weather forecast for any city.
    days: number of days (1-7), default is 5.
    """
    # Corner cases
    if not city.strip():
        return "❌ Please provide a city name."
    if not 1 <= days <= 7:
        return "❌ Days must be between 1 and 7."

    coords = await get_coordinates(city)
    if not coords:
        return f"❌ City '{city}' not found. Please check the spelling."

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "daily": ["temperature_2m_max", "temperature_2m_min",
                  "precipitation_sum", "weather_code"],
        "forecast_days": days,
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    daily = data["daily"]
    lines = [f"📅 {days}-Day Forecast for {coords['name']}, {coords['country']}\n"]

    for i in range(days):
        desc = get_weather_description(daily["weather_code"][i])
        lines.append(
            f"Day {i+1} ({daily['time'][i]})\n"
            f"   🌡️  High: {daily['temperature_2m_max'][i]}°C  "
            f"Low: {daily['temperature_2m_min'][i]}°C\n"
            f"   🌧️  Rain: {daily['precipitation_sum'][i]}mm\n"
            f"   ☁️  {desc}\n"
        )

    return "\n".join(lines)


# ── Tool 3: List Sample Cities ─────────────────────────────────────────────
@mcp.tool()
async def list_sample_cities() -> str:
    """
    Returns a list of example cities you can use with this weather server.
    """
    cities = [
        "Mumbai", "Delhi", "Bengaluru", "Chennai", "Kolkata",
        "London", "New York", "Tokyo", "Paris", "Sydney",
        "Dubai", "Singapore", "Toronto", "Berlin", "Cairo"
    ]
    return "🌐 Sample cities you can query:\n" + "\n".join(f"  • {c}" for c in cities)
# ── Weather Code → Human readable ─────────────────────────────────────────
def get_weather_description(code: int) -> str:
    """
    Convert Open-Meteo WMO weather codes to readable descriptions.
    Full code list: https://open-meteo.com/en/docs
    """
    codes = {
        0: "☀️ Clear sky",
        1: "🌤️ Mainly clear",
        2: "⛅ Partly cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Foggy",
        48: "🌫️ Icy fog",
        51: "🌦️ Light drizzle",
        53: "🌦️ Moderate drizzle",
        55: "🌧️ Dense drizzle",
        61: "🌧️ Slight rain",
        63: "🌧️ Moderate rain",
        65: "🌧️ Heavy rain",
        71: "🌨️ Slight snow",
        73: "🌨️ Moderate snow",
        75: "❄️ Heavy snow",
        80: "🌦️ Slight showers",
        81: "🌧️ Moderate showers",
        82: "⛈️ Violent showers",
        95: "⛈️ Thunderstorm",
        99: "⛈️ Thunderstorm with hail",
    }
    return codes.get(code, f"🌡️ Unknown condition (code {code})")


# ── Step 8: Run the server ─────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")