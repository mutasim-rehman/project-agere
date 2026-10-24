import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_sequence import inside, require_complete


class SequenceTests(unittest.TestCase):
    def test_paths_cannot_escape_checkout(self):
        with self.assertRaises(ValueError):
            inside("../../outside")

    def test_failed_or_over_cap_dependency_cannot_release_queue(self):
        valid = {"status": "complete", "exit_code": 0, "n": 2, "expected": 2,
                 "peak_tree_rss_bytes": 50, "cap_bytes": 100}
        for field, value in (("status", "failed"), ("exit_code", 1), ("n", 1), ("peak_tree_rss_bytes", 101)):
            with patch.object(Path, "read_text", return_value=json.dumps({**valid, field: value})):
                with self.assertRaises(ValueError):
                    require_complete("research/tier8_v2/runs/example")


if __name__ == "__main__":
    unittest.main()
