"""
Sutanto Capital — Flask Routes
All API endpoints and page-serving routes.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request, render_template
from app.services.similarity import find_similar_deals

api = Blueprint("api", __name__)
pages = Blueprint("pages", __name__)


def _get_state():
    """Retrieve shared application state from Flask app config."""
    from flask import current_app
    return current_app.config["APP_STATE"]


def _get_clients():
    from flask import current_app
    return current_app.config["API_CLIENTS"]


# ── Pages ───────────────────────────────────────────────────

@pages.route("/")
def index():
    state = _get_state()
    clients = _get_clients()
    api_status = {}
    for name, client in clients.items():
        if hasattr(client, "connection_error"):
            api_status[name] = (
                {"connected": True, "label": name}
                if client.is_connected()
                else client.connection_error()
            )
    return render_template(
        "index.html",
        deals=state["deals"],
        my_assets=state["my_assets"],
        pe_deals=state["pe_deals"],
        api_status=api_status,
        mode=state.get("mode", "demo"),
    )


# ── Deals API ───────────────────────────────────────────────

@api.route("/api/deals", methods=["GET"])
def get_deals():
    state = _get_state()
    return jsonify(state["deals"])


@api.route("/api/similar_deals", methods=["POST"])
def similar_deals():
    state = _get_state()
    asset = request.json.get("asset", {})
    comps = find_similar_deals(asset, state["deals"], 5)
    return jsonify(comps)


@api.route("/api/save_deal", methods=["POST"])
def save_deal():
    state = _get_state()
    data = request.json
    deal_data = data.get("deal", {})
    deal_id = data.get("id")

    if deal_id:
        for i, d in enumerate(state["deals"]):
            if d["id"] == deal_id:
                state["deals"][i] = {**state["deals"][i], **deal_data}
                break
    else:
        deal_data["id"] = state["next_deal_id"]
        deal_data["createdAt"] = "2024-06-01"
        deal_data["source"] = "manual"
        state["deals"].append(deal_data)
        state["next_deal_id"] += 1

    return jsonify({"deals": state["deals"]})


# ── Assets API ──────────────────────────────────────────────

@api.route("/api/save_asset", methods=["POST"])
def save_asset():
    state = _get_state()
    asset_data = request.json.get("asset", {})
    asset_data["id"] = state["next_asset_id"]
    state["my_assets"].append(asset_data)
    state["next_asset_id"] += 1
    return jsonify({"myAssets": state["my_assets"]})


@api.route("/api/toggle_include", methods=["POST"])
def toggle_include():
    state = _get_state()
    asset_id = request.json.get("id")
    for asset in state["my_assets"]:
        if asset["id"] == asset_id:
            asset["included"] = not asset["included"]
            break
    return jsonify({"myAssets": state["my_assets"]})


@api.route("/api/delete_asset", methods=["POST"])
def delete_asset():
    state = _get_state()
    asset_id = request.json.get("id")
    state["my_assets"] = [a for a in state["my_assets"] if a["id"] != asset_id]
    return jsonify({"myAssets": state["my_assets"]})


@api.route("/api/update_asset_comp", methods=["POST"])
def update_asset_comp():
    state = _get_state()
    data = request.json
    asset_id = data.get("assetId")
    comp_id = data.get("compId")
    for asset in state["my_assets"]:
        if asset["id"] == asset_id:
            asset["selectedCompId"] = comp_id
            break
    return jsonify({"myAssets": state["my_assets"]})


# ── News API ────────────────────────────────────────────────

@api.route("/api/news", methods=["GET"])
def news():
    state = _get_state()
    return jsonify({
        "articles": state.get("news_articles", []),
        "themeStats": [],
        "connections": [],
        "lastUpdated": "Now",
        "sources": [],
        "hasFeedparser": True,
    })


@api.route("/api/news/refresh", methods=["POST"])
def refresh_news():
    # In live mode, this would re-fetch from Bloomberg/Google/etc.
    state = _get_state()
    return jsonify({
        "articles": state.get("news_articles", []),
        "themeStats": [],
        "connections": [],
        "lastUpdated": "Now",
        "sources": [],
        "hasFeedparser": True,
    })


# ── PE Deals API ────────────────────────────────────────────

@api.route("/api/pe_deals", methods=["GET"])
def pe_deals():
    state = _get_state()
    return jsonify(state.get("pe_deals", []))


# ── API Status ──────────────────────────────────────────────

@api.route("/api/status", methods=["GET"])
def api_status():
    clients = _get_clients()
    status = {}
    for name, client in clients.items():
        if hasattr(client, "is_connected"):
            status[name] = {
                "connected": client.is_connected(),
                "label": getattr(client, "connection_error", lambda: {"label": name})()
                    .get("label", name) if not client.is_connected() else name,
            }
    return jsonify(status)
