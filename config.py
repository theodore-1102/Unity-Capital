"""
Sutanto Capital — PE Secondary Dealflow Platform
Configuration module: centralises env vars, API credentials, and app settings.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BloombergConfig:
    """Bloomberg B-PIPE / BLPAPI configuration."""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("BLOOMBERG_API_KEY"))
    host: str = field(default_factory=lambda: os.getenv("BLOOMBERG_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("BLOOMBERG_PORT", "8194")))
    enabled: bool = field(default_factory=lambda: bool(os.getenv("BLOOMBERG_API_KEY")))


@dataclass
class MergermarketConfig:
    """Mergermarket (ION / Acuris) API configuration."""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("MERGERMARKET_API_KEY"))
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "MERGERMARKET_BASE_URL",
            "https://api.mergermarket.com/v1",
        )
    )
    enabled: bool = field(default_factory=lambda: bool(os.getenv("MERGERMARKET_API_KEY")))


@dataclass
class SPCapitalIQConfig:
    """S&P Capital IQ (Xpressfeed / REST) configuration."""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("SP_CAPITALIQ_API_KEY"))
    username: Optional[str] = field(default_factory=lambda: os.getenv("SP_CAPITALIQ_USERNAME"))
    password: Optional[str] = field(default_factory=lambda: os.getenv("SP_CAPITALIQ_PASSWORD"))
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "SP_CAPITALIQ_BASE_URL",
            "https://api-ciq.marketintelligence.spglobal.com/gdsapi/rest/v3",
        )
    )
    enabled: bool = field(default_factory=lambda: bool(os.getenv("SP_CAPITALIQ_API_KEY")))


@dataclass
class GoogleSearchConfig:
    """Google Custom Search JSON API configuration."""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_SEARCH_API_KEY"))
    cx: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_SEARCH_CX"))
    enabled: bool = field(default_factory=lambda: bool(os.getenv("GOOGLE_SEARCH_API_KEY")))


@dataclass
class SecondariesInvestorConfig:
    """Secondaries Investor (PEI Media) API configuration."""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("SECONDARIES_INVESTOR_API_KEY"))
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "SECONDARIES_INVESTOR_BASE_URL",
            "https://api.secondariesinvestor.com/v1",
        )
    )
    enabled: bool = field(default_factory=lambda: bool(os.getenv("SECONDARIES_INVESTOR_API_KEY")))


@dataclass
class AppConfig:
    """Top-level application configuration."""
    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production")
    )
    DEBUG: bool = field(default_factory=lambda: os.getenv("FLASK_DEBUG", "0") == "1")
    DATABASE_URI: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///sutanto.db")
    )
    NEWS_CACHE_TTL: int = 1800  # seconds

    bloomberg: BloombergConfig = field(default_factory=BloombergConfig)
    mergermarket: MergermarketConfig = field(default_factory=MergermarketConfig)
    sp_capitaliq: SPCapitalIQConfig = field(default_factory=SPCapitalIQConfig)
    google_search: GoogleSearchConfig = field(default_factory=GoogleSearchConfig)
    secondaries_investor: SecondariesInvestorConfig = field(default_factory=SecondariesInvestorConfig)

    def api_status(self) -> dict:
        """Return connection status of every external API."""
        return {
            "bloomberg": {
                "connected": self.bloomberg.enabled,
                "label": "Bloomberg Terminal",
            },
            "mergermarket": {
                "connected": self.mergermarket.enabled,
                "label": "Mergermarket (ION Analytics)",
            },
            "sp_capitaliq": {
                "connected": self.sp_capitaliq.enabled,
                "label": "S&P Capital IQ",
            },
            "google_search": {
                "connected": self.google_search.enabled,
                "label": "Google Search API",
            },
            "secondaries_investor": {
                "connected": self.secondaries_investor.enabled,
                "label": "Secondaries Investor",
            },
        }
