"""
Forecast Tools for Open-Meteo MCP Server.

Provides tools for accessing current weather, hourly forecasts, daily forecasts,
and 15-minute interval forecasts.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import OpenMeteoClient, create_client


# ==================== Current Weather Tools ====================

def register_forecast_tools(mcp: FastMCP, client: OpenMeteoClient) -> None:
    """Register all forecast-related tools with the MCP server."""
    
    @mcp.tool()
    async def get_current_weather(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
    ) -> dict[str, Any]:
        """
        Get current weather conditions for a location.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Weather variables to retrieve. Common options:
                - temperature_2m: Air temperature at 2 meters
                - relative_humidity_2m: Relative humidity at 2 meters
                - apparent_temperature: Feels-like temperature
                - weather_code: WMO weather condition code
                - wind_speed_10m: Wind speed at 10 meters
                - wind_direction_10m: Wind direction at 10 meters
                - wind_gusts_10m: Wind gusts at 10 meters
                - pressure_msl: Sea level pressure
                - cloud_cover: Total cloud cover
                - visibility: Visibility in meters
                - precipitation: Current precipitation
                If None, returns common variables.
            timezone: Timezone for the response (e.g., "auto", "Europe/Berlin")
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"
        
        Returns:
            Current weather data including time and requested variables
        """
        if variables is None:
            variables = [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "pressure_msl",
                "cloud_cover",
                "precipitation",
            ]
        
        response = await client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            current=variables,
            timezone=timezone,
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        result = {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "elevation": data.get("elevation"),
                "timezone": data.get("timezone"),
            },
            "current": data.get("current", {}),
        }
        
        return result
    
    @mcp.tool()
    async def get_hourly_forecast(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 7,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
    ) -> dict[str, Any]:
        """
        Get hourly weather forecast for a location.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Weather variables to retrieve. Options include:
                Temperature: temperature_2m, temperature_2m_max, temperature_2m_min
                Wind: wind_speed_10m, wind_direction_10m, wind_gusts_10m
                Precipitation: precipitation, rain, snowfall, precipitation_probability
                Clouds: cloud_cover, cloud_cover_low, cloud_cover_mid, cloud_cover_high
                Pressure: pressure_msl, surface_pressure
                Humidity: relative_humidity_2m, dewpoint_2m
                Solar: shortwave_radiation, direct_radiation, diffuse_radiation
                UV: uv_index, uv_index_clear_sky
                Soil: soil_temperature_0_7cm, soil_moisture_0_to_7cm
                And many more (use list_weather_variables tool for full list)
            forecast_days: Number of forecast days (1-16, default 7)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"
            precipitation_unit: "mm" or "inch"
        
        Returns:
            Hourly forecast data with timestamps and variable values
        """
        if variables is None:
            variables = [
                "temperature_2m",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "precipitation_probability",
                "cloud_cover",
                "pressure_msl",
            ]
        
        response = await client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
            forecast_days=forecast_days,
            timezone=timezone,
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
            precipitation_unit=precipitation_unit,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        return {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "elevation": data.get("elevation"),
                "timezone": data.get("timezone"),
            },
            "hourly": data.get("hourly", {}),
            "forecast_days": forecast_days,
        }
    
    @mcp.tool()
    async def get_daily_forecast(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 7,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
    ) -> dict[str, Any]:
        """
        Get daily weather forecast for a location.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Daily weather variables. Options include:
                temperature_2m_max, temperature_2m_min: Daily max/min temperature
                apparent_temperature_max, apparent_temperature_min: Feels-like
                sunrise, sunset: Sunrise and sunset times
                daylight_duration: Duration of daylight in seconds
                sunshine_duration: Sunshine duration in seconds
                precipitation_sum: Total precipitation
                rain_sum: Rain sum
                snowfall_sum: Snowfall sum
                precipitation_hours: Hours with precipitation
                wind_speed_10m_max, wind_gusts_10m_max: Max wind/gusts
                wind_direction_10m_dominant: Dominant wind direction
                shortwave_radiation_sum: Solar radiation sum
                et0_fao_evapotranspiration: Evapotranspiration
                weather_code: Daily weather code
            forecast_days: Number of forecast days (1-16, default 7)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"
            precipitation_unit: "mm" or "inch"
        
        Returns:
            Daily forecast data with dates and aggregated values
        """
        if variables is None:
            variables = [
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "sunrise",
                "sunset",
                "daylight_duration",
                "precipitation_sum",
                "rain_sum",
                "snowfall_sum",
                "precipitation_hours",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "weather_code",
            ]
        
        response = await client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            daily=variables,
            forecast_days=forecast_days,
            timezone=timezone,
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
            precipitation_unit=precipitation_unit,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        return {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "elevation": data.get("elevation"),
                "timezone": data.get("timezone"),
            },
            "daily": data.get("daily", {}),
            "forecast_days": forecast_days,
        }
    
    @mcp.tool()
    async def get_15min_forecast(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 1,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
    ) -> dict[str, Any]:
        """
        Get 15-minute interval weather forecast.
        
        Available for Central Europe and North America with high resolution.
        Other locations receive interpolated data.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Weather variables for 15-min intervals:
                temperature_2m, weather_code, cloud_cover
                wind_speed_10m, wind_direction_10m, wind_gusts_10m
                precipitation, rain, showers
                precipitation_probability
            forecast_days: Number of forecast days (1-3 recommended)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"
        
        Returns:
            15-minute interval forecast data
        """
        if variables is None:
            variables = [
                "temperature_2m",
                "weather_code",
                "cloud_cover",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
                "precipitation",
                "rain",
                "precipitation_probability",
            ]
        
        response = await client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            minutely_15=variables,
            forecast_days=forecast_days,
            timezone=timezone,
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        return {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "elevation": data.get("elevation"),
                "timezone": data.get("timezone"),
            },
            "minutely_15": data.get("minutely_15", {}),
            "forecast_days": forecast_days,
        }
    
    @mcp.tool()
    async def get_complete_forecast(
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
    ) -> dict[str, Any]:
        """
        Get complete weather forecast with current, hourly, and daily data.
        
        This is a convenience tool that retrieves all common weather variables
        in a single request.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            forecast_days: Number of forecast days (1-16)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"
            precipitation_unit: "mm" or "inch"
        
        Returns:
            Complete forecast with current, hourly, and daily data
        """
        hourly_vars = [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "precipitation",
            "precipitation_probability",
            "cloud_cover",
            "pressure_msl",
            "visibility",
            "uv_index",
        ]
        
        daily_vars = [
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "sunrise",
            "sunset",
            "daylight_duration",
            "precipitation_sum",
            "rain_sum",
            "snowfall_sum",
            "precipitation_hours",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "weather_code",
            "uv_index_max",
        ]
        
        current_vars = [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "pressure_msl",
            "cloud_cover",
            "visibility",
        ]
        
        response = await client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            current=current_vars,
            hourly=hourly_vars,
            daily=daily_vars,
            forecast_days=forecast_days,
            timezone=timezone,
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
            precipitation_unit=precipitation_unit,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        return response.data
