#!/usr/bin/env python3
"""PVT characterisation of the IHP SG13G2 ring amplifier.

Netlists the xschem testbench of the layout-ready design (RAMP-LR/tb_RAMP_LR.sch)
and builds two versions of the amplifier:

  reg : VCTRLP/VCTRLN come from the deadzone regulation loop (STG2_REPLICA_LR,
        the circuit of thesis Fig. 3.6)
  fix : the regulation loop is removed and VCTRLP/VCTRLN are held at the values
        the loop produces at TT, 27 degC, nominal VDD (thesis Table 3.1 setup)

For every (bias, corner, temperature, VDD) point one ngspice job runs
  * the operating point (output-stage quiescent current I_Q, control voltages,
    supply current),
  * the loop gain of the unity-gain buffer (Middlebrook double injection, as in
    RAMP-Test/RamP_tb1_CP_FB.sch),
  * the closed-loop supply rejection, and
  * a 200 mV up/down step response.
A DC temperature sweep is run for every corner and bias.  The original design
(RAMP-Test/RamP_tb1_CP_FB.sch, ideal bias sources) is also run at 27 degC, AC
only, as the reference point.

Results go to sim/results/; make_figures.py turns them into the figures.
Run from anywhere:  python3 sim/ramp_pvt.py   (needs xschem, ngspice, PDK_ROOT)
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

REPO = Path(__file__).resolve().parents[1]
RAMP_DIR = REPO / "Design Files" / "RAMP"
BUILD = REPO / "sim" / "build"
RESULTS = REPO / "sim" / "results"

TB_LR = RAMP_DIR / "RAMP-LR" / "tb_RAMP_LR.sch"
TB_ORIG = RAMP_DIR / "RAMP-Test" / "RamP_tb1_CP_FB.sch"
CORNERS = ["mos_tt", "mos_ss", "mos_ff", "mos_sf", "mos_fs"]
PASSIVE = {"mos_tt": ("res_typ", "cap_typ"), "mos_ss": ("res_wcs", "cap_wcs"),
           "mos_ff": ("res_bcs", "cap_bcs"), "mos_sf": ("res_typ", "cap_typ"),
           "mos_fs": ("res_typ", "cap_typ")}
TEMPS = [-40, 27, 125]
VDD0 = 1.65
VDDS = [1.5675, 1.65, 1.7325]          # nominal +- 5 %
VCM = 0.825
CLOAD = "50p"
IBIAS = "1u"
STEP = 0.2
T_EDGE, T_FALL, T_STOP = 100e-9, 600e-9, 1100e-9
# switched-capacitor (charge-transfer) amplifier test, as in thesis Fig. 2.2/3.4:
# inverting gain CS/CF = 1, inputs held at the virtual ground, CL = 50 pF
CS, CF = 5e-12, 5e-12
SC_EDGES = [(100e-9, +0.004, 2000e-9), (2100e-9, -0.004, 2000e-9),  # small steps first,
            (4100e-9, +0.2, 1000e-9), (5100e-9, -0.2, 1000e-9)]      # from a settled state
SC_STOP = 6100e-9


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def subckts(tb: Path) -> dict[str, str]:
    run(["xschem", "-n", "-q", "-x", "--rcfile", str(RAMP_DIR / "xschemrc"), "-o", str(BUILD), str(tb)])
    text = (BUILD / (tb.stem + ".spice")).read_text()
    return {b.split()[1]: b for b in re.findall(r"^\.subckt .*?^\.ends\s*$", text, flags=re.M | re.S)}


def netlist_library() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    lib = subckts(TB_LR)
    top = lib["RAMP_LR"]
    # 0-V source in the source of the output PMOS to measure I_Q (bulk stays at VDD)
    top = top.replace("XM2 Vout mp_dz VDD VDD", "VIQ VDD vdd_q 0\nXM2 Vout mp_dz vdd_q VDD")
    assert "VIQ" in top
    line = "x3 VDD VCTRLP V1_CM VCTRLN GND irn irp ipota inota STG2_REPLICA_LR"
    assert line in top, "regulation-loop instance not found"
    fixed = top.replace(".subckt RAMP_LR ", ".subckt RAMP_LR_FIXED ", 1).replace(
        line, "VCP VCTRLP GND {vcp_fix}\nVCN VCTRLN GND {vcn_fix}")
    pwr = top.replace(".subckt RAMP_LR ", ".subckt RAMP_LR_PWR ", 1)
    for inst in ("xb", "x1", "x4", "x2", "x3", "xd"):
        pwr = re.sub(rf"^{inst} VDD ", f"V_{inst} VDD vdd_{inst} 0\n{inst} vdd_{inst} ", pwr, count=1, flags=re.M)
    assert pwr.count("V_x") == 6, "block supplies not found"
    lib["RAMP_LR"], lib["RAMP_LR_FIXED"], lib["RAMP_LR_PWR"] = top, fixed, pwr
    (BUILD / "lr_lib.spice").write_text("* RAMP_LR sub-circuits netlisted by xschem\n" + "\n\n".join(lib.values()) + "\n")
    orig = subckts(TB_ORIG)
    orig["RAMP"] = orig["RAMP"].replace("XM2 Vout mp_dz VDD VDD", "VIQ VDD vdd_q 0\nXM2 Vout mp_dz vdd_q VDD")
    (BUILD / "orig_lib.spice").write_text("* original RAMP sub-circuits\n" + "\n\n".join(orig.values()) + "\n")


def models(corner):
    r, c = PASSIVE[corner]
    return (f".lib cornerMOSlv.lib {corner}\n.lib cornerMOShv.lib {corner}\n"
            f".lib cornerRES.lib {r}\n.lib cornerCAP.lib {c}\n")


CTRL_AC = """
ac dec 40 1 10G
alter @vprobe1[acmag]=0
alter @iprobe1[acmag]=1
ac dec 40 1 10G
let mb = 1/(ac1.v(probe) + ac2.i(vprobe2)) - 1
let mbr = real(mb)
let mbi = imag(mb)
wrdata {d}/loop.dat mbr mbi
"""


def ibias_src(ptat=False):
    """External reference: constant 1 uA, or PTAT (1 uA at 27 degC, ideal)."""
    return (f"B_B VDD IBIAS I={IBIAS.rstrip('u')}u*(temper+273.15)/300.15" if ptat
            else f"I_B VDD IBIAS {IBIAS}")


def testbench(name, sub, corner, temp, vdd, vcp=0.0, vcn=0.0, transient=True, orig=False, ptat=False):
    d = BUILD / name
    d.mkdir(parents=True, exist_ok=True)
    lo, hi = VCM - STEP / 2, VCM + STEP / 2
    pwl = f"pwl(0 {lo} {T_EDGE} {lo} {T_EDGE + 1e-9} {hi} {T_FALL} {hi} {T_FALL + 1e-9} {lo})"
    if orig:
        dut = "x1 VDD VICM out inp GND RAMP"
        lib, ops = "orig_lib.spice", "v(x1.net2) v(x1.net1)"
    else:
        dut = f"x1 VDD GND IBIAS VICM inp out {sub}\n{ibias_src(ptat)}"
        lib, ops = "lr_lib.spice", "v(x1.vctrlp) v(x1.vctrln)"
    tran = f"""
