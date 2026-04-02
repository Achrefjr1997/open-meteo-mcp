"""
Tests for Open-Meteo MCP Server.

Tests the server.py module including:
- Server creation and configuration
- Tool registration
- Resource registration
- Prompt registration
- Client creation from environment
"""

import os
from unittest.mock import patch, MagicMock

from mcp.server.fastmcp import FastMCP

from src.server import (
    SERVER_NAME,
    SERVER_VERSION,
    SERVER_DESCRIPTION,
    create_client_from_env,
    create_mcp_server,
    register_all_tools,
    register_all_resources,
    register_all_prompts,
    create_app,
    main,
    run_stdio,
    run_sse,
)
from src.client import OpenMeteoClient


# ==================== Server Configuration Tests ====================

class TestServerConfiguration:
    """Tests for server configuration constants."""

    def test_server_name(self):
        """Test server name is set correctly."""
        assert SERVER_NAME == "open-meteo-mcp"

    def test_server_version(self):
        """Test server version is set correctly."""
        assert SERVER_VERSION == "0.1.0"

    def test_server_description(self):
        """Test server description contains key features."""
        assert "MCP Server" in SERVER_DESCRIPTION
        assert "Open-Meteo" in SERVER_DESCRIPTION
        assert "weather" in SERVER_DESCRIPTION.lower()


# ==================== Client Creation Tests ====================

class TestClientCreation:
    """Tests for client creation functions."""

    def test_create_client_from_env_defaults(self):
        """Test client creation with default environment."""
        # Ensure no env vars are set
        with patch.dict(os.environ, {}, clear=True):
            client = create_client_from_env()
            
            assert isinstance(client, OpenMeteoClient)
            assert client.config.api_key is None
            assert client.config.timeout == 30.0
            assert client.config.default_timezone == "GMT"
            assert client.config.rate_limit_delay == 0.1

    def test_create_client_from_env_with_api_key(self):
        """Test client creation with API key in environment."""
        with patch.dict(os.environ, {"OPEN_METEO_API_KEY": "test_key_123"}):
            client = create_client_from_env()
            
            assert client.config.api_key == "test_key_123"

    def test_create_client_from_env_custom_timeout(self):
        """Test client creation with custom timeout."""
        with patch.dict(os.environ, {"OPEN_METEO_TIMEOUT": "60.0"}):
            client = create_client_from_env()
            
            assert client.config.timeout == 60.0

    def test_create_client_from_env_custom_timezone(self):
        """Test client creation with custom timezone."""
        with patch.dict(os.environ, {"OPEN_METEO_TIMEZONE": "Europe/London"}):
            client = create_client_from_env()
            
            assert client.config.default_timezone == "Europe/London"

    def test_create_client_from_env_custom_rate_limit(self):
        """Test client creation with custom rate limit."""
        with patch.dict(os.environ, {"OPEN_METEO_RATE_LIMIT": "0.5"}):
            client = create_client_from_env()
            
            assert client.config.rate_limit_delay == 0.5

    def test_create_client_from_env_all_settings(self):
        """Test client creation with all environment settings."""
        env_vars = {
            "OPEN_METEO_API_KEY": "my_key",
            "OPEN_METEO_TIMEOUT": "45.0",
            "OPEN_METEO_TIMEZONE": "America/New_York",
            "OPEN_METEO_RATE_LIMIT": "0.3",
        }
        
        with patch.dict(os.environ, env_vars):
            client = create_client_from_env()
            
            assert client.config.api_key == "my_key"
            assert client.config.timeout == 45.0
            assert client.config.default_timezone == "America/New_York"
            assert client.config.rate_limit_delay == 0.3


# ==================== MCP Server Creation Tests ====================

class TestMCPServerCreation:
    """Tests for MCP server creation."""

    def test_create_mcp_server(self):
        """Test MCP server creation."""
        mcp = create_mcp_server()
        
        assert isinstance(mcp, FastMCP)
        assert mcp.name == SERVER_NAME


# ==================== Tool Registration Tests ====================

