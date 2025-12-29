#!/usr/bin/env python3
"""Standalone integration test script for dorc-api service.

This script makes real HTTP calls to test your deployed service.
No mocks, no fakes - actual integration testing.

Usage:
    export DORC_MCP_URL="https://your-mcp-service.run.app"
    export DORC_JWT="your-jwt-token"
    python test_integration_standalone.py

Or run with pytest:
    pytest tests/test_integration.py -v -m integration
"""

import os
import sys
from typing import Optional

from dorc_client import DorcClient
from dorc_client.errors import DorcAuthError, DorcError


def test_health(client: DorcClient) -> bool:
    """Test /health endpoint."""
    print("\n🔍 Testing /health endpoint...")
    try:
        result = client.health()
        print(f"✅ Health check passed: {result}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_healthz(client: DorcClient) -> bool:
    """Test /healthz endpoint."""
    print("\n🔍 Testing /healthz endpoint...")
    try:
        result = client.healthz()
        print(f"✅ Healthz check passed: {result}")
        return True
    except Exception as e:
        print(f"❌ Healthz check failed: {e}")
        return False


def test_validate_basic(client: DorcClient) -> Optional[str]:
    """Test basic validation."""
    print("\n🔍 Testing /v1/validate endpoint...")
    try:
        response = client.validate(
            candidate_content="# Test Document\n\nThis is a simple test.",
            content_type="text/markdown",
            mode="audit",
        )
        print(f"✅ Validation successful!")
        print(f"   Run ID: {response.run_id}")
        print(f"   Status: {response.pipeline_status}")
        print(f"   Summary: PASS={response.content_summary.pass}, "
              f"FAIL={response.content_summary.fail}, "
              f"WARN={response.content_summary.warn}")
        return response.run_id
    except DorcAuthError as e:
        print(f"❌ Authentication failed: {e}")
        print("   Make sure DORC_JWT is set correctly")
        return None
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None


def test_get_run(client: DorcClient, run_id: str) -> bool:
    """Test getting run status."""
    print(f"\n🔍 Testing GET /v1/runs/{run_id}...")
    try:
        run_state = client.get_run(run_id)
        print(f"✅ Get run successful!")
        print(f"   Status: {run_state.pipeline_status}")
        print(f"   Summary: {run_state.content_summary}")
        return True
    except Exception as e:
        print(f"❌ Get run failed: {e}")
        return False


def test_list_chunks(client: DorcClient, run_id: str) -> bool:
    """Test listing chunks."""
    print(f"\n🔍 Testing GET /v1/runs/{run_id}/chunks...")
    try:
        chunks = client.list_chunks(run_id)
        print(f"✅ List chunks successful! Got {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:3]):  # Show first 3
            print(f"   Chunk {chunk.index}: {chunk.status} - {chunk.message}")
        if len(chunks) > 3:
            print(f"   ... and {len(chunks) - 3} more chunks")
        return True
    except Exception as e:
        print(f"❌ List chunks failed: {e}")
        return False


def test_validate_without_jwt() -> bool:
    """Test that validation fails without JWT."""
    print("\n🔍 Testing validation without JWT (should fail)...")
    mcp_url = os.getenv("DORC_MCP_URL")
    if not mcp_url:
        print("⚠️  Skipped: DORC_MCP_URL not set")
        return True  # Skip, not a failure
    
    try:
        client = DorcClient.for_mcp(mcp_url, jwt_token=None)
        client.validate(candidate_content="# Test")
        print("❌ Should have failed without JWT!")
        return False
    except (DorcAuthError, ValueError) as e:
        print(f"✅ Correctly failed without JWT: {e}")
        return True
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
        return False


def main() -> int:
    """Run all integration tests."""
    print("=" * 60)
    print("🚀 DORC-API Integration Test")
    print("=" * 60)
    
    # Check environment variables
    mcp_url = os.getenv("DORC_MCP_URL")
    jwt = os.getenv("DORC_JWT") or os.getenv("DORC_TOKEN")
    
    if not mcp_url:
        print("\n❌ ERROR: DORC_MCP_URL environment variable is required")
        print("   Example: export DORC_MCP_URL=https://dorc-api-xxxxx.us-east1.run.app")
        return 1
    
    if not jwt:
        print("\n❌ ERROR: DORC_JWT or DORC_TOKEN environment variable is required")
        return 1
    
    print(f"\n📋 Configuration:")
    print(f"   URL: {mcp_url}")
    print(f"   JWT: {jwt[:20]}... (truncated)")
    
    # Create client
    try:
        client = DorcClient()
    except Exception as e:
        print(f"\n❌ Failed to create client: {e}")
        return 1
    
    # Run tests
    results = []
    
    # Test 1: Health endpoints (no auth)
    results.append(("Health Check", test_health(client)))
    results.append(("Healthz Check", test_healthz(client)))
    
    # Test 2: Validation (requires auth)
    run_id = test_validate_basic(client)
    results.append(("Validation", run_id is not None))
    
    # Test 3 & 4: Only if validation succeeded
    if run_id:
        results.append(("Get Run", test_get_run(client, run_id)))
        results.append(("List Chunks", test_list_chunks(client, run_id)))
    
    # Test 5: Auth error handling
    results.append(("Auth Error Handling", test_validate_without_jwt()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

