"""Parametric prototype of RAMP v2 (direct deadzone regulation, high-gain stage 1).

Ports as RAMP_LR: VDD GND IBIAS minus plus Vout.  Bias units are 0.5/8-um NMOS at 1 uA.
"""
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ramp_pvt as rp  # noqa: E402
import montecarlo as mcm  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "build" / "redesign"
OUT.mkdir(parents=True, exist_ok=True)

SPI = (Path.home() / ".spiceinit").read_text() + "\nset num_threads=1\n"
RSQ = 100e3 / 33.7          # rhigh ohm per um length at W = 0.5 um

DEF = dict(
    s1_w=2.5, s1_l=0.5, s1_m=8,        # input pair finger W/L and fingers per side (lv pmos)
    tail=20,                           # stage-1 tail current (uA, even)
    ld_w=1.0, ld_l=2.0, ld_m=2,        # stage-1 loads (lv nmos), fingers per side
    R=100e3,                           # stage-1 load / CM-sense resistors R1, R3
    mc_w=2.0, mc_l=1.0, mc_m=2,        # CMFB pair (lv pmos)
    cm_tail=10,                        # CMFB tail (uA)
    kN=1,                              # VDZN inverter multiplier (drives MN3)
    pP=2, nP=4, sP=4,                  # VDZP inverter (drives MP3): PMOS, NMOS and starve-NMOS fingers
    mp3_w=4.5, mp3_m=4, mn3_m=4,       # output stage: MP3 fingers of mp3_w/0.5, MN3 fingers of mn3_w/mn3_l
    mn3_w=2.3, mn3_l=1.0,
    mpr_m=1, iref=1,                   # MP_R fingers (mp3_w/0.5) and its current (uA): I_Q = iref*mp3_m/mpr_m
    ota_w=2.0, ota_l=2.0, ota_m=2,     # NOTA input pair (lv nmos) per side
    ota_tail=2,                        # NOTA tail (uA)
    Rs=1e6,                            # isolation resistor mp_dz -> NOTA input
    Cn=0.5e-12,                        # decoupling on VCTRLN
    istarve=3,                         # current in the VCTRLP diode (uA); diode = 1 plv unit
    trip="N",                          # trip-point replica: copy of the VDZN inverter
    reg="ideal", greg=1.3e-6,          # regulation: "ideal" integrator (gm greg into Cn) or "ota"
    casc=False, cas_w=2.0, cas_l=0.13, cas_m=2, vcas=0.58,   # PMOS cascode on the input pair
    cmref="trip", Rlp=2e6, Clp=1e-12,                        # CMFB reference: "servo" (LPF of Vo_STG1) or "trip"
    servo="none", gsv=1e-6, csv=1e-12, itrim=3e-6,
    cmfb="diode", cml_w=1.0, cml_l=2.0, ccm=0.0, rcm=0,     # CMFB load: "diode" (low gain) or "mirror" (+ rcm across)
    cmsense="net3",                                          # CMFB senses net3 (output CM) or net2 (non-signal output only)
    cmsplit=False, rcl=1e6, ccl=0.5e-12,                     # Vo_STG1-side load gate through an RC low-pass
    tl_w=1.0, tl_l=2.0,                                      # PMOS tail-mirror unit (2 uA each)
    ccr=1e-12, reg_l=24, reg_w=1.0, rz=33e3,                 # regulation Miller integrator: Cc, tail-device L (0.5/L), pair W
    ccs=2e-12, srv_l=24, rta=1e6, rtb=150e3,                 # offset servo: Cc, tail-device L, trim divider          # offset servo: "none" or "ideal" (integrates Vo1 - net2)
    mdz_l=0.13,                        # length of the VDZP starve device
)


