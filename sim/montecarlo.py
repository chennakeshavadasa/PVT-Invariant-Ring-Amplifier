#!/usr/bin/env python3
"""Monte Carlo analysis of RAMP_LR with the IHP SG13G2 statistical models (TT, 27 degC, 1.65 V).

Three sets of random variation, each for the regulated and the fixed-bias amplifier:
  process  : global (die-to-die) variation, the *_stat sections of the PDK corner libraries;
             every device of a type moves together
  mismatch : local (device-to-device) variation, the *_mismatch sections; Pelgrom-scaled
             threshold, mobility, W and L offsets per device
  both     : the *_stat parameters combined with the mismatch model files
Every sample is a separate ngspice process with its own seed (.options seed), so samples are
independent and the run is reproducible.  Each sample runs the operating point, the loop gain
of the unity-gain buffer and the SC step test of sim/ramp_pvt.py.

Run sim/ramp_pvt.py first (it builds sim/build/lr_lib.spice and the fixed-bias values).
Output: sim/results/mc_summary.csv, sim/results/mc_waves.npz (Bode and step traces of the
first N_WAVE samples of every set).   Usage: python3 sim/montecarlo.py [samples]
"""
import csv
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ramp_pvt as rp  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 500
N_WAVE = 100
MC = rp.BUILD / "mc"
MODELS = Path(os.environ["PDK_ROOT"]) / "ihp-sg13g2" / "libs.tech" / "ngspice" / "models"
SETS = {
    "process": ".lib cornerMOSlv.lib mos_tt_stat\n.lib cornerMOShv.lib mos_tt_stat\n"
               ".lib cornerRES.lib res_typ_stat\n.lib cornerCAP.lib cap_typ_stat\n",
    "mismatch": ".lib cornerMOSlv.lib mos_tt_mismatch\n.lib cornerMOShv.lib mos_tt_mismatch\n"
                ".lib cornerRES.lib res_typ_mismatch\n.lib cornerCAP.lib cap_typ_mismatch\n",
}
# global + local: the PDK has no such section, so build one from the *_stat sections with the
# model files swapped for their mismatch versions
BOTH_SWAP = {"cornerMOSlv.lib": ("mos_tt_stat", {"sg13g2_moslv_mod.lib": ["sg13g2_moslv_mismatch.lib",
                                                                          "sg13g2_moslv_mod_mismatch.lib"]}),
             "cornerMOShv.lib": ("mos_tt_stat", {"sg13g2_moshv_mod.lib": ["sg13g2_moshv_mismatch.lib",
                                                                          "sg13g2_moshv_mod_mismatch.lib"],
                                                 "sg13g2_svaricaphv_mod.lib": ["sg13g2_svaricaphv_mod_mismatch.lib"]}),
             "cornerRES.lib": ("res_typ_stat", {"resistors_mod.lib": ["resistors_mod_mismatch.lib"]}),
             "cornerCAP.lib": ("cap_typ_stat", {"capacitors_mod.lib": ["capacitors_mod_mismatch.lib"]})}


def both_library() -> str:
    out, calls = [], []
    for lib, (sec, swap) in BOTH_SWAP.items():
        text = (MODELS / lib).read_text()
        body = re.search(rf"^\.LIB {sec}\s*$(.*?)^\.ENDL", text, re.M | re.S | re.I).group(1)
        for old, new in swap.items():
            assert old in body, (lib, old)
            body = body.replace(f".include {old}", "\n".join(f".include {MODELS / n}" for n in new))
        body = re.sub(r"\.include (\S+\.lib)", lambda m: m.group(0) if m.group(1).startswith("/")
                      else f".include {MODELS / m.group(1)}", body)
        name = f"{lib[6:-4].lower()}_mc"
        out.append(f".LIB {name}\n{body}.ENDL {name}\n")
        calls.append(f".lib {MC / 'mc_both.lib'} {name}\n")
    (MC / "mc_both.lib").write_text("* global + local variation, built by sim/montecarlo.py\n" + "\n".join(out))
    return "".join(calls)


