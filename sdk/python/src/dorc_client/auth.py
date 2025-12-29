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
    """Get an Identity Platform JWT token (RS256) for API Gateway authentication.
    
    This function uses Google Application Default Credentials (ADC) to obtain
    an Identity Platform token. The token will be validated by API Gateway.
    
    Args:
        audience: The API Gateway audience (typically "dorc-api")
        tenant: Optional tenant identifier (will be set as custom claim if supported)
        project_id: Optional GCP project ID (defaults to ADC project)
        credentials_path: Optional path to service account JSON (for local dev)
    
    Returns:
        JWT token string (RS256, issued by Identity Platform)
    
    Raises:
        RuntimeError: If token cannot be obtained
    
    Note:
        This requires the `google-auth` library. Install with:
        pip install google-auth
        
        For Identity Platform tokens, you typically need to:
        1. Configure Identity Platform in your GCP project
        2. Set up OAuth2/OIDC providers
        3. Authenticate users via Identity Platform (not service accounts)
        
        For service account-based access, consider using ID tokens instead.
    """
    try:
        from google.auth import default
        from google.auth.transport.requests import Request as AuthRequest
    except ImportError:
        raise RuntimeError(
            "google-auth is required for Identity Platform tokens. "
            "Install with: pip install google-auth"
        )
    
    # For Identity Platform, we typically need user authentication tokens
    # Service accounts can't directly get Identity Platform tokens
    # This is a placeholder - actual implementation depends on your auth flow
    raise NotImplementedError(
        "Identity Platform token generation requires user authentication. "
        "Use OAuth2/OIDC flow to authenticate users and obtain tokens, "
        "or use HS256 tokens for direct API access (when API Gateway is disabled)."
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

