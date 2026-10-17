import itertools, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2
CORN = (("mos_ss", -40), ("mos_sf", -40), ("mos_tt", 27), ("mos_ff", 125), ("mos_ss", 125))
grid = []
for R, tail, kN, inv, iref in itertools.product((50e3, 70e3), (20, 40), (2, 3), ((2, 6, 6), (3, 9, 9)), (0.5, 1)):
    if iref == 0.5:
        continue  # handled by the ratio below
    grid.append(dict(R=R, tail=tail, kN=kN, pP=inv[0], nP=inv[1], sP=inv[2], Cn=10e-12, ld_m=tail // 10,
                     mpr_m=2, iref=1))          # I_Q = 1 uA * 4/2 = 2 uA
    grid.append(dict(R=R, tail=tail, kN=kN, pP=inv[0], nP=inv[1], sP=inv[2], Cn=10e-12, ld_m=tail // 10,
                     mpr_m=1, iref=1))          # I_Q = 4 uA
res = []
for k, p in enumerate(grid):
    name = f"g{k}"
    out, _ = v2.evaluate(p, name, corners=CORN)
    pms = [r.get("pm", np.nan) for r in out.values()]
    ugf_tt = out[("mos_tt", 27)].get("ugf", np.nan)
    osc = max(r.get("osc", 0) for r in out.values())
    itot = out[("mos_tt", 27)].get("itot", np.nan)
    a0 = min(r.get("a0", np.nan) for r in out.values())
    res.append((p, min(pms), ugf_tt, osc, itot, a0))
    print(f"{name}: R {p['R']/1e3:.0f}k tail {p['tail']} kN {p['kN']} inv {p['pP']},{p['nP']},{p['sP']} IQ {4/p['mpr_m']:.0f}u -> "
          f"PMmin {min(pms):5.1f} UGF_TT {ugf_tt:5.1f} osc {osc:5.1f} Itot {itot:4.0f} A0min {a0:5.1f}", flush=True)
json.dump([(r[0], *r[1:]) for r in res], open("grid.json", "w"))
