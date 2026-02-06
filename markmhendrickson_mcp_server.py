#!/usr/bin/env python3
"""
MCP server for markmhendrickson.com website content.

Provides read-only access to posts, links, and timeline by fetching
production JSON endpoints. No local parquet or DATA_DIR required.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, List

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

BASE_URL = "https://markmhendrickson.com/api"
ENDPOINTS = {"posts": f"{BASE_URL}/posts.json", "links": f"{BASE_URL}/links.json", "timeline": f"{BASE_URL}/timeline.json"}

app = Server("markmhendrickson")


def _error_response(message: str) -> List[TextContent]:
    return [TextContent(type="text", text=json.dumps({"success": False, "error": message}))]


def _apply_filters(items: List[dict], filters: dict[str, Any] | None) -> List[dict]:
    if not filters or not items:
        return items
    out = []
    for item in items:
        match = True
        for key, value in filters.items():
            if key not in item or item[key] != value:
                match = False
                break
        if match:
            out.append(item)
    return out


async def _fetch_json(url: str) -> List[dict]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Production returns { "url": "...", "posts": [...] } or { "links": [...] } etc.
        for key in ("posts", "links", "timeline", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]
    return []


async def _read_data(data_type: str, filters: dict[str, Any] | None) -> dict[str, Any]:
    url = ENDPOINTS.get(data_type)
    if not url:
        return {"success": False, "error": f"Unknown data type: {data_type}", "data": [], "count": 0}
    try:
        raw = await _fetch_json(url)
        data = _apply_filters(raw, filters)
        return {"success": True, "data": data, "count": len(data)}
    except httpx.HTTPError as e:
        return {"success": False, "error": str(e), "data": [], "count": 0}


async def _get_home_post() -> dict[str, Any]:
    data = await _read_data("posts", {"slug": "professional-mission"})
    posts = data.get("data", [])
    if not posts:
        return {"success": False, "error": "Home post not found", "slug": "professional-mission"}
    return {"success": True, "data": posts[0]}


@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="markmhendrickson_get_posts",
            description="Return post records from production (markmhendrickson.com). Optional filters supported. Production serves published posts only.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply (e.g., {\"published\": true})",
                    }
                },
            },
        ),
        Tool(
            name="markmhendrickson_get_links",
            description="Return links records from production (markmhendrickson.com). Optional filters supported.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply (e.g., {\"active\": true})",
                    }
                },
            },
        ),
        Tool(
            name="markmhendrickson_get_timeline",
            description="Return timeline records from production (markmhendrickson.com). Optional filters supported.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply (e.g., {\"entry_type\": \"work\"})",
                    }
                },
            },
        ),
        Tool(
            name="markmhendrickson_get_all_content",
            description="Return posts, links, and timeline records in a single response.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="markmhendrickson_get_about",
            description="Return the home post (about page) content.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    if not isinstance(arguments, dict):
        return _error_response("Invalid arguments. Expected an object.")

    try:
        if name == "markmhendrickson_get_posts":
            filters = arguments.get("filters")
            if filters is not None and not isinstance(filters, dict):
                return _error_response("Invalid filters. Expected an object.")
            data = await _read_data("posts", filters)
            return [TextContent(type="text", text=json.dumps(data))]

        if name == "markmhendrickson_get_links":
            filters = arguments.get("filters")
            if filters is not None and not isinstance(filters, dict):
                return _error_response("Invalid filters. Expected an object.")
            data = await _read_data("links", filters)
            return [TextContent(type="text", text=json.dumps(data))]

        if name == "markmhendrickson_get_timeline":
            filters = arguments.get("filters")
            if filters is not None and not isinstance(filters, dict):
                return _error_response("Invalid filters. Expected an object.")
            data = await _read_data("timeline", filters)
            return [TextContent(type="text", text=json.dumps(data))]

        if name == "markmhendrickson_get_all_content":
            posts = await _read_data("posts", None)
            links = await _read_data("links", None)
            timeline = await _read_data("timeline", None)
            result = {
                "success": True,
                "posts": posts.get("data", []),
                "links": links.get("data", []),
                "timeline": timeline.get("data", []),
            }
            result["counts"] = {
                "posts": len(result["posts"]),
                "links": len(result["links"]),
                "timeline": len(result["timeline"]),
            }
            return [TextContent(type="text", text=json.dumps(result))]

        if name == "markmhendrickson_get_about":
            result = await _get_home_post()
            return [TextContent(type="text", text=json.dumps(result))]

        return _error_response(f"Unknown tool: {name}")
    except Exception as exc:  # noqa: BLE001
        return _error_response(str(exc))


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
