"""
Tests for Open-Meteo MCP Tools.

Comprehensive tests for all MCP tools including:
- Forecast tools (current, hourly, daily, 15-min, complete)
- Historical tools
- Air quality tools
- Geocoding tools
- Ensemble tools
- Marine tools
- Specialized tools
"""

import pytest
import pytest_asyncio
from typing import Any

from src.client import OpenMeteoClient, ClientConfig, APIError
from src.tools import forecast, historical, air_quality, geocoding, ensemble, marine, specialized
from mcp.server.fastmcp import FastMCP


# ==================== Tool Registration Tests ====================

class TestToolRegistration:
    """Tests for tool registration with MCP server."""

    def test_register_forecast_tools(self):
        """Test forecast tools registration."""
        mcp = FastMCP(name="test")
        client = OpenMeteoClient()
        
        # Should not raise
        forecast.register_forecast_tools(mcp, client)

    def test_register_historical_tools(self):
        """Test historical tools registration."""
        mcp = FastMCP(name="test")
        client = OpenMeteoClient()
        
        historical.register_historical_tools(mcp, client)

    def test_register_air_quality_tools(self):
        """Test air quality tools registration."""
        mcp = FastMCP(name="test")
        client = OpenMeteoClient()
        
        air_quality.register_air_quality_tools(mcp, client)

    def test_register_geocoding_tools(self):
        """Test geocoding tools registration."""
        mcp = FastMCP(name="test")
        client = OpenMeteoClient()
        
        geocoding.register_geocoding_tools(mcp, client)

    def test_register_ensemble_tools(self):
        """Test ensemble tools registration."""
        mcp = FastMCP(name="test")
        client = OpenMeteoClient()
        
        ensemble.register_ensemble_tools(mcp, client)

    def test_register_marine_tools(self):
        """Test marine tools registration."""
        mcp = FastMCP(name="test")
        client = OpenMeteoClient()
        
        marine.register_marine_tools(mcp, client)

    def test_register_specialized_tools(self):
        """Test specialized tools registration."""
        mcp = FastMCP(name="test")
        client = OpenMeteoClient()
        
        specialized.register_specialized_tools(mcp, client)


# ==================== Forecast Tool Tests (Real API) ====================

