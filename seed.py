"""
Sutanto Capital — Seed Data Service
Provides static/demo data when external APIs are not connected.
"""

from __future__ import annotations
from typing import List


def seed_deals() -> List[dict]:
    return [
        {"id": 1, "dealName": "Lexington Co-Investment IV", "description": "Secondary interest in diversified buyout fund", "seller": "Lexington Capital", "buyer": "Apollo Global", "region": "North America", "transactionType": "Funds", "assetClass": "Buyout", "discountToNav": 12.5, "transactionSize": 25, "status": "Active", "createdAt": "2024-01-15", "source": "manual"},
        {"id": 2, "dealName": "CVC Capital Partners VIII", "description": "Large European buyout fund interest", "seller": "Pantheon", "buyer": "Ardian", "region": "Europe", "transactionType": "Funds", "assetClass": "Buyout", "discountToNav": 8.0, "transactionSize": 45, "status": "Closed", "createdAt": "2024-03-10", "source": "manual"},
        {"id": 3, "dealName": "Kohlberg Fund X", "description": "Mid-market buyout fund secondary", "seller": "Goldman Sachs AM", "buyer": "Lexington", "region": "North America", "transactionType": "Funds", "assetClass": "Buyout", "discountToNav": 14.3, "transactionSize": 38, "status": "Active", "createdAt": "2024-03-25", "source": "manual"},
        {"id": 4, "dealName": "Asia Growth Fund I", "description": "Asia-focused growth fund", "seller": "SoftBank Vision", "buyer": "Draper Esprit", "region": "Asia", "transactionType": "Funds", "assetClass": "Growth", "discountToNav": 22.5, "transactionSize": 18, "status": "Active", "createdAt": "2024-04-01", "source": "manual"},
        {"id": 5, "dealName": "Infrastructure Fund III", "description": "Core infrastructure fund stake", "seller": "Macquarie", "buyer": "Brookfield", "region": "Europe", "transactionType": "Directs", "assetClass": "Infrastructure", "discountToNav": 5.2, "transactionSize": 62, "status": "Under Review", "createdAt": "2024-04-10", "source": "manual"},
        {"id": 6, "dealName": "Brazil Buyout Co-invest", "description": "Brazilian buyout co-investment", "seller": "GP Capital", "buyer": "Advent International", "region": "LatAm", "transactionType": "Co-investments", "assetClass": "Buyout", "discountToNav": 16.8, "transactionSize": 22, "status": "Active", "createdAt": "2024-04-15", "source": "manual"},
        {"id": 7, "dealName": "Real Assets Fund V", "description": "Real estate and infrastructure blend", "seller": "BlackRock", "buyer": "Insight Partners", "region": "North America", "transactionType": "Funds", "assetClass": "Real Assets", "discountToNav": 9.5, "transactionSize": 55, "status": "Draft", "createdAt": "2024-04-20", "source": "manual"},
        {"id": 8, "dealName": "India Tech Fund II", "description": "India-focused VC fund", "seller": "Sequoia India", "buyer": "Lightspeed", "region": "Asia", "transactionType": "Funds", "assetClass": "VC", "discountToNav": 28.0, "transactionSize": 12, "status": "Active", "createdAt": "2024-05-01", "source": "manual"},
        {"id": 9, "dealName": "European Real Estate Co-invest", "description": "German logistics real estate", "seller": "Segro", "buyer": "Hansteen", "region": "Europe", "transactionType": "Co-investments", "assetClass": "Real Assets", "discountToNav": 11.2, "transactionSize": 30, "status": "Under Review", "createdAt": "2024-05-10", "source": "manual"},
        {"id": 10, "dealName": "Sequoia Capital XV", "description": "Venture fund secondary", "seller": "Harvard Management", "buyer": "Lexington", "region": "North America", "transactionType": "Funds", "assetClass": "VC", "discountToNav": 28.5, "transactionSize": 15, "status": "Active", "createdAt": "2024-01-08", "source": "manual"},
        {"id": 11, "dealName": "Silver Lake Fund VII", "description": "Technology buyout fund", "seller": "State Street", "buyer": "Lexington", "region": "North America", "transactionType": "Funds", "assetClass": "Buyout", "discountToNav": 13.7, "transactionSize": 65, "status": "Closed", "createdAt": "2024-05-05", "source": "manual"},
        {"id": 12, "dealName": "KKR North America Fund XIV", "description": "Large cap buyout secondary", "seller": "Cambridge Associates", "buyer": "Ardian", "region": "North America", "transactionType": "Funds", "assetClass": "Buyout", "discountToNav": 10.2, "transactionSize": 78, "status": "Active", "createdAt": "2024-03-18", "source": "manual"},
        {"id": 13, "dealName": "General Atlantic Fund XVII", "description": "Growth equity fund", "seller": "Cambridge Associates", "buyer": "Lexington", "region": "North America", "transactionType": "Funds", "assetClass": "Growth", "discountToNav": 19.5, "transactionSize": 38, "status": "Active", "createdAt": "2024-01-12", "source": "manual"},
        {"id": 14, "dealName": "Brookfield Infrastructure V", "description": "Global infrastructure", "seller": "Cambridge Associates", "buyer": "Lexington", "region": "North America", "transactionType": "Funds", "assetClass": "Infrastructure", "discountToNav": 6.8, "transactionSize": 55, "status": "Active", "createdAt": "2024-01-18", "source": "manual"},
        {"id": 15, "dealName": "Blackstone Real Estate Partners IX", "description": "Real estate fund", "seller": "Cambridge Associates", "buyer": "Lexington", "region": "North America", "transactionType": "Funds", "assetClass": "Real Assets", "discountToNav": 10.8, "transactionSize": 62, "status": "Active", "createdAt": "2024-01-22", "source": "manual"},
        {"id": 16, "dealName": "EQT Fund IX", "description": "Nordic buyout fund", "seller": "Nordea", "buyer": "Pantheon", "region": "Europe", "transactionType": "Funds", "assetClass": "Buyout", "discountToNav": 11.2, "transactionSize": 44, "status": "Closed", "createdAt": "2024-02-28", "source": "manual"},
        {"id": 17, "dealName": "European Growth Fund IV", "description": "Pan-European growth", "seller": "Allianz", "buyer": "Lexington", "region": "Europe", "transactionType": "Funds", "assetClass": "Growth", "discountToNav": 16.4, "transactionSize": 24, "status": "Closed", "createdAt": "2024-02-08", "source": "manual"},
        {"id": 18, "dealName": "Hillhouse Fund V", "description": "Asia Buyout Fund", "seller": "Sequoia Capital", "buyer": "GIC", "region": "Asia", "transactionType": "Funds", "assetClass": "Buyout", "discountToNav": 18.4, "transactionSize": 42, "status": "Active", "createdAt": "2024-01-25", "source": "manual"},
        {"id": 19, "dealName": "China Growth Fund IV", "description": "China tech fund", "seller": "Hillhouse", "buyer": "Sequoia", "region": "Asia", "transactionType": "Funds", "assetClass": "VC", "discountToNav": 25.4, "transactionSize": 19, "status": "Closed", "createdAt": "2024-02-10", "source": "manual"},
        {"id": 20, "dealName": "Mexico Infrastructure Fund", "description": "Mexican infrastructure", "seller": "BlackRock", "buyer": "Brookfield", "region": "LatAm", "transactionType": "Funds", "assetClass": "Infrastructure", "discountToNav": 12.3, "transactionSize": 28, "status": "Active", "createdAt": "2024-01-28", "source": "manual"},
    ]


def seed_assets() -> List[dict]:
    return [
        {"id": 1, "assetName": "North America Buyout Fund VII", "assetClass": "Buyout", "region": "North America", "nav": 85, "weight": 25, "description": "Large cap buyout fund", "included": True, "selectedCompId": None},
        {"id": 2, "assetName": "Asia Growth Fund III", "assetClass": "Growth", "region": "Asia", "nav": 45, "weight": 15, "description": "Asia growth fund", "included": True, "selectedCompId": None},
        {"id": 3, "assetName": "US Venture Fund XII", "assetClass": "VC", "region": "North America", "nav": 120, "weight": 35, "description": "US venture fund", "included": True, "selectedCompId": None},
        {"id": 4, "assetName": "European Infrastructure Co-invest", "assetClass": "Infrastructure", "region": "Europe", "nav": 55, "weight": 20, "description": "European infrastructure", "included": True, "selectedCompId": None},
        {"id": 5, "assetName": "Real Assets Fund II", "assetClass": "Real Assets", "region": "North America", "nav": 20, "weight": 5, "description": "Real assets blend", "included": True, "selectedCompId": None},
    ]
