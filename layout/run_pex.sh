#!/usr/bin/env bash
# Parasitic extraction of layout/RAMP_LR.gds with magic and the IHP SG13G2 extraction rules:
# every device plus the area, fringe and coupling capacitance of every net (C only, the wire
# resistance is not extracted).  A netgen LVS of magic's device netlist against the xschem
# schematic checks that the extracted netlist is the right circuit.
# Output: layout/pex/RAMP_LR_pex.spice and layout/reports/pex.txt
# Usage: layout/run_pex.sh        (needs PDK_ROOT, magic, netgen, xschem)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
RUN="$HERE/build/pex"
OUT="$HERE/pex"
TECH="$PDK_ROOT/ihp-sg13g2/libs.tech"
rm -rf "$RUN"; mkdir -p "$RUN" "$OUT" "$HERE/reports"
cat > "$RUN/ext.tcl" <<EOF
gds read $HERE/RAMP_LR.gds
load RAMP_LR
select top cell
extract all
ext2spice lvs
ext2spice subcircuit top on
ext2spice -o $RUN/RAMP_LR_lvs.spice
ext2spice cthresh 0.01
ext2spice -o $OUT/RAMP_LR_pex.spice
quit -noprompt
EOF
( cd "$RUN" && magic -dnull -noconsole -rcfile "$TECH/magic/ihp-sg13g2.magicrc" ext.tcl > magic.log 2>&1 )
# layout cells are named after their PCells (e.g. "rhigh", "nmos$1"); prefix them so that no
# cell has the name of a device model, and drop the "$" from the names
python3 - "$RUN/RAMP_LR_lvs.spice" "$OUT/RAMP_LR_pex.spice" <<'PYEOF'
import re, sys
for f in sys.argv[1:]:
    s = open(f).read().replace("$", "_")
    cells = [c for c in re.findall(r"^\.subckt (\S+)", s, re.M) if c != "RAMP_LR"]
    for c in cells:
        s = re.sub(rf"^(\.subckt ){re.escape(c)} ", rf"\1pc_{c} ", s, flags=re.M)
        s = re.sub(rf"^(X\S+ .* ){re.escape(c)}$", rf"\1pc_{c}", s, flags=re.M)
    open(f, "w").write(s)
PYEOF
# schematic netlist for netgen: xschem's hierarchical SPICE netlist with the top cell as .subckt
( cd "$HERE/../Design Files/RAMP" &&
  xschem -n -q -x --rcfile xschemrc --tcl "set top_subckt 1" -o "$RUN" RAMP-LR/RAMP_LR.sch )
sed -i 's/^\*\*\.subckt RAMP_LR/.subckt RAMP_LR/; s/^\*\*\.ends$/.ends/' "$RUN/RAMP_LR.spice"
( cd "$RUN" && netgen -batch lvs "RAMP_LR_lvs.spice RAMP_LR" "RAMP_LR.spice RAMP_LR" \
    "$TECH/netgen/ihp-sg13g2_setup.tcl" netgen.out > netgen.log 2>&1 ) || true
python3 - "$OUT/RAMP_LR_pex.spice" "$RUN/netgen.out" "$HERE/reports/pex.txt" <<'PYEOF'
import re, sys
pex, rep = open(sys.argv[1]).read(), open(sys.argv[2]).read()
units = {"a": 1e-18, "f": 1e-15, "p": 1e-12}
caps = [float(v[:-1]) * units[v[-1]] for v in re.findall(r"^C\d+ \S+ \S+ ([0-9.]+[afp])\s*$", pex, re.M)]
match = "Circuits match uniquely" in rep
lines = [f"magic PEX of RAMP_LR.gds: {len(caps)} parasitic capacitors, {sum(caps) * 1e12:.2f} pF in total "
         f"(threshold 0.01 fF, C only)",
         "netgen LVS of the magic netlist vs. schematic: " + ("Circuits match uniquely" if match else "MISMATCH")]
open(sys.argv[3], "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if match else 1)
PYEOF
