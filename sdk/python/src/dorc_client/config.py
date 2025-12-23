from __future__ import annotations

import os
from dataclasses import dataclass

from .errors import DorcConfigError


@dataclass(frozen=True)
class Config:
    """Configuration for the dorc-engine client."""

    base_url: str
    tenant_slug: str
    api_key: str | None = None

    @classmethod
    def from_env(cls) -> Config:
        # Prefer DORC_BASE_URL (new name), allow DORC_ENGINE_URL for backward compat.
        base_url = os.getenv("DORC_BASE_URL") or os.getenv("DORC_ENGINE_URL")
        if not base_url:
            raise DorcConfigError(
                "Missing base URL. Set DORC_BASE_URL to your dorc-engine URL "
                "(example: https://dorc-engine-xxxxx.us-east1.run.app)."
            )
        base_url = base_url.rstrip("/")

        tenant_slug = os.getenv("DORC_TENANT_SLUG")
        if not tenant_slug:
            raise DorcConfigError("Missing DORC_TENANT_SLUG (tenant is required for all calls).")

        api_key = os.getenv("DORC_API_KEY")
        return cls(base_url=base_url, tenant_slug=tenant_slug, api_key=api_key)


