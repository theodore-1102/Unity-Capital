"""
Mergermarket API Client
=======================
Connects to Mergermarket (ION Analytics / Acuris) REST API to pull:
  • M&A deal intelligence (feeds into Secondary Deal Database)
  • Rumoured / announced / completed PE deals
  • Fund-level transaction data with seller/buyer, region, asset class

Requires: MERGERMARKET_API_KEY

Mergermarket API reference (ION Analytics):
  https://developer.iongroup.com/apis/mergermarket
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from app.config import MergermarketConfig

logger = logging.getLogger(__name__)

# Map Mergermarket deal types → app transaction types
_TX_TYPE_MAP = {
    "Fund Secondary": "Funds",
    "LP Secondary": "Funds",
    "GP-Led Secondary": "Funds",
    "Direct Secondary": "Directs",
    "Co-investment Secondary": "Co-investments",
    "Strip Sale": "Funds",
    "Single Asset Continuation": "Directs",
    "Multi-Asset Continuation": "Funds",
    "Preferred Equity": "Funds",
    "Tender Offer": "Funds",
}

# Map Mergermarket status → app status
_STATUS_MAP = {
    "Rumoured": "Under Review",
    "Announced": "Active",
    "Completed": "Closed",
    "Withdrawn": "Draft",
    "On Hold": "Under Review",
}


class MergermarketClient:
    """Wrapper for Mergermarket REST API (ION Analytics)."""

    def __init__(self, config: MergermarketConfig):
        self._cfg = config
        self._session = requests.Session()
        if config.api_key:
            self._session.headers.update({
                "Authorization": f"Bearer {config.api_key}",
                "Accept": "application/json",
                "X-MM-Version": "2024-01",
            })
        self._base = config.base_url.rstrip("/")

    # ── Connection ──────────────────────────────────────────

    def is_connected(self) -> bool:
        return self._cfg.enabled

    def connection_error(self) -> dict:
        return {
            "connected": False,
            "provider": "mergermarket",
            "label": "Mergermarket (ION Analytics)",
            "message": (
                "Mergermarket API key not configured. "
                "Set MERGERMARKET_API_KEY in your .env file to enable "
                "live M&A deal intelligence from Mergermarket."
            ),
        }

    # ── Secondary Deals ─────────────────────────────────────

    def fetch_secondary_deals(
        self,
        region: Optional[str] = None,
        asset_class: Optional[str] = None,
        status: Optional[str] = None,
        days_back: int = 180,
        max_results: int = 100,
    ) -> List[dict]:
        """
        Pull PE secondary market deals from Mergermarket.

        Returns list of dicts compatible with the Deal model:
            {dealName, seller, buyer, region, transactionType,
             assetClass, discountToNav, transactionSize, status, ...}
        """
        if not self.is_connected():
            return []

        since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        params: Dict[str, Any] = {
            "sector": "Private Equity",
            "subSector": "Secondaries",
            "dateFrom": since,
            "limit": max_results,
            "sortBy": "announcedDate",
            "sortOrder": "desc",
        }
        if region:
            params["region"] = region
        if asset_class:
            params["assetClass"] = asset_class
        if status:
            params["dealStatus"] = status

        deals: List[dict] = []
        try:
            resp = self._session.get(
                f"{self._base}/deals/search",
                params=params,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()

            for idx, item in enumerate(data.get("deals", []), start=1):
                mm_type = item.get("dealSubType", "Fund Secondary")
                mm_status = item.get("status", "Announced")

                deals.append({
                    "id": None,  # assigned by app
                    "dealName": item.get("dealName", f"MM Deal {idx}"),
                    "description": item.get("synopsis", "")[:500],
                    "seller": item.get("seller", {}).get("name", "Undisclosed"),
                    "buyer": item.get("buyer", {}).get("name", "Undisclosed"),
                    "region": self._normalise_region(item.get("region", "")),
                    "transactionType": _TX_TYPE_MAP.get(mm_type, "Funds"),
                    "assetClass": item.get("assetClass", "Buyout"),
                    "discountToNav": item.get("discountToNav"),
                    "transactionSize": item.get("dealValue"),  # in $M
                    "status": _STATUS_MAP.get(mm_status, "Active"),
                    "createdAt": item.get("announcedDate", ""),
                    "source": "mergermarket",
                    # Extra Mergermarket metadata
                    "_mm_id": item.get("dealId"),
                    "_mm_type": mm_type,
                    "_mm_url": item.get("url", ""),
                })
        except requests.RequestException as exc:
            logger.warning("Mergermarket deal fetch failed: %s", exc)

        return deals

    # ── News / Intelligence ────────────────────────────────

    def fetch_intelligence(
        self,
        keywords: Optional[List[str]] = None,
        max_results: int = 30,
    ) -> List[dict]:
        """
        Pull Mergermarket intelligence articles (for News tab).
        """
        if not self.is_connected():
            return []

        keywords = keywords or [
            "secondary", "secondaries", "GP-led", "continuation vehicle",
            "private equity fund", "LP stake",
        ]

        articles: List[dict] = []
        try:
            resp = self._session.get(
                f"{self._base}/intelligence/search",
                params={
                    "query": " OR ".join(keywords),
                    "limit": max_results,
                    "sortBy": "publishedDate",
                    "sortOrder": "desc",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            for idx, item in enumerate(data.get("articles", []), start=1):
                articles.append({
                    "id": idx,
                    "title": item.get("headline", ""),
                    "summary": (item.get("body", "") or "")[:500],
                    "link": item.get("url", ""),
                    "published": item.get("publishedDate", ""),
                    "source": "Mergermarket",
                    "sourceColor": "#dc2626",
                    "themes": [],
                    "regionTags": [],
                    "assetTags": [],
                })
        except requests.RequestException as exc:
            logger.warning("Mergermarket intelligence fetch failed: %s", exc)

        return articles

    # ── Helpers ──────────────────────────────────────────────

    @staticmethod
    def _normalise_region(raw: str) -> str:
        r = raw.lower()
        if any(k in r for k in ["north america", "united states", "usa", "canada"]):
            return "North America"
        if any(k in r for k in ["europe", "uk", "nordic", "dach"]):
            return "Europe"
        if any(k in r for k in ["asia", "china", "japan", "india", "apac"]):
            return "Asia"
        if any(k in r for k in ["latin", "brazil", "mexico"]):
            return "LatAm"
        return raw or "Global"
