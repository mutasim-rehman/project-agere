"""Compare label-blind retrieval on the public FinQA development split."""
import argparse
from collections import Counter, defaultdict
from decimal import InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import random
from statistics import median

from tokenizers import Tokenizer

from evidence_atoms import atom_catalog
from program_binding_domains import binding_domains
from tier8_v2_demo_retrieval import report_group
from tier8_v2_finqa import packet, tokens


def bm25_rank(query, documents, original_order):
    counts = {key: Counter(tokens(text)) for key, text in documents.items()}
    df = Counter(term for count in counts.values() for term in count)
    n = len(counts)
    lengths = {key: sum(count.values()) for key, count in counts.items()}
    average = max(1, sum(lengths.values()) / max(1, n))
    terms = set(tokens(query))
    scores = {}
    for key, count in counts.items():
        length_factor = 1.2 * (0.25 + 0.75 * lengths[key] / average)
        scores[key] = sum(math.log1p((n - df[term] + 0.5) / (df[term] + 0.5))
                          * 2.2 * count[term] / (count[term] + length_factor)
                          for term in sorted(terms))
    return sorted(counts, key=lambda key: (-scores[key], original_order[key]))


def draft_evidence_tokens(tokenizer, evidence):
    atoms = atom_catalog(evidence)
    catalog = "\n".join(f"{key}={atom['value']}@{atom['span_id']}" for key, atom in atoms.items())
    return len(tokenizer.encode(json.dumps(evidence) + "\n" + catalog).ids)


class DenseRanker:
    def __init__(self, weights):
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        torch.set_num_threads(2)
        self.tokenizer = AutoTokenizer.from_pretrained(weights, local_files_only=True)
        self.model = AutoModel.from_pretrained(weights, local_files_only=True).eval()
        self.documents = {}

    def encode(self, texts):
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True,
                                truncation=True, max_length=512)
        with self.torch.inference_mode():
            features = self.model(**inputs).last_hidden_state[:, 0]
            return self.torch.nn.functional.normalize(features, p=2, dim=1)

    def rank(self, question, evidence):
        if not evidence:
            return []
        pending = list(dict.fromkeys(text for text in evidence.values() if text not in self.documents))
        for start in range(0, len(pending), 32):
            batch = pending[start:start + 32]
            self.documents.update(zip(batch, self.encode(batch)))
        query = self.encode(["Represent this sentence for searching relevant passages: " + question])[0]
        scores = self.torch.stack([self.documents[text] for text in evidence.values()]) @ query
        return sorted(evidence, key=dict(zip(evidence, (-scores).tolist())).__getitem__)


def ranked_packets(row, tokenizer, dense=None):
    full = packet(row, limit=len(row["table"]) + len(row["pre_text"]) + len(row["post_text"]))
    evidence = full["evidence"]
    base_rank = list(evidence)
    original = {key: rank for rank, key in enumerate(base_rank)}
    base = dict(list(evidence.items())[:8])
    cap = draft_evidence_tokens(tokenizer, base)
    # Rank row labels separately from full rows, where years and units
    # repeated across all columns can hide the requested financial concept.
    labels = {key: row["table"][int(key[6:])][0] if key.startswith("table_") else text
              for key, text in evidence.items()}
    content_rank = bm25_rank(full["question"], evidence, original)
    label_rank = bm25_rank(full["question"], labels, original)
    def fuse(*orders):
        ranks = [{key: position for position, key in enumerate(order, 1)} for order in orders]
        return sorted(evidence, key=lambda key: (-sum(1 / (60 + rank[key]) for rank in ranks),
                                                  original[key]))

    def pack(order, limit, budget):
        kept = {}
        for key in order:
            trial = {**kept, key: evidence[key]}
            if draft_evidence_tokens(tokenizer, trial) <= budget:
                kept = trial
                if len(kept) == limit:
                    break
        return kept

    variants = {
        "lexical8": base,
        "bm25_matched": pack(content_rank, 8, cap),
        "fusion_matched": pack(fuse(base_rank, content_rank, label_rank), 8, cap),
        "lexical16_bounded": pack(base_rank, 16, max(cap, min(cap * 2, 2300))),
    }
    if dense:
        dense_rank = dense.rank(full["question"], evidence)
        variants["bge_matched"] = pack(dense_rank, 8, cap)
        variants["bge_lexical_matched"] = pack(fuse(base_rank, dense_rank), 8, cap)
    return full, variants


