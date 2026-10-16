#!/usr/bin/env bash
# Export xschem schematics as light-background PNGs for the README (docs/figures/schematics/).
# Needs xschem, PDK_ROOT and an X display (xschem renders PNGs through Tk).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$REPO/docs/figures/schematics"
mkdir -p "$OUT"
cd "$REPO/Design Files/RAMP"
export_one() {   # <schematic> <png name>
  cat > /tmp/xschem_export_$$.tcl <<TCL
xschem toggle_colorscheme
xschem load [file normalize "$1"]
set n [xschem get instances]
for {set i [expr {\$n-1}]} {\$i >= 0} {incr i -1} {
  if {[string match *annotate_fet_params* [xschem getprop instance \$i cell::name]]} { xschem select instance \$i }
}
xschem delete
xschem zoom_full
xschem print png $OUT/$2 2200 1200
exit
TCL
  xschem -q --rcfile xschemrc --script /tmp/xschem_export_$$.tcl > /dev/null 2>&1
  rm -f /tmp/xschem_export_$$.tcl
  echo "wrote $OUT/$2"
}
export_one Fully-Diff-RAMP/RAMP.sch          sch_ramp_top.png
export_one Fully-Diff-RAMP/STG1.sch          sch_stg1.png
export_one Fully-Diff-RAMP/STG1-CM.sch       sch_stg1_cm.png
export_one Fully-Diff-RAMP/STG2.sch          sch_stg2.png
export_one Fully-Diff-RAMP/STG2_Replica.sch  sch_stg2_replica.png
export_one OTA/POTA.sch                      sch_pota.png
export_one OTA/NOTA.sch                      sch_nota.png
export_one RAMP-Test/RamP_tb1_CP_FB.sch      sch_tb_loopgain.png
