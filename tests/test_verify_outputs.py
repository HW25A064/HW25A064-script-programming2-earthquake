from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from src.verify_outputs import verify


class VerifyOutputTests(unittest.TestCase):
    def test_verify_accepts_consistent_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            event = {
                "event_id": "x1", "time_utc": "2026-01-01T00:00:00+00:00",
                "time_jst": "2026-01-01T09:00:00+09:00", "magnitude": 3.2,
                "place": "test", "latitude": 35.0, "longitude": 135.0,
                "depth_km": 10.0, "tsunami": False, "detail_url": ""
            }
            doc = {"student": {"id": "HW25A064"}, "summary": {"count": 1}, "events": [event]}
            (root / "earthquakes.json").write_text(json.dumps(doc), encoding="utf-8")
            (root / "earthquakes.csv").write_text(
                "event_id,time_utc,time_jst,magnitude,place,latitude,longitude,depth_km,tsunami,detail_url\n"
                "x1,2026,2026,3.2,test,35,135,10,False,\n", encoding="utf-8-sig"
            )
            (root / "index.html").write_text("Japan Earthquake Monitor HW25A064 earthquake-data", encoding="utf-8")
            result = verify(root)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["event_count"], 1)

    def test_verify_rejects_missing_files(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(AssertionError):
                verify(Path(temp))


if __name__ == "__main__":
    unittest.main()
