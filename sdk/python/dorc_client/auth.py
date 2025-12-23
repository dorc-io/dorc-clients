"""Authentication helpers for dorc-client."""

from typing import Dict


def get_auth_headers(api_key: str | None) -> Dict[str, str]:
    """Get authentication headers for API requests.
    
    Args:
        api_key: Optional API key. If provided, returns Bearer token header.
        
    Returns:
        Dictionary with Authorization header if api_key is set, otherwise empty dict.
    """
    if api_key:
        return {"Authorization": f"Bearer {api_key}"}
    return {}

