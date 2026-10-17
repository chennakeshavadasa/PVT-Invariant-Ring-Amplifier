#!/usr/bin/env bash
# DRC of layout/<TOP>.gds (default RAMP_LR) with the IHP SG13G2 KLayout main rule deck.
# Density/fill rules are chip-level and are skipped (--no_density).
# Usage: layout/run_drc.sh [run_dir]
set -euo pipefail
TOP="${TOP:-RAMP_LR}"                       # RAMP_V2: TOP=RAMP_V2 layout/run_drc.sh
CELLDIR="${CELLDIR:-${TOP/_/-}}"               # xschem library directory (RAMP-LR, RAMP-V2)
HERE="$(cd "$(dirname "$0")" && pwd)"
RUN="${1:-$HERE/build/drc}"
PY="${PYTHON:-python3}"
rm -rf "$RUN"; mkdir -p "$RUN"
"$PY" "$PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/drc/run_drc.py" --path="$HERE/${TOP}.gds" \
      --topcell=${TOP} --run_dir="$RUN" --no_density --mp="$(nproc)" > "$RUN/run.log" 2>&1 || true
"$PY" "$HERE/drc_summary.py" "$RUN/${TOP}_${TOP}_full.lyrdb" 5 | tee "$RUN/summary.txt"
grep -q "DRC clean" "$RUN/summary.txt"
