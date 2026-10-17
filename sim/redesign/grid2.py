import itertools, sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2
CORN = (("mos_ss", -40), ("mos_sf", -40), ("mos_tt", 27), ("mos_ff", 125), ("mos_ss", 125))
specs = []
for R, tail, mpr in itertools.product((25e3, 35e3), (40, 60), (1, 2)):
    specs.append(dict(R=R, tail=tail, kN=2, pP=2, nP=6, sP=6, Cn=10e-12, ld_m=tail // 10, mpr_m=mpr, iref=1))
for k, p in enumerate(specs):
    out, _ = v2.evaluate(p, f"h{k}", corners=CORN)
    pms = {c: r.get("pm", np.nan) for c, r in out.items()}
    gms = [r.get("gm", np.nan) for r in out.values()]
    print(f"h{k}: R {p['R']/1e3:.0f}k tail {p['tail']} IQ {4/p['mpr_m']:.0f}u -> PM " +
          " ".join(f"{c[0][4:]}{c[1]}:{v:.0f}" for c, v in pms.items()) +
          f" | GMmin {min(gms):.1f} UGF_TT {out[('mos_tt',27)].get('ugf',np.nan):.1f} UGF_SS-40 {out[('mos_ss',-40)].get('ugf',np.nan):.1f}"
          f" osc {max(r.get('osc',0) for r in out.values()):.1f} Itot {out[('mos_tt',27)].get('itot',np.nan):.0f}"
          f" A0min {min(r.get('a0',np.nan) for r in out.values()):.1f} offTT {out[('mos_tt',27)].get('off_mv',np.nan):.2f}", flush=True)
