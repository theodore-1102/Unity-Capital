"""
S&P Capital IQ API Client
==========================
Connects to S&P Global Market Intelligence (Capital IQ) REST API to pull:
  • PE transaction data (feeds directly into Recent PE Deals tab)
  • Company fundamentals for deal enrichment
  • Industry classifications (GICS)

Requires: SP_CAPITALIQ_API_KEY + SP_CAPITALIQ_USERNAME + SP_CAPITALIQ_PASSWORD

S&P Capital IQ GDS API reference:
  https://developer.spglobal.com/
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from app.config import SPCapitalIQConfig

logger = logging.getLogger(__name__)

# Geography → flag emoji for UI
GEO_FLAGS = {
    "United States": "\U0001f1fa\U0001f1f8",
    "USA": "\U0001f1fa\U0001f1f8",
    "United Kingdom": "\U0001f1ec\U0001f1e7",
    "China": "\U0001f1e8\U0001f1f3",
    "France": "\U0001f1eb\U0001f1f7",
    "Germany": "\U0001f1e9\U0001f1ea",
    "India": "\U0001f1ee\U0001f1f3",
    "Singapore": "\U0001f1f8\U0001f1ec",
    "Italy": "\U0001f1ee\U0001f1f9",
    "Canada": "\U0001f1e8\U0001f1e6",
    "Japan": "\U0001f1ef\U0001f1f5",
    "South Korea": "\U0001f1f0\U0001f1f7",
    "Brazil": "\U0001f1e7\U0001f1f7",
    "Australia": "\U0001f1e6\U0001f1fa",
}


class SPCapitalIQClient:
    """Wrapper for S&P Capital IQ GDS REST API."""

    # CIQ PE transaction types we query
    PE_TX_TYPES = [
        "Private Placement",
        "Leveraged Buyout",
        "Management Buyout",
        "Venture Capital",
        "Growth Capital",
        "Acquisition",
        "Merger",
    ]

    def __init__(self, config: SPCapitalIQConfig):
        self._cfg = config
        self._session = requests.Session()
        self._base = config.base_url.rstrip("/")
        self._token: Optional[str] = None
        self._token_expiry: float = 0

    # ── Connection ──────────────────────────────────────────

    def is_connected(self) -> bool:
        return self._cfg.enabled

    def connection_error(self) -> dict:
        return {
            "connected": False,
            "provider": "sp_capitaliq",
            "label": "S&P Capital IQ",
            "message": (
                "S&P Capital IQ credentials not configured. "
                "Set SP_CAPITALIQ_API_KEY, SP_CAPITALIQ_USERNAME, and "
                "SP_CAPITALIQ_PASSWORD in your .env file to enable "
                "live PE transaction data from Capital IQ."
            ),
        }

    # ── Authentication ──────────────────────────────────────

    def _authenticate(self) -> bool:
        """Obtain OAuth token from S&P Capital IQ."""
        if not self.is_connected():
            return False

        import time
        if self._token and time.time() < self._token_expiry:
            return True

        try:
            resp = requests.post(
                f"{self._base}/auth/token",
                json={
                    "username": self._cfg.username,
                    "password": self._cfg.password,
                    "apiKey": self._cfg.api_key,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data.get("accessToken")
            self._token_expiry = time.time() + data.get("expiresIn", 3600) - 60
            self._session.headers.update({
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
            })
            return True
        except requests.RequestException as exc:
            logger.warning("S&P CIQ authentication failed: %s", exc)
            return False

    # ── PE Transactions ─────────────────────────────────────

    def fetch_pe_transactions(
        self,
        days_back: int = 30,
        geography: Optional[str] = None,
        status: Optional[str] = None,
        activity: Optional[str] = None,
        tx_type: Optional[str] = None,
        max_results: int = 200,
    ) -> List[dict]:
        """
        Pull PE transactions from S&P Capital IQ.

        Returns list of dicts compatible with PETransaction model:
            {txId, date, status, company, industry, geography, txType,
             tags, features, investors, portfolioStatus, activity, amount}
        """
        if not self.is_connected():
            return []

        if not self._authenticate():
            return []

        since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        params: Dict[str, Any] = {
            "transactionTypes": ",".join(self.PE_TX_TYPES),
            "dateFrom": since,
            "limit": max_results,
            "includeInvestors": True,
            "includeFeatures": True,
            "sortBy": "announcedDate",
            "sortOrder": "desc",
        }
        if geography:
            params["geography"] = geography
        if status:
            params["transactionStatus"] = status
        if activity:
            params["peActivity"] = activity
        if tx_type:
            params["transactionType"] = tx_type

        transactions: List[dict] = []
        try:
            resp = self._session.get(
                f"{self._base}/transactions/pe",
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("transactions", []):
                # Map activity types
                activities = []
                raw_activity = item.get("peActivity", [])
                if isinstance(raw_activity, str):
                    raw_activity = [raw_activity]
                for act in raw_activity:
                    if "entry" in act.lower():
                        activities.append("Entry")
                    elif "exit" in act.lower():
                        activities.append("Exit")
                    elif "stake" in act.lower():
                        activities.append("Stake Increase/Decrease")

                # Extract investors
                investors = []
                for inv in item.get("investors", []):
                    inv_name = inv.get("name", "")
                    if inv_name:
                        investors.append(inv_name)

                # Extract features
                features = []
                for feat in item.get("features", []):
                    feat_name = feat.get("name", feat) if isinstance(feat, dict) else str(feat)
                    features.append(feat_name)

                # Extract tags / topics
                tags = item.get("topicTags", [])
                if isinstance(tags, str):
                    tags = [tags]

                transactions.append({
                    "txId": item.get("transactionId", ""),
                    "date": item.get("announcedDate", ""),
                    "status": item.get("status", "Pending"),
                    "company": item.get("targetCompany", {}).get("name", "Unknown"),
                    "industry": item.get("primaryIndustry", "N/A"),
                    "geography": item.get("geography", "Unknown"),
                    "txType": item.get("transactionType", ""),
                    "tags": tags,
                    "features": features,
                    "investors": investors,
                    "portfolioStatus": item.get("portfolioStatus", "Current"),
                    "activity": activities or ["Entry"],
                    "amount": item.get("dealAmount"),
                })
        except requests.RequestException as exc:
            logger.warning("S&P CIQ transaction fetch failed: %s", exc)

        return transactions

    # ── Company Lookup (for deal enrichment) ────────────────

    def lookup_company(self, company_name: str) -> Optional[dict]:
        """Search for a company and return basic fundamentals."""
        if not self.is_connected() or not self._authenticate():
            return None

        try:
            resp = self._session.get(
                f"{self._base}/companies/search",
                params={"query": company_name, "limit": 1},
                timeout=10,
            )
            resp.raise_for_status()
            results = resp.json().get("companies", [])
            if results:
                co = results[0]
                return {
                    "ciqId": co.get("companyId"),
                    "name": co.get("companyName"),
                    "industry": co.get("primaryIndustry"),
                    "geography": co.get("country"),
                    "revenue": co.get("totalRevenue"),
                    "employees": co.get("employees"),
                }
        except requests.RequestException as exc:
            logger.warning("S&P CIQ company lookup failed: %s", exc)

        return None
