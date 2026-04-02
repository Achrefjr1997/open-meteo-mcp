"""
Air Quality Tools for Open-Meteo MCP Server.

Provides tools for accessing air quality data including particulate matter,
gases, air quality indices (AQI), and pollen forecasts (Europe).
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import OpenMeteoClient


def register_air_quality_tools(mcp: FastMCP, client: OpenMeteoClient) -> None:
    """Register all air quality tools with the MCP server."""
    
    @mcp.tool()
    async def get_current_air_quality(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        domains: str = "auto",
        timezone: str = "GMT",
    ) -> dict[str, Any]:
        """
        Get current air quality conditions.
        
        Data sources:
        - CAMS European Air Quality Forecast (Europe, 11km resolution)
        - CAMS Global Atmospheric Composition Forecasts (Global, 45km resolution)
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Air quality variables. Options include:
                Particulate Matter: pm10, pm2_5
                Gases: co (carbon monoxide), co2 (carbon dioxide),
                    no2 (nitrogen dioxide), so2 (sulphur dioxide),
                    o3 (ozone), nh3 (ammonia)
                Indices: european_aqi_pm2_5, european_aqi_pm10,
                    european_aqi_no2, european_aqi_o3, european_aqi_so2,
                    us_aqi_pm2_5, us_aqi_pm10, us_aqi_no2,
                    us_aqi_co, us_aqi_o3, us_aqi_so2
                Other: uv_index, dust, aerosol_optical_depth
                Pollen (Europe, seasonal): alder_pollen, birch_pollen,
                    grass_pollen, mugwort_pollen, olive_pollen, ragweed_pollen
                If None, returns PM2.5, PM10, and main AQI indices.
            domains: Data domain selection:
                - "auto" (default): Automatic selection based on location
                - "cams_europe": European domain only
                - "cams_global": Global domain only
            timezone: Timezone for the response
        
        Returns:
            Current air quality data with variable values and AQI interpretations
        """
        if variables is None:
            variables = [
                "pm10",
                "pm2_5",
                "carbon_monoxide",
                "nitrogen_dioxide",
                "sulphur_dioxide",
                "ozone",
                "european_aqi_pm2_5",
                "european_aqi_pm10",
                "us_aqi_pm2_5",
                "us_aqi_pm10",
            ]
        
        response = await client.get_air_quality(
            latitude=latitude,
            longitude=longitude,
            current=variables,
            domains=domains,
            timezone=timezone,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        current = data.get("current", {})
        
        result = {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timezone"),
            },
            "current": current,
            "aqi_interpretation": _interpret_aqi(current),
        }
        
        return result
    
    @mcp.tool()
    async def get_hourly_air_quality(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 5,
        past_days: int = 0,
        domains: str = "auto",
        timezone: str = "GMT",
    ) -> dict[str, Any]:
        """
        Get hourly air quality forecast and historical data.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Air quality variables (see get_current_air_quality)
            forecast_days: Number of forecast days (0-7, default 5)
            past_days: Number of past days to include (0-92, default 0)
            domains: Data domain selection ("auto", "cams_europe", "cams_global")
            timezone: Timezone for the response
        
        Returns:
            Hourly air quality data with timestamps
        """
        if variables is None:
            variables = [
                "pm10",
                "pm2_5",
                "ozone",
                "nitrogen_dioxide",
                "european_aqi_pm2_5",
                "us_aqi_pm2_5",
            ]
        
        response = await client.get_air_quality(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
            forecast_days=forecast_days,
            past_days=past_days,
            domains=domains,
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
            "period": {
                "forecast_days": forecast_days,
                "past_days": past_days,
            },
        }
    
    @mcp.tool()
    async def get_air_quality_index(
        latitude: float,
        longitude: float,
        standard: str = "european",
        timezone: str = "GMT",
    ) -> dict[str, Any]:
        """
        Get air quality index with health recommendations.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            standard: AQI standard to use:
                - "european": European Air Quality Index
                - "us": US Air Quality Index (EPA)
            timezone: Timezone for the response
        
        Returns:
            AQI values with category, health implications, and recommendations
        """
        if standard.lower() == "european":
            variables = [
                "european_aqi_pm2_5",
                "european_aqi_pm10",
                "european_aqi_no2",
                "european_aqi_o3",
                "european_aqi_so2",
            ]
        else:  # US
            variables = [
                "us_aqi_pm2_5",
                "us_aqi_pm10",
                "us_aqi_no2",
                "us_aqi_co",
                "us_aqi_o3",
                "us_aqi_so2",
            ]
        
        response = await client.get_air_quality(
            latitude=latitude,
            longitude=longitude,
            current=variables,
            timezone=timezone,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        current = data.get("current", {})
        
        # Get the overall AQI (maximum of all sub-indices)
        aqi_values = [v for v in current.values() if isinstance(v, (int, float))]
        overall_aqi = max(aqi_values) if aqi_values else None
        
        result = {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            },
            "standard": standard,
            "overall_aqi": overall_aqi,
            "category": _get_aqi_category(overall_aqi, standard),
            "pollutants": current,
            "health_recommendations": _get_health_recommendations(overall_aqi, standard),
        }
        
        return result
    
    @mcp.tool()
    async def get_pollen_forecast(
        latitude: float,
        longitude: float,
        days: int = 5,
        timezone: str = "GMT",
    ) -> dict[str, Any]:
        """
        Get pollen forecast for allergy sufferers.
        
        Note: Pollen data is only available for Europe during pollen season.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            days: Number of forecast days (1-5)
            timezone: Timezone for the response
        
        Returns:
            Pollen forecast with concentration levels for different pollen types
        """
        variables = [
            "alder_pollen",
            "birch_pollen",
            "grass_pollen",
            "mugwort_pollen",
            "olive_pollen",
            "ragweed_pollen",
        ]
        
        response = await client.get_air_quality(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
            forecast_days=days,
            timezone=timezone,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        hourly = data.get("hourly", {})
        
        # Check if pollen data is available
        has_pollen = any(k.endswith("_pollen") for k in hourly.keys())
        if not has_pollen:
            return {
                "location": {
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                },
                "message": "Pollen data not available for this location. "
                          "Pollen forecasts are only available for Europe during pollen season.",
            }
        
        return {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            },
            "hourly": hourly,
            "pollen_types": [
                "alder", "birch", "grass", "mugwort", "olive", "ragweed"
            ],
        }
    
    @mcp.tool()
    async def get_uv_index_forecast(
        latitude: float,
        longitude: float,
        days: int = 5,
        timezone: str = "GMT",
    ) -> dict[str, Any]:
        """
        Get UV index forecast with safety recommendations.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            days: Number of forecast days (1-7)
            timezone: Timezone for the response
        
        Returns:
            UV index forecast with risk levels and safety recommendations
        """
        variables = ["uv_index", "uv_index_clear_sky"]
        
        response = await client.get_air_quality(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
            forecast_days=days,
            timezone=timezone,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        hourly = data.get("hourly", {})
        
        # Extract daily max UV index
        time = hourly.get("time", [])
        uv_index = hourly.get("uv_index", [])
        
        daily_max_uv = {}
        for i, t in enumerate(time):
            if i < len(uv_index):
                day = t[:10]  # Extract YYYY-MM-DD
                if day not in daily_max_uv:
                    daily_max_uv[day] = 0
                daily_max_uv[day] = max(daily_max_uv[day], uv_index[i])
        
        result = {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            },
            "hourly": hourly,
            "daily_max_uv": daily_max_uv,
            "uv_risk_levels": {
                day: _get_uv_risk_level(uv) for day, uv in daily_max_uv.items()
            },
        }
        
        return result


# ==================== Helper Functions ====================

def _interpret_aqi(current: dict) -> dict[str, str]:
    """Interpret AQI values and provide health guidance."""
    interpretation = {}
    
    # European AQI interpretation
    eu_aqi = current.get("european_aqi_pm2_5") or current.get("european_aqi_pm10")
    if eu_aqi:
        if eu_aqi <= 20:
            interpretation["european"] = "Good - Air quality is satisfactory"
        elif eu_aqi <= 40:
            interpretation["european"] = "Fair - Acceptable air quality"
        elif eu_aqi <= 60:
            interpretation["european"] = "Moderate - Sensitive individuals should limit outdoor activity"
        elif eu_aqi <= 80:
            interpretation["european"] = "Poor - Health effects for sensitive groups"
        elif eu_aqi <= 100:
            interpretation["european"] = "Very Poor - Health warnings for everyone"
        else:
            interpretation["european"] = "Extremely Poor - Emergency conditions"
    
    # US AQI interpretation
    us_aqi = current.get("us_aqi_pm2_5") or current.get("us_aqi_pm10")
    if us_aqi:
        if us_aqi <= 50:
            interpretation["us"] = "Good - Air quality is satisfactory"
        elif us_aqi <= 100:
            interpretation["us"] = "Moderate - Acceptable for most people"
        elif us_aqi <= 150:
            interpretation["us"] = "Unhealthy for Sensitive Groups"
        elif us_aqi <= 200:
            interpretation["us"] = "Unhealthy - Health effects for everyone"
        elif us_aqi <= 300:
            interpretation["us"] = "Very Unhealthy - Health alert"
        else:
            interpretation["us"] = "Hazardous - Emergency conditions"
    
    return interpretation


def _get_aqi_category(aqi: int | float | None, standard: str) -> str:
    """Get AQI category name based on value and standard."""
    if aqi is None:
        return "Unknown"
    
    aqi = int(aqi)
    
    if standard.lower() == "european":
        if aqi <= 20:
            return "Good"
        elif aqi <= 40:
            return "Fair"
        elif aqi <= 60:
            return "Moderate"
        elif aqi <= 80:
            return "Poor"
        elif aqi <= 100:
            return "Very Poor"
        else:
            return "Extremely Poor"
    else:  # US
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"


def _get_health_recommendations(aqi: int | float | None, standard: str) -> dict[str, str]:
    """Get health recommendations based on AQI."""
    if aqi is None:
        return {"general": "No data available"}
    
    aqi = int(aqi)
    
    if standard.lower() == "european":
        if aqi <= 20:
            return {
                "general": "Enjoy your usual outdoor activities.",
                "sensitive": "No special precautions needed.",
            }
        elif aqi <= 40:
            return {
                "general": "Enjoy your usual outdoor activities.",
                "sensitive": "Consider reducing intense outdoor activities if you experience symptoms.",
            }
        elif aqi <= 60:
            return {
                "general": "Consider reducing intense outdoor activities if you experience symptoms.",
                "sensitive": "Reduce intense outdoor activities, especially if you experience coughing or throat irritation.",
            }
        elif aqi <= 80:
            return {
                "general": "Reduce intense outdoor activities.",
                "sensitive": "Avoid intense outdoor activities. Consider staying indoors.",
            }
        else:
            return {
                "general": "Avoid outdoor activities. Stay indoors.",
                "sensitive": "Stay indoors and keep windows closed. Use air purifier if available.",
            }
    else:  # US
        if aqi <= 50:
            return {
                "general": "Air quality is satisfactory. Enjoy outdoor activities.",
                "sensitive": "No precautions needed.",
            }
        elif aqi <= 100:
            return {
                "general": "Acceptable air quality for most people.",
                "sensitive": "Unusually sensitive people should consider limiting prolonged outdoor exertion.",
            }
        elif aqi <= 150:
            return {
                "general": "Members of sensitive groups may experience health effects.",
                "sensitive": "Reduce prolonged or heavy outdoor exertion.",
            }
        elif aqi <= 200:
            return {
                "general": "Everyone may begin to experience health effects.",
                "sensitive": "Avoid prolonged or heavy outdoor exertion. Move activities indoors.",
            }
        else:
            return {
                "general": "Health alert: everyone may experience serious health effects.",
                "sensitive": "Avoid all outdoor activities. Stay indoors with air purifier.",
            }


def _get_uv_risk_level(uv_index: float) -> dict[str, str]:
    """Get UV risk level and recommendations."""
    if uv_index < 3:
        return {
            "level": "Low",
            "color": "Green",
            "recommendation": "No protection needed. Safe to be outside.",
        }
    elif uv_index < 6:
        return {
            "level": "Moderate",
            "color": "Yellow",
            "recommendation": "Seek shade during midday hours. Wear sunscreen and protective clothing.",
        }
    elif uv_index < 8:
        return {
            "level": "High",
            "color": "Orange",
            "recommendation": "Reduce time in sun between 10am-4pm. Wear protective clothing, hat, and sunglasses.",
        }
    elif uv_index < 11:
        return {
            "level": "Very High",
            "color": "Red",
            "recommendation": "Avoid sun exposure during midday hours. Take all precautions.",
        }
    else:
        return {
            "level": "Extreme",
            "color": "Violet",
            "recommendation": "Avoid all sun exposure. Take all precautions: protective clothing, sunscreen, shade.",
        }
