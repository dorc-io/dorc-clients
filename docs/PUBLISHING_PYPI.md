## Publishing `dorc-client` to PyPI

This repo publishes the Python SDK located at `sdk/python` as the PyPI project **`dorc-client`**.

### Recommended: PyPI Trusted Publishing (no API key in GitHub)

The GitHub Actions workflow is:

- `.github/workflows/publish-pypi.yml`
- Trigger: pushing a git tag like `v0.0.1`

GitHub uses OIDC to request a short-lived token from PyPI (Trusted Publishing). No long-lived PyPI API token is stored in GitHub.

### PyPI setup (what you must do once)

1. Create a PyPI account.
2. Ensure the project **exists** on PyPI:
   - If it doesn’t exist yet, do a one-time manual upload (see “Bootstrap” below), or create it however you prefer.
3. In the PyPI project settings for `dorc-client`, configure **Trusted Publisher**:
   - **Owner / Organization**: your GitHub org/user (e.g. `dorc-io`)
   - **Repository**: `dorc-clients`
   - **Workflow file**: `.github/workflows/publish-pypi.yml`
   - **Environment**: leave blank (this workflow does not require a GitHub Environment)

After this is set, any `v*` tag push will publish.

### Bootstrap (first ever publish)

PyPI Trusted Publishing usually expects the project to already exist.

For the very first publish you can:
- Create a PyPI **API token** (one-time)
- Build+upload from `sdk/python` using `twine`
- Then switch to Trusted Publishing and delete/revoke the token

### Release process

1. Bump version in `sdk/python/src/dorc_client/version.py`
2. Commit
3. Tag and push:

```bash
git tag v0.0.1
git push origin v0.0.1
```

The `publish-pypi` workflow will build and publish `sdk/python` to PyPI.


