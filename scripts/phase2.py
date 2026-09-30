"""Build the pinned CPU runtime, convert Phase 2 weights, and smoke both arms.

All Phase 2 products are written beneath AGERE_SSD_ROOT. The repository checkout,
Python environment, and llama.cpp source/build remain on the host computer.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


REPO = Path(__file__).resolve().parents[1]
LLAMA_URL = "https://github.com/ggml-org/llama.cpp.git"
LLAMA_TAG = "v0.5.0"
LLAMA_COMMIT = "7fe450e19305b828c199d602c23a8337aaa1f03b"
SOURCE_MODELS = {
    "0.5b": "Qwen/Qwen2.5-0.5B-Instruct",
    "1.5b": "Qwen/Qwen2.5-1.5B-Instruct",
    "3b": "Qwen/Qwen2.5-3B-Instruct",
    "7b": "Qwen/Qwen2.5-7B-Instruct",
    "14b": "Qwen/Qwen2.5-14B-Instruct",
    "32b": "Qwen/Qwen2.5-32B-Instruct",
}
F16_SIZES_GIB = {"0.5b": 1.2, "1.5b": 3.2, "3b": 6.3, "7b": 15.0,
                 "14b": 29.5, "32b": 62.0}
Q4_SIZES_GIB = {"7b": 5.0, "14b": 9.0, "32b": 21.0}
FINAL_MODELS = (("0.5b", "f16"), ("1.5b", "f16"), ("3b", "f16"),
                ("7b", "f16"), ("7b", "q4_k_m"), ("14b", "q4_k_m"),
                ("32b", "q4_k_m"))
TIERS = {
    "8": {"cap_gb": 6.4, "context": 4096, "sas": "7b",
          "mas": (("orchestrator_drafter", "1.5b"), ("extractor", "0.5b"),
                  ("verifier", "0.5b"))},
    "16": {"cap_gb": 12.8, "context": 8192, "sas": "14b",
           "mas": (("orchestrator_drafter", "3b"), ("extractor", "1.5b"),
                   ("verifier", "0.5b"))},
    "32": {"cap_gb": 25.6, "context": 8192, "sas": "32b",
           "mas": (("orchestrator_drafter", "7b"), ("extractor", "3b"),
                   ("verifier", "0.5b"))},
}
GIB = 1024**3
GB = 1000**3


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def die(message: str) -> None:
    raise RuntimeError(message)


def sha256(path: Path, *, progress: bool = False) -> str:
    digest = hashlib.sha256()
    total = path.stat().st_size
    completed = 0
    next_notice = time.monotonic() + 5
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
            completed += len(chunk)
            if progress and time.monotonic() >= next_notice:
                print(f"Hashing {path.name}: {completed / total:.0%} ({completed / GIB:.1f}/{total / GIB:.1f} GiB)", flush=True)
                next_notice = time.monotonic() + 5
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class Paths:
    ssd: Path

    @property
    def llama(self) -> Path:
        return REPO / ".local" / "llama.cpp"

    @property
    def phase(self) -> Path:
        return self.ssd / "phase2"

    @property
    def logs(self) -> Path:
        return self.phase / "logs"

    @property
    def manifests(self) -> Path:
        return self.phase / "manifests"

    @property
    def runs(self) -> Path:
        return self.phase / "runs"

    @property
    def gguf(self) -> Path:
        return self.ssd / "weights" / "gguf"

    @property
    def scratch(self) -> Path:
        return self.phase / "tmp"

    def source(self, size: str) -> Path:
        return self.ssd / "weights" / "hf" / SOURCE_MODELS[size].replace("/", "--")

    def output(self, size: str, kind: str) -> Path:
        return self.gguf / f"qwen2.5-{size}-instruct-{kind}.gguf"


def validate_paths() -> Paths:
    value = os.environ.get("AGERE_SSD_ROOT", "").strip()
    if not value:
        die("Set AGERE_SSD_ROOT to this lab PC's mounted Agere SSD path first.")
    ssd = Path(value).expanduser().resolve(strict=True)
    if not ssd.is_dir() or not (ssd / "weights" / "hf").is_dir():
        die(f"SSD root is missing weights/hf: {ssd}")
    if ssd == REPO or ssd.is_relative_to(REPO) or REPO.is_relative_to(ssd):
        die("The repository checkout must be on the lab PC, separate from the SSD.")
    if os.stat(ssd).st_dev == os.stat(REPO).st_dev:
        die("The repository and AGERE_SSD_ROOT resolve to the same device.")
    paths = Paths(ssd)
    for directory in (paths.logs, paths.manifests, paths.runs, paths.gguf, paths.scratch):
        directory.mkdir(parents=True, exist_ok=True)
    print(f"Repository (code and build): {REPO}", flush=True)
    print(f"External SSD (all Phase 2 products): {ssd}", flush=True)
    print(f"SSD free: {shutil.disk_usage(ssd).free / GIB:.1f} GiB", flush=True)
    return paths


def run_logged(command: list[str], log: Path, *, cwd: Path = REPO, env: dict | None = None) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8", errors="replace") as output:
        output.write(f"\n[{now()}] cwd={cwd}\n[{now()}] command={subprocess.list2cmdline(command)}\n")
        output.flush()
        print(f"$ {subprocess.list2cmdline(command)}", flush=True)
        with subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                              errors="replace", bufsize=1) as process:
            assert process.stdout is not None
            try:
                for line in process.stdout:
                    print(line, end="", flush=True)
                    output.write(line)
                    output.flush()
                return_code = process.wait()
            except KeyboardInterrupt:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                output.write(f"[{now()}] interrupted\n")
                raise
        output.write(f"[{now()}] exit={return_code}\n")
    if return_code:
        die(f"Command exited {return_code}; see {log}")


def capture(command: list[str], *, cwd: Path = REPO) -> str:
    result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def binary(paths: Paths, name: str) -> Path:
    extension = ".exe" if os.name == "nt" else ""
    for candidate in (
        paths.llama / "build" / "bin" / "Release" / (name + extension),
        paths.llama / "build" / "bin" / (name + extension),
    ):
        if candidate.is_file():
            return candidate
    die(f"Missing {name}; run the Phase 2 setup command first.")


def runtime_commit(paths: Paths) -> str:
    if not (paths.llama / ".git").is_dir():
        die(f"Missing pinned llama.cpp checkout at {paths.llama}; run setup first.")
    commit = capture(["git", "rev-parse", "HEAD"], cwd=paths.llama)
    if commit != LLAMA_COMMIT:
        die(f"llama.cpp is at {commit}, but Phase 2 requires {LLAMA_COMMIT} ({LLAMA_TAG}).")
    if capture(["git", "status", "--porcelain"], cwd=paths.llama):
        die("The pinned llama.cpp source checkout is modified; use a clean checkout.")
    return commit


def setup(paths: Paths) -> None:
    if sys.maxsize < 2**32:
        die("Phase 2 requires 64-bit Python on the lab PC.")
    for tool in ("git", "cmake"):
        if shutil.which(tool) is None:
            die(f"Install {tool} on the lab PC and add it to PATH before setup.")
    if not paths.llama.exists():
        paths.llama.parent.mkdir(parents=True, exist_ok=True)
        run_logged(["git", "clone", "--depth", "1", "--branch", LLAMA_TAG, LLAMA_URL,
                    str(paths.llama)], paths.logs / "setup.log")
    commit = runtime_commit(paths)
    run_logged(["cmake", "-S", str(paths.llama), "-B", str(paths.llama / "build"),
                "-DGGML_CUDA=OFF", "-DLLAMA_BUILD_TESTS=OFF"], paths.logs / "setup.log")
    run_logged(["cmake", "--build", str(paths.llama / "build"), "--config", "Release",
                "--target", "llama-quantize", "llama-server", "--parallel",
                str(min(os.cpu_count() or 4, 8))], paths.logs / "setup.log")
    run_logged([sys.executable, "-m", "pip", "install", "psutil>=6,<8", "PyYAML>=6,<7"],
               paths.logs / "setup.log")
    requirements = paths.llama / "requirements" / "requirements-convert_hf_to_gguf.txt"
    if not requirements.is_file():
        die(f"Pinned llama.cpp conversion requirements are missing: {requirements}")
    run_logged([sys.executable, "-m", "pip", "install", "-r", str(requirements)],
               paths.logs / "setup.log", cwd=requirements.parent)
    binary(paths, "llama-quantize")
    binary(paths, "llama-server")
    (paths.manifests / "pip-freeze.txt").write_text(
        capture([sys.executable, "-m", "pip", "freeze"]) + "\n", encoding="utf-8"
    )
    write_json(paths.manifests / "runtime.json", {
        "generated_at_utc": now(), "llama_cpp_url": LLAMA_URL,
        "llama_cpp_tag": LLAMA_TAG, "llama_cpp_commit": commit,
        "python": sys.version, "platform": platform.platform(),
        "project_commit": capture(["git", "rev-parse", "HEAD"]),
        "project_dirty": bool(capture(["git", "status", "--porcelain"])),
        "cmake": capture(["cmake", "--version"]).splitlines()[0],
    })
    print(f"Pinned CPU runtime ready: {commit}", flush=True)


def verify_locked_tiers() -> None:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is missing; run the Phase 2 setup command first.") from exc
    for tier, spec in TIERS.items():
        config_path = REPO / "configs" / "locked" / "tiers" / f"t{('8', '16', '32').index(tier) + 1}_{tier}gb.yaml"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        expected = {
            "physical_ram_gb": int(tier),
            "nominal_peak_rss_cap_gb": spec["cap_gb"],
            "context_tokens": spec["context"],
        }
        for key, value in expected.items():
            if config.get(key) != value:
                die(f"Runner {tier} GB {key} differs from locked config {config_path}: {value!r} versus {config.get(key)!r}")
        sas = config.get("sas", {})
        if sas.get("hf_id") != SOURCE_MODELS[spec["sas"]] or sas.get("gguf") != "Q4_K_M":
            die(f"Runner {tier} GB SAS differs from locked config {config_path}")
        locked_mas = [(item.get("instance"), item.get("hf_id"), item.get("gguf"))
                      for item in config.get("mas", {}).get("models", [])]
        runner_mas = [(instance, SOURCE_MODELS[size], "F16") for instance, size in spec["mas"]]
        if locked_mas != runner_mas:
            die(f"Runner {tier} GB MAS differs from locked config {config_path}")


def verify_sources(paths: Paths) -> dict[str, str]:
    manifest = REPO / "manifests" / "hf_snapshots.json"
    if not manifest.is_file():
        die(f"Missing Phase 1 source manifest in the cloned repository: {manifest}")
    entries = read_json(manifest).get("artifacts", [])
    revisions: dict[str, str] = {}
    verified = []
    with (paths.logs / "verify_sources.log").open("a", encoding="utf-8") as log:
        log.write(f"\n[{now()}] Verifying Phase 2 source weights at {paths.ssd}\n")
        for size, repo_id in SOURCE_MODELS.items():
            model_entries = [entry for entry in entries if entry.get("repo_id") == repo_id]
            if not model_entries or not any(str(e.get("path", "")).endswith(".safetensors") for e in model_entries):
                die(f"Phase 1 manifest has no complete safetensors listing for {repo_id}.")
            revisions_seen = {entry.get("revision") for entry in model_entries}
            if len(revisions_seen) != 1 or not next(iter(revisions_seen)):
                die(f"Inconsistent source revision for {repo_id}.")
            revisions[repo_id] = next(iter(revisions_seen))
            if not (paths.source(size) / "config.json").is_file():
                die(f"Missing source model config: {paths.source(size)}")
            for entry in model_entries:
                relative = PurePosixPath(entry["path"])
                file_path = (paths.ssd / relative).resolve()
                if not file_path.is_relative_to(paths.source(size)) or not file_path.is_file():
                    die(f"Missing or invalid source file: {relative}")
                if file_path.stat().st_size != entry["size_bytes"]:
                    die(f"Source file size differs from Phase 1 manifest: {relative}")
                actual = sha256(file_path, progress=True)
                if actual != entry["sha256"]:
                    die(f"Source file SHA-256 differs from Phase 1 manifest: {relative}")
                message = f"OK {relative} sha256={actual}\n"
                print(message, end="", flush=True)
                log.write(message)
                log.flush()
                verified.append(str(relative))
    write_json(paths.manifests / "source_verification.json", {
        "verified_at_utc": now(), "source_manifest": "repository/manifests/hf_snapshots.json",
        "source_manifest_sha256": sha256(manifest), "revisions": revisions,
        "verified_file_count": len(verified), "verified_files": verified,
    })
    return revisions


def valid_gguf(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 100_000_000:
        return False
    with path.open("rb") as stream:
        return stream.read(4) == b"GGUF"


def conversion_env(paths: Paths) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update({"TMP": str(paths.scratch), "TEMP": str(paths.scratch),
                        "TMPDIR": str(paths.scratch), "PYTHONUNBUFFERED": "1",
                        "HF_HOME": str(paths.ssd / "weights" / "hub_cache")})
    return environment


def preflight_space(paths: Paths) -> None:
    # Simulate conversion order. The 14B and 32B F16 intermediates are
    # removed after each Q4 checksum, so their peak space is not additive.
    retained_gib = 0.0
    peak_gib = 0.0
    for size in ("0.5b", "1.5b", "3b"):
        if not valid_gguf(paths.output(size, "f16")):
            retained_gib += F16_SIZES_GIB[size]
            peak_gib = max(peak_gib, retained_gib)
    for size in ("14b", "7b", "32b"):
        f16 = paths.output(size, "f16") if size == "7b" else intermediate_f16(paths, size)
        q4 = paths.output(size, "q4_k_m")
        if size == "7b" and not valid_gguf(f16):
            retained_gib += F16_SIZES_GIB[size]
            peak_gib = max(peak_gib, retained_gib)
        if not valid_gguf(q4):
            temp_gib = F16_SIZES_GIB[size] if size != "7b" and not valid_gguf(f16) else 0.0
            peak_gib = max(peak_gib, retained_gib + temp_gib + Q4_SIZES_GIB[size])
            retained_gib += Q4_SIZES_GIB[size]
    needed_gib = peak_gib + 10.0  # safety room for temporary files and filesystem overhead
    free_gib = shutil.disk_usage(paths.ssd).free / GIB
    print(f"Conversion space preflight: need ~{needed_gib:.1f} GiB, free {free_gib:.1f} GiB")
    if free_gib < needed_gib:
        die(f"Insufficient SSD space for all-tier conversion; free at least {needed_gib:.1f} GiB.")


def intermediate_f16(paths: Paths, size: str) -> Path:
    return paths.gguf / f"qwen2.5-{size}-instruct-f16.tmp.gguf"


def convert_f16(paths: Paths, converter: Path, size: str, output: Path,
                environment: dict[str, str]) -> None:
    if valid_gguf(output):
        print(f"Already present: {output}")
        return
    partial = output.with_name(output.stem + ".partial.gguf")
    partial.unlink(missing_ok=True)
    run_logged([sys.executable, "-u", str(converter), str(paths.source(size)),
                "--outtype", "f16", "--outfile", str(partial)],
               paths.logs / f"convert_{size}.log", cwd=paths.llama, env=environment)
    if not valid_gguf(partial):
        die(f"Converter did not produce a valid GGUF: {partial}")
    os.replace(partial, output)


def quantize_model(paths: Paths, quantize: Path, size: str, f16: Path,
                   environment: dict[str, str]) -> None:
    q4 = paths.output(size, "q4_k_m")
    if valid_gguf(q4):
        print(f"Already present: {q4}")
        return
    partial = q4.with_name(q4.stem + ".partial.gguf")
    partial.unlink(missing_ok=True)
    run_logged([str(quantize), str(f16), str(partial), "Q4_K_M"],
               paths.logs / f"quantize_{size}.log", cwd=paths.llama, env=environment)
    if not valid_gguf(partial):
        die(f"Quantizer did not produce a valid GGUF: {partial}")
    os.replace(partial, q4)


def convert(paths: Paths) -> None:
    verify_locked_tiers()
    runtime_commit(paths)
    quantize = binary(paths, "llama-quantize")
    converter = paths.llama / "convert_hf_to_gguf.py"
    if not converter.is_file():
        die(f"Missing pinned converter: {converter}")
    revisions = verify_sources(paths)
    preflight_space(paths)
    environment = conversion_env(paths)
    for size in ("0.5b", "1.5b", "3b"):
        convert_f16(paths, converter, size, paths.output(size, "f16"), environment)
    for size in ("14b", "7b", "32b"):
        q4 = paths.output(size, "q4_k_m")
        f16 = paths.output(size, "f16") if size == "7b" else intermediate_f16(paths, size)
        if size == "7b" or not valid_gguf(q4):
            convert_f16(paths, converter, size, f16, environment)
        if not valid_gguf(q4):
            quantize_model(paths, quantize, size, f16, environment)
        if size != "7b" and f16.is_file():
            checksum = sha256(q4, progress=True)
            print(f"Verified Q4 checksum before removing {size} F16 intermediate: {checksum}")
            f16.unlink()
            print(f"Removed verified intermediate: {f16}")
    records = []
    for size, kind in FINAL_MODELS:
        output = paths.output(size, kind)
        if not valid_gguf(output):
            die(f"Missing or invalid Phase 2 output: {output}")
        checksum = sha256(output, progress=True)
        records.append({"model": SOURCE_MODELS[size], "source_revision": revisions[SOURCE_MODELS[size]],
                        "gguf_type": kind.upper(),
                        "path": output.relative_to(paths.ssd).as_posix(),
                        "size_bytes": output.stat().st_size, "sha256": checksum})
        print(f"SHA-256 {output.name}: {checksum}", flush=True)
    write_json(paths.manifests / "gguf_artifacts.json", {
        "generated_at_utc": now(), "llama_cpp_commit": LLAMA_COMMIT, "artifacts": records,
    })
    (paths.manifests / "weights.sha256").write_text(
        "".join(f"{record['sha256']}  {record['path']}\n" for record in records), encoding="utf-8"
    )
    print(f"Seven GGUF model files covering all three tiers are ready under {paths.ssd}")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def kill_tree(process: subprocess.Popen) -> None:
    try:
        import psutil
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except Exception:
        if process.poll() is None:
            process.kill()


class MemoryMonitor:
    def __init__(self, cap_bytes: int, reserve_bytes: int):
        self.cap_bytes = cap_bytes
        self.reserve_bytes = reserve_bytes
        self.processes: list[subprocess.Popen] = []
        self.peak_rss_bytes = 0
        self.minimum_host_available_bytes = 2**63 - 1
        self.samples = 0
        self.breach: str | None = None
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._watch, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=3)

    def _watch(self) -> None:
        import psutil
        while not self._stop.is_set():
            rss = 0
            for process in list(self.processes):
                try:
                    parent = psutil.Process(process.pid)
                    family = [parent] + parent.children(recursive=True)
                    rss += sum(item.memory_info().rss for item in family if item.is_running())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            available = psutil.virtual_memory().available
            self.samples += 1
            self.peak_rss_bytes = max(self.peak_rss_bytes, rss)
            self.minimum_host_available_bytes = min(self.minimum_host_available_bytes, available)
            if rss > self.cap_bytes:
                self.breach = f"Process tree RSS {rss / GB:.2f} GB exceeded {self.cap_bytes / GB:.2f} GB cap"
            elif available < self.reserve_bytes:
                self.breach = f"Host available memory fell below {self.reserve_bytes / GB:.1f} GB reserve"
            if self.breach:
                for process in list(self.processes):
                    kill_tree(process)
                return
            self._stop.wait(0.1)


class HardMemoryCap:
    """Apply one aggregate OS memory limit to every server in an arm."""

    def __init__(self, cap_bytes: int, arm: str):
        self.method = ""
        self._handle = None
        self._cgroup: Path | None = None
        if os.name == "nt":
            self._windows_setup(cap_bytes)
            self.method = "Windows Job Object job memory limit plus RSS watchdog"
        elif sys.platform == "linux":
            self._linux_setup(cap_bytes, arm)
            self.method = "Linux cgroup v2 memory.max and swap.max plus RSS watchdog"
        else:
            die("A hard aggregate memory cap is not implemented for this operating system.")

    def _windows_setup(self, cap_bytes: int) -> None:
        import ctypes

        class BasicLimits(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                        ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", ctypes.c_uint32),
                        ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t),
                        ("ActiveProcessLimit", ctypes.c_uint32),
                        ("Affinity", ctypes.c_size_t),
                        ("PriorityClass", ctypes.c_uint32),
                        ("SchedulingClass", ctypes.c_uint32)]

        class IoCounters(ctypes.Structure):
            _fields_ = [("ReadOperationCount", ctypes.c_size_t),
                        ("WriteOperationCount", ctypes.c_size_t),
                        ("OtherOperationCount", ctypes.c_size_t),
                        ("ReadTransferCount", ctypes.c_uint64),
                        ("WriteTransferCount", ctypes.c_uint64),
                        ("OtherTransferCount", ctypes.c_uint64)]

        class ExtendedLimits(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", BasicLimits), ("IoInfo", IoCounters),
                        ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t),
                        ("PeakJobMemoryUsed", ctypes.c_size_t)]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p)
        kernel.CreateJobObjectW.restype = ctypes.c_void_p
        kernel.SetInformationJobObject.argtypes = (ctypes.c_void_p, ctypes.c_int,
                                                    ctypes.c_void_p, ctypes.c_uint32)
        kernel.SetInformationJobObject.restype = ctypes.c_int
        kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
        kernel.CloseHandle.restype = ctypes.c_int
        kernel.OpenProcess.argtypes = (ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32)
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.AssignProcessToJobObject.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
        kernel.AssignProcessToJobObject.restype = ctypes.c_int
        handle = kernel.CreateJobObjectW(None, None)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = 0x00000200 | 0x00002000
        limits.JobMemoryLimit = cap_bytes
        if not kernel.SetInformationJobObject(handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            error = ctypes.get_last_error()
            kernel.CloseHandle(handle)
            raise ctypes.WinError(error)
        self._handle = handle
        self._kernel = kernel

    def _linux_setup(self, cap_bytes: int, arm: str) -> None:
        membership = Path("/proc/self/cgroup").read_text(encoding="utf-8").splitlines()
        unified = next((row.split("::", 1)[1] for row in membership if row.startswith("0::")), None)
        if unified is None:
            die("Linux smoke requires cgroup v2 for an aggregate hard memory cap.")
        parent = Path("/sys/fs/cgroup") / unified.lstrip("/")
        group = parent / f"agere-phase2-{os.getpid()}-{arm}"
        try:
            group.mkdir()
            (group / "memory.max").write_text(str(cap_bytes), encoding="ascii")
            (group / "memory.swap.max").write_text("0", encoding="ascii")
        except OSError as exc:
            if group.is_dir():
                try:
                    group.rmdir()
                except OSError:
                    pass
            die(f"Cannot create a writable cgroup v2 memory limit at {parent}: {exc}")
        self._cgroup = group

    def add(self, pid: int) -> None:
        if self._handle is not None:
            import ctypes
            process_handle = self._kernel.OpenProcess(0x0101, False, pid)
            if not process_handle:
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                if not self._kernel.AssignProcessToJobObject(self._handle, process_handle):
                    raise ctypes.WinError(ctypes.get_last_error())
            finally:
                self._kernel.CloseHandle(process_handle)
        elif self._cgroup is not None:
            (self._cgroup / "cgroup.procs").write_text(str(pid), encoding="ascii")

    def close(self) -> None:
        if self._handle is not None:
            self._kernel.CloseHandle(self._handle)
            self._handle = None
        if self._cgroup is not None:
            self._cgroup.rmdir()
            self._cgroup = None


def request_json(url: str, data: dict | None = None, *, timeout: float = 5) -> dict:
    body = json.dumps(data).encode("utf-8") if data is not None else None
    request = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"} if body else {})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def wait_ready(process: subprocess.Popen, port: int, monitor: MemoryMonitor, label: str,
               timeout_seconds: int, log: Path) -> None:
    started = time.monotonic()
    next_notice = started
    while time.monotonic() - started < timeout_seconds:
        if monitor.breach:
            die(monitor.breach)
        if process.poll() is not None:
            die(f"{label} server exited {process.returncode} while loading; see {log}")
        try:
            if request_json(f"http://127.0.0.1:{port}/health", timeout=3).get("status") == "ok":
                return
        except (urllib.error.URLError, TimeoutError, ValueError):
            pass
        if time.monotonic() >= next_notice:
            print(f"Waiting for {label} model load ({int(time.monotonic() - started)}s)...", flush=True)
            next_notice = time.monotonic() + 15
        time.sleep(0.5)
    die(f"Timed out loading {label} after {timeout_seconds}s; see {log}")


def smoke_arm(paths: Paths, tier: str, arm: str, context: int, timeout_seconds: int) -> dict:
    try:
        import psutil
    except ImportError as exc:
        raise RuntimeError("psutil is missing; run the Phase 2 setup command first.") from exc
    idle = psutil.virtual_memory()
    reserve = GB
    tier_spec = TIERS[tier]
    nominal_cap = int(tier_spec["cap_gb"] * GB)
    effective = min(nominal_cap, idle.available - reserve)
    if effective <= 0:
        die("Insufficient idle host memory after the required 1 GB OS safety reserve.")
    labels = (("sas", tier_spec["sas"]),) if arm == "sas" else tier_spec["mas"]
    monitor = MemoryMonitor(effective, reserve)
    hard_cap: HardMemoryCap | None = None
    processes: list[subprocess.Popen] = []
    handles = []
    result: dict = {
        "arm": arm, "tier_ram_gb": int(tier), "started_at_utc": now(), "status": "failed",
        "repository_root": str(REPO), "ssd_root": str(paths.ssd),
        "llama_cpp_commit": LLAMA_COMMIT, "context_tokens_per_model": context,
        "host_physical_bytes": idle.total,
        "idle_host_available_bytes": idle.available,
        "idle_non_job_use_bytes": idle.total - idle.available,
        "nominal_tier_process_cap_bytes": nominal_cap,
        "os_safety_reserve_bytes": reserve,
        "effective_process_cap_bytes": effective,
        "models": [],
    }
    output = paths.runs / f"smoke_{arm}_{tier}gb.json"
    print(f"{tier} GB {arm.upper()} effective process cap: {effective / GB:.2f} GB; idle host available: {idle.available / GB:.2f} GB")
    try:
        hard_cap = HardMemoryCap(effective, f"{tier}-{arm}")
        result["hard_cap_method"] = hard_cap.method
        monitor.start()
        for instance, size in labels:
            model = paths.output(size, "q4_k_m" if arm == "sas" else "f16")
            if not valid_gguf(model):
                die(f"Missing model for {tier} GB {arm} smoke: {model}")
            port = free_port()
            log = paths.logs / f"smoke_{tier}gb_{arm}_{instance}.log"
            handle = log.open("a", encoding="utf-8")
            handles.append(handle)
            command = [str(binary(paths, "llama-server")), "--model", str(model),
                       "--host", "127.0.0.1", "--port", str(port),
                       "--ctx-size", str(context), "--n-gpu-layers", "0",
                       "--fit", "off", "--threads", "4" if arm == "sas" else "2",
                       "--parallel", "1"]
            handle.write(f"\n[{now()}] command={subprocess.list2cmdline(command)}\n")
            handle.flush()
            process = subprocess.Popen(command, cwd=REPO, stdout=handle, stderr=subprocess.STDOUT)
            processes.append(process)
            monitor.processes.append(process)
            hard_cap.add(process.pid)
            print(f"Loading {tier} GB {instance} ({size}) on localhost:{port}; server log: {log}", flush=True)
            wait_ready(process, port, monitor, f"{tier} GB {instance}", timeout_seconds, log)
            result["models"].append({"instance": instance, "model": SOURCE_MODELS[size],
                                     "path": model.relative_to(paths.ssd).as_posix(),
                                     "port": port, "log": log.relative_to(paths.ssd).as_posix()})
        for item in result["models"]:
            if monitor.breach:
                die(monitor.breach)
            response = request_json(f"http://127.0.0.1:{item['port']}/completion",
                                    {"prompt": "Answer in one word: what is 2 + 2?", "n_predict": 16,
                                     "temperature": 0.0, "seed": 42}, timeout=180)
            if not response.get("content") and not response.get("tokens_predicted", 0):
                die(f"Completion produced no tokens for {item['model']}")
            item["completion"] = str(response["content"])[:256]
            item["tokens_predicted"] = response.get("tokens_predicted")
            print(f"Generated {item['instance']} ({item['model']}): {item['completion']!r}", flush=True)
        if monitor.breach:
            die(monitor.breach)
        if any(process.poll() is not None for process in processes):
            die("A resident model exited before the arm smoke completed.")
        result["status"] = "passed"
    except Exception as exc:
        result["error"] = str(exc)
        raise
    finally:
        monitor.stop()
        for process in processes:
            kill_tree(process)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        if hard_cap is not None:
            try:
                hard_cap.close()
            except OSError as exc:
                result["cleanup_error"] = str(exc)
                result["status"] = "failed"
        for handle in handles:
            handle.close()
        result["completed_at_utc"] = now()
        result["peak_process_tree_rss_bytes"] = monitor.peak_rss_bytes
        result["minimum_host_available_bytes"] = (
            monitor.minimum_host_available_bytes if monitor.samples else None
        )
        result["monitor_samples"] = monitor.samples
        if monitor.breach:
            result["memory_breach"] = monitor.breach
            result["status"] = "failed"
        write_json(output, result)
        print(f"Wrote {output}: {result['status']}", flush=True)
    if result["status"] != "passed":
        die(result.get("memory_breach") or result.get("cleanup_error") or f"{tier} GB {arm} smoke failed")
    return result


def verify_outputs(paths: Paths) -> None:
    manifest = paths.manifests / "gguf_artifacts.json"
    if not manifest.is_file():
        die(f"Missing Phase 2 GGUF manifest; run convert first: {manifest}")
    entries = read_json(manifest).get("artifacts", [])
    if len(entries) != len(FINAL_MODELS):
        die("The GGUF manifest must contain seven files across the three tiers.")
    expected = {paths.output(size, kind).relative_to(paths.ssd).as_posix()
                for size, kind in FINAL_MODELS}
    if {entry.get("path") for entry in entries} != expected:
        die("The GGUF manifest does not list the seven locked output filenames.")
    for entry in entries:
        model = (paths.ssd / PurePosixPath(entry["path"])).resolve()
        if not model.is_relative_to(paths.gguf) or not valid_gguf(model):
            die(f"Invalid GGUF path in manifest: {entry['path']}")
        if model.stat().st_size != entry["size_bytes"] or sha256(model, progress=True) != entry["sha256"]:
            die(f"GGUF size or SHA-256 mismatch: {model}")
        print(f"Verified GGUF: {model.name}", flush=True)


def smoke(paths: Paths, tier: str, arm: str, context: int | None, timeout_seconds: int) -> None:
    verify_locked_tiers()
    runtime_commit(paths)
    binary(paths, "llama-server")
    verify_outputs(paths)
    selected_arms = ("sas", "mas") if arm == "both" else (arm,)
    selected_tiers = ("16", "8", "32") if tier == "all" else (tier,)
    write_json(paths.phase / "phase2_summary.json", {
        "generated_at_utc": now(), "status": "incomplete",
        "message": f"Smoke run started for tiers {', '.join(selected_tiers)} and arms {', '.join(selected_arms)}",
    })
    for tier_name in selected_tiers:
        actual_context = context if context is not None else TIERS[tier_name]["context"]
        for arm_name in selected_arms:
            smoke_arm(paths, tier_name, arm_name, actual_context, timeout_seconds)
    tier_results = {}
    for tier_name in TIERS:
        sas = paths.runs / f"smoke_sas_{tier_name}gb.json"
        mas = paths.runs / f"smoke_mas_{tier_name}gb.json"
        if sas.is_file() and mas.is_file():
            sas_result, mas_result = read_json(sas), read_json(mas)
            same_context = sas_result.get("context_tokens_per_model") == mas_result.get("context_tokens_per_model")
            passed = sas_result.get("status") == mas_result.get("status") == "passed" and same_context
            tier_results[tier_name] = {
                "status": "passed" if passed else "incomplete",
                "context_tokens_per_model": sas_result.get("context_tokens_per_model") if same_context else None,
                "sas_smoke": f"phase2/runs/smoke_sas_{tier_name}gb.json",
                "mas_smoke": f"phase2/runs/smoke_mas_{tier_name}gb.json",
            }
    status = "complete" if len(tier_results) == 3 and all(
        value["status"] == "passed" for value in tier_results.values()
    ) else "incomplete"
    write_json(paths.phase / "phase2_summary.json", {
        "generated_at_utc": now(), "status": status, "tiers": tier_results,
        "gguf_manifest": "phase2/manifests/gguf_artifacts.json",
        "runtime_manifest": "phase2/manifests/runtime.json",
    })
    print(f"All-tier Phase 2 summary: {status} at {paths.phase / 'phase2_summary.json'}")


class Tee:
    def __init__(self, terminal, logfile):
        self.terminal = terminal
        self.logfile = logfile

    def write(self, text: str) -> int:
        self.terminal.write(text)
        self.logfile.write(text)
        self.logfile.flush()
        return len(text)

    def flush(self) -> None:
        self.terminal.flush()
        self.logfile.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=("setup", "convert", "smoke", "all"))
    parser.add_argument("--arm", choices=("sas", "mas", "both"), default="both",
                        help="smoke step: arm to load; both is the completion path")
    parser.add_argument("--tier", choices=("8", "16", "32", "all"), default="all",
                        help="smoke step: RAM tier to load; all is the completion path")
    parser.add_argument("--context", type=int,
                        help="override the locked context for the selected smoke tier(s)")
    parser.add_argument("--load-timeout", type=int, default=900,
                        help="seconds allowed for each model server to load")
    args = parser.parse_args()
    if (args.context is not None and args.context < 512) or args.load_timeout < 30:
        parser.error("--context must be >=512 and --load-timeout must be >=30")
    try:
        paths = validate_paths()
        logfile = paths.logs / f"session_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{args.step}.log"
        with logfile.open("a", encoding="utf-8") as session_log:
            with redirect_stdout(Tee(sys.stdout, session_log)), redirect_stderr(Tee(sys.stderr, session_log)):
                print(f"[{now()}] Phase 2 {args.step}; repository={REPO}; ssd={paths.ssd}")
                try:
                    if args.step in ("setup", "all"):
                        setup(paths)
                    if args.step in ("convert", "all"):
                        convert(paths)
                    if args.step in ("smoke", "all"):
                        smoke(paths, args.tier, args.arm, args.context, args.load_timeout)
                except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
                    print(f"ERROR: {exc}", file=sys.stderr, flush=True)
                    return 1
                except KeyboardInterrupt:
                    print("Interrupted; rerun the same step to resume completed outputs.", file=sys.stderr)
                    return 130
    except (RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
