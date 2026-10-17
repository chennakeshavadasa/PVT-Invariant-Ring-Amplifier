import sys, json
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import numpy as np
import v2, pgrid
BASE = dict(R=25e3, tail=40, ld_m=4, itrim=15e-6, ptat="cgm", servo="ideal", gsv=1e-7, csv=1e-12, mn3_w=1.15, mn3_l=0.5,
            pP=1, nP=6, sP=6, mdz_l=0.3, kN=3, mpr_m=1, iref=1, Cn=10e-12, cmfb="mirror", tl_w=4.0, tl_l=1.0)
if __name__ == "__main__":
    specs = {"x_" + k: dict(BASE, **json.loads(v)) for k, v in (a.split("=", 1) for a in sys.argv[1:])} or {"x_base": BASE}
    res = pgrid.run_all(specs)
    for name, out in res.items():
        print(pgrid.summary(name, out))
        print("   PM:", " ".join(f"{c[0][4:]}{c[1]}:{r.get('pm',np.nan):.0f}" for c, r in out.items()),
              "| ts:", " ".join(f"{c[0][4:]}{c[1]}:{r.get('ts01',np.nan):.0f}" for c, r in out.items()),
              "| off:", " ".join(f"{r.get('off_mv',np.nan):.2f}" for r in out.values()))