alter @vprobe1[acmag]=0
alter @v2[acmag]=0
dc V1 {lo} {hi} {STEP}
wrdata {d}/dc.dat v(out)
tran 0.2n {T_STOP} 0 0.5n
wrdata {d}/tran.dat v(out) v(vicm) v(x1.mp_dz) v(x1.mn_dz) i(v.x1.viq) i(v2)
""" if transient else ""
    psrr = f"""
alter @iprobe1[acmag]=0
alter @v2[acmag]=1
ac dec 40 1 10G
let psr = v(out)
let psrr_re = real(psr)
let psrr_im = imag(psr)
wrdata {d}/psrr.dat psrr_re psrr_im
""" if not orig else ""
    deck = f"""* {name}
.include {BUILD / lib}
{models(corner)}.param vcp_fix={vcp} vcn_fix={vcn}
.temp {temp}
{dut}
V1 VICM GND dc {VCM} ac 0 {pwl}
V2 VDD GND dc {vdd} ac 0
C1 out GND {CLOAD}
Vprobe2 probe inp 0
Vprobe1 probe out dc 0 ac 1
Iprobe1 GND probe dc 0 ac 0
.control
set wr_singlescale
set wr_vecnames
op
wrdata {d}/op.dat v(out) {ops} v(x1.mp_dz) v(x1.mn_dz) v(x1.vo_stg1) v(x1.v1_cm) i(v.x1.viq) i(v2)
{CTRL_AC.format(d=d)}{psrr}{tran}
quit
.endc
.end
"""
    f = d / "tb.spice"
    f.write_text(deck)
    return f


def sc_deck(name, sub, corner, temp, vdd, vcp, vcn, ptat=False):
    """Charge-transfer step response: the input common mode stays at VCM."""
    d = BUILD / name
    d.mkdir(parents=True, exist_ok=True)
    pts, v = [f"0 {VCM}"], VCM
    for t0, dv, _ in SC_EDGES:
        pts += [f"{t0} {v}", f"{t0 + 0.5e-9} {v + dv}"]
        v += dv
    deck = f"""* {name}: SC amplifier, gain -CS/CF
