#!/usr/bin/env python3
"""Optional Discord notification. The webhook is read only from an environment variable."""
from __future__ import annotations
import json
import os
import sys
import urllib.request


def main() -> int:
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    status = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"
    build_url = os.environ.get("BUILD_URL", "")
    if not webhook:
        print("[discord] DISCORD_WEBHOOK_URL is not configured; skipping")
        return 0
    payload = {
        "content": f"HW25A064 earthquake dashboard Jenkins build: **{status}**\n{build_url}".strip()
    }
    request = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "HW25A064-Jenkins"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        print(f"[discord] HTTP {response.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
