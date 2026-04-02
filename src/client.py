"""
Open-Meteo API Client.

Async HTTP client for all Open-Meteo API endpoints with comprehensive error handling,
rate limiting, and response parsing.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Literal
from enum import Enum

import httpx


class APIEndpoint(Enum):
    """Open-Meteo API endpoints."""

    FORECAST = "forecast"
    HISTORICAL = "historical-weather"
    AIR_QUALITY = "air-quality"
    GEOCODING_SEARCH = "geocoding/search"
    GEOCODING_GET = "geocoding/get"
    ENSEMBLE = "ensemble"
    ECMWF = "ecmwf"
    GFS = "gfs"
    GFS_HRRR = "gfs-hrrr"
    METEO_FRANCE = "meteofrance"
    DWD_ICON = "dwd-icon"
    GEM = "gem"
    JMA = "jma"
    MET_NORWAY = "metno"
    MARINE = "marine"
    CLIMATE = "climate"
    ELEVATION = "elevation"
    FLOOD = "flood"


@dataclass
class ClientConfig:
    """Configuration for Open-Meteo API client."""

    # Base URLs
    forecast_base_url: str = "https://api.open-meteo.com/v1"
    geocoding_base_url: str = "https://geocoding-api.open-meteo.com/v1"

    # Request settings
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_delay: float = 0.1  # Delay between requests

    # API key for commercial use
    api_key: str | None = None

    # Default parameters
    default_timezone: str = "GMT"
    default_timeformat: Literal["iso8601", "unixtime"] = "iso8601"

    # HTTP settings
    follow_redirects: bool = True
    max_redirects: int = 3


@dataclass
class APIResponse:
    """Standardized API response wrapper."""

    data: dict[str, Any]
    status_code: int
    headers: dict[str, str]
    url: str
    elapsed_ms: float
    success: bool = True
    error_message: str | None = None


class OpenMeteoError(Exception):
    """Base exception for Open-Meteo API errors."""

    pass


class RateLimitError(OpenMeteoError):
    """Raised when rate limit is exceeded."""

    pass


class ValidationError(OpenMeteoError):
    """Raised when input validation fails."""

    pass


class APIError(OpenMeteoError):
    """Raised when API returns an error."""

    def __init__(self, message: str, status_code: int, response: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class OpenMeteoClient:
    """
    Async client for Open-Meteo weather APIs.

    Supports all Open-Meteo endpoints:
    - Forecast API (7-16 day forecasts)
    - Historical Weather API (1940-present)
    - Air Quality API (PM, gases, AQI, pollen)
    - Geocoding API (location search)
    - Ensemble API (multi-model forecasts)
    - Model-specific APIs (ECMWF, GFS, ICON, etc.)
    - Marine, Climate, Elevation, Flood APIs
    """

    def __init__(self, config: ClientConfig | None = None):
        self.config = config or ClientConfig()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                follow_redirects=self.config.follow_redirects,
                max_redirects=self.config.max_redirects,
                headers={
                    "User-Agent": "open-meteo-mcp/0.1.0",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self) -> "OpenMeteoClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @staticmethod
    def _validate_coordinates(latitude: float, longitude: float) -> None:
        """Validate latitude and longitude."""
        if not -90 <= latitude <= 90:
            raise ValidationError(f"Latitude must be between -90 and 90, got {latitude}")
        if not -180 <= longitude <= 180:
            raise ValidationError(f"Longitude must be between -180 and 180, got {longitude}")

    @staticmethod
    def _build_params(**kwargs) -> dict[str, Any]:
        """Build query parameters, handling lists and None values."""
        params = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, list):
                params[key] = ",".join(str(v) for v in value)
            elif isinstance(value, bool):
                params[key] = str(value).lower()
            else:
                params[key] = str(value)
        return params

    async def _request(
        self,
        endpoint: APIEndpoint,
        params: dict[str, Any],
        base_url: str | None = None,
    ) -> APIResponse:
        """Make API request with retry logic."""
        # Determine base URL
        if "geocoding" in endpoint.value:
            url_base = self.config.geocoding_base_url
        else:
            url_base = self.config.forecast_base_url

        # Build URL
        endpoint_path = endpoint.value.replace("geocoding/", "")
        url = f"{url_base}/{endpoint_path}"

        # Add API key if configured
        if self.config.api_key:
            params["apikey"] = self.config.api_key

        client = await self._get_client()

        for attempt in range(self.config.max_retries):
            try:
                # Rate limiting
                await asyncio.sleep(self.config.rate_limit_delay)

                start_time = asyncio.get_event_loop().time()
                response = await client.get(url, params=params)
                elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000

                # Handle response
                if response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")

                if response.status_code >= 400:
                    error_data = (
                        response.json()
                        if response.headers.get("content-type") == "application/json"
                        else {}
                    )
                    raise APIError(
                        f"API error: {response.status_code}",
                        status_code=response.status_code,
                        response=error_data,
                    )

                return APIResponse(
                    data=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    url=str(response.url),
                    elapsed_ms=elapsed_ms,
                    success=True,
                )

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt == self.config.max_retries - 1:
                    return APIResponse(
                        data={},
                        status_code=0,
                        headers={},
                        url=url,
                        elapsed_ms=0,
                        success=False,
                        error_message=f"Request failed after {self.config.max_retries} attempts: {str(e)}",
                    )
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))

            except RateLimitError:
                if attempt == self.config.max_retries - 1:
                    return APIResponse(
                        data={},
                        status_code=429,
                        headers={},
                        url=url,
                        elapsed_ms=0,
                        success=False,
                        error_message="Rate limit exceeded after retries",
                    )
                await asyncio.sleep(self.config.retry_delay * (attempt + 1) * 2)

        # Should not reach here, but just in case
        return APIResponse(
            data={},
            status_code=0,
            headers={},
            url=url,
            elapsed_ms=0,
            success=False,
            error_message="Unknown error",
        )

    # ==================== Forecast API ====================

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        hourly: list[str] | None = None,
        daily: list[str] | None = None,
        current: list[str] | None = None,
        minutely_15: list[str] | None = None,
        elevation: float | None = None,
        timezone: str | None = None,
        past_days: int | None = None,
        forecast_days: int | None = None,
        models: str | list[str] | None = None,
        temperature_unit: Literal["celsius", "fahrenheit"] = None,
        wind_speed_unit: Literal["kmh", "ms", "mph", "kn"] = None,
        precipitation_unit: Literal["mm", "inch"] = None,
        timeformat: Literal["iso8601", "unixtime"] | None = None,
    ) -> APIResponse:
        """Get weather forecast from the Forecast API."""
        self._validate_coordinates(latitude, longitude)

        params = self._build_params(
            latitude=latitude,
            longitude=longitude,
            hourly=hourly,
            daily=daily,
            current=current,
            minutely_15=minutely_15,
            elevation=elevation,
            timezone=timezone or self.config.default_timezone,
            past_days=past_days,
            forecast_days=forecast_days,
            models=models,
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
            precipitation_unit=precipitation_unit,
            timeformat=timeformat or self.config.default_timeformat,
        )

        return await self._request(APIEndpoint.FORECAST, params)

    # ==================== Historical Weather API ====================

    async def get_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        hourly: list[str] | None = None,
        daily: list[str] | None = None,
        elevation: float | None = None,
        timezone: str | None = None,
        models: str | list[str] | None = None,
        temperature_unit: Literal["celsius", "fahrenheit"] = None,
        wind_speed_unit: Literal["kmh", "ms", "mph", "kn"] = None,
        precipitation_unit: Literal["mm", "inch"] = None,
        timeformat: Literal["iso8601", "unixtime"] | None = None,
    ) -> APIResponse:
        """Get historical weather data."""
        self._validate_coordinates(latitude, longitude)

        params = self._build_params(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            hourly=hourly,
            daily=daily,
            elevation=elevation,
            timezone=timezone or self.config.default_timezone,
            models=models,
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
            precipitation_unit=precipitation_unit,
            timeformat=timeformat or self.config.default_timeformat,
        )

        return await self._request(APIEndpoint.HISTORICAL, params)

    # ==================== Air Quality API ====================

    async def get_air_quality(
        self,
        latitude: float,
        longitude: float,
        hourly: list[str] | None = None,
        current: list[str] | None = None,
        domains: Literal["auto", "cams_europe", "cams_global"] = None,
        timezone: str | None = None,
        past_days: int | None = None,
        forecast_days: int | None = None,
        forecast_hours: int | None = None,
        past_hours: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        start_hour: str | None = None,
        end_hour: str | None = None,
        cell_selection: Literal["nearest", "land", "sea"] = None,
        temperature_unit: Literal["celsius", "fahrenheit"] = None,
        timeformat: Literal["iso8601", "unixtime"] | None = None,
    ) -> APIResponse:
        """Get air quality data."""
        self._validate_coordinates(latitude, longitude)

        params = self._build_params(
            latitude=latitude,
            longitude=longitude,
            hourly=hourly,
            current=current,
            domains=domains,
            timezone=timezone or self.config.default_timezone,
            past_days=past_days,
            forecast_days=forecast_days,
            forecast_hours=forecast_hours,
            past_hours=past_hours,
            start_date=start_date,
            end_date=end_date,
            start_hour=start_hour,
            end_hour=end_hour,
            cell_selection=cell_selection,
            temperature_unit=temperature_unit,
            timeformat=timeformat or self.config.default_timeformat,
        )

        return await self._request(APIEndpoint.AIR_QUALITY, params)

    # ==================== Geocoding API ====================

    async def search_location(
        self,
        name: str,
        count: int | None = None,
        language: str | None = None,
        country_code: str | None = None,
        format: Literal["json", "protobuf"] = None,
    ) -> APIResponse:
        """Search for locations by name."""
        params = self._build_params(
            name=name,
            count=count,
            language=language,
            countryCode=country_code,
            format=format,
        )

        return await self._request(APIEndpoint.GEOCODING_SEARCH, params)

    async def get_location_by_id(
        self,
        location_id: int,
    ) -> APIResponse:
        """Get location details by ID."""
        params = {"id": str(location_id)}
        return await self._request(APIEndpoint.GEOCODING_GET, params)

    # ==================== Ensemble API ====================

    async def get_ensemble(
        self,
        latitude: float,
        longitude: float,
        models: str | list[str],
        hourly: list[str] | None = None,
        daily: list[str] | None = None,
        timezone: str | None = None,
        past_days: int | None = None,
        forecast_days: int | None = None,
        forecast_hours: int | None = None,
        past_hours: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        start_hour: str | None = None,
        end_hour: str | None = None,
        elevation: float | None = None,
        temperature_unit: Literal["celsius", "fahrenheit"] = None,
        wind_speed_unit: Literal["kmh", "ms", "mph", "kn"] = None,
        precipitation_unit: Literal["mm", "inch"] = None,
        timeformat: Literal["iso8601", "unixtime"] | None = None,
        cell_selection: Literal["land", "sea", "nearest"] = None,
    ) -> APIResponse:
        """Get ensemble forecast from multiple models."""
        self._validate_coordinates(latitude, longitude)

        params = self._build_params(
            latitude=latitude,
            longitude=longitude,
            models=models,
            hourly=hourly,
            daily=daily,
            timezone=timezone or self.config.default_timezone,
            past_days=past_days,
            forecast_days=forecast_days,
            forecast_hours=forecast_hours,
            past_hours=past_hours,
            start_date=start_date,
            end_date=end_date,
            start_hour=start_hour,
            end_hour=end_hour,
            elevation=elevation,
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
            precipitation_unit=precipitation_unit,
            timeformat=timeformat or self.config.default_timeformat,
            cell_selection=cell_selection,
        )

        return await self._request(APIEndpoint.ENSEMBLE, params)

    # ==================== Model-Specific APIs ====================

    async def _get_model_forecast(
        self,
        endpoint: APIEndpoint,
        latitude: float,
        longitude: float,
        hourly: list[str] | None = None,
        daily: list[str] | None = None,
        current: list[str] | None = None,
        minutely_15: list[str] | None = None,
        timezone: str | None = None,
        past_days: int | None = None,
        forecast_days: int | None = None,
        elevation: float | None = None,
        temperature_unit: Literal["celsius", "fahrenheit"] = None,
        wind_speed_unit: Literal["kmh", "ms", "mph", "kn"] = None,
        precipitation_unit: Literal["mm", "inch"] = None,
        timeformat: Literal["iso8601", "unixtime"] | None = None,
    ) -> APIResponse:
        """Generic model-specific forecast method."""
        self._validate_coordinates(latitude, longitude)

        params = self._build_params(
            latitude=latitude,
            longitude=longitude,
            hourly=hourly,
            daily=daily,
            current=current,
            minutely_15=minutely_15,
            timezone=timezone or self.config.default_timezone,
            past_days=past_days,
            forecast_days=forecast_days,
            elevation=elevation,
            temperature_unit=temperature_unit,
            wind_speed_unit=wind_speed_unit,
            precipitation_unit=precipitation_unit,
            timeformat=timeformat or self.config.default_timeformat,
        )

        return await self._request(endpoint, params)

    async def get_ecmwf(self, latitude: float, longitude: float, **kwargs) -> APIResponse:
        """Get ECMWF forecast."""
        return await self._get_model_forecast(APIEndpoint.ECMWF, latitude, longitude, **kwargs)

    async def get_gfs(self, latitude: float, longitude: float, **kwargs) -> APIResponse:
        """Get GFS forecast."""
        return await self._get_model_forecast(APIEndpoint.GFS, latitude, longitude, **kwargs)

    async def get_gfs_hrrr(self, latitude: float, longitude: float, **kwargs) -> APIResponse:
        """Get GFS-HRRR forecast."""
        return await self._get_model_forecast(APIEndpoint.GFS_HRRR, latitude, longitude, **kwargs)

    async def get_meteo_france(self, latitude: float, longitude: float, **kwargs) -> APIResponse:
        """Get Météo-France forecast."""
        return await self._get_model_forecast(
            APIEndpoint.METEO_FRANCE, latitude, longitude, **kwargs
        )

    async def get_dwd_icon(self, latitude: float, longitude: float, **kwargs) -> APIResponse:
        """Get DWD ICON forecast."""
        return await self._get_model_forecast(APIEndpoint.DWD_ICON, latitude, longitude, **kwargs)

    async def get_gem(self, latitude: float, longitude: float, **kwargs) -> APIResponse:
        """Get GEM (Canada) forecast."""
        return await self._get_model_forecast(APIEndpoint.GEM, latitude, longitude, **kwargs)

    async def get_jma(self, latitude: float, longitude: float, **kwargs) -> APIResponse:
        """Get JMA (Japan) forecast."""
        return await self._get_model_forecast(APIEndpoint.JMA, latitude, longitude, **kwargs)

    async def get_met_norway(self, latitude: float, longitude: float, **kwargs) -> APIResponse:
        """Get Met Norway forecast."""
        return await self._get_model_forecast(APIEndpoint.MET_NORWAY, latitude, longitude, **kwargs)

    # ==================== Specialized APIs ====================

    async def get_marine(
        self,
        latitude: float,
        longitude: float,
        hourly: list[str] | None = None,
        daily: list[str] | None = None,
        timezone: str | None = None,
        past_days: int | None = None,
        forecast_days: int | None = None,
        models: str | list[str] | None = None,
        timeformat: Literal["iso8601", "unixtime"] | None = None,
    ) -> APIResponse:
        """Get marine weather forecast."""
        self._validate_coordinates(latitude, longitude)

        params = self._build_params(
            latitude=latitude,
            longitude=longitude,
            hourly=hourly,
            daily=daily,
            timezone=timezone or self.config.default_timezone,
            past_days=past_days,
            forecast_days=forecast_days,
            models=models,
            timeformat=timeformat or self.config.default_timeformat,
        )

        return await self._request(APIEndpoint.MARINE, params)

    async def get_elevation(
        self,
        latitude: float,
        longitude: float,
    ) -> APIResponse:
        """Get elevation data for coordinates."""
        self._validate_coordinates(latitude, longitude)

        params = {"lat": latitude, "lon": longitude}
        return await self._request(APIEndpoint.ELEVATION, params)

    async def get_climate(
        self,
        latitude: float,
        longitude: float,
        start_date: str | None = None,
        end_date: str | None = None,
        daily: list[str] | None = None,
        timezone: str | None = None,
        timeformat: Literal["iso8601", "unixtime"] | None = None,
    ) -> APIResponse:
        """Get climate data."""
        self._validate_coordinates(latitude, longitude)

        params = self._build_params(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            daily=daily,
            timezone=timezone or self.config.default_timezone,
            timeformat=timeformat or self.config.default_timeformat,
        )

        return await self._request(APIEndpoint.CLIMATE, params)


# Convenience function for quick client creation
def create_client(
    api_key: str | None = None,
    timeout: float = 30.0,
    timezone: str = "GMT",
) -> OpenMeteoClient:
    """Create an Open-Meteo client with basic configuration."""
    config = ClientConfig(
        api_key=api_key,
        timeout=timeout,
        default_timezone=timezone,
    )
    return OpenMeteoClient(config)