def lib(p, name):
    q = dict(DEF, **p)
    def miller(pre, inp, inm, out, ccv, itail_l, w_in, l_in):
        """Two-stage Miller integrator: NMOS pair (gate inp raises out), PMOS mirror, PMOS CS + NMOS sink."""
        return (f"X{pre}1 {pre}d1 {inm} {pre}t GND sg13_lv_nmos w={w_in}u l={l_in}u ng=1 m=1\n"
                f"X{pre}2 {pre}o1 {inp} {pre}t GND sg13_lv_nmos w={w_in}u l={l_in}u ng=1 m=1\n"
                f"X{pre}3 {pre}d1 {pre}d1 VDD VDD sg13_lv_pmos w=1u l=2u ng=1 m=1\n"
                f"X{pre}4 {pre}o1 {pre}d1 VDD VDD sg13_lv_pmos w=1u l=2u ng=1 m=1\n"
                f"X{pre}5 {pre}t IBIAS GND GND sg13_lv_nmos w=0.5u l={itail_l}u ng=1 m=1\n"
                f"X{pre}6 {out} {pre}o1 VDD VDD sg13_lv_pmos w=1u l=1u ng=1 m=1\n"
                f"X{pre}7 {out} IBIAS GND GND sg13_lv_nmos w=0.5u l=8u ng=1 m=1\n"
                f"X{pre}Z {out} {pre}z GND rhigh w=0.5e-6 l={q['rz'] / RSQ:.4g}e-6 m=1 b=0\n"
                f"C{pre}C {pre}z {pre}o1 {ccv}")
    rl = q["R"] / RSQ
    mpc = q["ld_m"] * q["cm_tail"] // q["tail"]          # CMFB diodes : loads = CMFB tail : stage-1 tail
    cmsense = q["cmsense"]
    vo1gate = "vcmlp" if q["cmsplit"] else "vcmfb"
    if q["cmfb"] == "diode":
        assert mpc >= 1 and mpc * q["tail"] == q["ld_m"] * q["cm_tail"], "load/diode ratio"
    nseg = int(np.ceil(rl / 10))
    t = f"""* RAMP v2 prototype {name}
.subckt RAMP_V2 VDD GND IBIAS minus plus Vout
* ---- bias: NMOS mirror of 0.5/8 units; PMOS mirror for the stage-1 and CMFB tails ------------
XMB0 IBIAS IBIAS GND GND sg13_lv_nmos w=0.5u l=8u ng=1
XMB2 pb IBIAS GND GND sg13_lv_nmos w=0.5u l=8u ng=1 m=2
XMB3 inota IBIAS GND GND sg13_lv_nmos w=0.5u l=8u ng=1 m={q['ota_tail']}
XMB4 irn IBIAS GND GND sg13_lv_nmos w=0.5u l=8u ng=1 m={q['iref']}
XMB5 VCTRLP IBIAS GND GND sg13_lv_nmos w=0.5u l=8u ng=1 m={q['istarve']}
XMBP0 pb pb VDD VDD sg13_lv_pmos w=1u l=2u ng=1 m=1
XMBP1 it1 pb VDD VDD sg13_lv_pmos w=1u l=2u ng=1 m={q['tail'] // 2}
XMBP2 icm pb VDD VDD sg13_lv_pmos w=1u l=2u ng=1 m={q['cm_tail'] // 2}
* ---- stage 1: PMOS input pair, NMOS loads, rhigh CM sense, PMOS-pair CMFB -----------------
{{s1pair}}
XMP1 net2 vcmfb GND GND sg13_lv_nmos w={q['ld_w']}u l={q['ld_l']}u ng=1 m={q['ld_m']}
XMP2 Vo_STG1 {vo1gate} GND GND sg13_lv_nmos w={q['ld_w']}u l={q['ld_l']}u ng=1 m={q['ld_m']}
XR1 net2 net3 GND rhigh w=0.5e-6 l={rl:.4g}e-6 m=1 b=0
XR3 Vo_STG1 net3 GND rhigh w=0.5e-6 l={rl:.4g}e-6 m=1 b=0
XMC1 vcmfb V1_CM icm VDD sg13_lv_pmos w={q['mc_w']}u l={q['mc_l']}u ng=1 m={q['mc_m']}
XMC2 dB {cmsense} icm VDD sg13_lv_pmos w={q['mc_w']}u l={q['mc_l']}u ng=1 m={q['mc_m']}
{{cmfbload}}
{{cmref}}
* ---- stage 2 ------------------------------------------------------------------------
XMN_STG2_3N1 mn_dz Vo_STG1 GND GND sg13_lv_nmos w=0.15u l=0.13u ng=1 m={q['kN']}
XMN_STG2_3P1 mn_dz Vo_STG1 n2a VDD sg13_lv_pmos w=0.15u l=0.13u ng=1 m={3 * q['kN']}
XMP_DZ_STG2_3N n2a VCTRLP VDD VDD sg13_lv_pmos w=0.15u l=0.13u ng=1 m={5 * q['kN']}
XMP_STG2_3P2 mp_dz Vo_STG1 n2b GND sg13_lv_nmos w=0.15u l=0.13u ng=1 m={q['nP']}
XMP_STG2_3P1 mp_dz Vo_STG1 VDD VDD sg13_lv_pmos w=0.15u l=0.13u ng=1 m={q['pP']}
XMN_DZ_STG2_3P n2b VCTRLN GND GND sg13_lv_nmos w=0.15u l={q['mdz_l']}u ng=1 m={q['sP']}
* ---- output stage ---------------------------------------------------------------------
XM1 Vout mn_dz GND GND sg13_hv_nmos w={q['mn3_w']}u l={q['mn3_l']}u ng=1 m={q['mn3_m']}
VIQ VDD vdd_q 0
XM2 Vout mp_dz vdd_q VDD sg13_hv_pmos w={q['mp3_w']}u l=0.5u ng=1 m={q['mp3_m']}
* ---- direct deadzone regulation (P side) ---------------------------------------------
XMP_R irn irn VDD VDD sg13_hv_pmos w={q['mp3_w']}u l=0.5u ng=1 m={q['mpr_m']}
XRS mp_dz vgps GND rhigh w=0.5e-6 l={q['Rs'] / RSQ:.4g}e-6 m=1 b=0
{{ota}}
CCN VCTRLN GND {q["Cn"]}
* ---- fixed starve bias of the VDZN inverter ---------------------------------------------
XMD VCTRLP VCTRLP VDD VDD sg13_lv_pmos w=0.15u l=0.13u ng=1 m=1
.ends
"""
    if q["cmref"] == "servo":
        cmref = (f"* ---- CMFB reference: Vo_STG1 low-pass filtered (DC servo) ----\n"
                 f"XRLP Vo_STG1 V1_CM GND rhigh w=0.5e-6 l={q['Rlp'] / RSQ:.4g}e-6 m=1 b=0\n"
                 f"CLP V1_CM GND {q['Clp']}")
    else:
        cmref = (f"XMT1 V1_CM V1_CM GND GND sg13_lv_nmos w=0.15u l=0.13u ng=1 m={q['kN']}\n"
                 f"XMT2 V1_CM V1_CM ntr VDD sg13_lv_pmos w=0.15u l=0.13u ng=1 m={3 * q['kN']}\n"
                 f"XMT3 ntr VCTRLP VDD VDD sg13_lv_pmos w=0.15u l=0.13u ng=1 m={5 * q['kN']}")
    t = t.replace("{cmref}", cmref)
    if q["cmfb"] == "mirror":     # high-gain CMFB: NMOS mirror load, high-impedance output vcmfb
        cl = (f"XMPC1 vcmfb dB GND GND sg13_lv_nmos w={q['cml_w']}u l={q['cml_l']}u ng=1 m=1\n"
              f"XMPC2 dB dB GND GND sg13_lv_nmos w={q['cml_w']}u l={q['cml_l']}u ng=1 m=1\n"
              f"CCM vcmfb GND {q['ccm']}" + (f"\nXRCM vcmfb dB GND rhigh w=0.5e-6 l={q['rcm'] / RSQ:.4g}e-6 m=1 b=0" if q['rcm'] else ""))
    else:
        cl = (f"XMPC1 vcmfb vcmfb GND GND sg13_lv_nmos w={q['ld_w']}u l={q['ld_l']}u ng=1 m={mpc}\n"
              f"XMPC2 dB dB GND GND sg13_lv_nmos w={q['ld_w']}u l={q['ld_l']}u ng=1 m={mpc}")
    if q["cmsplit"]:
        cl += (f"\nXRCL vcmfb vcmlp GND rhigh w=0.5e-6 l={q['rcl'] / RSQ:.4g}e-6 m=1 b=0\nCCL vcmlp GND {q['ccl']}")
    t = t.replace("{cmfbload}", cl)
    t = t.replace("XMBP0 pb pb VDD VDD sg13_lv_pmos w=1u l=2u ng=1 m=1",
                  f"XMBP0 pb pb VDD VDD sg13_lv_pmos w={q['tl_w']}u l={q['tl_l']}u ng=1 m=1")
    t = t.replace(f"XMBP1 it1 pb VDD VDD sg13_lv_pmos w=1u l=2u ng=1 m={q['tail'] // 2}",
                  f"XMBP1 it1 pb VDD VDD sg13_lv_pmos w={q['tl_w']}u l={q['tl_l']}u ng=1 m={q['tail'] // 2}")
    t = t.replace(f"XMBP2 icm pb VDD VDD sg13_lv_pmos w=1u l=2u ng=1 m={q['cm_tail'] // 2}",
                  f"XMBP2 icm pb VDD VDD sg13_lv_pmos w={q['tl_w']}u l={q['tl_l']}u ng=1 m={q['cm_tail'] // 2}")
    if q["servo"] == "miller":
        t = t.replace("XMT1 V1_CM V1_CM GND", "XMT1 vtrip vtrip GND").replace("XMT2 V1_CM V1_CM ntr", "XMT2 vtrip vtrip ntr")
        t = t.replace(".ends", miller("XSV", "Vo_STG1", "net2", "VSV", q["ccs"], q["srv_l"], 1.0, 1.0) + "\n"
                      f"XRTA VSV V1_CM GND rhigh w=0.5e-6 l={q['rta'] / RSQ:.4g}e-6 m=1 b=0\n"
                      f"XRTB vtrip V1_CM GND rhigh w=0.5e-6 l={q['rtb'] / RSQ:.4g}e-6 m=1 b=0\n.ends")
    if q["servo"] == "ideal":
        # integrate the stage-1 differential output; inject a bounded trim current into the CMFB reference
        t = t.replace(".ends", f"GSV GND VSV Vo_STG1 net2 {q['gsv']}\nCSV VSV GND {q['csv']}\nRSV VSV GND 1e9\n"
                               f"BTR GND V1_CM I={q['itrim']}*tanh(V(VSV))\n.ends")
    if q["casc"]:
        s1pair = (f"XMN1 c2 minus it1 VDD sg13_lv_pmos w={q['s1_w']}u l={q['s1_l']}u ng=1 m={q['s1_m']}\n"
                  f"XMN2 c1 plus it1 VDD sg13_lv_pmos w={q['s1_w']}u l={q['s1_l']}u ng=1 m={q['s1_m']}\n"
                  f"XMK1 net2 vcas c2 VDD sg13_lv_pmos w={q['cas_w']}u l={q['cas_l']}u ng=1 m={q['cas_m']}\n"
                  f"XMK2 Vo_STG1 vcas c1 VDD sg13_lv_pmos w={q['cas_w']}u l={q['cas_l']}u ng=1 m={q['cas_m']}\n"
                  f"VCAS vcas GND {q['vcas']}")
    else:
        s1pair = (f"XMN1 net2 minus it1 VDD sg13_lv_pmos w={q['s1_w']}u l={q['s1_l']}u ng=1 m={q['s1_m']}\n"
                  f"XMN2 Vo_STG1 plus it1 VDD sg13_lv_pmos w={q['s1_w']}u l={q['s1_l']}u ng=1 m={q['s1_m']}")
    t = t.replace("{s1pair}", s1pair)
    if q["reg"] == "miller":
        ota = miller("XRG", "vgps", "irn", "VCTRLN", q["ccr"], q["reg_l"], q["reg_w"], 1.0)
    elif q["reg"] == "ideal":
        ota = f"GREG GND VCTRLN vgps irn {q['greg']}\nRREG VCTRLN GND 1e9"
    else:
        ota = (f"XNM1 nota2 vgps inota GND sg13_lv_nmos w={q['ota_w']}u l={q['ota_l']}u ng=1 m={q['ota_m']}\n"
               f"XNM2 VCTRLN irn inota GND sg13_lv_nmos w={q['ota_w']}u l={q['ota_l']}u ng=1 m={q['ota_m']}\n"
               "XNM3 VCTRLN nota2 VDD VDD sg13_hv_pmos w=0.5u l=0.75u ng=1 m=1\n"
               "XNM4 nota2 nota2 VDD VDD sg13_hv_pmos w=0.5u l=0.75u ng=1 m=1")
    t = t.replace("{ota}", ota)
    f = OUT / f"lib_{name}.spice"
    f.write_text(t)
    return f


