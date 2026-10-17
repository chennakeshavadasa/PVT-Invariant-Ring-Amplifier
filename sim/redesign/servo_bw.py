import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2, pgrid
base = dict(R=25e3, tail=40, ld_m=4, kN=2, pP=2, nP=6, sP=6, Cn=10e-12, itrim=15e-6, ptat="cgm", mpr_m=3, iref=2,
            mn3_w=1.15, mn3_l=0.5)
specs = {"sb_none": dict(base, servo="none")}
for g in (1e-6, 1e-7, 1e-8):
    specs[f"sb_g{g:.0e}"] = dict(base, servo="ideal", gsv=g, csv=1e-12)
res = pgrid.run_all(specs, corners=(("mos_tt", 27), ("mos_ss", -40), ("mos_ff", 125)))
for name, out in res.items():
    print(pgrid.summary(name, out), "| ts per corner:", {f"{c[0][4:]}{c[1]}": round(r.get('ts01', -1)) for c, r in out.items()})
