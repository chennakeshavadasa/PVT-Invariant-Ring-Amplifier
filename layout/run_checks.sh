#!/usr/bin/env bash
# Regenerate the layout and run every physical check; short reports go to layout/reports/.
#   DRC (main deck incl. extra rules, no density) - must be clean
#   antenna                                       - must be clean
#   density (chip-level fill rules)               - reported only: an unfilled block cannot meet them
#   LVS against the xschem schematic              - must match
# Needs PDK_ROOT, klayout, xschem and a python with the 'klayout' module (set PYTHON=...).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
DECK="$PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/drc/run_drc.py"
mkdir -p "$HERE/reports"
( cd "$HERE" && python3 gen_schematics.py )
( cd "$HERE/.." && klayout -b -r layout/gen_layout.py ) | tee "$HERE/reports/layout.txt"
"$HERE/run_drc.sh" "$HERE/build/drc" > /dev/null || true
cp "$HERE/build/drc/summary.txt" "$HERE/reports/drc_main.txt"
for mode in antenna_only density_only; do
  run="$HERE/build/drc_$mode"; rm -rf "$run"
  "$PY" "$DECK" --path="$HERE/RAMP_LR.gds" --topcell=RAMP_LR --run_dir="$run" --"$mode" > "$run.log" 2>&1 || true
  "$PY" "$HERE/drc_summary.py" "$(ls "$run"/*.lyrdb | head -1)" 2 > "$HERE/reports/drc_${mode%_only}.txt"
done
"$HERE/run_lvs.sh" "$HERE/build/lvs" > /dev/null || true
cp "$HERE/build/lvs/summary.txt" "$HERE/reports/lvs.txt"
echo "== DRC (main)";  cat "$HERE/reports/drc_main.txt"
echo "== antenna";     cat "$HERE/reports/drc_antenna.txt"
echo "== density";     head -3 "$HERE/reports/drc_density.txt"
echo "== LVS";         cat "$HERE/reports/lvs.txt"
grep -q "DRC clean" "$HERE/reports/drc_main.txt" && grep -q "DRC clean" "$HERE/reports/drc_antenna.txt" \
  && grep -q "RAMP_LR <-> RAMP_LR: Match" "$HERE/reports/lvs.txt"
