import sys, json, subprocess
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import numpy as np
import v2, chk
def loop_at(p, name, corner, temp, which="reg"):
    f = v2.with_par(v2.lib(p, name)); t = f.read_text()
    if which == "reg":
        t = t.replace("XMN_DZ_STG2_3P n2b VCTRLN GND", "XMN_DZ_STG2_3P n2b vbrk GND")
        t = t.replace(".ends", "Vpb2 prb vbrk 0\nVpb1 prb VCTRLN dc 0 ac 1\nIpb1 GND prb dc 0 ac 0\n.ends")
    else:   # servo: break between VSV and the trim divider
        t = t.replace("XXRTA VSV V1_CM", "XXRTA vbrk V1_CM").replace("XRTA VSV V1_CM", "XRTA vbrk V1_CM")
        t = t.replace(".ends", "Vpb2 prb vbrk 0\nVpb1 prb VSV dc 0 ac 1\nIpb1 GND prb dc 0 ac 0\n.ends")
    g = f.with_name(f.stem + f"_{which}l.spice"); g.write_text(t)
    d = v2.OUT / f"{name}_{which}l_{corner}_{temp}"; d.mkdir(exist_ok=True); (d / ".spiceinit").write_text(v2.SPI)
    (d / "tb.spice").write_text(f"""* {which} loop
.include {g}
{v2.rp.models(corner)}.temp {temp}
x1 VDD GND IBIAS VICM out out RAMP_V2
{v2.ref_src(p.get('ptat'))}
V1 VICM GND dc 0.825
V2 VDD GND dc 1.65
C1 out GND 50p
.nodeset v(x1.vctrln)=0.6 v(x1.vo_stg1)=0.72 v(x1.net2)=0.72 v(out)=0.825
.control
set wr_singlescale
set wr_vecnames
ac dec 20 10 1G
alter @v.x1.vpb1[acmag]=0
alter @i.x1.ipb1[acmag]=1
ac dec 20 10 1G
let mb = 1/(ac1.v(x1.prb) + ac2.i(v.x1.vpb2)) - 1
let mbr = real(mb)
let mbi = imag(mb)
wrdata {d}/loop.dat mbr mbi
quit
.endc
.end
""")
    subprocess.run(["ngspice", "-b", "tb.spice"], cwd=d, capture_output=True)
    return v2.rp.loop_metrics(d)
if __name__ == "__main__":
    for spec in sys.argv[1:]:
        k, v = spec.split("=", 1); p = dict(chk.BASE, **json.loads(v))
        for which in ("reg", "servo"):
            for c, t in (("mos_tt", 27), ("mos_ss", -40), ("mos_ff", 125)):
                m = loop_at(p, "rl_" + k, c, t, which)
                print(f"{k:6s} {which:5s} {c[4:]} {t:4}: A0 {m['a0_db']:.1f} dB UGF {m['ugf_hz']/1e3:.1f} kHz PM {m['pm_deg']:.1f} GM {m['gm_db']:.1f}", flush=True)
