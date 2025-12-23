import os

from dorc_client import DorcClient


def main() -> None:
    os.environ.setdefault("DORC_BASE_URL", "http://localhost:8080")
    os.environ.setdefault("DORC_TENANT_SLUG", "example-tenant")

    content = """# Example CCE

This is a tiny example payload.
"""

    with DorcClient() as c:
        r = c.validate(content=content, candidate_id="example-001", candidate_title="Example CCE")
        print(f"run_id={r.run_id} pipeline_status={r.pipeline_status}")
        print(r.content_summary.model_dump(by_alias=True))


if __name__ == "__main__":
    main()


