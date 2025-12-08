#!/usr/bin/env python3
"""Run a minimal readiness check against a running Fallat CrewAI instance."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

import httpx

DEFAULT_BASE_URL = os.getenv("SMOKE_BASE_URL", "http://127.0.0.1:8080")
TIMEOUT = float(os.getenv("SMOKE_TIMEOUT", "10"))
API_TOKEN = os.getenv("SMOKE_API_TOKEN") or os.getenv("FALLAT_API_TOKEN")


class SmokeTestError(RuntimeError):
    """Raised when one of the smoke checks fails."""


def request(client: httpx.Client, method: str, path: str, *, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    url = f"{client.base_url}{path}"
    headers = {}
    if API_TOKEN:
        headers["X-Fallat-Token"] = API_TOKEN
    response = client.request(method, url, json=payload, headers=headers or None, timeout=TIMEOUT)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


def main() -> None:
    global API_TOKEN  # noqa: PLW0603 - intentional runtime override from CLI
    parser = argparse.ArgumentParser(description="Smoke test for Fallat CrewAI")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL of the running service")
    parser.add_argument(
        "--enqueue-demo",
        action="store_true",
        help="Queue a demo executive directive to verify write endpoints",
    )
    parser.add_argument(
        "--api-token",
        default=API_TOKEN,
        help="API token for protected endpoints (falls back to SMOKE_API_TOKEN or FALLAT_API_TOKEN env vars)",
    )
    args = parser.parse_args()

    API_TOKEN = args.api_token

    failures: list[str] = []
    with httpx.Client(base_url=args.base_url) as client:
        try:
            health = request(client, "GET", "/health")
            print("/health", json.dumps(health, indent=2))
        except Exception as exc:  # pragma: no cover - CLI utility
            failures.append(f"Health check failed: {exc}")

        try:
            system_status = request(client, "GET", "/api/system/status")
            print("/api/system/status", json.dumps(system_status, indent=2))
        except Exception as exc:
            failures.append(f"System status check failed: {exc}")

        try:
            dashboard = request(client, "GET", "/api/dashboard/snapshot")
            print("/api/dashboard/snapshot", json.dumps(dashboard, indent=2))
        except Exception as exc:
            failures.append(f"Dashboard snapshot failed: {exc}")

        try:
            summary = request(client, "GET", "/api/system/summary")
            print("/api/system/summary", json.dumps(summary, indent=2))
        except Exception as exc:
            failures.append(f"System summary failed: {exc}")

        if args.enqueue_demo:
            payload = {
                "directive": "Demo readiness directive",
                "priority": "medium",
                "departments": ["Operations", "Finance"],
            }
            try:
                enqueue = request(client, "POST", "/api/execute_directive", payload=payload)
                print("Demo directive queued", json.dumps(enqueue, indent=2))
            except Exception as exc:
                failures.append(f"Directive enqueue failed: {exc}")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        raise SmokeTestError("Smoke test failed")

    print("Smoke test completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except SmokeTestError:
        sys.exit(1)
