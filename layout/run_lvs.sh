#!/usr/bin/env bash
# LVS of layout/<TOP>.gds (default RAMP_LR) against the xschem schematic (IHP SG13G2 KLayout deck).
# Usage: layout/run_lvs.sh [run_dir]     (needs PDK_ROOT, xschem, klayout + python 'klayout' module)
set -euo pipefail
TOP="${TOP:-RAMP_LR}"                       # RAMP_V2: TOP=RAMP_V2 layout/run_lvs.sh
CELLDIR="${CELLDIR:-${TOP/_/-}}"               # xschem library directory (RAMP-LR, RAMP-V2)
HERE="$(cd "$(dirname "$0")" && pwd)"
RUN="${1:-$HERE/build/lvs}"
PY="${PYTHON:-python3}"
DECK="$PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/lvs/run_lvs.py"
rm -rf "$RUN"; mkdir -p "$RUN"
( cd "$HERE/../Design Files/RAMP" &&
  xschem -n -q -x --rcfile xschemrc --tcl "set lvs_netlist 1; set lvs_ignore 1; set top_subckt 1; set flat_netlist 1" \
         -o "$RUN" ${CELLDIR}/${TOP}.sch )
# xschem's flat netlist has no .subckt wrapper: add it from the PININFO line
"$PY" - "$RUN/${TOP}.spice" "$RUN/${TOP}.cir" "$TOP" <<'PYEOF'
import re, sys
s = open(sys.argv[1]).read()
pins = [p.split(":")[0] for p in re.search(r"^\*\.PININFO (.*)$", s, re.M).group(1).split()]
body = "\n".join(l for l in s.splitlines() if l.strip() and not l.startswith("**") and l.strip().upper() != ".END")
top = sys.argv[3]
open(sys.argv[2], "w").write(f".SUBCKT {top} {' '.join(pins)}\n{body}\n.ENDS {top}\n")
PYEOF
"$PY" "$DECK" --layout="$HERE/${TOP}.gds" --netlist="$RUN/${TOP}.cir" --topcell=${TOP} --run_dir="$RUN" > "$RUN/run.log" 2>&1 || true
# do not trust the runner's status line: read the comparison result itself
"$PY" "$HERE/lvs_summary.py" "$RUN/${TOP}.lvsdb" | tee "$RUN/summary.txt"
grep -q "${TOP} <-> ${TOP}: Match" "$RUN/summary.txt"
