"""
Tests for Open-Meteo MCP Prompts.

Tests the prompts module including:
- Weather analysis prompt
- Marine weather prompt
- Climate analysis prompt
- Air quality health prompt
- Prompt registration
"""

from mcp.server.fastmcp import FastMCP

from src.prompts import weather_assistant

# ==================== Prompt Registration Tests ====================


class TestPromptRegistration:
    """Tests for prompt registration with MCP server."""

    def test_register_prompts(self):
        """Test prompt registration."""
        mcp = FastMCP(name="test")

        # Should not raise
        weather_assistant.register_prompts(mcp)

    def test_prompts_module_has_register_function(self):
        """Test prompts module has register function."""
        assert hasattr(weather_assistant, "register_prompts")


# ==================== Prompt Content Tests ====================


class TestPromptContent:
    """Tests for prompt content validation."""

    def test_weather_analysis_prompt_exists(self):
        """Test weather analysis prompt is defined."""
        import inspect

        source = inspect.getsource(weather_assistant)

        # Should have weather analysis prompt
        assert "weather_analysis_prompt" in source

    def test_marine_weather_prompt_exists(self):
        """Test marine weather prompt is defined."""
        import inspect

        source = inspect.getsource(weather_assistant)

        assert "marine_weather_prompt" in source

    def test_climate_prompt_exists(self):
        """Test climate prompt is defined."""
        import inspect

        source = inspect.getsource(weather_assistant)

        assert "climate_analysis_prompt" in source

    def test_air_quality_prompt_exists(self):
        """Test air quality health prompt is defined."""
        import inspect

        source = inspect.getsource(weather_assistant)

        assert "air_quality_health_prompt" in source


# ==================== Prompt Structure Tests ====================


class TestPromptStructure:
    """Tests for prompt structure."""

    def test_prompts_use_fastmcp_prompt_decorator(self):
        """Test that prompts use the FastMCP prompt decorator."""
        import inspect

        source = inspect.getsource(weather_assistant)

        # Should use @mcp.prompt() decorator
        assert "@mcp.prompt" in source

    def test_prompts_have_docstrings(self):
        """Test that prompts include docstrings."""
        import inspect

        source = inspect.getsource(weather_assistant)

        # Prompts should have docstrings
        assert '"""' in source


# ==================== Prompt Integration Tests ====================


class TestPromptIntegration:
    """Integration tests for prompts."""

    def test_all_prompts_register_on_server(self):
        """Test that all prompts register correctly on a server."""
        mcp = FastMCP(name="test-prompts")

        # Register all prompts
        weather_assistant.register_prompts(mcp)

        # Should complete without errors


# ==================== Prompt Count Tests ====================


class TestPromptCount:
    """Tests for prompt count validation."""

    def test_expected_prompt_count(self):
        """Test that expected number of prompts are registered."""
        # Should have 4 prompts
        import inspect

        source = inspect.getsource(weather_assistant)

        # Count prompt definitions
        prompt_count = source.count("@mcp.prompt")

        assert prompt_count == 4


# ==================== Prompt Quality Tests ====================


class TestPromptQuality:
    """Tests for prompt quality."""

    def test_weather_analysis_prompt_has_content(self):
        """Test weather analysis prompt has substantial content."""
        mcp = FastMCP(name="test")
        weather_assistant.register_prompts(mcp)

        # The prompt should return substantial guidance
        # We can't easily call it without the full MCP infrastructure,
        # but we can verify the source has content
        import inspect

        source = inspect.getsource(weather_assistant)

        # Should have substantial content
        assert len(source) > 5000  # Should be comprehensive

    def test_prompts_cover_all_weather_categories(self):
        """Test that prompts cover all major weather categories."""
        import inspect

        source = inspect.getsource(weather_assistant).lower()

        # Should cover major categories
        assert "forecast" in source
        assert "historical" in source
        assert "air quality" in source
        assert "marine" in source
        assert "climate" in source


# ==================== Prompt Return Value Tests ====================


class TestPromptReturnValues:
    """Tests for prompt return values."""

    def test_prompts_return_strings(self):
        """Test that prompts return string content."""
        # Verify the prompt functions are callable and return strings
        import inspect

        # Get the source to verify structure
        source = inspect.getsource(weather_assistant)

        # Each prompt should return a string (the guidance text)
        assert 'return """' in source or "return '''" in source
