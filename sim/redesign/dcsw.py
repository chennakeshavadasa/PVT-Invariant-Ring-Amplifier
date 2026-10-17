import sys, json, numpy as np, subprocess
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import v2
def sweep(p, name, corners=(("mos_tt", 27), ("mos_ff", 125), ("mos_ss", -40), ("mos_fs", 125))):
    f = v2.lib(p, name)
    out = {}
    for c, t in corners:
        d = v2.OUT / f"{name}_dc_{c}_{t}"; d.mkdir(exist_ok=True); (d / ".spiceinit").write_text(v2.SPI)
        (d / "tb.spice").write_text(f"""* dc sweep
.include {f}
{v2.rp.models(c)}.temp {t}
x1 VDD GND IBIAS VICM out out RAMP_V2
{v2.ref_src(p.get('ptat'))}
V1 VICM GND dc 0.825
V2 VDD GND dc 1.65
.nodeset v(x1.vctrln)=0.6 v(x1.vo_stg1)=0.72 v(x1.net2)=0.72 v(out)=0.825
.control
set wr_singlescale
set wr_vecnames
dc V1 0.725 0.925 0.05
wrdata {d}/dc.dat v(out) v(x1.net3) v(x1.it1)
quit
.endc
.end
""")
        subprocess.run(["ngspice", "-b", "tb.spice"], cwd=d, capture_output=True)
        r = v2.rp.read(d / "dc.dat")
        err = 1e3 * (r["v(out)"] - r["v-sweep"])
        out[(c, t)] = (err, r["v(x1.net3)"], r["v(x1.it1)"])
    return out
if __name__ == "__main__":
    base = dict(R=25e3, tail=40, ld_m=4, itrim=15e-6, ptat="cgm", servo="none", mn3_w=1.15, mn3_l=0.5, pP=1, nP=6, sP=6,
                mdz_l=0.3, kN=3, mpr_m=1, iref=1, Cn=10e-12)
    for name, p in (("dc_diode", base), ("dc_mirror", dict(base, cmfb="mirror")),
                    ("dc_mirror_tl", dict(base, cmfb="mirror", tl_w=4.0, tl_l=1.0))):
        out = sweep(p, name)
        for (c, t), (err, cm, tail) in out.items():
            print(f"{name:14s} {c[4:]} {t:4}: err over 0.725..0.925 V: " + " ".join(f"{e:6.2f}" for e in err) +
                  f" mV | gain error {abs(err[-1]-err[0])/200*100:.2f} % | CM {cm[0]:.3f}->{cm[-1]:.3f} tail {tail[-1]:.3f}")
