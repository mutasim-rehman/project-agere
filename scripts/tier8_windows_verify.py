"""Replay a binary verifier on frozen Windows one-step candidates."""
import argparse
import json
from pathlib import Path

from evidence_contract import TokenLedger
from financial_review_protocol import BINARY_INSTRUCTION, BINARY_SCHEMA, binary_review
from tier8_windows_pilot import Models, ROOT, jsonl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cli", "weights", "output", "candidates"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--review-model", choices=("verifier", "drafter"), default="verifier",
                        help="Use the 0.5B verifier or reuse the 3B drafter checkpoint")
    args = parser.parse_args()
    rows = jsonl(args.candidates)
    packets = {row["id"]: row for row in jsonl(
        ROOT / "research/tier8_v2/data/finqa-development-public.jsonl")}
    if not rows or len({r["case_id"] for r in rows}) != len(rows):
        raise ValueError("Expected distinct frozen candidates")
    model = Models(args)
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "replay.jsonl").open("x", encoding="utf-8") as ledger:
        for row in rows:
            packet = packets[row["case_id"]]
            answer, execution = row["initial_answer"], row["initial_execution"]
            if execution["issues"] or execution["value"] is None:
                raise ValueError(f"Expected an executable candidate: {row['case_id']}")
            prompt = ("Question: " + packet["question"] + "\nFinancial report evidence by source ID:\n"
                      + json.dumps(packet["evidence"]) + "\nProposed program:\n" + json.dumps(answer)
                      + "\nDeterministic execution:\n" + json.dumps(execution) + "\n" + BINARY_INSTRUCTION)
            raw, event = model.call(args.review_model, prompt, BINARY_SCHEMA,
                                    TokenLedger(), 192, "binary_review")
            binary = binary_review(raw)
            rich = row["initial_verdict"]
            fields_pass = bool(rich and all(v == "PASS" for v in rich["checks"].values()))
            result = dict(case_id=row["case_id"], score=row["score"], rich=rich,
                          fields_only_pass=fields_pass, binary=binary, stage=event,
                          review_model=args.review_model)
            ledger.write(json.dumps(result) + "\n")
            ledger.flush()
            print(row["case_id"], row["score"]["case_success"], fields_pass, raw, flush=True)


if __name__ == "__main__":
    main()
