#!/usr/bin/env python3
"""
AI Bootstrap — Runtime Smoke Checker v1.0

Verifies that generated multi-app projects actually run: requests the root URL
and health endpoint of each declared app and prints an HTTP status table.

Usage:
    python3 smoke.py --dir /path/to/project
    python3 smoke.py --dir /path/to/project --ports 3000,3002,3100
    python3 smoke.py --dir /path/to/project --json
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_APPS = [
    {"id": "app-web-hr", "name": "HR 前台", "port": 3000, "checks": ["/"]},
    {"id": "app-web-platform", "name": "平台运营后台", "port": 3002, "checks": ["/"]},
    {"id": "app-web-server", "name": "API 服务", "port": 3100, "checks": ["/health", "/api/echo?name=Smoke"]},
]


def _load_apps_from_project(project_dir: Path) -> list[dict]:
    """Read app declarations from the bootstrap manifest when available."""
    manifest = project_dir / ".ai-bootstrap" / "bootstrap-manifest.yaml"
    if not manifest.exists():
        return DEFAULT_APPS
    try:
        from yaml_utils import load_yaml

        data = load_yaml(manifest)
        apps = data.get("manifest", {}).get("apps", [])
        if not isinstance(apps, list) or not apps:
            return DEFAULT_APPS
        resolved = []
        for app in apps:
            if not isinstance(app, dict):
                continue
            resolved.append({
                "id": app.get("id", "app"),
                "name": app.get("name", app.get("id", "app")),
                "port": int(app.get("port") or 0),
                "checks": app.get("checks") or ["/"],
            })
        return resolved or DEFAULT_APPS
    except Exception:
        return DEFAULT_APPS


def _http(url: str, timeout: float = 5.0) -> tuple:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ai-bootstrap-smoke"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(4096).decode("utf-8", errors="replace")
            return resp.status, resp.geturl(), body[:200]
    except urllib.error.HTTPError as exc:
        body = exc.read(4096).decode("utf-8", errors="replace")
        return exc.code, exc.geturl(), body[:200]
    except Exception as exc:  # noqa: BLE001
        return None, None, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Bootstrap — Runtime Smoke Checker")
    parser.add_argument("--dir", required=True, help="Project directory")
    parser.add_argument("--ports", default="", help="Comma-separated ports overriding defaults")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-request timeout (seconds)")
    args = parser.parse_args()

    project_dir = Path(args.dir).resolve()
    apps = _load_apps_from_project(project_dir)
    if args.ports:
        ports = [int(p) for p in args.ports.split(",") if p.strip()]
        for idx, port in enumerate(ports):
            if idx < len(apps):
                apps[idx]["port"] = port

    results = []
    failures = 0
    for app in apps:
        port = app.get("port") or 0
        app_id = app.get("id") or app.get("name") or "unknown"
        for path in app.get("checks") or ["/"]:
            url = f"http://127.0.0.1:{port}{path}"
            status, final_url, body = _http(url, args.timeout)
            ok = status is not None and 200 <= status < 400
            results.append({
                "app": app_id,
                "url": url,
                "status": status,
                "ok": ok,
                "body_excerpt": body,
            })
            if not ok:
                failures += 1

    if args.json:
        print(json.dumps({"results": results, "failures": failures}, indent=2))
    else:
        print(f"\n  AI Bootstrap — Runtime Smoke Checker")
        print(f"  {'App':<22} {'URL':<52} {'Status':<8} Result")
        print(f"  {'-' * 100}")
        for r in results:
            mark = "✅" if r["ok"] else "❌"
            status_text = str(r["status"]) if r["status"] else "ERR"
            print(f"  {r['app']:<22} {r['url']:<52} {status_text:<8} {mark}")
        print(f"\n  Summary: {len(results) - failures}/{len(results)} checks ok, {failures} failures")
        print()

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
