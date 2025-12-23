"""Minimal MCP server stub for dorc-engine.

This is a thin adapter over the dorc_client SDK that exposes MCP tools.
Currently a stub implementation - refine based on your MCP library requirements.
"""

import os
import sys
from typing import Any, Dict, List

try:
    from dorc_client import DorcClient, Config
except ImportError:
    # Fallback if SDK not installed
    print(
        "Warning: dorc_client not found. Install with: pip install -e ../sdk/python",
        file=sys.stderr,
    )
    Config = None
    DorcClient = None


class DorcMCPServer:
    """Minimal MCP server for dorc-engine.
    
    This is a thin adapter that wraps the dorc_client SDK.
    """
    
    def __init__(self):
        """Initialize the MCP server."""
        if Config is None or DorcClient is None:
            raise ImportError("dorc_client SDK not available")
        
        # Load config from environment
        self.config = Config.from_env()
        self.client = DorcClient(config=self.config)
    
    def dorc_validate(
        self,
        content: str,
        candidate_id: str | None = None,
        **options: Any,
    ) -> Dict[str, Any]:
        """Validate candidate content.
        
        Args:
            content: The content to validate (markdown).
            candidate_id: Optional candidate identifier.
            **options: Optional validation options.
            
        Returns:
            Dictionary with validation results.
        """
        response = self.client.validate(
            candidate_text=content,
            candidate_id=candidate_id,
            **options,
        )
        
        # Convert to dict for MCP response
        return {
            "run_id": response.run_id,
            "tenant_slug": response.tenant_slug,
            "pipeline_status": response.pipeline_status,
            "content_summary": {
                "pass": response.content_summary.pass_,
                "fail": response.content_summary.fail,
                "warn": response.content_summary.warn,
                "error": response.content_summary.error,
            },
            "chunks": [
                {
                    "chunk_id": chunk.chunk_id,
                    "index": chunk.index,
                    "status": chunk.status,
                    "message": chunk.message,
                    "finding_count": chunk.finding_count,
                }
                for chunk in response.chunks
            ],
        }
    
    def dorc_get_run(self, run_id: str) -> Dict[str, Any]:
        """Get run status and summary.
        
        Args:
            run_id: The run identifier.
            
        Returns:
            Dictionary with run status and summary.
        """
        response = self.client.get_run(run_id)
        
        return {
            "run_id": response.run_id,
            "tenant_slug": response.tenant_slug,
            "pipeline_status": response.pipeline_status,
            "content_summary": {
                "pass": response.content_summary.pass_,
                "fail": response.content_summary.fail,
                "warn": response.content_summary.warn,
                "error": response.content_summary.error,
            },
            "inserted_at": response.inserted_at,
            "meta": response.meta,
        }
    
    def dorc_list_chunks(self, run_id: str) -> List[Dict[str, Any]]:
        """Get detailed chunk results for a run.
        
        Args:
            run_id: The run identifier.
            
        Returns:
            List of chunk result dictionaries.
        """
        chunks = self.client.list_chunks(run_id)
        
        return [
            {
                "chunk_id": chunk.chunk_id,
                "index": chunk.index,
                "status": chunk.status,
                "model_used": chunk.model_used,
                "finding_count": chunk.finding_count,
                "message": chunk.message,
                "evidence": [
                    {
                        "source": ev.source,
                        "excerpt": ev.excerpt,
                        "note": ev.note,
                    }
                    for ev in chunk.evidence
                ],
                "details": chunk.details,
            }
            for chunk in chunks
        ]


# TODO: Integrate with actual MCP library
# The structure above provides the core functionality.
# To complete the MCP server:
# 1. Choose an MCP library (e.g., mcp-python-sdk if available)
# 2. Register the three methods as MCP tools
# 3. Add proper request/response handling
# 4. Add error handling and validation
# 5. Add logging
#
# Example stub for MCP integration:
#
# if __name__ == "__main__":
#     server = DorcMCPServer()
#     # Register tools with MCP library
#     # Start MCP server
#     pass


if __name__ == "__main__":
    # CLI-style stub for testing
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python server.py <command> [args...]")
        print("Commands: validate, get_run, list_chunks")
        sys.exit(1)
    
    server = DorcMCPServer()
    command = sys.argv[1]
    
    try:
        if command == "validate":
            if len(sys.argv) < 3:
                print("Usage: python server.py validate <content> [candidate_id]")
                sys.exit(1)
            content = sys.argv[2]
            candidate_id = sys.argv[3] if len(sys.argv) > 3 else None
            result = server.dorc_validate(content, candidate_id)
            print(json.dumps(result, indent=2))
        
        elif command == "get_run":
            if len(sys.argv) < 3:
                print("Usage: python server.py get_run <run_id>")
                sys.exit(1)
            run_id = sys.argv[2]
            result = server.dorc_get_run(run_id)
            print(json.dumps(result, indent=2))
        
        elif command == "list_chunks":
            if len(sys.argv) < 3:
                print("Usage: python server.py list_chunks <run_id>")
                sys.exit(1)
            run_id = sys.argv[2]
            result = server.dorc_list_chunks(run_id)
            print(json.dumps(result, indent=2))
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

