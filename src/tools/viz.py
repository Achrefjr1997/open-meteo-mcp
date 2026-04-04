"""
Visualization Tools for Open-Meteo MCP Server.

Provides tools that analyze weather data and produce metadata for visualization.
Similar to pg-mcp server's visualization tools, but for weather data.
"""

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import OpenMeteoClient

logger = __import__("logging").getLogger(__name__)


def _detect_field_type(key: str, values: list) -> str:
    """Detect the logical type of a weather data field."""
    key_lower = key.lower()
    
    # Temporal fields
    if "time" in key_lower or "date" in key_lower or "sunrise" in key_lower or "sunset" in key_lower:
        return "temporal"
    
    # Quantitative fields
    if any(term in key_lower for term in [
        "temperature", "humidity", "wind", "pressure", "precipitation",
        "cloud", "radiation", "uv", "visibility", "elevation", "wave",
        "pm", "no2", "so2", "o3", "co", "aqi", "snow", "dewpoint"
    ]):
        return "quantitative"
    
    # Categorical/Nominal fields
    if any(term in key_lower for term in [
        "code", "direction", "condition", "category", "name"
    ]):
        return "nominal"
    
    # Check actual values
    if values:
        sample = [v for v in values if v is not None][:10]
        if all(isinstance(v, (int, float)) for v in sample):
            return "quantitative"
        if all(isinstance(v, str) for v in sample):
            if len(set(sample)) <= 20:  # Low cardinality
                return "nominal"
            return "text"
    
    return "text"


def _compute_field_stats(key: str, values: list) -> dict[str, Any]:
    """Compute statistics for a field."""
    if not values:
        return {"name": key, "type": "unknown"}
    
    field_type = _detect_field_type(key, values)
    non_null = [v for v in values if v is not None]
    
    stats = {"name": key, "type": field_type}
    
    if field_type == "quantitative" and non_null:
        try:
            numeric_values = [float(v) for v in non_null if v is not None]
            if numeric_values:
                stats["min"] = min(numeric_values)
                stats["max"] = max(numeric_values)
                stats["mean"] = round(sum(numeric_values) / len(numeric_values), 2)
                stats["count"] = len(numeric_values)
                stats["unique"] = len(set(numeric_values))
        except (ValueError, TypeError):
            pass
    
    elif field_type == "nominal" and non_null:
        stats["unique"] = len(set(str(v) for v in non_null))
        # Show top values
        from collections import Counter
        counter = Counter(str(v) for v in non_null)
        stats["topValues"] = [
            {"value": val, "count": cnt} 
            for val, cnt in counter.most_common(5)
        ]
    
    elif field_type == "temporal" and non_null:
        try:
            sorted_times = sorted(str(v) for v in non_null)
            stats["range"] = [sorted_times[0], sorted_times[-1]]
            stats["count"] = len(sorted_times)
        except Exception:
            pass
    
    return stats


