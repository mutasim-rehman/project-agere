"""Development-only evidence-selection probes. No confirmatory test generation.

Gold is produced from latent records, separately from deployment source checks.
This is a synthetic pilot, not a substitute for real-document external validation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("registered_owner", "declared_applicant", "identity_expiry_date")
NAMES = ("Amina Cedar", "Bilal Harbor", "Dania Willow", "Ehsan Quartz", "Farah Maple", "Haris Indigo")


def generate(index: int, seed: int = 20261024) -> dict:
    rng = random.Random(seed + index * 7919)
    owner, stale_owner, other = rng.sample(NAMES, 3)
    mismatch = index % 2 == 0
    missing = index % 3 == 0
    applicant = other if mismatch else owner
    cid = f"EVIDENCE-DEV-{index:04d}"
    # Opaque randomized IDs must not disclose which source is authoritative.
    ids = rng.sample(range(100, 999), 5)
    registry = f"{cid}-DOC-{ids[0]}#L01"
    declaration = f"{cid}-DOC-{ids[1]}#L01"
    identity = f"{cid}-DOC-{ids[2]}#L01"
    templates = (
        f"The registry extract issued on 2026-09-01 records {owner} as the beneficial owner.",
        f"As of its issue date, 2026-09-01, this registry names {owner} as beneficial owner.",
        f"Beneficial ownership is attributed to {owner} in the registry dated 2026-09-01.",
        f"This filing, issued 2026-09-01, identifies the beneficial owner as {owner}.",
    )
    docs = [
        {"id": registry.split("#")[0], "lines": ["L01 " + templates[index % len(templates)]]},
        {"id": f"{cid}-DOC-{ids[3]}", "lines": [f"L01 A registry extract issued on 2025-09-01 records {stale_owner} as the beneficial owner."]},
        {"id": declaration.split("#")[0], "lines": [f"L01 The applicant declares their name as {applicant} on the onboarding form signed 2026-09-02."]},
        {"id": identity.split("#")[0], "lines": ["L01 The identity expiry date was not supplied." if missing else "L01 The identity document expires on 2028-12-31."]},
        {"id": f"{cid}-DOC-{ids[4]}", "lines": [f"L01 Relationship manager {other} scheduled a review for 2029-12-31. This is an internal note, not an identity record or registry filing."]},
    ]
    rng.shuffle(docs)
    truth = {
        "registered_owner": {"value": owner, "span_id": registry},
        "declared_applicant": {"value": applicant, "span_id": declaration},
        "identity_expiry_date": {"value": "MISSING" if missing else "2028-12-31", "span_id": identity},
    }
    return {"id": cid, "split": "development", "family": "temporal_identity_reconciliation",
            "template": index % len(templates), "case_documents": docs,
            "task": "Use the most recently issued registry for registered_owner; use the onboarding form for declared_applicant. Read identity_expiry_date only from the identity record. Cite explicit absence when returning MISSING. Compare owner with applicant for identity_name_mismatch. Internal notes are not authoritative for these fields.",
            "gold": {"facts": truth, "identity_name_mismatch": mismatch}}


def evaluate(case: dict, answer) -> dict:
    facts = answer.get("facts", {}) if isinstance(answer, dict) else {}
    correct = {field: facts.get(field) == expected for field, expected in case["gold"]["facts"].items()}
    mismatch_correct = isinstance(answer, dict) and type(answer.get("identity_name_mismatch")) is bool and answer["identity_name_mismatch"] == case["gold"]["identity_name_mismatch"]
    return {"field_correct": correct, "mismatch_correct": mismatch_correct,
            "case_success": all(correct.values()) and mismatch_correct and answer.get("case_id") == case["id"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=24)
    args = parser.parse_args()
    root = ROOT / "research/tier8_v2/data"
    root.mkdir(exist_ok=True)
    rows = [generate(i) for i in range(args.count)]
    for name, data in (("development.jsonl", rows), ("development-public.jsonl", [{k: v for k, v in r.items() if k != "gold"} for r in rows])):
        payload = "".join(json.dumps(r, sort_keys=True) + "\n" for r in data)
        (root / name).write_text(payload)
    print(json.dumps({"n": len(rows), "sha256": hashlib.sha256((root / "development.jsonl").read_bytes()).hexdigest(), "split": "development", "test_created": False}))


if __name__ == "__main__":
    main()
