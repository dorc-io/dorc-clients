"""Configuration management for dorc-client."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for dorc-client.
    
    All configuration comes from environment variables.
    """
    engine_url: str
    tenant_slug: str
    api_key: str | None = None
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.
        
        Raises:
            ValueError: If required environment variables are missing.
        """
        engine_url = os.getenv("DORC_ENGINE_URL")
        if not engine_url:
            raise ValueError(
                "DORC_ENGINE_URL environment variable is required. "
                "Set it to your dorc-engine Cloud Run service URL, e.g., "
                "https://dorc-engine-1092170595100.us-east1.run.app"
            )
        
        # Remove trailing slash if present
        engine_url = engine_url.rstrip("/")
        
        tenant_slug = os.getenv("DORC_TENANT_SLUG")
        if not tenant_slug:
            raise ValueError(
                "DORC_TENANT_SLUG environment variable is required. "
                "Set it to your tenant identifier, e.g., 'my-tenant'"
            )
        
        api_key = os.getenv("DORC_API_KEY")
        
        return cls(
            engine_url=engine_url,
            tenant_slug=tenant_slug,
            api_key=api_key,
        )

