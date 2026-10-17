import itertools, sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2
specs = {
 "q1": dict(R=25e3, tail=40, kN=2, pP=2, nP=6, sP=6, Cn=10e-12, ld_m=4, mpr_m=2, iref=1, ptat=1),
 "q2": dict(R=35e3, tail=40, kN=2, pP=2, nP=6, sP=6, Cn=10e-12, ld_m=4, mpr_m=2, iref=1, ptat=1),
 "q3": dict(R=25e3, tail=40, kN=2, pP=2, nP=6, sP=6, Cn=10e-12, ld_m=4, mpr_m=1, iref=1, ptat=1),
 "q4": dict(R=35e3, tail=60, kN=2, pP=2, nP=6, sP=6, Cn=10e-12, ld_m=6, mpr_m=2, iref=1, ptat=1),
}
for name, p in specs.items():
    out, _ = v2.evaluate(p, name, corners=v2.CORNERS)
    pms = {c: r.get("pm", np.nan) for c, r in out.items()}
    gms = [r.get("gm", np.nan) for r in out.values()]
    ugfs = {c: r.get("ugf", np.nan) for c, r in out.items()}
    print(f"{name}: R {p['R']/1e3:.0f}k tail {p['tail']} IQ {4/p['mpr_m']:.0f}u PTAT -> PM " +
          " ".join(f"{c[0][4:]}{c[1]}:{v:.0f}" for c, v in pms.items()) + "\n      UGF " +
          " ".join(f"{c[0][4:]}{c[1]}:{v:.1f}" for c, v in ugfs.items()) +
          f" | GMmin {min(gms):.1f} osc {max(r.get('osc',0) for r in out.values()):.1f} Itot {out[('mos_tt',27)].get('itot',np.nan):.0f}"
          f" A0min {min(r.get('a0',np.nan) for r in out.values()):.1f} off " +
          " ".join(f"{r.get('off_mv',np.nan):.1f}" for r in out.values()), flush=True)
