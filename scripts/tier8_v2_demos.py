"""Select two short, source-disjoint training demonstrations before evaluation.

Only training gold builds targets. Development answers never enter examples.
The deterministic eligibility rules and skipped counts are recorded for audit.
"""
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
from collections import Counter

from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import CONSTANTS, OPERATIONS, execute
from tier8_v2_finqa import packet
from tier8_v2_financial_pipeline import reported_reference

ROOT = Path(__file__).resolve().parents[1]


def target_plan(row, public, atoms):
    text = row["qa"]["program"]
    parsed = re.findall(r"([a-z_]+)\(([^,]+),\s*([^\)]+)\)", text)
    if not 1 <= len(parsed) <= 4 or any(op not in OPERATIONS for op, _, _ in parsed):
        raise ValueError("unsupported_program")
    gold_sources = set(row["qa"]["gold_inds"])
    def reference(value):
        value = value.strip()
        if re.fullmatch(r"#\d+", value):
            return value
        literal = value.removeprefix("const_").replace("m1", "-1")
        number = Decimal(literal)
        if value.startswith("const_"):
            if number not in CONSTANTS:
                raise ValueError("unsupported_constant")
            return "CONST:" + format(number, "f").split(".")[0]
        matching = [k for k, a in atoms.items() if Decimal(a["value"]) == number]
        preferred = [k for k in matching if atoms[k]["span_id"] in gold_sources]
        if preferred or matching:
            return (preferred or matching)[0]
        raise ValueError("unretrieved_operand")
    plan = {"decision": "ANSWER", "answer_unit": "number", "steps": [
        {"op": op, "left": reference(a), "right": reference(b)} for op, a, b in parsed]}
    if len(plan["steps"]) == 1:
        step = plan["steps"][0]
        if (step["op"] in ("multiply", "divide") and step["right"] == "CONST:1") or (step["op"] in ("add", "subtract") and step["right"] == "CONST:0"):
            raise ValueError("identity_only_program")
    compiled = compile_plan(plan, atoms)
    if len(compiled["steps"]) == 1:
        first = compiled["steps"][0]
        if not any(first[side]["value"].startswith("#") for side in ("left", "right")):
            left, right = (Decimal(first[s]["value"]) for s in ("left", "right"))
            if (first["op"] == "multiply" and 1 in (left, right)) or (first["op"] == "divide" and right == 1) or (first["op"] == "add" and 0 in (left, right)) or (first["op"] == "subtract" and right == 0):
                raise ValueError("identity_only_program")
    execution = execute(compiled["steps"], public["evidence"])
    if execution["issues"]:
        raise ValueError("unexecutable_target")
    value = Decimal(execution["value"])
    expected = Decimal(str(row["qa"]["exe_ans"]))
    if abs(value - expected) > max(Decimal("0.00001"), abs(expected) * Decimal("0.00001")):
        raise ValueError("gold_execution_mismatch")
    ref = reported_reference(row["qa"]["answer"])
    if not ref:
        raise ValueError("unsupported_reported_reference")
    tolerance = max(ref["tolerance"], Decimal("0.00001"))
    if abs(value - ref["value"]) <= tolerance:
        plan["answer_unit"] = "fraction" if ref["percent"] else "number"
    elif ref["percent"] and abs(value / 100 - ref["value"]) <= tolerance:
        plan["answer_unit"] = "percent"
    else:
        raise ValueError("reported_execution_disagreement")
    # Match the grounded causal grammar, not merely generic execution validity.
    for i, step in enumerate(plan["steps"]):
        if not any(v.startswith("A") or (v.startswith("#") and int(v[1:]) < i) for v in (step["left"], step["right"])):
            raise ValueError("constant_only_step")
    return plan


def example_text(public, atoms, target):
    return ("Training example question: " + public["question"] + "\nEvidence: " + json.dumps(public["evidence"])
            + "\nQuantities: " + "; ".join(f"{k}={v['value']}@{v['span_id']}" for k, v in atoms.items())
            + "\nCorrect program: " + json.dumps(target))


def main():
    source = ROOT / ".local/datasets/finqa/train.json"
    train = json.loads(source.read_text())
    dev = json.loads((ROOT / "research/tier8_v2/external/finqa/dataset-dev.json").read_text())
    dev_documents = {r["id"].rsplit("-", 1)[0] for r in dev}
    chosen, skipped = [], Counter()
    used_documents, used_buckets = set(), set()
    for row in sorted(train, key=lambda r: r["id"]):
        if row["id"].rsplit("-", 1)[0] in dev_documents:
            skipped["development_document_overlap"] += 1
            continue
        if row["id"].rsplit("-", 1)[0] in used_documents:
            skipped["duplicate_demonstration_document"] += 1
            continue
        public = packet(row)
        atoms = atom_catalog(public["evidence"])
        try:
            target = target_plan(row, public, atoms)
        except (ValueError, InvalidOperation) as exc:
            skipped[str(exc)] += 1
            continue
        text = example_text(public, atoms, target)
        bucket = "single_step" if len(target["steps"]) == 1 else "multi_step"
        if bucket in used_buckets:
            skipped["operation_length_bucket_already_selected"] += 1
            continue
        if len(text) > 1800:
            skipped["example_longer_than_1800_chars"] += 1
            continue
        chosen.append({"source_id": row["id"], "split": "train", "text": text,
                       "target": target, "bucket": bucket, "document_disjoint_from_all_development": True})
        used_documents.add(row["id"].rsplit("-", 1)[0])
        used_buckets.add(bucket)
        if len(chosen) == 2:
            break
    if len(chosen) != 2:
        raise RuntimeError("Could not find two eligible training examples")
    result = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "examples": chosen,
              "selection": "first eligible single-step and multi-step sorted training IDs; distinct documents, <=4 operations, <=1800 chars, no identity-only programs, disjoint from all dev",
              "skipped_before_selection_complete": dict(skipped), "development_answers_used": False, "test_opened": False}
    (ROOT / "research/tier8_v2/data/finqa-training-demos.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"ids": [r["source_id"] for r in chosen], "skipped": dict(skipped)}, indent=2))


if __name__ == "__main__":
    main()
