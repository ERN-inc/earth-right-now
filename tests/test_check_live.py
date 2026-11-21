"""Regression: extraction errors must not publish a false offline status."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import check_live

class LiveDetectorSafetyTest(unittest.TestCase):
    def test_extractor_offline_message_is_not_authoritative(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "live.json"
            previous = {"status":"live","videoId":"xrYBoAiEnRc"}
            output.write_text(json.dumps(previous), encoding="utf-8")
            class Result:
                returncode = 1
                stderr = "The channel is not currently live"
                stdout = ""
            with patch.object(check_live, "OUTPUT", output), \
                 patch.object(check_live.subprocess, "run", return_value=Result()), \
                 patch.object(check_live, "fallback_live_page", return_value=None):
                self.assertEqual(check_live.legacy_lookup(), 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), previous)

    def test_verified_live_id_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "live.json"
            with patch.object(check_live, "OUTPUT", output):
                self.assertEqual(check_live.write_status({"live_status":"is_live","id":"xrYBoAiEnRc"}), 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["videoId"], "xrYBoAiEnRc")
if __name__ == "__main__":
    unittest.main()
