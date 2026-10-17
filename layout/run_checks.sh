#!/usr/bin/env bash
# Regenerate the layout and run every physical check; short reports go to layout/reports/.
#   DRC (main deck incl. extra rules, no density) - must be clean
#   antenna                                       - must be clean
#   density (chip-level fill rules)               - reported only: an unfilled block cannot meet them
#   LVS against the xschem schematic              - must match
# Needs PDK_ROOT, klayout, xschem and a python with the 'klayout' module (set PYTHON=...).
# Usage: layout/run_checks.sh            (RAMP_LR, reports/*.txt)
#        TOP=RAMP_V2 layout/run_checks.sh (RAMP_V2, reports/RAMP_V2_*.txt)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
export TOP="${TOP:-RAMP_LR}"
DECK="$PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/drc/run_drc.py"
if [ "$TOP" = RAMP_LR ]; then PRE=""; DESIGN=ramp_lr_design; ARG=""; else PRE="${TOP}_"; DESIGN=ramp_v2_design; ARG=v2; fi
mkdir -p "$HERE/reports"
( cd "$HERE" && python3 gen_schematics.py $ARG )
( cd "$HERE/.." && klayout -b -r layout/gen_layout.py -rd design=$DESIGN ) | tee "$HERE/reports/${PRE}layout.txt"
"$HERE/run_drc.sh" "$HERE/build/drc_$TOP" > /dev/null || true
cp "$HERE/build/drc_$TOP/summary.txt" "$HERE/reports/${PRE}drc_main.txt"
for mode in antenna_only density_only; do
  run="$HERE/build/drc_${TOP}_$mode"; rm -rf "$run"
  "$PY" "$DECK" --path="$HERE/$TOP.gds" --topcell="$TOP" --run_dir="$run" --"$mode" > "$run.log" 2>&1 || true
  "$PY" "$HERE/drc_summary.py" "$(ls "$run"/*.lyrdb | head -1)" 2 > "$HERE/reports/${PRE}drc_${mode%_only}.txt"
done
"$HERE/run_lvs.sh" "$HERE/build/lvs_$TOP" > /dev/null || true
cp "$HERE/build/lvs_$TOP/summary.txt" "$HERE/reports/${PRE}lvs.txt"
echo "== DRC (main)";  cat "$HERE/reports/${PRE}drc_main.txt"
echo "== antenna";     cat "$HERE/reports/${PRE}drc_antenna.txt"
echo "== density";     head -3 "$HERE/reports/${PRE}drc_density.txt"
echo "== LVS";         cat "$HERE/reports/${PRE}lvs.txt"
grep -q "DRC clean" "$HERE/reports/${PRE}drc_main.txt" && grep -q "DRC clean" "$HERE/reports/${PRE}drc_antenna.txt" \
  && grep -q "$TOP <-> $TOP: Match" "$HERE/reports/${PRE}lvs.txt"