PAR = {"Vo_STG1": 12e-15, "mp_dz": 10e-15, "mn_dz": 8e-15}


def with_par(f):
    t = f.read_text().replace(".ends", "".join(f"Cpar_{n} {n} GND {c}\n" for n, c in PAR.items()) + ".ends")
    g = f.with_name(f.stem + "_par.spice")
    g.write_text(t)
    return g


def ref_src(ptat):
    """Reference current into IBIAS: constant 1 uA (False), PTAT (True or "ptat") or constant-gm
    ("cgm": I = 1 uA * T/300.15 K * R0/R, R a dummy 100-kOhm rhigh at the same corner)."""
    if ptat == "cgm":
        return ("XRREF rref1 GND GND rhigh w=0.5e-6 l=33.7e-6 m=1 b=0\nVRREF rref1 GND 1\n"
                "B_B VDD IBIAS I=1u*(temper+273.15)/300.15*1e5*abs(i(VRREF))")
    return rp.ibias_src(bool(ptat))


def tb(f, d, corner, temp, vdd=1.65, seed=None, models=None, tran=True, ac=True, ptat=False, extra_save=""):
    lo, hi = 0.725, 0.925
    return f"""* tb
{f'.options seed={seed}' if seed else ''}
.include {f}
{models or rp.models(corner)}.temp {temp}
x1 VDD GND IBIAS VICM inp out RAMP_V2
{ref_src(ptat)}
V1 VICM GND dc 0.825 ac 0 {f'pwl(0 {lo} 100n {lo} 101n {hi} 1.6u {hi})' if tran else ''}
V2 VDD GND dc {vdd}
C1 out GND 50p
Vprobe2 probe inp 0
Vprobe1 probe out dc 0 ac 1
Iprobe1 GND probe dc 0 ac 0
.nodeset v(x1.vctrln)=0.8 v(x1.vo_stg1)=0.72 v(x1.net2)=0.72 v(out)=0.825
.control
set wr_singlescale
set wr_vecnames
op
wrdata {d}/op.dat v(out) i(v.x1.viq) i(v2) v(x1.vctrln) v(x1.vctrlp) v(x1.vo_stg1) v(x1.v1_cm) v(x1.mp_dz) v(x1.mn_dz) v(x1.net2) {extra_save}
{rp.CTRL_AC.format(d=d) if ac else ''}
{'alter @vprobe1[acmag]=0' if ac else ''}
{'tran 0.1n 1.6u 0 0.25n' if tran else ''}
{f'wrdata {d}/tran.dat v(out)' if tran else ''}
quit
.endc
.end
"""


