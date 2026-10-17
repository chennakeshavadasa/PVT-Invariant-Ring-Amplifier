import itertools, sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2, pgrid
base = dict(Cn=10e-12, iref=1, ptat=1, casc=False, s1_w=2.5, s1_l=0.5, s1_m=8, tail=40, ld_m=4,
            pP=2, nP=6, sP=6, cmref="servo")
specs = {}
for R, iq, kN, mn3 in itertools.product((25e3, 30e3), ((2, 1), (3, 2), (4, 3)), (2, 3), ((2.3, 1.0), (1.15, 0.5))):
    # I_Q = iref * mp3_m / mpr_m with mp3_m = 4: (mpr_m, iref) pairs below give 2, 2.67, 3 uA
    mpr, ir = {2: (2, 1), 3: (3, 2), 4: (4, 3)}[iq[0]]
    specs[f"s_R{R/1e3:.0f}_IQ{4*ir/mpr:.2f}_kN{kN}_L{mn3[1]}"] = dict(base, R=R, kN=kN, mn3_w=mn3[0], mn3_l=mn3[1],
                                                                       mpr_m=mpr, iref=ir)
res = pgrid.run_all(specs)
for name, out in res.items():
    print(pgrid.summary(name, out), flush=True)
