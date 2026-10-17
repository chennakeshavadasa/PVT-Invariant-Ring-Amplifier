"""OP currents of the low-current bias chain over corners."""
import sys, json
from concurrent.futures import ThreadPoolExecutor
import v2, chk
T2 = {"cmfb":"diode","reg":"miller","servo":"miller","Cn":1e-15,"ccr":2e-12,"reg_l":"lo:16","srv_l":"lo:16"}
cs = [("mos_tt", 27), ("mos_ss", -40), ("mos_sf", -40), ("mos_ff", 125), ("mos_fs", 125), ("mos_tt", -40), ("mos_tt", 125)]
def probe(p, name):
    f = v2.with_par(v2.lib(p, name)); t = f.read_text()
    t = t.replace("XXRG5 XRGt ", "VXRGT XRGt XRGt5 0\nXXRG5 XRGt5 ").replace("XXSV5 XSVt ", "VXSVT XSVt XSVt5 0\nXXSV5 XSVt5 ")
    t = t.replace("XMBL0 nlo nlo", "VNLO nlo nlo5 0\nXMBL0 nlo5 nlo").replace("XMBL3 nlo nlo", "VNLO nlo nlo5 0\nXMBL3 nlo5 nlo")
    t = t.replace("XXRG5a XRGt ", "VXRGT XRGt XRGt5 0\nXXRG5a XRGt5 ").replace("XXSV5a XSVt ", "VXSVT XSVt XSVt5 0\nXXSV5a XSVt5 ")
    f.write_text(t)
    def one(ct):
        c, T = ct; d = v2.OUT / f"{name}_ip_{c[4:]}_{T}"
        txt = v2.tb(f, d, c, T, ptat=p.get("ptat"), tran=False, ac=False,
                    extra_save="i(v.x1.vxrgt) i(v.x1.vxsvt) i(v.x1.vnlo)")
        v2.run(d, txt)
        o = v2.rp.read(d / "op.dat")
        return {k: float(o[k][0]) for k in o if k != "time"}
    with ThreadPoolExecutor(8) as ex:
        return dict(zip(cs, ex.map(one, cs)))
if __name__ == "__main__":
    for a in sys.argv[1:]:
        k, v = a.split("=", 1); p = dict(chk.BASE, **dict(T2, **json.loads(v)))
        for (c, T), o in probe(p, "ip_" + k).items():
            print(f"{k:5} {c[4:]} {T:4}: nlo {o['i(v.x1.vnlo)']*1e9:7.2f} nA  reg tail {o['i(v.x1.vxrgt)']*1e9:7.3f} nA  servo tail {o['i(v.x1.vxsvt)']*1e9:7.3f} nA  IQ {o['i(v.x1.viq)']*1e6:.2f} uA VCN {o['v(x1.vctrln)']:.3f}")
