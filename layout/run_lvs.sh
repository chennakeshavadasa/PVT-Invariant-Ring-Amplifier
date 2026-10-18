#!/usr/bin/env bash
# LVS of layout/RAMP_LR.gds against the xschem schematic (IHP SG13G2 KLayout deck).
# Usage: layout/run_lvs.sh [run_dir]     (needs PDK_ROOT, xschem, klayout + python 'klayout' module)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
RUN="${1:-$HERE/build/lvs}"
PY="${PYTHON:-python3}"
DECK="$PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/lvs/run_lvs.py"
rm -rf "$RUN"; mkdir -p "$RUN"
( cd "$HERE/../Design Files/RAMP" &&
  xschem -n -q -x --rcfile xschemrc --tcl "set lvs_netlist 1; set lvs_ignore 1; set top_subckt 1; set flat_netlist 1" \
         -o "$RUN" RAMP-LR/RAMP_LR.sch )
# xschem's flat netlist has no .subckt wrapper: add it from the PININFO line
"$PY" - "$RUN/RAMP_LR.spice" "$RUN/RAMP_LR.cir" <<'PYEOF'
import re, sys
s = open(sys.argv[1]).read()
pins = [p.split(":")[0] for p in re.search(r"^\*\.PININFO (.*)$", s, re.M).group(1).split()]
body = "\n".join(l for l in s.splitlines() if l.strip() and not l.startswith("**") and l.strip().upper() != ".END")
open(sys.argv[2], "w").write(f".SUBCKT RAMP_LR {' '.join(pins)}\n{body}\n.ENDS RAMP_LR\n")
PYEOF
"$PY" "$DECK" --layout="$HERE/RAMP_LR.gds" --netlist="$RUN/RAMP_LR.cir" --topcell=RAMP_LR --run_dir="$RUN" > "$RUN/run.log" 2>&1 || true
# do not trust the runner's status line: read the comparison result itself
"$PY" "$HERE/lvs_summary.py" "$RUN/RAMP_LR.lvsdb" | tee "$RUN/summary.txt"
grep -q "RAMP_LR <-> RAMP_LR: Match" "$RUN/summary.txt"