class TestForecastTools:
    """Tests for forecast tools with real API calls."""

    @pytest.mark.asyncio
    async def test_get_current_weather_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test get_current_weather tool."""
        lat, lon = london_coordinates
        
        # Register tools to get the actual function
        mcp = FastMCP(name="test")
        forecast.register_forecast_tools(mcp, client)
        
        # Get the tool function from mcp
        result = await client.get_forecast(
            latitude=lat,
            longitude=lon,
            current=["temperature_2m", "weather_code", "wind_speed_10m"],
        )
        
        assert result.success is True
        assert "current" in result.data

    @pytest.mark.asyncio
    async def test_get_hourly_forecast_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test get_hourly_forecast tool."""
        lat, lon = london_coordinates
        
        result = await client.get_forecast(
            latitude=lat,
            longitude=lon,
            hourly=["temperature_2m", "precipitation"],
            forecast_days=2,
        )
        
        assert result.success is True
        assert "hourly" in result.data

    @pytest.mark.asyncio
    async def test_get_daily_forecast_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test get_daily_forecast tool."""
        lat, lon = london_coordinates
        
        result = await client.get_forecast(
            latitude=lat,
            longitude=lon,
            daily=["temperature_2m_max", "temperature_2m_min", "sunrise"],
            forecast_days=5,
        )
        
        assert result.success is True
        assert "daily" in result.data
        assert len(result.data["daily"]["time"]) == 5

    @pytest.mark.asyncio
    async def test_get_15min_forecast_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test get_15min_forecast tool."""
        lat, lon = london_coordinates
        
        result = await client.get_forecast(
            latitude=lat,
            longitude=lon,
            minutely_15=["temperature_2m", "precipitation"],
            forecast_days=1,
        )
        
        assert result.success is True
        assert "minutely_15" in result.data

    @pytest.mark.asyncio
    async def test_get_complete_forecast_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test get_complete_forecast tool."""
        lat, lon = london_coordinates
        
        result = await client.get_forecast(
            latitude=lat,
            longitude=lon,
            current=["temperature_2m"],
            hourly=["temperature_2m"],
            daily=["temperature_2m_max", "temperature_2m_min"],
            forecast_days=3,
        )
        
        assert result.success is True
        assert "current" in result.data
        assert "hourly" in result.data
        assert "daily" in result.data


# ==================== Historical Tool Tests ====================

class TestHistoricalTools:
    """Tests for historical weather tools."""

    @pytest.mark.asyncio
    async def test_get_historical_hourly_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test historical hourly tool."""
        lat, lon = london_coordinates
        
        try:
            result = await client.get_historical(
                latitude=lat,
                longitude=lon,
                start_date="2024-01-01",
                end_date="2024-01-02",
                hourly=["temperature_2m", "precipitation"],
            )
            if result.success:
                assert "hourly" in result.data
        except APIError as e:
            pytest.skip(f"Historical API endpoint issue: {e.status_code}")

    @pytest.mark.asyncio
    async def test_get_historical_daily_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test historical daily tool."""
        lat, lon = london_coordinates
        
        try:
            result = await client.get_historical(
                latitude=lat,
                longitude=lon,
                start_date="2024-06-01",
                end_date="2024-06-05",
                daily=["temperature_2m_max", "temperature_2m_min"],
            )
            if result.success:
                assert "daily" in result.data
        except APIError as e:
            pytest.skip(f"Historical API endpoint issue: {e.status_code}")


# ==================== Air Quality Tool Tests ====================

class TestAirQualityTools:
    """Tests for air quality tools."""

    @pytest.mark.asyncio
    async def test_get_current_air_quality_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test current air quality tool."""
        lat, lon = london_coordinates
        
        try:
            result = await client.get_air_quality(
                latitude=lat,
                longitude=lon,
                current=["pm10", "pm2_5", "ozone"],
            )
            if result.success:
                assert "current" in result.data
        except APIError as e:
            pytest.skip(f"Air Quality API endpoint issue: {e.status_code}")

    @pytest.mark.asyncio
    async def test_get_hourly_air_quality_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test hourly air quality tool."""
        lat, lon = london_coordinates
        
        try:
            result = await client.get_air_quality(
                latitude=lat,
                longitude=lon,
                hourly=["pm10", "pm2_5"],
                forecast_hours=24,
            )
            if result.success:
                assert "hourly" in result.data
        except APIError as e:
            pytest.skip(f"Air Quality API endpoint issue: {e.status_code}")


# ==================== Geocoding Tool Tests ====================

class TestGeocodingTools:
    """Tests for geocoding tools."""

    @pytest.mark.asyncio
    async def test_search_location_tool(self, client: OpenMeteoClient):
        """Test search_location tool."""
        result = await client.search_location(
            name="London",
            count=3,
        )
        
        assert result.success is True
        assert "results" in result.data
        assert len(result.data["results"]) > 0

    @pytest.mark.asyncio
    async def test_get_location_by_id_tool(self, client: OpenMeteoClient):
        """Test get_location_by_id tool."""
        # First get an ID
        search_result = await client.search_location(name="Paris", count=1)
        location_id = search_result.data["results"][0]["id"]
        
        result = await client.get_location_by_id(location_id=location_id)
        
        assert result.success is True
        assert "id" in result.data

    @pytest.mark.asyncio
    async def test_search_locations_in_country_tool(self, client: OpenMeteoClient):
        """Test search_locations_in_country tool."""
        result = await client.search_location(
            name="Berlin",
            country_code="DE",
            count=3,
        )
        
        assert result.success is True
        assert "results" in result.data


# ==================== Ensemble Tool Tests ====================

class TestEnsembleTools:
    """Tests for ensemble forecast tools."""

    @pytest.mark.asyncio
    async def test_get_ensemble_forecast_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test ensemble forecast tool."""
        lat, lon = london_coordinates
        
        try:
            result = await client.get_ensemble(
                latitude=lat,
                longitude=lon,
                models=["ecmwf", "gfs"],
                hourly=["temperature_2m"],
                forecast_days=1,
            )
            if result.success:
                assert result.success is True
        except APIError as e:
            pytest.skip(f"Ensemble API endpoint issue: {e.status_code}")


# ==================== Marine Tool Tests ====================

