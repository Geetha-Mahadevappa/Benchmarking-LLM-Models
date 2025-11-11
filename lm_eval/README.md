# LM Eval Harness Assets

This directory contains configuration templates for the [LM Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness).

## Contents

- `configs/` – YAML definitions for multi-task sweeps and single-task runs.
- `checkpoints/` – Place optional adapters or checkpoints here if required for local inference.

## Usage

```bash
lm_eval --config lm_eval/configs/math_gsm.yaml --model gpt-4o-mini
