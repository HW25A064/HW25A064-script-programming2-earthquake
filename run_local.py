#!/usr/bin/env python3
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    fetch = [sys.executable, "src/earthquake_fetcher.py", "--allow-fallback"]
    if args.offline:
        fetch.append("--offline")
    run(fetch)
    run(["node", "src/build_dashboard.mjs"])
    run([sys.executable, "src/verify_outputs.py"])
    print("Local pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
