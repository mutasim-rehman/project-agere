"""Rule-only control for the temporal KYC pilot; no labels used for prediction.

The parser explicitly supports this development generator's wording. Its success
does not demonstrate arbitrary-document understanding or held-out generalization.
"""
import json
from pathlib import Path
import re

from evidence_contract import source_spans
from tier8_v2_data import evaluate

ROOT = Path(__file__).resolve().parents[1]


def predict(public):
    spans = source_spans(public["case_documents"])
    registry = []
    applicant = None
    expiry = None
    for span, text in spans.items():
        if "registry" in text.lower() or "filing" in text.lower():
            patterns = [r"records (.+?) as the beneficial owner", r"names (.+?) as beneficial owner",
                        r"attributed to (.+?) in the registry", r"beneficial owner as (.+?)\."]
            names = [m[1] for p in patterns if (m := re.search(p, text))]
            dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text)
            if len(names) == 1 and len(dates) == 1:
                registry.append((dates[0], {"value": names[0], "span_id": span}))
        if match := re.search(r"applicant declares their name as (.+?) on the onboarding form", text):
            applicant = {"value": match[1], "span_id": span}
        if "identity" in text.lower() and "internal note" not in text.lower():
            if "expiry date was not supplied" in text:
                expiry = {"value": "MISSING", "span_id": span}
            elif match := re.search(r"identity document expires on (\d{4}-\d{2}-\d{2})", text):
                expiry = {"value": match[1], "span_id": span}
    owner = max(registry, key=lambda item: item[0])[1] if registry else None
    facts = {"registered_owner": owner, "declared_applicant": applicant, "identity_expiry_date": expiry}
    return {"case_id": public["id"], "facts": facts,
            "identity_name_mismatch": owner["value"] != applicant["value"] if owner and applicant else None}


def main():
    root = ROOT / "research/tier8_v2/evidence"
    rows = [json.loads(s) for s in (ROOT / "research/tier8_v2/data/development.jsonl").read_text().splitlines()]
    records = []
    for case in rows:
        public = {k: v for k, v in case.items() if k != "gold"}
        answer = predict(public)
        records.append({"case_id": case["id"], "answer": answer, "score": evaluate(case, answer)})
    (root / "temporal-rules-cases.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records))
    summary = {"n": len(records), "case_successes": sum(r["score"]["case_success"] for r in records),
               "generated_tokens": 0, "scope": "Generator-aware development control; not held-out or arbitrary-document validation."}
    (root / "temporal-rules-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
