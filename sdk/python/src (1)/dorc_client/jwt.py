"""JWT minting helper for local/dev use ONLY.

WARNING: This is for development/testing only. Production clients should obtain
JWTs from a proper OIDC provider or authentication service.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

try:
    import jwt as pyjwt
except ImportError:
    raise ImportError(
        "PyJWT is required for JWT minting. Install with: pip install PyJWT"
    ) from None


def mint_jwt(
    *,
    secret: str,
    issuer: str,
    audience: str,
    tenant_slug: str,
    subject: str,
    ttl_seconds: int = 3600,
    scope: Optional[str] = None,
    permissions: Optional[List[str]] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Mint an HS256 JWT token for local/dev use.

    Args:
        secret: Shared secret (must match MCP's DORC_JWT_SECRET)
        issuer: Token issuer (must match MCP's DORC_JWT_ISSUER)
        audience: Token audience (must match MCP's DORC_JWT_AUDIENCE)
        tenant_slug: Tenant identifier (slug format)
        subject: Subject identifier (e.g., user ID)
        ttl_seconds: Token lifetime in seconds (default: 1 hour)
        scope: Optional scope string (or use permissions)
        permissions: Optional permissions list (or use scope)
        additional_claims: Optional additional claims to include

    Returns:
        JWT token string

    Example:
        >>> token = mint_jwt(
        ...     secret="my-secret-key",
        ...     issuer="dorc-dev",
        ...     audience="dorc-mcp",
        ...     tenant_slug="scott",
        ...     subject="user-123",
        ...     scope="read write",
        ... )
    """
    now = int(time.time())
    exp = now + ttl_seconds

    claims: Dict[str, Any] = {
        "iss": issuer,
        "aud": audience,
        "sub": subject,
        "tenant_slug": tenant_slug,
        "iat": now,
        "exp": exp,
    }

    if scope:
        claims["scope"] = scope
    elif permissions:
        claims["permissions"] = permissions
    else:
        # Default scope if neither provided
        claims["scope"] = "read write"

    if additional_claims:
        claims.update(additional_claims)

    token = pyjwt.encode(claims, secret, algorithm="HS256")
    return token

