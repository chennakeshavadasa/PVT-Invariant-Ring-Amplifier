import sys, json
from concurrent.futures import ThreadPoolExecutor
import v2, chk, regloop
T2 = {"cmfb":"diode","reg":"miller","servo":"miller","Cn":1e-15,"ccr":2e-12,"reg_l":"lo:16","srv_l":"lo:16"}
V = {k: dict(chk.BASE, **dict(T2, **json.loads(v))) for k, v in (a.split("=", 1) for a in sys.argv[1:])}
cs = [("mos_tt", 27), ("mos_ss", -40), ("mos_ff", 125), ("mos_sf", -40), ("mos_fs", 125)]
jobs = [(k, w, c, t) for k in V for w in ("reg", "servo") for c, t in cs]
with ThreadPoolExecutor(15) as ex:
    res = list(ex.map(lambda j: regloop.loop_at(V[j[0]], "rs_" + j[0], j[2], j[3], j[1]), jobs))
for (k, w, c, t), m in zip(jobs, res):
    print(f"{k:8s} {w:5s} {c[4:]} {t:4}: A0 {m['a0_db']:.1f} dB UGF {m['ugf_hz']/1e3:8.2f} kHz PM {m['pm_deg']:.1f} GM {m['gm_db']:.1f}")
