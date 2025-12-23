"""Tests for dorc-client SDK using mocked HTTP responses."""

import os
from unittest.mock import patch

import httpx
import pytest

from dorc_client import Config, DorcClient
from dorc_client.errors import DorcConfigError, DorcError
from dorc_client.models import ChunkResult, RunStateResponse, ValidateResponse


@pytest.fixture
def config():
    """Create a test configuration."""
    return Config(
        base_url="https://test-engine.run.app",
        tenant_slug="test-tenant",
        api_key=None,
    )


@pytest.fixture
def client(config):
    """Create a test client."""
    c = DorcClient(config=config)
    return c


def _with_transport(client: DorcClient, handler):
    client._client.close()
    client._client = httpx.Client(base_url=client.config.base_url, transport=httpx.MockTransport(handler))  # type: ignore[attr-defined]


def test_health_success(client):
    """Test successful health check."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "https://test-engine.run.app/healthz"
        return httpx.Response(status_code=200)

    _with_transport(client, handler)
    assert client.health() is True


def test_health_failure(client):
    """Test failed health check."""
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url).endswith("/healthz"):
            return httpx.Response(status_code=500)
        if str(request.url).endswith("/health"):
            return httpx.Response(status_code=500)
        return httpx.Response(status_code=404)

    _with_transport(client, handler)
    assert client.health() is False


def test_validate_success(client):
    """Test successful validation request."""
    mock_response = {
        "request_id": "req-test-1",
        "run_id": "run-test-123",
        "status": "COMPLETE",
        "result": "PASS",
        "counts": {"PASS": 1, "FAIL": 0, "WARN": 0, "ERROR": 0, "total_chunks": 1},
        "links": {"run": "/v1/runs/run-test-123", "chunks": "/v1/runs/run-test-123/chunks"},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == "https://test-engine.run.app/v1/validate"
        return httpx.Response(status_code=200, json=mock_response)

    _with_transport(client, handler)
    response = client.validate(candidate_content="Test content")
    
    assert isinstance(response, ValidateResponse)
    assert response.run_id == "run-test-123"
    assert response.status == "COMPLETE"
    assert response.result == "PASS"
    assert response.counts.pass_ == 1


def test_get_run_success(client):
    """Test successful get_run request."""
    mock_response = {
        "run_id": "run-test-123",
        "tenant_slug": "test-tenant",
        "pipeline_status": "COMPLETE",
        "content_summary": {
            "pass": 2,
            "fail": 0,
            "warn": 0,
            "error": 0,
        },
        "inserted_at": "2024-01-15T10:30:00Z",
        "meta": {},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "https://test-engine.run.app/v1/runs/run-test-123"
        return httpx.Response(status_code=200, json=mock_response)

    _with_transport(client, handler)
    response = client.get_run("run-test-123")
    
    assert isinstance(response, RunStateResponse)
    assert response.run_id == "run-test-123"
    assert response.pipeline_status == "COMPLETE"


def test_get_run_not_found(client):
    """Test get_run with 404 error."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "https://test-engine.run.app/v1/runs/nonexistent"
        return httpx.Response(status_code=404, json={"error": {"code": "NOT_FOUND", "message": "run not found"}})

    _with_transport(client, handler)
    
    with pytest.raises(DorcError):
        client.get_run("nonexistent")


def test_list_chunks_success(client):
    """Test successful list_chunks request."""
    mock_response = {
        "run_id": "run-test-123",
        "tenant_slug": "test-tenant",
        "chunks": [
            {
                "chunk_id": "ch-0-abc",
                "index": 0,
                "status": "PASS",
                "model_used": "gemini-2.5-pro",
                "finding_count": 0,
                "message": "No contradictions",
                "evidence": [],
                "details": None,
            },
            {
                "chunk_id": "ch-1-def",
                "index": 1,
                "status": "FAIL",
                "model_used": "gemini-2.5-pro",
                "finding_count": 2,
                "message": "Found contradictions",
                "evidence": [
                    {
                        "source": "canon_v2/section.md",
                        "excerpt": "Existing content...",
                        "note": "Contradiction",
                    }
                ],
                "details": {"confidence": 0.85},
            },
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "https://test-engine.run.app/v1/runs/run-test-123/chunks"
        return httpx.Response(status_code=200, json=mock_response)

    _with_transport(client, handler)
    chunks = client.list_chunks("run-test-123")
    
    assert len(chunks) == 2
    assert isinstance(chunks[0], ChunkResult)
    assert chunks[0].status == "PASS"
    assert chunks[1].status == "FAIL"
    assert chunks[1].finding_count == 2


def test_config_from_env_missing_url():
    """Test Config.from_env raises error when base URL is missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(Exception, match="DORC_MCP_URL|DORC_BASE_URL|DORC_ENGINE_URL"):
            Config.from_env()


def test_config_from_env_missing_tenant():
    """Test Config.from_env raises error when DORC_TENANT_SLUG is missing."""
    with patch.dict(os.environ, {"DORC_BASE_URL": "https://test.run.app"}, clear=True):
        with pytest.raises(DorcConfigError, match="DORC_TENANT_SLUG"):
            Config.from_env()


def test_config_from_env_success():
    """Test Config.from_env loads successfully with all required vars."""
    with patch.dict(
        os.environ,
        {
            "DORC_BASE_URL": "https://test.run.app",
            "DORC_TENANT_SLUG": "test-tenant",
        },
        clear=True,
    ):
        config = Config.from_env()
        assert config.base_url == "https://test.run.app"
        assert config.tenant_slug == "test-tenant"
        assert config.api_key is None


def test_config_from_env_with_api_key():
    """Test Config.from_env loads API key when set."""
    with patch.dict(
        os.environ,
        {
            "DORC_BASE_URL": "https://test.run.app",
            "DORC_TENANT_SLUG": "test-tenant",
            "DORC_API_KEY": "test-key-123",
        },
        clear=True,
    ):
        config = Config.from_env()
        assert config.api_key == "test-key-123"


def test_config_strips_trailing_slash():
    """Test Config.from_env strips trailing slash from engine_url."""
    with patch.dict(
        os.environ,
        {
            "DORC_BASE_URL": "https://test.run.app/",
            "DORC_TENANT_SLUG": "test-tenant",
        },
        clear=True,
    ):
        config = Config.from_env()
        assert config.base_url == "https://test.run.app"


def test_client_with_auth(config):
    """Test client sends auth header when API key is set."""
    config_with_key = Config(
        base_url=config.base_url,
        mode="engine",
        tenant_slug=config.tenant_slug,
        api_key="test-key-123",
    )
    client = DorcClient(config=config_with_key)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("X-API-Key") == "test-key-123"
        return httpx.Response(status_code=200)

    _with_transport(client, handler)
    client.health()

