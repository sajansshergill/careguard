#!/usr/bin/env bash
set -euo pipefail
echo "Building policy index..."
python -m careguard.ingest --source data/policies/
echo "Generating synthetic cases..."
python data/cases/generate_cases.py
echo "Done. Index + labeled set ready."
