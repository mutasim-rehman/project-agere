"""Run and audit the sealed 16 GB comparison on native Windows."""
import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
from statistics import median
import subprocess
import sys
import time

import psutil

from lab_tiers_analyze import paired
from lab_tiers_common import append, completed_cases, inside, read, run_id, sha, ssd_root, verify, write
from windows_job_commit import CREATE_SUSPENDED, JobCommitLimit
from windows_memory_counters import MemoryCounters


ARCHIVE = "runs/lab_tiers_v1/lab-16-115gb-recovery-02"
ARCHIVE_SHA = "2bc2c447e1e2c09fde8883077105b74f52b847bbe80ad121b3b53303095c3ac8"
CAP = 11_500_000_000
HEADROOM = 500_000_000
METRICS = ("case_success", "raw_execution_match")
PROFILES = ("primary", "direct_control", "repair_ablation")


def utc():
    return datetime.now(timezone.utc).isoformat()


def records(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()] if path.exists() else []


def inputs(ssd):
    archive = inside(ssd, ARCHIVE)
    manifest = archive / "manifest.json"
    verify(manifest, ARCHIVE_SHA, {})
    frozen = read(manifest)
    spec = frozen["protocol"]
    if spec["tiers"]["16"]["nominal_cap_bytes"] != CAP or tuple(spec["profiles"]) != PROFILES:
        raise ValueError("Unexpected archived 16 GB protocol")
    for relative, digest in frozen["freeze"]["code_sha256"].items():
        verify(inside(archive / "code", relative), digest, {})
    data = spec["dataset"]
    for name in ("public", "gold", "demos"):
        verify(inside(ssd, data[name]), data[f"{name}_sha256"], {})
    for arm in ("sas", "mas"):
        for model in spec["tiers"]["16"][arm].values():
            path = inside(ssd, model["path"])
            if path.stat().st_size != model["size_bytes"]:
                raise ValueError(f"Unexpected model size: {path}")
            print(f"Verifying {path.name}", flush=True)
            verify(path, model["sha256"], {})
    packets = records(inside(ssd, data["public"]))
    if [p["id"] for p in packets] != data["ids"] or len(packets) != data["n"]:
        raise ValueError("Public packets do not match the frozen cohort")
    return spec


def runtime():
    import llama_cpp
    import numpy
    lib = Path(llama_cpp.__file__).parent / "lib"
    return dict(os=platform.platform(), python=sys.version, llama_cpp=llama_cpp.__version__,
                numpy=numpy.__version__, psutil=psutil.__version__,
                cpu_backend=llama_cpp.llama_print_system_info().decode(),
                physical_bytes=psutil.virtual_memory().total,
                dll_sha256={p.name: sha(p) for p in sorted(lib.glob("*.dll"))})


def pagefiles():
    result = subprocess.check_output(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
         "Get-CimInstance Win32_PageFileUsage -ErrorAction Stop | "
         "Select-Object Name,AllocatedBaseSize,CurrentUsage | ConvertTo-Json -Compress"],
        creationflags=subprocess.CREATE_NO_WINDOW, timeout=30,
    ).strip()
    return json.loads(result) if result else []


@contextmanager
def run_lock(folder):
    import msvcrt
    with (folder / "run.lock").open("a+b") as handle:
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise RuntimeError(f"Another launcher holds {folder / 'run.lock'}") from exc
        try:
            yield
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def config(spec, arm, profile):
    return {**spec["common"], **spec["profiles"][profile], "arm": arm,
            "models": spec["tiers"]["16"][arm]}


def use_archive(ssd):
    sys.path.insert(0, str(inside(ssd, ARCHIVE + "/code/scripts")))


