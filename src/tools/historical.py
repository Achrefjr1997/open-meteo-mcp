"""
Historical Weather Tools for Open-Meteo MCP Server.

Provides tools for accessing historical weather data from 1940 to present,
including hourly and daily resolutions with multiple reanalysis models.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import OpenMeteoClient


def register_historical_tools(mcp: FastMCP, client: OpenMeteoClient) -> None:
    """Register all historical weather tools with the MCP server."""
    
    @mcp.tool()
    async def get_historical_hourly(
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        variables: list[str] | None = None,
        models: str | None = None,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
    ) -> dict[str, Any]:
        """
        Get historical hourly weather data for a date range.
        
        Historical data is based on reanalysis datasets (ERA5, ERA5-Land, IFS)
        combining weather station, aircraft, buoy, radar, and satellite observations.
        
        Data availability by model:
        - ERA5: 1940-present (global, 0.25° resolution)
        - ERA5-Land: 1950-present (global, 0.1° resolution)
        - ECMWF IFS: 2017-present (global, 9km resolution, highest accuracy)
        - CERRA: 1985-2021 (Europe only, 5km resolution)
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            variables: Weather variables to retrieve. Options include:
                Temperature: temperature_2m, apparent_temperature, dewpoint_2m
                Humidity: relative_humidity_2m, vapour_pressure_deficit
                Pressure: pressure_msl, surface_pressure
                Wind: wind_speed_10m, wind_direction_10m, wind_gusts_10m
                Precipitation: precipitation, rain, snowfall, snow_depth
                Clouds: cloud_cover, cloud_cover_low, cloud_cover_mid, cloud_cover_high
                Radiation: shortwave_radiation, direct_radiation, diffuse_radiation
                Solar: sunshine_duration, albedo
                Soil: soil_temperature_0_7cm, soil_moisture_0_to_7cm (4 depths)
                Evapotranspiration: et0_fao_evapotranspiration
                Weather: weather_code, is_day
            models: Weather model to use:
                - "best_match" (default): Automatic best combination
                - "era5": ERA5 reanalysis (1940-present)
                - "era5_land": ERA5-Land (1950-present)
                - "ecmwf_ifs": ECMWF IFS (2017-present, highest resolution)
                - "cerra": CERRA for Europe (1985-2021)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"
            precipitation_unit: "mm" or "inch"
        
        Returns:
            Historical hourly data with timestamps and variable values
        
        Example:
            get_historical_hourly(
                latitude=52.52,
                longitude=13.41,
                start_date="2024-01-01",
                end_date="2024-01-07",
                variables=["temperature_2m", "precipitation", "wind_speed_10m"]
            )
        """
        if variables is None:
            variables = [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "cloud_cover",
                "pressure_msl",
                "shortwave_radiation",
            ]
        
        response = await client.get_historical(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            hourly=variables,
            models=models,
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
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "model": data.get("current_weather", {}).get("model", models or "best_match"),
        }
    
    @mcp.tool()
    async def get_historical_daily(
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        variables: list[str] | None = None,
        models: str | None = None,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
    ) -> dict[str, Any]:
        """
        Get historical daily aggregated weather data.
        
        Daily values are aggregated from hourly data (min, max, sum, mean).
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            variables: Daily weather variables. Options include:
                temperature_2m_max, temperature_2m_min: Daily max/min temperature
                apparent_temperature_max, apparent_temperature_min
                sunrise, sunset: Sunrise and sunset times
                daylight_duration: Daylight duration in seconds
                sunshine_duration: Sunshine duration in seconds
                precipitation_sum: Total daily precipitation
                rain_sum: Rain sum
                snowfall_sum: Snowfall sum
                precipitation_hours: Hours with precipitation
                wind_speed_10m_max, wind_gusts_10m_max: Max wind/gusts
                wind_direction_10m_dominant: Dominant wind direction
                shortwave_radiation_sum: Solar radiation sum
                et0_fao_evapotranspiration: Evapotranspiration sum
                weather_code: Daily weather code
                soil_moisture_index: Soil moisture index
            models: Weather model (see get_historical_hourly)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
            wind_speed_unit: "kmh", "ms", "mph", or "kn"
            precipitation_unit: "mm" or "inch"
        
        Returns:
            Historical daily data with dates and aggregated values
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
                "shortwave_radiation_sum",
                "et0_fao_evapotranspiration",
            ]
        
        response = await client.get_historical(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            daily=variables,
            models=models,
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
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
        }
    
    @mcp.tool()
    async def get_historical_temperature_extremes(
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        timezone: str = "GMT",
        temperature_unit: str = "celsius",
    ) -> dict[str, Any]:
        """
        Get historical temperature extremes for a period.
        
        Retrieves maximum and minimum temperatures with their occurrence times.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            timezone: Timezone for the response
            temperature_unit: "celsius" or "fahrenheit"
        
        Returns:
            Temperature extremes including max/min values and timestamps
        """
        variables = [
            "temperature_2m",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature",
        ]
        
        response = await client.get_historical(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            hourly=variables,
            timezone=timezone,
            temperature_unit=temperature_unit,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        hourly = data.get("hourly", {})
        time = hourly.get("time", [])
        temp = hourly.get("temperature_2m", [])
        temp_max = hourly.get("temperature_2m_max", [])
        temp_min = hourly.get("temperature_2m_min", [])
        
        # Calculate extremes
        result = {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            },
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "extremes": {},
        }
        
        if temp_max:
            max_value = max(temp_max)
            max_index = temp_max.index(max_value)
            result["extremes"]["maximum"] = {
                "value": max_value,
                "unit": temperature_unit,
                "time": time[max_index] if max_index < len(time) else None,
            }
        
        if temp_min:
            min_value = min(temp_min)
            min_index = temp_min.index(min_value)
            result["extremes"]["minimum"] = {
                "value": min_value,
                "unit": temperature_unit,
                "time": time[min_index] if min_index < len(time) else None,
            }
        
        if temp:
            result["extremes"]["average"] = sum(temp) / len(temp) if temp else None
        
        return result
    
    @mcp.tool()
    async def get_historical_precipitation_analysis(
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        timezone: str = "GMT",
        precipitation_unit: str = "mm",
    ) -> dict[str, Any]:
        """
        Get historical precipitation analysis for a period.
        
        Calculates total, average, rainy days, and daily breakdown.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            timezone: Timezone for the response
            precipitation_unit: "mm" or "inch"
        
        Returns:
            Precipitation analysis with totals, averages, and daily data
        """
        variables = ["precipitation", "rain", "snowfall"]
        
        response = await client.get_historical(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            hourly=variables,
            timezone=timezone,
            precipitation_unit=precipitation_unit,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        hourly = data.get("hourly", {})
        time = hourly.get("time", [])
        precip = hourly.get("precipitation", [])
        rain = hourly.get("rain", [])
        snow = hourly.get("snowfall", [])
        
        # Calculate statistics
        total_precip = sum(precip) if precip else 0
        total_rain = sum(rain) if rain else 0
        total_snow = sum(snow) if snow else 0
        
        # Count rainy hours
        rainy_hours = sum(1 for p in precip if p > 0)
        
        result = {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            },
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "analysis": {
                "total_precipitation": total_precip,
                "total_rain": total_rain,
                "total_snowfall": total_snow,
                "rainy_hours": rainy_hours,
                "unit": precipitation_unit,
            },
        }
        
        # Add daily breakdown if data available
        if time and precip:
            daily_totals = {}
            for i, t in enumerate(time):
                day = t[:10]  # Extract YYYY-MM-DD
                if day not in daily_totals:
                    daily_totals[day] = 0
                daily_totals[day] += precip[i] if i < len(precip) else 0
            
            result["daily_breakdown"] = daily_totals
        
        return result
    
    @mcp.tool()
    async def get_historical_wind_analysis(
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        timezone: str = "GMT",
        wind_speed_unit: str = "kmh",
    ) -> dict[str, Any]:
        """
        Get historical wind analysis for a period.
        
        Calculates max wind speed, dominant direction, and statistics.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            timezone: Timezone for the response
            wind_speed_unit: "kmh", "ms", "mph", or "kn"
        
        Returns:
            Wind analysis with max speed, average, and direction statistics
        """
        variables = ["wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"]
        
        response = await client.get_historical(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            hourly=variables,
            timezone=timezone,
            wind_speed_unit=wind_speed_unit,
        )
        
        if not response.success:
            return {"error": response.error_message}
        
        data = response.data
        hourly = data.get("hourly", {})
        time = hourly.get("time", [])
        wind_speed = hourly.get("wind_speed_10m", [])
        wind_dir = hourly.get("wind_direction_10m", [])
        wind_gusts = hourly.get("wind_gusts_10m", [])
        
        result = {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            },
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "analysis": {
                "max_wind_speed": max(wind_speed) if wind_speed else None,
                "avg_wind_speed": sum(wind_speed) / len(wind_speed) if wind_speed else None,
                "max_wind_gusts": max(wind_gusts) if wind_gusts else None,
                "unit": wind_speed_unit,
            },
        }
        
        # Calculate dominant wind direction
        if wind_dir:
            # Convert to vectors for proper averaging
            import math
            sin_sum = sum(math.sin(math.radians(d)) for d in wind_dir if d is not None)
            cos_sum = sum(math.cos(math.radians(d)) for d in wind_dir if d is not None)
            avg_direction = math.degrees(math.atan2(sin_sum, cos_sum)) % 360
            result["analysis"]["dominant_wind_direction"] = avg_direction
        
        return result
