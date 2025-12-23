"""Type definitions for dorc-engine API requests and responses."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict

ValidationStatus = Literal["PASS", "FAIL", "WARN", "ERROR"]
PipelineStatus = Literal["COMPLETE", "ERROR"]


class ValidateOptions(BaseModel):
    """Validation options for candidate content."""
    model_config = ConfigDict(extra="allow")
    
    mode: Literal["audit"] = "audit"
    chunk_size_chars: int = 8000
    overlap_chars: int = 400
    resume: bool = True


class ValidateRequest(BaseModel):
    """Request model for /v1/validate endpoint."""
    model_config = ConfigDict(extra="allow")
    
    tenant_slug: str = Field(..., min_length=1, max_length=80)
    candidate_id: Optional[str] = Field(default=None, max_length=120)
    candidate_title: Optional[str] = Field(default=None, max_length=200)
    content_type: Literal["markdown"] = "markdown"
    content: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    options: ValidateOptions = Field(default_factory=ValidateOptions)


class EvidenceItem(BaseModel):
    """Evidence item from validation results."""
    model_config = ConfigDict(extra="allow")
    
    source: Optional[str] = None
    excerpt: Optional[str] = None
    note: Optional[str] = None


class ChunkResult(BaseModel):
    """Result for a single content chunk."""
    model_config = ConfigDict(extra="allow")
    
    chunk_id: str
    index: int
    status: ValidationStatus
    model_used: Optional[str] = None
    finding_count: int = 0
    message: str = ""
    evidence: List[EvidenceItem] = Field(default_factory=list)
    details: Optional[Dict[str, Any]] = None


class ContentSummary(BaseModel):
    """Summary counts of validation results."""
    model_config = ConfigDict(extra="allow")
    
    pass_: int = Field(0, alias="pass")
    fail: int = 0
    warn: int = 0
    error: int = 0


class ValidateResponse(BaseModel):
    """Response from /v1/validate endpoint."""
    model_config = ConfigDict(extra="allow")
    
    run_id: str
    tenant_slug: str
    pipeline_status: PipelineStatus
    content_summary: ContentSummary
    chunks: List[ChunkResult]


class RunStateResponse(BaseModel):
    """Response from /v1/runs/{run_id} endpoint."""
    model_config = ConfigDict(extra="allow")
    
    run_id: str
    tenant_slug: str
    pipeline_status: PipelineStatus
    content_summary: ContentSummary
    inserted_at: str
    meta: Dict[str, Any] = Field(default_factory=dict)


class ChunkResultsResponse(BaseModel):
    """Response from /v1/runs/{run_id}/chunks endpoint."""
    model_config = ConfigDict(extra="allow")
    
    run_id: str
    tenant_slug: str
    chunks: List[ChunkResult]

