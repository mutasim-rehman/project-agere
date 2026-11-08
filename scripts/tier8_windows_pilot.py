"""Paired FinQA pilot with native Windows CPU inference and sequential roles."""
import argparse
from contextlib import nullcontext
import json
from pathlib import Path
import re
import subprocess
import time

import psutil

from tier8_v2_financial_pipeline import evaluate_financial, run_financial
from windows_job_commit import CREATE_SUSPENDED, JobCommitLimit


ROOT = Path(__file__).resolve().parents[1]
CAP = 6_400_000_000
WEIGHTS = {"drafter": "qwen2.5-3b-instruct-q4_k_m.gguf",
           "verifier": "qwen2.5-0.5b-instruct-native-f16.gguf"}


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class Models:
    def __init__(self, args):
        self.args = args
        self.forced = False
        self.calls = 0
        self.adapter = None
        self.drafter_weights = None

    def call(self, role, content, schema, budget, limit, stage):
        if stage == "program":
            # The Windows CLI accepts fixed-length tuples via prefixItems but
            # rejects boolean items. The explicit bounds still close the tuple.
            for length in schema["oneOf"][0]["properties"]["steps"]["oneOf"]:
                length.pop("items")
        if stage == "program" and self.forced:
            schema = schema["oneOf"][0]
            content = content.replace("ANSWER or INSUFFICIENT", "ANSWER").replace(
                "If necessary evidence is missing, use INSUFFICIENT and empty steps.",
                "Attempt the best supported program using the available evidence.")
            if self.args.one_step:
                steps = schema["properties"]["steps"]
                schema["properties"]["steps"] = steps["oneOf"][0]
                content += "\nUse exactly one arithmetic operation."
        self.calls += 1
        prefix = self.args.output / f"call-{self.calls:03}"
        prompt = prefix.with_suffix(".prompt")
        grammar = prefix.with_suffix(".json")
        # Use Qwen's ChatML delimiters and disable the CLI's own chat templating.
        prompt.write_text(f"<|im_start|>user\n{content}<|im_end|>\n<|im_start|>assistant\n",
                          encoding="utf-8")
        grammar.write_text(json.dumps(schema), encoding="utf-8")
        allowance = budget.allowance(limit)
        budget.charge(allowance)  # Conservative reservation; exact use is in the CLI log.
        weights = self.drafter_weights if role == "drafter" and self.drafter_weights else WEIGHTS[role]
        cmd = [str(self.args.cli.resolve()), "-m", str((self.args.weights / weights).resolve()),
               "-f", str(prompt), "-jf", str(grammar), "-c", "4096", "-t", "8", "-ngl", "0",
               "--load-mode", "none", "--no-conversation", "--no-display-prompt",
               "--temp", "0", "--seed", "42", "-n", str(allowance)]
        if self.adapter is not None and stage in ("program", "trained_critic"):
            cmd.extend(("--lora", str(self.adapter.resolve())))
        started = time.monotonic()
        peak = 0
        commit_cap = getattr(self.args, "job_commit_limit", None)
        job_context = JobCommitLimit(commit_cap) if commit_cap else nullcontext()
        flags = subprocess.CREATE_NO_WINDOW | (CREATE_SUSPENDED if commit_cap else 0)
        with (prefix.with_suffix(".out").open("wb") as out,
              prefix.with_suffix(".log").open("wb") as log, job_context as job):
            worker = subprocess.Popen(cmd, stdout=out, stderr=log, creationflags=flags)
            try:
                process = psutil.Process(worker.pid)
                if job:
                    job.assign(worker._handle)
                    process.resume()
                while worker.poll() is None:
                    rss = process.memory_info().rss + psutil.Process().memory_info().rss
                    peak = max(rss, peak)
                    if peak > CAP or time.monotonic() - started > 300:
                        raise RuntimeError(f"Runtime limit exceeded at {prefix}")
                    time.sleep(0.2)
            except psutil.NoSuchProcess:
                pass
            finally:
                if worker.poll() is None:
                    worker.terminate()
                worker.wait()
            commit_peak = job.peak_commit() if job else None
        if worker.returncode:
            raise RuntimeError(f"Inference exited {worker.returncode}; see {prefix}.log")
        raw = prefix.with_suffix(".out").read_text(encoding="utf-8", errors="replace").strip()
        runtime_log = prefix.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
        prompt_perf = re.search(r"prompt eval time =\s*([\d.]+) ms\s*/\s*(\d+) tokens", runtime_log)
        decode_perf = re.search(r"(?<!prompt )\beval time =\s*([\d.]+) ms\s*/\s*(\d+) runs", runtime_log)
        try:
            parsed, end = json.JSONDecoder().raw_decode(raw)
            if raw[end:].strip() not in ("", "[end of text]"):
                parsed = None
        except ValueError:
            parsed = None
        return parsed, dict(role=role, stage=stage, raw=raw, token_ceiling=allowance,
                            peak_sampled_rss=peak, elapsed_seconds=time.monotonic() - started,
                            job_commit_limit=commit_cap, peak_job_commit=commit_peak,
                            prompt_eval_tokens=int(prompt_perf[2]) if prompt_perf else None,
                            prompt_eval_ms=float(prompt_perf[1]) if prompt_perf else None,
                            decode_eval_runs=int(decode_perf[2]) if decode_perf else None,
                            decode_eval_ms=float(decode_perf[1]) if decode_perf else None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("cli", "weights", "gold", "output"):
        parser.add_argument(f"--{arg}", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=24, choices=range(1, 25))
    parser.add_argument("--one-step", action="store_true",
                        help="Run only the one-step forced arm for a follow-up comparison")
    args = parser.parse_args()
    data = ROOT / "research/tier8_v2"
    ids = [row["case_id"] for row in jsonl(
        data / "runs/finqa-mas-3b-unadapted-direct-dev24-01/cases.jsonl")][:args.limit]
    public = {row["id"]: row for row in jsonl(data / "data/finqa-development-public.jsonl")}
    gold = {row["id"]: row for row in json.loads(args.gold.read_text(encoding="utf-8"))}
    for key in ids:
        if public[key]["question"] != gold[key]["qa"]["question"]:
            raise ValueError(f"Gold question mismatch for {key}")
    models = Models(args)
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "cases.jsonl").open("x", encoding="utf-8") as ledger:
        for index, key in enumerate(ids):
            order = (True,) if args.one_step else (bool(index % 2), not bool(index % 2))
            for forced in order:
                models.forced = forced
                packet = {k: v for k, v in public[key].items() if k != "gold"}
                result = run_financial(packet, models, "mas", "none", representation="reference",
                                       selector="none", causal_mode="grammar", catalog_style="compact",
                                       unit_mode="question")
                score = evaluate_financial(gold[key], result["initial_answer"], result["initial_execution"])
                ledger.write(json.dumps({**result, "forced": forced, "score": score,
                                         "one_step": args.one_step}) + "\n")
                ledger.flush()
                print(key, forced, result["delivered"], score["case_success"], flush=True)


if __name__ == "__main__":
    main()
