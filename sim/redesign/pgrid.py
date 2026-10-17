"""Run many v2 configurations in one process pool and rank them."""
import itertools, json, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2

def run_all(specs, corners=v2.CORNERS, threads=15):
    jobs = []
    for name, p in specs.items():
        f = v2.with_par(v2.lib(p, name))
        for c, t in corners:
            d = v2.OUT / f"{name}_{c[4:]}_{t}"
            jobs.append((d, v2.tb(f, d, c, t, ptat=bool(p.get("ptat")))))
    with ThreadPoolExecutor(threads) as ex:
        list(ex.map(lambda j: v2.run(*j), jobs))
    res = {}
    for name in specs:
        out = {}
        for c, t in corners:
            try:
                out[(c, t)] = v2.metrics(v2.OUT / f"{name}_{c[4:]}_{t}")
            except Exception:
                out[(c, t)] = {}
        res[name] = out
    return res

def summary(name, out):
    g = lambda k, f=min: f([r.get(k, np.nan) if r.get(k) is not None else np.nan for r in out.values()])
    tt = out.get(("mos_tt", 27), {})
    return (f"{name:34s} PMmin {g('pm'):5.1f} GMmin {g('gm'):5.1f} osc {g('osc', max):5.1f} UGF tt {tt.get('ugf', np.nan):5.1f} "
            f"max {g('ugf', max):5.1f} Itot {tt.get('itot', np.nan):4.0f} A0min {g('a0'):5.1f} "
            f"offTT {tt.get('off_mv', np.nan):5.2f} |off|max {max(abs(r.get('off_mv', np.nan)) for r in out.values()):5.2f} "
            f"ts {tt.get('ts01', np.nan):4.0f}")

if __name__ == "__main__":
    base = dict(Cn=10e-12, iref=1, ptat=1, casc=True, s1_w=4.0, s1_l=0.5, s1_m=16, cas_w=2.0, cas_l=0.13, cas_m=4,
                tail=40, ld_m=4, vcas=0.55, kN=4, mn3_w=1.15, mn3_l=0.5)
    specs = {}
    for mpr, R, inv, mp3w in itertools.product((4, 5, 6), (40e3, 50e3), ((2, 6, 6), (3, 9, 9)), (4.5, 3.0)):
        specs[f"e_IQ{4/mpr:.2f}_R{R/1e3:.0f}_P{inv[0]}_W{mp3w}"] = dict(base, mpr_m=mpr, R=R, pP=inv[0], nP=inv[1],
                                                                        sP=inv[2], mp3_w=mp3w)
    res = run_all(specs)
    for name, out in res.items():
        print(summary(name, out), flush=True)
