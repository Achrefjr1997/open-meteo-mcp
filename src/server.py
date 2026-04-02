"""
Open-Meteo MCP Server - Main Entry Point.

This module creates and configures the MCP server, registering all tools,
resources, and prompts for the Open-Meteo weather API.
"""

import os
from mcp.server.fastmcp import FastMCP

from .client import OpenMeteoClient, ClientConfig
from .tools import forecast, historical, air_quality, geocoding, ensemble, marine, specialized
from .resources import variables as variables_resources, models as models_resources
from .prompts import weather_assistant


# ==================== Server Configuration ====================

SERVER_NAME = "open-meteo-mcp"
SERVER_VERSION = "0.1.0"
SERVER_DESCRIPTION = """
MCP Server for Open-Meteo Weather API - Full API capability exposure.

Provides comprehensive weather data access including:
- Current weather and forecasts (up to 16 days)
- Historical weather (1940-present)
- Air quality (PM, gases, AQI, pollen)
- Ensemble forecasts and model comparisons
- Marine weather and wave forecasts
- Climate data and analysis
- Geocoding and location services

All Open-Meteo API endpoints and variables are exposed as tools and resources.
"""


def create_client_from_env() -> OpenMeteoClient:
    """Create Open-Meteo client from environment variables."""
    config = ClientConfig(
        api_key=os.environ.get("OPEN_METEO_API_KEY"),
        timeout=float(os.environ.get("OPEN_METEO_TIMEOUT", "30.0")),
        default_timezone=os.environ.get("OPEN_METEO_TIMEZONE", "GMT"),
        rate_limit_delay=float(os.environ.get("OPEN_METEO_RATE_LIMIT", "0.1")),
    )
    return OpenMeteoClient(config)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP(
        name=SERVER_NAME,
        instructions=SERVER_DESCRIPTION,
    )
    return mcp


def register_all_tools(mcp: FastMCP, client: OpenMeteoClient) -> None:
    """Register all tool modules with the MCP server."""
    forecast.register_forecast_tools(mcp, client)
    historical.register_historical_tools(mcp, client)
    air_quality.register_air_quality_tools(mcp, client)
    geocoding.register_geocoding_tools(mcp, client)
    ensemble.register_ensemble_tools(mcp, client)
    marine.register_marine_tools(mcp, client)
    specialized.register_specialized_tools(mcp, client)


def register_all_resources(mcp: FastMCP) -> None:
    """Register all resource modules with the MCP server."""
    variables_resources.register_variable_resources(mcp)
    models_resources.register_model_resources(mcp)


def register_all_prompts(mcp: FastMCP) -> None:
    """Register all prompt modules with the MCP server."""
    weather_assistant.register_prompts(mcp)


def create_app() -> FastMCP:
    """Create the complete MCP application."""
    # Create server
    mcp = create_mcp_server()

    # Create client
    client = create_client_from_env()

    # Register all components
    register_all_tools(mcp, client)
    register_all_resources(mcp)
    register_all_prompts(mcp)

    return mcp


# ==================== Main Entry Point ====================


def main() -> None:
    """Main entry point for the MCP server."""
    mcp = create_app()
    mcp.run()


def run_stdio() -> None:
    """Run the server with stdio transport."""
    mcp = create_app()
    mcp.run(transport="stdio")


def run_sse(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the server with SSE transport for remote access using uvicorn."""
    import uvicorn

    mcp = create_app()
    # Get the SSE Starlette app from FastMCP
    app = mcp.sse_app()
    uvicorn.run(app, host=host, port=port, log_level="info")


# ==================== CLI Helper ====================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Open-Meteo MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  OPEN_METEO_API_KEY      API key for commercial use (optional)
  OPEN_METEO_TIMEOUT      Request timeout in seconds (default: 30)
  OPEN_METEO_TIMEZONE     Default timezone (default: GMT)
  OPEN_METEO_RATE_LIMIT   Rate limit delay in seconds (default: 0.1)

Examples:
  # Run with stdio transport (for local MCP clients)
  python -m src.server
  
  # Run with SSE transport (for remote access)
  python -m src.server --transport sse --port 8000
  
  # Set API key for commercial use
  export OPEN_METEO_API_KEY=your_api_key
  python -m src.server
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )

    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for SSE transport (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port", type=int, default=8000, help="Port for SSE transport (default: 8000)"
    )

    args = parser.parse_args()

    if args.transport == "stdio":
        run_stdio()
    else:
        run_sse(args.host, args.port)
