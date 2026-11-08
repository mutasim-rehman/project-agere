"""Measure two local resident inference roles inside one Windows commit job."""
import argparse
from contextlib import ExitStack
import http.client
import json
from pathlib import Path
import socket
import subprocess
from threading import Event, Thread
import time

import psutil

from tier8_windows_pilot import CAP
from windows_job_commit import CREATE_SUSPENDED, JobCommitLimit


def request(port, route, body=None, timeout=5):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        if body is None:
            connection.request("GET", route)
        else:
            connection.request("POST", route, json.dumps(body), {"Content-Type": "application/json"})
        response = connection.getresponse()
        data = response.read()
        return response.status, json.loads(data)
    finally:
        connection.close()


def unused_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def stop_worker(worker):
    if worker.poll() is None:
        worker.terminate()
    worker.wait(timeout=20)


def run(args):
    args.output.mkdir(parents=True, exist_ok=False)
    state = {"status": "starting", "worker_job_commit_limit": args.commit_limit,
             "sampled_rss_limit": CAP, "models": [str(p) for p in args.model],
             "adapters": [str(p) if p else None for p in args.adapter],
             "context_per_worker": 4096, "peak_sampled_rss": 0, "responses": []}
    workers, ports = [], []
    stopped = Event()
    breached = Event()
    controller = psutil.Process()

    with ExitStack() as stack:
        trace = stack.enter_context((args.output / "memory.jsonl").open("x", encoding="utf-8"))
        job = stack.enter_context(JobCommitLimit(args.commit_limit))

        def sample():
            while not stopped.is_set():
                rss = controller.memory_info().rss
                for worker in tuple(workers):
                    try:
                        rss += psutil.Process(worker.pid).memory_info().rss
                    except psutil.NoSuchProcess:
                        pass
                state["peak_sampled_rss"] = max(state["peak_sampled_rss"], rss)
                trace.write(json.dumps(dict(timestamp=time.time(), sampled_rss=rss,
                    host_available=psutil.virtual_memory().available)) + "\n")
                trace.flush()
                if rss > CAP:
                    breached.set()
                    for worker in tuple(workers):
                        if worker.poll() is None:
                            worker.terminate()
                    return
                stopped.wait(0.2)

        monitor = Thread(target=sample)
        monitor.start()
        try:
            for index, (model, adapter) in enumerate(zip(args.model, args.adapter)):
                port = unused_port()
                ports.append(port)
                log = stack.enter_context((args.output / f"worker-{index}.log").open("wb"))
                argv = [str(args.server.resolve()), "-m", str(model.resolve()), "--host", "127.0.0.1",
                        "--port", str(port), "-c", "4096", "-np", "1", "-t", "8", "-ngl", "0",
                        "--load-mode", "none", "--no-webui"]
                if adapter:
                    argv.extend(["--lora", str(adapter.resolve())])
                worker = subprocess.Popen(argv, stdout=log, stderr=log,
                    creationflags=subprocess.CREATE_NO_WINDOW | CREATE_SUSPENDED)
                stack.callback(stop_worker, worker)
                workers.append(worker)
                job.assign(worker._handle)
                psutil.Process(worker.pid).resume()
                deadline = time.monotonic() + 150
                while True:
                    if breached.is_set() or worker.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError(f"Worker {index} failed readiness; see its log")
                    try:
                        status, _ = request(port, "/health", timeout=1)
                    except (OSError, ValueError):
                        status = 0
                    if status == 200:
                        break
                    time.sleep(0.25)
            for port in ports:
                status, response = request(port, "/v1/chat/completions", {
                    "messages": [{"role": "user", "content": "Reply with the word READY."}],
                    "temperature": 0, "max_tokens": 16}, timeout=90)
                if status != 200 or not response.get("choices") or any(p.poll() is not None for p in workers):
                    raise RuntimeError(f"Resident inference returned HTTP {status}")
                state["responses"].append(response["choices"][0]["message"]["content"])
            state["status"] = "completed"
        except (RuntimeError, OSError, ValueError) as exc:
            state.update(status="failed", error=str(exc))
        finally:
            stopped.set()
            monitor.join()
            state["peak_worker_job_commit"] = job.peak_commit()
            state["sampled_rss_breached"] = breached.is_set()
            state["worker_returncodes_before_cleanup"] = [worker.poll() for worker in workers]
            (args.output / "summary.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(state, indent=2), flush=True)
    if state["status"] != "completed" or state["sampled_rss_breached"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", type=Path, required=True)
    parser.add_argument("--model", type=Path, nargs=2, required=True)
    parser.add_argument("--adapter", type=Path, nargs=2, default=(None, None))
    parser.add_argument("--commit-limit", type=int, default=6_100_000_000)
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args())
