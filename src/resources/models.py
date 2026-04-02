"""
MCP Resources for Weather Models.

Provides read-only access to weather model information,
coverage, resolution, and update frequencies.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP


def register_model_resources(mcp: FastMCP) -> None:
    """Register all model-related resources with the MCP server."""

    @mcp.resource("weather://models/all")
    def get_all_models() -> dict[str, Any]:
        """
        Get all available weather models with descriptions.

        Returns complete list of weather models organized by provider.
        """
        return {
            "total": len(_MODELS),
            "providers": list(_PROVIDERS.keys()),
            "models": _MODELS,
        }

    @mcp.resource("weather://models/ecmwf")
    def get_ecmwf_models() -> dict[str, Any]:
        """Get ECMWF (European Centre) weather models."""
        return _filter_by_provider("ECMWF")

    @mcp.resource("weather://models/noaa")
    def get_noaa_models() -> dict[str, Any]:
        """Get NOAA (US) weather models."""
        return _filter_by_provider("NOAA")

    @mcp.resource("weather://models/dwd")
    def get_dwd_models() -> dict[str, Any]:
        """Get DWD (German) weather models."""
        return _filter_by_provider("DWD")

    @mcp.resource("weather://models/meteo_france")
    def get_meteo_france_models() -> dict[str, Any]:
        """Get Météo-France weather models."""
        return _filter_by_provider("Météo-France")

    @mcp.resource("weather://models/ukmo")
    def get_ukmo_models() -> dict[str, Any]:
        """Get UK Met Office weather models."""
        return _filter_by_provider("UK Met Office")

    @mcp.resource("weather://models/met_norway")
    def get_met_norway_models() -> dict[str, Any]:
        """Get Met Norway weather models."""
        return _filter_by_provider("Met Norway")

    @mcp.resource("weather://models/eccc")
    def get_eccc_models() -> dict[str, Any]:
        """Get Environment Canada (ECCC) weather models."""
        return _filter_by_provider("ECCC")

    @mcp.resource("weather://models/jma")
    def get_jma_models() -> dict[str, Any]:
        """Get JMA (Japan) weather models."""
        return _filter_by_provider("JMA")

    @mcp.resource("weather://models/ensemble")
    def get_ensemble_models() -> dict[str, Any]:
        """Get ensemble forecast models."""
        return {
            "description": "Ensemble models combine multiple forecasts for uncertainty estimation",
            "models": _filter_by_type("ensemble"),
        }

    @mcp.resource("weather://models/comparison")
    def get_model_comparison() -> dict[str, Any]:
        """
        Compare weather models by resolution and coverage.

        Useful for selecting the best model for a specific location.
        """
        comparison = {
            "by_resolution": {
                "highest_resolution": [],
                "high_resolution": [],
                "medium_resolution": [],
                "global_models": [],
            },
            "by_coverage": {
                "global": [],
                "regional_europe": [],
                "regional_north_america": [],
                "regional_asia": [],
            },
            "recommendations": {
                "europe": ["icon_eu", "icon_d2", "ecmwf_ifs04", "meteofrance_seamless"],
                "north_america": ["gfs_hrrr", "gfs_global", "gem_global"],
                "asia": ["jma_msm", "jma_gsm"],
                "global": ["ecmwf_ifs04", "gfs_global", "icon_global"],
                "marine": ["gfs_global", "ecmwf_ifs04", "wave_models"],
            },
        }

        for model_id, info in _MODELS.items():
            res = info.get("resolution_km", 999)
            if res <= 3:
                comparison["by_resolution"]["highest_resolution"].append(model_id)
            elif res <= 7:
                comparison["by_resolution"]["high_resolution"].append(model_id)
            elif res <= 15:
                comparison["by_resolution"]["medium_resolution"].append(model_id)

            coverage = info.get("coverage", "global")
            if coverage == "global":
                comparison["by_coverage"]["global"].append(model_id)
            elif "Europe" in coverage:
                comparison["by_coverage"]["regional_europe"].append(model_id)

        return comparison

    @mcp.resource("weather://models/usage-guide")
    def get_models_usage_guide() -> dict[str, Any]:
        """
        Get guide for selecting and using weather models.

        Includes model characteristics, best use cases, and selection tips.
        """
        return {
            "title": "Weather Models Usage Guide",
            "sections": {
                "model_selection": {
                    "title": "How to Select a Model",
                    "guidelines": [
                        "For Europe: Use ICON-EU (7km) or ICON-D2 (2km) for highest accuracy",
                        "For North America: Use GFS-HRRR for short-term, GFS for extended",
                        "For global coverage: ECMWF IFS is generally most accurate",
                        "For ensemble/uncertainty: Use ICON-EPS or GFS-Ensemble",
                        "For marine: Use GFS or ECMWF with marine variables",
                    ],
                },
                "model_characteristics": {
                    "title": "Model Characteristics",
                    "factors": {
                        "resolution": "Higher resolution = better local detail",
                        "update_frequency": "More frequent = more current forecasts",
                        "forecast_range": "Some models excel at short-term, others at extended",
                        "ensemble": "Provides probability and uncertainty information",
                    },
                },
                "best_practices": {
                    "title": "Best Practices",
                    "tips": [
                        "Use 'best_match' for automatic model selection",
                        "Compare multiple models for important decisions",
                        "Check ensemble spread for forecast confidence",
                        "Regional models outperform global models locally",
                        "Update frequency matters for rapidly changing conditions",
                    ],
                },
            },
        }


def _filter_by_provider(provider: str) -> dict[str, Any]:
    """Filter models by provider."""
    return {
        model_id: info for model_id, info in _MODELS.items() if info.get("provider") == provider
    }


def _filter_by_type(model_type: str) -> dict[str, Any]:
    """Filter models by type."""
    return {model_id: info for model_id, info in _MODELS.items() if info.get("type") == model_type}


# ==================== Model Definitions ====================

_PROVIDERS = {
    "ECMWF": "European Centre for Medium-Range Weather Forecasts",
    "NOAA": "US National Oceanic and Atmospheric Administration",
    "DWD": "German Weather Service (Deutscher Wetterdienst)",
    "Météo-France": "French National Meteorological Service",
    "UK Met Office": "United Kingdom Met Office",
    "Met Norway": "Norwegian Meteorological Institute",
    "ECCC": "Environment and Climate Change Canada",
    "JMA": "Japan Meteorological Agency",
    "KMA": "Korea Meteorological Administration",
    "BOM": "Australian Bureau of Meteorology",
    "MeteoSwiss": "Federal Office of Meteorology and Climatology Switzerland",
    "DMI": "Danish Meteorological Institute",
    "KNMI": "Royal Netherlands Meteorological Institute",
    "GeoSphere Austria": "Austrian National Weather Service",
    "ItaliaMeteo": "Italian Weather Service",
}


_MODELS = {
    # ECMWF Models
    "ecmwf_ifs04": {
        "provider": "ECMWF",
        "name": "IFS High Resolution",
        "description": "ECMWF Integrated Forecasting System - High Resolution",
        "resolution_km": 9,
        "coverage": "Global",
        "forecast_days": 10,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "Global medium-range forecasting, most accurate global model",
    },
    "ecmwf_ifs025": {
        "provider": "ECMWF",
        "name": "IFS 0.25°",
        "description": "ECMWF IFS at 0.25 degree resolution",
        "resolution_km": 25,
        "coverage": "Global",
        "forecast_days": 10,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "Global forecasting with lower data requirements",
    },
    "ifs_ensemble": {
        "provider": "ECMWF",
        "name": "IFS Ensemble",
        "description": "ECMWF Ensemble Prediction System",
        "resolution_km": 25,
        "coverage": "Global",
        "forecast_days": 15,
        "update_frequency": "Every 6 hours",
        "type": "ensemble",
        "best_for": "Uncertainty estimation, probability forecasts",
    },
    "aifs_ensemble": {
        "provider": "ECMWF",
        "name": "AIFS Ensemble",
        "description": "ECMWF AI Forecasting System Ensemble",
        "resolution_km": 25,
        "coverage": "Global",
        "forecast_days": 10,
        "update_frequency": "Every 6 hours",
        "type": "ensemble",
        "best_for": "AI-enhanced ensemble forecasting",
    },
    # NOAA Models
    "gfs_global": {
        "provider": "NOAA",
        "name": "GFS Global",
        "description": "Global Forecast System",
        "resolution_km": 25,
        "coverage": "Global",
        "forecast_days": 16,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "Extended range forecasting, North America",
    },
    "gfs_hrrr": {
        "provider": "NOAA",
        "name": "HRRR",
        "description": "High-Resolution Rapid Refresh",
        "resolution_km": 3,
        "coverage": "North America (CONUS)",
        "forecast_days": 1,
        "update_frequency": "Every hour",
        "type": "deterministic",
        "best_for": "Short-term convection, severe weather, North America",
    },
    "gfs_ens": {
        "provider": "NOAA",
        "name": "GFS Ensemble",
        "description": "GFS Ensemble Forecast System",
        "resolution_km": 25,
        "coverage": "Global",
        "forecast_days": 16,
        "update_frequency": "Every 6 hours",
        "type": "ensemble",
        "best_for": "Uncertainty estimation for North America",
    },
    "gfs_ens_025": {
        "provider": "NOAA",
        "name": "GFS Ensemble 0.25°",
        "description": "GFS Ensemble at 0.25 degree",
        "resolution_km": 25,
        "coverage": "Global",
        "forecast_days": 16,
        "update_frequency": "Every 6 hours",
        "type": "ensemble",
        "best_for": "Lower resolution ensemble forecasting",
    },
    # DWD (German) Models
    "icon_global": {
        "provider": "DWD",
        "name": "ICON Global",
        "description": "Icosahedral Non-hydrostatic Global Model",
        "resolution_km": 13,
        "coverage": "Global",
        "forecast_days": 7,
        "update_frequency": "Every hour",
        "type": "deterministic",
        "best_for": "Global forecasting, excellent for Europe",
    },
    "icon_eu": {
        "provider": "DWD",
        "name": "ICON Europe",
        "description": "ICON Regional Model for Europe",
        "resolution_km": 7,
        "coverage": "Europe",
        "forecast_days": 7,
        "update_frequency": "Every hour",
        "type": "deterministic",
        "best_for": "European regional forecasting",
    },
    "icon_d2": {
        "provider": "DWD",
        "name": "ICON D2",
        "description": "ICON for Germany (2km)",
        "resolution_km": 2,
        "coverage": "Central Europe (Germany)",
        "forecast_days": 3,
        "update_frequency": "Every hour",
        "type": "deterministic",
        "best_for": "High-resolution forecasting for Central Europe",
    },
    "icon_eps": {
        "provider": "DWD",
        "name": "ICON Ensemble",
        "description": "ICON Global Ensemble",
        "resolution_km": 13,
        "coverage": "Global",
        "forecast_days": 7,
        "update_frequency": "Every 6 hours",
        "type": "ensemble",
        "best_for": "Global ensemble with European focus",
    },
    "icon_eps_eu": {
        "provider": "DWD",
        "name": "ICON Ensemble Europe",
        "description": "ICON Ensemble for Europe",
        "resolution_km": 7,
        "coverage": "Europe",
        "forecast_days": 5,
        "update_frequency": "Every 6 hours",
        "type": "ensemble",
        "best_for": "European ensemble forecasting",
    },
    "icon_eps_d2": {
        "provider": "DWD",
        "name": "ICON Ensemble D2",
        "description": "ICON Ensemble for Germany",
        "resolution_km": 2,
        "coverage": "Central Europe",
        "forecast_days": 3,
        "update_frequency": "Every 6 hours",
        "type": "ensemble",
        "best_for": "High-resolution ensemble for Germany",
    },
    # Météo-France Models
    "meteofrance_seamless": {
        "provider": "Météo-France",
        "name": "Météo-France Seamless",
        "description": "Météo-France Seamless Forecast",
        "resolution_km": 2.5,
        "coverage": "France and surroundings",
        "forecast_days": 14,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "France and French territories",
    },
    "meteofrance_arpege": {
        "provider": "Météo-France",
        "name": "ARPEGE",
        "description": "Action de Recherche Petite Echelle pour la Météorologie",
        "resolution_km": 10,
        "coverage": "Europe/North Atlantic",
        "forecast_days": 10,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "European medium-range forecasting",
    },
    "meteofrance_arome": {
        "provider": "Météo-France",
        "name": "AROME",
        "description": "Application de la Recherche à l'Opérationnel à Méso Echelle",
        "resolution_km": 1.3,
        "coverage": "France",
        "forecast_days": 2,
        "update_frequency": "Every 3 hours",
        "type": "deterministic",
        "best_for": "High-resolution forecasting for France",
    },
    # UK Met Office Models
    "ukmo_global": {
        "provider": "UK Met Office",
        "name": "UKMO Global",
        "description": "UK Met Office Global Model",
        "resolution_km": 10,
        "coverage": "Global",
        "forecast_days": 7,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "Global forecasting with UK focus",
    },
    "ukmo_uk": {
        "provider": "UK Met Office",
        "name": "UKMO UK",
        "description": "UK Met Office UK Model (2km)",
        "resolution_km": 2,
        "coverage": "United Kingdom",
        "forecast_days": 4,
        "update_frequency": "Every hour",
        "type": "deterministic",
        "best_for": "High-resolution forecasting for UK",
    },
    "ukmo_ensemble": {
        "provider": "UK Met Office",
        "name": "UKMO Ensemble",
        "description": "UK Met Office Global Ensemble",
        "resolution_km": 10,
        "coverage": "Global",
        "forecast_days": 7,
        "update_frequency": "Every 6 hours",
        "type": "ensemble",
        "best_for": "Ensemble forecasting with UK focus",
    },
    # Met Norway Models
    "metno_nordic": {
        "provider": "Met Norway",
        "name": "Met Norway Nordic",
        "description": "Met Norway Nordic Model",
        "resolution_km": 2.5,
        "coverage": "Nordic countries",
        "forecast_days": 10,
        "update_frequency": "Every hour",
        "type": "deterministic",
        "best_for": "Nordic countries and Arctic forecasting",
    },
    "metno_global": {
        "provider": "Met Norway",
        "name": "Met Norway Global",
        "description": "Met Norway Global Model",
        "resolution_km": 10,
        "coverage": "Global",
        "forecast_days": 10,
        "update_frequency": "Every hour",
        "type": "deterministic",
        "best_for": "Global forecasting with Arctic focus",
    },
    # ECCC (Canada) Models
    "gem_global": {
        "provider": "ECCC",
        "name": "GEM Global",
        "description": "Global Environmental Multiscale Model",
        "resolution_km": 25,
        "coverage": "Global",
        "forecast_days": 10,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "North American forecasting",
    },
    "gem_regional": {
        "provider": "ECCC",
        "name": "GEM Regional",
        "description": "GEM Regional Model for North America",
        "resolution_km": 10,
        "coverage": "North America",
        "forecast_days": 5,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "Regional forecasting for Canada and North America",
    },
    "gem_ensemble": {
        "provider": "ECCC",
        "name": "GEM Ensemble",
        "description": "GEM Ensemble Forecast System",
        "resolution_km": 25,
        "coverage": "Global",
        "forecast_days": 10,
        "update_frequency": "Every 6 hours",
        "type": "ensemble",
        "best_for": "Ensemble forecasting for North America",
    },
    # JMA (Japan) Models
    "jma_msm": {
        "provider": "JMA",
        "name": "JMA MSM",
        "description": "JMA Meso Scale Model",
        "resolution_km": 5,
        "coverage": "Japan and surroundings",
        "forecast_days": 4,
        "update_frequency": "Every 3 hours",
        "type": "deterministic",
        "best_for": "Japan regional forecasting",
    },
    "jma_gsm": {
        "provider": "JMA",
        "name": "JMA GSM",
        "description": "JMA Global Spectral Model",
        "resolution_km": 20,
        "coverage": "Global",
        "forecast_days": 9,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "Global forecasting with Asia focus",
    },
    # Other Regional Models
    "kma_ldps": {
        "provider": "KMA",
        "name": "KMA LDPS",
        "description": "Korea Local Data Processing System",
        "resolution_km": 1.5,
        "coverage": "Korea",
        "forecast_days": 3,
        "update_frequency": "Every 3 hours",
        "type": "deterministic",
        "best_for": "Korea regional forecasting",
    },
    "bom_access": {
        "provider": "BOM",
        "name": "ACCESS",
        "description": "Australian Community Climate and Earth-System Simulator",
        "resolution_km": 12,
        "coverage": "Australia",
        "forecast_days": 7,
        "update_frequency": "Every 6 hours",
        "type": "deterministic",
        "best_for": "Australia and Oceania forecasting",
    },
    "meteoswiss_icon_ch1": {
        "provider": "MeteoSwiss",
        "name": "ICON CH1",
        "description": "ICON for Switzerland (1km)",
        "resolution_km": 1,
        "coverage": "Switzerland",
        "forecast_days": 3,
        "update_frequency": "Every hour",
        "type": "deterministic",
        "best_for": "Very high-resolution forecasting for Switzerland",
    },
    "meteoswiss_icon_ch2": {
        "provider": "MeteoSwiss",
        "name": "ICON CH2",
        "description": "ICON for Switzerland (2km)",
        "resolution_km": 2,
        "coverage": "Switzerland",
        "forecast_days": 5,
        "update_frequency": "Every hour",
        "type": "deterministic",
        "best_for": "High-resolution forecasting for Switzerland",
    },
}