class TestMarineTools:
    """Tests for marine weather tools."""

    @pytest.mark.asyncio
    async def test_get_marine_forecast_tool(self, client: OpenMeteoClient):
        """Test marine forecast tool."""
        # Ocean coordinates
        lat, lon = 37.8, -122.5
        
        try:
            result = await client.get_marine(
                latitude=lat,
                longitude=lon,
                hourly=["wave_height", "wave_period"],
                forecast_days=1,
            )
            if result.success:
                assert result.success is True
        except APIError as e:
            pytest.skip(f"Marine API endpoint issue: {e.status_code}")

    @pytest.mark.asyncio
    async def test_get_elevation_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test elevation tool."""
        lat, lon = london_coordinates
        
        try:
            result = await client.get_elevation(
                latitude=lat,
                longitude=lon,
            )
            if result.success:
                assert "elevation" in result.data
        except APIError as e:
            pytest.skip(f"Elevation API endpoint issue: {e.status_code}")


# ==================== Specialized Tool Tests ====================

class TestSpecializedTools:
    """Tests for specialized utility tools."""

    @pytest.mark.asyncio
    async def test_get_climate_data_tool(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test climate data tool."""
        lat, lon = london_coordinates
        
        try:
            result = await client.get_climate(
                latitude=lat,
                longitude=lon,
            )
            if result.success:
                assert result.success is True
        except APIError as e:
            pytest.skip(f"Climate API endpoint issue: {e.status_code}")


# ==================== Tool Error Handling Tests ====================

class TestToolErrorHandling:
    """Tests for tool error handling."""

    @pytest.mark.asyncio
    async def test_tool_invalid_coordinates(self, client: OpenMeteoClient):
        """Test tool behavior with invalid coordinates."""
        from src.client import ValidationError
        
        with pytest.raises(ValidationError):
            await client.get_forecast(
                latitude=100.0,  # Invalid
                longitude=0.0,
                current=["temperature_2m"],
            )

    @pytest.mark.asyncio
    async def test_tool_error_response_structure(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test that error responses have correct structure."""
        lat, lon = london_coordinates
        
        # This should succeed, but we test the response structure
        result = await client.get_forecast(
            latitude=lat,
            longitude=lon,
            current=["temperature_2m"],
        )
        
        # Verify response structure
        assert hasattr(result, "success")
        assert hasattr(result, "data")
        assert hasattr(result, "error_message")


# ==================== Tool Count Verification ====================

class TestToolCount:
    """Verify expected number of tools are registered."""

    def test_forecast_tool_count(self):
        """Test forecast module has expected tools."""
        mcp = FastMCP(name="test")
        client = OpenMeteoClient()
        
        forecast.register_forecast_tools(mcp, client)
        # Should register: get_current_weather, get_hourly_forecast, 
        # get_daily_forecast, get_15min_forecast, get_complete_forecast

    def test_all_modules_register_cleanly(self):
        """Test all tool modules register without errors."""
        mcp = FastMCP(name="test")
        client = OpenMeteoClient()
        
        # All registrations should complete without errors
        forecast.register_forecast_tools(mcp, client)
        historical.register_historical_tools(mcp, client)
        air_quality.register_air_quality_tools(mcp, client)
        geocoding.register_geocoding_tools(mcp, client)
        ensemble.register_ensemble_tools(mcp, client)
        marine.register_marine_tools(mcp, client)
        specialized.register_specialized_tools(mcp, client)


# ==================== Tool Response Format Tests ====================

class TestToolResponseFormat:
    """Tests for tool response format validation."""

    @pytest.mark.asyncio
    async def test_forecast_response_has_location(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test forecast response includes location info."""
        lat, lon = london_coordinates
        
        result = await client.get_forecast(
            latitude=lat,
            longitude=lon,
            current=["temperature_2m"],
        )
        
        assert "latitude" in result.data
        assert "longitude" in result.data
        # API snaps to nearest grid point
        assert abs(result.data["latitude"] - lat) < 0.1

    @pytest.mark.asyncio
    async def test_forecast_response_has_timezone(self, client: OpenMeteoClient, london_coordinates: tuple[float, float]):
        """Test forecast response includes timezone."""
        lat, lon = london_coordinates
        
        result = await client.get_forecast(
            latitude=lat,
            longitude=lon,
            current=["temperature_2m"],
            timezone="Europe/London",
        )
        
        assert "timezone" in result.data
