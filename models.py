"""
Sutanto Capital — Data Models
Plain dataclass models used across the platform.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional, List


# ── Deal (Secondary Deal Database) ──────────────────────────

@dataclass
class Deal:
    id: int
    dealName: str
    seller: str
    buyer: str
    region: str
    transactionType: str
    assetClass: str
    description: str = ""
    discountToNav: Optional[float] = None
    transactionSize: Optional[float] = None
    status: str = "Draft"
    createdAt: str = ""
    source: str = "manual"           # manual | mergermarket | secondaries_investor

    def to_dict(self) -> dict:
        return asdict(self)


# ── PE Asset (My PE Assets) ─────────────────────────────────

@dataclass
class PEAsset:
    id: int
    assetName: str
    assetClass: str
    region: str
    nav: float
    weight: float = 0.0
    description: str = ""
    included: bool = True
    selectedCompId: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


# ── News Article ────────────────────────────────────────────

@dataclass
class NewsArticle:
    id: int
    title: str
    summary: str = ""
    link: str = ""
    published: str = ""
    source: str = ""
    sourceColor: str = "#6b7280"
    themes: List[str] = field(default_factory=list)
    regionTags: List[str] = field(default_factory=list)
    assetTags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ── PE Transaction (Recent PE Deals — S&P CIQ style) ───────

@dataclass
class PETransaction:
    txId: str
    date: str
    status: str
    company: str
    industry: str
    geography: str
    txType: str
    tags: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    investors: List[str] = field(default_factory=list)
    portfolioStatus: str = "Current"
    activity: List[str] = field(default_factory=list)
    amount: Optional[float] = None

    def to_dict(self) -> dict:
        return asdict(self)
