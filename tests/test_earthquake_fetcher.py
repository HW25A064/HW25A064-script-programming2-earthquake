from __future__ import annotations
import json
import unittest
from pathlib import Path

from src.earthquake_fetcher import calculate_summary, normalize_geojson

FIXTURE = Path(__file__).resolve().parents[1] / "data" / "sample_usgs_japan.json"


class EarthquakeFetcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.events = normalize_geojson(cls.payload)

    def test_fixture_normalizes_all_events(self):
        self.assertEqual(len(self.events), 12)
        self.assertTrue(all(event.event_id for event in self.events))

    def test_events_are_sorted_newest_first(self):
        times = [event.time_utc for event in self.events]
        self.assertEqual(times, sorted(times, reverse=True))

    def test_coordinates_and_depth_are_mapped(self):
        first = self.events[0]
        self.assertGreater(first.latitude, 20)
        self.assertGreater(first.longitude, 120)
        self.assertGreaterEqual(first.depth_km, 0)

    def test_summary_values(self):
        summary = calculate_summary(self.events)
        self.assertEqual(summary["count"], 12)
        self.assertEqual(summary["max_magnitude"], 5.4)
        self.assertEqual(summary["magnitude_5_or_more"], 2)


if __name__ == "__main__":
    unittest.main()
