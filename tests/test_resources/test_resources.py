"""
Tests for Open-Meteo MCP Resources.

Tests the resources module including:
- Variable resources (weather://variables/*)
- Model resources (weather://models/*)
- Resource registration
- Resource content validation
"""

from mcp.server.fastmcp import FastMCP

from src.resources import variables as variables_resources, models as models_resources


# ==================== Resource Registration Tests ====================

class TestResourceRegistration:
    """Tests for resource registration with MCP server."""

    def test_register_variable_resources(self):
        """Test variable resources registration."""
        mcp = FastMCP(name="test")
        
        # Should not raise
        variables_resources.register_variable_resources(mcp)

    def test_register_model_resources(self):
        """Test model resources registration."""
        mcp = FastMCP(name="test")
        
        # Should not raise
        models_resources.register_model_resources(mcp)


# ==================== Variable Resource Tests ====================

class TestVariableResources:
    """Tests for weather variable resources."""

    def test_variables_module_has_register_function(self):
        """Test variables module has register function."""
        assert hasattr(variables_resources, "register_variable_resources")

    def test_variable_categories_defined(self):
        """Test that variable categories are defined."""
        assert hasattr(variables_resources, "_CATEGORIES")
        assert hasattr(variables_resources, "_VARIABLES")
        
        # Check categories exist
        categories = variables_resources._CATEGORIES
        assert "temperature" in categories
        assert "wind" in categories
        assert "precipitation" in categories
        assert "clouds" in categories
        assert "pressure" in categories
        assert "humidity" in categories
        assert "solar" in categories
        assert "soil" in categories
        assert "air_quality" in categories
        assert "marine" in categories

    def test_weather_codes_defined(self):
        """Test that weather codes are defined."""
        assert hasattr(variables_resources, "_WEATHER_CODES")
        
        weather_codes = variables_resources._WEATHER_CODES
        assert "0" in weather_codes  # Clear sky
        assert "61" in weather_codes  # Rain
        assert "95" in weather_codes  # Thunderstorm

    def test_filter_by_category(self):
        """Test filtering variables by category."""
        # Test temperature category
        temp_vars = variables_resources._filter_by_category("temperature")
        assert len(temp_vars) > 0
        assert "temperature_2m" in temp_vars
        
        # Test wind category
        wind_vars = variables_resources._filter_by_category("wind")
        assert len(wind_vars) > 0
        assert "wind_speed_10m" in wind_vars
        
        # Test air_quality category
        aq_vars = variables_resources._filter_by_category("air_quality")
        assert len(aq_vars) > 0
        assert "pm2_5" in aq_vars

    def test_variable_count(self):
        """Test expected number of variables."""
        variables = variables_resources._VARIABLES
        assert len(variables) > 50  # Should have many variables


# ==================== Model Resource Tests ====================

class TestModelResources:
    """Tests for weather model resources."""

    def test_models_module_has_register_function(self):
        """Test models module has register function."""
        assert hasattr(models_resources, "register_model_resources")

    def test_model_providers_defined(self):
        """Test that model providers are defined."""
        assert hasattr(models_resources, "_PROVIDERS")
        
        providers = models_resources._PROVIDERS
        assert "ECMWF" in providers
        assert "NOAA" in providers
        assert "DWD" in providers
        assert "Météo-France" in providers
        assert "UK Met Office" in providers
        assert "Met Norway" in providers
        assert "ECCC" in providers
        assert "JMA" in providers

    def test_models_defined(self):
        """Test that weather models are defined."""
        assert hasattr(models_resources, "_MODELS")
        
        models = models_resources._MODELS
        assert "ecmwf_ifs04" in models
        assert "gfs_global" in models
        assert "icon_global" in models

    def test_filter_by_provider(self):
        """Test filtering models by provider."""
        # Test ECMWF models
        ecmwf_models = models_resources._filter_by_provider("ECMWF")
        assert len(ecmwf_models) > 0
        assert "ecmwf_ifs04" in ecmwf_models
        
        # Test NOAA models
        noaa_models = models_resources._filter_by_provider("NOAA")
        assert len(noaa_models) > 0
        assert "gfs_global" in noaa_models

    def test_filter_by_type(self):
        """Test filtering models by type."""
        ensemble_models = models_resources._filter_by_type("ensemble")
        assert len(ensemble_models) > 0

    def test_model_count(self):
        """Test expected number of models."""
        models = models_resources._MODELS
        assert len(models) > 20  # Should have many models


# ==================== Resource Content Tests ====================

class TestResourceContent:
    """Tests for resource content validation."""

    def test_variable_has_required_fields(self):
        """Test that variables have required fields."""
        variables = variables_resources._VARIABLES
        
        for name, info in variables.items():
            assert "description" in info
            assert "category" in info

    def test_model_has_required_fields(self):
        """Test that models have required fields."""
        models = models_resources._MODELS
        
        for model_id, info in models.items():
            assert "provider" in info
            assert "name" in info
            assert "description" in info
            assert "resolution_km" in info
            assert "coverage" in info


# ==================== Resource Integration Tests ====================

class TestResourceIntegration:
    """Integration tests for resources."""

    def test_all_resources_register_on_server(self):
        """Test that all resources register correctly on a server."""
        mcp = FastMCP(name="test-resources")
        
        # Register all resources
        variables_resources.register_variable_resources(mcp)
        models_resources.register_model_resources(mcp)
        
        # Should complete without errors

    def test_resources_use_fastmcp_resource_decorator(self):
        """Test that resources use the FastMCP resource decorator."""
        import inspect
        
        var_source = inspect.getsource(variables_resources)
        model_source = inspect.getsource(models_resources)
        
        # Should use @mcp.resource() decorator
        assert "@mcp.resource" in var_source
        assert "@mcp.resource" in model_source


# ==================== Resource URI Pattern Tests ====================

class TestResourceURIPatterns:
    """Tests for resource URI patterns."""

    def test_variable_uri_pattern(self):
        """Test variable resource URI pattern."""
        import inspect
        source = inspect.getsource(variables_resources)
        
        # Check for URI patterns
        assert 'weather://variables/all' in source
        assert 'weather://variables/temperature' in source
        assert 'weather://variables/wind' in source
        assert 'weather://variables/precipitation' in source

    def test_model_uri_pattern(self):
        """Test model resource URI pattern."""
        import inspect
        source = inspect.getsource(models_resources)
        
        # Check for URI patterns
        assert 'weather://models/all' in source
        assert 'weather://models/ecmwf' in source
        assert 'weather://models/noaa' in source
        assert 'weather://models/dwd' in source
