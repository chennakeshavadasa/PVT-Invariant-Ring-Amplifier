"""Fast-loop DC gain: slow-loop nodes (VCTRLN, VSV) frozen with 1-F caps; stage gains at 10 Hz."""
import sys, json, subprocess
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import v2, chk
NODES = ["inp", "x1.vo_stg1", "x1.net2", "x1.mp_dz", "x1.mn_dz", "out"]
def run(p, name, corner, temp, freeze=True):
    f = v2.with_par(v2.lib(p, name)); t = f.read_text()
    if freeze:
        t = t.replace(".ends", "CFZ1 VCTRLN GND 1\nCFZ2 VSV GND 1\n.ends")
    g = f.with_name(f.stem + "_fz.spice"); g.write_text(t)
    d = v2.OUT / f"fg_{name}_{corner}_{temp}"; d.mkdir(exist_ok=True); (d / ".spiceinit").write_text(v2.SPI)
    (d / "tb.spice").write_text(f"""* fast gain
.include {g}
{v2.rp.models(corner)}.temp {temp}
x1 VDD GND IBIAS VICM inp out RAMP_V2
{v2.ref_src(p.get('ptat'))}
V1 VICM GND dc 0.825
V2 VDD GND dc 1.65
C1 out GND 50p
Vprobe2 probe inp 0
Vprobe1 probe out dc 0 ac 1
.nodeset v(x1.vctrln)=0.6 v(x1.vo_stg1)=0.72 v(x1.net2)=0.72 v(out)=0.825
.control
set wr_singlescale
set wr_vecnames
ac dec 10 10 100Meg
""" + "".join(f"let r{i} = real(v({n}))\nlet i{i} = imag(v({n}))\n" for i, n in enumerate(NODES)) +
f"""wrdata {d}/n.dat {' '.join(f'r{i} i{i}' for i in range(len(NODES)))}
quit
.endc
.end
""")
    subprocess.run(["ngspice", "-b", "tb.spice"], cwd=d, capture_output=True)
    a = np.loadtxt(d / "n.dat", skiprows=1)
    fr = a[:, 0]
    V = {n: a[:, 1 + 2 * i] + 1j * a[:, 2 + 2 * i] for i, n in enumerate(NODES)}
    def f3(h):
        m = np.abs(h); j = np.where(m < m[0] / np.sqrt(2))[0]
        return fr[j[0]] / 1e6 if len(j) else np.nan
    poles = dict(f_A1=f3(V["x1.vo_stg1"] / V["inp"]), f_A2p=f3(V["x1.mp_dz"] / V["x1.vo_stg1"]),
                 f_A2n=f3(V["x1.mn_dz"] / V["x1.vo_stg1"]), f_A3=f3(V["out"] / V["x1.mp_dz"]))
    v = {n: x[0] for n, x in V.items()}
    db = lambda x: 20 * np.log10(abs(x))
    vd = v["x1.vo_stg1"] - v["x1.net2"]
    return dict(T=db(v["out"] / v["inp"]), A1=db(v["x1.vo_stg1"] / v["inp"]), A1d=db(vd / v["inp"]),
                A2p=db(v["x1.mp_dz"] / v["x1.vo_stg1"]), A2n=db(v["x1.mn_dz"] / v["x1.vo_stg1"]),
                A3p=db(v["out"] / v["x1.mp_dz"]), A23=db(v["out"] / v["x1.vo_stg1"]), **poles)
if __name__ == "__main__":
    cs = [("mos_tt", 27), ("mos_ss", -40), ("mos_ff", 125), ("mos_fs", 125), ("mos_sf", -40)]
    for a in sys.argv[1:]:
        k, val = a.split("=", 1); p = dict(chk.BASE, **json.loads(val))
        with ThreadPoolExecutor(10) as ex:
            res = list(ex.map(lambda ct: run(p, k, *ct), cs))
        for (c, T), r in zip(cs, res):
            print(f"{k:5} {c[4:]} {T:4}: " + " ".join(f"{n} {x:5.1f}" for n, x in r.items()) + " (dB, MHz)")
