"""Prospective paired repair pilot after a verified serial baseline sequence."""
import argparse
import json
import subprocess
import sys
import time

import psutil

from tier8_v2_sequence import check_inputs, inside, require_complete
from tier8_v2_replay import validate_base


def select_baseline(candidates):
    return min(candidates, key=lambda name: (-candidates[name]["case_successes"],
        -candidates[name]["delivered_correct"], candidates[name]["delivered_incorrect"],
        candidates[name]["total_generated_tokens"], name))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--journal", required=True)
    args = parser.parse_args()
    plan = json.loads(inside(args.plan).read_text())
    journal = inside(args.journal)
    if journal.exists():
        raise ValueError("Use a new pilot journal; no silent retries")
    def record(state, **fields):
        with journal.open("a") as stream:
            stream.write(json.dumps({"time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "state": state, **fields}) + "\n")
    try:
        check_inputs(plan)
        dependency = plan["dependency"]
        try:
            process = psutil.Process(dependency["pid"])
        except psutil.NoSuchProcess:
            process = None
        if process:
            if process.create_time() != dependency["create_time"] or dependency["command_argument"] not in process.cmdline():
                raise ValueError("Dependency process identity changed")
            record("waiting", dependency=dependency, verified_live=True)
            while True:
                try:
                    process.wait(timeout=10)
                    break
                except psutil.TimeoutExpired:
                    pass
        events = [json.loads(line) for line in inside(plan["dependency_journal"]).read_text().splitlines()]
        if not events or events[-1]["state"] != "complete":
            raise ValueError("Baseline sequence did not finish successfully")
        candidates, identities, references = {}, [], []
        for name in plan["candidate_baselines"]:
            manifest, summary, snapshots = validate_base(inside(name))
            candidates[name] = summary
            identities.append({r["case_id"] for r in snapshots})
            references.append(manifest["evaluation_source_sha256"])
        if any(ids != identities[0] for ids in identities) or len(set(references)) != 1:
            raise ValueError("Candidate baselines do not share evaluation cases/source")
        selected = select_baseline(candidates)
        record("baseline_selected", selected=selected, summaries=candidates, rule=plan["selection_rule"])
        for job in plan["jobs"]:
            check_inputs(plan)
            if inside(job["out"]).exists() or inside(job["log"]).exists():
                raise ValueError("Pilot output or log already exists")
            command = [sys.executable, "-u", str(inside("scripts/tier8_v2_replay.py")),
                       "--base", selected, "--out", job["out"], "--feedback", job["feedback"]]
            record("starting", command=command, feedback=job["feedback"])
            with inside(job["log"]).open("x") as log:
                result = subprocess.run(command, cwd=inside("."), stdout=log, stderr=log)
            if result.returncode != 0:
                raise ValueError("Repair component failed; no automatic retry")
            summary = require_complete(job["out"])
            record("experiment_complete", feedback=job["feedback"], summary=summary)
        record("complete")
    except Exception as exc:
        record("failed", error=type(exc).__name__, detail=str(exc))
        raise


if __name__ == "__main__":
    main()
