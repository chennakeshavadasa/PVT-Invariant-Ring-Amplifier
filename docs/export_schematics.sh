#!/usr/bin/env bash
# Export xschem schematics as light-background PNGs for the README (docs/figures/schematics/).
# The title block, code blocks and launchers are removed and the drawing is cropped to its
# content.  Needs xschem, PDK_ROOT, an X display (xschem renders PNGs through Tk) and Pillow.
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
  set c [xschem getprop instance \$i cell::name]
  if {[regexp {annotate_fet_params|title\.sym|code_shown|code\.sym|launcher} \$c]} { xschem select instance \$i }
}
xschem delete
xschem zoom_full
xschem print png $OUT/$2 3600 2400
exit
TCL
  xschem -q --rcfile xschemrc --script /tmp/xschem_export_$$.tcl > /dev/null 2>&1
  rm -f /tmp/xschem_export_$$.tcl
  python3 - "$OUT/$2" <<'PY'
import sys
from PIL import Image, ImageChops
p = sys.argv[1]
im = Image.open(p).convert("RGB")
bg = Image.new("RGB", im.size, (255, 255, 255))
box = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
im = im.crop(box)
pad = 30
out = Image.new("RGB", (im.width + 2 * pad, im.height + 2 * pad), (255, 255, 255))
out.paste(im, (pad, pad))
out.save(p, optimize=True)
PY
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
