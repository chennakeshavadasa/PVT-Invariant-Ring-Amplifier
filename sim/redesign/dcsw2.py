"""DC input sweep of the v2 buffer with internal nodes (where the CM-dependent error comes from)."""
import sys, json, subprocess
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import v2, chk
SAVE = "v(out) v(x1.vo_stg1) v(x1.net2) v(x1.net3) v(x1.v1_cm) v(x1.vsv) v(x1.vtrip) v(x1.it1) v(x1.vcmfb) v(x1.mp_dz) v(x1.mn_dz) v(x1.vctrln) i(v.x1.viq)"
def sweep(p, name, corner, temp, lo=0.625, hi=1.025, extra=""):
    f = v2.with_par(v2.lib(p, name)); d = v2.OUT / f"{name}_dc2_{corner}_{temp}"
    d.mkdir(exist_ok=True); (d / ".spiceinit").write_text(v2.SPI)
    (d / "tb.spice").write_text(f"""* dc sweep
.include {f}
{v2.rp.models(corner)}.temp {temp}
x1 VDD GND IBIAS VICM out out RAMP_V2
{v2.ref_src(p.get('ptat'))}
V1 VICM GND dc 0.825
V2 VDD GND dc 1.65
{extra}
.nodeset v(x1.vctrln)=0.6 v(x1.vo_stg1)=0.72 v(x1.net2)=0.72 v(out)=0.825
.control
set wr_singlescale
set wr_vecnames
dc V1 {lo} {hi} 0.05
wrdata {d}/dc.dat {SAVE}
quit
.endc
.end
""")
    subprocess.run(["ngspice", "-b", "tb.spice"], cwd=d, capture_output=True)
    return v2.rp.read(d / "dc.dat")
if __name__ == "__main__":
    k, val = sys.argv[1].split("=", 1); p = dict(chk.BASE, **json.loads(val))
    cs = [("mos_tt", 27), ("mos_fs", 125), ("mos_ss", -40)]
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda ct: sweep(p, k, *ct), cs))
    for (c, t), r in zip(cs, res):
        print(f"== {c[4:]} {t}")
        vin = r["v-sweep"]
        for i in range(len(vin)):
            print(f"  Vin {vin[i]:.3f}: err {1e3*(r['v(out)'][i]-vin[i]):7.2f} mV  Vo1-net2 {1e3*(r['v(x1.vo_stg1)'][i]-r['v(x1.net2)'][i]):7.2f} mV  Vo1 {r['v(x1.vo_stg1)'][i]:.3f} V1CM {r['v(x1.v1_cm)'][i]:.3f} VSV {r['v(x1.vsv)'][i]:.3f} vtrip {r['v(x1.vtrip)'][i]:.3f} it1 {r['v(x1.it1)'][i]:.3f} vcmfb {r['v(x1.vcmfb)'][i]:.3f} VCN {r['v(x1.vctrln)'][i]:.3f} IQ {r['i(v.x1.viq)'][i]*1e6:.2f}")
