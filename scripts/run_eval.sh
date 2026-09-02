#!/usr/bin/env bash
set -euo pipefail
python -m careguard.eval
echo "Report written to data/eval_report.json"