def worker(ssd, attempt):
    # This subprocess is created suspended and assigned to the controller's job
    # before it can load any models.
    use_archive(ssd)
    from llama_cpp import Llama, LlamaGrammar
    from tier8_v2_financial_pipeline import evaluate_financial, run_financial
    from tier8_v2_natural_run import Models

    info = read(attempt / "attempt.json")
    spec = read(inside(ssd, ARCHIVE + "/manifest.json"))["protocol"]
    job = config(spec, info["arm"], info["profile"])
    data = spec["dataset"]
    packets = records(inside(ssd, data["public"]))
    gold = {r["id"]: r for r in read(inside(ssd, data["gold"]))}
    demos = read(inside(ssd, data["demos"]))["examples"][:job["demos"]]

    class ResidentModels(Models):
        def __init__(self):
            self.models = {}
            self.context, self.grammar = job["context"], LlamaGrammar

    models = ResidentModels()
    try:
        for role, model in job["models"].items():
            models.models[role] = Llama(
                model_path=str(inside(ssd, model["path"])), n_ctx=job["context"],
                n_gpu_layers=0, n_threads=job["threads"], n_threads_batch=job["threads"],
                n_batch=64, n_ubatch=64, seed=42, use_mmap=False, verbose=False,
            )
            print(f"Resident model loaded: {role}", flush=True)
        for index, p in enumerate(packets[info["start"]:], info["start"] + 1):
            row = run_financial(
                p, models, job["arm"], job["repair"], representation=job["program_mode"],
                unit_mode=job["unit_mode"], selector=job["selector"], causal_mode=job["causal_mode"],
                catalog_style=job["catalog_style"], demonstrations=demos,
                analysis_tokens=job["analysis_tokens"], planner=job["planner"],
                critic_protocol=job["critic_protocol"],
            )
            if row["tokens"] > job["output_token_cap"]:
                raise ValueError("Frozen token cap exceeded")
            annotation = gold[p["id"]]
            row["initial_score"] = evaluate_financial(annotation, row["initial_answer"], row["initial_execution"])
            row["score"] = evaluate_financial(annotation, row["answer"], row["execution"])
            append(attempt / "cases.jsonl", row)
            print(f"{info['arm']} / {info['profile']}: {index}/{len(packets)} {p['id']}", flush=True)
    finally:
        for model in models.models.values():
            model.close()


def retained(job_folder, ids):
    accepted = []
    for folder in sorted(job_folder.glob("attempt-*")):
        state_path = folder / "state.json"
        if not state_path.is_file():
            continue
        state = read(state_path)
        if state["status"] not in ("complete", "interrupted"):
            continue
        if (state["peak_working_set_bytes"] > CAP or state["peak_job_commit_bytes"] > CAP
                or state["lowest_host_available_bytes"] < HEADROOM
                or sha(folder / "memory.jsonl") != state["memory_sha256"]):
            raise ValueError(f"Resource evidence failed validation: {folder}")
        info = read(folder / "attempt.json")
        path = folder / "cases.jsonl"
        if info["start"] != len(accepted) or (sha(path) if path.exists() else None) != state["cases_sha256"]:
            raise ValueError(f"Saved case evidence changed: {folder}")
        attempt_rows = completed_cases(path, ids[len(accepted):])
        expected = ids[len(accepted):len(accepted) + len(attempt_rows)]
        if [r["case_id"] for r in attempt_rows] != expected:
            raise ValueError(f"Attempt is not an exact frozen prefix: {folder}")
        accepted.extend(attempt_rows)
    return accepted


def ensure_headroom():
    available = psutil.virtual_memory().available
    if available < CAP + HEADROOM:
        raise RuntimeError(f"{available / 1e9:.2f} GB RAM available; need {(CAP + HEADROOM) / 1e9:.2f} GB before model load. Close apps, then rerun the same command.")


def process_working_set(root):
    try:
        processes = [root, *root.children(recursive=True)]
    except psutil.NoSuchProcess:
        return 0
    total = 0
    for process in processes:
        try:
            total += process.memory_info().rss
        except psutil.NoSuchProcess:
            continue
    return total


