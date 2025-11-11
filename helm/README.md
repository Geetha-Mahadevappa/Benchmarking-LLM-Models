# HELM Assets

Configuration templates for [HELM](https://github.com/stanford-crfm/helm) benchmarking live in this directory.

## Contents

- `configs/` – JSON configuration snippets for the HELM runner.
- `scenarios/` – Add HELM scenario overrides here as you expand coverage.

## Usage

```bash
helm-run --config helm/configs/core.json
