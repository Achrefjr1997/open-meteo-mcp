"""
MCP Resources for Weather Variables.

Provides read-only access to weather variable definitions, categories,
and usage information via URI-based resources.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP


def register_variable_resources(mcp: FastMCP) -> None:
    """Register all variable-related resources with the MCP server."""

    @mcp.resource("weather://variables/all")
    def get_all_variables() -> dict[str, Any]:
        """
        Get all available weather variables with descriptions.

        Returns complete list of 200+ weather variables organized by category.
        """
        return {
            "total": len(_VARIABLES),
            "categories": list(_CATEGORIES.keys()),
            "variables": _VARIABLES,
        }

    @mcp.resource("weather://variables/temperature")
    def get_temperature_variables() -> dict[str, str]:
        """Get temperature-related weather variables."""
        return _filter_by_category("temperature")

    @mcp.resource("weather://variables/wind")
    def get_wind_variables() -> dict[str, str]:
        """Get wind-related weather variables."""
        return _filter_by_category("wind")

    @mcp.resource("weather://variables/precipitation")
    def get_precipitation_variables() -> dict[str, str]:
        """Get precipitation-related weather variables."""
        return _filter_by_category("precipitation")

    @mcp.resource("weather://variables/clouds")
    def get_cloud_variables() -> dict[str, str]:
        """Get cloud-related weather variables."""
        return _filter_by_category("clouds")

    @mcp.resource("weather://variables/pressure")
    def get_pressure_variables() -> dict[str, str]:
        """Get pressure-related weather variables."""
        return _filter_by_category("pressure")

    @mcp.resource("weather://variables/humidity")
    def get_humidity_variables() -> dict[str, str]:
        """Get humidity-related weather variables."""
        return _filter_by_category("humidity")

    @mcp.resource("weather://variables/solar")
    def get_solar_variables() -> dict[str, str]:
        """Get solar radiation and UV variables."""
        return _filter_by_category("solar")

    @mcp.resource("weather://variables/soil")
    def get_soil_variables() -> dict[str, str]:
        """Get soil temperature and moisture variables."""
        return _filter_by_category("soil")

    @mcp.resource("weather://variables/air_quality")
    def get_air_quality_variables() -> dict[str, str]:
        """Get air quality variables including PM, gases, and AQI indices."""
        return _filter_by_category("air_quality")

    @mcp.resource("weather://variables/marine")
    def get_marine_variables() -> dict[str, str]:
        """Get marine weather variables including waves and swells."""
        return _filter_by_category("marine")

    @mcp.resource("weather://variables/pressure_levels")
    def get_pressure_level_variables() -> dict[str, str]:
        """
        Get atmospheric pressure level variables.

        Available at levels: 1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50 hPa
        """
        return {
            "description": "Variables available at specific pressure levels",
            "levels_hpa": [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50],
            "variables": {
                "temperature_{level}hPa": "Temperature at pressure level",
                "relative_humidity_{level}hPa": "Relative humidity at pressure level",
                "dewpoint_{level}hPa": "Dewpoint at pressure level",
                "cloud_cover_{level}hPa": "Cloud cover at pressure level",
                "wind_speed_{level}hPa": "Wind speed at pressure level",
                "wind_direction_{level}hPa": "Wind direction at pressure level",
                "vertical_velocity_{level}hPa": "Vertical velocity at pressure level",
                "geopotential_height_{level}hPa": "Geopotential height at pressure level",
            },
        }

    @mcp.resource("weather://variables/weather_codes")
    def get_weather_codes() -> dict[str, dict[str, str]]:
        """
        Get WMO weather codes with descriptions.

        Weather codes (0-99) describe weather conditions.
        """
        return _WEATHER_CODES

    @mcp.resource("weather://variables/usage-guide")
    def get_variables_usage_guide() -> dict[str, Any]:
        """
        Get guide for using weather variables effectively.

        Includes best practices, common combinations, and usage examples.
        """
        return {
            "title": "Weather Variables Usage Guide",
            "sections": {
                "getting_started": {
                    "title": "Getting Started",
                    "content": "Use list_weather_variables() tool to discover available variables. "
                    "Variables are grouped by category for easy discovery.",
                },
                "common_combinations": {
                    "title": "Common Variable Combinations",
                    "combinations": {
                        "basic_weather": [
                            "temperature_2m",
                            "weather_code",
                            "wind_speed_10m",
                            "precipitation",
                            "cloud_cover",
                        ],
                        "detailed_forecast": [
                            "temperature_2m",
                            "relative_humidity_2m",
                            "apparent_temperature",
                            "weather_code",
                            "wind_speed_10m",
                            "wind_direction_10m",
                            "precipitation",
                            "precipitation_probability",
                            "cloud_cover",
                            "pressure_msl",
                            "uv_index",
                        ],
                        "marine_conditions": [
                            "wave_height",
                            "wave_period",
                            "wave_direction",
                            "swell_height",
                            "swell_period",
                            "swell_direction",
                            "wind_speed_10m",
                            "wind_direction_10m",
                        ],
                        "air_quality": [
                            "pm10",
                            "pm2_5",
                            "ozone",
                            "nitrogen_dioxide",
                            "european_aqi_pm2_5",
                            "us_aqi_pm2_5",
                        ],
                        "solar_energy": [
                            "shortwave_radiation",
                            "direct_radiation",
                            "diffuse_radiation",
                            "direct_normal_irradiance",
                            "global_tilted_irradiance",
                            "uv_index",
                            "cloud_cover",
                        ],
                        "agriculture": [
                            "temperature_2m",
                            "precipitation",
                            "soil_moisture_0_to_7cm",
                            "et0_fao_evapotranspiration",
                            "sunshine_duration",
                        ],
                    },
                },
                "units": {
                    "title": "Units and Conversion",
                    "content": "Units can be configured via API parameters:",
                    "options": {
                        "temperature": ["celsius", "fahrenheit"],
                        "wind_speed": ["kmh", "ms", "mph", "kn"],
                        "precipitation": ["mm", "inch"],
                    },
                },
                "tips": {
                    "title": "Best Practices",
                    "tips": [
                        "Request only needed variables to reduce response size",
                        "Use daily variables for long-term forecasts",
                        "Use hourly variables for detailed analysis",
                        "Check weather_code for quick condition overview",
                        "Use apparent_temperature for 'feels like' information",
                        "Combine precipitation_probability with precipitation for confidence",
                    ],
                },
            },
        }


def _filter_by_category(category: str) -> dict[str, str]:
    """Filter variables by category."""
    return {
        name: info["description"]
        for name, info in _VARIABLES.items()
        if info.get("category") == category
    }


# ==================== Variable Definitions ====================

_VARIABLES = {
    # Temperature
    "temperature_2m": {
        "description": "Air temperature at 2 meters above ground",
        "category": "temperature",
    },
    "temperature_2m_max": {
        "description": "Daily maximum temperature at 2 meters",
        "category": "temperature",
    },
    "temperature_2m_min": {
        "description": "Daily minimum temperature at 2 meters",
        "category": "temperature",
    },
    "apparent_temperature": {
        "description": "Apparent (feels-like) temperature",
        "category": "temperature",
    },
    "apparent_temperature_max": {
        "description": "Maximum apparent temperature",
        "category": "temperature",
    },
    "apparent_temperature_min": {
        "description": "Minimum apparent temperature",
        "category": "temperature",
    },
    "surface_temperature": {
        "description": "Surface temperature (ground level)",
        "category": "temperature",
    },
    "soil_temperature_0_7cm": {
        "description": "Soil temperature at 0-7 cm depth",
        "category": "temperature",
    },
    "soil_temperature_7_to_28cm": {
        "description": "Soil temperature at 7-28 cm depth",
        "category": "temperature",
    },
    "soil_temperature_28_to_100cm": {
        "description": "Soil temperature at 28-100 cm depth",
        "category": "temperature",
    },
    "soil_temperature_100_to_255cm": {
        "description": "Soil temperature at 100-255 cm depth",
        "category": "temperature",
    },
    "dewpoint_2m": {"description": "Dew point temperature at 2 meters", "category": "temperature"},
    "wetbulb_temperature_2m": {
        "description": "Wet bulb temperature at 2 meters",
        "category": "temperature",
    },
    # Wind
    "wind_speed_10m": {"description": "Wind speed at 10 meters above ground", "category": "wind"},
    "wind_direction_10m": {
        "description": "Wind direction at 10 meters (0-360°)",
        "category": "wind",
    },
    "wind_gusts_10m": {"description": "Wind gusts at 10 meters", "category": "wind"},
    "wind_speed_80m": {
        "description": "Wind speed at 80 meters (turbine height)",
        "category": "wind",
    },
    "wind_speed_100m": {"description": "Wind speed at 100 meters", "category": "wind"},
    "wind_speed_120m": {"description": "Wind speed at 120 meters", "category": "wind"},
    "wind_speed_180m": {"description": "Wind speed at 180 meters", "category": "wind"},
    "max_wind_speed_10m": {"description": "Maximum wind speed at 10 meters", "category": "wind"},
    "dominant_wind_direction_10m": {"description": "Dominant wind direction", "category": "wind"},
    # Precipitation
    "precipitation": {
        "description": "Total precipitation (rain + snow + showers)",
        "category": "precipitation",
    },
    "rain": {"description": "Rain", "category": "precipitation"},
    "snowfall": {"description": "Snowfall (water equivalent)", "category": "precipitation"},
    "snow_depth": {"description": "Snow depth on ground", "category": "precipitation"},
    "precipitation_probability": {
        "description": "Precipitation probability",
        "category": "precipitation",
    },
    "showers": {"description": "Showers", "category": "precipitation"},
    "freezing_rain": {"description": "Freezing rain", "category": "precipitation"},
    "precipitation_hours": {"description": "Hours with precipitation", "category": "precipitation"},
    "runoff": {"description": "Surface runoff", "category": "precipitation"},
    # Clouds
    "cloud_cover": {"description": "Total cloud cover (%)", "category": "clouds"},
    "cloud_cover_low": {"description": "Low cloud cover (%)", "category": "clouds"},
    "cloud_cover_mid": {"description": "Mid cloud cover (%)", "category": "clouds"},
    "cloud_cover_high": {"description": "High cloud cover (%)", "category": "clouds"},
    # Pressure
    "pressure_msl": {"description": "Sea level pressure", "category": "pressure"},
    "surface_pressure": {"description": "Surface pressure", "category": "pressure"},
    # Humidity
    "relative_humidity_2m": {
        "description": "Relative humidity at 2 meters (%)",
        "category": "humidity",
    },
    "vapour_pressure_deficit": {"description": "Vapour pressure deficit", "category": "humidity"},
    "total_column_integrated_water_vapour": {
        "description": "Total column water vapour",
        "category": "humidity",
    },
    # Solar
    "shortwave_radiation": {
        "description": "Shortwave radiation (Global Horizontal Irradiance)",
        "category": "solar",
    },
    "direct_radiation": {"description": "Direct solar radiation", "category": "solar"},
    "diffuse_radiation": {"description": "Diffuse radiation (DHI)", "category": "solar"},
    "direct_normal_irradiance": {
        "description": "Direct Normal Irradiance (DNI)",
        "category": "solar",
    },
    "global_tilted_irradiance": {
        "description": "Global Tilted Irradiance (GTI)",
        "category": "solar",
    },
    "terrestrial_radiation": {"description": "Terrestrial radiation", "category": "solar"},
    "uv_index": {"description": "UV Index", "category": "solar"},
    "uv_index_clear_sky": {"description": "UV Index (clear sky)", "category": "solar"},
    "sunshine_duration": {"description": "Sunshine duration", "category": "solar"},
    "albedo": {"description": "Surface albedo", "category": "solar"},
    # Soil
    "soil_moisture_0_to_7cm": {"description": "Soil moisture at 0-7 cm depth", "category": "soil"},
    "soil_moisture_7_to_28cm": {
        "description": "Soil moisture at 7-28 cm depth",
        "category": "soil",
    },
    "soil_moisture_28_to_100cm": {
        "description": "Soil moisture at 28-100 cm depth",
        "category": "soil",
    },
    "soil_moisture_100_to_255cm": {
        "description": "Soil moisture at 100-255 cm depth",
        "category": "soil",
    },
    "soil_moisture_index_0_to_7cm": {
        "description": "Soil moisture index at 0-7 cm",
        "category": "soil",
    },
    # Air Quality
    "pm10": {"description": "PM10 particulate matter (μg/m³)", "category": "air_quality"},
    "pm2_5": {"description": "PM2.5 particulate matter (μg/m³)", "category": "air_quality"},
    "carbon_monoxide": {"description": "Carbon monoxide (CO) (μg/m³)", "category": "air_quality"},
    "carbon_dioxide": {"description": "Carbon dioxide (CO2) (ppm)", "category": "air_quality"},
    "nitrogen_dioxide": {
        "description": "Nitrogen dioxide (NO2) (μg/m³)",
        "category": "air_quality",
    },
    "sulphur_dioxide": {"description": "Sulphur dioxide (SO2) (μg/m³)", "category": "air_quality"},
    "ozone": {"description": "Ozone (O3) (μg/m³)", "category": "air_quality"},
    "ammonia": {"description": "Ammonia (NH3) (μg/m³)", "category": "air_quality"},
    "methane": {"description": "Methane (CH4)", "category": "air_quality"},
    "aerosol_optical_depth": {"description": "Aerosol optical depth", "category": "air_quality"},
    "dust": {"description": "Dust concentration", "category": "air_quality"},
    "european_aqi_pm2_5": {"description": "European AQI (PM2.5)", "category": "air_quality"},
    "european_aqi_pm10": {"description": "European AQI (PM10)", "category": "air_quality"},
    "european_aqi_no2": {"description": "European AQI (NO2)", "category": "air_quality"},
    "european_aqi_o3": {"description": "European AQI (O3)", "category": "air_quality"},
    "us_aqi_pm2_5": {"description": "US EPA AQI (PM2.5)", "category": "air_quality"},
    "us_aqi_pm10": {"description": "US EPA AQI (PM10)", "category": "air_quality"},
    "us_aqi_no2": {"description": "US EPA AQI (NO2)", "category": "air_quality"},
    "us_aqi_co": {"description": "US EPA AQI (CO)", "category": "air_quality"},
    "us_aqi_o3": {"description": "US EPA AQI (O3)", "category": "air_quality"},
    # Marine
    "wave_height": {"description": "Significant wave height", "category": "marine"},
    "wave_direction": {"description": "Wave direction (°)", "category": "marine"},
    "wave_period": {"description": "Wave period (seconds)", "category": "marine"},
    "wave_peak_period": {"description": "Peak wave period", "category": "marine"},
    "wind_wave_height": {"description": "Wind wave height", "category": "marine"},
    "wind_wave_period": {"description": "Wind wave period", "category": "marine"},
    "wind_wave_direction": {"description": "Wind wave direction", "category": "marine"},
    "swell_height": {"description": "Swell height", "category": "marine"},
    "swell_period": {"description": "Swell period", "category": "marine"},
    "swell_direction": {"description": "Swell direction", "category": "marine"},
    "water_temperature": {"description": "Water temperature", "category": "marine"},
    # Other
    "weather_code": {"description": "WMO weather condition code (0-99)", "category": "other"},
    "is_day": {"description": "Is day (1) or night (0)", "category": "other"},
    "visibility": {"description": "Visibility (meters)", "category": "other"},
    "et0_fao_evapotranspiration": {"description": "Evapotranspiration (ET0)", "category": "other"},
    "sunrise": {"description": "Sunrise time", "category": "other"},
    "sunset": {"description": "Sunset time", "category": "other"},
    "daylight_duration": {"description": "Daylight duration (seconds)", "category": "other"},
    "boundary_layer_height": {
        "description": "Atmospheric boundary layer height",
        "category": "other",
    },
    "cape": {"description": "Convective Available Potential Energy", "category": "other"},
}


_CATEGORIES = {
    "temperature": "Temperature variables",
    "wind": "Wind speed, direction, and gusts",
    "precipitation": "Rain, snow, and precipitation",
    "clouds": "Cloud cover and types",
    "pressure": "Atmospheric pressure",
    "humidity": "Humidity and moisture",
    "solar": "Solar radiation and UV",
    "soil": "Soil temperature and moisture",
    "air_quality": "Air quality and pollutants",
    "marine": "Marine and wave conditions",
    "other": "Other weather variables",
}


_WEATHER_CODES = {
    "0": {"description": "Clear sky", "icon": "☀️", "category": "Clear"},
    "1": {"description": "Mainly clear", "icon": "🌤️", "category": "Partly Cloudy"},
    "2": {"description": "Partly cloudy", "icon": "⛅", "category": "Partly Cloudy"},
    "3": {"description": "Overcast", "icon": "☁️", "category": "Cloudy"},
    "45": {"description": "Fog", "icon": "🌫️", "category": "Foggy"},
    "48": {"description": "Depositing rime fog", "icon": "🌫️", "category": "Foggy"},
    "51": {"description": "Light drizzle", "icon": "🌦️", "category": "Drizzle"},
    "53": {"description": "Moderate drizzle", "icon": "🌦️", "category": "Drizzle"},
    "55": {"description": "Dense drizzle", "icon": "🌧️", "category": "Drizzle"},
    "56": {"description": "Light freezing drizzle", "icon": "🌨️", "category": "Freezing"},
    "57": {"description": "Dense freezing drizzle", "icon": "🌨️", "category": "Freezing"},
    "61": {"description": "Slight rain", "icon": "🌧️", "category": "Rain"},
    "63": {"description": "Moderate rain", "icon": "🌧️", "category": "Rain"},
    "65": {"description": "Heavy rain", "icon": "⛈️", "category": "Rain"},
    "66": {"description": "Light freezing rain", "icon": "🌨️", "category": "Freezing"},
    "67": {"description": "Heavy freezing rain", "icon": "🌨️", "category": "Freezing"},
    "71": {"description": "Slight snow fall", "icon": "🌨️", "category": "Snow"},
    "73": {"description": "Moderate snow fall", "icon": "🌨️", "category": "Snow"},
    "75": {"description": "Heavy snow fall", "icon": "❄️", "category": "Snow"},
    "77": {"description": "Snow grains", "icon": "🌨️", "category": "Snow"},
    "80": {"description": "Slight rain showers", "icon": "🌦️", "category": "Showers"},
    "81": {"description": "Moderate rain showers", "icon": "🌧️", "category": "Showers"},
    "82": {"description": "Violent rain showers", "icon": "⛈️", "category": "Showers"},
    "85": {"description": "Slight snow showers", "icon": "🌨️", "category": "Snow Showers"},
    "86": {"description": "Heavy snow showers", "icon": "❄️", "category": "Snow Showers"},
    "95": {"description": "Thunderstorm", "icon": "⚡", "category": "Thunderstorm"},
    "96": {
        "description": "Thunderstorm with slight hail",
        "icon": "⛈️",
        "category": "Thunderstorm",
    },
    "99": {"description": "Thunderstorm with heavy hail", "icon": "⛈️", "category": "Thunderstorm"},
}
