# MCP Server for dorc-engine

Minimal Model Context Protocol (MCP) server that wraps the dorc-client SDK.

## Status

This is a **stub implementation**. The server skeleton is provided but needs refinement based on the specific MCP library and requirements.

## Overview

The MCP server provides a thin adapter layer over the `dorc_client` SDK, exposing three tools:

1. **`dorc_validate`** - Validate candidate content
2. **`dorc_get_run`** - Get run status and summary
3. **`dorc_list_chunks`** - Get detailed chunk results

## Configuration

The server uses the same environment variables as the SDK:

- `DORC_BASE_URL` (required)
- `DORC_TENANT_SLUG` (required)
- `DORC_API_KEY` (optional)

## Usage

See `server.py` for the implementation. The server is a thin adapter that:

1. Loads configuration from environment variables
2. Creates a `DorcClient` instance
3. Exposes MCP tools that call SDK methods
4. Returns results in MCP-compatible format

## Implementation Notes

- The server uses the SDK internally - no direct HTTP calls
- Tenant slug is implied from environment (not per-request)
- Error handling is minimal - errors bubble up from SDK
- This is a starting point - refine based on your MCP library requirements

## TODO

- [ ] Choose and integrate MCP library (if not using stub)
- [ ] Add proper error handling and validation
- [ ] Add request/response logging
- [ ] Add authentication/authorization if needed
- [ ] Add connection pooling if needed
- [ ] Add health check endpoint