def run(d, text):
    d.mkdir(parents=True, exist_ok=True)
    (d / ".spiceinit").write_text(SPI)
    (d / "tb.spice").write_text(text)
    subprocess.run(["ngspice", "-b", "tb.spice"], cwd=d, capture_output=True)


def metrics(d, tran=True):
    o = rp.read(d / "op.dat")
    g = lambda k: float(o[k][0])
    r = dict(off_mv=1e3 * (g("v(out)") - 0.825), iq=1e6 * g("i(v.x1.viq)"), itot=-1e6 * g("i(v2)"),
             vctrln=g("v(x1.vctrln)"), vctrlp=g("v(x1.vctrlp)"), vo1=g("v(x1.vo_stg1)"), v1cm=g("v(x1.v1_cm)"),
             vgp=g("v(x1.mp_dz)"), vgn=g("v(x1.mn_dz)"))
    if (d / "loop.dat").exists():
        lm = rp.loop_metrics(d)
        r.update(ugf=lm["ugf_hz"] / 1e6, pm=lm["pm_deg"], gm=lm["gm_db"], a0=lm["a0_db"])
    if tran and (d / "tran.dat").exists():
        tr = rp.read(d / "tran.dat")
        t, v = tr["time"], tr["v(out)"]
        err = np.abs(v - v[-1]) / 0.2
        m = t > 100e-9
        bad = np.where(err[m] > 1e-3)[0]
        r["ts01"] = (t[m][bad[-1]] - 100e-9) * 1e9 if len(bad) else 0.0
        r["osc"] = 1e3 * np.ptp(v[t > 1.3e-6])
    return r


