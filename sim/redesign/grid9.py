import itertools, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2, pgrid
base = dict(R=25e3, tail=40, ld_m=4, Cn=10e-12, itrim=15e-6, ptat="cgm", servo="ideal", gsv=1e-7, csv=1e-12,
            mn3_w=1.15, mn3_l=0.5)
specs = {}
for (mpr, ir), kN, inv in itertools.product(((4, 3), (5, 4), (6, 5), (1, 1)), (2, 3), ((2, 6, 6), (3, 9, 9))):
    specs[f"m_IQ{4*ir/mpr:.2f}_kN{kN}_P{inv[0]}"] = dict(base, mpr_m=mpr, iref=ir, kN=kN, pP=inv[0], nP=inv[1], sP=inv[2])
res = pgrid.run_all(specs)
for name, out in res.items():
    print(pgrid.summary(name, out), flush=True)
