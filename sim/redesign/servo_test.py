import sys, numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2
q1 = dict(R=25e3, tail=40, kN=2, pP=2, nP=6, sP=6, Cn=10e-12, ld_m=4, mpr_m=2, iref=1, ptat=1)
for name, p in (("q1_noservo", dict(q1)), ("q1_servo", dict(q1, servo="ideal"))):
    v2.show(name, *v2.evaluate(p, name, mc_n=80))
