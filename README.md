# Markmhendrickson MCP Server

Read-only MCP server that exposes [markmhendrickson.com](https://markmhendrickson.com) content to AI agents: posts, links, timeline, pages, meet, consulting, and investing. It fetches **production JSON only**; no local data or environment variables are required.

## Overview

| Aspect | Detail |
|--------|--------|
| **Data source** | Production API (`https://markmhendrickson.com/api/*.json`) |
| **Operations** | Read-only; no credentials or local storage |
| **Posts** | Published posts only (what is live on the site) |

## Data source

The server fetches from these public endpoints:

| Content | URL |
|---------|-----|
| Posts | `https://markmhendrickson.com/api/posts.json` |
| Links | `https://markmhendrickson.com/api/links.json` |
| Timeline | `https://markmhendrickson.com/api/timeline.json` |
| Pages | `https://markmhendrickson.com/api/pages.json` |
| Meet | `https://markmhendrickson.com/api/meet.json` |
| Consulting | `https://markmhendrickson.com/api/consulting.json` |
| Investing | `https://markmhendrickson.com/api/investing.json` |

Filtering is applied in memory after fetch. All filters use exact key-value match on top-level fields (e.g. `{"slug": "some-slug"}`, `{"entry_type": "work"}`).

## Tools

### Summary

| Tool | Purpose |
|------|--------|
| `markmhendrickson_get_posts` | Post records, with optional filters |
| `markmhendrickson_get_links` | Link records, with optional filters |
| `markmhendrickson_get_timeline` | Timeline records, with optional filters |
| `markmhendrickson_get_all_content` | Posts, links, timeline, pages, meet, consulting, and investing in one response |
| `markmhendrickson_get_about` | Home/about post (slug `professional-mission`) |
| `markmhendrickson_get_meet` | Meet page content |
| `markmhendrickson_get_consulting` | Consulting page content |
| `markmhendrickson_get_investing` | Investing page content |
| `markmhendrickson_get_pages` | Static pages index |

---

### `markmhendrickson_get_posts`

Returns post records from production. Production serves published posts only; drafts are not included.

**Parameters**

- `filters` (object, optional): Exact-match filters, e.g. `{"category": "technical"}`, `{"slug": "truth-layer-agent-memory"}`.

**Response**

- `success` (boolean)
- `data` (array of post objects)
- `count` (number)

**Example**

```json
// Request
{ "filters": { "slug": "truth-layer-agent-memory" } }

// Response
{
  "success": true,
  "data": [
    {
      "slug": "truth-layer-agent-memory",
      "title": "Building a truth layer for persistent agent memory",
      "published": true,
      "published_date": "2026-02-02",
      "category": "technical",
      "read_time": 6,
      "tags": "[\"truth-layer\", \"agents\"]"
    }
  ],
  "count": 1
}
```

---

### `markmhendrickson_get_links`

Returns link records (e.g. social, contact) from production.

**Parameters**

- `filters` (object, optional): Exact-match filters, e.g. `{"active": true}`.

**Response**

- `success`, `data` (array of link objects), `count`

**Example**

```json
// Request
{ "filters": { "active": true } }

// Response
{
  "success": true,
  "data": [
    {
      "name": "GitHub",
      "url": "https://github.com/markmhendrickson",
      "icon": "Github",
      "description": "Code repositories and open source projects",
      "display_order": 1
    }
  ],
  "count": 1
}
```

---

### `markmhendrickson_get_timeline`

Returns timeline records (e.g. work, education) from production.

**Parameters**

- `filters` (object, optional): Exact-match filters, e.g. `{"entry_type": "work"}`.

**Response**

- `success`, `data` (array of timeline objects), `count`

**Example**

```json
// Request
{ "filters": { "entry_type": "work" } }

// Response
{
  "success": true,
  "data": [
    {
      "role": "Founder",
      "company": "Startup (Neotoma & Ateles)",
      "date": "2025 – Present · Barcelona, Spain",
      "description": "[\"Building Neotoma...\"]"
    }
  ],
  "count": 1
}
```

---

### `markmhendrickson_get_all_content`

Fetches all endpoints and returns posts, links, timeline, pages, meet, consulting, and investing in one response. No parameters.

**Response**

- `success` (boolean)
- `posts` (array)
- `links` (array)
- `timeline` (array)
- `pages` (array)
- `meet` (array)
- `consulting` (array)
- `investing` (array)
- `counts` (object): `{ "posts": n, "links": n, "timeline": n, "pages": n, "meet": n, "consulting": n, "investing": n }`

**Example**

```json
{
  "success": true,
  "posts": [...],
  "links": [...],
  "timeline": [...],
  "pages": [...],
  "meet": [...],
  "consulting": [...],
  "investing": [...],
  "counts": {
    "posts": 25,
    "links": 8,
    "timeline": 12,
    "pages": 3,
    "meet": 1,
    "consulting": 1,
    "investing": 1
  }
}
```

---

### `markmhendrickson_get_meet`

Returns meet page content from production. No parameters.

**Response**

- `success`, `data` (array of meet page records), `count`

---

### `markmhendrickson_get_consulting`

Returns consulting page content from production. No parameters.

**Response**

- `success`, `data` (array of consulting page records), `count`

---

### `markmhendrickson_get_investing`

Returns investing page content from production. No parameters.

**Response**

- `success`, `data` (array of investing page records), `count`

---

### `markmhendrickson_get_pages`

Returns static pages index from production. No parameters.

**Response**

- `success`, `data` (array of page index records), `count`

---

### `markmhendrickson_get_about`

Returns the home/about post (slug `professional-mission`). No parameters.

**Response**

- `success`, `data` (single post object), or on failure `success: false`, `error`, and optionally `slug`.

**Example**

```json
{
  "success": true,
  "data": {
    "slug": "professional-mission",
    "title": "Mark Hendrickson",
    "published": true,
    "excerpt": "Building sovereign systems..."
  }
}
```

## Error responses

On failure, the server returns JSON with:

- `success`: `false`
- `error`: string (e.g. HTTP error, timeout)
- `data`: `[]` for list tools; omitted for `get_about`

Example: `{"success": false, "error": "Connection timeout", "data": [], "count": 0}`.

## Requirements

- Python 3.10+
- Dependencies: `mcp`, `httpx` (see `requirements.txt`)

## Installation

```bash
cd mcp/markmhendrickson
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

No environment variables are required. The server uses fixed production URLs.

### Cursor

Add to your MCP config (e.g. `.cursor/mcp.json`). The working directory for the command must be the repository root when using a relative path:

```json
{
  "mcpServers": {
    "markmhendrickson": {
      "command": "python3",
      "args": ["./mcp/markmhendrickson/markmhendrickson_mcp_server.py"]
    }
  }
}
```

### Claude Desktop

Use an absolute path so the server runs regardless of working directory:

```json
{
  "mcpServers": {
    "markmhendrickson": {
      "command": "python3",
      "args": ["/absolute/path/to/repo/mcp/markmhendrickson/markmhendrickson_mcp_server.py"]
    }
  }
}
```

If you use a venv, point `command` at the venv Python and ensure `httpx` is installed in that venv.

## Running

From the repo root:

```bash
./mcp/markmhendrickson/run-markmhendrickson-mcp.sh
```

The script uses the repo `execution/venv` if present, otherwise system `python3`.

## Troubleshooting

| Issue | What to do |
|-------|------------|
| `success: false` with connection/HTTP error | Check network; production site must be reachable. |
| Import or runtime error | Install deps: `pip install -r requirements.txt` (in the same env used to run the server). |
| Cursor doesn’t see the server | Ensure the MCP config path is correct and the process starts (check Cursor logs). |

## Security

- Read-only: the server does not write or modify any data.
- No credentials or secrets in code; it only reads public JSON URLs.
- No local data access; all content comes from the production site.