.include {BUILD / 'lr_lib.spice'}
{models(corner)}.param vcp_fix={vcp} vcn_fix={vcn}
.temp {temp}
x1 VDD GND IBIAS VCM vx out {sub}
{ibias_src(ptat)}
VCMS VCM GND dc {VCM}
VIN vin GND pwl({' '.join(pts)})
CS vin vx {CS}
CF vx out {CF}
RF vx out 1G
CL out GND {CLOAD}
V2 VDD GND dc {vdd}
.control
set wr_singlescale
set wr_vecnames
tran 0.2n {SC_STOP} 0 0.5n
wrdata {d}/sc.dat v(out) v(vin) v(vx) v(x1.mp_dz) v(x1.mn_dz) i(v.x1.viq) i(v2)
quit
.endc
.end
"""
    f = d / "tb.spice"
    f.write_text(deck)
    return f


def sc_metrics(d: Path) -> dict:
    """Error against the ideal charge transfer, v_before - (CS/CF)*dVin, per edge."""
    tr = read(d / "sc.dat")
    t, v = tr["time"], tr["v(out)"]
    res = {}
    for k, (t0, dv, win) in enumerate(SC_EDGES):
        tag = ("L" if abs(dv) > 0.01 else "S") + ("r" if dv > 0 else "f")
        step = CS / CF * abs(dv)
        target = np.interp(t0 - 1e-9, t, v) - CS / CF * dv
        m = (t >= t0) & (t <= t0 + win)
        tt, err = t[m], np.abs(v[m] - target) / step
        for tol, name in ((1e-2, "ts1"), (1e-3, "ts01")):
            out = np.where(err > tol)[0]
            res[f"sc_{name}_{tag}_ns"] = (np.nan if err[-1] > tol else
                                          0.0 if not len(out) else (tt[min(out[-1] + 1, len(tt) - 1)] - t0) * 1e9)
        res[f"sc_err250_{tag}_pct"] = 100 * abs(np.interp(t0 + 250e-9, t, v) - target) / step
        res[f"sc_errend_{tag}_pct"] = 100 * err[-1]
    return res


def temp_sweep_deck(name, sub, corner, vcp, vcn):
    d = BUILD / name
    d.mkdir(parents=True, exist_ok=True)
    deck = f"""* {name}: DC temperature sweep of the closed-loop buffer
.include {BUILD / 'lr_lib.spice'}
{models(corner)}.param vcp_fix={vcp} vcn_fix={vcn}
x1 VDD GND IBIAS VICM out out {sub}
I_B VDD IBIAS {IBIAS}
V1 VICM GND dc {VCM}
V2 VDD GND dc {VDD0}
.control
set wr_singlescale
set wr_vecnames
dc temp -40 125 5
wrdata {d}/tsweep.dat v(out) v(x1.vctrlp) v(x1.vctrln) v(x1.mp_dz) v(x1.mn_dz) i(v.x1.viq) i(v2)
quit
.endc
.end
"""
    f = d / "tb.spice"
    f.write_text(deck)
    return f


def power_deck():
    """Supply current of each block at TT, 27 degC, nominal VDD (closed loop, at rest)."""
    d = BUILD / "power_tt_27"
    d.mkdir(parents=True, exist_ok=True)
    blocks = " ".join(f"i(v.x1.v_{b})" for b in ("xb", "x1", "x4", "x2", "x3"))
    deck = f"""* supply current by block
