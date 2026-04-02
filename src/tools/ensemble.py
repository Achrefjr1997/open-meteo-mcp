"""
Ensemble and Specialized Model Tools for Open-Meteo MCP Server.

Provides tools for accessing ensemble forecasts from multiple weather models,
and model-specific forecasts (ECMWF, GFS, ICON, etc.).
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import OpenMeteoClient


def register_ensemble_tools(mcp: FastMCP, client: OpenMeteoClient) -> None:
    """Register all ensemble and specialized model tools with the MCP server."""

    @mcp.tool()
    async def get_ensemble_forecast(
        latitude: float,
        longitude: float,
        models: list[str] | None = None,
        variables: list[str] | None = None,
        forecast_days: int = 7,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
    ) -> dict[str, Any]:
        """
        Get ensemble forecast from multiple weather models.

        Ensemble forecasts combine predictions from multiple models or model runs
        to provide probability information and uncertainty estimates.

        Available models by provider:
        - DWD (Germany): icon_eps, icon_eps_eu, icon_eps_d2
        - NOAA (USA): gfs_ens, gfs_ens_025, gfs_ens_05
        - ECMWF: ifs_ensemble, aifs_ensemble
        - ECCC (Canada): gem_ensemble
        - UK Met Office: ukmo_ensemble
        - MeteoSwiss: icon_ch1_eps, icon_ch2_eps
        - And many more...

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            models: List of model names to include. Common options:
                - "best_match": Automatic best combination (default)
                - "icon_eps": DWD ICON Ensemble (Global)
                - "icon_eps_eu": DWD ICON Ensemble (Europe)
                - "gfs_ens": NOAA GFS Ensemble
                - "ifs_ensemble": ECMWF IFS Ensemble
                - "gem_ensemble": Environment Canada GEM Ensemble
                - "ukmo_ensemble": UK Met Office Ensemble
                Use list_available_models() to see all options.
            variables: Weather variables. Options include:
                temperature_2m, weather_code, wind_speed_10m, wind_direction_10m
                precipitation_probability, precipitation_amount
                cloud_cover, pressure_msl, relative_humidity_2m
            forecast_days: Number of forecast days (1-35, model dependent)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"
            precipitation_unit: "mm" or "inch"

        Returns:
            Ensemble forecast data with model comparisons and statistics
        """
        if models is None:
            models = ["best_match"]

        if variables is None:
            variables = [
                "temperature_2m",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation_probability",
                "precipitation",
                "cloud_cover",
                "pressure_msl",
            ]

        response = await client.get_ensemble(
            latitude=latitude,
            longitude=longitude,
            models=models,
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
            "models": models,
            "hourly": data.get("hourly", {}),
            "forecast_days": forecast_days,
        }

    @mcp.tool()
    async def compare_weather_models(
        latitude: float,
        longitude: float,
        models: list[str] | None = None,
        variable: str = "temperature_2m",
        forecast_days: int = 7,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
    ) -> dict[str, Any]:
        """
        Compare forecasts from multiple weather models for a specific variable.

        This tool helps identify model agreement/disagreement and uncertainty.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            models: List of models to compare. Default includes major global models:
                ["ecmwf_ifs04", "gfs_global", "icon_global", "gem_global"]
            variable: Single weather variable to compare (default: temperature_2m)
            forecast_days: Number of forecast days
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"

        Returns:
            Model comparison with statistics (min, max, mean, spread)
        """
        if models is None:
            models = ["ecmwf_ifs04", "gfs_global", "icon_global", "gem_global"]

        response = await client.get_ensemble(
            latitude=latitude,
            longitude=longitude,
            models=models,
            hourly=[variable],
            forecast_days=forecast_days,
            timezone=timezone,
            temperature_unit=temperature_unit,
        )

        if not response.success:
            return {"error": response.error_message}

        data = response.data
        hourly = data.get("hourly", {})
        time = hourly.get("time", [])

        # Extract model data
        model_data = {}
        for key, values in hourly.items():
            if key != "time" and variable in key:
                model_data[key] = values

        # Calculate statistics across models
        statistics = []
        for i, t in enumerate(time):
            values_at_time = []
            for model_values in model_data.values():
                if i < len(model_values) and model_values[i] is not None:
                    values_at_time.append(model_values[i])

            if values_at_time:
                statistics.append(
                    {
                        "time": t,
                        "min": min(values_at_time),
                        "max": max(values_at_time),
                        "mean": sum(values_at_time) / len(values_at_time),
                        "spread": max(values_at_time) - min(values_at_time),
                        "model_count": len(values_at_time),
                    }
                )

        return {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            },
            "variable": variable,
            "unit": temperature_unit,
            "models_compared": list(model_data.keys()),
            "model_count": len(models),
            "statistics": statistics,
            "interpretation": {
                "low_spread": "Models agree - higher confidence",
                "high_spread": "Models disagree - lower confidence",
            },
        }

    @mcp.tool()
    async def get_ecmwf_forecast(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 10,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
    ) -> dict[str, Any]:
        """
        Get ECMWF IFS weather forecast.

        The ECMWF (European Centre for Medium-Range Weather Forecasts) IFS model
        is one of the most accurate global weather models, with 9km resolution.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Weather variables (see get_ensemble_forecast)
            forecast_days: Number of forecast days (1-10)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"

        Returns:
            ECMWF IFS forecast data
        """
        if variables is None:
            variables = [
                "temperature_2m",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "cloud_cover",
                "pressure_msl",
                "shortwave_radiation",
            ]

        response = await client.get_ecmwf(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
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
            "model": "ECMWF IFS",
            "model_info": {
                "provider": "European Centre for Medium-Range Weather Forecasts",
                "resolution": "9 km global",
                "update_frequency": "Every 6 hours",
            },
            "hourly": data.get("hourly", {}),
            "forecast_days": forecast_days,
        }

    @mcp.tool()
    async def get_gfs_forecast(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 16,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
    ) -> dict[str, Any]:
        """
        Get NOAA GFS (Global Forecast System) weather forecast.

        GFS is the primary global weather model used by the US National Weather Service.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Weather variables
            forecast_days: Number of forecast days (1-16)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"

        Returns:
            GFS forecast data
        """
        if variables is None:
            variables = [
                "temperature_2m",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "cloud_cover",
                "pressure_msl",
            ]

        response = await client.get_gfs(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
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
            "model": "NOAA GFS",
            "model_info": {
                "provider": "US National Oceanic and Atmospheric Administration",
                "resolution": "0.25° (~25 km) global",
                "update_frequency": "Every 6 hours",
            },
            "hourly": data.get("hourly", {}),
            "forecast_days": forecast_days,
        }

    @mcp.tool()
    async def get_icon_forecast(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 7,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
    ) -> dict[str, Any]:
        """
        Get DWD ICON weather forecast.

        ICON (Icosahedral Non-hydrostatic) is Germany's global weather model,
        known for high accuracy especially in Europe.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Weather variables
            forecast_days: Number of forecast days (1-7)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"

        Returns:
            ICON forecast data
        """
        if variables is None:
            variables = [
                "temperature_2m",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "cloud_cover",
                "pressure_msl",
            ]

        response = await client.get_dwd_icon(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
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
            "model": "DWD ICON",
            "model_info": {
                "provider": "German Weather Service (DWD)",
                "resolution": "~6 km global",
                "update_frequency": "Every hour",
            },
            "hourly": data.get("hourly", {}),
            "forecast_days": forecast_days,
        }

    @mcp.tool()
    async def get_metno_forecast(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 10,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
    ) -> dict[str, Any]:
        """
        Get Met Norway weather forecast.

        Met Norway (Norwegian Meteorological Institute) provides high-quality
        forecasts especially for Northern Europe and the Arctic.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Weather variables
            forecast_days: Number of forecast days (1-10)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"

        Returns:
            Met Norway forecast data
        """
        if variables is None:
            variables = [
                "temperature_2m",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "cloud_cover",
                "pressure_msl",
            ]

        response = await client.get_met_norway(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
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
            "model": "Met Norway",
            "model_info": {
                "provider": "Norwegian Meteorological Institute",
                "resolution": "~2.5 km (Nordic), ~10 km (global)",
                "update_frequency": "Every hour",
            },
            "hourly": data.get("hourly", {}),
            "forecast_days": forecast_days,
        }

    @mcp.tool()
    async def get_meteo_france_forecast(
        latitude: float,
        longitude: float,
        variables: list[str] | None = None,
        forecast_days: int = 14,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
    ) -> dict[str, Any]:
        """
        Get Météo-France weather forecast.

        Best for France and French overseas territories.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            variables: Weather variables
            forecast_days: Number of forecast days (1-14)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"

        Returns:
            Météo-France forecast data
        """
        if variables is None:
            variables = [
                "temperature_2m",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "cloud_cover",
                "pressure_msl",
            ]

        response = await client.get_meteo_france(
            latitude=latitude,
            longitude=longitude,
            hourly=variables,
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
            "model": "Météo-France",
            "model_info": {
                "provider": "Météo-France",
                "resolution": "~2.5 km (France), ~10 km (global)",
                "update_frequency": "Every 6 hours",
            },
            "hourly": data.get("hourly", {}),
            "forecast_days": forecast_days,
        }
