from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ValidationStatus = Literal["PASS", "FAIL", "WARN", "ERROR"]
PipelineStatus = Literal["COMPLETE", "ERROR"]


class ValidateOptions(BaseModel):
    model_config = ConfigDict(extra="allow")

    mode: Literal["audit"] = "audit"
    chunk_size_chars: int = 8000
    overlap_chars: int = 400
    resume: bool = True


class ValidateRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    tenant_slug: str = Field(..., min_length=1, max_length=80)
    candidate_id: str | None = Field(default=None, max_length=120)
    candidate_title: str | None = Field(default=None, max_length=200)
    content_type: Literal["markdown"] = "markdown"
    content: str = Field(..., min_length=1)
    context: dict[str, Any] | None = None
    options: ValidateOptions = Field(default_factory=ValidateOptions)


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    source: str | None = None
    excerpt: str | None = None
    note: str | None = None


class ChunkResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    chunk_id: str
    index: int
    status: ValidationStatus
    model_used: str | None = None
    finding_count: int = 0
    message: str = ""
    evidence: list[EvidenceItem] = Field(default_factory=list)
    details: dict[str, Any] | None = None


class ContentSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    pass_: int = Field(0, alias="pass")
    fail: int = 0
    warn: int = 0
    error: int = 0


class ValidateResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    run_id: str
    tenant_slug: str
    pipeline_status: PipelineStatus
    content_summary: ContentSummary
    chunks: list[ChunkResult]


class RunStateResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    run_id: str
    tenant_slug: str
    pipeline_status: PipelineStatus
    content_summary: ContentSummary
    inserted_at: str
    meta: dict[str, Any] = Field(default_factory=dict)


class ChunkResultsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    run_id: str
    tenant_slug: str
    chunks: list[ChunkResult]


