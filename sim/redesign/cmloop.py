import sys, json, subprocess
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import numpy as np
import v2, chk
def cmfb_loop(p, name, corner, temp):
    f = v2.with_par(v2.lib(p, name))
    t = f.read_text()
    t = t.replace("XMP1 net2 vcmfb GND", "XMP1 net2 vcmg GND").replace("XMP2 Vo_STG1 vcmfb GND", "XMP2 Vo_STG1 vcmg GND")
    t = t.replace("XRCL vcmfb vcmlp", "XRCL vcmg vcmlp")
    t = t.replace(".ends", "Vpb2 prb vcmg 0\nVpb1 prb vcmfb dc 0 ac 1\nIpb1 GND prb dc 0 ac 0\n.ends")
    g = f.with_name(f.stem + "_cml.spice"); g.write_text(t)
    d = v2.OUT / f"{name}_cml_{corner}_{temp}"; d.mkdir(exist_ok=True); (d / ".spiceinit").write_text(v2.SPI)
    (d / "tb.spice").write_text(f"""* cmfb loop
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
ac dec 40 1 10G
alter @v.x1.vpb1[acmag]=0
alter @i.x1.ipb1[acmag]=1
ac dec 40 1 10G
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
        for c, t in (("mos_tt", 27), ("mos_ss", -40), ("mos_ff", 125)):
            m = cmfb_loop(p, "cm_" + k, c, t)
            print(f"{k:10s} {c[4:]} {t:4}: CMFB loop A0 {m['a0_db']:.1f} dB UGF {m['ugf_hz']/1e6:.1f} MHz PM {m['pm_deg']:.1f} GM {m['gm_db']:.1f}")
