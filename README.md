# 🌤️ Weather MCP API

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Anthropic-FF6B6B?style=flat)](https://modelcontextprotocol.io/)
[![Open-Meteo](https://img.shields.io/badge/API-Open--Meteo-blue?style=flat)](https://open-meteo.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

A free weather API and web app built with **FastAPI** and **MCP (Model Context Protocol)**. Get real-time weather and 7-day forecasts for any city worldwide — no API key required.

---

## 📸 Screenshots

**Current Weather:**

![Current Weather](screenshot1.png)

**5-Day Forecast:**

![Forecast](screenshot2.png)

---

## 📌 Overview

This project has two layers:

**Layer 1 — MCP Server (`server.py`)**
A Model Context Protocol server that exposes weather tools any AI (like Claude) can call directly. Built using Anthropic's `mcp` Python SDK.

**Layer 2 — FastAPI Web App (`api.py`)**
A full web app with a dark UI and REST API endpoints. Anyone can use it from a browser or call the JSON endpoints directly.

---

## 🤖 What is MCP?

MCP (Model Context Protocol) is an open standard by Anthropic that lets AI models call external tools — your Python functions become tools the AI can use. This project exposes 3 MCP tools:

| Tool | What it does |
|------|-------------|
| `get_current_weather` | Returns temperature, humidity, wind, condition for any city |
| `get_forecast` | Returns day-by-day forecast up to 7 days |
| `list_sample_cities` | Returns a list of supported example cities |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI |
| GET | `/weather/{city}` | Current weather for a city |
| GET | `/forecast/{city}` | 5-day forecast (default) |
| GET | `/forecast/{city}/{days}` | Custom forecast (1–7 days) |
| GET | `/cities` | List of sample cities |
| GET | `/docs` | Interactive Swagger UI |

### Example responses

**`/weather/Mumbai`**
```json
{
  "city": "Mumbai",
  "country": "India",
  "temperature_c": 30.1,
  "humidity_percent": 72,
  "wind_speed_kmh": 8.9,
  "condition": "Partly cloudy",
  "emoji": "⛅",
  "source": "Open-Meteo (open-meteo.com)"
}
```

**`/forecast/Delhi/3`**
```json
{
  "city": "Delhi",
  "country": "India",
  "forecast_days": 3,
  "forecast": [
    { "date": "2026-05-28", "max_temp_c": 42.1, "min_temp_c": 28.3, "rainfall_mm": 0.0, "condition": "Clear sky", "emoji": "☀️" },
    { "date": "2026-05-29", "max_temp_c": 41.5, "min_temp_c": 27.9, "rainfall_mm": 0.0, "condition": "Mainly clear", "emoji": "🌤️" },
    { "date": "2026-05-30", "max_temp_c": 40.2, "min_temp_c": 27.1, "rainfall_mm": 2.1, "condition": "Partly cloudy", "emoji": "⛅" }
  ]
}
```

---

## 📁 Project Structure

```
weather-mcp-server/
├── server.py           ← MCP server (tools for AI agents)
├── api.py              ← FastAPI web app with UI
├── requirements.txt    ← Dependencies
└── README.md           ← You are here
```

---

## 🚀 How to Run Locally

**Step 1 — Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**Step 2 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Run the web app**
```bash
python api.py
```
Open **http://localhost:8000**

**Step 4 — Run the MCP server (for AI agent use)**
```bash
npx @modelcontextprotocol/inspector venv\Scripts\python.exe server.py
```
Open MCP Inspector → Connect → test all 3 tools

---

## 🧪 Corner Cases Handled

| Case | How it's handled |
|------|-----------------|
| Empty city name | Returns 400 with clear error message |
| City not found | Returns 404 with "City not found, check spelling" |
| Invalid days (not 1–7) | Returns 400 with valid range message |
| API timeout | 10 second timeout with connection error |
| Unknown weather code | Falls back to "Unknown (code X)" |

---

## 📦 Dependencies

| Library | Purpose |
|---------|---------|
| `fastapi` | Web framework for REST API and UI |
| `uvicorn` | ASGI server to run FastAPI |
| `httpx` | Async HTTP client for weather API calls |
| `mcp` | Anthropic's MCP SDK for AI tool integration |

---

## 🔭 What to Try Next

- **Deploy to Render** — push to GitHub, connect Render, get a free public URL
- **Add more tools** — air quality index, UV index, sunrise/sunset times
- **Connect to Claude** — configure as an MCP server in Claude Desktop settings
- **Add caching** — cache API responses for 10 minutes to reduce API calls
- **Authentication** — add API keys for rate limiting

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

<div align="center">
Made with ⚡ FastAPI + 🤖 MCP + ☀️ Open-Meteo
</div>
