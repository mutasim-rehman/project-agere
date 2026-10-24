"""Run a frozen development sequence after an identified live pilot exits.

No retries, restarts, concurrent inference or shell commands. Completed valid
summaries authorize the next experiment; a missing/failed result stops the queue.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import psutil

ROOT = Path(__file__).resolve().parents[1]


def inside(name):
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Sequence paths must remain in the repository")
    return path


def require_complete(directory):
    summary = json.loads((inside(directory) / "summary.json").read_text())
    if (summary["status"] != "complete" or summary["exit_code"] != 0
            or summary["n"] != summary["expected"]
            or summary["peak_tree_rss_bytes"] > summary["cap_bytes"]):
        raise ValueError("Dependency experiment did not finish validly")
    return summary


def check_inputs(plan):
    for name, expected in plan["input_sha256"].items():
        if hashlib.sha256(inside(name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Frozen input changed: {name}")


def active_workers():
    active = []
    for process in psutil.process_iter(["pid", "cmdline"]):
        args = process.info["cmdline"] or []
        if any(Path(arg).name == "tier8_v2_run.py" for arg in args):
            active.append(process.pid)
    return active


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--journal", required=True)
    args = parser.parse_args()
    plan = json.loads(inside(args.plan).read_text())
    journal = inside(args.journal)
    if journal.exists():
        raise ValueError("Use a new journal; never silently rerun a sequence")
    def record(state, **fields):
        with journal.open("a") as stream:
            stream.write(json.dumps({"time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                     "state": state, **fields}) + "\n")
            stream.flush()
    try:
        check_inputs(plan)
        dependency = plan["dependency"]
        try:
            process = psutil.Process(dependency["pid"])
        except psutil.NoSuchProcess:
            process = None
        if process:
            if process.create_time() != dependency["create_time"] or dependency["run"] not in process.cmdline() or "--worker" in process.cmdline():
                raise ValueError("Dependency PID does not identify the expected monitor")
            record("waiting", dependency=dependency, verified_live=True)
            while True:
                try:
                    process.wait(timeout=10)
                    break
                except psutil.TimeoutExpired:
                    pass
        require_complete(dependency["run"])
        record("dependency_complete")
        for job in plan["jobs"]:
            check_inputs(plan)
            if active_workers():
                raise ValueError("Another tier8 inference process is still active")
            runner_args = job["args"]
            out = runner_args[runner_args.index("--out") + 1]
            if inside(out).exists() or inside(job["log"]).exists():
                raise ValueError("Queued output or log already exists; refusing to overwrite")
            command = [sys.executable, "-u", str(ROOT / "scripts/tier8_v2_run.py"), *runner_args]
            record("starting", out=out, command=command)
            with inside(job["log"]).open("x") as log:
                result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=log)
            if result.returncode != 0:
                raise ValueError(f"Queued experiment exited {result.returncode}: {out}")
            summary = require_complete(out)
            record("experiment_complete", out=out, summary=summary)
        record("complete")
    except Exception as exc:
        record("failed", error=type(exc).__name__, detail=str(exc))
        raise


if __name__ == "__main__":
    main()
