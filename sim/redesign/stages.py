"""Stage-by-stage transfer functions from one AC run with the loop broken (voltage injection)."""
import sys, subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ramp_pvt as rp
OUT = Path(__file__).resolve().parents[1] / "build" / "redesign_stages"
OUT.mkdir(parents=True, exist_ok=True)
SPI = (Path.home() / ".spiceinit").read_text() + "\nset num_threads=1\n"
NODES = ["inp", "x1.vo_stg1", "x1.mp_dz", "x1.mn_dz", "out"]

def run(name, lib, sub, corner, temp, extra="", vcm=0.825):
    d = OUT / name; d.mkdir(exist_ok=True); (d / ".spiceinit").write_text(SPI)
    (d / "tb.spice").write_text(f"""* stages
.include {lib}
{rp.models(corner)}.temp {temp}
x1 VDD GND IBIAS VICM inp out {sub}
I_B VDD IBIAS 1u
V1 VICM GND dc {vcm}
V2 VDD GND dc 1.65
C1 out GND 50p
Vprobe2 probe inp 0
Vprobe1 probe out dc 0 ac 1
{extra}
.control
set wr_singlescale
set wr_vecnames
ac dec 40 1 10G
""" + "".join(f"let r{i} = real(v({n}))\nlet i{i} = imag(v({n}))\n" for i, n in enumerate(NODES)) +
f"""wrdata {d}/n.dat {' '.join(f'r{i} i{i}' for i in range(len(NODES)))}
quit
.endc
.end
""")
    subprocess.run(["ngspice", "-b", "tb.spice"], cwd=d, capture_output=True)
    a = np.loadtxt(d / "n.dat", skiprows=1)
    f = a[:, 0]
    v = {n: a[:, 1 + 2 * i] + 1j * a[:, 2 + 2 * i] for i, n in enumerate(NODES)}
    return f, v

def report(tag, f, v):
    T = -v["out"] / v["inp"]                  # loop gain (inp -> out), sign so that T(0) > 0
    stages = {"A1 (inp->Vo1)": v["x1.vo_stg1"] / v["inp"], "A2p (Vo1->mp_dz)": v["x1.mp_dz"] / v["x1.vo_stg1"],
              "A2n (Vo1->mn_dz)": v["x1.mn_dz"] / v["x1.vo_stg1"], "A3 (gates->out)": v["out"] / v["x1.mp_dz"]}
    mag = 20 * np.log10(np.abs(T)); i0 = np.where((mag[:-1] >= 0) & (mag[1:] < 0))[0][0]; fu = f[i0]
    ph = np.degrees(np.unwrap(np.angle(T)))
    ph -= 360 * np.round(ph[0] / 360)
    print(f"{tag}: |T(0)| {mag[0]:.1f} dB, UGF {fu/1e6:.1f} MHz, PM {180 + ph[i0]:.1f}")
    for k, h in stages.items():
        m = 20 * np.log10(np.abs(h)); p = np.degrees(np.unwrap(np.angle(h))); p -= p[0]
        j = np.where(m < m[0] - 3)[0]
        f3 = f[j[0]] if len(j) else np.nan
        print(f"   {k:18s} DC {m[0]:6.1f} dB  f-3dB {f3/1e6:9.2f} MHz  extra phase at UGF {np.interp(fu, f, p):7.1f} deg")

if __name__ == "__main__":
    for corner, temp in (("mos_ss", -40), ("mos_tt", 27)):
        for view, lib, sub in (("sch", rp.BUILD / "lr_lib.spice", "RAMP_LR"),
                               ("pex", rp.BUILD / "postlayout" / "pex_lib.spice", "RAMP_LR_PEX")):
            f, v = run(f"st_{view}_{corner}_{temp}", lib, sub, corner, temp)
            report(f"{view} {corner[4:]} {temp}", f, v)
