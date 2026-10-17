#!/usr/bin/env python3
"""Monte Carlo analysis of RAMP_V2 with the IHP SG13G2 statistical models (TT, 27 degC, 1.65 V).

Three sets of random variation (as sim/montecarlo.py for RAMP_LR):
  process  : global (die-to-die) variation, the *_stat sections of the PDK corner libraries
  mismatch : local (device-to-device) variation, the *_mismatch sections
  both     : the *_stat parameters combined with the mismatch model files
Every sample is a separate ngspice process with its own seed.  Each sample runs the operating
point, the loop gain and the 200-mV step of the unity-gain buffer, and the SC step test.
The constant-gm reference uses a dummy rhigh, so it varies with the resistor like an on-chip
reference would.

Run sim/v2_sim.py first (it builds sim/build/v2/v2_lib.spice).
Output: sim/results/v2/mc_summary.csv, sim/results/v2/mc_waves.npz.
Usage: python3 sim/v2_montecarlo.py [samples per set]
"""
import csv
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import montecarlo as mc  # noqa: E402
import ramp_pvt as rp  # noqa: E402
import v2_sim as v2  # noqa: E402

N = 300
N_WAVE = 100
MCDIR = v2.BUILD / "mc"


def run_sample(job):
    mset, k, models = job
    name = f"{mset}_{k:04d}"
    tb = v2.testbench(name, "mos_tt", 27, rp.VDD0, psrr=False, build=MCDIR, modeltext=models, seed=k + 1)
    sc = v2.sc_deck("sc_" + name, "mos_tt", 27, rp.VDD0, build=MCDIR, modeltext=models, seed=k + 1)
    row = dict(set=mset, sample=k, seed=k + 1, ok=0)
    if not (rp.ngspice(tb) and rp.ngspice(sc)):
        return row, None
    d, ds = tb.parent, sc.parent
    try:
        row.update(v2.op_metrics(d))
        row.update(rp.loop_metrics(d))
        row.update(v2.step_metrics(d))
        row.update(rp.sc_metrics(ds))
    except Exception:
        return row, None
    row["ok"] = 1
    wave = None
    if k < N_WAVE:
        lp, tr, st = rp.read(d / "loop.dat"), rp.read(ds / "sc.dat"), rp.read(d / "tran.dat")
        tl = rp.SC_EDGES[2][0]
        tg = np.arange(tl - 50e-9, tl + 1000e-9, 2e-9)
        tb_ = np.arange(rp.T_EDGE - 50e-9, rp.T_FALL, 1e-9)
        wave = dict(f=lp["frequency"], t=(lp["mbr"] + 1j * lp["mbi"]).astype(np.complex64), tt=tg,
                    v=np.interp(tg, tr["time"], tr["v(out)"]), tstep=tb_, vstep=np.interp(tb_, st["time"], st["v(out)"]))
    shutil.rmtree(ds)
    shutil.rmtree(d)
    return row, wave


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else N
    if not v2.LIB.exists():
        v2.netlist_library()
    mc.MC.mkdir(parents=True, exist_ok=True)
    MCDIR.mkdir(parents=True, exist_ok=True)
    sets = dict(mc.SETS, both=mc.both_library())
    jobs = [(s, k, m) for s, m in sets.items() for k in range(n)]
    with ThreadPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
        res = list(ex.map(run_sample, jobs))
    rows = [r for r, _ in res]
    keys = list(dict.fromkeys(k for r in rows for k in r))
    v2.RESULTS.mkdir(parents=True, exist_ok=True)
    with open(v2.RESULTS / "mc_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    waves = {}
    for (s, k, _), (_, wv) in zip(jobs, res):
        if wv is not None:
            for key, val in wv.items():
                if key in ("f", "tt", "tstep"):
                    waves.setdefault(key, val)
                else:
                    waves.setdefault(f"{s}_{key}", []).append(val)
    np.savez_compressed(v2.RESULTS / "mc_waves.npz", **{k: np.array(v) for k, v in waves.items()})
    for s in sets:
        ok = [r for r in rows if r["set"] == s and r["ok"]]
        off = np.array([r["offset_mv"] for r in ok])
        iq = np.array([r["iq_ua"] for r in ok])
        pm = np.array([r["pm_deg"] for r in ok])
        print(f"{s:9s} n={len(ok):3d}: offset mean {off.mean():+.2f} sigma {off.std():.2f} mV (+-3 sigma "
              f"{off.mean() - 3 * off.std():+.1f}..{off.mean() + 3 * off.std():+.1f} mV), I_Q sigma/mean "
              f"{100 * iq.std() / iq.mean():.1f} %, PM min {pm.min():.1f} deg")


if __name__ == "__main__":
    main()
