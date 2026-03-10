"""
Google Custom Search API Client
================================
Uses Google Custom Search JSON API to pull PE/secondaries news articles.
Feeds into the Private Markets News tab alongside Bloomberg & Mergermarket.

Requires: GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_CX

Reference: https://developers.google.com/custom-search/v1/reference/rest
"""

from __future__ import annotations

import logging
from typing import List, Optional

import requests

from app.config import GoogleSearchConfig

logger = logging.getLogger(__name__)

# Pre-built search queries for PE secondaries news
DEFAULT_QUERIES = [
    "private equity secondary market deals",
    "GP-led secondary continuation fund",
    "private equity fundraising close",
    "LP secondary stake sale",
    "private equity buyout announcement",
    "private credit direct lending fund",
    "infrastructure fund investment",
    "venture capital fund raise",
    "private equity secondaries pricing",
    "PE co-investment deal",
]

# Source → colour mapping for the news UI
SOURCE_COLORS = {
    "reuters.com": "#f97316",
    "bloomberg.com": "#1a1a2e",
    "ft.com": "#cc0000",
    "cnbc.com": "#2563eb",
    "wsj.com": "#374151",
    "pitchbook.com": "#064e3b",
    "preqin.com": "#065f46",
    "privateequitywire.co.uk": "#10b981",
    "pehub.com": "#0891b2",
    "secondariesinvestor.com": "#6d28d9",
    "institutionalinvestor.com": "#6b21a8",
    "buyoutsinsider.com": "#dc2626",
}


class GoogleSearchClient:
    """Wrapper for Google Custom Search JSON API."""

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, config: GoogleSearchConfig):
        self._cfg = config
        self._session = requests.Session()

    # ── Connection ──────────────────────────────────────────

    def is_connected(self) -> bool:
        return self._cfg.enabled and bool(self._cfg.cx)

    def connection_error(self) -> dict:
        return {
            "connected": False,
            "provider": "google_search",
            "label": "Google Search API",
            "message": (
                "Google Custom Search credentials not configured. "
                "Set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX in your "
                ".env file to enable web-sourced PE news."
            ),
        }

    # ── Search ──────────────────────────────────────────────

    def search(
        self,
        query: str,
        max_results: int = 10,
        date_restrict: str = "d7",   # last 7 days
    ) -> List[dict]:
        """
        Run a single search query. Returns raw Google items.
        date_restrict: d[N] days, w[N] weeks, m[N] months
        """
        if not self.is_connected():
            return []

        try:
            resp = self._session.get(
                self.BASE_URL,
                params={
                    "key": self._cfg.api_key,
                    "cx": self._cfg.cx,
                    "q": query,
                    "num": min(max_results, 10),
                    "dateRestrict": date_restrict,
                    "sort": "date",
                },
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("items", [])
        except requests.RequestException as exc:
            logger.warning("Google search failed for '%s': %s", query, exc)
            return []

    # ── Batch News Fetch ────────────────────────────────────

    def fetch_pe_news(
        self,
        queries: Optional[List[str]] = None,
        max_per_query: int = 5,
    ) -> List[dict]:
        """
        Run multiple PE-themed queries and de-duplicate results.

        Returns list of dicts compatible with NewsArticle model:
            {title, summary, link, published, source, sourceColor, ...}
        """
        if not self.is_connected():
            return []

        queries = queries or DEFAULT_QUERIES
        seen_urls: set = set()
        articles: List[dict] = []
        article_id = 1

        for q in queries:
            items = self.search(q, max_results=max_per_query)
            for item in items:
                link = item.get("link", "")
                if link in seen_urls:
                    continue
                seen_urls.add(link)

                # Determine source from display link
                display = (item.get("displayLink") or "").lower()
                source_color = "#4285f4"
                source_name = display.replace("www.", "").split("/")[0] if display else "Web"
                for domain, color in SOURCE_COLORS.items():
                    if domain in display:
                        source_color = color
                        break

                articles.append({
                    "id": article_id,
                    "title": item.get("title", ""),
                    "summary": (item.get("snippet") or "")[:500],
                    "link": link,
                    "published": item.get("pagemap", {})
                        .get("metatags", [{}])[0]
                        .get("article:published_time", ""),
                    "source": source_name.title(),
                    "sourceColor": source_color,
                    "themes": [],
                    "regionTags": [],
                    "assetTags": [],
                })
                article_id += 1

        return articles
