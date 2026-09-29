"""Generate versioned synthetic Agere corpora and an SFT mixture on the SSD.

All generator code and manifests stay in the repository. The output contains
only synthetic dataset files and is written beneath AGERE_SSD_ROOT/datasets.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import random
from pathlib import Path
from typing import Any


VERSION = "agere-synth-v1"
SEED = 20260929
SPLITS = {"train": (400, 200), "dev": (100, 50), "test": (100, 75)}
FIRST = ["Amina", "Bilal", "Dania", "Ehsan", "Farah", "Haris", "Iqra", "Jamal", "Kiran", "Laila"]
LAST = ["Saffron", "Juniper", "Quartz", "Cedar", "Orbit", "Maple", "Indigo", "Harbor", "Willow", "Cobalt"]
BUSINESSES = ["Blue Orchard Traders", "Kite Harbor Textiles", "Copper Lantern Foods", "Paper Bridge Components", "Quiet River Logistics", "Cedar Loop Packaging"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def case_seed(split: str, index: int, kind: str) -> int:
    key = f"{VERSION}|{SEED}|{split}|{kind}|{index}".encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big")


def make_kyc(split: str, index: int) -> dict[str, Any]:
    rng = random.Random(case_seed(split, index, "kyc"))
    case_id = f"KYC-{split.upper()}-{index + 1:04d}"
    name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    mismatch = index % 5 == 0
    declared_name = f"{rng.choice(FIRST)} {rng.choice(LAST)}" if mismatch else name
    company = rng.choice(BUSINESSES)
    owners = [rng.randint(15, 65), 0]
    owners[1] = 100 - owners[0]
    cnic = f"99999-{(index + 1):07d}-{(index % 9) + 1}"
    atl_status = "ACTIVE" if index % 4 else "NOT_FOUND"
    watch_status = "POTENTIAL_MATCH" if index % 11 == 0 else "NO_MATCH"
    expiry = None if index % 3 == 0 else f"202{7 + index % 3}-12-31"
    lines = [
        f"L01 Customer identity record: name={name}; synthetic_id={cnic}; expiry={expiry or 'NOT_PROVIDED'}.",
        f"L02 Tax record: synthetic_tax_ref=SYN-TAX-{index + 1:05d}; ATL_status={atl_status}.",
        f"L03 Registry filing: entity={company}; beneficial_owner_1={name} ({owners[0]}%); beneficial_owner_2={rng.choice(FIRST)} {rng.choice(LAST)} ({owners[1]}%).",
        f"L04 Screening result: status={watch_status}; synthetic_record_id=SAN-SYNTH-{index + 1:05d}.",
        f"L05 Onboarding declaration: applicant_name={declared_name}; declared_UBO_total=100%.",
    ]
    return {
        "id": case_id,
        "corpus": "Agere-KYC-Synth",
        "split": split,
        "generation_version": VERSION,
        "synthetic_only": True,
        "case_documents": [{"id": f"{case_id}-DOC", "kind": "synthetic_onboarding_pack", "lines": lines}],
        "labels": {
            "identity_name_mismatch": mismatch,
            "registry_name": name,
            "declared_name": declared_name,
            "atl_status": atl_status,
            "screening_status": watch_status,
            "missing_fields": ["identity_expiry_date"] if expiry is None else [],
            "required_behavior_for_missing": "MISSING",
            "source_spans": {"registry_name": f"{case_id}-DOC#L03", "declared_name": f"{case_id}-DOC#L05"},
        },
    }


def make_credit(split: str, index: int) -> dict[str, Any]:
    rng = random.Random(case_seed(split, index, "credit"))
    case_id = f"CR-{split.upper()}-{index + 1:04d}"
    business = rng.choice(BUSINESSES)
    turnover = rng.randrange(45, 950) * 1_000_000
    gross_profit = turnover * rng.randrange(12, 41) // 100
    operating_profit = gross_profit * rng.randrange(30, 71) // 100
    annual_debt_service = rng.randrange(12, 95) * 1_000_000
    dscr = round(operating_profit / annual_debt_service, 4)
    current_assets = rng.randrange(25, 260) * 1_000_000
    current_liabilities = rng.randrange(18, 180) * 1_000_000
    current_ratio = round(current_assets / current_liabilities, 4)
    e_cib_status = "NO_ADVERSE_LINE" if index % 6 else "ADVERSE_LINE_REVIEW_REQUIRED"
    missing_review_date = index % 3 == 0
    lines = [
        f"L01 Borrower application: entity={business}; requested_finance_pkr={rng.randrange(10, 90) * 1_000_000}.",
        f"L02 Audited income statement: annual_turnover_pkr={turnover}; gross_profit_pkr={gross_profit}; operating_profit_pkr={operating_profit}.",
        f"L03 Cashflow schedule: annual_debt_service_pkr={annual_debt_service}; current_assets_pkr={current_assets}; current_liabilities_pkr={current_liabilities}.",
        f"L04 e-CIB summary: status={e_cib_status}; last_review_date={'NOT_PROVIDED' if missing_review_date else '2026-06-30'}.",
    ]
    return {
        "id": case_id,
        "corpus": "Agere-Credit-Synth",
        "split": split,
        "generation_version": VERSION,
        "synthetic_only": True,
        "case_documents": [{"id": f"{case_id}-DOC", "kind": "synthetic_sme_credit_pack", "lines": lines}],
        "calculator_inputs": {
            "operating_profit_pkr": operating_profit,
            "annual_debt_service_pkr": annual_debt_service,
            "current_assets_pkr": current_assets,
            "current_liabilities_pkr": current_liabilities,
        },
        "labels": {
            "dscr": dscr,
            "current_ratio": current_ratio,
            "e_cib_status": e_cib_status,
            "missing_fields": ["e_cib_last_review_date"] if missing_review_date else [],
            "required_behavior_for_missing": "MISSING",
            "source_spans": {"operating_profit": f"{case_id}-DOC#L03", "e_cib_status": f"{case_id}-DOC#L04"},
        },
    }


def source_text(case: dict[str, Any]) -> str:
    doc = case["case_documents"][0]
    return "\n".join(doc["lines"])


def make_sft(case: dict[str, Any], task: str) -> dict[str, Any]:
    labels = case["labels"]
    doc = case["case_documents"][0]
    if task == "missing_data":
        if labels["missing_fields"]:
            field = labels["missing_fields"][0]
        else:
            field = "date_of_birth" if case["corpus"] == "Agere-KYC-Synth" else "guarantor_reference"
        prompt = f"Read this synthetic case and report {field}. If the source omits it, return status MISSING.\n{source_text(case)}"
        target = {"field": field, "status": "MISSING", "value": None, "source_span": None}
    elif task == "tool_calls":
        if case["corpus"] == "Agere-Credit-Synth":
            prompt = f"Calculate DSCR for case {case['id']} using the financial_calculator. Do not calculate in prose."
            target = {"tool": "financial_calculator", "arguments": {"metric": "dscr", "numerator": case["calculator_inputs"]["operating_profit_pkr"], "denominator": case["calculator_inputs"]["annual_debt_service_pkr"]}}
        else:
            prompt = f"Extract and classify the stated screening result for case {case['id']} with document_extractor."
            target = {"tool": "document_extractor", "arguments": {"case_id": case["id"], "field": "screening_status", "source_span": f"{doc['id']}#L04"}}
    else:
        if case["corpus"] == "Agere-KYC-Synth":
            fact = labels["declared_name"]
            line_id = labels["source_spans"]["declared_name"]
            quote = doc["lines"][4]
            predicate = "The applicant name declared at onboarding is recorded in the source."
        else:
            fact = labels["e_cib_status"]
            line_id = labels["source_spans"]["e_cib_status"]
            quote = doc["lines"][3]
            predicate = f"The e-CIB status is {fact}."
        prompt = f"Write one factual sentence about this case and cite the exact source span.\n{source_text(case)}"
        target = {"text": predicate, "citations": [{"document_id": doc["id"], "span_id": line_id, "quote": quote}]}
    return {"id": f"SFT-{task}-{case['id']}", "task": task, "messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": json.dumps(target, ensure_ascii=False, sort_keys=True)}], "source_case_id": case["id"], "synthetic_only": True}


def main() -> None:
    ssd_root_raw = os.environ.get("AGERE_SSD_ROOT")
    if not ssd_root_raw:
        raise SystemExit("Set AGERE_SSD_ROOT to the mounted external SSD before dataset generation.")
    ssd_root = Path(ssd_root_raw).expanduser().resolve()
    if not ssd_root.is_dir():
        raise SystemExit(f"AGERE_SSD_ROOT is not a mounted directory: {ssd_root}")
    repo_root = Path(__file__).resolve().parents[1]
    if ssd_root == repo_root or ssd_root.drive.casefold() == repo_root.drive.casefold():
        raise SystemExit("AGERE_SSD_ROOT must resolve to the external data drive, separate from the repository drive.")
    if not (ssd_root / "weights" / "hf").is_dir():
        raise SystemExit(f"AGERE_SSD_ROOT is missing the expected Phase 1 weights/hf directory: {ssd_root}")
    dataset_root = ssd_root / "datasets"
    synth_root = dataset_root / "agere_synthetic" / VERSION
    synth_root.mkdir(parents=True, exist_ok=True)

    cases: dict[str, list[dict[str, Any]]] = {"train": [], "dev": [], "test": []}
    outputs: list[dict[str, Any]] = []
    for split, (kyc_n, credit_n) in SPLITS.items():
        kyc = [make_kyc(split, i) for i in range(kyc_n)]
        credit = [make_credit(split, i) for i in range(credit_n)]
        cases[split] = kyc + credit
        kyc_path = synth_root / split / "kyc.jsonl"
        credit_path = synth_root / split / "credit.jsonl"
        write_jsonl(kyc_path, kyc)
        write_jsonl(credit_path, credit)
        outputs.extend([{"path": kyc_path, "name": f"Agere-KYC-Synth/{split}", "rows": len(kyc)}, {"path": credit_path, "name": f"Agere-Credit-Synth/{split}", "rows": len(credit)}])

    tasks = ["missing_data"] * 240 + ["tool_calls"] * 180 + ["citations"] * 180
    train_cases = list(cases["train"])
    random.Random(SEED + 1).shuffle(train_cases)
    train_sft = [make_sft(train_cases[i], task) for i, task in enumerate(tasks)]
    dev_tasks = ["missing_data"] * 24 + ["tool_calls"] * 18 + ["citations"] * 18
    dev_cases = list(cases["dev"])
    random.Random(SEED + 2).shuffle(dev_cases)
    dev_sft = [make_sft(dev_cases[i], task) for i, task in enumerate(dev_tasks)]
    train_path = synth_root / "finetune" / "train.jsonl"
    dev_path = synth_root / "finetune" / "dev.jsonl"
    write_jsonl(train_path, train_sft)
    write_jsonl(dev_path, dev_sft)
    outputs.extend([{"path": train_path, "name": "Agere-SFT/train", "rows": len(train_sft)}, {"path": dev_path, "name": "Agere-SFT/dev", "rows": len(dev_sft)}])

    # Derive a deterministic 100-question FRAMES control slice, then freeze it.
    frames_source = dataset_root / "external" / "FRAMES" / "58d9fb6330f3ab1316d1eca12e5e8ef23dcc22ef" / "test.tsv"
    frames_rows: list[dict[str, str]] = []
    with frames_source.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            prompt = row.get("Prompt", "").strip()
            if prompt:
                stable_id = row.get("", "")
                rank = hashlib.sha256(f"{SEED}|{stable_id}|{prompt}".encode()).hexdigest()
                frames_rows.append({"_rank": rank, "id": f"FRAMES-{int(stable_id):04d}", "question": prompt, "answer": row.get("Answer", "").strip(), "reasoning_types": row.get("reasoning_types", "").strip(), "evidence_links": row.get("wiki_links", "").strip(), "source_dataset": "google/frames-benchmark", "source_revision": "58d9fb6330f3ab1316d1eca12e5e8ef23dcc22ef"})
    frames_rows = sorted(frames_rows, key=lambda row: row["_rank"])[:100]
    if len(frames_rows) != 100:
        raise SystemExit(f"Expected at least 100 FRAMES questions; found {len(frames_rows)}")
    for row in frames_rows:
        row.pop("_rank")
    frames_slice = dataset_root / "external" / "FRAMES" / "58d9fb6330f3ab1316d1eca12e5e8ef23dcc22ef" / "frames_100.jsonl"
    write_jsonl(frames_slice, frames_rows)

    # Freeze only the explicitly held-out inputs, never training or dev files.
    test_files = [synth_root / "test" / "kyc.jsonl", synth_root / "test" / "credit.jsonl"]
    test_lines = [f"{sha256(path)}  {path.relative_to(ssd_root).as_posix()}" for path in test_files]
    test_lines.append(f"{sha256(frames_slice)}  {frames_slice.relative_to(ssd_root).as_posix()}")
    mortar_root = dataset_root / "external" / "MortarBench" / "ab3421d6b1a9f0cedbb9f98d34a4e1eb4473532f" / "data"
    test_lines.extend(f"{sha256(path)}  {path.relative_to(ssd_root).as_posix()}" for path in sorted(mortar_root.glob("*.jsonl")))
    manifest_path = repo_root / "manifests" / "test.sha256"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("\n".join(sorted(test_lines)) + "\n", encoding="utf-8")

    metadata = {
        "generator": VERSION,
        "seed": SEED,
        "ssd_subdir": "datasets/agere_synthetic/agere-synth-v1/",
        "train_mix": {"missing_data": 240, "tool_calls": 180, "citations": 180},
        "dev_mix": {"missing_data": 24, "tool_calls": 18, "citations": 18},
        "evaluation_slices": [{"dataset": "FRAMES", "path": frames_slice.relative_to(ssd_root).as_posix(), "rows": len(frames_rows), "sha256": sha256(frames_slice)}],
        "files": [{"path": row["path"].relative_to(ssd_root).as_posix(), "rows": row["rows"], "sha256": sha256(row["path"]), "dataset": row["name"]} for row in outputs],
        "note": "Synthetic starter corpus; validate content, labels, diversity, and coverage before using it for scientific claims or training. Test files are frozen in manifests/test.sha256.",
    }
    metadata_path = repo_root / "manifests" / "synthetic_datasets.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"SSD root: {ssd_root}")
    print(f"Generated 925 cases; train SFT={len(train_sft)} (40/30/30), dev SFT={len(dev_sft)}")
    print(f"Created and froze the FRAMES 100-question control slice.")
    print(f"Frozen held-out file hashes in repository: {manifest_path}")
    print(f"Repository data manifest: {metadata_path}")


if __name__ == "__main__":
    main()
