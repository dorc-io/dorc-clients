def api_key_headers(api_key: str | None) -> dict[str, str]:
    """Return headers for API key authentication.

    The engine is expected to accept `X-API-Key`. If api_key is None, returns {}.
    """

    if not api_key:
        return {}
    return {"X-API-Key": api_key}


def bearer_headers(token: str | None) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def get_identity_platform_token(
    *,
    audience: str,
    tenant: str | None = None,
    project_id: str | None = None,
    credentials_path: str | None = None,
) -> str:
    """DEPRECATED: Identity Platform is no longer used for tenant-scoped tokens.

    DORC now uses:
    - Firebase Authentication for web UI (human users)
    - dorc-api-minted RS256 tenant access tokens for SDK/agents

    To get a tenant access token:
    1. Authenticate with Firebase (web UI)
    2. Call POST /v1/tenants/{tenant}/tokens via dorc-api
    3. Use the returned token for SDK/agent authentication

    This function is kept for backward compatibility but will always raise NotImplementedError.
    """
    raise NotImplementedError(
        "Identity Platform is deprecated. "
        "Use Firebase Authentication (web UI) or dorc-api tenant access tokens (SDK/agents). "
        "See dorc-api/docs/DUAL_TOKEN_AUTH.md for details."
    )


def get_id_token(*, audience: str, credentials_path: str | None = None) -> str:
    """Get a Google ID token for service-to-service authentication.
    
    This uses Application Default Credentials (ADC) to obtain an ID token
    for the specified audience. Useful for service-to-service calls.
    
    Args:
        audience: The target service URL or audience
        credentials_path: Optional path to service account JSON (for local dev)
    
    Returns:
        ID token string
    
    Raises:
        RuntimeError: If token cannot be obtained
    """
    try:
        from google.auth import default
        from google.auth.transport.requests import Request as AuthRequest
        from google.oauth2 import id_token
    except ImportError:
        raise RuntimeError(
            "google-auth is required for ID tokens. "
            "Install with: pip install google-auth"
        )
    
    credentials, project = default()
    if not credentials.valid:
        credentials.refresh(AuthRequest())
    
    # Request ID token for the audience
    request = AuthRequest()
    token = id_token.fetch_id_token(request, audience)
    return token