def run_attempt(ssd, folder, arm, profile, start, expected):
    ensure_headroom()
    folder.mkdir(parents=True, exist_ok=True)
    index = len(list(folder.glob("attempt-*"))) + 1
    attempt = folder / f"attempt-{index:04d}"
    attempt.mkdir()
    write(attempt / "attempt.json", dict(arm=arm, profile=profile, start=start, expected=expected, started_utc=utc()))
    state = dict(status="failed", peak_working_set_bytes=0, peak_job_commit_bytes=0,
                 lowest_host_available_bytes=psutil.virtual_memory().available)
    controller = psutil.Process()
    memory_path, cases_path = attempt / "memory.jsonl", attempt / "cases.jsonl"
    process = None
    try:
        with (
            JobCommitLimit(CAP) as job,
            MemoryCounters() as counters,
            memory_path.open("x", encoding="utf-8") as trace,
            (attempt / "worker.log").open("xb") as errors,
        ):
            process = subprocess.Popen(
                [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "--ssd", str(ssd),
                 "--worker-attempt", str(attempt)],
                creationflags=CREATE_SUSPENDED | subprocess.CREATE_NO_WINDOW,
                stdout=errors, stderr=subprocess.STDOUT,
            )
            root = psutil.Process(process.pid)
            job.assign(process._handle)
            root.resume()
            next_rate = time.monotonic() + 1
            next_progress = time.monotonic() + 10
            completed = start
            while True:
                memory = psutil.virtual_memory()
                rss = controller.memory_info().rss + process_working_set(root)
                commit = job.peak_commit()
                sample = dict(timestamp=utc(), combined_working_set_bytes=rss,
                              peak_job_commit_bytes=commit, host_available_bytes=memory.available)
                if time.monotonic() >= next_rate:
                    sample.update(counters.sample())
                    next_rate = time.monotonic() + 1
                trace.write(json.dumps(sample) + "\n")
                trace.flush()
                state["peak_working_set_bytes"] = max(rss, state["peak_working_set_bytes"])
                state["peak_job_commit_bytes"] = max(commit, state["peak_job_commit_bytes"])
                state["lowest_host_available_bytes"] = min(memory.available, state["lowest_host_available_bytes"])
                if rss > CAP or commit > CAP or memory.available < HEADROOM:
                    raise RuntimeError("Resource guard stopped the job; see memory.jsonl")
                if time.monotonic() >= next_progress:
                    count = start + (cases_path.read_bytes().count(b"\n") if cases_path.exists() else 0)
                    if count != completed:
                        print(f"{arm} / {profile}: {count}/{expected} saved", flush=True)
                        completed = count
                    next_progress = time.monotonic() + 10
                if process.poll() is not None:
                    break
                time.sleep(0.2)
            if process.returncode != 0 or len(records(cases_path)) != expected - start:
                raise RuntimeError(f"Worker exited {process.returncode} or returned incomplete cases; see {attempt}")
        state["status"] = "complete"
    except KeyboardInterrupt:
        state["status"] = "interrupted"
        raise
    except Exception as exc:
        state["error"] = str(exc)
        raise
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=20)
        if state["status"] == "interrupted":
            ids = read(inside(ssd, ARCHIVE + "/manifest.json"))["protocol"]["dataset"]["ids"]
            try:
                completed_cases(cases_path, ids[start:], repair_tail=True)
            except ValueError as exc:
                state.update(status="failed", error=str(exc))
        state.update(finished_utc=utc(), memory_sha256=sha(memory_path) if memory_path.exists() else None,
                     cases_sha256=sha(cases_path) if cases_path.exists() else None)
        write(attempt / "state.json", state)


def outcome(row, metric):
    if not row["delivered"]:
        return "withheld"
    return "correct_delivered" if row["score"][metric] else "wrong_delivered"


