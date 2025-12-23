"""HTTP client for dorc-engine API."""

from typing import Any, Dict

import httpx

from .auth import get_auth_headers
from .config import Config
from .types import (
    ChunkResult,
    RunStateResponse,
    ValidateOptions,
    ValidateRequest,
    ValidateResponse,
)


class DorcClient:
    """Client for interacting with dorc-engine HTTP API."""
    
    def __init__(self, config: Config | None = None):
        """Initialize the client.
        
        Args:
            config: Optional configuration. If not provided, loads from environment.
        """
        if config is None:
            config = Config.from_env()
        self.config = config
        self._client = httpx.Client(
            base_url=config.engine_url,
            headers=get_auth_headers(config.api_key),
            timeout=300.0,  # 5 minutes for validation requests
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def healthz(self) -> bool:
        """Check if the engine service is healthy.
        
        Returns:
            True if service is healthy, False otherwise.
        """
        try:
            response = self._client.get("/healthz")
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False
    
    def validate(
        self,
        candidate_text: str,
        candidate_id: str | None = None,
        candidate_title: str | None = None,
        metadata: Dict[str, Any] | None = None,
        **options: Any,
    ) -> ValidateResponse:
        """Validate candidate content.
        
        Args:
            candidate_text: The content to validate (markdown).
            candidate_id: Optional candidate identifier.
            candidate_title: Optional candidate title.
            metadata: Optional context metadata dictionary.
            **options: Optional validation options (mode, chunk_size_chars, overlap_chars, resume).
            
        Returns:
            ValidateResponse with validation results.
            
        Raises:
            httpx.HTTPError: If the request fails.
        """
        validate_options = ValidateOptions(**options) if options else ValidateOptions()
        
        request = ValidateRequest(
            tenant_slug=self.config.tenant_slug,
            candidate_id=candidate_id,
            candidate_title=candidate_title,
            content=candidate_text,
            context=metadata,
            options=validate_options,
        )
        
        response = self._client.post(
            "/v1/validate",
            json=request.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        
        return ValidateResponse.model_validate(response.json())
    
    def get_run(self, run_id: str) -> RunStateResponse:
        """Get run status and summary.
        
        Args:
            run_id: The run identifier.
            
        Returns:
            RunStateResponse with run status and summary.
            
        Raises:
            httpx.HTTPError: If the request fails (404 if run not found).
        """
        response = self._client.get(f"/v1/runs/{run_id}")
        response.raise_for_status()
        
        return RunStateResponse.model_validate(response.json())
    
    def list_chunks(self, run_id: str) -> list[ChunkResult]:
        """Get detailed chunk results for a run.
        
        Args:
            run_id: The run identifier.
            
        Returns:
            List of ChunkResult objects.
            
        Raises:
            httpx.HTTPError: If the request fails (404 if run not found).
        """
        from .types import ChunkResultsResponse
        
        response = self._client.get(f"/v1/runs/{run_id}/chunks")
        response.raise_for_status()
        
        chunks_response = ChunkResultsResponse.model_validate(response.json())
        return chunks_response.chunks