def _analyze_weather_response(data: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze weather API response and produce visualization metadata.
    
    Similar to pg-mcp's get_query_metadata but for weather data.
    """
    metadata = {
        "sections": [],
        "totalFields": 0,
        "recommendedCharts": []
    }
    
    # Analyze current weather
    if "current" in data:
        current = data["current"]
        fields = []
        for key, value in current.items():
            if isinstance(value, list):
                fields.append(_compute_field_stats(key, value[:10]))
            else:
                fields.append(_compute_field_stats(key, [value]))
        
        metadata["sections"].append({
            "name": "current",
            "type": "point-in-time",
            "fields": fields,
            "rowCount": 1
        })
        metadata["recommendedCharts"].append({
            "section": "current",
            "type": "bar",
            "description": "Current conditions comparison"
        })
    
    # Analyze hourly forecast
    if "hourly" in data:
        hourly = data["hourly"]
        fields = []
        row_count = 0
        
        for key, values in hourly.items():
            if isinstance(values, list):
                fields.append(_compute_field_stats(key, values))
                if key == "time":
                    row_count = len(values)
        
        metadata["sections"].append({
            "name": "hourly",
            "type": "time-series",
            "fields": fields,
            "rowCount": row_count
        })
        
        # Recommend charts
        temporal_fields = [f["name"] for f in fields if f.get("type") == "temporal"]
        quantitative_fields = [f["name"] for f in fields if f.get("type") == "quantitative"]
        
        if temporal_fields and quantitative_fields:
            metadata["recommendedCharts"].append({
                "section": "hourly",
                "type": "line",
                "xField": temporal_fields[0],
                "yFields": quantitative_fields[:3],
                "description": f"Time series: {', '.join(quantitative_fields[:3])}"
            })
    
    # Analyze daily forecast
    if "daily" in data:
        daily = data["daily"]
        fields = []
        row_count = 0
        
        for key, values in daily.items():
            if isinstance(values, list):
                fields.append(_compute_field_stats(key, values))
                if key == "time":
                    row_count = len(values)
        
        metadata["sections"].append({
            "name": "daily",
            "type": "daily-aggregates",
            "fields": fields,
            "rowCount": row_count
        })
        
        temporal_fields = [f["name"] for f in fields if f.get("type") == "temporal"]
        quantitative_fields = [f["name"] for f in fields if f.get("type") == "quantitative"]
        
        if temporal_fields and quantitative_fields:
            metadata["recommendedCharts"].append({
                "section": "daily",
                "type": "line",
                "xField": temporal_fields[0],
                "yFields": quantitative_fields[:3],
                "description": f"Daily trends: {', '.join(quantitative_fields[:3])}"
            })
        
        # Special recommendation for temp range
        temp_fields = [f for f in quantitative_fields if "temperature" in f.lower() or "temp" in f.lower()]
        if len(temp_fields) >= 2:
            metadata["recommendedCharts"].append({
                "section": "daily",
                "type": "area",
                "xField": temporal_fields[0] if temporal_fields else "time",
                "yFields": temp_fields[:2],
                "description": "Temperature range (min/max)"
            })
    
    # Analyze location info
    if "location" in data:
        loc = data["location"]
        if isinstance(loc, dict):
            fields = []
            for key, value in loc.items():
                fields.append(_compute_field_stats(key, [value]))
            
            metadata["sections"].append({
                "name": "location",
                "type": "metadata",
                "fields": fields,
                "rowCount": 1
            })
    
    # Analyze air quality
    if "pollutants" in data:
        pollutants = data["pollutants"]
        if isinstance(pollutants, dict):
            fields = []
            for key, value in pollutants.items():
                fields.append(_compute_field_stats(key, [value] if not isinstance(value, list) else value))
            
            metadata["sections"].append({
                "name": "pollutants",
                "type": "composition",
                "fields": fields,
                "rowCount": 1
            })
            
            metadata["recommendedCharts"].append({
                "section": "pollutants",
                "type": "bar",
                "description": "Pollutant breakdown"
            })
    
    # Count total fields
    metadata["totalFields"] = sum(len(s["fields"]) for s in metadata["sections"])
    
    return metadata


def register_viz_tools(mcp: FastMCP, client: OpenMeteoClient) -> None:
    """Register visualization tools with the MCP server."""
    logger.info("Registering visualization tools")

    @mcp.tool()
    async def analyze_weather_data(
        weather_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Analyzes weather data and produces visualization metadata.
        
        This tool analyzes the structure and content of weather API responses
        to recommend appropriate visualizations and provide field statistics.
        
        Args:
            weather_data: Weather data object (from current weather, forecast, 
                         air quality, or any other weather tool result)
            
        Returns:
            JSON metadata including:
            - sections: Data sections (current, hourly, daily, etc.)
            - fields: Field names, types, and statistics
            - recommendedCharts: Suggested chart types and configurations
            - totalFields: Total number of data fields
        
        Example:
            First call get_current_weather, then pass the result to this tool
            to get visualization recommendations.
        """
        try:
            metadata = _analyze_weather_response(weather_data)
            return {
                "success": True,
                "metadata": metadata,
                "chartRecommendations": metadata.get("recommendedCharts", [])
            }
        except Exception as e:
            logger.error(f"Visualization analysis failed: {e}")
            return {
                "success": False,
                "error": f"Failed to analyze weather data: {str(e)}"
            }

    @mcp.tool()
    async def get_chart_recommendation(
        data_type: str,
        variables: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Get chart type recommendations for weather data.
        
        Provides guidance on the best way to visualize specific types of 
        weather data.
        
        Args:
            data_type: Type of weather data. Options:
                - "current": Current conditions
                - "hourly": Hourly forecast
                - "daily": Daily forecast
                - "air_quality": Air quality data
                - "marine": Marine weather
                - "historical": Historical weather
            variables: Specific weather variables (optional)
        
        Returns:
            Chart recommendations with types, configurations, and tips
        """
        recommendations = {
            "current": {
                "primary": "bar",
                "secondary": "metric_cards",
                "tips": [
                    "Use bar charts to compare different weather metrics",
                    "Show temperature and feels-like side by side",
                    "Include humidity and wind speed for context"
                ]
            },
            "hourly": {
                "primary": "line",
                "secondary": "area",
                "tips": [
                    "Line charts work best for time series data",
                    "Show 24 hours for daily patterns",
                    "Use area charts for precipitation probability",
                    "Highlight peak temperature hours"
                ]
            },
            "daily": {
                "primary": "line",
                "secondary": "area",
                "tertiary": "bar",
                "tips": [
                    "Line charts for temperature trends over days",
                    "Area charts for min/max temperature range",
                    "Bar charts for daily precipitation totals",
                    "Show 7-14 day forecasts for trends"
                ]
            },
            "air_quality": {
                "primary": "bar",
                "secondary": "gauge",
                "tips": [
                    "Bar charts for pollutant comparison",
                    "Use gauge/metric for overall AQI",
                    "Color-code by severity (good/poor/very poor)",
                    "Show health recommendations alongside"
                ]
            },
            "marine": {
                "primary": "line",
                "secondary": "area",
                "tips": [
                    "Line charts for wave height over time",
                    "Show wind speed and wave period together",
                    "Use area charts for swell height range"
                ]
            },
            "historical": {
                "primary": "line",
                "secondary": "bar",
                "tertiary": "heatmap",
                "tips": [
                    "Line charts for temperature trends over time",
                    "Bar charts for monthly precipitation totals",
                    "Heatmaps for daily temperature patterns"
                ]
            }
        }
        
        result = recommendations.get(data_type, {
            "primary": "bar",
            "secondary": "line",
            "tips": ["Use bar or line charts for most weather data"]
        })
        
        if variables:
            result["requestedVariables"] = variables
            # Add variable-specific tips
            var_tips = []
            for var in variables:
                if "temperature" in var.lower():
                    var_tips.append(f"Show {var} with min/max range for clarity")
                elif "precipitation" in var.lower() or "rain" in var.lower():
                    var_tips.append(f"Use bar chart for {var} totals")
                elif "wind" in var.lower():
                    var_tips.append(f"Combine {var} with direction for full picture")
            
            if var_tips:
                result["variableTips"] = var_tips
        
        return result
