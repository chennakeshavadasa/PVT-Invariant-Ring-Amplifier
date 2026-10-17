"""SC charge-transfer test of the v2 prototype (sim/ramp_pvt.py sc_deck, constant-gm reference)."""
import sys, json
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import v2, chk
rp = v2.rp
def sc_deck(f, d, corner, temp, vdd=1.65, ptat="cgm", models=None, seed=None, extra=""):
    pts, v = [f"0 {rp.VCM}"], rp.VCM
    for t0, dv, _ in rp.SC_EDGES:
        pts += [f"{t0} {v}", f"{t0 + 0.5e-9} {v + dv}"]
        v += dv
    return f"""* sc
{f'.options seed={seed}' if seed else ''}
.include {f}
{models or rp.models(corner)}.temp {temp}
x1 VDD GND IBIAS VCM vx out RAMP_V2
{v2.ref_src(ptat)}
VCMS VCM GND dc {rp.VCM}
VIN vin GND pwl({' '.join(pts)})
CS vin vx {rp.CS}
CF vx out {rp.CF}
RF vx out 1G
CL out GND {rp.CLOAD}
V2 VDD GND dc {vdd}
.nodeset v(x1.vctrln)=0.6 v(x1.vo_stg1)=0.72 v(x1.net2)=0.72 v(out)=0.825
.control
set wr_singlescale
set wr_vecnames
tran 0.2n {rp.SC_STOP} 0 0.5n
wrdata {d}/sc.dat v(out) v(vin)
{f'wrdata {d}/int.dat {extra}' if extra else ''}
quit
.endc
.end
"""
def run(p, name, corners=v2.CORNERS, par=True, extra=""):
    f = v2.lib(p, name); fp = v2.with_par(f) if par else f
    jobs = [(v2.OUT / f"{name}_sc_{c[4:]}_{t}", c, t) for c, t in corners]
    with ThreadPoolExecutor(15) as ex:
        list(ex.map(lambda j: v2.run(j[0], sc_deck(fp, j[0], j[1], j[2], ptat=p.get("ptat"), extra=extra)), jobs))
    out = {}
    for d, c, t in jobs:
        try:
            out[(c, t)] = rp.sc_metrics(d)
        except Exception as e:
            out[(c, t)] = {}
    return out
if __name__ == "__main__":
    for spec in sys.argv[1:]:
        k, v = spec.split("=", 1); p = dict(chk.BASE, **json.loads(v))
        out = run(p, "sc_" + k)
        print(k)
        for (c, t), r in out.items():
            print(f"  {c[4:]} {t:4}: 4 mV  ts0.1% {r.get('sc_ts01_Sr_ns', np.nan):6.0f} ns err@250 {r.get('sc_err250_Sr_pct', np.nan):.3f} % | "
                  f"200 mV ts0.1% {r.get('sc_ts01_Lr_ns', np.nan):6.0f} ns err@250 {r.get('sc_err250_Lr_pct', np.nan):.3f} % | end err S {r.get('sc_errend_Sr_pct', np.nan):.3f} L {r.get('sc_errend_Lr_pct', np.nan):.3f} %")
