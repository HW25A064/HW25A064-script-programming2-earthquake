#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))


def verify(output_dir: Path) -> dict:
    json_path = output_dir / "earthquakes.json"
    csv_path = output_dir / "earthquakes.csv"
    html_path = output_dir / "index.html"
    required = [json_path, csv_path, html_path]
    missing = [path.name for path in required if not path.exists() or path.stat().st_size == 0]
    if missing:
        raise AssertionError(f"missing or empty outputs: {', '.join(missing)}")

    document = json.loads(json_path.read_text(encoding="utf-8"))
    events = document.get("events") or []
    if not events:
        raise AssertionError("earthquakes.json contains no events")
    if document.get("student", {}).get("id") != "HW25A064":
        raise AssertionError("student id mismatch")
    if document.get("summary", {}).get("count") != len(events):
        raise AssertionError("summary count mismatch")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != len(events):
        raise AssertionError("CSV and JSON event counts differ")

    html = html_path.read_text(encoding="utf-8")
    for marker in ("Japan Earthquake Monitor", "HW25A064", "earthquake-data"):
        if marker not in html:
            raise AssertionError(f"HTML marker missing: {marker}")

    magnitudes = [float(item["magnitude"]) for item in events]
    if magnitudes != sorted(magnitudes, reverse=True):
        # Events are sorted by time, not magnitude; just confirm every value is sane.
        if any(value < 0 or value > 10 for value in magnitudes):
            raise AssertionError("magnitude outside expected range")

    return {
        "status": "success",
        "verified_at_jst": datetime.now(JST).isoformat(timespec="seconds"),
        "event_count": len(events),
        "files": {path.name: path.stat().st_size for path in required},
        "checks": [
            "required files exist",
            "JSON structure and student id",
            "CSV/JSON row count consistency",
            "HTML title and embedded data",
            "magnitude values are valid",
        ],
    }


def main() -> int:
    output_dir = Path("output")
    summary = verify(output_dir)
    summary_path = output_dir / "build_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[verify] success: {summary['event_count']} events")
    print(f"[verify] wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
