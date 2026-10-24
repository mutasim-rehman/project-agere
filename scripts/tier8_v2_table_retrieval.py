"""Shared table-complete retrieval control; no annotated evidence selection."""
import hashlib
import json
from pathlib import Path

from tier8_v2_finqa import packet

ROOT = Path(__file__).resolve().parents[1]


def table_complete_packet(row, text_limit=4):
    full = packet(row, limit=len(row["table"]) + len(row["pre_text"]) + len(row["post_text"]))
    chosen, text_count = {}, 0
    for key, value in full["evidence"].items():
        if key.startswith("table_"):
            chosen[key] = value
        elif text_count < text_limit:
            chosen[key] = value
            text_count += 1
    return {**full, "evidence": chosen, "retrieval": {
        "method": "all-table-rows-plus-lexical-top-text", "text_limit": text_limit,
        "source_units": full["retrieval"]["source_units"],
        "table_rows_retained": sum(k.startswith("table_") for k in chosen),
        "text_units_retained": text_count, "gold_used": False}}


def main():
    base = ROOT / "research/tier8_v2"
    source = base / "external/finqa/dataset-dev.json"
    rows = json.loads(source.read_text())[:24]
    public = [table_complete_packet(row) for row in rows]
    path = base / "data/finqa-development-table-complete.jsonl"
    path.write_text("".join(json.dumps(p, sort_keys=True) + "\n" for p in public))
    # Annotation audit follows selection; it cannot modify selected evidence.
    cases = [{"id": row["id"], "all_gold_retrieved": set(row["qa"]["gold_inds"]) <= set(p["evidence"]),
              "gold_units_retrieved": len(set(row["qa"]["gold_inds"]) & set(p["evidence"])),
              "gold_units_total": len(row["qa"]["gold_inds"]),
              "source_characters": sum(map(len, p["evidence"].values())),
              "selected_units": len(p["evidence"])} for row, p in zip(rows, public)]
    report = {"n": len(public), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "public_packets_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "policy": "All table rows plus four lexical-ranked text units; fixed first 24 development IDs; no gold selection",
              "all_gold_retrieved_cases": sum(r["all_gold_retrieved"] for r in cases),
              "gold_units_retrieved": sum(r["gold_units_retrieved"] for r in cases),
              "gold_units_total": sum(r["gold_units_total"] for r in cases),
              "tokenizer_fit_or_model_accuracy_tested": False, "test_opened": False, "cases": cases}
    (base / "evidence/table-complete-retrieval.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
