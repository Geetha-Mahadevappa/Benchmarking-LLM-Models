
```markdown
# 🚀 Benchmarking-LLM-Models

**Benchmarking-LLM-Models** is a unified, lightweight toolkit for evaluating and comparing large language models (LLMs) using three major benchmarking ecosystems: **[OpenAI Evals](https://github.com/openai/evals)**, **[HELM](https://github.com/stanford-crfm/helm)**, and **[LM Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness)**.  
It provides a reproducible workflow to test reasoning, bias, safety, and performance characteristics of any model — from API-hosted systems to local open-weight deployments.

---

## 📚 Table of Contents

1. [Key Features](#-key-features)
2. [Project Layout](#-project-layout)
3. [Quickstart](#-quickstart)
4. [Example Benchmark Tables](#-example-benchmark-tables)
5. [Configuration Overview](#%EF%B8%8F-configuration-overview)
6. [Automation & Reporting](#-automation--reporting)
7. [Extending the Toolkit](#-extending-the-toolkit)
8. [Troubleshooting](#-troubleshooting)

---

## ✨ Key Features

- 🧩 **Unified Workflow** – Run benchmarks from multiple frameworks through one CLI interface.  
- ⚙️ **Pre-configured Templates** – Ready-to-run configs for MMLU, GSM8K, HELM Core, and more.  
- 📊 **Cross-Framework Reporting** – Aggregate metrics (accuracy, perplexity, bias, etc.) in one schema.  
- 🧠 **Automation Helpers** – A single script orchestrates runs, saves outputs, and summarizes results.  
- 🪶 **Lightweight Design** – No monolithic dependencies; uses each framework’s native runner.

---

## 📁 Project Layout
.
├── helm/                # HELM scenarios, configs, and adapters
├── lm_eval/             # LM Eval Harness configs and optional checkpoints
├── openai_evals/        # OpenAI Evals templates and prompt assets
├── scripts/             # Automation and summary utilities
├── .env.example         # Environment variable template
├── requirements.txt     # Minimal helper dependencies
└── README.md            # You are here!
---

## ⚡ Quickstart

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

### 2. Install the benchmarking frameworks

Follow the official installation guides to install each framework and its datasets:

* 🧠 [OpenAI Evals](https://github.com/openai/evals)
* 🧩 [HELM](https://github.com/stanford-crfm/helm)
* 📐 [LM Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness)

### 3. Provide API keys and credentials

Copy `.env.example` → `.env` and fill in the appropriate keys:

```bash
cp .env.example .env
# Edit .env with your OpenAI, Anthropic, Google, or Hugging Face credentials.
```

Export the variables to your shell:

```bash
export $(cat .env | xargs)
```

### 4. Run your first benchmark

Example (OpenAI Evals + MMLU):

```bash
python scripts/run_benchmarks.py run \
  --tool openai-evals \
  --config openai_evals/configs/mmlu.yaml
