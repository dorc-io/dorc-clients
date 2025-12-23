# dorc-clients

Open-source client libraries and tools for interacting with the `dorc-engine` HTTP API.

This repository contains:
- **Python SDK** - Clean HTTP client for calling dorc-engine
- **MCP Server** - Minimal Model Context Protocol adapter (stub)
- **Google Colab Notebooks** - Interactive workflows for creating and validating Candidate Canon Entries (CCE)

## Quickstart

### Install the SDK

```bash
cd sdk/python
pip install -e .
```

Or from the repository root:
```bash
pip install -e sdk/python
```

Or from a Colab notebook:
```python
!pip install -e sdk/python
```

### Basic Usage

```python
import os
from dorc_client import DorcClient

# Set environment variables
os.environ["DORC_BASE_URL"] = "https://your-engine-url.run.app"
os.environ["DORC_TENANT_SLUG"] = "my-tenant"

# Create client
client = DorcClient()

# Check health
if client.health():
    print("Engine is healthy!")

# Validate content
response = client.validate(
    content="# My Document\n\nContent here...",
    candidate_id="my-candidate-001",
)

print(f"Run ID: {response.run_id}")
print(f"Status: {response.pipeline_status}")
print(f"Summary: {response.content_summary}")
```

## Environment Variables

### Required

- **`DORC_BASE_URL`** - Base URL of the dorc-engine Cloud Run service
  - Example: `https://dorc-engine-1092170595100.us-east1.run.app`
  - No trailing slash
  - Back-compat: `DORC_ENGINE_URL` is still accepted but deprecated

- **`DORC_TENANT_SLUG`** - Tenant identifier for all requests
  - Example: `my-tenant`, `research-team`, `hyperfocus`
  - Must be 1-80 characters

### Optional

- **`DORC_API_KEY`** - API key for authentication (if required)
  - If set, sends `X-API-Key: <key>` header
  - If not set, no auth header is sent

## Repository Structure

```
dorc-clients/
├── sdk/python/          # Python SDK package
│   └── dorc_client/     # Main SDK module
├── mcp/                 # MCP server stub
├── notebooks/           # Google Colab notebooks
└── tests/               # SDK tests
```

## Components

### Python SDK

The SDK provides a clean, type-safe interface to dorc-engine:

- **`DorcClient`** - Main client class
- **Methods:**
  - `health() -> bool` - Check service health (tries `/healthz` then `/health`)
  - `validate(...) -> ValidateResponse` - Validate candidate content (POST `/v1/validate`)
  - `get_run(run_id: str) -> RunStateResponse` - Get run status
  - `list_chunks(run_id: str) -> list[ChunkResult]` - Get chunk details

See `sdk/python/dorc_client/` for implementation.

### MCP Server

Minimal Model Context Protocol adapter that wraps the SDK. Currently a stub implementation.

See `mcp/README.md` for details.

### Colab Notebooks

Interactive notebooks for CCE workflows:

- **`00_quickstart.ipynb`** - Health check and basic setup
- **`01_create_and_validate_cce.ipynb`** - Submit and display validation results
- **`02_review_and_rectify_loop.ipynb`** - Human-in-the-loop validation workflow
- **`03_export_jsonl_for_rag.ipynb`** - Export validated CCE to JSONL format

See `notebooks/README.md` for details.

## API Endpoints

The SDK calls these dorc-engine endpoints:

- `GET /healthz` - Health check
- `POST /v1/validate` - Validate candidate content (synchronous)
- `GET /v1/runs/{run_id}` - Get run status and summary
- `GET /v1/runs/{run_id}/chunks` - Get detailed chunk results

For detailed API documentation, see [dorc-engine colab-integration.md](https://github.com/your-org/dorc-engine/blob/main/docs/colab-integration.md).

## Development

### Install for Development

```bash
pip install -e sdk/python[dev]
```

### Run Tests

```bash
pytest sdk/python/tests/
```

Tests use mocked HTTP responses - no real network calls.

### Project Structure

- **SDK**: Pure client code, no server logic
- **MCP**: Thin adapter over SDK
- **Notebooks**: Real `.ipynb` JSON files, runnable in Colab
- **No infrastructure**: No Terraform, no deployment configs
- **No engine code**: This repo only contains client code

## Docs policy

- Notebooks are **examples only** (`notebooks/`).
- Documentation is plain markdown (`docs/`).
- This repo intentionally does **not** publish a static site (no GitHub Pages, no JupyterBook, no MkDocs).

## License

Apache-2.0 - See [LICENSE](LICENSE) file.
