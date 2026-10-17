import itertools, sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2
base = dict(kN=2, pP=2, nP=6, sP=6, Cn=10e-12, iref=1, ptat=1, casc=True, s1_w=4.0, s1_l=0.5, s1_m=16,
            cas_w=2.0, cas_l=0.13, cas_m=4)
specs = {}
for R, tail, mpr, vcas in itertools.product((50e3, 70e3), (40, 60), (2, 4), (0.55,)):
    specs[f"c_R{R/1e3:.0f}_t{tail}_IQ{4/mpr:.0f}"] = dict(base, R=R, tail=tail, ld_m=tail // 10, mpr_m=mpr, vcas=vcas)
for name, p in specs.items():
    out, _ = v2.evaluate(p, name, corners=v2.CORNERS)
    pms = {c: r.get("pm", np.nan) for c, r in out.items()}
    gms = [r.get("gm", np.nan) for r in out.values()]
    print(f"{name}: PM " + " ".join(f"{c[0][4:]}{c[1]}:{v:.0f}" for c, v in pms.items()) +
          f" | UGF tt {out[('mos_tt',27)].get('ugf',np.nan):.1f} ss-40 {out[('mos_ss',-40)].get('ugf',np.nan):.1f}"
          f" GMmin {min(gms):.1f} osc {max(r.get('osc',0) for r in out.values()):.1f} Itot {out[('mos_tt',27)].get('itot',np.nan):.0f}"
          f" A0min {min(r.get('a0',np.nan) for r in out.values()):.1f} off " +
          " ".join(f"{r.get('off_mv',np.nan):.1f}" for r in out.values()), flush=True)
