"""Interactive demo for Open-Meteo MCP Server."""
import asyncio
from src.client import OpenMeteoClient
from mcp.server.fastmcp import FastMCP
from src.tools.forecast import register_forecast_tools
from src.tools.geocoding import register_geocoding_tools
from src.tools.specialized import register_specialized_tools


async def demo():
    """Run interactive demo."""
    print("=" * 60)
    print("🌤️  Open-Meteo MCP Server - Interactive Demo")
    print("=" * 60)
    
    # Create client and server
    client = OpenMeteoClient()
    mcp = FastMCP("demo")
    
    # Register some tools
    register_forecast_tools(mcp, client)
    register_geocoding_tools(mcp, client)
    register_specialized_tools(mcp, client)
    
    print("\n✅ Server initialized with tools:\n")
    
    # List available tools
    tools = list(mcp._tool_manager._tools.keys())
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool}")
    
    print("\n" + "=" * 60)
    print("🧪 Running tool demonstrations...\n")
    
    # Demo 1: Get weather summary
    print("📍 Demo 1: Weather Summary for London")
    print("-" * 40)
    try:
        geo_tool = mcp._tool_manager.get_tool("resolve_coordinates")
        result = await geo_tool.fn(location_name="London", country_code="GB")
        print(f"   Location: {result.get('matched_name')}, {result.get('country')}")
        print(f"   Coordinates: ({result.get('latitude')}, {result.get('longitude')})")
        
        weather_tool = mcp._tool_manager.get_tool("get_current_weather")
        result = await weather_tool.fn(
            latitude=result.get('latitude'),
            longitude=result.get('longitude'),
        )
        current = result.get('current', {})
        print(f"   Temperature: {current.get('temperature_2m')}°C")
        print(f"   Weather: {current.get('weather_code')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n📍 Demo 2: List Weather Variables")
    print("-" * 40)
    try:
        var_tool = mcp._tool_manager.get_tool("list_weather_variables")
        result = await var_tool.fn()
        print(f"   Total Variables: {result.get('total_variables')}")
        print(f"   Categories: {', '.join(result.get('categories', [])[:5])}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n📍 Demo 3: List Weather Models")
    print("-" * 40)
    try:
        model_tool = mcp._tool_manager.get_tool("list_weather_models")
        result = await model_tool.fn()
        print(f"   Total Models: {result.get('total_models')}")
        print(f"   Providers: {', '.join(result.get('providers', [])[:5])}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n📍 Demo 4: 7-Day Forecast for Tokyo")
    print("-" * 40)
    try:
        forecast_tool = mcp._tool_manager.get_tool("get_daily_forecast")
        result = await forecast_tool.fn(
            latitude=35.6762,
            longitude=139.6503,
            forecast_days=7,
        )
        daily = result.get('daily', {})
        time = daily.get('time', [])
        temp_max = daily.get('temperature_2m_max', [])
        temp_min = daily.get('temperature_2m_min', [])
        
        print("   Date        | Max °C | Min °C")
        print("   " + "-" * 30)
        for i in range(min(7, len(time))):
            date = time[i][:10] if i < len(time) else "N/A"
            max_t = temp_max[i] if i < len(temp_max) else "N/A"
            min_t = temp_min[i] if i < len(temp_min) else "N/A"
            print(f"   {date} | {max_t:6} | {min_t:6}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("✨ Demo complete!\n")
    print("💡 To use this server with an MCP client:")
    print("   1. Add to your MCP client configuration:")
    print('      {')
    print('        "mcpServers": {')
    print('          "open-meteo": {')
    print('            "command": "python",')
    print('            "args": ["-m", "src.server"],')
    print('            "cwd": "path/to/open-meteo-mcp"')
    print('          }')
    print('        }')
    print('      }')
    print("\n   2. Restart your MCP client (Cursor, Claude Desktop, etc.)")
    print("   3. Ask: 'What's the weather in London?'\n")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(demo())
