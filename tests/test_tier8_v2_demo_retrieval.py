import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_demo_retrieval import DemoIndex, report_group, build_bank


class DemoRetrievalTests(unittest.TestCase):
    def test_question_similarity_beats_matching_calendar_year(self):
        examples = [{"source_id": "A/2020/page_1.pdf-1", "question": "what was the percent growth in revenue?"},
                    {"source_id": "B/2021/page_1.pdf-1", "question": "what was the average payment volume per transaction?"}]
        selected = DemoIndex(examples).select("average payment volume per transaction in 2020?", 1)
        self.assertEqual(selected[0]["source_id"], examples[1]["source_id"])

    def test_selection_is_stable_and_report_diverse(self):
        examples = [{"source_id": ident, "question": "percent growth in revenue"}
                    for ident in ("A/2020/page_2.pdf-1", "B/2020/page_1.pdf-1", "A/2020/page_1.pdf-1")]
        selected = DemoIndex(examples).select("percent growth in revenue", 2)
        self.assertEqual([e["source_id"] for e in selected], ["A/2020/page_1.pdf-1", "B/2020/page_1.pdf-1"])
        self.assertEqual(report_group(selected[0]["source_id"]), "A/2020")

    def test_excluded_reports_are_removed_before_reading_training_targets(self):
        examples, skipped = build_bank([{"id": "A/2020/page_1.pdf-1", "qa": {"answer": "DO NOT READ"}}], {"A/2020"})
        self.assertEqual(examples, [])
        self.assertEqual(skipped, {"development_report_overlap": 1})

    def test_no_overlap_does_not_force_irrelevant_example(self):
        self.assertEqual(DemoIndex([{"source_id": "A/1/p-1", "question": "debt"}]).select("inventory", 2), [])
        self.assertEqual(DemoIndex([]).select("debt", 2), [])

    def test_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            DemoIndex([{"source_id": "A", "question": "debt"}] * 2)


if __name__ == "__main__":
    unittest.main()
