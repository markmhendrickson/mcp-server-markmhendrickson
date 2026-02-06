# Markmhendrickson MCP Server

Read-only MCP server for markmhendrickson.com website content backed by Neotoma. It exposes posts, links, and timeline records via Neotoma.

## Features

- Read-only access to posts, links, and timeline
- Optional filtering via Neotoma-backed datasets
- Single combined response for all content

## Public JSON endpoints (production)

The same content is available as JSON at the site TLD for clients that prefer HTTP over MCP:

- **Posts:** https://markmhendrickson.com/posts.json
- **Links:** https://markmhendrickson.com/links.json
- **Timeline:** https://markmhendrickson.com/timeline.json

Cache generation runs before site builds; Neotoma (parquet) remains the source of truth.

## Tools

### 1. `markmhendrickson_get_posts`

Return post records from Neotoma. Supports optional filters and returns raw records.

**Behavior:**
- Returns full post records, including body and metadata fields present in Neotoma.
- Use filters to limit results (published, category, slug, tags, etc.).
- Order is the underlying parquet order unless a filter reduces it.

**Parameters:**
- `filters` (object, optional): Filters such as `{ "published": true }`

**Example request:**
```json
{
  "filters": { "published": true }
}
```

**Example response:**
```json
{
  "success": true,
  "data": [
    {
      "slug": "truth-layer-agent-memory",
      "title": "Truth layer agent memory",
      "published": true,
      "published_date": "2026-01-20",
      "category": "technical",
      "read_time": 6,
      "tags": "[\"truth-layer\", \"agents\"]"
    }
  ],
  "count": 1
}
```

### 2. `markmhendrickson_get_links`

Return link records from Neotoma. Supports optional filters and returns raw records.

**Behavior:**
- Returns full link records, including display order and category.
- Use filters to limit results (active, category, name, etc.).

**Parameters:**
- `filters` (object, optional): Filters such as `{ "active": true }`

**Example request:**
```json
{
  "filters": { "active": true }
}
```

**Example response:**
```json
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

### 3. `markmhendrickson_get_timeline`

Return timeline records from Neotoma. Supports optional filters and returns raw records.

**Behavior:**
- Returns full timeline records including location, entry type, and display order.
- Descriptions are stored as JSON arrays or strings in Neotoma.

**Parameters:**
- `filters` (object, optional): Filters such as `{ "entry_type": "work" }`

**Example request:**
```json
{
  "filters": { "entry_type": "work" }
}
```

**Example response:**
```json
{
  "success": true,
  "data": [
    {
      "role": "Founder",
      "company": "Startup (Neotoma & Ateles)",
      "date": "2025 – Present · Barcelona, Spain",
      "description": "[\"Building Neotoma, a truth layer for AI memory, and Ateles, a sovereign agentic operating system for personal workflow automation.\"]"
    }
  ],
  "count": 1
}
```

### 4. `markmhendrickson_get_all_content`

Return posts, links, and timeline records in a single response.

**Behavior:**
- Aggregates raw parquet records for posts, links, and timeline.
- Includes `counts` for each dataset.

**Parameters:** none

**Example response:**
```json
{
  "success": true,
  "posts": [],
  "links": [],
  "timeline": [],
  "counts": {
    "posts": 0,
    "links": 0,
    "timeline": 0
  }
}
```

### 5. `markmhendrickson_get_about`

Return the home post (about page) content using the `professional-mission` slug.

**Behavior:**
- Returns a single post record if found.
- Returns `success: false` if the home post is missing.

**Parameters:** none

**Example response:**
```json
{
  "success": true,
  "data": {
    "slug": "professional-mission",
    "title": "Professional mission",
    "published": true
  }
}
```

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

### Environment Variables

- `DATA_DIR` (required): Path to Neotoma data directory
- `PARQUET_MCP_SERVER_PATH` (optional): Override Neotoma storage adapter path

The server loads environment variables from repo `.env`.

### Cursor MCP Configuration

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

### Claude Desktop Configuration

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

## Running

```bash
./run-markmhendrickson-mcp.sh
```

## Error Handling and Troubleshooting

Common issues:
- Missing `DATA_DIR`: Ensure `.env` includes `DATA_DIR`
- Missing dependencies: `pip install -r requirements.txt`
- Parquet MCP path issues: Set `PARQUET_MCP_SERVER_PATH`

## Security Notes

- Read-only operations only
- No credentials stored in code
- Access to Neotoma data is controlled via environment configuration
