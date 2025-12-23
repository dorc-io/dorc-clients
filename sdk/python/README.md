## dorc-client (Python)

Contract-native Python SDK for DORC.

**Use MCP (JWT) by default.** Engine-direct mode (X-API-Key) is supported only as an explicit advanced option.

### Install

```bash
pip install dorc-client
```

### Environment variables

#### MCP mode (recommended)

- **`DORC_MCP_URL`**: base URL of dorc-mcp (example: `https://dorc-mcp-xxxxx.us-east1.run.app`)
- **`DORC_JWT`** (or `DORC_TOKEN`): JWT bearer token to send as `Authorization: Bearer <token>`

Tenant is derived by MCP from the JWT claims; the SDK **does not** take `tenant_slug` in MCP mode.

#### Engine-direct mode (advanced)

- **`DORC_BASE_URL`** (or legacy `DORC_ENGINE_URL`): base URL of dorc-engine
- **`DORC_TENANT_SLUG`**: required tenant slug (only for engine-direct)
- **`DORC_API_KEY`**: required for engine v0.1 (sent as `X-API-Key`)

### Usage

```python
import os
from dorc_client import DorcClient

os.environ["DORC_MCP_URL"] = "https://your-mcp-url.run.app"
os.environ["DORC_JWT"] = "<your oidc jwt>"

with DorcClient() as c:
    if not c.health():
        raise SystemExit("service not healthy")

    r = c.validate(candidate_content="# Example\n\nHello.")
    print(r.run_id, r.result)
```


