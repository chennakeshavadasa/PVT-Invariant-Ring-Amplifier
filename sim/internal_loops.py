#!/usr/bin/env python3
"""Loop gain of the internal loops (deadzone regulation, CMFB) of both designs.

Each loop is broken with the same double (voltage + current) injection that the
testbench uses for the main loop.  Run sim/ramp_pvt.py first (it writes the
netlists to sim/build).  Output: sim/results/internal_loops.csv
"""
import csv
import re
import subprocess
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
BUILD = REPO / "sim" / "build"
RES = REPO / "sim" / "results"
PROBE = "Vpb2 prb {load} 0\nVpb1 prb {drive} dc 0 ac 1\nIpb1 GND prb dc 0 ac 0"

# (design, loop, netlist, subckt, [(old, new), ...], driving node, loaded node)
CASES = [
    ("RAMP (original)", "regulation V_CTRLN", "orig", "STG2_Replica",
     [("x2 VDD VCTRLN net4 net6 GND NOTA", "x2 VDD amp_o net4 net6 GND NOTA")], "amp_o", "VCTRLN"),
    ("RAMP (original)", "regulation V_CTRLP", "orig", "STG2_Replica",
     [("x1 VDD net1 net5 VCTRLP GND POTA", "x1 VDD net1 net5 amp_o GND POTA")], "amp_o", "VCTRLP"),
    ("RAMP (original)", "stage-1 CMFB (ideal E1)", "orig", "STG1",
     [("E1 net1 GND net3 V1_CM 10k", "E1 amp_o GND net3 V1_CM 10k")], "amp_o", "net1"),
    ("RAMP_LR", "regulation V_CTRLN", "lr", "STG2_REPLICA_LR",
     [("x2 VDD VCTRLN net4 irn GND inota NOTA_LR", "x2 VDD amp_o net4 irn GND inota NOTA_LR")], "amp_o", "VCTRLN"),
    ("RAMP_LR", "regulation V_CTRLP", "lr", "STG2_REPLICA_LR",
     [("x1 VDD net1 irp VCTRLP GND ipota POTA_LR", "x1 VDD net1 irp amp_o GND ipota POTA_LR")], "amp_o", "VCTRLP"),
    ("RAMP_LR", "stage-1 CMFB (transistor)", "lr", "STG1_LR",
     [("XMP1 net2 vcmfb VDD VDD", "XMP1 net2 vg VDD VDD"), ("XMP2 Vo1 vcmfb VDD VDD", "XMP2 Vo1 vg VDD VDD")],
     "vcmfb", "vg"),
]
INST = {"STG2_Replica": "x3", "STG1": "x1", "STG2_REPLICA_LR": "x3", "STG1_LR": "x1"}


def loop(case, corner):
    design, name, which, sub, edits, drive, load = case
    lib = (BUILD / f"{which}_lib.spice").read_text()
    blk = re.search(rf"^\.subckt {sub} .*?^\.ends", lib, re.M | re.S).group(0)
    blk2 = blk
    for old, new in edits:
        assert old in blk2, (name, old)
        blk2 = blk2.replace(old, new)
    blk2 = blk2.replace(".ends", PROBE.format(drive=drive, load=load) + "\n.ends")
    lib = lib.replace(blk, blk2)
    (BUILD / "il_lib.spice").write_text(lib)
    inst = f"x1.{INST[sub]}"
    if which == "orig":
        dut = "x1 VDD VICM out out GND RAMP"
    else:
        dut = "x1 VDD GND IBIAS VICM out out RAMP_LR\nI_B VDD IBIAS 1u"
    passive = {"mos_tt": "typ", "mos_ss": "wcs", "mos_ff": "bcs"}[corner]
    (BUILD / "il.spice").write_text(f"""* internal loop
.include {BUILD / 'il_lib.spice'}
.lib cornerMOSlv.lib {corner}
.lib cornerMOShv.lib {corner}
.lib cornerRES.lib res_{passive}
.lib cornerCAP.lib cap_{passive}
{dut}
V1 VICM GND dc 0.825
V2 VDD GND dc 1.65
C1 out GND 50p
.control
set wr_singlescale
set wr_vecnames
ac dec 40 1 100G
alter @v.{inst}.vpb1[acmag]=0
alter @i.{inst}.ipb1[acmag]=1
ac dec 40 1 100G
let mb = 1/(ac1.v({inst}.prb) + ac2.i(v.{inst}.vpb2)) - 1
let mbr = real(mb)
let mbi = imag(mb)
wrdata {BUILD / 'il.dat'} mbr mbi
quit
.endc
.end
""")
    (BUILD / "il.dat").unlink(missing_ok=True)
    subprocess.run(["ngspice", "-b", str(BUILD / "il.spice")], capture_output=True, cwd=BUILD)
    if not (BUILD / "il.dat").exists():
        return np.nan, np.nan, np.nan, np.nan          # no operating point
    d = np.loadtxt(BUILD / "il.dat", skiprows=1)
    f, t = d[:, 0], d[:, 1] + 1j * d[:, 2]
    mag = 20 * np.log10(np.abs(t))
    ph = np.degrees(np.unwrap(np.angle(t)))
    ph -= 360 * np.round(ph[0] / 360)
    i = np.where((mag[:-1] >= 0) & (mag[1:] < 0))[0]
    if not len(i):
        return mag[0], np.nan, np.nan, mag[-1]
    return mag[0], f[i[0]], 180 + ph[i[0]], np.nan


def main():
    rows = []
    for case in CASES:
        for corner in ("mos_tt", "mos_ss", "mos_ff"):
            a0, ugf, pm, mag_end = loop(case, corner)
            rows.append(dict(design=case[0], loop=case[1], corner=corner[4:].upper(),
                             a0_db=round(a0, 1) if a0 == a0 else "no OP",
                             ugf_mhz=round(ugf / 1e6, 2) if ugf == ugf else "", pm_deg=round(pm, 1) if pm == pm else "",
                             gain_at_100GHz_db=round(mag_end, 1) if mag_end == mag_end else ""))
            print(rows[-1])
    with open(RES / "internal_loops.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
