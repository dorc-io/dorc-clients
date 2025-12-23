from __future__ import annotations

import re
import time
import warnings
from collections.abc import Callable
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

from .auth import api_key_headers, bearer_headers
from .config import Config
from .errors import DorcAuthError, DorcError
from .models import (
    TENANT_SLUG_REGEX,
    Candidate,
    ChunkResult,
    ChunkResultsResponse,
    RunStateResponse,
    ValidateOptions,
    ValidateRequest,
    ValidateResponse,
)

_TENANT_RE = re.compile(TENANT_SLUG_REGEX)


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
    """Python SDK for DORC.

    Default mode is MCP (JWT) when `DORC_MCP_URL` is set; otherwise engine-direct (legacy).
    Prefer `DorcClient.for_mcp(...)`.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        tenant_slug: str | None = None,
        api_key: str | None = None,
        jwt_token: str | None = None,
        token_provider: Callable[[], str] | None = None,
        timeout_s: float = 30.0,
        validate_timeout_s: float = 300.0,
        config: Config | None = None,
    ):
        if config is None:
            if base_url is None and tenant_slug is None and api_key is None and jwt_token is None:
                config = Config.from_env()
            else:
                # Back-compat: specifying tenant_slug implies engine-direct mode.
                if tenant_slug is not None:
                    config = Config(
                        base_url=(base_url or "").rstrip("/"),
                        mode="engine",
                        tenant_slug=tenant_slug,
                        api_key=api_key,
                    )
                else:
                    # MCP mode: tenant derived by MCP from JWT.
                    config = Config(
                        base_url=(base_url or "").rstrip("/"),
                        mode="mcp",
                        jwt_token=jwt_token,
                        api_key=api_key,
                    )

        self.config = config
        self._token_provider = token_provider
        self._timeout = httpx.Timeout(timeout_s)
        self._validate_timeout = httpx.Timeout(validate_timeout_s)
        self._client = httpx.Client(
            base_url=self.config.base_url,
            headers={},  # auth headers are per-request
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> DorcClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    @classmethod
    def for_mcp(
        cls,
        base_url: str,
        *,
        jwt_token: str | None = None,
        token_provider: Callable[[], str] | None = None,
        timeout_s: float = 30.0,
        validate_timeout_s: float = 300.0,
    ) -> DorcClient:
        if (jwt_token is None or not jwt_token.strip()) and token_provider is None:
            raise ValueError("for_mcp requires jwt_token=... or token_provider=...")
        cfg = Config(
            base_url=base_url.rstrip("/"),
            mode="mcp",
            jwt_token=(jwt_token.strip() if jwt_token else None),
        )
        return cls(
            config=cfg,
            token_provider=token_provider,
            timeout_s=timeout_s,
            validate_timeout_s=validate_timeout_s,
        )

    @classmethod
    def for_engine(
        cls,
        base_url: str,
        *,
        api_key: str,
        tenant_slug: str,
        timeout_s: float = 30.0,
        validate_timeout_s: float = 300.0,
    ) -> DorcClient:
        tenant_slug = tenant_slug.strip()
        if not _TENANT_RE.fullmatch(tenant_slug):
            raise ValueError(f"invalid tenant_slug (must match {TENANT_SLUG_REGEX})")
        cfg = Config(
            base_url=base_url.rstrip("/"),
            mode="engine",
            tenant_slug=tenant_slug,
            api_key=api_key,
        )
        return cls(config=cfg, timeout_s=timeout_s, validate_timeout_s=validate_timeout_s)

    def _auth_headers(self) -> dict[str, str]:
        if self.config.mode == "mcp":
            token = None
            if self._token_provider is not None:
                token = self._token_provider()
            token = (token or self.config.jwt_token or "").strip() or None
            return bearer_headers(token)
        # engine-direct
        return api_key_headers(self.config.api_key)

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if 200 <= resp.status_code < 300:
            return

        text: str | None
        try:
            text = resp.text
        except Exception:
            text = None

        # Prefer contract error envelope.
        code = "HTTP_ERROR"
        message = "request failed"
        request_id = None
        try:
            payload = resp.json()
            if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
                err = payload["error"]
                code = str(err.get("code") or code)
                message = str(err.get("message") or message)
                request_id = str(err.get("request_id")) if err.get("request_id") else None
        except Exception:
            pass

        if resp.status_code in (401, 403):
            raise DorcAuthError(
                resp.status_code,
                code=code,
                message=message,
                request_id=request_id,
                response_text=text,
            )

        raise DorcError(
            resp.status_code,
            code=code,
            message=message,
            request_id=request_id,
            response_text=text,
        )

    @_retry_get()
    def _get(self, path: str) -> httpx.Response:
        resp = self._client.get(path, timeout=self._timeout, headers=self._auth_headers())
        if _is_transient_response(resp):
            return resp
        self._raise_for_status(resp)
        return resp

    def health(self) -> bool:
        """Health check. Tries /healthz then /health."""
        for p in ("/healthz", "/health"):
            try:
                r = self._client.get(p, timeout=self._timeout, headers=self._auth_headers())
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
        candidate_content: str | None = None,
        content_type: str = "text/markdown",
        mode: str = "audit",
        title: str | None = None,
        metadata: dict[str, str] | None = None,
        options: dict[str, Any] | None = None,
        request_id: str | None = None,
        # legacy args (deprecated)
        content: str | None = None,
        candidate_text: str | None = None,
        candidate_id: str | None = None,
        candidate_title: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ValidateResponse:
        """POST /v1/validate (contract-native).

        In MCP mode, tenant is derived by MCP from the JWT.
        In engine-direct mode, tenant is required.
        """
        # Deprecation adapter: old callers used content=/candidate_text=
        # and candidate_id/title/context.
        if candidate_content is None and (content is not None or candidate_text is not None):
            warnings.warn(
                (
                    "validate(content=...)/validate(candidate_text=...) is deprecated; "
                    "use validate(candidate_content=...)."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
            candidate_content = content or candidate_text
            title = title or candidate_title
            if metadata is None and context is not None and isinstance(context, dict):
                # Best-effort: map context.tags into labels
                metadata = {k: str(v) for k, v in context.items() if isinstance(k, str)}

        if candidate_content is None or not str(candidate_content).strip():
            raise ValueError("validate() requires candidate_content=... (non-empty)")

        validate_options = ValidateOptions(**(options or {}))
        req = ValidateRequest(
            request_id=request_id,
            mode=mode,  # type: ignore[arg-type]
            candidate=Candidate(
                content=str(candidate_content),
                content_type=content_type,  # type: ignore[arg-type]
                title=title,
                labels=metadata,
                cce_id=candidate_id,
            ),
            options=validate_options,
        )

        payload = req.model_dump(exclude_none=True)

        # Engine-direct requires tenant_slug; MCP must not include it.
        if self.config.mode == "engine":
            tenant = (self.config.tenant_slug or "").strip()
            if not tenant:
                raise ValueError("tenant_slug is required for engine-direct client")
            if not _TENANT_RE.fullmatch(tenant):
                raise ValueError(f"invalid tenant_slug (must match {TENANT_SLUG_REGEX})")
            payload["tenant_slug"] = tenant
            payload["actor"] = {"subject": "sdk"}

        resp = self._client.post(
            "/v1/validate",
            json=payload,
            timeout=self._validate_timeout,
            headers=self._auth_headers(),
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

    def wait_for_completion(
        self,
        run_id: str,
        *,
        poll_interval_s: float = 2.0,
        timeout_s: float = 60.0,
    ) -> RunStateResponse:
        """Poll /v1/runs/{run_id} until pipeline_status != RUNNING (best-effort helper).

        Note: engine currently exposes `pipeline_status` not contract `status`.
        """
        deadline = time.time() + timeout_s
        while True:
            r = self.get_run(run_id)
            if str(r.pipeline_status).upper() != "RUNNING":
                return r
            if time.time() >= deadline:
                raise TimeoutError(f"timeout waiting for run {run_id}")
            time.sleep(poll_interval_s)


