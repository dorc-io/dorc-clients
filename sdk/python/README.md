## dorc-client (Python)

Minimal Python SDK for the `dorc-engine` HTTP API.

### Install

```bash
pip install dorc-client
```

### Environment variables

- **`DORC_BASE_URL`**: base URL of dorc-engine (example: `https://dorc-engine-xxxxx.us-east1.run.app`)
- **`DORC_TENANT_SLUG`**: required tenant slug
- **`DORC_API_KEY`**: optional (sent as `X-API-Key`)

### Usage

```python
import os
from dorc_client import DorcClient

os.environ["DORC_BASE_URL"] = "https://your-engine-url.run.app"
os.environ["DORC_TENANT_SLUG"] = "my-tenant"

with DorcClient() as c:
    if not c.health():
        raise SystemExit("engine not healthy")

    r = c.validate(content="# Example\n\nHello.", candidate_id="example-001")
    print(r.run_id, r.pipeline_status)
```


