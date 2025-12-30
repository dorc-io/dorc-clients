def api_key_headers(api_key: str | None) -> dict[str, str]:
    """Return headers for API key authentication.

    The engine is expected to accept `X-API-Key`. If api_key is None, returns {}.
    """

    if not api_key:
        return {}
    return {"X-API-Key": api_key}


def bearer_headers(token: str | None) -> dict[str, str]:
    """Return headers for Bearer token authentication.

    If token is None, returns {}.
    """
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def get_identity_platform_token(tenant_slug: str) -> str:
    """DEPRECATED: Identity Platform tokens are no longer supported.

    This function is deprecated. DORC has moved away from Google Identity Platform
    for tenant-scoped tokens. Identity Platform tokens require user authentication
    via OAuth2/OIDC flow, which cannot be automated in SDK/agent contexts.

    **New approach:**
    - Use tenant access tokens minted by dorc-api (RS256 JWTs)
    - Obtain tokens via dorc-web UI: navigate to tenant → tokens page
    - Tokens are shown once and must be copied securely
    - Use tokens with `bearer_headers(token)` for API authentication

    **Migration:**
    1. Authenticate via Firebase (Google sign-in) in dorc-web
    2. Create tenant access token via UI
    3. Use the token with the SDK client

    Args:
        tenant_slug: Tenant identifier (ignored, function always raises)

    Raises:
        NotImplementedError: Always, as this function is deprecated

    Returns:
        Never returns (always raises)
    """
    raise NotImplementedError(
        "get_identity_platform_token() is deprecated. "
        "DORC no longer uses Google Identity Platform for tenant-scoped tokens. "
        "Please use tenant access tokens obtained via dorc-web UI instead. "
        "See https://github.com/your-org/dorc-api/docs/DUAL_TOKEN_AUTH.md for details."
    )


def get_id_token(target_audience: str) -> str:
    """Get Google ID token for service-to-service authentication.

    This function uses Application Default Credentials (ADC) to obtain an ID token
    for authenticating with Google Cloud services (e.g., Cloud Run).

    **Usage:**
    ```python
    token = get_id_token("https://your-service.run.app")
    headers = bearer_headers(token)
    ```

    **Requirements:**
    - Application Default Credentials must be configured
    - Service account must have permission to generate ID tokens
    - For local development, use `gcloud auth application-default login`
    - For Cloud Run/Cloud Functions, ADC is automatically configured

    Args:
        target_audience: The target service URL (e.g., Cloud Run service URL)

    Returns:
        ID token string (JWT)

    Raises:
        Exception: If ID token cannot be obtained (e.g., ADC not configured)
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token
    except ImportError:
        raise ImportError(
            "google-auth library is required for get_id_token(). "
            "Install with: pip install google-auth"
        )

    request = Request()
    token = id_token.fetch_id_token(request, target_audience)
    return token


