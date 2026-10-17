import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import numpy as np
import v2, pgrid
base = dict(R=25e3, tail=40, ld_m=4, itrim=15e-6, ptat="cgm", servo="ideal", mn3_w=1.15, mn3_l=0.5, pP=1, nP=6, sP=6,
            mdz_l=0.3, kN=3, mpr_m=1, iref=1)
specs = {"b_ref": dict(base, Cn=10e-12, gsv=1e-7, csv=1e-12),
         "b_reg10": dict(base, Cn=1e-12, gsv=1e-7, csv=1e-12),
         "b_reg100": dict(base, Cn=1e-13, gsv=1e-7, csv=1e-12),
         "b_srv3": dict(base, Cn=10e-12, gsv=3e-7, csv=1e-12)}
res = pgrid.run_all(specs)
for name, out in res.items():
    print(pgrid.summary(name, out), "| ts:", " ".join(f"{c[0][4:]}{c[1]}:{r.get('ts01',np.nan):.0f}" for c, r in out.items()), flush=True)
