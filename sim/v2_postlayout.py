#!/usr/bin/env python3
"""Schematic versus post-layout simulation of RAMP_V2 (1.65 V, constant-gm reference).

The post-layout view is magic's extraction of layout/RAMP_V2.gds (TOP=RAMP_V2 layout/run_pex.sh),
turned into the sub-circuit RAMP_V2_PEX by postlayout.pex_library (same ports as the schematic,
the I_Q ammeter VIQ in the source of the four MP3 fingers, 1 TOhm on capacitor-only nodes).
Both views run the testbenches of sim/v2_sim.py (operating point, loop gain, supply rejection,
buffer step, SC test, limit-cycle steps) at the five corners and -40/27/125 degC.
A sensitivity run removes the parasitics of one net group at a time (TT/27 and SS/-40 degC).

Run sim/v2_sim.py and the extraction first.
Output: sim/results/v2/postlayout_summary.csv, postlayout_sensitivity.csv and the post-layout
waveforms sim/results/v2/{loop,psrr,tran,sc,lc}_pex_<corner>_<T>.dat.
"""
import csv
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import postlayout as pl  # noqa: E402
import ramp_pvt as rp  # noqa: E402
import v2_sim as v2  # noqa: E402

PEX = rp.REPO / "layout" / "pex" / "RAMP_V2_pex.spice"
OUT = v2.BUILD / "postlayout"
SENS = {"all parasitics removed": None, "Vo_STG1, Vo1n (stage-1 outputs)": {"Vo_STG1", "Vo1n"},
        "mp_dz, mn_dz (stage-2 outputs)": {"mp_dz", "mn_dz"}, "VCTRLP, VCTRLN": {"VCTRLP", "VCTRLN"},
        "integrator MIM nets": {"xr.o1", "xr.z", "xs.o1", "xs.z"}, "Vout": {"Vout"}}


def sensitivity(pexlib: Path) -> list:
    src = pexlib.read_text()
    i = src.index(".subckt RAMP_V2_PEX")
    cells, top = src[:i], src[i:]
    jobs = []
    for k, (label, nets) in enumerate(SENS.items()):
        if nets is None:
            text = re.sub(r"^C\d+ .*\n", "", cells, flags=re.M) + re.sub(r"^C\S* .*\n", "", top, flags=re.M)
        else:
            text = cells + "".join(l for l in top.splitlines(True)
                                   if not (l.startswith("C") and set(l.split()[1:3]) & nets))
        lib = OUT / f"pex_sens{k}.spice"
        lib.write_text(text)
        for c, t in (("mos_tt", 27), ("mos_ss", -40)):
            jobs.append((label, c, t, v2.testbench(f"sens{k}_{c[4:]}_{t}", c, t, rp.VDD0, sub="RAMP_V2_PEX",
                                                   transient=False, psrr=False, netlib=lib, build=OUT)))
    ok = v2.run_all([j[3] for j in jobs])
    assert all(ok)
    return [dict(removed=label, corner=c[4:].upper(), temp_c=t, **rp.loop_metrics(d.parent))
            for label, c, t, d in jobs]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if not v2.LIB.exists():
        v2.netlist_library()
    pexlib = pl.pex_library(PEX, "RAMP_V2", OUT)
    views = {"sch": ("RAMP_V2", None), "pex": ("RAMP_V2_PEX", pexlib)}
    jobs = []
    for view, (sub, lib) in views.items():
        for c in rp.CORNERS:
            for t in rp.TEMPS:
                tag = f"{view}_{c[4:]}_{t}"
                kw = dict(sub=sub, netlib=lib, build=OUT)
                jobs += [(view, c, t, "tb", v2.testbench(tag, c, t, rp.VDD0, **kw)),
                         (view, c, t, "sc", v2.sc_deck("sc_" + tag, c, t, rp.VDD0, **kw)),
                         (view, c, t, "lc", v2.lc_deck("lc_" + tag, c, t, rp.VDD0, **kw))]
    ok = v2.run_all([j[4] for j in jobs])
    bad = [j[4].parent.name for j, k in zip(jobs, ok) if not k]
    assert not bad, f"ngspice failed: {bad}"
    rows = {}
    for view, c, t, kind, deck in jobs:
        d = deck.parent
        row = rows.setdefault((view, c, t), dict(view=view, corner=c[4:].upper(), temp_c=t, vdd=rp.VDD0))
        tag = f"pex_{c[4:]}_{t}"
        if kind == "tb":
            row.update(v2.op_metrics(d))
            row.update(rp.loop_metrics(d))
            row.update(v2.step_metrics(d))
            if view == "pex":
                shutil.copy(d / "loop.dat", v2.RESULTS / f"loop_{tag}.dat")
                shutil.copy(d / "psrr.dat", v2.RESULTS / f"psrr_{tag}.dat")
                rp.save_resampled(d / "tran.dat", v2.RESULTS / f"tran_{tag}.dat", 0.5e-9)
        elif kind == "sc":
            row.update(rp.sc_metrics(d))
            if view == "pex":
                rp.save_resampled(d / "sc.dat", v2.RESULTS / f"sc_{tag}.dat", 2e-9,
                                  keep=("time", "v(out)", "v(x1.vctrln)"), fmt="%.9g")
        else:
            row.update(v2.lc_metrics(d))
            if view == "pex":
                rp.save_resampled(d / "lc.dat", v2.RESULTS / f"lc_{tag}.dat", 0.5e-9, drop=(), fmt="%.7g")
    rows = list(rows.values())
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(v2.RESULTS / "postlayout_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    sens = sensitivity(pexlib)
    with open(v2.RESULTS / "postlayout_sensitivity.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sens[0]))
        w.writeheader()
        for r in sens:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    for r in sens:
        print(f"parasitics of {r['removed']:32s} removed, {r['corner']} {r['temp_c']:4}: "
              f"UGF {r['ugf_hz'] / 1e6:6.2f} MHz, PM {r['pm_deg']:5.1f} deg, GM {r['gm_db']:5.1f} dB")
    print(f"{'corner':6} {'T':>4}  {'I_Q sch/pex':>13} {'UGF sch/pex':>13} {'PM sch/pex':>12} {'GM sch/pex':>12} "
          f"{'ts0.1% sch/pex':>15} {'SC L err250 %':>15} {'ripple uV':>11}")
    for c in rp.CORNERS:
        for t in rp.TEMPS:
            a, b = (next(r for r in rows if r["view"] == v and r["corner"] == c[4:].upper() and r["temp_c"] == t)
                    for v in ("sch", "pex"))
            print(f"{c[4:]:6} {t:4}  {a['iq_ua']:5.2f}/{b['iq_ua']:<6.2f} {a['ugf_hz'] / 1e6:5.1f}/{b['ugf_hz'] / 1e6:<6.1f} "
                  f"{a['pm_deg']:5.1f}/{b['pm_deg']:<5.1f} {a['gm_db']:5.1f}/{b['gm_db']:<5.1f} "
                  f"{a['ts01_fall_ns']:6.0f}/{b['ts01_fall_ns']:<7.0f} {a['sc_err250_Lr_pct']:6.3f}/{b['sc_err250_Lr_pct']:<6.3f} "
                  f"{1e3 * a['lc_ripple_mv']:4.1f}/{1e3 * b['lc_ripple_mv']:<4.1f}")


if __name__ == "__main__":
    main()
