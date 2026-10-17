#!/usr/bin/env python3
"""PVT characterisation of RAMP_V2 (the redesigned ring amplifier).

Netlists the xschem testbench Design Files/RAMP/RAMP-V2/tb_RAMP_V2.sch and runs, for
every corner (TT, SS, FF, SF, FS), temperature (-40, 27, 125 degC) and supply
(1.65 V +- 5 %):
  * the operating point (I_Q, VCTRLN, servo output, supply current),
  * the loop gain of the unity-gain buffer (Middlebrook double injection) and the
    closed-loop supply rejection,
  * a 200-mV up/down buffer step (0.725 <-> 0.925 V),
  * the switched-capacitor charge-transfer test of ramp_pvt.py (4-mV and 200-mV steps,
    input common mode held at VCM),
  * a limit-cycle test: buffer steps of +-10 ... +-200 mV, 500 ns each.
plus a DC temperature sweep per corner, the supply current by block, and a power-up
transient (the slow loops settle in about 1 ms).

The reference current is the constant-gm reference of the design (ideal): I_BIAS =
1 uA x T/300.15 K x R0/R, R a dummy rhigh at the same corner.
Results: sim/results/v2/.  Usage: python3 sim/v2_sim.py
"""
from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ramp_pvt as rp  # noqa: E402

BUILD = rp.BUILD / "v2"
RESULTS = rp.RESULTS / "v2"
TB = rp.RAMP_DIR / "RAMP-V2" / "tb_RAMP_V2.sch"
LIB = BUILD / "v2_lib.spice"
SUB = "RAMP_V2"
BLOCKS = ("xb", "x1", "xt", "x2", "xr", "xs")
REF = {"cgm": ("XRREF rref1 GND GND rhigh w=0.5e-6 l=33.7e-6 m=1 b=0\nVRREF rref1 GND 1\n"
               "B_B VDD IBIAS I=1u*(temper+273.15)/300.15*1e5*abs(i(VRREF))"),
       "const": "I_B VDD IBIAS 1u"}
NODESET = ".nodeset v(x1.vctrln)=0.6 v(x1.vo_stg1)=0.72 v(x1.vo1n)=0.72 v(out)=0.825"
OPS = ("v(out) v(x1.vctrlp) v(x1.vctrln) v(x1.mp_dz) v(x1.mn_dz) v(x1.vo_stg1) v(x1.vo1n) v(x1.v1_cm) "
       "v(x1.vtrip) v(x1.xs.vsv) i(v.x1.viq) i(v2)")
LC_STEPS = [0.01, -0.01, 0.02, -0.02, 0.05, -0.05, 0.1, -0.1, 0.2, -0.2]
LC_SEG = 500e-9
STARTUP = [("mos_tt", 27), ("mos_ss", -40), ("mos_sf", -40), ("mos_ff", 125), ("mos_fs", 125)]


def netlist_library() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    rp.run(["xschem", "-n", "-q", "-x", "--rcfile", str(rp.RAMP_DIR / "xschemrc"), "-o", str(BUILD), str(TB)])
    text = (BUILD / (TB.stem + ".spice")).read_text()
    lib = {b.split()[1]: b for b in re.findall(r"^\.subckt .*?^\.ends\s*$", text, flags=re.M | re.S)}
    top = lib[SUB]
    # 0-V source in the source of the output PMOS to measure I_Q (bulk stays at VDD)
    top = top.replace("XM2 Vout mp_dz VDD VDD", "VIQ VDD vdd_q 0\nXM2 Vout mp_dz vdd_q VDD")
    assert "VIQ" in top
    pwr = top.replace(f".subckt {SUB} ", f".subckt {SUB}_PWR ", 1)
    for inst in BLOCKS:
        pwr = re.sub(rf"^{inst} VDD ", f"V_{inst} VDD vdd_{inst} 0\n{inst} vdd_{inst} ", pwr, count=1, flags=re.M)
    assert pwr.count("V_x") == len(BLOCKS), "block supplies not found"
    lib[SUB], lib[SUB + "_PWR"] = top, pwr
    LIB.write_text("* RAMP_V2 sub-circuits netlisted by xschem\n" + "\n\n".join(lib.values()) + "\n")


