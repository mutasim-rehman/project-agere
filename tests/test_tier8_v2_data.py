import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_data import generate, evaluate
from evidence_contract import source_spans, validate


class DataTests(unittest.TestCase):
    def test_all_latent_answers_are_source_supported(self):
        for i in range(24):
            case = generate(i)
            answer = {"case_id": case["id"], **case["gold"]}
            self.assertTrue(evaluate(case, answer)["case_success"])
            self.assertEqual(validate(answer, case_id=case["id"], fields=tuple(case["gold"]["facts"]),
                                      spans=source_spans(case["case_documents"]), calculations={}), [])

    def test_supported_stale_owner_is_semantically_wrong(self):
        case = generate(0)
        answer = copy.deepcopy({"case_id": case["id"], **case["gold"]})
        old = next(d for d in case["case_documents"] if "2025-09-01" in d["lines"][0])
        owner = old["lines"][0].split("records ")[1].split(" as ")[0]
        answer["facts"]["registered_owner"] = {"value": owner, "span_id": old["id"] + "#L01"}
        self.assertEqual(validate(answer, case_id=case["id"], fields=tuple(case["gold"]["facts"]),
                                  spans=source_spans(case["case_documents"]), calculations={}), [])
        self.assertFalse(evaluate(case, answer)["case_success"])

    def test_document_ids_do_not_reveal_source_roles(self):
        for doc in generate(0)["case_documents"]:
            self.assertRegex(doc["id"], r"^EVIDENCE-DEV-0000-DOC-\d+$")


if __name__ == "__main__":
    unittest.main()
