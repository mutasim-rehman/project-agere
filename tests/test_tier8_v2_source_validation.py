from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_analyze import validate_sources


class SourceValidationTests(unittest.TestCase):
    def test_changed_packets_require_explicit_flag(self):
        manifests = [{"data_sha256": x, "evaluation_source_sha256": "G", "config": {"task": "finqa"}} for x in ("A", "B")]
        with self.assertRaises(ValueError):
            validate_sources(manifests)
        self.assertFalse(validate_sources(manifests, True)["public_packets_identical"])

    def test_changed_references_or_unknown_task_cannot_be_overridden(self):
        first = {"data_sha256": "A", "evaluation_source_sha256": "G", "config": {"task": "finqa"}}
        for second in ({"data_sha256": "B", "evaluation_source_sha256": "OTHER", "config": {"task": "finqa"}},
                       {"data_sha256": "B", "config": {"task": "finqa"}},
                       {"data_sha256": "B", "evaluation_source_sha256": "G", "config": {"task": "kyc"}}):
            with self.assertRaises(ValueError):
                validate_sources([first, second], True)


if __name__ == "__main__":
    unittest.main()