def run_sample(job):
    mset, bias, k, models, vcp, vcn = job
    sub = "RAMP_LR" if bias == "reg" else "RAMP_LR_FIXED"
    seed = f".options seed={k + 1}\n"
    name = f"{mset}_{bias}_{k:04d}"
    tb = rp.testbench(name, sub, "mos_tt", 27, rp.VDD0, vcp, vcn, transient=False, psrr=False,
                      modeltext=seed + models, build=MC)
    sc = rp.sc_deck("sc_" + name, sub, "mos_tt", 27, rp.VDD0, vcp, vcn, modeltext=seed + models, build=MC)
    row = dict(set=mset, bias=bias, sample=k, seed=k + 1, ok=0)
    if not (rp.ngspice(tb) and rp.ngspice(sc)):
        return row, None
    d, ds = tb.parent, sc.parent
    row.update(rp.op_metrics(d))
    row.update(rp.loop_metrics(d))
    row.update(rp.sc_metrics(ds))
    row["offset_mv"] = 1e3 * (row["vout"] - rp.VCM)
    row["ok"] = 1
    wave = None
    if k < N_WAVE:
        lp, tr = rp.read(d / "loop.dat"), rp.read(ds / "sc.dat")
        t0 = rp.SC_EDGES[0][0]
        tg = np.arange(t0 - 50e-9, t0 + 1000e-9, 2e-9)
        wave = dict(f=lp["frequency"], t=mp(lp), tt=tg, v=np.interp(tg, tr["time"], tr["v(out)"]))
    shutil.rmtree(ds)                      # the full SC waveform is 1 MB per sample
    return row, wave


def mp(lp):
    return (lp["mbr"] + 1j * lp["mbi"]).astype(np.complex64)


def main():
    MC.mkdir(parents=True, exist_ok=True)
    fixed = dict(l.split("=") for l in (rp.RESULTS / "fixed_bias.txt").read_text().split() if "_fixed=" in l)
    vcp, vcn = float(fixed["VCTRLP_fixed"]), float(fixed["VCTRLN_fixed"])
    sets = dict(SETS, both=both_library())
    jobs = [(s, b, k, m, vcp, vcn) for s, m in sets.items() for b in ("reg", "fix") for k in range(N)]
    with ThreadPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 2)) as ex:
        res = list(ex.map(run_sample, jobs))
    rows = [r for r, _ in res]
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(rp.RESULTS / "mc_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    waves = {}
    for (s, b, k, *_), (_, wv) in zip(jobs, res):
        if wv is not None:
            waves.setdefault(f"{s}_{b}", []).append(wv)
    arrays = {}
    for key, wl in waves.items():
        arrays[f"{key}_f"] = wl[0]["f"].astype(np.float32)
        arrays[f"{key}_loop"] = np.stack([w["t"] for w in wl])
        arrays[f"{key}_t"] = wl[0]["tt"].astype(np.float32)
        arrays[f"{key}_vout"] = np.stack([w["v"] for w in wl]).astype(np.float32)
    np.savez_compressed(rp.RESULTS / "mc_waves.npz", **arrays)
    for s in sets:
        for b in ("reg", "fix"):
            sel = [r for r in rows if r["set"] == s and r["bias"] == b and r["ok"]]
            iq = np.array([r["iq_ua"] for r in sel])
            ugf = np.array([r["ugf_hz"] for r in sel]) / 1e6
            print(f"{s:8} {b}: {len(sel)}/{N} ok, I_Q {iq.mean():.2f} +- {iq.std():.2f} uA "
                  f"[{iq.min():.2f}, {iq.max():.2f}], UGF {np.nanmean(ugf):.1f} +- {np.nanstd(ugf):.1f} MHz")


if __name__ == "__main__":
    main()
