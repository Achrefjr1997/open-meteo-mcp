"""
Geocoding Tools for Open-Meteo MCP Server.

Provides tools for searching locations by name, resolving coordinates,
and getting location details by ID.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import OpenMeteoClient


def register_geocoding_tools(mcp: FastMCP, client: OpenMeteoClient) -> None:
    """Register all geocoding tools with the MCP server."""

    @mcp.tool()
    async def search_location(
        name: str,
        count: int = 10,
        language: str = "en",
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Search for locations by name or postal code.

        Supports exact matching (2+ characters) and fuzzy matching (3+ characters).
        Returns translated results based on language parameter.

        Args:
            name: Search term (location name or postal code). Minimum 2 characters.
            count: Number of results to return (1-100, default 10)
            language: Language code for translated results (default "en")
                Examples: "en", "de", "fr", "es", "it", "pt", "nl", "pl", "ru"
            country_code: Filter by ISO-3166-1 alpha2 country code (optional)
                Examples: "US", "GB", "DE", "FR", "ES", "IT", "JP", "CN"

        Returns:
            List of matching locations with coordinates, timezone, population,
            elevation, country info, and administrative divisions.

        Example:
            search_location(name="London", count=5, country_code="GB")
            search_location(name="90210", count=1)  # Postal code search
        """
        if len(name) < 2:
            return {
                "error": "Search term must be at least 2 characters",
                "results": [],
            }

        response = await client.search_location(
            name=name,
            count=count,
            language=language,
            country_code=country_code,
        )

        if not response.success:
            return {"error": response.error_message, "results": []}

        data = response.data
        results = data.get("results", [])

        # Format results for readability
        formatted_results = []
        for loc in results:
            formatted = {
                "id": loc.get("id"),
                "name": loc.get("name"),
                "country": loc.get("country", ""),
                "country_code": loc.get("country_code", ""),
                "latitude": loc.get("latitude"),
                "longitude": loc.get("longitude"),
                "elevation": loc.get("elevation"),
                "timezone": loc.get("timezone"),
                "population": loc.get("population"),
                "feature_code": loc.get("feature_code"),
            }

            # Add administrative divisions if available
            if loc.get("admin1"):
                formatted["admin1"] = loc.get("admin1")
            if loc.get("admin2"):
                formatted["admin2"] = loc.get("admin2")

            formatted_results.append(formatted)

        return {
            "query": name,
            "count": len(formatted_results),
            "results": formatted_results,
        }

    @mcp.tool()
    async def get_location_by_id(location_id: int) -> dict[str, Any]:
        """
        Get full location details by unique ID.

        Use this to retrieve complete information for a location
        after finding it with search_location.

        Args:
            location_id: Unique location ID from search results

        Returns:
            Complete location details including all administrative levels,
            postal codes, and alternative names.
        """
        response = await client.get_location_by_id(location_id=location_id)

        if not response.success:
            return {"error": response.error_message}

        data = response.data
        return data

    @mcp.tool()
    async def resolve_coordinates(
        location_name: str,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Resolve a location name to coordinates.

        This is a convenience tool that searches for a location and returns
        the best match's coordinates. Useful for converting place names to
        coordinates for use with other weather tools.

        Args:
            location_name: Name of the location to resolve
            country_code: Optional country code to narrow search

        Returns:
            Best match with coordinates and location info, or error if not found.

        Example:
            resolve_coordinates("Paris", "FR")  # Returns Paris, France coordinates
            resolve_coordinates("New York")  # Returns New York City coordinates
        """
        # Search for the location
        search_result = await search_location(
            name=location_name,
            count=1,
            country_code=country_code,
        )

        if "error" in search_result:
            return search_result

        results = search_result.get("results", [])
        if not results:
            return {
                "error": f"Location '{location_name}' not found",
                "suggestion": "Try a different spelling or add country code",
            }

        best_match = results[0]
        return {
            "location": location_name,
            "matched_name": best_match.get("name"),
            "country": best_match.get("country"),
            "latitude": best_match.get("latitude"),
            "longitude": best_match.get("longitude"),
            "elevation": best_match.get("elevation"),
            "timezone": best_match.get("timezone"),
            "population": best_match.get("population"),
        }

    @mcp.tool()
    async def search_locations_in_country(
        country_code: str,
        name_prefix: str | None = None,
        count: int = 20,
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Search for locations within a specific country.

        Args:
            country_code: ISO-3166-1 alpha2 country code (required)
                Examples: "US", "GB", "DE", "FR", "ES", "IT", "JP", "CN", "AU"
            name_prefix: Optional name prefix to filter results
            count: Number of results to return (1-100, default 20)
            language: Language code for results (default "en")

        Returns:
            List of locations in the specified country
        """
        if len(country_code) != 2:
            return {
                "error": "Country code must be 2 characters (ISO-3166-1 alpha2)",
                "results": [],
            }

        search_term = name_prefix if name_prefix else "a"  # Generic search

        response = await client.search_location(
            name=search_term,
            count=count,
            language=language,
            country_code=country_code,
        )

        if not response.success:
            return {"error": response.error_message, "results": []}

        data = response.data
        results = data.get("results", [])

        # Group by feature type
        by_feature = {}
        for loc in results:
            feature = loc.get("feature_code", "unknown")
            if feature not in by_feature:
                by_feature[feature] = []
            by_feature[feature].append(
                {
                    "name": loc.get("name"),
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                    "population": loc.get("population"),
                }
            )

        return {
            "country_code": country_code,
            "count": len(results),
            "results": results,
            "by_feature_type": by_feature,
        }

    @mcp.tool()
    async def get_nearby_cities(
        latitude: float,
        longitude: float,
        max_results: int = 10,
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Find nearby cities/locations for a coordinate.

        This searches for populated places near the given coordinates,
        useful for getting a location name for weather data.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            max_results: Maximum number of results (1-100, default 10)
            language: Language code for results

        Returns:
            List of nearby populated places with distances
        """
        import math

        # Search for locations (we'll filter by distance after)
        response = await client.search_location(
            name="a",  # Generic search to get many results
            count=100,  # Get more to filter
            language=language,
        )

        if not response.success:
            return {"error": response.error_message, "results": []}

        data = response.data
        all_results = data.get("results", [])

        # Calculate distances and filter
        def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            """Calculate distance between two points in kilometers."""
            R = 6371  # Earth's radius in km
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)

            a = (
                math.sin(delta_lat / 2) ** 2
                + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            return R * c

        # Filter to populated places and calculate distance
        nearby = []
        for loc in all_results:
            feature = loc.get("feature_code", "")
            if feature in [
                "PPL",
                "PPLA",
                "PPLA2",
                "PPLA3",
                "PPLA4",
                "PPLC",
                "PPLG",
                "PPLR",
                "PPLS",
            ]:
                loc_lat = loc.get("latitude")
                loc_lon = loc.get("longitude")
                if loc_lat and loc_lon:
                    distance = haversine_distance(latitude, longitude, loc_lat, loc_lon)
                    if distance < 100:  # Within 100 km
                        nearby.append(
                            {
                                "name": loc.get("name"),
                                "country": loc.get("country"),
                                "latitude": loc_lat,
                                "longitude": loc_lon,
                                "population": loc.get("population"),
                                "distance_km": round(distance, 2),
                            }
                        )

        # Sort by distance and limit results
        nearby.sort(key=lambda x: x["distance_km"])
        nearby = nearby[:max_results]

        return {
            "query_coordinates": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "count": len(nearby),
            "nearby_cities": nearby,
        }
