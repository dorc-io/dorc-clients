from __future__ import annotations

from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

from .auth import api_key_headers
from .config import Config
from .errors import DorcAuthError, DorcHttpError
from .models import (
    ChunkResult,
    ChunkResultsResponse,
    RunStateResponse,
    ValidateOptions,
    ValidateRequest,
    ValidateResponse,
)


def _is_transient_exc(exc: BaseException) -> bool:
    return isinstance(exc, (httpx.TimeoutException, httpx.NetworkError))


def _is_transient_response(resp: httpx.Response) -> bool:
    return resp.status_code in (429, 500, 502, 503, 504)


def _retry_get():
    return retry(
        retry=(
            retry_if_exception(_is_transient_exc)
            | retry_if_result(_is_transient_response)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )


class DorcClient:
    """Minimal Python SDK for the dorc-engine HTTP API."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        tenant_slug: str | None = None,
        api_key: str | None = None,
        timeout_s: float = 30.0,
        validate_timeout_s: float = 300.0,
        config: Config | None = None,
    ):
        if config is None:
            if base_url is None or tenant_slug is None:
                config = Config.from_env()
            else:
                config = Config(
                    base_url=base_url.rstrip("/"),
                    tenant_slug=tenant_slug,
                    api_key=api_key,
                )

        self.config = config
        self._timeout = httpx.Timeout(timeout_s)
        self._validate_timeout = httpx.Timeout(validate_timeout_s)
        self._client = httpx.Client(
            base_url=self.config.base_url,
            headers=api_key_headers(self.config.api_key),
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> DorcClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if 200 <= resp.status_code < 300:
            return

        text = None
        try:
            text = resp.text
        except Exception:
            text = None

        if resp.status_code in (401, 403):
            raise DorcAuthError(resp.status_code, "auth failure", text)

        raise DorcHttpError(resp.status_code, "request failed", text)

    @_retry_get()
    def _get(self, path: str) -> httpx.Response:
        resp = self._client.get(path, timeout=self._timeout)
        if _is_transient_response(resp):
            return resp
        self._raise_for_status(resp)
        return resp

    def health(self) -> bool:
        """Health check. Tries /healthz then /health."""
        for p in ("/healthz", "/health"):
            try:
                r = self._client.get(p, timeout=self._timeout)
                if 200 <= r.status_code < 300:
                    return True
            except httpx.HTTPError:
                continue
        return False

    # Backwards-compat alias (older notebooks used healthz()).
    def healthz(self) -> bool:
        return self.health()

    def validate(
        self,
        *,
        content: str | None = None,
        candidate_text: str | None = None,
        candidate_id: str | None = None,
        candidate_title: str | None = None,
        context: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> ValidateResponse:
        """POST /v1/validate (no automatic retries; this may create a new run)."""
        if content is None and candidate_text is None:
            raise ValueError("validate() requires content=... (or legacy candidate_text=...)")
        if content is None:
            content = candidate_text

        validate_options = ValidateOptions(**(options or {}))
        req = ValidateRequest(
            tenant_slug=self.config.tenant_slug,
            candidate_id=candidate_id,
            candidate_title=candidate_title,
            content=content,
            context=context,
            options=validate_options,
        )

        resp = self._client.post(
            "/v1/validate",
            json=req.model_dump(exclude_none=True),
            timeout=self._validate_timeout,
        )
        self._raise_for_status(resp)
        return ValidateResponse.model_validate(resp.json())

    def get_run(self, run_id: str) -> RunStateResponse:
        resp = self._get(f"/v1/runs/{run_id}")
        return RunStateResponse.model_validate(resp.json())

    def list_chunks(self, run_id: str) -> list[ChunkResult]:
        resp = self._get(f"/v1/runs/{run_id}/chunks")
        parsed = ChunkResultsResponse.model_validate(resp.json())
        return parsed.chunks


