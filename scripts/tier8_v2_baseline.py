"""Independent deployment rule baseline for the original key=value benchmark.

No labels or expected_facts are used to construct predictions. The old evaluator
is called only after prediction, to expose how much of v1 needs an LLM at all.
"""
import hashlib
import json
from pathlib import Path

from prepare_project_datasets import make_credit, make_kyc
import phase3

ROOT = Path(__file__).resolve().parents[1]


def predict(case):
    extracted = phase3.document_extractor(case)["fields"]
    def field(key, *, strip_owner=False):
        entries = extracted.get(key, [])
        if len(entries) != 1:
            return {"value": "MISSING", "span_id": None}
        item = entries[0]
        value = item["value"].rsplit(" (", 1)[0] if strip_owner else item["value"]
        return {"value": "MISSING" if value == "NOT_PROVIDED" else value,
                "span_id": None if value == "NOT_PROVIDED" else item["span_id"]}
    if case["_kind"] == "kyc":
        facts = {"registry_name": field("beneficial_owner_1", strip_owner=True),
                 "declared_name": field("applicant_name"),
                 "screening_status": field("status"), "identity_expiry_date": field("expiry")}
        mismatch = facts["registry_name"]["value"] != facts["declared_name"]["value"]
    else:
        numbers = {}
        for key in ("operating_profit_pkr", "annual_debt_service_pkr", "current_assets_pkr", "current_liabilities_pkr"):
            numbers[key] = int(field(key)["value"])
        facts = {"e_cib_status": field("status"), "e_cib_last_review_date": field("last_review_date"),
                 "dscr": {"value": round(numbers["operating_profit_pkr"] / numbers["annual_debt_service_pkr"], 4), "span_id": "CALC#DSCR"},
                 "current_ratio": {"value": round(numbers["current_assets_pkr"] / numbers["current_liabilities_pkr"], 4), "span_id": "CALC#CURRENT_RATIO"}}
        mismatch = None
    return {"case_id": case["id"], "facts": facts, "identity_name_mismatch": mismatch,
            "draft": "Structured evidence prepared for human review."}


def main():
    out = ROOT / "research/tier8_v2/evidence"
    rows = []
    for kind, make, n in (("kyc", make_kyc, 100), ("credit", make_credit, 50)):
        for i in range(n):
            case = make("dev", i)
            case["_kind"] = kind
            # Remove labels before calling deployment code; retain independent gold for scoring.
            deployment = {k: v for k, v in case.items() if k not in ("labels", "calculator_inputs")}
            prediction = predict(deployment)
            score = phase3.score_case(case, prediction, phase3.common_tools(case), "sas")
            rows.append({"case_id": case["id"], "answer": prediction, "score": score})
    payload = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    (out / "deterministic-dev-cases.jsonl").write_text(payload)
    summary = {"dataset": "agere-synth-v1/dev", "n": len(rows),
               "case_success": sum(not r["score"]["failure_tag"] for r in rows) / len(rows),
               "mismatch_eligible": sum(r["score"]["mismatch_eligible"] for r in rows),
               "missing_fields": sum(r["score"]["refusal_total"] for r in rows),
               "generated_tokens": 0, "test_opened": False,
               "cases_sha256": hashlib.sha256(payload.encode()).hexdigest(),
               "scope": "Structured facts only. Fixed templates; no prose quality or policy reasoning assessment."}
    (out / "deterministic-dev-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
