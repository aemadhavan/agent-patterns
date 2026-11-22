"""Benchmark runner for all 15 Agent Design Patterns.

Runs each pattern's `run()` entrypoint, counts LLM calls, measures wall-clock
latency (plus P50/P99), scores output quality (0-1) via LLM-as-a-Judge,
optionally enables Arize Phoenix OpenTelemetry tracing, and writes
`benchmarks/results.md`.
"""

import importlib.util
import os
import re
import statistics
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from shared.llm import generate_text, get_call_count, reset_call_count

PATTERNS = [
    ("01_single_agent", "Single-Agent System", "Start Simple"),
    ("02_react", "ReAct (Reason + Act)", "Start Simple"),
    ("03_plan_and_execute", "Plan-and-Execute", "Start Simple"),
    ("04_sequential", "Sequential (Prompt Chaining)", "Control Flow"),
    ("05_parallel", "Parallel", "Control Flow"),
    ("06_loop", "Loop", "Control Flow"),
    ("07_routing", "Routing", "Dispatch & Scale"),
    ("08_coordinator", "Coordinator (Orchestrator-Workers)", "Dispatch & Scale"),
    ("09_hierarchical", "Hierarchical Task Decomposition", "Dispatch & Scale"),
    ("10_swarm", "Swarm (Multi-Agent Collaboration)", "Collaboration & Quality"),
    ("11_review_and_critique", "Review and Critique", "Collaboration & Quality"),
    ("12_iterative_refinement", "Iterative Refinement (Reflection)", "Collaboration & Quality"),
    ("13_tool_use_and_rag", "Tool Use and RAG (Grounded Agent)", "Grounding & Safety"),
    ("14_human_in_the_loop", "Human-in-the-Loop", "Grounding & Safety"),
    ("15_elephant_goldfish", "Elephant-Goldfish Model", "Collaboration & Quality"),
]


def _load_pattern_module(folder: str):
    path = ROOT / folder / "app.py"
    spec = importlib.util.spec_from_file_location(f"{folder}_app", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def judge_output(pattern_name: str, output: str) -> float:
    """LLM-as-a-Judge scoring output quality from 0.00 to 1.00."""
    prompt = (
        f"You are an impartial AI engineering evaluator.\n"
        f"Score the following output from the `{pattern_name}` agent pattern on a scale from "
        f"0.00 to 1.00 based on: (1) task completion, (2) factual grounding/accuracy, and "
        f"(3) clarity and actionability.\n\n"
        f"OUTPUT:\n{output[:2500]}\n\n"
        "Respond with ONLY a single decimal number between 0.00 and 1.00 (e.g., 0.92)."
    )
    raw = generate_text(prompt, max_tokens=16, track=False).strip()
    match = re.search(r"(?:0\.\d+|1\.00?|0|1)", raw)
    return round(float(match.group(0)), 2) if match else 0.0


def _percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((pct / 100.0) * (len(ordered) - 1)))))
    return ordered[idx]


def main() -> None:
    console = Console()
    if os.getenv("ENABLE_PHOENIX", "false").lower() == "true":
        from shared.observability import init_tracing
        init_tracing()

    rows = []
    latencies = []
    total_calls = 0

    table = Table(title="Agent Design Patterns Benchmark (15 Patterns)")
    table.add_column("Pattern", style="cyan")
    table.add_column("Quality (0-1)", justify="right", style="green")
    table.add_column("LLM Calls", justify="right", style="magenta")
    table.add_column("Latency (ms)", justify="right", style="yellow")

    for folder, name, category in PATTERNS:
        mod = _load_pattern_module(folder)
        reset_call_count()
        t0 = time.perf_counter()
        try:
            output = mod.run()
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            calls = get_call_count()
            score = judge_output(name, output)
            status = "OK"
            latencies.append(elapsed_ms)
            total_calls += calls
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            calls = get_call_count()
            score = 0.0
            status = f"ERR: {type(exc).__name__}"

        rows.append((folder, name, category, status, score, calls, elapsed_ms))
        table.add_row(folder, f"{score:.2f}", str(calls), str(elapsed_ms))

    p50 = int(statistics.median(latencies)) if latencies else 0
    p99 = _percentile(latencies, 99)

    console.print(table)
    console.print(
        f"\n[bold]Summary:[/bold] Total Agent LLM Calls = {total_calls} | "
        f"P50 Latency = {p50} ms | P99 Latency = {p99} ms"
    )

    out_dir = ROOT / "benchmarks"
    out_dir.mkdir(exist_ok=True)
    md_lines = [
        "# Agent Design Patterns — Benchmark Results",
        "",
        f"- **Total Agent LLM Calls:** {total_calls}",
        f"- **P50 Latency:** {p50} ms",
        f"- **P99 Latency:** {p99} ms",
        "",
        "| Pattern | Name | Category | Quality (0-1) | LLM Calls | Latency (ms) |",
        "| :--- | :--- | :--- | :---: | :---: | :---: |",
    ]
    for folder, name, category, status, score, calls, elapsed_ms in rows:
        md_lines.append(
            f"| `{folder}` | {name} | {category} | {score:.2f} | {calls} | {elapsed_ms} |"
        )
    (out_dir / "results.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    console.print(f"Saved markdown report to [bold]{out_dir / 'results.md'}[/bold]")


if __name__ == "__main__":
    main()
