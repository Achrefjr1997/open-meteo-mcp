"""
Specialized Tools for Open-Meteo MCP Server.

Provides utility tools and specialized functions.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import OpenMeteoClient


def register_specialized_tools(mcp: FastMCP, client: OpenMeteoClient) -> None:
    """Register all specialized tools with the MCP server."""
    
    @mcp.tool()
    async def list_weather_variables(
        category: str | None = None,
    ) -> dict[str, Any]:
        """
        List all available weather variables, optionally filtered by category.
        
        Use this tool to discover available variables for weather requests.
        
        Args:
            category: Optional category filter. Options:
                - "temperature": Temperature-related variables
                - "wind": Wind speed, direction, gusts
                - "precipitation": Rain, snow, showers
                - "clouds": Cloud cover and types
                - "pressure": Atmospheric pressure
                - "humidity": Humidity and dewpoint
                - "solar": Solar radiation, UV index
                - "soil": Soil temperature and moisture
                - "air_quality": Particulate matter, gases, AQI
                - "marine": Wave height, period, direction
                - "all": All variables (default)
        
        Returns:
            Dictionary of variable names with descriptions
        """
        variables = get_all_weather_variables()
        
        if category and category.lower() != "all":
            variables = {k: v for k, v in variables.items() 
                        if v.get("category", "").lower() == category.lower()}
        
        # Group by category
        by_category = {}
        for name, info in variables.items():
            cat = info.get("category", "other")
            if cat not in by_category:
                by_category[cat] = {}
            by_category[cat][name] = info.get("description", "")
        
        return {
            "total_variables": len(variables),
            "categories": list(by_category.keys()),
            "variables_by_category": by_category,
        }
    
    @mcp.tool()
    async def list_weather_models() -> dict[str, Any]:
        """
        List all available weather models with descriptions.
        
        Returns:
            Dictionary of model names with provider info and descriptions
        """
        models = get_all_weather_models()
        
        # Group by provider
        by_provider = {}
        for model_id, info in models.items():
            provider = info.get("provider", "Unknown")
            if provider not in by_provider:
                by_provider[provider] = {}
            by_provider[provider][model_id] = info
        
        return {
            "total_models": len(models),
            "providers": list(by_provider.keys()),
            "models_by_provider": by_provider,
        }
    
    @mcp.tool()
    async def get_weather_summary(
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        """
        Get a quick weather summary for a location.
        
        This is a convenience tool that returns current conditions
        and today's forecast in a human-readable format.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
        
        Returns:
            Human-readable weather summary
        """
        # Get current weather
        from .forecast import get_current_weather as _get_current
        current_result = await _get_current(
            latitude=latitude,
            longitude=longitude,
        )
        
        if "error" in current_result:
            return current_result
        
        current = current_result.get("current", {})
        location = current_result.get("location", {})
        
        # Get today's forecast
        from .forecast import get_daily_forecast as _get_daily
        daily_result = await _get_daily(
            latitude=latitude,
            longitude=longitude,
            forecast_days=1,
        )
        
        daily = daily_result.get("daily", {})
        time = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        
        summary = {
            "location": location,
            "current_conditions": {
                "temperature": current.get("temperature_2m"),
                "feels_like": current.get("apparent_temperature"),
                "condition": _get_weather_description(current.get("weather_code", 0)),
                "wind_speed": current.get("wind_speed_10m"),
                "humidity": current.get("relative_humidity_2m"),
            },
            "today_forecast": {},
        }
        
        if time and len(time) > 0:
            summary["today_forecast"] = {
                "date": time[0] if time else None,
                "high": temp_max[0] if temp_max else None,
                "low": temp_min[0] if temp_min else None,
            }
        
        return summary


# ==================== Reference Data ====================

def get_all_weather_variables() -> dict[str, dict[str, str]]:
    """Get all available weather variables with descriptions."""
    return {
        # Temperature
        "temperature_2m": {"description": "Air temperature at 2 meters", "category": "temperature"},
        "temperature_2m_max": {"description": "Daily maximum temperature", "category": "temperature"},
        "temperature_2m_min": {"description": "Daily minimum temperature", "category": "temperature"},
        "apparent_temperature": {"description": "Feels-like temperature", "category": "temperature"},
        "surface_temperature": {"description": "Surface temperature", "category": "temperature"},
        "soil_temperature_0_7cm": {"description": "Soil temperature at 0-7cm depth", "category": "temperature"},
        "soil_temperature_7_to_28cm": {"description": "Soil temperature at 7-28cm depth", "category": "temperature"},
        "soil_temperature_28_to_100cm": {"description": "Soil temperature at 28-100cm depth", "category": "temperature"},
        "soil_temperature_100_to_255cm": {"description": "Soil temperature at 100-255cm depth", "category": "temperature"},
        
        # Wind
        "wind_speed_10m": {"description": "Wind speed at 10 meters", "category": "wind"},
        "wind_direction_10m": {"description": "Wind direction at 10 meters", "category": "wind"},
        "wind_gusts_10m": {"description": "Wind gusts at 10 meters", "category": "wind"},
        "wind_speed_80m": {"description": "Wind speed at 80 meters", "category": "wind"},
        "wind_speed_100m": {"description": "Wind speed at 100 meters", "category": "wind"},
        "wind_speed_120m": {"description": "Wind speed at 120 meters", "category": "wind"},
        
        # Precipitation
        "precipitation": {"description": "Total precipitation (rain + snow)", "category": "precipitation"},
        "rain": {"description": "Rain", "category": "precipitation"},
        "snowfall": {"description": "Snowfall", "category": "precipitation"},
        "precipitation_probability": {"description": "Precipitation probability", "category": "precipitation"},
        "showers": {"description": "Showers", "category": "precipitation"},
        
        # Clouds
        "cloud_cover": {"description": "Total cloud cover", "category": "clouds"},
        "cloud_cover_low": {"description": "Low cloud cover", "category": "clouds"},
        "cloud_cover_mid": {"description": "Mid cloud cover", "category": "clouds"},
        "cloud_cover_high": {"description": "High cloud cover", "category": "clouds"},
        
        # Pressure
        "pressure_msl": {"description": "Sea level pressure", "category": "pressure"},
        "surface_pressure": {"description": "Surface pressure", "category": "pressure"},
        
        # Humidity
        "relative_humidity_2m": {"description": "Relative humidity at 2 meters", "category": "humidity"},
        "dewpoint_2m": {"description": "Dewpoint at 2 meters", "category": "humidity"},
        "vapour_pressure_deficit": {"description": "Vapour pressure deficit", "category": "humidity"},
        
        # Solar
        "shortwave_radiation": {"description": "Shortwave radiation (GHI)", "category": "solar"},
        "direct_radiation": {"description": "Direct radiation", "category": "solar"},
        "diffuse_radiation": {"description": "Diffuse radiation (DHI)", "category": "solar"},
        "direct_normal_irradiance": {"description": "Direct normal irradiance (DNI)", "category": "solar"},
        "global_tilted_irradiance": {"description": "Global tilted irradiance (GTI)", "category": "solar"},
        "uv_index": {"description": "UV Index", "category": "solar"},
        "uv_index_clear_sky": {"description": "UV Index (clear sky)", "category": "solar"},
        "sunshine_duration": {"description": "Sunshine duration", "category": "solar"},
        
        # Soil
        "soil_moisture_0_to_7cm": {"description": "Soil moisture at 0-7cm depth", "category": "soil"},
        "soil_moisture_7_to_28cm": {"description": "Soil moisture at 7-28cm depth", "category": "soil"},
        "soil_moisture_28_to_100cm": {"description": "Soil moisture at 28-100cm depth", "category": "soil"},
        "soil_moisture_100_to_255cm": {"description": "Soil moisture at 100-255cm depth", "category": "soil"},
        
        # Air Quality
        "pm10": {"description": "PM10 particulate matter", "category": "air_quality"},
        "pm2_5": {"description": "PM2.5 particulate matter", "category": "air_quality"},
        "carbon_monoxide": {"description": "Carbon monoxide (CO)", "category": "air_quality"},
        "nitrogen_dioxide": {"description": "Nitrogen dioxide (NO2)", "category": "air_quality"},
        "sulphur_dioxide": {"description": "Sulphur dioxide (SO2)", "category": "air_quality"},
        "ozone": {"description": "Ozone (O3)", "category": "air_quality"},
        "european_aqi_pm2_5": {"description": "European AQI (PM2.5)", "category": "air_quality"},
        "us_aqi_pm2_5": {"description": "US AQI (PM2.5)", "category": "air_quality"},
        
        # Marine
        "wave_height": {"description": "Significant wave height", "category": "marine"},
        "wave_direction": {"description": "Wave direction", "category": "marine"},
        "wave_period": {"description": "Wave period", "category": "marine"},
        "swell_height": {"description": "Swell height", "category": "marine"},
        "swell_period": {"description": "Swell period", "category": "marine"},
        "swell_direction": {"description": "Swell direction", "category": "marine"},
        
        # Other
        "weather_code": {"description": "WMO weather condition code", "category": "other"},
        "is_day": {"description": "Is day or night", "category": "other"},
        "visibility": {"description": "Visibility", "category": "other"},
        "et0_fao_evapotranspiration": {"description": "Evapotranspiration (ET0)", "category": "other"},
        "sunrise": {"description": "Sunrise time", "category": "other"},
        "sunset": {"description": "Sunset time", "category": "other"},
        "daylight_duration": {"description": "Daylight duration", "category": "other"},
    }


def get_all_weather_models() -> dict[str, dict[str, str]]:
    """Get all available weather models with descriptions."""
    return {
        # Global Models
        "ecmwf_ifs04": {"provider": "ECMWF", "description": "ECMWF IFS High Resolution (9km)", "resolution": "9km"},
        "gfs_global": {"provider": "NOAA", "description": "GFS Global Forecast System", "resolution": "25km"},
        "icon_global": {"provider": "DWD", "description": "ICON Global", "resolution": "13km"},
        "gem_global": {"provider": "ECCC", "description": "GEM Global", "resolution": "25km"},
        
        # Regional Models
        "icon_eu": {"provider": "DWD", "description": "ICON Europe", "resolution": "7km"},
        "icon_d2": {"provider": "DWD", "description": "ICON Germany (D2)", "resolution": "2km"},
        "meteofrance_seamless": {"provider": "Météo-France", "description": "Météo-France Seamless", "resolution": "2.5km"},
        "ukmo_uk": {"provider": "UK Met Office", "description": "UK Model (2km)", "resolution": "2km"},
        "metno_nordic": {"provider": "Met Norway", "description": "Met Norway Nordic", "resolution": "2.5km"},
        
        # Ensemble Models
        "icon_eps": {"provider": "DWD", "description": "ICON Ensemble Global", "resolution": "13km"},
        "icon_eps_eu": {"provider": "DWD", "description": "ICON Ensemble Europe", "resolution": "7km"},
        "gfs_ens": {"provider": "NOAA", "description": "GFS Ensemble", "resolution": "25km"},
        "ifs_ensemble": {"provider": "ECMWF", "description": "ECMWF IFS Ensemble", "resolution": "25km"},
        "gem_ensemble": {"provider": "ECCC", "description": "GEM Ensemble", "resolution": "25km"},
        "ukmo_ensemble": {"provider": "UK Met Office", "description": "UK Met Office Ensemble", "resolution": "10km"},
    }


def _get_weather_description(code: int) -> str:
    """Get human-readable weather description from WMO code."""
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Rain showers",
        81: "Moderate showers",
        82: "Violent showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail",
    }
    return descriptions.get(code, "Unknown")
