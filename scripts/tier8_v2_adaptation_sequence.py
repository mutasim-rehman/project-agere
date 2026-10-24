"""Run frozen fit -> training -> conversion after the identified CPU study exits.

No retries or implicit resumes. A failed fit prevents full training. Conversion
remains separate from applied-adapter inference and scientific task evaluation.
"""
import argparse
import json
import subprocess
import time

import psutil

from tier8_v2_adapter_convert import sha, validate_adapter
from tier8_v2_sequence import inside, check_inputs, require_complete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--journal", required=True)
    args = parser.parse_args()
    plan = json.loads(inside(args.plan).read_text())
    journal = inside(args.journal)
    if journal.exists():
        raise ValueError("Existing journal; do not restart a training sequence")
    if [job["kind"] for job in plan["jobs"]] != ["fit", "train", "convert"]:
        raise ValueError("Require fit, train, convert in that order")
    def record(state, **fields):
        with journal.open("a") as stream:
            stream.write(json.dumps({"state": state, "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **fields}) + "\n")
            stream.flush()
    try:
        check_inputs(plan)
        dependency = plan["dependency"]
        try:
            process = psutil.Process(dependency["pid"])
        except psutil.NoSuchProcess:
            process = None
        if process:
            if process.create_time() != dependency["create_time"] or dependency["command_arg"] not in process.cmdline():
                raise ValueError("Dependency PID identity differs")
            record("waiting", dependency=dependency, verified_live=True)
            while True:
                try:
                    process.wait(timeout=10)
                    break
                except psutil.TimeoutExpired:
                    pass
        require_complete(dependency["run"])
        dependency_journal = inside(dependency["journal"])
        if json.loads(dependency_journal.read_text().splitlines()[-1])["state"] != "complete":
            raise ValueError("CPU sequence did not complete")
        record("dependency_complete", journal_sha256=sha(dependency_journal))
        root = inside(".")
        python = root / ".venv-training/bin/python"
        inside(str(python))  # Validate symlink destination without losing venv invocation.
        probe = "import importlib.metadata as m,json,sys; print(json.dumps({k:m.version(k) for k in json.loads(sys.argv[1])}))"
        observed = json.loads(subprocess.check_output([str(python), "-c", probe,
            json.dumps(list(plan["runtime_versions"]))], cwd=root, text=True))
        if observed != plan["runtime_versions"]:
            raise ValueError("Training package versions changed")
        record("runtime_verified", versions=observed)
        previous = None
        for job in plan["jobs"]:
            check_inputs(plan)
            out, log = inside(job["out"]), inside(job["log"])
            if out.exists() or log.exists():
                raise ValueError("Existing job output/log; refusing duplicate updates")
            if job["kind"] == "convert":
                command = [str(python), "-u", str(inside("scripts/tier8_v2_adapter_convert.py")),
                           "--run", previous, "--out", str(out)]
            else:
                command = [str(python), "-u", str(inside("scripts/tier8_v2_adapt.py")),
                           "--profile", plan["profile"], "--mode", job["kind"], "--out", str(out)]
            record("starting", kind=job["kind"], out=str(out.relative_to(root)), command=command)
            with log.open("x") as stream:
                subprocess.run(command, cwd=root, stdout=stream, stderr=stream, check=True)
            if job["kind"] == "convert":
                result = json.loads((out / "manifest.json").read_text())
                if result["status"] != "complete" or result["diagnostic_only"] or sha(inside(result["file"])) != result["sha256"]:
                    raise ValueError("Invalid converted training adapter")
            else:
                manifest, result, _ = validate_adapter(out)
                if result["mode"] != job["kind"] or manifest["profile"] != plan["profile"]:
                    raise ValueError("Training result differs from planned condition")
                previous = str(out)
            record("job_complete", kind=job["kind"], summary=result)
        record("complete", adapter_applied=False, measured_reasoning_gain=False)
    except Exception as exc:
        record("failed", error=type(exc).__name__, reason=str(exc))
        raise


if __name__ == "__main__":
    main()
