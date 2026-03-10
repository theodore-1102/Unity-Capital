"""
Bloomberg API Client
====================
Connects to Bloomberg B-PIPE or Data License REST API to pull:
  • Private-markets news headlines (feeds into Private Markets News tab)
  • NAV / pricing data for PE fund benchmarks
  • Index data (PE secondary pricing indices)

Requires: BLOOMBERG_API_KEY  (or B-PIPE session via BLOOMBERG_HOST:BLOOMBERG_PORT)

Bloomberg Data License REST endpoint reference:
  https://data.bloomberg.com/portal/docs
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from app.config import BloombergConfig

logger = logging.getLogger(__name__)


class BloombergClient:
    """Thin wrapper around Bloomberg Data License REST / B-PIPE."""

    # Bloomberg news categories relevant to PE secondaries
    NEWS_TOPICS = [
        "PRIV_EQUITY",
        "LEVERAGED_BUYOUT",
        "FUND_FLOWS",
        "ALT_INVESTMENTS",
        "MERGERS_ACQUISITIONS",
    ]

    # Tickers useful for secondary pricing context
    BENCHMARK_TICKERS = [
        "BPEASEC Index",   # Bloomberg PE Secondary Index (illustrative)
        "SPGPEI Index",    # S&P Listed PE Index
        "LPX50 Index",     # LPX Major Market Index
    ]

    def __init__(self, config: BloombergConfig):
        self._cfg = config
        self._session = requests.Session()
        if config.api_key:
            self._session.headers.update({
                "Authorization": f"Bearer {config.api_key}",
                "Accept": "application/json",
            })
        self._base = "https://data.bloomberg.com/api/v1"
        self._cache: Dict[str, Any] = {}
        self._cache_ts: float = 0
        self._cache_ttl: int = 900   # 15 min

    # ── Connection ──────────────────────────────────────────

    def is_connected(self) -> bool:
        """Return True if a valid API key is configured."""
        return self._cfg.enabled

    def connection_error(self) -> dict:
        """Standard error payload when not connected."""
        return {
            "connected": False,
            "provider": "bloomberg",
            "label": "Bloomberg Terminal",
            "message": (
                "Bloomberg API key not configured. "
                "Set BLOOMBERG_API_KEY in your .env file or environment variables "
                "to enable live market data and PE news from Bloomberg."
            ),
        }

    # ── News ────────────────────────────────────────────────

    def fetch_news(
        self,
        topics: Optional[List[str]] = None,
        max_results: int = 50,
        hours_back: int = 72,
    ) -> List[dict]:
        """
        Pull recent PE / alternatives headlines from Bloomberg.

        Returns list of dicts compatible with NewsArticle model:
            {title, summary, link, published, source, sourceColor, themes, regionTags, assetTags}
        """
        if not self.is_connected():
            return []

        topics = topics or self.NEWS_TOPICS
        since = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

        articles: List[dict] = []
        try:
            # Bloomberg Data License news search endpoint (illustrative)
            resp = self._session.get(
                f"{self._base}/news/search",
                params={
                    "topics": ",".join(topics),
                    "publishedSince": since,
                    "limit": max_results,
                    "sort": "publishedDesc",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            for idx, item in enumerate(data.get("results", []), start=1):
                articles.append({
                    "id": idx,
                    "title": item.get("headline", ""),
                    "summary": (item.get("body", "") or "")[:500],
                    "link": item.get("url", ""),
                    "published": item.get("publishedAt", ""),
                    "source": "Bloomberg",
                    "sourceColor": "#1a1a2e",
                    "themes": [],       # enriched downstream by theme tagger
                    "regionTags": [],
                    "assetTags": [],
                })
        except requests.RequestException as exc:
            logger.warning("Bloomberg news fetch failed: %s", exc)

        return articles

    # ── Market Data ─────────────────────────────────────────

    def fetch_benchmark_prices(
        self,
        tickers: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        Pull last-price snapshot for PE benchmark indices.
        Useful for secondary discount context.
        """
        if not self.is_connected():
            return []

        tickers = tickers or self.BENCHMARK_TICKERS
        results: List[dict] = []
        try:
            resp = self._session.get(
                f"{self._base}/data/snapshot",
                params={
                    "securities": ",".join(tickers),
                    "fields": "PX_LAST,CHG_PCT_1D,NAME",
                },
                timeout=10,
            )
            resp.raise_for_status()
            for row in resp.json().get("data", []):
                results.append({
                    "ticker": row.get("security", ""),
                    "name": row.get("NAME", ""),
                    "price": row.get("PX_LAST"),
                    "change_pct": row.get("CHG_PCT_1D"),
                })
        except requests.RequestException as exc:
            logger.warning("Bloomberg benchmark fetch failed: %s", exc)

        return results

    # ── Fund-level NAV (for My PE Assets enrichment) ────────

    def fetch_fund_nav(self, fund_identifier: str) -> Optional[dict]:
        """
        Retrieve latest reported NAV for a PE fund via Bloomberg.
        fund_identifier can be a Bloomberg ID or ISIN.
        """
        if not self.is_connected():
            return None

        try:
            resp = self._session.get(
                f"{self._base}/data/history",
                params={
                    "securities": fund_identifier,
                    "fields": "FUND_NET_ASSET_VAL,FUND_TOTAL_ASSETS",
                    "periodicitySelection": "QUARTERLY",
                    "limit": 1,
                },
                timeout=10,
            )
            resp.raise_for_status()
            rows = resp.json().get("data", [])
            if rows:
                return {
                    "fund": fund_identifier,
                    "nav": rows[0].get("FUND_NET_ASSET_VAL"),
                    "total_assets": rows[0].get("FUND_TOTAL_ASSETS"),
                    "as_of": rows[0].get("date"),
                }
        except requests.RequestException as exc:
            logger.warning("Bloomberg fund NAV fetch failed: %s", exc)

        return None
