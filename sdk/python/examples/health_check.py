import os

from dorc_client import DorcClient


def main() -> None:
    # Minimal example: set env vars or pass constructor args.
    os.environ.setdefault("DORC_BASE_URL", "http://localhost:8080")
    os.environ.setdefault("DORC_TENANT_SLUG", "example-tenant")

    with DorcClient() as c:
        ok = c.health()
        print(f"health={ok}")


if __name__ == "__main__":
    main()


