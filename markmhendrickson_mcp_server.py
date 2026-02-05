#!/usr/bin/env python3
"""
MCP server for markmhendrickson.com website content.

Provides read-only access to posts, links, and timeline records stored in parquet.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

SERVER_DIR = Path(__file__).resolve().parent
REPO_ROOT = SERVER_DIR.parent.parent

sys.path.insert(0, str(REPO_ROOT / "execution" / "scripts"))

load_dotenv(REPO_ROOT / ".env")
load_dotenv(SERVER_DIR / ".env")

from parquet_client import ParquetMCPClient

app = Server("markmhendrickson")


def _error_response(message: str) -> List[TextContent]:
    return [TextContent(type="text", text=json.dumps({"success": False, "error": message}))]


def _get_parquet_client() -> ParquetMCPClient:
    parquet_server_path = REPO_ROOT / "mcp" / "parquet" / "parquet_mcp_server.py"
    return ParquetMCPClient(parquet_server_path=str(parquet_server_path))


async def _read_data(data_type: str, filters: dict[str, Any] | None) -> dict[str, Any]:
    def _call() -> dict[str, Any]:
        client = _get_parquet_client()
        args: dict[str, Any] = {"data_type": data_type}
        if filters:
            args["filters"] = filters
        return client.call_tool_sync("read_parquet", args)

    result = await asyncio.to_thread(_call)
    data = result.get("data", [])
    return {"success": True, "data": data, "count": len(data)}


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
            description="Return post records from parquet. Optional filters supported.",
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
            description="Return links records from parquet. Optional filters supported.",
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
            description="Return timeline records from parquet. Optional filters supported.",
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
