import sys, json
import numpy as np
import v2, chk, sctest
rp = v2.rp
EX = "v(x1.vctrln) v(x1.v1_cm) v(x1.vo_stg1) v(x1.net2) v(x1.mp_dz) v(x1.mn_dz) i(v.x1.viq) v(vx)"
T2 = {"cmfb":"diode","reg":"miller","servo":"miller","Cn":1e-15,"ccr":2e-12,"reg_l":"lo:16","srv_l":"lo:16"}
VAR = {"T2": T2,
       "regI_srvM": dict(T2, reg="ideal", Cn=10e-12),
       "regM_srvI": dict(T2, servo="ideal"),
       "regI_srvI": dict(T2, reg="ideal", servo="ideal", Cn=10e-12),
       "regM_srvN": dict(T2, servo="none")}
for a in sys.argv[1:]:
    if "=" in a:
        k, v = a.split("=", 1); VAR[k] = dict(T2, **json.loads(v))
sel = [a.split("=")[0] for a in sys.argv[1:]] or list(VAR)
cs = [("mos_tt", 27), ("mos_ff", 125)]
for k in sel:
    p = dict(chk.BASE, **VAR[k])
    out = sctest.run(p, "scd_" + k, corners=cs, extra=EX)
    for c, t in cs:
        d = v2.OUT / f"scd_{k}_sc_{c[4:]}_{t}"
        tr = rp.read(d / "sc.dat"); ti, v = tr["time"], tr["v(out)"]
        line = []
        for t0, dv, win in rp.SC_EDGES[:2]:
            tg = np.interp(t0 - 1e-9, ti, v) - dv
            line.append(" ".join(f"{(np.interp(t0 + x * 1e-9, ti, v) - tg) * 1e6:+6.1f}" for x in (50, 100, 250, 500, 1000, 1900)))
        print(f"{k:10} {c[4:]} {t:4} +4mV: {line[0]} | -4mV: {line[1]} uV")