BOTH = None
CORNERS = (("mos_ss", -40), ("mos_sf", -40), ("mos_tt", -40), ("mos_tt", 27), ("mos_ff", 125), ("mos_fs", 125),
           ("mos_ss", 125))


def evaluate(p, name, par=True, corners=CORNERS, mc_n=0, mc_set="mismatch"):
    f = lib(p, name)
    fp = with_par(f) if par else f
    ptat = p.get("ptat")
    jobs = [(OUT / f"{name}_{c[4:]}_{t}", tb(fp, OUT / f"{name}_{c[4:]}_{t}", c, t, ptat=ptat)) for c, t in corners]
    jobs += [(OUT / f"{name}_mc{k}", tb(f, OUT / f"{name}_mc{k}", "mos_tt", 27, seed=k + 1, ptat=ptat,
                                        models=mcm.SETS[mc_set] if mc_set != "both" else BOTH,
                                        tran=False, ac=False)) for k in range(mc_n)]
    with ThreadPoolExecutor(15) as ex:
        list(ex.map(lambda j: run(*j), jobs))
    out = {}
    for (c, t) in corners:
        try:
            out[(c, t)] = metrics(OUT / f"{name}_{c[4:]}_{t}")
        except Exception as e:
            out[(c, t)] = dict(err=str(e)[:60])
    mcres = []
    for k in range(mc_n):
        try:
            mcres.append(metrics(OUT / f"{name}_mc{k}", tran=False))
        except Exception:
            pass
    return out, mcres


