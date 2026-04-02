# Open-Meteo MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-purple.svg)](https://opensource.org/licenses/AGPL-3.0)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](DOCKER.md)

A comprehensive Model Context Protocol (MCP) server for the [Open-Meteo](https://open-meteo.com/) weather API, exposing the full API capability as tools, resources, and prompts for AI assistants.

![Features](https://img.shields.io/badge/Tools-33-green)
![Features](https://img.shields.io/badge/Resources-25-blue)
![Features](https://img.shields.io/badge/Prompts-4-orange)
![Features](https://img.shields.io/badge/Weather%20Models-30+-red)

---

## 🌟 Features

### 🌤️ Complete Weather Data Access

| Category | Coverage | Variables |
|----------|----------|-----------|
| **Current Weather** | Real-time, 15-min resolution | 50+ |
| **Hourly Forecasts** | Up to 16 days | 200+ |
| **Daily Forecasts** | Aggregated values | 100+ |
| **Historical Weather** | 1940-present (ERA5, ECMWF) | 150+ |
| **Air Quality** | PM2.5, PM10, gases, AQI, pollen | 30+ |
| **Marine Weather** | Waves, swells, water temp | 20+ |
| **Climate Data** | Long-term patterns, normals | 50+ |

### 🎯 Weather Model Coverage

| Provider | Models | Resolution | Coverage |
|----------|--------|------------|----------|
| **ECMWF** | IFS High Resolution, Ensemble | 9km | Global |
| **NOAA** | GFS, HRRR, Ensemble | 3-25km | North America |
| **DWD** | ICON Global/EU/D2 | 2-13km | Europe/Global |
| **Météo-France** | ARPEGE, AROME | 1.3-10km | France/Europe |
| **UK Met Office** | UKMO Global/UK | 2-10km | UK/Global |
| **Met Norway** | Nordic, Global | 2.5-10km | Nordic/Global |
| **ECCC (Canada)** | GEM Global/Regional | 10-25km | North America |
| **JMA (Japan)** | MSM, GSM | 5-20km | Japan/Asia |

### 🛠️ MCP Components

#### **33 Tools** - Full API Access
- **Forecast**: `get_current_weather`, `get_hourly_forecast`, `get_daily_forecast`, `get_15min_forecast`, `get_complete_forecast`
- **Historical**: `get_historical_hourly`, `get_historical_daily`, temperature/precipitation/wind analysis
- **Air Quality**: `get_current_air_quality`, `get_air_quality_index`, `get_pollen_forecast`, `get_uv_index_forecast`
- **Geocoding**: `search_location`, `get_location_by_id`, `resolve_coordinates`, `get_nearby_cities`
- **Ensemble**: `get_ensemble_forecast`, `compare_weather_models`, model-specific tools
- **Marine**: `get_marine_forecast`, `get_elevation`, `get_climate_data`
- **Utility**: `list_weather_variables`, `list_weather_models`, `get_weather_summary`

#### **25 Resources** - Reference Data
- **Variables**: `weather://variables/{all,temperature,wind,precipitation,clouds,pressure,humidity,solar,soil,air_quality,marine,weather_codes,usage-guide}`
- **Models**: `weather://models/{all,ecmwf,noaa,dwd,meteo_france,ukmo,met_norway,eccc,jma,ensemble,comparison,usage-guide}`

#### **4 Prompts** - AI Assistant Guidance
- `weather_analysis_prompt` - General weather assistance best practices
- `marine_weather_prompt` - Marine and coastal weather specialization
- `climate_analysis_prompt` - Climate data analysis guidance
- `air_quality_health_prompt` - Air quality and health recommendations

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Docker (optional, for containerized deployment)

### Option 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/open-meteo-mcp.git
cd open-meteo-mcp

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Option 2: Install with Development Dependencies

```bash
pip install -e ".[dev]"
```

### Option 3: Docker (Production Ready)

```bash
# Build the Docker image
docker build -t open-meteo-mcp .

# Run with Docker Compose (stdio transport)
docker compose up open-meteo-mcp

# Run with SSE transport (HTTP access on port 8000)
docker compose up open-meteo-sse

# Run test suite
docker compose --profile test up open-meteo-test
```

> 📘 **Docker Documentation**: See [DOCKER.md](DOCKER.md) for complete Docker setup, including Kubernetes deployment, resource limits, and production best practices.

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPEN_METEO_API_KEY` | API key for commercial use (>10k calls/day) | None | ❌ |
| `OPEN_METEO_TIMEOUT` | Request timeout in seconds | 30.0 | ❌ |
| `OPEN_METEO_TIMEZONE` | Default timezone (e.g., `Africa/Tunis`, `Europe/Paris`) | GMT | ❌ |
| `OPEN_METEO_RATE_LIMIT` | Rate limit delay in seconds | 0.1 | ❌ |

### Configuration Examples

**Linux/Mac:**
```bash
export OPEN_METEO_API_KEY=your_api_key
export OPEN_METEO_TIMEOUT=60.0
export OPEN_METEO_TIMEZONE=Africa/Tunis
```

**Windows (PowerShell):**
```powershell
$env:OPEN_METEO_API_KEY="your_api_key"
$env:OPEN_METEO_TIMEOUT="60.0"
$env:OPEN_METEO_TIMEZONE="Africa/Tunis"
```

**Docker (.env file):**
```bash
OPEN_METEO_API_KEY=your_api_key
OPEN_METEO_TIMEOUT=60.0
OPEN_METEO_TIMEZONE=Africa/Tunis
```

### Common Timezones

| Region | Timezone |
|--------|----------|
| Tunisia | `Africa/Tunis` |
| France | `Europe/Paris` |
| Germany | `Europe/Berlin` |
| UK | `Europe/London` |
| US Eastern | `America/New_York` |
| US Pacific | `America/Los_Angeles` |
| Japan | `Asia/Tokyo` |
| Australia (Sydney) | `Australia/Sydney` |

---

## 🚀 Usage

### Running the Server

#### Stdio Transport (Local MCP Clients)

```bash
# Run directly
python -m src.server

# Or use the installed command
open-meteo-mcp
```

#### SSE Transport (Remote HTTP Access)

```bash
# Run with SSE for remote access
python -m src.server --transport sse --port 8000

# With custom host
python -m src.server --transport sse --host 0.0.0.0 --port 8080
```

### MCP Client Configuration

#### Cursor IDE

Add to `.cursor/settings.json`:

```json
{
  "mcpServers": {
    "open-meteo": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/open-meteo-mcp",
      "description": "Weather data from Open-Meteo API"
    }
  }
}
```

#### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "open-meteo": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/open-meteo-mcp"
    }
  }
}
```

#### Docker with MCP Client

```json
{
  "mcpServers": {
    "open-meteo": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "OPEN_METEO_API_KEY=your_key", "open-meteo-mcp"],
      "description": "Weather data via Docker"
    }
  }
}
```

### Example Queries

Once connected, you can ask the AI assistant:

```
What's the current weather in London?

Show me the 7-day forecast for Tokyo with temperature and precipitation.

What was the weather like in Paris during January 2024?

Compare the ECMWF and GFS models for New York this week.

What's the air quality index in Beijing right now? Is it safe for outdoor exercise?

Find coordinates for Barcelona, Spain and get the marine forecast for sailing.

What's the elevation of Denver, Colorado?

List all available weather variables for solar energy applications.

I have allergies - what's the pollen forecast for Berlin this week?

Plan my outdoor wedding in Amsterdam on Saturday - give me hour-by-hour weather from 2 PM to 10 PM.
```

---

## 📚 Available Tools

### Forecast Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_current_weather` | Current weather conditions | lat, lon, variables, units |
| `get_hourly_forecast` | Hourly forecast (up to 16 days) | lat, lon, variables, forecast_days |
| `get_daily_forecast` | Daily forecast summary | lat, lon, variables, forecast_days |
| `get_15min_forecast` | 15-minute interval forecast (EU/NA) | lat, lon, variables, forecast_days |
| `get_complete_forecast` | Current + hourly + daily combined | lat, lon, forecast_days |

### Historical Tools

| Tool | Description | Date Range |
|------|-------------|------------|
| `get_historical_hourly` | Historical hourly data | 1940-present |
| `get_historical_daily` | Historical daily aggregates | 1940-present |
| `get_historical_temperature_extremes` | Temperature max/min analysis | 1940-present |
| `get_historical_precipitation_analysis` | Precipitation statistics | 1940-present |
| `get_historical_wind_analysis` | Wind speed/direction analysis | 1940-present |

### Air Quality Tools

| Tool | Description | Coverage |
|------|-------------|----------|
| `get_current_air_quality` | PM2.5, PM10, gases | Global |
| `get_hourly_air_quality` | Hourly air quality forecast | Global |
| `get_air_quality_index` | AQI with health recommendations | Global |
| `get_pollen_forecast` | Pollen forecast (alder, birch, grass, etc.) | Europe |
| `get_uv_index_forecast` | UV index with safety guidance | Global |

### Geocoding Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `search_location` | Search locations by name | City lookup |
| `get_location_by_id` | Get location details by ID | Cached lookups |
| `resolve_coordinates` | Convert place name to coordinates | Natural language |
| `get_nearby_cities` | Find nearby cities | Regional queries |

### Ensemble & Model-Specific Tools

| Tool | Description | Models |
|------|-------------|--------|
| `get_ensemble_forecast` | Multi-model ensemble | All |
| `compare_weather_models` | Compare model forecasts | ECMWF, GFS, ICON |
| `get_ecmwf_forecast` | ECMWF IFS forecast | ECMWF |
| `get_gfs_forecast` | NOAA GFS forecast | NOAA |
| `get_icon_forecast` | DWD ICON forecast | DWD |
| `get_metno_forecast` | Met Norway forecast | Met Norway |
| `get_meteo_france_forecast` | Météo-France forecast | Météo-France |

### Marine & Specialized Tools

| Tool | Description | Variables |
|------|-------------|-----------|
| `get_marine_forecast` | Marine weather and waves | wave_height, period, direction |
| `get_elevation` | Elevation data | elevation |
| `get_climate_data` | Long-term climate normals | temperature, precipitation |
| `get_weather_code_explanation` | WMO weather codes | 0-99 codes |
| `list_weather_variables` | All available variables | 200+ |
| `list_weather_models` | All available models | 30+ |
| `get_weather_summary` | Quick weather summary | All |

---

## 📖 Available Resources

Access reference data via URIs in MCP clients:

### Variable Resources

| URI | Description |
|-----|-------------|
| `weather://variables/all` | All 200+ weather variables |
| `weather://variables/temperature` | Temperature-related variables |
| `weather://variables/wind` | Wind speed, direction, gusts |
| `weather://variables/precipitation` | Rain, snow, precipitation |
| `weather://variables/clouds` | Cloud cover and types |
| `weather://variables/pressure` | Atmospheric pressure |
| `weather://variables/humidity` | Humidity and moisture |
| `weather://variables/solar` | Solar radiation and UV |
| `weather://variables/soil` | Soil temperature and moisture |
| `weather://variables/air_quality` | Air quality and pollutants |
| `weather://variables/marine` | Marine and wave conditions |
| `weather://variables/weather_codes` | WMO weather codes (0-99) |
| `weather://variables/usage-guide` | Best practices and examples |

### Model Resources

| URI | Description |
|-----|-------------|
| `weather://models/all` | All 30+ weather models |
| `weather://models/ecmwf` | ECMWF (European Centre) models |
| `weather://models/noaa` | NOAA (US) models |
| `weather://models/dwd` | DWD (German) models |
| `weather://models/meteo_france` | Météo-France models |
| `weather://models/ukmo` | UK Met Office models |
| `weather://models/met_norway` | Met Norway models |
| `weather://models/eccc` | Environment Canada models |
| `weather://models/jma` | JMA (Japan) models |
| `weather://models/ensemble` | Ensemble forecast models |
| `weather://models/comparison` | Model comparison guide |
| `weather://models/usage-guide` | Model selection guide |

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_client.py -v

# Run tests in Docker
docker compose --profile test up open-meteo-test
```

### Test Results

```
============================= test session starts =============================
collected 118 items

tests/test_client.py ...................ss...ss........                 [ 28%]
tests/test_prompts/test_prompts.py .............                         [ 39%]
tests/test_resources/test_resources.py ...................               [ 55%]
tests/test_server.py .......................                             [ 75%]
tests/test_tools/test_tools.py ............ssss...ssss......             [100%]

====================== 106 passed, 12 skipped in 39.50s ======================
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# All quality checks
black --check src/ tests/ && ruff check src/ tests/ && mypy src/
```

---

## 🏗️ Project Structure

```
open-meteo-mcp/
├── src/
│   ├── __init__.py              # Package metadata
│   ├── server.py                # Main MCP server entry point
│   ├── client.py                # Open-Meteo API client (async)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── forecast.py          # 5 forecast tools
│   │   ├── historical.py        # 5 historical tools
│   │   ├── air_quality.py       # 5 air quality tools
│   │   ├── geocoding.py         # 5 geocoding tools
│   │   ├── ensemble.py          # 7 ensemble/model tools
│   │   ├── marine.py            # 3 marine tools
│   │   └── specialized.py       # 3 utility tools
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── variables.py         # 13 variable resources
│   │   └── models.py            # 12 model resources
│   └── prompts/
│       ├── __init__.py
│       └── weather_assistant.py # 4 prompts
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_client.py           # API client tests (38 tests)
│   ├── test_server.py           # Server tests (23 tests)
│   ├── test_tools/
│   │   ├── __init__.py
│   │   └── test_tools.py        # Tool tests (28 tests)
│   ├── test_resources/
│   │   ├── __init__.py
│   │   └── test_resources.py    # Resource tests (19 tests)
│   └── test_prompts/
│       ├── __init__.py
│       └── test_prompts.py      # Prompt tests (13 tests)
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Multi-stage build
├── DOCKER.md                    # Docker documentation
├── pyproject.toml               # Project configuration
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── QUICKSTART.md                # 5-minute setup guide
└── TEST_PROMPTS.md              # Comprehensive test prompts
```

---

## 📊 API Rate Limits & Pricing

Open-Meteo is **free for non-commercial use**:

| Usage Tier | API Key | Rate Limit | Cost |
|------------|---------|------------|------|
| **Non-Commercial** | Not required | Fair use | Free |
| **Commercial (<10k/day)** | Not required | Fair use | Free |
| **Commercial (>10k/day)** | Required | As agreed | Paid |

### Best Practices

- ✅ Implement rate limiting (default: 0.1s delay)
- ✅ Cache responses when possible
- ✅ Use specific variables (don't request unnecessary data)
- ✅ Attribute Open-Meteo: "Weather data provided by Open-Meteo.com"

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Test** your changes (`pytest tests/ -v`)
5. **Lint** your code (`black . && ruff check .`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/open-meteo-mcp.git
cd open-meteo-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests to verify setup
pytest tests/ -v
```

---

## 📄 License

- **Code**: [AGPL-3.0 License](LICENSE)
- **Weather Data**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

**Attribution Requirement:**
When using weather data in publications or products, please attribute Open-Meteo:

```
Weather data provided by Open-Meteo.com
```

---

## 🆘 Support

| Resource | Link |
|----------|------|
| **Open-Meteo API Docs** | https://open-meteo.com/en/docs |
| **Open-Meteo GitHub** | https://github.com/open-meteo/open-meteo |
| **MCP Specification** | https://modelcontextprotocol.io/ |
| **This Project Issues** | [GitHub Issues](https://github.com/yourusername/open-meteo-mcp/issues) |

---

## 🙏 Acknowledgments

- **[Open-Meteo](https://open-meteo.com/)** - Providing free and open weather APIs
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - MCP specification
- **Weather Data Providers**: ECMWF, NOAA, DWD, Météo-France, Met Norway, UK Met Office, ECCC, JMA, and others
- **Community Contributors** - All who have contributed to this project

---

## 📈 Roadmap

- [ ] Add flood API support
- [ ] Add solar radiation API support
- [ ] Implement response caching
- [ ] Add WebSocket transport support
- [ ] Create official Python SDK
- [ ] Add more language localizations

---

**Built with ❤️ for weather enthusiasts and AI developers**

*Last updated: April 2026*