def analyze(ssd, folder, spec, jobs):
    use_archive(ssd)
    from llama_cpp import Llama
    from completion_tokenization import completion_tokens
    from financial_trace_replay import replay
    from tier8_v2_natural_run import Models

    data = spec["dataset"]
    packets = records(inside(ssd, data["public"]))
    gold = {r["id"]: r for r in read(inside(ssd, data["gold"]))}
    demos = read(inside(ssd, data["demos"]))["examples"]
    groups = {p["id"]: p["id"].rsplit("/", 1)[0] for p in packets}
    report = dict(status="complete_accuracy_audited", tier=16, windows_paging_status="unverified",
                  questions=len(packets), reports=len(set(groups.values())), jobs={}, comparisons={})
    for (arm, profile), rows in jobs.items():
        job = config(spec, arm, profile)
        name = f"{arm}-{profile}"
        tokenizers = {}
        print(f"Replaying {name}", flush=True)
        try:
            for role, model in job["models"].items():
                tokenizers[role] = Llama(model_path=str(inside(ssd, model["path"])), vocab_only=True,
                                        n_gpu_layers=0, n_threads=1, use_mmap=True, verbose=False)

            def count(role, content, structured):
                return len(completion_tokens(tokenizers[role], Models.prompt(content, structured)))

            for packet, row in zip(packets, rows):
                replay(packet, gold[packet["id"]], row, job, count, demos[:job["demos"]])
        finally:
            for model in tokenizers.values():
                model.close()
        ledger = folder / name / "cases.jsonl"
        ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        attempts = [read(p) for p in sorted((folder / name).glob("attempt-*/state.json"))]
        report["jobs"][name] = dict(
            outcomes={metric: Counter(outcome(r, metric) for r in rows) for metric in METRICS},
            correct_initial_candidates={metric: sum(r["initial_score"][metric] for r in rows) for metric in METRICS},
            executable_initial_candidates=sum(not r["initial_execution"]["issues"] for r in rows),
            generated_tokens=sum(r["tokens"] for r in rows),
            median_case_inference_seconds=median(sum(s["seconds"] for s in r["stages"]) for r in rows),
            cases_sha256=sha(ledger), attempts=attempts,
        )
    for profile in PROFILES:
        left, right = ({r["case_id"]: r for r in jobs[arm, profile]} for arm in ("sas", "mas"))
        report["comparisons"][profile] = {}
        for metric in METRICS:
            result = paired(left, right, groups, metric)
            result["case_transitions"] = Counter(
                outcome(left[k], metric) + " -> " + outcome(right[k], metric) for k in left)
            report["comparisons"][profile][metric] = result
    attempt_dirs = list(folder.glob("*/attempt-*"))
    report["uninterrupted_all_jobs"] = (len(attempt_dirs) == len(jobs) and all(
        (a / "state.json").is_file() and read(a / "state.json")["status"] == "complete" for a in attempt_dirs))
    report["pagefiles_at_end"] = pagefiles()
    write(folder / "summary.json", report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ssd", required=True)
    parser.add_argument("--run-id", default="windows16-replication-v1")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--worker-attempt", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error("This runner requires native Windows")
    ssd = ssd_root(args.ssd)
    if args.worker_attempt:
        worker(ssd, args.worker_attempt)
        return
    spec = inputs(ssd)
    info = runtime()
    with MemoryCounters() as counters:
        time.sleep(1)
        rates = counters.sample()
    host = dict(available_bytes=psutil.virtual_memory().available, pagefiles=pagefiles(), rates=rates)
    if args.preflight_only:
        print(json.dumps(dict(input_checks="passed", runtime=info, host=host,
                              ready_to_load=host["available_bytes"] >= CAP + HEADROOM), indent=2))
        return
    folder = inside(ssd, f"runs/windows_tier16/{run_id(args.run_id)}")
    folder.mkdir(parents=True, exist_ok=True)
    with run_lock(folder.parent):
        manifest = dict(archive_manifest_sha256=ARCHIVE_SHA, runner_sha256=sha(Path(__file__)),
                        monitor_sha256=sha(Path(__file__).with_name("windows_memory_counters.py")),
                        job_guard_sha256=sha(Path(__file__).with_name("windows_job_commit.py")),
                        paired_analysis_sha256=sha(Path(__file__).with_name("lab_tiers_analyze.py")),
                        runtime=info, working_set_ceiling_bytes=CAP, job_commit_limit_bytes=CAP,
                        host_available_floor_bytes=HEADROOM)
        path = folder / "manifest.json"
        if path.exists():
            if read(path)["frozen"] != manifest:
                raise ValueError("Runtime or code changed; use a new run ID")
        else:
            write(path, dict(frozen=manifest, host_at_start=host, started_utc=utc(), protocol=spec))
        ids = spec["dataset"]["ids"]
        jobs = {}
        for profile in PROFILES:
            for arm in ("sas", "mas"):
                job_folder = folder / f"{arm}-{profile}"
                done = retained(job_folder, ids)
                if len(done) < len(ids):
                    print(f"Starting {arm} / {profile} at {len(done)}/{len(ids)}", flush=True)
                    run_attempt(ssd, job_folder, arm, profile, len(done), len(ids))
                jobs[arm, profile] = retained(job_folder, ids)
                if len(jobs[arm, profile]) != len(ids):
                    raise ValueError("Cannot analyze an incomplete job")
        analyze(ssd, folder, spec, jobs)
    print(f"Complete: {folder / 'summary.json'}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Repeat the same command to resume.", file=sys.stderr)
        raise SystemExit(130)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Stopped: {exc}", file=sys.stderr)
        raise SystemExit(1)
