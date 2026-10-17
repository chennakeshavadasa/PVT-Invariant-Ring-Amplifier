import itertools, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2, pgrid
base = dict(R=25e3, tail=40, ld_m=4, kN=2, pP=2, nP=6, sP=6, Cn=10e-12, servo="ideal", itrim=15e-6)
specs = {}
for ref, iq, mn3 in itertools.product(("ptat", "cgm"), ((2, 1), (3, 2), (4, 3), (1, 1)), ((2.3, 1.0), (1.15, 0.5))):
    mpr, ir = iq
    specs[f"k_{ref}_IQ{4*ir/mpr:.2f}_L{mn3[1]}"] = dict(base, ptat=ref, mpr_m=mpr, iref=ir, mn3_w=mn3[0], mn3_l=mn3[1])
res = pgrid.run_all(specs)
for name, out in res.items():
    print(pgrid.summary(name, out), flush=True)
