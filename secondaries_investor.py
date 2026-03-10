"""
Secondaries Investor API Client
=================================
Connects to the Secondaries Investor (PEI Media) API to pull:
  • Specialist secondary market deal data (feeds into Secondary Deal Database)
  • LP-led and GP-led transaction details
  • Pricing benchmarks (discount-to-NAV ranges by asset class)

Requires: SECONDARIES_INVESTOR_API_KEY

Secondaries Investor is published by PEI Media (Private Equity International).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from app.config import SecondariesInvestorConfig

logger = logging.getLogger(__name__)

# Transaction structure categories tracked by Secondaries Investor
STRUCTURE_TYPES = [
    "LP Portfolio Sale (Strip)",
    "LP Portfolio Sale (Mosaic / Cherry-pick)",
    "GP-Led Continuation Vehicle (Single Asset)",
    "GP-Led Continuation Vehicle (Multi-Asset)",
    "GP-Led Tender Offer",
    "Preferred Equity",
    "Stapled Secondary",
    "GP Stake Sale",
    "Annex Fund / Top-Up",
    "Deferred Payment Structure",
    "NAV Loan / NAV Financing",
]


class SecondariesInvestorClient:
    """Wrapper for Secondaries Investor (PEI Media) API."""

    def __init__(self, config: SecondariesInvestorConfig):
        self._cfg = config
        self._session = requests.Session()
        if config.api_key:
            self._session.headers.update({
                "Authorization": f"Bearer {config.api_key}",
                "Accept": "application/json",
            })
        self._base = config.base_url.rstrip("/")

    # ── Connection ──────────────────────────────────────────

    def is_connected(self) -> bool:
        return self._cfg.enabled

    def connection_error(self) -> dict:
        return {
            "connected": False,
            "provider": "secondaries_investor",
            "label": "Secondaries Investor",
            "message": (
                "Secondaries Investor API key not configured. "
                "Set SECONDARIES_INVESTOR_API_KEY in your .env file "
                "to enable specialist secondary deal data from PEI Media."
            ),
        }

    # ── Secondary Deals ─────────────────────────────────────

    def fetch_deals(
        self,
        region: Optional[str] = None,
        asset_class: Optional[str] = None,
        structure_type: Optional[str] = None,
        days_back: int = 180,
        max_results: int = 100,
    ) -> List[dict]:
        """
        Pull specialist secondary deals.

        Returns list of dicts compatible with the Deal model.
        Includes secondary-specific fields:
            _si_structure, _si_pricing_range, _si_gp_led, _si_deferred
        """
        if not self.is_connected():
            return []

        since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        params: Dict[str, Any] = {
            "dateFrom": since,
            "limit": max_results,
            "sortBy": "closedDate",
            "sortOrder": "desc",
        }
        if region:
            params["region"] = region
        if asset_class:
            params["assetClass"] = asset_class
        if structure_type:
            params["structureType"] = structure_type

        deals: List[dict] = []
        try:
            resp = self._session.get(
                f"{self._base}/deals",
                params=params,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()

            for idx, item in enumerate(data.get("deals", []), start=1):
                is_gp_led = item.get("isGPLed", False)
                structure = item.get("structureType", "LP Portfolio Sale (Strip)")

                # Determine transaction type from structure
                if "continuation" in structure.lower() or is_gp_led:
                    tx_type = "Directs" if "single" in structure.lower() else "Funds"
                elif "co-invest" in structure.lower():
                    tx_type = "Co-investments"
                else:
                    tx_type = "Funds"

                deals.append({
                    "id": None,  # assigned by app
                    "dealName": item.get("dealName", f"SI-{idx}"),
                    "description": item.get("description", "")[:500],
                    "seller": item.get("seller", "Undisclosed"),
                    "buyer": item.get("buyer", "Undisclosed"),
                    "region": item.get("region", "Global"),
                    "transactionType": tx_type,
                    "assetClass": item.get("assetClass", "Buyout"),
                    "discountToNav": item.get("discountToNav"),
                    "transactionSize": item.get("dealSize"),
                    "status": self._map_status(item.get("status", "Closed")),
                    "createdAt": item.get("closedDate", ""),
                    "source": "secondaries_investor",
                    # Secondary-specific metadata
                    "_si_structure": structure,
                    "_si_pricing_range": item.get("pricingRange"),
                    "_si_gp_led": is_gp_led,
                    "_si_deferred": item.get("deferredPercentage"),
                    "_si_preferred_equity": item.get("hasPreferredEquity", False),
                    "_si_num_funds": item.get("numberOfFunds"),
                    "_si_vintage_years": item.get("vintageYears", []),
                })
        except requests.RequestException as exc:
            logger.warning("Secondaries Investor deal fetch failed: %s", exc)

        return deals

    # ── Pricing Benchmarks ──────────────────────────────────

    def fetch_pricing_benchmarks(self) -> List[dict]:
        """
        Pull secondary market pricing benchmarks by asset class.
        Returns median bid, ask, and mid for each category.
        """
        if not self.is_connected():
            return []

        try:
            resp = self._session.get(
                f"{self._base}/benchmarks/pricing",
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("benchmarks", [])
        except requests.RequestException as exc:
            logger.warning("Secondaries Investor benchmark fetch failed: %s", exc)
            return []

    # ── News / Analysis ─────────────────────────────────────

    def fetch_articles(self, max_results: int = 20) -> List[dict]:
        """
        Pull editorial / analysis articles for the News tab.
        """
        if not self.is_connected():
            return []

        articles: List[dict] = []
        try:
            resp = self._session.get(
                f"{self._base}/articles",
                params={"limit": max_results, "sortBy": "publishedDate"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            for idx, item in enumerate(data.get("articles", []), start=1):
                articles.append({
                    "id": idx,
                    "title": item.get("headline", ""),
                    "summary": (item.get("abstract", "") or "")[:500],
                    "link": item.get("url", ""),
                    "published": item.get("publishedDate", ""),
                    "source": "Secondaries Investor",
                    "sourceColor": "#6d28d9",
                    "themes": [],
                    "regionTags": [],
                    "assetTags": [],
                })
        except requests.RequestException as exc:
            logger.warning("Secondaries Investor articles fetch failed: %s", exc)

        return articles

    # ── Helpers ──────────────────────────────────────────────

    @staticmethod
    def _map_status(raw: str) -> str:
        mapping = {
            "Closed": "Closed",
            "In Market": "Active",
            "Under Negotiation": "Under Review",
            "LOI Signed": "Active",
            "Cancelled": "Draft",
        }
        return mapping.get(raw, "Active")
