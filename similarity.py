"""
Sutanto Capital — Similarity Service
Scores deals against portfolio assets to find comparable transactions.
"""

from __future__ import annotations
from typing import List


def find_similar_deals(asset: dict, deals: List[dict], limit: int = 5) -> List[dict]:
    """Score each deal against the given asset and return top matches."""
    scored = []
    for deal in deals:
        score = 0
        reasons = []

        if deal.get("assetClass") == asset.get("assetClass"):
            score += 10
            reasons.append("Same asset class")

        if deal.get("region") == asset.get("region"):
            score += 5
            reasons.append("Same region")

        if deal.get("transactionType") in ("Directs", "Co-investments"):
            score += 3
            reasons.append("Similar transaction type")

        deal_size = deal.get("transactionSize") or 0
        asset_nav = asset.get("nav", 1)
        if asset_nav and abs(deal_size - asset_nav) < asset_nav * 0.3:
            score += 2
            reasons.append("Similar size")

        if score > 0:
            scored.append({
                **deal,
                "score": score,
                "explanation": ", ".join(reasons),
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]
