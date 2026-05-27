# ── Imports ────────────────────────────────────────────────────────────────
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

# ── App instance ───────────────────────────────────────────────────────────
app = FastAPI(
    title="Weather MCP API",
    description="Free weather API powered by Open-Meteo.",
    version="1.0.0"
)

# ── Weather code decoder ───────────────────────────────────────────────────
def get_weather_description(code: int) -> tuple[str, str]:
    codes = {
        0: ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"), 45: ("Foggy", "🌫️"), 48: ("Icy fog", "🌫️"),
        51: ("Light drizzle", "🌦️"), 53: ("Moderate drizzle", "🌦️"), 55: ("Dense drizzle", "🌧️"),
        61: ("Slight rain", "🌧️"), 63: ("Moderate rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
        71: ("Slight snow", "🌨️"), 73: ("Moderate snow", "🌨️"), 75: ("Heavy snow", "❄️"),
        80: ("Slight showers", "🌦️"), 81: ("Moderate showers", "🌧️"), 82: ("Violent showers", "⛈️"),
        95: ("Thunderstorm", "⛈️"), 99: ("Thunderstorm with hail", "⛈️"),
    }
    result = codes.get(code, (f"Unknown (code {code})", "🌡️"))
    return result

# ── Geocoding helper ───────────────────────────────────────────────────────
async def get_coordinates(city: str) -> dict:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    if not data.get("results"):
        return None
    result = data["results"][0]
    return {
        "lat": result["latitude"],
        "lon": result["longitude"],
        "name": result["name"],
        "country": result.get("country", ""),
    }

# ── Route 1: Home UI ───────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weather MCP API</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); min-height: 100vh; color: #fff; padding: 20px; }
  .container { max-width: 800px; margin: 0 auto; }
  h1 { font-size: 2.2rem; text-align: center; margin: 30px 0 6px; }
  .subtitle { text-align: center; color: #a0aec0; margin-bottom: 30px; font-size: 0.95rem; }
  .search-box { background: rgba(255,255,255,0.07); border-radius: 16px; padding: 24px; margin-bottom: 24px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
  .search-row { display: flex; gap: 10px; flex-wrap: wrap; }
  input, select { flex: 1; min-width: 160px; padding: 12px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); color: #fff; font-size: 1rem; outline: none; }
  input::placeholder { color: #718096; }
  select option { background: #1a1a2e; color: #fff; }
  .btn { padding: 12px 24px; border-radius: 10px; border: none; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.2s; }
  .btn-primary { background: #4299e1; color: #fff; }
  .btn-primary:hover { background: #3182ce; transform: translateY(-1px); }
  .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.2); }
  .btn-secondary:hover { background: rgba(255,255,255,0.2); }
  .quick-cities { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
  .city-chip { padding: 6px 14px; background: rgba(255,255,255,0.08); border-radius: 20px; font-size: 0.85rem; cursor: pointer; border: 1px solid rgba(255,255,255,0.15); transition: all 0.2s; }
  .city-chip:hover { background: rgba(66,153,225,0.3); border-color: #4299e1; }
  .result-card { background: rgba(255,255,255,0.07); border-radius: 16px; padding: 24px; margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.1); display: none; }
  .result-card.show { display: block; }
  .weather-header { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
  .weather-emoji { font-size: 3.5rem; }
  .weather-city { font-size: 1.6rem; font-weight: 700; }
  .weather-country { color: #a0aec0; font-size: 0.9rem; }
  .weather-condition { font-size: 1rem; color: #90cdf4; margin-top: 4px; }
  .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .stat { background: rgba(255,255,255,0.06); border-radius: 12px; padding: 16px; text-align: center; }
  .stat-value { font-size: 1.8rem; font-weight: 700; color: #90cdf4; }
  .stat-label { font-size: 0.75rem; color: #718096; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
  .forecast-grid { display: flex; flex-direction: column; gap: 10px; }
  .forecast-row { display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.05); border-radius: 10px; padding: 12px 16px; }
  .forecast-date { font-size: 0.85rem; color: #a0aec0; width: 100px; }
  .forecast-cond { flex: 1; font-size: 0.9rem; }
  .forecast-temps { font-size: 0.9rem; }
  .temp-high { color: #fc8181; font-weight: 600; }
  .temp-low { color: #90cdf4; }
  .forecast-rain { font-size: 0.8rem; color: #76e4f7; width: 60px; text-align: right; }
  .error-msg { background: rgba(245,101,101,0.15); border: 1px solid rgba(245,101,101,0.3); border-radius: 10px; padding: 14px 18px; color: #fc8181; display: none; margin-top: 12px; }
  .error-msg.show { display: block; }
  .loading { text-align: center; padding: 20px; color: #a0aec0; display: none; }
  .loading.show { display: block; }
  .tabs { display: flex; gap: 8px; margin-bottom: 16px; }
  .tab { padding: 8px 18px; border-radius: 8px; cursor: pointer; font-size: 0.9rem; border: 1px solid rgba(255,255,255,0.15); background: rgba(255,255,255,0.05); transition: all 0.2s; }
  .tab.active { background: #4299e1; border-color: #4299e1; }
  .api-section { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 16px; margin-top: 16px; }
  .api-section h3 { font-size: 0.9rem; color: #a0aec0; margin-bottom: 10px; }
  .endpoint { font-family: monospace; font-size: 0.85rem; color: #90cdf4; padding: 6px 10px; background: rgba(0,0,0,0.2); border-radius: 6px; margin-bottom: 6px; cursor: pointer; }
  .endpoint:hover { color: #fff; }
  .source { text-align: center; color: #4a5568; font-size: 0.75rem; margin-top: 20px; }
</style>
</head>
<body>
<div class="container">
  <h1>🌤️ Weather MCP API</h1>
  <p class="subtitle">Free weather data — no API key needed · Powered by Open-Meteo</p>

  <div class="search-box">
    <div class="tabs">
      <div class="tab active" onclick="switchTab('current')">Current Weather</div>
      <div class="tab" onclick="switchTab('forecast')">Forecast</div>
    </div>

    <div class="search-row">
      <input type="text" id="cityInput" placeholder="Enter city name (e.g. Mumbai, Tokyo...)" onkeydown="if(event.key==='Enter') search()">
      <select id="daysSelect" style="display:none; max-width:130px">
        <option value="3">3 days</option>
        <option value="5" selected>5 days</option>
        <option value="7">7 days</option>
      </select>
      <button class="btn btn-primary" onclick="search()">🔍 Search</button>
    </div>

    <div class="quick-cities">
      <span style="font-size:0.8rem; color:#718096; align-self:center">Quick:</span>
      <div class="city-chip" onclick="quickSearch('Mumbai')">🇮🇳 Mumbai</div>
      <div class="city-chip" onclick="quickSearch('Delhi')">🇮🇳 Delhi</div>
      <div class="city-chip" onclick="quickSearch('Bengaluru')">🇮🇳 Bengaluru</div>
      <div class="city-chip" onclick="quickSearch('London')">🇬🇧 London</div>
      <div class="city-chip" onclick="quickSearch('Tokyo')">🇯🇵 Tokyo</div>
      <div class="city-chip" onclick="quickSearch('New York')">🇺🇸 New York</div>
      <div class="city-chip" onclick="quickSearch('Dubai')">🇦🇪 Dubai</div>
    </div>

    <div class="error-msg" id="errorMsg"></div>
    <div class="loading" id="loading">⏳ Fetching weather data...</div>
  </div>

  <!-- Current Weather Result -->
  <div class="result-card" id="currentCard">
    <div class="weather-header">
      <div class="weather-emoji" id="weatherEmoji">⛅</div>
      <div>
        <div class="weather-city" id="cityName"></div>
        <div class="weather-country" id="countryName"></div>
        <div class="weather-condition" id="conditionText"></div>
      </div>
    </div>
    <div class="stats-grid">
      <div class="stat">
        <div class="stat-value" id="tempVal">--</div>
        <div class="stat-label">Temperature °C</div>
      </div>
      <div class="stat">
        <div class="stat-value" id="humidVal">--</div>
        <div class="stat-label">Humidity %</div>
      </div>
      <div class="stat">
        <div class="stat-value" id="windVal">--</div>
        <div class="stat-label">Wind km/h</div>
      </div>
    </div>
  </div>

  <!-- Forecast Result -->
  <div class="result-card" id="forecastCard">
    <div class="weather-header">
      <div>
        <div class="weather-city" id="fCityName"></div>
        <div class="weather-country" id="fCountryName"></div>
      </div>
    </div>
    <div class="forecast-grid" id="forecastGrid"></div>
  </div>

  <!-- API Endpoints -->
  <div class="api-section">
    <h3>📡 API ENDPOINTS — click to open</h3>
    <div class="endpoint" onclick="window.open('/weather/Mumbai')">GET /weather/{city}</div>
    <div class="endpoint" onclick="window.open('/forecast/Delhi/5')">GET /forecast/{city}/{days}</div>
    <div class="endpoint" onclick="window.open('/cities')">GET /cities</div>
    <div class="endpoint" onclick="window.open('/docs')">GET /docs — Interactive Swagger UI</div>
  </div>

  <p class="source">Data: Open-Meteo.com · Built with FastAPI + MCP</p>
</div>

<script>
  let activeTab = 'current';

  function switchTab(tab) {
    activeTab = tab;
    document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', (i===0&&tab==='current')||(i===1&&tab==='forecast')));
    document.getElementById('daysSelect').style.display = tab === 'forecast' ? 'block' : 'none';
    document.getElementById('currentCard').classList.remove('show');
    document.getElementById('forecastCard').classList.remove('show');
  }

  function quickSearch(city) {
    document.getElementById('cityInput').value = city;
    search();
  }

  async function search() {
    const city = document.getElementById('cityInput').value.trim();
    if (!city) return;

    document.getElementById('errorMsg').classList.remove('show');
    document.getElementById('currentCard').classList.remove('show');
    document.getElementById('forecastCard').classList.remove('show');
    document.getElementById('loading').classList.add('show');

    try {
      if (activeTab === 'current') {
        const res = await fetch(`/weather/${encodeURIComponent(city)}`);
        if (!res.ok) { const e = await res.json(); throw new Error(e.detail); }
        const d = await res.json();
        document.getElementById('weatherEmoji').textContent = getEmoji(d.condition);
        document.getElementById('cityName').textContent = d.city;
        document.getElementById('countryName').textContent = d.country;
        document.getElementById('conditionText').textContent = d.condition;
        document.getElementById('tempVal').textContent = d.temperature_c + '°';
        document.getElementById('humidVal').textContent = d.humidity_percent + '%';
        document.getElementById('windVal').textContent = d.wind_speed_kmh;
        document.getElementById('currentCard').classList.add('show');
      } else {
        const days = document.getElementById('daysSelect').value;
        const res = await fetch(`/forecast/${encodeURIComponent(city)}/${days}`);
        if (!res.ok) { const e = await res.json(); throw new Error(e.detail); }
        const d = await res.json();
        document.getElementById('fCityName').textContent = `📅 ${d.forecast_days}-Day Forecast — ${d.city}`;
        document.getElementById('fCountryName').textContent = d.country;
        document.getElementById('forecastGrid').innerHTML = d.forecast.map(f => `
          <div class="forecast-row">
            <div class="forecast-date">${f.date}</div>
            <div class="forecast-cond">${getEmoji(f.condition)} ${f.condition}</div>
            <div class="forecast-temps"><span class="temp-high">${f.max_temp_c}°</span> / <span class="temp-low">${f.min_temp_c}°</span></div>
            <div class="forecast-rain">🌧 ${f.rainfall_mm}mm</div>
          </div>`).join('');
        document.getElementById('forecastCard').classList.add('show');
      }
    } catch(e) {
      document.getElementById('errorMsg').textContent = '❌ ' + e.message;
      document.getElementById('errorMsg').classList.add('show');
    } finally {
      document.getElementById('loading').classList.remove('show');
    }
  }

  function getEmoji(condition) {
    const map = {'Clear sky':'☀️','Mainly clear':'🌤️','Partly cloudy':'⛅','Overcast':'☁️','Foggy':'🌫️','Icy fog':'🌫️','Light drizzle':'🌦️','Moderate drizzle':'🌦️','Dense drizzle':'🌧️','Slight rain':'🌧️','Moderate rain':'🌧️','Heavy rain':'🌧️','Slight snow':'🌨️','Moderate snow':'🌨️','Heavy snow':'❄️','Slight showers':'🌦️','Moderate showers':'🌧️','Violent showers':'⛈️','Thunderstorm':'⛈️','Thunderstorm with hail':'⛈️'};
    return map[condition] || '🌡️';
  }
</script>
</body>
</html>"""

# ── Route 2: Current Weather JSON ─────────────────────────────────────────
@app.get("/weather/{city}")
async def current_weather(city: str):
    if not city.strip():
        raise HTTPException(status_code=400, detail="City name cannot be empty")
    coords = await get_coordinates(city)
    if not coords:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found. Check spelling.")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"], "longitude": coords["lon"],
        "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "weather_code"],
        "timezone": "auto",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    current = data["current"]
    desc, emoji = get_weather_description(current["weather_code"])
    return {
        "city": coords["name"], "country": coords["country"],
        "temperature_c": current["temperature_2m"],
        "humidity_percent": current["relative_humidity_2m"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "condition": desc, "emoji": emoji,
        "source": "Open-Meteo (open-meteo.com)"
    }

# ── Route 3: Forecast JSON ─────────────────────────────────────────────────
@app.get("/forecast/{city}")
@app.get("/forecast/{city}/{days}")
async def forecast(city: str, days: int = 5):
    if not city.strip():
        raise HTTPException(status_code=400, detail="City name cannot be empty")
    if not 1 <= days <= 7:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 7")
    coords = await get_coordinates(city)
    if not coords:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found. Check spelling.")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"], "longitude": coords["lon"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "weather_code"],
        "forecast_days": days, "timezone": "auto",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    daily = data["daily"]
    forecast_list = []
    for i in range(days):
        desc, emoji = get_weather_description(daily["weather_code"][i])
        forecast_list.append({
            "date": daily["time"][i],
            "max_temp_c": daily["temperature_2m_max"][i],
            "min_temp_c": daily["temperature_2m_min"][i],
            "rainfall_mm": daily["precipitation_sum"][i],
            "condition": desc, "emoji": emoji,
        })
    return {"city": coords["name"], "country": coords["country"], "forecast_days": days, "forecast": forecast_list, "source": "Open-Meteo (open-meteo.com)"}

# ── Route 4: Sample Cities ─────────────────────────────────────────────────
@app.get("/cities")
async def sample_cities():
    return {"sample_cities": ["Mumbai","Delhi","Bengaluru","Chennai","Kolkata","London","New York","Tokyo","Paris","Sydney","Dubai","Singapore","Toronto","Berlin","Cairo"]}

# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
