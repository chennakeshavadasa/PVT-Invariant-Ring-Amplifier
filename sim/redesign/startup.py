"""Power-up transient: VDD ramps 0 -> 1.65 V in 1 us; slow loops settle from zero."""
import sys, json
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import v2, chk
def deck(f, d, corner, temp, stop, ptat="cgm"):
    return f"""* startup
.include {f}
{v2.rp.models(corner)}.temp {temp}
x1 VDD GND IBIAS VICM out out RAMP_V2
{v2.ref_src(ptat)}
V1 VICM GND dc 0.825
V2 VDD GND pwl(0 0 1u 1.65)
C1 out GND 50p
.control
set wr_singlescale
set wr_vecnames
tran 10n {stop} 0 50n uic
wrdata {d}/su.dat v(out) v(x1.vctrln) v(x1.v1_cm) v(x1.vsv) i(v.x1.viq) v(x1.mp_dz)
quit
.endc
.end
"""
def run(p, name, corners, stop):
    f = v2.with_par(v2.lib(p, name))
    jobs = [(v2.OUT / f"{name}_su_{c[4:]}_{t}", c, t) for c, t in corners]
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(lambda j: v2.run(j[0], deck(f, j[0], j[1], j[2], stop)), jobs))
    return jobs
if __name__ == "__main__":
    k, v = sys.argv[1].split("=", 1); stop = sys.argv[2] if len(sys.argv) > 2 else "8m"
    p = dict(chk.BASE, **json.loads(v))
    cs = [("mos_tt", 27), ("mos_ss", -40), ("mos_sf", -40), ("mos_ff", 125)]
    for d, c, t in run(p, k, cs, stop):
        try:
            r = v2.rp.read(d / "su.dat")
        except Exception as e:
            print(c, t, "FAILED", e); continue
        tt = r["time"]
        print(f"{c[4:]} {t}: " + " | ".join(f"{x*1e3:.2f}ms out {np.interp(x, tt, r['v(out)']):.4f} VCN {np.interp(x, tt, r['v(x1.vctrln)']):.3f} V1CM {np.interp(x, tt, r['v(x1.v1_cm)']):.3f} IQ {np.interp(x, tt, r['i(v.x1.viq)'])*1e6:.2f}"
                                          for x in (5e-6, 0.1e-3, 0.5e-3, 1e-3, 2e-3, 4e-3, tt[-1])))