def _deck(d: Path, body: str, control: str, corner, temp, netlib=None, modeltext=None, seed=None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    f = d / "tb.spice"
    f.write_text(f"""* {d.name}
{f'.options seed={seed}' if seed else ''}
.include {netlib or LIB}
{modeltext or rp.models(corner)}.temp {temp}
{body}
{NODESET}
.control
set wr_singlescale
set wr_vecnames
{control}
quit
.endc
.end
""")
    return f


def testbench(name, corner, temp, vdd, sub=SUB, ref="cgm", transient=True, psrr=True, build=None, **kw):
    d = (build or BUILD) / name
    lo, hi = rp.VCM - rp.STEP / 2, rp.VCM + rp.STEP / 2
    pwl = (f"pwl(0 {lo} {rp.T_EDGE} {lo} {rp.T_EDGE + 1e-9} {hi} {rp.T_FALL} {hi} "
           f"{rp.T_FALL + 1e-9} {lo})")
    body = f"""x1 VDD GND IBIAS VICM inp out {sub}
{REF[ref]}
V1 VICM GND dc {rp.VCM} ac 0 {pwl}
V2 VDD GND dc {vdd} ac 0
C1 out GND {rp.CLOAD}
Vprobe2 probe inp 0
Vprobe1 probe out dc 0 ac 1
Iprobe1 GND probe dc 0 ac 0"""
    ctl = f"op\nwrdata {d}/op.dat {OPS}\n" + rp.CTRL_AC.format(d=d)
    if psrr:
        ctl += f"""alter @iprobe1[acmag]=0
alter @v2[acmag]=1
ac dec 40 1 10G
let psr = v(out)
let psrr_re = real(psr)
let psrr_im = imag(psr)
wrdata {d}/psrr.dat psrr_re psrr_im
"""
    if transient:
        ctl += f"""alter @vprobe1[acmag]=0
alter @v2[acmag]=0
dc V1 {lo} {hi} {rp.STEP}
wrdata {d}/dc.dat v(out)
tran 0.2n {rp.T_STOP} 0 0.5n
wrdata {d}/tran.dat v(out) v(vicm) v(x1.mp_dz) v(x1.mn_dz) i(v.x1.viq) i(v2)
"""
    return _deck(d, body, ctl, corner, temp, **kw)


def sc_deck(name, corner, temp, vdd, sub=SUB, ref="cgm", build=None, **kw):
    d = (build or BUILD) / name
    pts, v = [f"0 {rp.VCM}"], rp.VCM
    for t0, dv, _ in rp.SC_EDGES:
        pts += [f"{t0} {v}", f"{t0 + 0.5e-9} {v + dv}"]
        v += dv
    body = f"""x1 VDD GND IBIAS VCM vx out {sub}
{REF[ref]}
VCMS VCM GND dc {rp.VCM}
VIN vin GND pwl({' '.join(pts)})
CS vin vx {rp.CS}
CF vx out {rp.CF}
RF vx out 1G
CL out GND {rp.CLOAD}
V2 VDD GND dc {vdd}"""
    ctl = (f"tran 0.2n {rp.SC_STOP} 0 0.5n\n"
           f"wrdata {d}/sc.dat v(out) v(vin) v(vx) v(x1.mp_dz) v(x1.mn_dz) v(x1.vctrln) i(v.x1.viq) i(v2)")
    return _deck(d, body, ctl, corner, temp, **kw)


def lc_deck(name, corner, temp, vdd, sub=SUB, ref="cgm", build=None, **kw):
    d = (build or BUILD) / name
    v, pts, t0 = rp.VCM, [f"0 {rp.VCM}"], 100e-9
    for s in LC_STEPS:
        pts += [f"{t0:.4g} {v:.4f}", f"{t0 + 1e-9:.4g} {v + s:.4f}"]
        v += s
        t0 += LC_SEG
    body = f"""x1 VDD GND IBIAS VICM out out {sub}
{REF[ref]}
V1 VICM GND pwl({' '.join(pts)})
V2 VDD GND dc {vdd}
C1 out GND {rp.CLOAD}"""
    ctl = f"tran 0.1n {100e-9 + LC_SEG * len(LC_STEPS):.4g} 0 0.25n\nwrdata {d}/lc.dat v(out) v(vicm)"
    return _deck(d, body, ctl, corner, temp, **kw)


def tsweep_deck(name, corner):
    d = BUILD / name
    body = f"""x1 VDD GND IBIAS VICM out out {SUB}
{REF['cgm']}
V1 VICM GND dc {rp.VCM}
V2 VDD GND dc {rp.VDD0}"""
    ctl = (f"dc temp -40 125 5\nwrdata {d}/tsweep.dat v(out) v(x1.vctrlp) v(x1.vctrln) v(x1.mp_dz) v(x1.mn_dz) "
           f"v(x1.v1_cm) v(x1.xs.vsv) i(v.x1.viq) i(v2) i(vrref)")
    return _deck(d, body, ctl, corner, 27)


def power_deck():
    d = BUILD / "power_tt_27"
    body = f"""x1 VDD GND IBIAS VICM out out {SUB}_PWR
{REF['cgm']}
V1 VICM GND dc {rp.VCM}
V2 VDD GND dc {rp.VDD0}"""
    blocks = " ".join(f"i(v.x1.v_{b})" for b in BLOCKS)
    return _deck(d, body, f"op\nwrdata {d}/power.dat {blocks} i(v.x1.viq) i(v2) i(vrref)", "mos_tt", 27)


def startup_deck(corner, temp, stop="3m"):
    d = BUILD / f"startup_{corner[4:]}_{temp}"
    body = f"""x1 VDD GND IBIAS VICM out out {SUB}
{REF['cgm']}
V1 VICM GND dc {rp.VCM}
V2 VDD GND pwl(0 0 1u {rp.VDD0})
C1 out GND {rp.CLOAD}"""
    ctl = (f"tran 10n {stop} 0 50n uic\n"
           f"wrdata {d}/su.dat v(out) v(x1.vctrln) v(x1.v1_cm) v(x1.xs.vsv) i(v.x1.viq) v(x1.mp_dz) v(x1.mn_dz)")
    return _deck(d, body, ctl, corner, temp)


# --------------------------------------------------------------------------
def op_metrics(d: Path) -> dict:
    op = rp.read(d / "op.dat")
    g = lambda k: float(op[k][0])
    return dict(vout=g("v(out)"), offset_mv=1e3 * (g("v(out)") - rp.VCM), vctrlp=g("v(x1.vctrlp)"),
                vctrln=g("v(x1.vctrln)"), vgp=g("v(x1.mp_dz)"), vgn=g("v(x1.mn_dz)"), vo1=g("v(x1.vo_stg1)"),
                vo1n=g("v(x1.vo1n)"), vcm1=g("v(x1.v1_cm)"), vtrip=g("v(x1.vtrip)"), vsv=g("v(x1.xs.vsv)"),
                iq_ua=1e6 * g("i(v.x1.viq)"), itot_ua=-1e6 * g("i(v2)"))


def step_metrics(d: Path) -> dict:
    """Buffer step: settling to the value the output reaches at the end of each edge
    (the slow loops are frozen on this time scale), and the remaining difference from the
    DC solution at the new input level - the transient common-mode error that the servo
    removes in about 1 ms."""
    tr, dc = rp.read(d / "tran.dat"), rp.read(d / "dc.dat")
    t, v = tr["time"], tr["v(out)"]
    res = {}
    for edge, (t0, t1, k) in {"rise": (rp.T_EDGE, rp.T_FALL, -1), "fall": (rp.T_FALL, rp.T_STOP, 0)}.items():
        fin = np.interp(t1 - 2e-9, t, v)
        res[f"ts1_{edge}_ns"] = rp.settling(t, v, t0, t1 - 2e-9, fin, 1e-2) * 1e9
        res[f"ts01_{edge}_ns"] = rp.settling(t, v, t0, t1 - 2e-9, fin, 1e-3) * 1e9
        res[f"cmerr_{edge}_mv"] = 1e3 * (fin - dc["v(out)"][k])
        m = (t >= t0) & (t <= t1)
        start = np.interp(t0 - 1e-9, t, v)
        over = (v[m].max() - fin) if fin > start else (fin - v[m].min())
        res[f"os_{edge}_pct"] = 100 * max(over, 0) / rp.STEP
    q = (t > rp.T_EDGE - 50e-9) & (t < rp.T_EDGE)
    res["idle_ripple_mv"] = 1e3 * np.ptp(v[q])
    return res


def lc_metrics(d: Path) -> dict:
    """Ripple (peak-to-peak, last 100 ns of each 500-ns step) and 1 % settling to the
    step's own final value; the largest over all steps."""
    r = rp.read(d / "lc.dat")
    t, v = r["time"], r["v(out)"]
    ripple, ts = [], []
    for k, s in enumerate(LC_STEPS):
        t1 = 100e-9 + (k + 1) * LC_SEG
        m = (t > t1 - 100e-9) & (t < t1 - 1e-9)
        ripple.append(1e3 * np.ptp(v[m]))
        fin = np.interp(t1 - 2e-9, t, v)
        m2 = (t > t1 - LC_SEG + 1e-9) & (t < t1 - 1e-9)
        bad = np.where(np.abs(v[m2] - fin) > 1e-2 * abs(s))[0]
        ts.append((t[m2][bad[-1]] - (t1 - LC_SEG)) * 1e9 if len(bad) else 0.0)
    return dict(lc_ripple_mv=max(ripple), lc_ts1_max_ns=max(ts))


def run_all(decks, workers=None):
    with ThreadPoolExecutor(max_workers=workers or max(1, (os.cpu_count() or 2) - 1)) as ex:
        return list(ex.map(rp.ngspice, decks))


def main() -> int:
    for tool in ("xschem", "ngspice"):
        if shutil.which(tool) is None:
            sys.exit(f"{tool} not found on PATH")
    RESULTS.mkdir(parents=True, exist_ok=True)
    netlist_library()
    jobs = []
    for c in rp.CORNERS:
        for t in rp.TEMPS:
            for vdd in rp.VDDS:
                tag = f"{c[4:]}_{t}_{vdd}"
                jobs += [("tb", c, t, vdd, testbench(f"tb_{tag}", c, t, vdd)),
                         ("sc", c, t, vdd, sc_deck(f"sc_{tag}", c, t, vdd)),
                         ("lc", c, t, vdd, lc_deck(f"lc_{tag}", c, t, vdd))]
        jobs.append(("tsweep", c, None, rp.VDD0, tsweep_deck(f"tsweep_{c[4:]}", c)))
    jobs.append(("power", "mos_tt", 27, rp.VDD0, power_deck()))
    jobs += [("startup", c, t, rp.VDD0, startup_deck(c, t)) for c, t in STARTUP]
    ok = run_all([j[4] for j in jobs])
    failed = [j[4].parent.name for j, k in zip(jobs, ok) if not k]
    for n in failed:
        print("ngspice failed:", n)
    res = {}
    for (kind, c, t, vdd, deck), k in zip(jobs, ok):
        if k and kind in ("tb", "sc", "lc"):
            d = deck.parent
            m = {"tb": lambda: {**op_metrics(d), **rp.loop_metrics(d), **step_metrics(d)},
                 "sc": lambda: rp.sc_metrics(d), "lc": lambda: lc_metrics(d)}[kind]()
            res.setdefault((c, t, vdd), {}).update(m)
    rows = [dict(corner=c[4:].upper(), temp_c=t, vdd=vdd, **r) for (c, t, vdd), r in res.items()]
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(RESULTS / "pvt_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    for (kind, c, t, vdd, deck), k in zip(jobs, ok):
        if not k:
            continue
        d, tag = deck.parent, f"{c[4:]}_{t}"
        if kind == "tb" and vdd == rp.VDD0:
            shutil.copy(d / "loop.dat", RESULTS / f"loop_{tag}.dat")
            shutil.copy(d / "psrr.dat", RESULTS / f"psrr_{tag}.dat")
            rp.save_resampled(d / "tran.dat", RESULTS / f"tran_{tag}.dat", 0.5e-9)
        elif kind == "sc" and vdd == rp.VDD0:
            rp.save_resampled(d / "sc.dat", RESULTS / f"sc_{tag}.dat", 2e-9,
                              keep=("time", "v(out)", "v(x1.vctrln)"), fmt="%.9g")
        elif kind == "lc" and vdd == rp.VDD0:
            rp.save_resampled(d / "lc.dat", RESULTS / f"lc_{tag}.dat", 0.5e-9, drop=(), fmt="%.7g")
        elif kind == "tsweep":
            shutil.copy(d / "tsweep.dat", RESULTS / f"tsweep_{c[4:]}.dat")
        elif kind == "power":
            shutil.copy(d / "power.dat", RESULTS / "power_tt_27.dat")
        elif kind == "startup":
            rp.save_resampled(d / "su.dat", RESULTS / f"startup_{tag}.dat", 1e-6, drop=(), fmt="%.7g")
    (RESULTS / "failed.txt").write_text("".join(n + "\n" for n in failed))
    nom = [r for r in rows if r["vdd"] == rp.VDD0]
    print(f"{'corner':6} {'T':>4} {'I_Q':>6} {'UGF':>6} {'PM':>5} {'GM':>5} {'off/mV':>7} {'ts01':>5} "
          f"{'SC L err250 %':>13} {'ripple/mV':>9}")
    for r in sorted(nom, key=lambda r: (r["corner"], r["temp_c"])):
        print(f"{r['corner']:6} {r['temp_c']:4} {r['iq_ua']:6.2f} {r['ugf_hz'] / 1e6:6.1f} {r['pm_deg']:5.1f} "
              f"{r['gm_db']:5.1f} {r['offset_mv']:7.2f} {np.nanmax([r['ts01_rise_ns'], r['ts01_fall_ns']]):5.0f} "
              f"{r['sc_err250_Lr_pct']:13.3f} {r['lc_ripple_mv']:9.4f}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
