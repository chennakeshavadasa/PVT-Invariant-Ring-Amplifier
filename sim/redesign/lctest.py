"""Limit-cycle step test: buffer steps of +-10..+-200 mV (500 ns each); peak-to-peak ripple in the last 100 ns."""
import sys, json
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import v2, chk
STEPS = [0.01, -0.01, 0.02, -0.02, 0.05, -0.05, 0.1, -0.1, 0.2, -0.2]
SEG = 500e-9
def deck(f, d, corner, temp, vdd=1.65, ptat="cgm", models=None, seed=None):
    v, pts, t0 = 0.825, ["0 0.825"], 100e-9
    for s in STEPS:
        pts += [f"{t0:.4g} {v:.4f}", f"{t0 + 1e-9:.4g} {v + s:.4f}"]; v += s; t0 += SEG
    return f"""* lc
{f'.options seed={seed}' if seed else ''}
.include {f}
{models or v2.rp.models(corner)}.temp {temp}
x1 VDD GND IBIAS VICM out out RAMP_V2
{v2.ref_src(ptat)}
V1 VICM GND pwl({' '.join(pts)})
V2 VDD GND dc {vdd}
C1 out GND 50p
.nodeset v(x1.vctrln)=0.6 v(x1.vo_stg1)=0.72 v(x1.net2)=0.72 v(out)=0.825
.control
set wr_singlescale
set wr_vecnames
tran 0.1n {100e-9 + SEG * len(STEPS):.4g} 0 0.25n
wrdata {d}/lc.dat v(out) v(vicm)
quit
.endc
.end
"""
def metrics(d):
    r = v2.rp.read(d / "lc.dat"); t, v, vin = r["time"], r["v(out)"], r["v(vicm)"]
    out = []
    for k, s in enumerate(STEPS):
        t1 = 100e-9 + (k + 1) * SEG; m = (t > t1 - 100e-9) & (t < t1 - 1e-9)
        tgt = np.interp(t1 - 2e-9, t, v)      # settling to the segment's own final value
        e = np.abs(v - tgt) / abs(s); m2 = (t > t1 - SEG + 1e-9) & (t < t1 - 1e-9); tt = t[m2]; bad = np.where(e[m2] > 1e-2)[0]
        out.append(dict(step=s, ripple_mv=1e3 * np.ptp(v[m]), err_mv=1e3 * (tgt - np.interp(t1 - 2e-9, t, vin)), ts1_ns=(tt[bad[-1]] - (t1 - SEG)) * 1e9 if len(bad) else 0.0))
    return out
def run(p, name, corners=v2.CORNERS, vdd=1.65, par=True):
    f = v2.lib(p, name); fp = v2.with_par(f) if par else f
    jobs = [(v2.OUT / f"{name}_lc_{c[4:]}_{t}_{vdd}", c, t) for c, t in corners]
    with ThreadPoolExecutor(15) as ex:
        list(ex.map(lambda j: v2.run(j[0], deck(fp, j[0], j[1], j[2], vdd=vdd, ptat=p.get("ptat"))), jobs))
    res = {}
    for d, c, t in jobs:
        try:
            res[(c, t)] = metrics(d)
        except Exception as e:
            res[(c, t)] = None
    return res
if __name__ == "__main__":
    for a in sys.argv[1:]:
        k, val = a.split("=", 1); p = dict(chk.BASE, **json.loads(val))
        for (c, t), r in run(p, "lc_" + k).items():
            if r is None:
                print(f"{k} {c[4:]} {t}: FAILED"); continue
            print(f"{k:4} {c[4:]} {t:4}: max ripple {max(x['ripple_mv'] for x in r):6.3f} mV | ts1% " +
                  " ".join(f"{x['step']*1e3:+.0f}:{x['ts1_ns']:.0f}" for x in r) + " | static err mV " + " ".join(f"{x['err_mv']:+.2f}" for x in r[::2]))
