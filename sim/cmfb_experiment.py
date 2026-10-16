#!/usr/bin/env python3
"""Supply rejection and common-mode-dependent error of the buffer (Table VI).

Compares the original design (ideal CMFB amplifier E1), RAMP_LR (transistor CMFB)
and RAMP_LR with an ideal, slow CMFB amplifier in place of MC1/MC2/MPC1/MPC2.
Run sim/ramp_pvt.py first.  Output: sim/results/cmfb_experiment.csv
"""
import csv
import re
import subprocess
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
BUILD = REPO / "sim" / "build"
RES = REPO / "sim" / "results"


def deck(lib, dut, name):
    return f"""* {name}
.include {lib}
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
{dut}
V1 VICM GND dc 0.825
V2 VDD GND dc 1.65 ac 1
.control
set wr_singlescale
set wr_vecnames
op
let vos = v(out) - v(vicm)
print vos
ac dec 10 1 1e6
let psrr = -db(v(out))
print psrr[0]
dc V1 0.725 0.925 0.2
let err = v(out) - v(vicm)
print err
quit
.endc
.end
"""


def run(name, lib, dut):
    f = BUILD / f"cmfb_{name}.spice"
    f.write_text(deck(lib, dut, name))
    out = subprocess.run(["ngspice", "-b", str(f)], capture_output=True, text=True, cwd=BUILD).stdout
    vals = dict(re.findall(r"^(\S+) = ([-0-9.e+]+)", out, re.M))
    errs = [float(e) for e in re.findall(r"^\d+\s+[-0-9.e+]+\s+([-0-9.e+]+)", out, re.M)]
    gain_err = 100 * (errs[1] - errs[0]) / 0.2 if len(errs) == 2 else float("nan")
    return dict(design=name, psrr_dc_db=round(float(vals["psrr[0]"]), 1),
                offset_mv=round(1e3 * float(vals["vos"]), 3), gain_err_pct=round(gain_err, 3))


def main():
    lr = (BUILD / "lr_lib.spice").read_text()
    blk = re.search(r"^\.subckt STG1_LR .*?^\.ends", lr, re.M | re.S).group(0)
    ideal = re.sub(r"^XMC1 .*\n|^XMC2 .*\n|^XMPC1 .*\n|^XMPC2 .*\n", "", blk, flags=re.M)
    ideal = ideal.replace(".ends", "E1 ne GND net3 V1_CM 10k\nRcm ne vcmfb 1Meg\nCcm vcmfb GND 160n\n.ends")
    (BUILD / "lr_idealcmfb_lib.spice").write_text(lr.replace(blk, ideal))
    rows = [run("RAMP (original, ideal E1)", BUILD / "orig_lib.spice", "x1 VDD VICM out out GND RAMP"),
            run("RAMP_LR (transistor CMFB)", BUILD / "lr_lib.spice",
                "x1 VDD GND IBIAS VICM out out RAMP_LR\nI_B VDD IBIAS 1u"),
            run("RAMP_LR with ideal CMFB", BUILD / "lr_idealcmfb_lib.spice",
                "x1 VDD GND IBIAS VICM out out RAMP_LR\nI_B VDD IBIAS 1u")]
    with open(RES / "cmfb_experiment.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
