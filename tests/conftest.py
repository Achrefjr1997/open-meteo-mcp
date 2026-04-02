"""
Pytest Fixtures for Open-Meteo MCP Server Tests.

Provides shared fixtures for client, server, and tool tests.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator

from src.client import OpenMeteoClient, ClientConfig
from src.server import create_app, create_client_from_env


# ==================== Client Fixtures ====================

@pytest.fixture
def client_config() -> ClientConfig:
    """Create a test client configuration."""
    return ClientConfig(
        timeout=30.0,
        max_retries=2,
        retry_delay=0.5,
        rate_limit_delay=0.2,  # Slightly longer for tests
        default_timezone="GMT",
    )


@pytest_asyncio.fixture
async def client(client_config: ClientConfig) -> AsyncGenerator[OpenMeteoClient, None]:
    """Create an async Open-Meteo client for tests."""
    client = OpenMeteoClient(client_config)
    try:
        yield client
    finally:
        await client.close()


@pytest_asyncio.fixture
async def client_with_api_defaults() -> AsyncGenerator[OpenMeteoClient, None]:
    """Create a client with default API settings."""
    client = create_client_from_env()
    try:
        yield client
    finally:
        await client.close()


# ==================== Server Fixtures ====================

@pytest.fixture
def mcp_server():
    """Create an MCP server instance."""
    return create_app()


# ==================== Coordinate Fixtures ====================

@pytest.fixture
def london_coordinates() -> tuple[float, float]:
    """London, UK coordinates."""
    return (51.5074, -0.1278)


@pytest.fixture
def paris_coordinates() -> tuple[float, float]:
    """Paris, France coordinates."""
    return (48.8566, 2.3522)


@pytest.fixture
def new_york_coordinates() -> tuple[float, float]:
    """New York, USA coordinates."""
    return (40.7128, -74.0060)


@pytest.fixture
def tokyo_coordinates() -> tuple[float, float]:
    """Tokyo, Japan coordinates."""
    return (35.6762, 139.6503)


@pytest.fixture
def sydney_coordinates() -> tuple[float, float]:
    """Sydney, Australia coordinates."""
    return (-33.8688, 151.2093)


@pytest.fixture
def invalid_coordinates() -> tuple[float, float]:
    """Invalid coordinates for error testing."""
    return (91.0, 181.0)  # Out of range


# ==================== Date Fixtures ====================

@pytest.fixture
def sample_date_range() -> tuple[str, str]:
    """Sample date range for historical tests."""
    return ("2024-01-01", "2024-01-07")


@pytest.fixture
def sample_single_date() -> str:
    """Sample single date."""
    return "2024-06-15"


# ==================== Weather Variable Fixtures ====================

@pytest.fixture
def common_weather_variables() -> list[str]:
    """Common weather variables for testing."""
    return [
        "temperature_2m",
        "relative_humidity_2m",
        "weather_code",
        "wind_speed_10m",
        "precipitation",
    ]


@pytest.fixture
def hourly_weather_variables() -> list[str]:
    """Hourly weather variables for testing."""
    return [
        "temperature_2m",
        "relative_humidity_2m",
        "weather_code",
        "wind_speed_10m",
        "wind_direction_10m",
        "precipitation",
        "cloud_cover",
    ]


@pytest.fixture
def daily_weather_variables() -> list[str]:
    """Daily weather variables for testing."""
    return [
        "temperature_2m_max",
        "temperature_2m_min",
        "sunrise",
        "sunset",
        "precipitation_sum",
        "weather_code",
    ]


@pytest.fixture
def air_quality_variables() -> list[str]:
    """Air quality variables for testing."""
    return [
        "pm10",
        "pm2_5",
        "ozone",
        "nitrogen_dioxide",
        "carbon_monoxide",
    ]


@pytest.fixture
def marine_variables() -> list[str]:
    """Marine weather variables for testing."""
    return [
        "wave_height",
        "wave_period",
        "wave_direction",
        "water_temperature",
    ]


# ==================== Helper Fixtures ====================

@pytest.fixture
def sample_location_name() -> str:
    """Sample location name for geocoding tests."""
    return "London"


@pytest.fixture
def sample_country_code() -> str:
    """Sample country code for geocoding tests."""
    return "GB"


@pytest.fixture
def sample_location_id() -> int:
    """Sample location ID (London)."""
    return 524901  # Open-Meteo geocoding ID for London, UK


# ==================== Async Test Helpers ====================

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
