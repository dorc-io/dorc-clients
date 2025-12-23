## dorc-client (Python)

Python SDK for DORC MCP service with JWT authentication.

### Install

```bash
pip install dorc-client
```

### Quick Start

```python
from dorc_client import DorcClient

# Create client with JWT token
client = DorcClient(
    base_url="https://dorc-mcp-xxxxx.run.app",
    jwt_token="your-jwt-token-here",
)

# Health check (no auth required)
health = client.health()
print(health)  # {"status": "ok", "service": "dorc-mcp", "version": "0.1.0"}

# Validate a CCE (JWT required)
result = client.validate_cce(
    tenant_slug="scott",
    cce_markdown="# My Canon Entry\n\nContent here...",
    source_id="doc-123",
    tags=["important", "draft"],
)
print(f"Run ID: {result.run_id}, Status: {result.pipeline_status}")

# Get run details
run = client.get_run(tenant_slug="scott", run_id=result.run_id)

# List chunks
chunks = client.list_chunks(tenant_slug="scott", run_id=result.run_id)
```

### Environment Variables

- **`DORC_MCP_URL`**: base URL of dorc-mcp (example: `https://dorc-mcp-xxxxx.us-east1.run.app`)
- **`DORC_JWT`** (or `DORC_TOKEN`): JWT bearer token for authentication
- **`DORC_ENGINE_API_KEY`** (optional): Engine API key (only if client calls engine directly)

### API Methods

- `health()` → `GET /health` (no auth)
- `healthz()` → `GET /healthz` (no auth)
- `validate_cce(tenant_slug, cce_markdown, source_id=None, tags=None)` → `POST /v1/validate` (JWT required)
- `get_run(tenant_slug, run_id)` → `GET /v1/runs/{run_id}` (JWT required)
- `list_chunks(tenant_slug, run_id)` → `GET /v1/runs/{run_id}/chunks` (JWT required)

All protected endpoints require JWT authentication. The `tenant_slug` parameter must match the `tenant_slug` claim in your JWT token.


