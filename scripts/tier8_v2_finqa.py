"""Prepare non-oracle financial-report evidence from FinQA development sources.

Gold programs, annotated rows and supplied model_input/retrieval fields NEVER
enter public packets. Lexical retrieval is shared preprocessing, not a new method.
"""
import collections
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STOP = set("a an the is are was were of in on for to and or what how much many did does as with from by at per".split())


def tokens(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


def packet(row, limit=8):
    evidence = {}
    header = row["table"][0] if row["table"] else []
    for i, cells in enumerate(row["table"][1:], 1):
        evidence[f"table_{i}"] = " ; ".join(f"{header[j] if j < len(header) else 'column ' + str(j)}: {value}" for j, value in enumerate(cells))
    # FinQA text_N indexes refer to concatenated pre_text and post_text.
    for i, text in enumerate(row["pre_text"] + row["post_text"]):
        if tokens(text):
            evidence[f"text_{i}"] = text
    question = row["qa"]["question"]
    query = collections.Counter(tokens(question))
    # Corpus-local inverse document frequency and length normalization.
    counts = {key: collections.Counter(tokens(text)) for key, text in evidence.items()}
    frequencies = collections.Counter(t for c in counts.values() for t in c)
    def score(key):
        count = counts[key]
        return sum(min(count[t], 2) * (len(counts) + 1) / (frequencies[t] + 1) for t in query) / max(1, sum(count.values()))**0.5
    selected = sorted(evidence, key=lambda k: (-score(k), k))[:limit]
    return {"id": row["id"], "split": "development", "question": question,
            "evidence": {key: evidence[key] for key in selected},
            "retrieval": {"method": "lexical-idf-length-normalized", "limit": limit,
                          "source_units": len(evidence), "gold_used": False}}


def main():
    root = ROOT / "research/tier8_v2"
    source = root / "external/finqa/dataset-dev.json"
    rows = json.loads(source.read_text())
    # A fixed prefix chosen before inference, no answer/program difficulty filter.
    subset = rows[:24]
    public = [packet(r) for r in subset]
    path = root / "data/finqa-development-public.jsonl"
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in public))
    # Retrieval evaluation is after packet construction and cannot change selection.
    evaluation = []
    for row, p in zip(subset, public):
        required = set(row["qa"]["gold_inds"])
        selected = set(p["evidence"])
        evaluation.append({"id": row["id"], "gold_units": sorted(required),
                           "selected_units": sorted(selected), "all_gold_retrieved": required <= selected,
                           "gold_retrieved": len(required & selected), "gold_total": len(required)})
    (root / "evidence/finqa-retrieval.json").write_text(json.dumps(evaluation, indent=2) + "\n")
    summary = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "n": len(public),
               "selected_ids": [p["id"] for p in public], "source_split": "development",
               "selection": "first 24 records, before model inference", "retrieval_limit": 8,
               "all_gold_retrieved_cases": sum(e["all_gold_retrieved"] for e in evaluation),
               "gold_units_retrieved": sum(e["gold_retrieved"] for e in evaluation),
               "gold_units_total": sum(e["gold_total"] for e in evaluation),
               "public_packets_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "test_opened": False}
    (root / "evidence/finqa-development-manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
