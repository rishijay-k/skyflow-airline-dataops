#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec python scripts/verify_streaming_pipeline.py "$@"