def cluster_interval(rows, method):
    groups = defaultdict(list)
    for row in rows:
        groups[row["report"]].append(int(row[method]["covered"]) - int(row["lexical8"]["covered"]))
    totals = [(sum(values), len(values)) for values in groups.values()]
    rng = random.Random(42)
    estimates = []
    for _ in range(2000):
        sample = rng.choices(totals, k=len(totals))
        estimates.append(sum(change for change, _ in sample) / sum(n for _, n in sample))
    estimates.sort()
    return [estimates[50], estimates[1949]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "tokenizer", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--bge", type=Path)
    parser.add_argument("--cohort", type=Path,
                        help="Export evidence packets for these frozen IDs instead of scoring retrieval")
    parser.add_argument("--method", default="lexical16_bounded")
    args = parser.parse_args()
    tokenizer = Tokenizer.from_file(str(args.tokenizer))
    dense = DenseRanker(args.bge) if args.bge else None
    raw = args.source.read_bytes()
    items = json.loads(raw)
    if args.cohort:
        sources = {item["id"]: item for item in items}
        baselines = [json.loads(line) for line in args.cohort.read_text(encoding="utf-8").splitlines()]
        with args.output.open("x", encoding="utf-8") as out:
            for base in baselines:
                source = sources[base["id"]]
                if packet(source)["evidence"] != base["evidence"]:
                    raise ValueError(f"Frozen baseline evidence differs for {base['id']}")
                _, variants = ranked_packets(source, tokenizer, dense)
                evidence = variants[args.method]
                out.write(json.dumps({**base, "evidence": evidence, "retrieval": {
                    "method": args.method, "gold_used": False}}) + "\n")
        return
    rows = []
    for item in items:
        _, packets = ranked_packets(item, tokenizer, dense)
        gold = set(item["qa"]["gold_inds"])
        row = {"id": item["id"], "report": report_group(item["id"]), "annotated_units": len(gold)}
        for method, evidence in packets.items():
            try:
                binding_domains(item["qa"]["program"], atom_catalog(evidence))
                bindable = True
            except (ValueError, InvalidOperation):
                bindable = False
            row[method] = dict(covered=bool(gold) and gold <= evidence.keys(),
                               hits=len(gold & evidence.keys()),
                               bindable=bindable,
                               tokens=draft_evidence_tokens(tokenizer, evidence))
        rows.append(row)
        if len(rows) % 100 == 0:
            print(f"Scored {len(rows)} questions", flush=True)
    methods = {}
    for method in packets:
        methods[method] = dict(
            covered=sum(row[method]["covered"] for row in rows),
            hits=sum(row[method]["hits"] for row in rows),
            numerically_bindable=sum(row[method]["bindable"] for row in rows),
            median_tokens=median(row[method]["tokens"] for row in rows),
            coverage_gains=sum(row[method]["covered"] and not row["lexical8"]["covered"] for row in rows),
            coverage_losses=sum(row["lexical8"]["covered"] and not row[method]["covered"] for row in rows),
            delta_cluster_95=cluster_interval(rows, method))
    result = dict(source_sha256=hashlib.sha256(raw).hexdigest(),
                  tokenizer_sha256=hashlib.sha256(args.tokenizer.read_bytes()).hexdigest(),
                  questions=len(rows), reports=len({row["report"] for row in rows}),
                  annotated_units=sum(row["annotated_units"] for row in rows),
                  methods=methods, rows=rows)
    if args.bge:
        result["bge_sha256"] = hashlib.sha256((args.bge / "model.safetensors").read_bytes()).hexdigest()
    with args.output.open("x", encoding="utf-8") as out:
        json.dump(result, out, indent=2)
        out.write("\n")
    print(json.dumps(methods, indent=2))


if __name__ == "__main__":
    main()
