"""Run the base track with real local inference; retain console evidence.

Usage: .venv/Scripts/python.exe scripts/run_base.py
Run setup first. Reports retain the required personal-review sections.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
import labkit

LOGS = ROOT / "benchmarks" / "logs"


def run_logged(label: str, args: list[str]) -> None:
    print(f"\n==> {label}", flush=True)
    with (LOGS / f"{label}.txt").open("w", encoding="utf-8") as log:
        proc = subprocess.Popen([sys.executable, *args], cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace")
        try:
            for line in proc.stdout:
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
            if proc.wait():
                raise RuntimeError(f"{label} failed; see benchmarks/logs/{label}.txt")
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=15)


def load_args(users: int) -> list[str]:
    return ["-m", "locust", "-f", "labs/02-serve/load-test.py", "--headless",
            "-u", str(users), "-r", "5" if users == 10 else "25", "-t", "60s",
            "--host", f"http://127.0.0.1:{labkit.server_port()}",
            "--csv", f"benchmarks/locust-{users}", "--csv-full-history"]


def main() -> int:
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONUNBUFFERED"] = "1"
    LOGS.mkdir(parents=True, exist_ok=True)
    active = labkit.load_active()
    for key in ("primary_model", "compare_model"):
        if not (ROOT / active[key]).is_file():
            labkit.die(f"Missing {active[key]}", "Run .\\lab.ps1 setup first.")
    labkit.runtime_bin("llama-server")
    labkit.runtime_bin("llama-bench")
    run_logged("01-hardware-probe", ["labs/00-setup/detect-hardware.py"])
    run_logged("02-bench", ["labs/01-measure/benchmark.py"])
    run_logged("02-tune", ["labs/01-measure/tune.py"])
    # Keep the original hardware-default thread count for every run so the
    # quant comparison and load runs remain comparable to the baseline.
    with labkit.serve_bg(str(ROOT / active["primary_model"])):
        run_logged("03-smoke", ["labs/02-serve/smoke-test.py"])
        run_logged("04-locust-10", load_args(10))
        # Sampling starts before spawning users and overlaps the whole load run.
        with (LOGS / "05-metrics-u50.txt").open("w", encoding="utf-8") as log:
            metrics = subprocess.Popen(
                [sys.executable, "labs/02-serve/record-metrics.py",
                 "--duration", "65", "--label", "u50"], cwd=ROOT,
                stdout=log, stderr=subprocess.STDOUT)
            try:
                run_logged("05-locust-50", load_args(50))
                if metrics.wait(timeout=90):
                    raise RuntimeError("Metrics sampling failed; see its log.")
            finally:
                if metrics.poll() is None:
                    metrics.terminate()
                    metrics.wait(timeout=15)
        run_logged("06-load-report", ["labs/02-serve/load-report.py"])
        run_logged("07-pipeline", ["labs/03-integrate/pipeline.py"])
    # Same prompt, same generation settings, on both quantizations. Preserve
    # outputs for the student's quality judgement without inventing a verdict.
    import httpx
    results = []
    question = "Explain the difference between throughput and goodput@SLO, with one example."
    for key in ("primary_model", "compare_model"):
        with labkit.serve_bg(str(ROOT / active[key])) as base:
            response = httpx.post(f"{base}/v1/chat/completions", timeout=300,
                                  json={"model": "local", "messages": [
                                      {"role": "user", "content": question}],
                                      "max_tokens": 200, "temperature": 0, "seed": 42})
            response.raise_for_status()
            results.append({"quant": active[key.replace("model", "quant")],
                            "question": question, "response": response.json()})
    import json
    (ROOT / "benchmarks" / "01-quality-comparison.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nBase measurements complete. Review reports, fill REFLECTION, capture the")
    print("five real screenshots, commit evidence, then run .\\lab.ps1 verify.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
