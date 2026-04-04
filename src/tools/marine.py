"""
Marine and Specialized Tools for Open-Meteo MCP Server.

Provides tools for marine weather, elevation data, and other specialized APIs.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import OpenMeteoClient


def register_marine_tools(mcp: FastMCP, client: OpenMeteoClient) -> None:
    """Register all marine and specialized tools with the MCP server."""

    @mcp.tool()
    async def get_marine_forecast(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 7,
        timezone: str = "GMT",
    ) -> dict[str, Any]:
        """
        Get marine weather forecast for ocean/coastal locations.

        Provides wave, wind, and weather data for marine activities.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Marine weather variables. Options include:
                Waves:
                    - wave_height: Significant wave height
                    - wave_direction: Wave direction
                    - wave_period: Wave period
                    - wave_peak_period: Peak wave period
                    - wind_wave_height: Wind wave height
                    - wind_wave_period: Wind wave period
                    - wind_wave_direction: Wind wave direction
                    - swell_height: Swell height
                    - swell_period: Swell period
                    - swell_direction: Swell direction
                Wind:
                    - wind_speed_10m, wind_direction_10m
                Weather:
                    - temperature_2m, weather_code, cloud_cover
                If None, returns common marine variables.
            forecast_days: Number of forecast days (1-16)
            timezone: Timezone for the response

        Returns:
            Marine forecast data with wave and weather conditions
        """
        if variables is None:
            variables = [
                "wave_height",
                "wave_direction",
                "wave_period",
                "wave_peak_period",
                "wind_wave_height",
                "wind_wave_period",
                "wind_wave_direction",
                "swell_wave_height",
                "swell_wave_period",
                "swell_wave_direction",
                "wind_speed_10m",
                "wind_direction_10m",
            ]

        response = await client.get_marine(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
            forecast_days=forecast_days,
            timezone=timezone,
        )

        if not response.success:
            return {"error": response.error_message}

        data = response.data
        return {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timezone"),
            },
            "hourly": data.get("hourly", {}),
            "forecast_days": forecast_days,
            "marine_conditions_summary": _summarize_marine_conditions(data.get("hourly", {})),
        }

    @mcp.tool()
    async def get_elevation(
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        """
        Get elevation data for coordinates.

        Uses 90m digital elevation model (DEM) for accurate elevation data.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)

        Returns:
            Elevation in meters above sea level
        """
        response = await client.get_elevation(
            latitude=latitude,
            longitude=longitude,
        )

        if not response.success:
            return {"error": response.error_message}

        data = response.data
        # Elevation API returns a list, extract first element
        elevation_data = data.get("elevation", [])
        elevation = elevation_data[0] if isinstance(elevation_data, list) and len(elevation_data) > 0 else elevation_data

        return {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "elevation": elevation,
            "unit": "meters",
            "elevation_ft": round(elevation * 3.28084, 1),
            "terrain_category": _get_terrain_category(elevation),
        }

    @mcp.tool()
    async def get_climate_data(
        latitude: float,
        longitude: float,
        year: int = 2025,
        variables: list[str] | None = None,
        timezone: str = "GMT",
    ) -> dict[str, Any]:
        """
        Get historical climate data for a specific year.

        Retrieves daily weather data for climate analysis.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            year: Year to retrieve data for (default: 2025)
            variables: Climate variables. Options include:
                temperature_2m_mean: Daily mean temperature
                temperature_2m_max: Daily maximum temperature
                temperature_2m_min: Daily minimum temperature
                precipitation_sum: Daily precipitation sum
                sunshine_duration: Daily sunshine duration
                et0_fao_evapotranspiration: Daily evapotranspiration
            timezone: Timezone for the response

        Returns:
            Daily climate data for the specified year
        """
        if variables is None:
            variables = [
                "temperature_2m_mean",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
            ]

        response = await client.get_climate(
            latitude=latitude,
            longitude=longitude,
            start_date=f"{year}-01-01",
            end_date=f"{year}-12-31",
            daily=variables,
            timezone=timezone,
        )

        if not response.success:
            return {"error": response.error_message}

        data = response.data
        return {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            },
            "year": year,
            "daily": data.get("daily", {}),
        }

    @mcp.tool()
    async def get_weather_code_explanation(
        weather_code: int,
    ) -> dict[str, str]:
        """
        Get human-readable explanation of WMO weather codes.

        Weather codes (0-99) describe weather conditions.

        Args:
            weather_code: WMO weather code (0-99)

        Returns:
            Weather condition description and icon suggestion
        """
        weather_codes = {
            0: {"description": "Clear sky", "icon": "☀️", "category": "Clear"},
            1: {"description": "Mainly clear", "icon": "🌤️", "category": "Partly Cloudy"},
            2: {"description": "Partly cloudy", "icon": "⛅", "category": "Partly Cloudy"},
            3: {"description": "Overcast", "icon": "☁️", "category": "Cloudy"},
            45: {"description": "Fog", "icon": "🌫️", "category": "Foggy"},
            48: {"description": "Depositing rime fog", "icon": "🌫️", "category": "Foggy"},
            51: {"description": "Light drizzle", "icon": "🌦️", "category": "Drizzle"},
            53: {"description": "Moderate drizzle", "icon": "🌦️", "category": "Drizzle"},
            55: {"description": "Dense drizzle", "icon": "🌧️", "category": "Drizzle"},
            56: {"description": "Light freezing drizzle", "icon": "🌨️", "category": "Freezing"},
            57: {"description": "Dense freezing drizzle", "icon": "🌨️", "category": "Freezing"},
            61: {"description": "Slight rain", "icon": "🌧️", "category": "Rain"},
            63: {"description": "Moderate rain", "icon": "🌧️", "category": "Rain"},
            65: {"description": "Heavy rain", "icon": "⛈️", "category": "Rain"},
            66: {"description": "Light freezing rain", "icon": "🌨️", "category": "Freezing"},
            67: {"description": "Heavy freezing rain", "icon": "🌨️", "category": "Freezing"},
            71: {"description": "Slight snow fall", "icon": "🌨️", "category": "Snow"},
            73: {"description": "Moderate snow fall", "icon": "🌨️", "category": "Snow"},
            75: {"description": "Heavy snow fall", "icon": "❄️", "category": "Snow"},
            77: {"description": "Snow grains", "icon": "🌨️", "category": "Snow"},
            80: {"description": "Slight rain showers", "icon": "🌦️", "category": "Showers"},
            81: {"description": "Moderate rain showers", "icon": "🌧️", "category": "Showers"},
            82: {"description": "Violent rain showers", "icon": "⛈️", "category": "Showers"},
            85: {"description": "Slight snow showers", "icon": "🌨️", "category": "Snow Showers"},
            86: {"description": "Heavy snow showers", "icon": "❄️", "category": "Snow Showers"},
            95: {"description": "Thunderstorm", "icon": "⚡", "category": "Thunderstorm"},
            96: {
                "description": "Thunderstorm with slight hail",
                "icon": "⛈️",
                "category": "Thunderstorm",
            },
            99: {
                "description": "Thunderstorm with heavy hail",
                "icon": "⛈️",
                "category": "Thunderstorm",
            },
        }

        code_info = weather_codes.get(
            weather_code,
            {
                "description": "Unknown weather code",
                "icon": "❓",
                "category": "Unknown",
            },
        )

        return {
            "weather_code": weather_code,
            **code_info,
        }


# ==================== Helper Functions ====================


def _summarize_marine_conditions(hourly: dict) -> dict[str, Any]:
    """Summarize marine conditions from hourly data."""
    if not hourly:
        return {}

    # Filter out None values from lists
    wave_height = [h for h in hourly.get("wave_height", []) if h is not None]
    wind_speed = [w for w in hourly.get("wind_speed_10m", []) if w is not None]

    summary = {}

    if wave_height:
        max_wave = max(wave_height)
        avg_wave = sum(wave_height) / len(wave_height)
        summary["waves"] = {
            "max_height_m": max_wave,
            "avg_height_m": round(avg_wave, 2),
            "condition": _get_wave_condition(max_wave),
        }

    if wind_speed:
        max_wind = max(wind_speed)
        summary["wind"] = {
            "max_speed": max_wind,
            "condition": _get_wind_condition(max_wind),
        }

    return summary


def _get_wave_condition(height: float) -> str:
    """Get wave condition description based on height."""
    if height < 0.5:
        return "Calm"
    elif height < 1.25:
        return "Smooth"
    elif height < 2.5:
        return "Slight"
    elif height < 4:
        return "Moderate"
    elif height < 6:
        return "Rough"
    elif height < 9:
        return "Very Rough"
    else:
        return "High/Extreme"


def _get_wind_condition(speed: float) -> str:
    """Get wind condition description based on speed."""
    if speed < 10:
        return "Light"
    elif speed < 20:
        return "Moderate"
    elif speed < 30:
        return "Fresh"
    elif speed < 40:
        return "Strong"
    elif speed < 50:
        return "Gale"
    else:
        return "Storm"


def _get_terrain_category(elevation: float) -> str:
    """Get terrain category based on elevation."""
    if elevation < 100:
        return "Lowland/Coastal"
    elif elevation < 500:
        return "Low Hills"
    elif elevation < 1500:
        return "Highlands"
    elif elevation < 3000:
        return "Mountains"
    else:
        return "High Mountains"
