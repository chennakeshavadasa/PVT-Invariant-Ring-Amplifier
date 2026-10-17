import itertools, sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2
base = dict(Cn=10e-12, iref=1, ptat=1, casc=True, s1_w=4.0, s1_l=0.5, s1_m=16, cas_w=2.0, cas_l=0.13, cas_m=4,
            R=50e3, tail=40, ld_m=4, vcas=0.55)
specs = {}
for kN, inv, mn3, mpr in itertools.product((2, 4), ((2, 6, 6), (4, 12, 12)), ((2.3, 1.0), (1.15, 0.5)), (2, 4)):
    specs[f"d_kN{kN}_P{inv[0]}_MN3L{mn3[1]}_IQ{4/mpr:.0f}"] = dict(base, kN=kN, pP=inv[0], nP=inv[1], sP=inv[2],
                                                                    mn3_w=mn3[0], mn3_l=mn3[1], mpr_m=mpr)
rows = []
for name, p in specs.items():
    out, _ = v2.evaluate(p, name, corners=v2.CORNERS)
    pm = min(r.get("pm", -99) for r in out.values()); gm = min(r.get("gm", -99) for r in out.values())
    osc = max(r.get("osc", 99) for r in out.values())
    print(f"{name:32s} PMmin {pm:5.1f} GMmin {gm:5.1f} osc {osc:5.1f} UGF tt {out[('mos_tt',27)].get('ugf',np.nan):5.1f} "
          f"ss-40 {out[('mos_ss',-40)].get('ugf',np.nan):5.1f} Itot {out[('mos_tt',27)].get('itot',np.nan):4.0f} "
          f"A0min {min(r.get('a0',np.nan) for r in out.values()):5.1f} offTT {out[('mos_tt',27)].get('off_mv',np.nan):5.2f} "
          f"offmax {max(abs(r.get('off_mv',0)) for r in out.values()):5.2f}", flush=True)
