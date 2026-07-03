#!/usr/bin/env python3
"""Fetch and normalize recent earthquake data around Japan.

The live source is the USGS Earthquake Catalog GeoJSON API.  The script can
fall back to a bundled fixture so the Jenkins pipeline remains testable even
when the external service is temporarily unavailable.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

JST = timezone(timedelta(hours=9))
DEFAULT_FIXTURE = Path(__file__).resolve().parents[1] / "data" / "sample_usgs_japan.json"
USGS_ENDPOINT = "https://earthquake.usgs.gov/fdsnws/event/1/query"


@dataclass(frozen=True)
class Earthquake:
    event_id: str
    time_utc: str
    time_jst: str
    magnitude: float
    place: str
    latitude: float
    longitude: float
    depth_km: float
    tsunami: bool
    detail_url: str


def _iso_from_epoch_ms(value: int | float, tz: timezone) -> str:
    return datetime.fromtimestamp(float(value) / 1000.0, tz=timezone.utc).astimezone(tz).isoformat(timespec="seconds")


def normalize_feature(feature: dict[str, Any]) -> Earthquake:
    properties = feature.get("properties") or {}
    geometry = feature.get("geometry") or {}
    coordinates = geometry.get("coordinates") or [0.0, 0.0, 0.0]
    if len(coordinates) < 3:
        coordinates = list(coordinates) + [0.0] * (3 - len(coordinates))

    mag = properties.get("mag")
    if mag is None:
        mag = 0.0
    epoch_ms = properties.get("time")
    if epoch_ms is None:
        raise ValueError("feature is missing properties.time")

    return Earthquake(
        event_id=str(feature.get("id") or "unknown"),
        time_utc=_iso_from_epoch_ms(epoch_ms, timezone.utc),
        time_jst=_iso_from_epoch_ms(epoch_ms, JST),
        magnitude=round(float(mag), 1),
        place=str(properties.get("place") or "場所不明"),
        latitude=round(float(coordinates[1]), 4),
        longitude=round(float(coordinates[0]), 4),
        depth_km=round(float(coordinates[2]), 1),
        tsunami=bool(properties.get("tsunami") or 0),
        detail_url=str(properties.get("url") or ""),
    )


def normalize_geojson(payload: dict[str, Any]) -> list[Earthquake]:
    events: list[Earthquake] = []
    for feature in payload.get("features", []):
        try:
            events.append(normalize_feature(feature))
        except (TypeError, ValueError, IndexError):
            continue
    events.sort(key=lambda item: item.time_utc, reverse=True)
    return events


def calculate_summary(events: Iterable[Earthquake]) -> dict[str, Any]:
    items = list(events)
    if not items:
        return {
            "count": 0,
            "max_magnitude": 0.0,
            "average_magnitude": 0.0,
            "average_depth_km": 0.0,
            "magnitude_5_or_more": 0,
            "tsunami_events": 0,
        }
    return {
        "count": len(items),
        "max_magnitude": round(max(item.magnitude for item in items), 1),
        "average_magnitude": round(mean(item.magnitude for item in items), 2),
        "average_depth_km": round(mean(item.depth_km for item in items), 1),
        "magnitude_5_or_more": sum(item.magnitude >= 5.0 for item in items),
        "tsunami_events": sum(item.tsunami for item in items),
    }


def build_query(days: int, min_magnitude: float) -> str:
    now = datetime.now(timezone.utc)
    params = {
        "format": "geojson",
        "starttime": (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "minmagnitude": str(min_magnitude),
        "minlatitude": "20.0",
        "maxlatitude": "46.5",
        "minlongitude": "122.0",
        "maxlongitude": "154.0",
        "orderby": "time",
        "limit": "200",
    }
    return f"{USGS_ENDPOINT}?{urllib.parse.urlencode(params)}"


def fetch_live(days: int, min_magnitude: float, timeout: int = 20) -> dict[str, Any]:
    request = urllib.request.Request(
        build_query(days, min_magnitude),
        headers={"User-Agent": "HW25A064-earthquake-dashboard/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"USGS returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def make_document(events: list[Earthquake], source: str, query_days: int, min_magnitude: float) -> dict[str, Any]:
    generated = datetime.now(JST).isoformat(timespec="seconds")
    return {
        "student": {"id": "HW25A064", "name": "實光駿斗"},
        "project": "Japan Earthquake Monitor",
        "generated_at_jst": generated,
        "source": source,
        "query": {"days": query_days, "minimum_magnitude": min_magnitude},
        "summary": calculate_summary(events),
        "events": [asdict(event) for event in events],
    }


def write_json(document: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(events: list[Earthquake], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(Earthquake.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for event in events:
            writer.writerow(asdict(event))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Japan earthquake data collector")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--min-magnitude", type=float, default=2.5)
    parser.add_argument("--output-json", type=Path, default=Path("output/earthquakes.json"))
    parser.add_argument("--output-csv", type=Path, default=Path("output/earthquakes.csv"))
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--offline", action="store_true", help="Use the bundled fixture without network access")
    parser.add_argument("--allow-fallback", action="store_true", help="Use the fixture if the live API fails")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = "USGS Earthquake Catalog API"
    if args.offline:
        payload = load_fixture(args.fixture)
        source = f"offline fixture: {args.fixture.name}"
    else:
        try:
            payload = fetch_live(args.days, args.min_magnitude)
        except Exception as exc:  # Jenkins needs a deterministic fallback path.
            if not args.allow_fallback:
                print(f"[fetch] failed: {exc}", file=sys.stderr)
                return 1
            print(f"[fetch] live API failed, using fixture: {exc}")
            payload = load_fixture(args.fixture)
            source = f"fallback fixture: {args.fixture.name}"

    events = [event for event in normalize_geojson(payload) if event.magnitude >= args.min_magnitude]
    if not events:
        print("[fetch] no earthquake events were available", file=sys.stderr)
        return 2

    document = make_document(events, source, args.days, args.min_magnitude)
    write_json(document, args.output_json)
    write_csv(events, args.output_csv)
    print(f"[fetch] source={source}")
    print(f"[fetch] events={len(events)} max_magnitude={document['summary']['max_magnitude']}")
    print(f"[fetch] wrote {args.output_json} and {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