```

Add `--model` or `--extra` arguments to forward custom parameters to the underlying runner.

### 5. Summarize results

```bash
python scripts/run_benchmarks.py summarize artifacts/
```

This aggregates metrics from JSON, JSONL, and YAML files under `artifacts/` and prints a compact summary table.

---

## 📊 Example Benchmark Tables

Below are **illustrative metrics** showing how to report results (replace with your actual outputs):

### 🧪 OpenAI Evals

| Model          | Task Suite  | Accuracy (%) | ECE ↓ | Notes                             |
| -------------- | ----------- | ------------ | ----- | --------------------------------- |
| GPT-4o         | MMLU (STEM) | **83.5**     | 0.07  | Few-shot prompts from `mmlu.yaml` |
| Claude 3 Opus  | GSM8K       | 90.2         | 0.05  | Chain-of-thought enabled          |
| Gemini 1.5 Pro | TruthfulQA  | 75.1         | 0.09  | Hallucination audit disabled      |
| Llama 3 70B    | CodeBench   | 64.3         | 0.12  | Quantized inference backend       |

### 🧭 HELM

| Model            | Scenario Bundle | Exact Match (%) | Robustness Δ | Bias ↓ | Notes                             |
| ---------------- | --------------- | --------------- | ------------ | ------ | --------------------------------- |
| GPT-4o           | HELM Core       | 71.8            | -3.4         | 0.18   | Run with `helm/configs/core.json` |
| Claude 3 Sonnet  | Safety Red Team | 63.5            | -1.1         | 0.11   | Safety filter enabled             |
| Gemini 1.5 Flash | SummEval        | 54.2            | -5.3         | 0.22   | Summaries benchmark               |
| Llama 3 8B       | MATH            | 38.7            | -6.5         | 0.27   | Custom inference wrapper required |

### 📐 LM Eval Harness

| Model           | Task Group    | Metric (↑)  | Score | Context | Notes                              |
| --------------- | ------------- | ----------- | ----- | ------- | ---------------------------------- |
| GPT-4o Mini     | HellaSwag     | Acc.        | 88.6  | 8K      | `--fewshot 5`                      |
| Claude 3 Haiku  | Winogrande    | Acc.        | 86.4  | 4K      | `--batch_size 16`                  |
| Gemini 1.5 Nano | ARC Challenge | Acc.        | 54.9  | 32K     | Tests long-context handling        |
| Llama 3 70B     | GSM8K         | Exact Match | 61.7  | 16K     | LoRA fine-tuned checkpoint adapter |

> 📝 *These values are placeholders for formatting illustration. Always replace them with real measurements.*

---

## ⚙️ Configuration Overview

| Framework           | Config Format | Directory               | Example         |
| ------------------- | ------------- | ----------------------- | --------------- |
| **OpenAI Evals**    | YAML          | `openai_evals/configs/` | `mmlu.yaml`     |
| **HELM**            | JSON          | `helm/configs/`         | `core.json`     |
| **LM Eval Harness** | YAML / JSON   | `lm_eval/configs/`      | `math_gsm.yaml` |

All configurations support environment variable substitution (API keys, model endpoints, etc.).
See `.env.example` for the canonical list of supported variables.

---

## 🤖 Automation & Reporting

`scripts/run_benchmarks.py` standardizes all runs and summaries:

* 🏃 `run` — Executes a benchmark via one of the supported tools.
* 📈 `summarize` — Recursively scans artifacts and aggregates numeric metrics.

Each run is logged under:

```
artifacts/{tool}/{timestamp}/
```

Example combined workflow:

```bash
# Run HELM
python scripts/run_benchmarks.py run --tool helm --config helm/configs/core.json --model gpt-4o

# Run LM Eval Harness
python scripts/run_benchmarks.py run --tool lm-eval --config lm_eval/configs/math_gsm.yaml --model llama-3-70b

# Summarize both
python scripts/run_benchmarks.py summarize artifacts/
```

---

## 🧩 Extending the Toolkit

You can easily add:

* 🧠 New tasks (JSON/YAML configs)
* 🧰 New frameworks (add to `TOOL_COMMANDS` in `scripts/run_benchmarks.py`)
* 📊 New metrics or visualization modules

To add a new benchmarking framework:

1. Define its CLI executable and flags in `TOOL_COMMANDS`.
2. Create a configuration directory (e.g., `new_framework/configs/`) with sample tasks.
3. Update automation scripts or documentation as needed.

---

## 🛠 Troubleshooting

* **Missing executables** – Run with `--dry-run` to verify the constructed command and ensure the framework is installed on your `PATH`.
* **Authentication errors** – Confirm credentials are exported in your shell session or configured in the framework-specific secrets store.
* **No metrics found** – Ensure the artifact directory contains JSON, JSONL, or YAML files with numeric fields. Non-numeric metrics are ignored by the summarizer.
```
