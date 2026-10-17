import itertools, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import numpy as np
import v2, pgrid
base = dict(R=25e3, tail=40, ld_m=4, Cn=10e-12, itrim=15e-6, ptat="cgm", servo="ideal", gsv=1e-7, csv=1e-12,
            mn3_w=1.15, mn3_l=0.5, pP=1, nP=6, sP=6, mdz_l=0.3)
specs = {}
for (mpr, ir), kN in itertools.product(((9, 8), (5, 5), (11, 12)), (3, 4)):
    specs[f"n_IQ{4*ir/mpr:.2f}_kN{kN}"] = dict(base, mpr_m=mpr, iref=ir, kN=kN)
res = pgrid.run_all(specs)
for name, out in res.items():
    print(pgrid.summary(name, out), "| PM:", " ".join(f"{c[0][4:]}{c[1]}:{r.get('pm',np.nan):.0f}" for c, r in out.items()), flush=True)