def show(name, out, mcres):
    print(f"== {name}")
    for (c, t), r in out.items():
        if "err" in r:
            print(f"  {c[4:]} {t:4}: FAILED {r['err']}")
            continue
        print(f"  {c[4:]} {t:4}: UGF {r.get('ugf', np.nan):5.1f} MHz PM {r.get('pm', np.nan):5.1f} GM {r.get('gm', np.nan):5.1f} "
              f"A0 {r.get('a0', np.nan):5.1f} | IQ {r['iq']:6.2f} Itot {r['itot']:5.0f} off {r['off_mv']:6.2f} mV "
              f"| ts {r.get('ts01', np.nan):5.0f} ns osc {r.get('osc', np.nan):5.2f} | Vo1 {r['vo1']:.3f} V1CM {r['v1cm']:.3f} "
              f"VCN {r['vctrln']:.3f} VCP {r['vctrlp']:.3f} VGP {r['vgp']:.3f} VGN {r['vgn']:.3f}")
    if mcres:
        off = np.array([r["off_mv"] for r in mcres])
        iq = np.array([r["iq"] for r in mcres])
        print(f"  MC mismatch ({len(mcres)}): offset mean {off.mean():.2f} sigma {off.std():.2f} mV (+-3s span {6 * off.std():.1f} mV);"
              f" IQ P5..P95 {np.percentile(iq, 5):.3g}..{np.percentile(iq, 95):.3g} uA, sigma/mean {iq.std() / iq.mean() * 100:.0f} %")


if __name__ == "__main__":
    import json
    name = sys.argv[1]
    p = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    mc_n = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    show(name, *evaluate(p, name, mc_n=mc_n))
