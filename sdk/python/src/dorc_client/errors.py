from __future__ import annotations

from dataclasses import dataclass


class DorcClientError(Exception):
    """Base error for dorc_client."""


class DorcConfigError(DorcClientError):
    """Configuration error (missing env vars, invalid base URL, etc.)."""


@dataclass
class DorcHttpError(DorcClientError):
    """HTTP-layer error returned by the dorc-engine service."""

    status_code: int
    message: str
    response_text: str | None = None

    def __str__(self) -> str:
        return f"HTTP {self.status_code}: {self.message}"


class DorcAuthError(DorcHttpError):
    """Authentication/authorization failure (401/403)."""


