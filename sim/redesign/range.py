import itertools, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import numpy as np
import v2, pgrid
base = dict(R=25e3, tail=40, ld_m=4, Cn=10e-12, itrim=15e-6, ptat="cgm", servo="ideal", gsv=1e-7, csv=1e-12,
            mn3_w=1.15, mn3_l=0.5, kN=3, mpr_m=5, iref=4)
specs = {}
for (pP, nP, sP), mdzl in itertools.product(((2, 6, 6), (1, 6, 6), (1, 4, 8), (1, 8, 8), (1, 6, 12)), (0.13, 0.3, 0.6)):
    specs[f"r_P{pP}N{nP}S{sP}_L{mdzl}"] = dict(base, pP=pP, nP=nP, sP=sP, mdz_l=mdzl)
res = pgrid.run_all(specs)
for name, out in res.items():
    vcn = [r.get("vctrln", np.nan) for r in out.values()]
    iq = [r.get("iq", np.nan) for r in out.values()]
    pm = [r.get("pm", np.nan) for r in out.values()]
    print(f"{name:22s} VCN {min(vcn):7.3f}..{max(vcn):9.3f}  IQ {min(iq):5.2f}..{max(iq):5.2f}  PMmin {min(pm):5.1f}  UGF_TT {out[('mos_tt',27)].get('ugf',np.nan):5.1f}", flush=True)
