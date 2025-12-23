"""Tests for dorc-client SDK using mocked HTTP responses."""

import os
from unittest.mock import patch

import pytest
import pytest_httpx

from dorc_client import Config, DorcClient
from dorc_client.errors import DorcConfigError, DorcHttpError
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
    return DorcClient(config=config)


def test_health_success(client, httpx_mock: pytest_httpx.HTTPXMock):
    """Test successful health check."""
    httpx_mock.add_response(
        method="GET",
        url="https://test-engine.run.app/healthz",
        status_code=200,
    )
    
    assert client.health() is True


def test_health_failure(client, httpx_mock: pytest_httpx.HTTPXMock):
    """Test failed health check."""
    httpx_mock.add_response(
        method="GET",
        url="https://test-engine.run.app/healthz",
        status_code=500,
        is_reusable=True,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://test-engine.run.app/health",
        status_code=500,
        is_reusable=True,
    )
    
    assert client.health() is False


def test_validate_success(client, httpx_mock: pytest_httpx.HTTPXMock):
    """Test successful validation request."""
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
        "chunks": [
            {
                "chunk_id": "ch-0-abc",
                "index": 0,
                "status": "PASS",
                "model_used": "gemini-2.5-pro",
                "finding_count": 0,
                "message": "No contradictions found",
                "evidence": [],
                "details": None,
            }
        ],
    }
    
    httpx_mock.add_response(
        method="POST",
        url="https://test-engine.run.app/v1/validate",
        json=mock_response,
        status_code=200,
    )
    
    response = client.validate(content="Test content")
    
    assert isinstance(response, ValidateResponse)
    assert response.run_id == "run-test-123"
    assert response.pipeline_status == "COMPLETE"
    assert response.content_summary.pass_ == 2
    assert len(response.chunks) == 1
    assert response.chunks[0].status == "PASS"


def test_get_run_success(client, httpx_mock: pytest_httpx.HTTPXMock):
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
    
    httpx_mock.add_response(
        method="GET",
        url="https://test-engine.run.app/v1/runs/run-test-123",
        json=mock_response,
        status_code=200,
    )
    
    response = client.get_run("run-test-123")
    
    assert isinstance(response, RunStateResponse)
    assert response.run_id == "run-test-123"
    assert response.pipeline_status == "COMPLETE"


def test_get_run_not_found(client, httpx_mock: pytest_httpx.HTTPXMock):
    """Test get_run with 404 error."""
    httpx_mock.add_response(
        method="GET",
        url="https://test-engine.run.app/v1/runs/nonexistent",
        status_code=404,
        json={"detail": "run not found"},
    )
    
    with pytest.raises(DorcHttpError):
        client.get_run("nonexistent")


def test_list_chunks_success(client, httpx_mock: pytest_httpx.HTTPXMock):
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
    
    httpx_mock.add_response(
        method="GET",
        url="https://test-engine.run.app/v1/runs/run-test-123/chunks",
        json=mock_response,
        status_code=200,
    )
    
    chunks = client.list_chunks("run-test-123")
    
    assert len(chunks) == 2
    assert isinstance(chunks[0], ChunkResult)
    assert chunks[0].status == "PASS"
    assert chunks[1].status == "FAIL"
    assert chunks[1].finding_count == 2


def test_config_from_env_missing_url():
    """Test Config.from_env raises error when base URL is missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(Exception, match="DORC_BASE_URL|DORC_ENGINE_URL"):
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


def test_client_with_auth(config, httpx_mock: pytest_httpx.HTTPXMock):
    """Test client sends auth header when API key is set."""
    config_with_key = Config(
        base_url=config.base_url,
        tenant_slug=config.tenant_slug,
        api_key="test-key-123",
    )
    client = DorcClient(config=config_with_key)
    
    httpx_mock.add_response(
        method="GET",
        url="https://test-engine.run.app/healthz",
        status_code=200,
    )
    
    client.health()
    
    # Verify the request included the auth header
    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers.get("X-API-Key") == "test-key-123"