class TestToolRegistration:
    """Tests for tool registration."""

    def test_register_all_tools(self):
        """Test that all tool modules are registered."""
        mcp = create_mcp_server()
        client = OpenMeteoClient()
        
        # Should not raise
        register_all_tools(mcp, client)
        
        # Verify tools are registered by checking the server has tools
        # Note: FastMCP doesn't expose a direct tool list, but we can verify
        # the registration completed without errors


# ==================== Resource Registration Tests ====================

class TestResourceRegistration:
    """Tests for resource registration."""

    def test_register_all_resources(self):
        """Test that all resource modules are registered."""
        mcp = create_mcp_server()
        
        # Should not raise
        register_all_resources(mcp)


# ==================== Prompt Registration Tests ====================

class TestPromptRegistration:
    """Tests for prompt registration."""

    def test_register_all_prompts(self):
        """Test that all prompt modules are registered."""
        mcp = create_mcp_server()
        
        # Should not raise
        register_all_prompts(mcp)


# ==================== Full App Creation Tests ====================

class TestAppCreation:
    """Tests for full application creation."""

    def test_create_app(self):
        """Test complete app creation with all components."""
        with patch.dict(os.environ, {}, clear=True):
            app = create_app()
            
            assert isinstance(app, FastMCP)
            assert app.name == SERVER_NAME

    def test_create_app_with_env_vars(self):
        """Test app creation with environment variables."""
        env_vars = {
            "OPEN_METEO_API_KEY": "test_key",
            "OPEN_METEO_TIMEOUT": "45.0",
            "OPEN_METEO_TIMEZONE": "Asia/Tokyo",
        }
        
        with patch.dict(os.environ, env_vars):
            app = create_app()
            
            assert isinstance(app, FastMCP)


# ==================== Server Transport Tests ====================

class TestServerTransport:
    """Tests for server transport modes."""

    def test_run_stdio_exists(self):
        """Test that run_stdio function exists."""
        assert callable(run_stdio)

    def test_run_sse_exists(self):
        """Test that run_sse function exists."""
        assert callable(run_sse)

    def test_run_sse_default_params(self):
        """Test run_sse with default parameters."""
        # We can't actually run the server in tests, but we can verify
        # the function signature and defaults
        import inspect
        sig = inspect.signature(run_sse)
        
        # Check default parameters
        assert sig.parameters["host"].default == "0.0.0.0"
        assert sig.parameters["port"].default == 8000


# ==================== Integration Tests ====================

class TestServerIntegration:
    """Integration tests for the complete server."""

    def test_full_server_setup(self):
        """Test complete server setup from scratch."""
        # Create app
        app = create_app()
        
        # Verify it's a valid FastMCP instance
        assert app is not None
        assert isinstance(app, FastMCP)
        
        # Verify name
        assert app.name == "open-meteo-mcp"

    def test_server_with_mock_client(self):
        """Test server creation with mocked client."""
        with patch("src.server.create_client_from_env") as mock_create:
            mock_client = MagicMock(spec=OpenMeteoClient)
            mock_create.return_value = mock_client
            
            app = create_app()
            
            assert isinstance(app, FastMCP)
            mock_create.assert_called_once()


# ==================== CLI Entry Point Tests ====================

class TestCLIEntryPoint:
    """Tests for CLI entry points."""

    def test_main_function_exists(self):
        """Test that main function exists."""
        assert callable(main)

    def test_server_module_has_run_method(self):
        """Test that server module structure is correct."""
        from src import server
        
        # Verify key functions exist
        assert hasattr(server, "create_app")
        assert hasattr(server, "create_mcp_server")
        assert hasattr(server, "register_all_tools")
        assert hasattr(server, "register_all_resources")
        assert hasattr(server, "register_all_prompts")


# ==================== Server Instructions Tests ====================

class TestServerInstructions:
    """Tests for server instructions and documentation."""

    def test_description_mentions_features(self):
        """Test that server description mentions key features."""
        description_lower = SERVER_DESCRIPTION.lower()
        
        # Check for key feature mentions
        assert "current" in description_lower or "forecast" in description_lower
        assert "historical" in description_lower
        assert "air quality" in description_lower
        assert "marine" in description_lower
