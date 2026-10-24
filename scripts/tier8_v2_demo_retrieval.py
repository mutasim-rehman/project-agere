"""Question-only BM25 training demonstrations: a baseline, not a novel method.

Training labels construct example targets offline. Development contributes report
IDs for exclusion only; its answers/programs never enter retrieval or prompting.
"""
from collections import Counter
from decimal import InvalidOperation
import hashlib
import json
import math
from pathlib import Path

from evidence_atoms import atom_catalog
from tier8_v2_demos import target_plan, example_text
from tier8_v2_finqa import packet, tokens

ROOT = Path(__file__).resolve().parents[1]
BANK = "research/tier8_v2/data/finqa-training-demo-bank.json"


def report_group(source_id):
    return source_id.rsplit("/", 1)[0]


def query_tokens(question):
    # Calendar years/numerals should not dominate formula similarity.
    return [t for t in tokens(question) if not t.isdigit()]


class DemoIndex:
    def __init__(self, examples):
        self.examples = sorted(examples, key=lambda e: e["source_id"])
        ids = [e["source_id"] for e in self.examples]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate training example IDs")
        self.counts = [Counter(query_tokens(e["question"])) for e in self.examples]
        self.df = Counter(t for counts in self.counts for t in counts)
        self.average_length = sum(map(lambda c: sum(c.values()), self.counts)) / max(1, len(self.counts))

    def select(self, question, count=2):
        if count not in (0, 1, 2):
            raise ValueError("At most two demonstrations are supported")
        query = set(query_tokens(question))
        ranked = []
        for example, frequencies in zip(self.examples, self.counts):
            norm = 1.2 * (0.25 + 0.75 * sum(frequencies.values()) / max(1, self.average_length))
            score = sum(math.log(1 + (len(self.examples) - self.df[t] + 0.5) / (self.df[t] + 0.5))
                        * frequencies[t] * 2.2 / (frequencies[t] + norm)
                        for t in query if frequencies[t])
            if score > 0:
                ranked.append((score, example))
        chosen, groups = [], set()
        for score, example in sorted(ranked, key=lambda item: (-item[0], item[1]["source_id"])):
            if len(chosen) >= count:
                break
            group = report_group(example["source_id"])
            if group not in groups:
                chosen.append({**example, "retrieval_score": score})
                groups.add(group)
        return chosen


def build_bank(train, excluded_groups):
    examples, skipped = [], Counter()
    for row in sorted(train, key=lambda r: r["id"]):
        if report_group(row["id"]) in excluded_groups:
            skipped["development_report_overlap"] += 1
            continue
        public = packet(row)
        atoms = atom_catalog(public["evidence"])
        try:
            target = target_plan(row, public, atoms)
        except (ValueError, InvalidOperation) as exc:
            skipped[str(exc)] += 1
            continue
        text = example_text(public, atoms, target)
        if len(text) > 1800:
            skipped["example_longer_than_1800_chars"] += 1
            continue
        examples.append({"source_id": row["id"], "split": "train", "question": public["question"],
                         "text": text, "target": target, "report_disjoint_from_all_development": True})
    return examples, dict(skipped)


def main():
    train_path = ROOT / ".local/datasets/finqa/train.json"
    dev_path = ROOT / "research/tier8_v2/external/finqa/dataset-dev.json"
    train = json.loads(train_path.read_text())
    # Do not use question, answer, program or gold evidence for exclusion.
    excluded = {report_group(row["id"]) for row in json.loads(dev_path.read_text())}
    examples, skipped = build_bank(train, excluded)
    if not examples:
        raise RuntimeError("No eligible report-disjoint examples")
    result = {"source_sha256": hashlib.sha256(train_path.read_bytes()).hexdigest(),
              "development_source_sha256": hashlib.sha256(dev_path.read_bytes()).hexdigest(),
              "examples": examples, "eligible_examples": len(examples), "skipped": skipped,
              "excluded_report_groups": sorted(excluded), "development_answers_used": False,
              "test_opened": False, "selection": "question-only BM25, k1=1.2 b=0.75; numeric tokens omitted; stable IDs break ties; distinct report groups; <=1800 characters per example"}
    (ROOT / BANK).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("examples", "excluded_report_groups")}, indent=2))


if __name__ == "__main__":
    main()
