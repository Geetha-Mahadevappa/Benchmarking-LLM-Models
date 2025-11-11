# OpenAI Evals Assets

This folder contains configuration templates and prompt assets for running [OpenAI Evals](https://github.com/openai/evals) as part of the Benchmarking-LLM-Models toolkit.

## Contents

- `configs/` – YAML configuration files that can be passed directly to `oaieval run`.
- `prompts/` – (create as needed) prompt JSONL files referenced by the configs.

## Usage

```bash
oaieval run openai_evals/configs/mmlu.yaml --model gpt-4o
