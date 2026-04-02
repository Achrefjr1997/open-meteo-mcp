# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd open-meteo-mcp
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Test the Server

```bash
# Run the server
python -m src.server
```

The server will start in stdio mode (waiting for input).

### Step 3: Connect Your MCP Client

#### For Cursor:

1. Open Cursor Settings
2. Navigate to Features > MCP Servers
3. Add new server:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "C:/path/to/open-meteo-mcp"
    }
  }
}
```

4. Save and restart Cursor

### Step 4: Try It Out

Ask Cursor:
- "What's the weather in London?"
- "Show me the 7-day forecast for Tokyo"
- "What's the air quality in Paris?"

## Testing Without MCP Client

You can test the API client directly:

```python
import asyncio
from src.client import OpenMeteoClient

async def test():
    async with OpenMeteoClient() as client:
        # Get current weather
        response = await client.get_forecast(
            latitude=52.52,
            longitude=13.41,
            current=["temperature_2m", "weather_code"],
        )
        print(response.data)

asyncio.run(test())
```

## Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Next Steps

1. Read the full [README.md](README.md) for all features
2. Check [Open-Meteo Documentation](https://open-meteo.com/en/docs) for API details
3. Explore available tools with `list_weather_variables()` and `list_weather_models()`

## Troubleshooting

### "Module not found" errors
- Make sure you're in the project directory
- Ensure virtual environment is activated
- Run `pip install -e .`

### Rate limit errors
- Increase `OPEN_METEO_RATE_LIMIT` in environment
- Add caching for repeated requests

### Connection timeout
- Increase `OPEN_METEO_TIMEOUT` in environment
- Check your internet connection