.include {BUILD / 'lr_lib.spice'}
{models('mos_tt')}.temp 27
x1 VDD GND IBIAS VICM out out RAMP_LR_PWR
{ibias_src()}
V1 VICM GND dc {VCM}
V2 VDD GND dc {VDD0}
.control
set wr_singlescale
set wr_vecnames
op
wrdata {d}/power.dat {blocks} i(v.x1.viq) i(v2)
quit
.endc
.end
"""
    f = d / "tb.spice"
    f.write_text(deck)
    return f


def ngspice(deck: Path) -> bool:
    r = subprocess.run(["ngspice", "-b", deck.name], cwd=deck.parent, capture_output=True, text=True)
    (deck.parent / "ngspice.log").write_text(r.stdout + r.stderr)
    return r.returncode == 0 and "simulation(s) aborted" not in r.stdout + r.stderr


# --------------------------------------------------------------------------
def read(path: Path) -> dict[str, np.ndarray]:
    with open(path) as fh:
        names = fh.readline().split()
    data = np.loadtxt(path, skiprows=1, ndmin=2)
    return {n: data[:, i] for i, n in enumerate(names)}


def loop_metrics(d: Path) -> dict:
    lp = read(d / "loop.dat")
    f, t = lp["frequency"], lp["mbr"] + 1j * lp["mbi"]
    mag = 20 * np.log10(np.abs(t))
    ph = np.degrees(np.unwrap(np.angle(t)))
    ph -= 360 * np.round(ph[0] / 360)
    i = np.where((mag[:-1] >= 0) & (mag[1:] < 0))[0]
    res = dict(a0_db=mag[0], ugf_hz=np.nan, pm_deg=np.nan, gm_db=np.nan)
    if len(i):
        i = i[0]
        x = (0 - mag[i]) / (mag[i + 1] - mag[i])
        res["ugf_hz"] = 10 ** (np.log10(f[i]) + x * np.log10(f[i + 1] / f[i]))
        res["pm_deg"] = 180 + ph[i] + x * (ph[i + 1] - ph[i])
        j = np.where((ph[:-1] > -180) & (ph[1:] <= -180))[0]
        if len(j):
            j = j[0]
            y = (-180 - ph[j]) / (ph[j + 1] - ph[j])
            res["gm_db"] = -(mag[j] + y * (mag[j + 1] - mag[j]))
    if (d / "psrr.dat").exists():
        ps = read(d / "psrr.dat")
        a = np.abs(ps["psrr_re"] + 1j * ps["psrr_im"])
        res["psrr_dc_db"] = -20 * np.log10(a[0])
        res["psrr_1meg_db"] = -20 * np.log10(np.interp(1e6, ps["frequency"], a))
    return res


def settling(t, v, t0, t1, target, tol):
    """Time after t0 until |v - target| stays below tol*STEP (NaN if not settled by t1)."""
    m = (t >= t0) & (t <= t1)
    tt, err = t[m], np.abs(v[m] - target) / STEP
    if err[-1] > tol:
        return np.nan
    out = np.where(err > tol)[0]
    return 0.0 if not len(out) else tt[min(out[-1] + 1, len(tt) - 1)] - t0


def tran_metrics(d: Path) -> dict:
    """Settling is measured against the DC solution at the new input level, so a
    response that stops inside the deadzone counts as an error, not as settled."""
    tr, dc = read(d / "tran.dat"), read(d / "dc.dat")
    t, v = tr["time"], tr["v(out)"]
    v_lo, v_hi = dc["v(out)"][0], dc["v(out)"][-1]
    res = dict(dc_gain=(v_hi - v_lo) / STEP)
    for edge, (t0, t1, start, target) in {"rise": (T_EDGE, T_FALL, v_lo, v_hi),
                                          "fall": (T_FALL, T_STOP, v_hi, v_lo)}.items():
        res[f"ts1_{edge}_ns"] = settling(t, v, t0, t1, target, 1e-2) * 1e9
        res[f"ts01_{edge}_ns"] = settling(t, v, t0, t1, target, 1e-3) * 1e9
        res[f"err250_{edge}_pct"] = 100 * abs(np.interp(t0 + 250e-9, t, v) - target) / STEP
        m = (t >= t0) & (t <= t1)
        over = (v[m].max() - target) if target > start else (target - v[m].min())
        res[f"os_{edge}_pct"] = 100 * max(over, 0) / STEP
    q = (t > T_EDGE - 50e-9) & (t < T_EDGE)
    res["idle_ripple_mv"] = 1e3 * np.ptp(v[q])
    return res


def op_metrics(d: Path, orig=False) -> dict:
    op = read(d / "op.dat")
    g = lambda k: float(op[k][0])
    cp, cn = ("v(x1.net2)", "v(x1.net1)") if orig else ("v(x1.vctrlp)", "v(x1.vctrln)")
    return dict(vout=g("v(out)"), vctrlp=g(cp), vctrln=g(cn), vgp=g("v(x1.mp_dz)"), vgn=g("v(x1.mn_dz)"),
                vo1=g("v(x1.vo_stg1)"), vcm1=g("v(x1.v1_cm)"), iq_ua=1e6 * g("i(v.x1.viq)"),
                itot_ua=-1e6 * g("i(v2)"))


def save_resampled(src: Path, dst: Path, dt: float, drop=("i(v2)", "v(vx)")) -> None:
    """Keep the result files small: transient waveforms on a uniform grid."""
    d = read(src)
    names = [n for n in d if n not in drop]
    t = d[names[0]]
    tg = np.arange(t[0], t[-1], dt)
    cols = [tg] + [np.interp(tg, t, d[n]) for n in names[1:]]
    np.savetxt(dst, np.column_stack(cols), fmt="%.6g", header=" ".join(names), comments="")


def main() -> int:
    for tool in ("xschem", "ngspice"):
        if shutil.which(tool) is None:
            sys.exit(f"{tool} not found on PATH")
    if not os.environ.get("PDK_ROOT"):
        sys.exit("set PDK_ROOT to the directory that contains ihp-sg13g2")
    RESULTS.mkdir(parents=True, exist_ok=True)
    netlist_library()

    ref = testbench("reg_tt_27_1.65", "RAMP_LR", "mos_tt", 27, VDD0)
    assert ngspice(ref), f"reference run failed: {ref.parent / 'ngspice.log'}"
    op = op_metrics(ref.parent)
    vcp, vcn = round(op["vctrlp"], 5), round(op["vctrln"], 5)
    print(f"TT/27 degC/{VDD0} V regulated: VCTRLP={vcp} V VCTRLN={vcn} V I_Q={op['iq_ua']:.3f} uA")

    jobs = []
    for bias, sub in (("reg", "RAMP_LR"), ("fix", "RAMP_LR_FIXED")):
        for c in CORNERS:
            for t in TEMPS:
                for vdd in VDDS:
                    jobs.append(("lr", bias, c, t, vdd,
                                 testbench(f"{bias}_{c[4:]}_{t}_{vdd}", sub, c, t, vdd, vcp, vcn)))
            jobs.append(("tsweep", bias, c, None, VDD0, temp_sweep_deck(f"{bias}_{c[4:]}_tsweep", sub, c, vcp, vcn)))
    for bias, sub, ptat in (("reg", "RAMP_LR", False), ("fix", "RAMP_LR_FIXED", False), ("ptat", "RAMP_LR", True)):
        for c in CORNERS:
            for t in TEMPS:
                for vdd in (VDDS if bias != "ptat" else [VDD0]):
                    jobs.append(("sc", bias, c, t, vdd,
                                 sc_deck(f"sc_{bias}_{c[4:]}_{t}_{vdd}", sub, c, t, vdd, vcp, vcn, ptat)))
    # constant-gm style experiment: the same regulated design with a PTAT IBIAS
    for c in CORNERS:
        for t in TEMPS:
            jobs.append(("lr", "ptat", c, t, VDD0,
                         testbench(f"ptat_{c[4:]}_{t}_{VDD0}", "RAMP_LR", c, t, VDD0, ptat=True)))
    jobs.append(("power", "reg", "mos_tt", 27, VDD0, power_deck()))
    for c in CORNERS:
        jobs.append(("orig", "orig", c, 27, VDD0,
                     testbench(f"orig_{c[4:]}_27", "RAMP", c, 27, VDD0, transient=False, orig=True)))
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
        ok = list(ex.map(lambda j: ngspice(j[5]), jobs))
    failed = [j for j, k in zip(jobs, ok) if not k]
    for j in failed:
        print(f"ngspice did not converge: {j[5].parent.name} (see {j[5].parent / 'ngspice.log'})")
    # the layout-ready design must simulate everywhere; the original may not
    assert all(j[0] == "orig" for j in failed), "RAMP_LR simulation failed"
    jobs = [j for j, k in zip(jobs, ok) if k]

    sc = {(b, c[4:].upper(), t, v): sc_metrics(dk.parent) for k, b, c, t, v, dk in jobs if k == "sc"}
    rows = []
    for kind, bias, c, t, vdd, deck in jobs:
        if kind in ("tsweep", "power", "sc"):
            continue
        d = deck.parent
        row = dict(design="RAMP" if kind == "orig" else "RAMP_LR", bias=bias,
                   corner=c[4:].upper(), temp_c=t, vdd=vdd)
        row.update(op_metrics(d, orig=kind == "orig"))
        row.update(loop_metrics(d))
        if kind == "lr":
            row.update(tran_metrics(d))
            row.update(sc[(bias, row["corner"], t, vdd)])
        rows.append(row)
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(RESULTS / "pvt_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    for kind, bias, c, t, vdd, deck in jobs:
        d, tag = deck.parent, f"{bias}_{c[4:]}"
        if kind == "tsweep":
            shutil.copy(d / "tsweep.dat", RESULTS / f"tsweep_{tag}.dat")
        elif kind == "lr" and vdd == VDD0 and t in (27,):
            for k in ("loop", "psrr"):
                shutil.copy(d / f"{k}.dat", RESULTS / f"{k}_{tag}_{t}.dat")
            save_resampled(d / "tran.dat", RESULTS / f"tran_{tag}_{t}.dat", 0.5e-9)
        elif kind == "orig":
            shutil.copy(d / "loop.dat", RESULTS / f"loop_orig_{c[4:]}_27.dat")
        elif kind == "sc" and vdd == VDD0 and bias != "ptat" and (
                t == 27 or (c[4:], t) in (("ss", -40), ("sf", -40), ("ff", 125))):
            save_resampled(d / "sc.dat", RESULTS / f"sc_{tag}_{t}.dat", 2e-9)
        elif kind == "power":
            shutil.copy(d / "power.dat", RESULTS / "power_tt_27.dat")
    (RESULTS / "fixed_bias.txt").write_text(
        f"VCTRLP_fixed={vcp}\nVCTRLN_fixed={vcn}\n"
        + "".join(f"no_convergence={j[5].parent.name}\n" for j in failed))

    print(f"{'design':8} {'bias':4} {'corner':6} {'T':>4} {'VDD':>6} {'I_Q/uA':>7} {'A0/dB':>6} "
          f"{'UGF/MHz':>8} {'PM/deg':>7} {'SC ts0.1% L/S ns':>17} {'SC err@250 L/S %':>17}")
    for r in rows:
        if r["vdd"] == VDD0:
            print(f"{r['design']:8} {r['bias']:4} {r['corner']:6} {r['temp_c']:4} {r['vdd']:6} "
                  f"{r['iq_ua']:7.2f} {r['a0_db']:6.1f} {r['ugf_hz'] / 1e6:8.2f} {r['pm_deg']:7.1f} "
                  f"{r.get('sc_ts01_Lr_ns', float('nan')):8.1f} {r.get('sc_ts01_Sr_ns', float('nan')):8.1f} "
                  f"{r.get('sc_err250_Lr_pct', float('nan')):8.3f} {r.get('sc_err250_Sr_pct', float('nan')):8.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
