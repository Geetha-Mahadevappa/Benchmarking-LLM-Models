#!/usr/bin/env python3
"""Utility helpers for running and summarizing LLM benchmark suites.

This script is intentionally lightweight: it simply wraps the command-line
interfaces of OpenAI Evals, HELM, and LM Eval Harness so that benchmark runs can
be orchestrated from a single entry point. A secondary "summarize" command scans
an artifacts directory and aggregates numeric metrics into a compact report.
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, Sequence

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore


TOOL_COMMANDS = {
    "openai-evals": {
        "executable": ["oaieval", "run"],
        "config_flag": None,
        "model_flag": "--model",
    },
    "helm": {
        "executable": ["helm-run"],
        "config_flag": "--config",
        "model_flag": "--model",
    },
    "lm-eval": {
        "executable": ["lm_eval"],
        "config_flag": "--config",
        "model_flag": "--model",
    },
}


def build_command(tool: str, config: Path, model: str | None, extra: Sequence[str]) -> List[str]:
    """Construct the command to execute for a given tool."""
    if tool not in TOOL_COMMANDS:
        raise ValueError(f"Unsupported tool '{tool}'. Expected one of {sorted(TOOL_COMMANDS)}")

    meta = TOOL_COMMANDS[tool]
    command: List[str] = list(meta["executable"])

    if meta["config_flag"]:
        command.extend([meta["config_flag"], str(config)])
    else:
        command.append(str(config))

    if model and meta["model_flag"]:
        command.extend([meta["model_flag"], model])

    command.extend(extra)
    return command


def command_available(command: Sequence[str]) -> bool:
    """Return True if the underlying executable for ``command`` exists on PATH."""
    if not command:
        return False
    executable = command[0]
    return shutil.which(executable) is not None


def run_tool(tool: str, config: Path, model: str | None, dry_run: bool, extra: Sequence[str]) -> int:
    """Execute a benchmarking command if the executable is available."""
    command = build_command(tool, config, model, extra)

    print(f"[benchmark] Tool     : {tool}")
    print(f"[benchmark] Config   : {config}")
    if model:
        print(f"[benchmark] Model    : {model}")
    print(f"[benchmark] Extra    : {' '.join(extra) if extra else '(none)'}")
    print(f"[benchmark] Command  : {' '.join(command)}")

    if dry_run:
        print("[benchmark] Dry run requested. Command not executed.")
        return 0

    if not command_available(command):
        print(
            "[benchmark] ERROR    : Executable not found on PATH. "
            "Install the relevant framework or run with --dry-run."
        )
        return 127

    result = subprocess.run(command, check=False)
    print(f"[benchmark] Exit code: {result.returncode}")
    return result.returncode


def summarize_artifacts(directory: Path) -> Dict[str, Dict[str, float]]:
    """Aggregate numeric metrics from JSON/JSONL/YAML artifact files."""
    metrics: MutableMapping[str, List[float]] = defaultdict(list)

    def collect_numeric(payload: Any, prefix: str = "") -> None:
        if isinstance(payload, MutableMapping):
            for key, value in payload.items():
                collect_numeric(value, f"{prefix}{key}.")
        elif isinstance(payload, list):
            for idx, value in enumerate(payload):
                collect_numeric(value, f"{prefix}{idx}.")
        else:
            if isinstance(payload, (int, float)) and not isinstance(payload, bool):
                metrics[prefix.rstrip(".")].append(float(payload))

    for path in directory.rglob("*"):
        if path.is_dir():
            continue
        try:
            if path.suffix == ".json":
                data = json.loads(path.read_text())
                collect_numeric(data)
            elif path.suffix == ".jsonl":
                for line in path.read_text().splitlines():
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    collect_numeric(data)
            elif path.suffix in {".yml", ".yaml"} and yaml is not None:
                data = yaml.safe_load(path.read_text())
                collect_numeric(data)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[summarize] Skipping {path} ({exc})", file=sys.stderr)
            continue

    summary: Dict[str, Dict[str, float]] = {}
    for name, values in metrics.items():
        if not values:
            continue
        summary[name] = {
            "count": float(len(values)),
            "mean": statistics.fmean(values),
            "min": min(values),
            "max": max(values),
        }
    return summary


def print_summary_table(summary: Dict[str, Dict[str, float]]) -> None:
    if not summary:
        print("[summarize] No numeric metrics discovered in artifacts.")
        return

    header = f"{'Metric':40} | {'Count':>5} | {'Mean':>8} | {'Min':>8} | {'Max':>8}"
    print(header)
    print("-" * len(header))
    for metric_name in sorted(summary):
        stats = summary[metric_name]
        print(
            f"{metric_name:40} | {int(stats['count']):5d} | "
            f"{stats['mean']:8.3f} | {stats['min']:8.3f} | {stats['max']:8.3f}"
        )


def ensure_output_directory(base: Path, tool: str) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_dir = base / tool / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=False)

    run_parser = subparsers.add_parser("run", help="Execute a benchmark run")
    run_parser.set_defaults(command="run")
    run_parser.add_argument("--tool", choices=sorted(TOOL_COMMANDS), required=True)
    run_parser.add_argument("--config", type=Path, required=True)
    run_parser.add_argument("--model", type=str, default=None)
    run_parser.add_argument("--extra", nargs=argparse.REMAINDER, default=[], help="Additional CLI args")
    run_parser.add_argument("--dry-run", action="store_true", help="Print the command without executing it")
    run_parser.add_argument(
        "--artifacts",
        type=Path,
        default=Path("artifacts"),
        help="Base directory for storing run outputs",
    )

    summarize_parser = subparsers.add_parser("summarize", help="Summarize numeric metrics from artifacts")
    summarize_parser.set_defaults(command="summarize")
    summarize_parser.add_argument("directory", type=Path, help="Artifact directory to summarize")

    args = parser.parse_args(argv)

    if args.command == "run":
        if args.config and not args.config.exists():
            parser.error(f"Configuration file '{args.config}' does not exist.")
        run_dir = ensure_output_directory(args.artifacts, args.tool)
        print(f"[benchmark] Outputs will be saved under: {run_dir}")
        return run_tool(args.tool, args.config, args.model, args.dry_run, args.extra)

    if args.command == "summarize":
        if not args.directory.exists():
            parser.error(f"Artifact directory '{args.directory}' does not exist.")
        summary = summarize_artifacts(args.directory)
        print_summary_table(summary)
        return 0

    parser.error(f"Unknown command '{args.command}'")


if __name__ == "__main__":
    sys.exit(main())
