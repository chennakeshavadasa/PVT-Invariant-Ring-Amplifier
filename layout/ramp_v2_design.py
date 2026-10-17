"""Single source of truth for RAMP_V2, the redesigned ring amplifier (IHP SG13G2).

RAMP_V2 is the circuit frozen in sim/redesign (v2.py + v2_final.json), written out
device by device:

  * stage 1: PMOS input pair (16 x 2.5/0.5 um per side, 40-uA tail), NMOS loads with a
    diode CMFB (PMOS pair MC1/MC2), 17-kOhm rhigh loads R1/R3 that also sense the CM;
  * stage 2: the two current-starved inverters of RAMP_LR; the VDZN inverter has a fixed
    starve bias (VCTRLP diode MD), the VDZP inverter is starved by VCTRLN;
  * output stage MN3 4 x 1.15/1.0 um, MP3 4 x 4.5/0.5 um (hv devices);
  * REG_V2: direct deadzone regulation - the MP3 gate (through R_S) is compared with the
    gate of MP_R (2 fingers of MP3 at 2 x I_BIAS) by a two-stage Miller integrator with a
    0.9-nA tail and a 4-pF MIM; it sets VCTRLN, so I_Q = 4 x I_BIAS;
  * SERVO_V2: offset servo - a Miller integrator of Vo1 - Vo1n (1.7-nA tail, 1-pF MIM)
    trims the CMFB reference V1_CM through the rhigh divider RTA/RTB around the
    stage-2 trip-point replica (TRIP_V2, one third of the VDZN inverter);
  * BIAS_V2: NMOS mirror of 0.5/8-um units from I_BIAS, PMOS mirror (4/1 um) for the
    stage-1 and CMFB tails, and the nA divider I_BIAS -> 1/13 (hv PMOS 1/1 um) -> 1/14
    (hv NMOS 0.3/2 um units); the integrator tails are series stacks of that unit.

gen_schematics.py v2 turns CELLS into xschem schematics/symbols, gen_layout.py (with
RAMP_DESIGN=ramp_v2_design) turns STRIPS/RES_BLOCKS/MIMS/BANDS into the layout.
"""

KINDS = {
    "nlv": ("sg13g2_pr/sg13_lv_nmos.sym", "sg13_lv_nmos", "nmos"),
    "plv": ("sg13g2_pr/sg13_lv_pmos.sym", "sg13_lv_pmos", "pmos"),
    "nhv": ("sg13g2_pr/sg13_hv_nmos.sym", "sg13_hv_nmos", "nmosHV"),
    "phv": ("sg13g2_pr/sg13_hv_pmos.sym", "sg13_hv_pmos", "pmosHV"),
    "rhigh": ("sg13g2_pr/rhigh.sym", "rhigh", "rhigh"),
    "cmim": ("sg13g2_pr/cap_cmim.sym", "cap_cmim", "cmim"),
}


def M(name, kind, d, g, s, b, w, l, m=1):
    return dict(name=name, kind=kind, pins=dict(D=d, G=g, S=s, B=b), w=w, l=l, m=m)


def R(name, p, n, w, l, body="GND"):
    return dict(name=name, kind="rhigh", pins=dict(P=p, M=n), w=w, l=l, m=1, body=body)


def C(name, top, bottom, w, l):
    """MIM capacitor: c0 = PLUS = top plate (TopMetal1 side), c1 = MINUS = bottom plate (Metal5)."""
    return dict(name=name, kind="cmim", pins=dict(c0=top, c1=bottom), w=w, l=l, m=1)


def X(name, cell, **conn):
    return dict(name=name, kind="inst", cell=cell, conn=conn)


WB, LB = 0.5, 8.0          # NMOS bias unit (as RAMP_LR)
RU = 5.73                  # rhigh segment, W = 0.5 um: 17.0 kOhm
WU, LU = 0.3, 2.0          # nA-divider NMOS unit (hv)
CAP4, CAP1 = 51.6, 25.8    # MIM sides: 4.00 pF and 1.00 pF


def stack(pre, top, n, kind, gate, w, l):
    """n devices in series from `top` to GND, gate on `gate` (one unit each)."""
    nodes = [top] + [f"s{i}" for i in range(1, n)] + ["GND"]
    return [M(f"{pre}{chr(97 + i)}", kind, nodes[i], gate, nodes[i + 1], "GND", w, l) for i in range(n)]


def miller(pair_w, pair_l, n_tail, cap, inp, inm, out):
    """Two-stage Miller integrator (hv): NMOS pair (gate inp raises out), PMOS mirror,
    PMOS common source with a 0.5/8 NMOS sink, Miller MIM with a series rhigh (2 x RU)."""
    return ([M("M1", "nhv", "d1", inm, "t", "GND", pair_w, pair_l),
             M("M2", "nhv", "o1", inp, "t", "GND", pair_w, pair_l),
             M("M3", "phv", "d1", "d1", "VDD", "VDD", 1.0, 2.0),
             M("M4", "phv", "o1", "d1", "VDD", "VDD", 1.0, 2.0)]
            + stack("M5", "t", n_tail, "nhv", "nlo", WU, LU)
            + [M("M6", "phv", out, "o1", "VDD", "VDD", 1.0, 1.0),
               M("M7", "nlv", out, "IBIAS", "GND", "GND", WB, LB),
               R("RZ", out, "z", 0.5, round(2 * RU, 3)),
               C("CC", "o1", "z", cap, cap)])


CELLS = {
    "BIAS_V2": dict(
        title="Bias: NMOS mirror from IBIAS, PMOS tail mirror, nA divider, VCTRLP starve bias",
        ports=["VDD", "GND", "IBIAS", "it1", "icm", "irn", "VCTRLP", "nlo"],
        dirs=dict(IBIAS="in", it1="out", icm="out", irn="out", VCTRLP="out", nlo="out"),
        items=[
            M("MB0", "nlv", "IBIAS", "IBIAS", "GND", "GND", WB, LB, 1),
            M("MB2", "nlv", "pb", "IBIAS", "GND", "GND", WB, LB, 2),
            M("MB4", "nlv", "irn", "IBIAS", "GND", "GND", WB, LB, 2),
            M("MB5", "nlv", "VCTRLP", "IBIAS", "GND", "GND", WB, LB, 3),
            M("MBL0", "nlv", "plo", "IBIAS", "GND", "GND", WB, LB, 1),
            M("MBP0", "plv", "pb", "pb", "VDD", "VDD", 4.0, 1.0, 1),
            M("MBP1", "plv", "it1", "pb", "VDD", "VDD", 4.0, 1.0, 20),
            M("MBP2", "plv", "icm", "pb", "VDD", "VDD", 4.0, 1.0, 5),
            M("MBL1", "phv", "plo", "plo", "VDD", "VDD", 1.0, 1.0, 13),
            M("MBL2", "phv", "nlo", "plo", "VDD", "VDD", 1.0, 1.0, 1),
            M("MBL3", "nhv", "nlo", "nlo", "GND", "GND", WU, LU, 14),
            M("MD", "plv", "VCTRLP", "VCTRLP", "VDD", "VDD", 0.15, 0.13, 1),
        ]),
    "STG1_V2": dict(
        title="Stage 1: PMOS input pair, NMOS loads, rhigh loads/CM sense, diode CMFB",
        ports=["VDD", "GND", "inp", "inm", "Vo1", "Vo1n", "V1_CM", "it1", "icm"],
        dirs=dict(inp="in", inm="in", V1_CM="in", Vo1="out", Vo1n="out"),
        items=[
            M("MN1", "plv", "Vo1n", "inm", "it1", "VDD", 2.5, 0.5, 16),
            M("MN2", "plv", "Vo1", "inp", "it1", "VDD", 2.5, 0.5, 16),
            M("MP1", "nlv", "Vo1n", "vcmfb", "GND", "GND", 1.0, 2.0, 4),
            M("MP2", "nlv", "Vo1", "vcmfb", "GND", "GND", 1.0, 2.0, 4),
            R("R1", "Vo1n", "net3", 0.5, RU),
            R("R3", "Vo1", "net3", 0.5, RU),
            M("MC1", "plv", "vcmfb", "V1_CM", "icm", "VDD", 2.0, 1.0, 2),
            M("MC2", "plv", "dB", "net3", "icm", "VDD", 2.0, 1.0, 2),
            M("MPC1", "nlv", "vcmfb", "vcmfb", "GND", "GND", 1.0, 2.0, 1),
            M("MPC2", "nlv", "dB", "dB", "GND", "GND", 1.0, 2.0, 1),
        ]),
    "TRIP_V2": dict(
        title="Stage-2 trip-point replica (one third of the VDZN inverter, input = output)",
        ports=["VDD", "GND", "VCTRLP", "vtrip"],
        dirs=dict(VCTRLP="in", vtrip="out"),
        items=[
            M("MT1", "nlv", "vtrip", "vtrip", "GND", "GND", 0.15, 0.13, 1),
            M("MT2", "plv", "vtrip", "vtrip", "ntr", "VDD", 0.15, 0.13, 3),
            M("MT3", "plv", "ntr", "VCTRLP", "VDD", "VDD", 0.15, 0.13, 5),
        ]),
    "STG2_V2": dict(
        title="Stage 2: current-starved inverters (deadzone)",
        ports=["VDD", "GND", "Vin_2", "VCTRLP", "VCTRLN", "VDZP", "VDZN"],
        dirs=dict(Vin_2="in", VCTRLP="in", VCTRLN="in", VDZP="out", VDZN="out"),
        items=[
            M("MN_STG2_3N1", "nlv", "VDZN", "Vin_2", "GND", "GND", 0.15, 0.13, 3),
            M("MN_STG2_3P1", "plv", "VDZN", "Vin_2", "n2a", "VDD", 0.15, 0.13, 9),
            M("MP_DZ_STG2_3N", "plv", "n2a", "VCTRLP", "VDD", "VDD", 0.15, 0.13, 15),
            M("MP_STG2_3P2", "nlv", "VDZP", "Vin_2", "n2b", "GND", 0.15, 0.13, 6),
            M("MP_STG2_3P1", "plv", "VDZP", "Vin_2", "VDD", "VDD", 0.15, 0.13, 1),
            M("MN_DZ_STG2_3P", "nlv", "n2b", "VCTRLN", "GND", "GND", 0.15, 0.3, 6),
        ]),
    "REG_V2": dict(
        title="I_Q regulation: MP3 gate vs. MP_R gate, Miller integrator (0.9 nA, 4 pF) -> VCTRLN",
        ports=["VDD", "GND", "IBIAS", "nlo", "VDZP", "irn", "VCTRLN"],
        dirs=dict(IBIAS="in", nlo="in", VDZP="in", irn="inout", VCTRLN="out"),
        items=[M("MPR", "phv", "irn", "irn", "VDD", "VDD", 4.5, 0.5, 2),
               R("RS", "VDZP", "vgps", 0.5, round(30 * RU, 3))]
              + miller(4.0, 4.0, 6, CAP4, "vgps", "irn", "VCTRLN")),
    "SERVO_V2": dict(
        title="Offset servo: Miller integrator of Vo1 - Vo1n (1.7 nA, 1 pF) trims V1_CM",
        ports=["VDD", "GND", "IBIAS", "nlo", "Vo1", "Vo1n", "vtrip", "V1_CM"],
        dirs=dict(IBIAS="in", nlo="in", Vo1="in", Vo1n="in", vtrip="in", V1_CM="out"),
        items=miller(3.0, 3.0, 3, CAP1, "Vo1", "Vo1n", "VSV")
              + [R("RTA", "VSV", "V1_CM", 0.5, round(30 * RU, 3)),
                 R("RTB", "vtrip", "V1_CM", 0.5, round(4 * RU, 3))]),
    "RAMP_V2": dict(
        title="Ring amplifier v2: direct deadzone regulation and offset servo (IHP SG13G2)",
        ports=["VDD", "GND", "IBIAS", "minus", "plus", "Vout"],
        dirs=dict(IBIAS="in", minus="in", plus="in", Vout="out"),
        items=[
            X("xb", "BIAS_V2", VDD="VDD", GND="GND", IBIAS="IBIAS", it1="it1", icm="icm", irn="irn",
              VCTRLP="VCTRLP", nlo="nlo"),
            X("x1", "STG1_V2", VDD="VDD", GND="GND", inp="plus", inm="minus", Vo1="Vo_STG1", Vo1n="Vo1n",
              V1_CM="V1_CM", it1="it1", icm="icm"),
            X("xt", "TRIP_V2", VDD="VDD", GND="GND", VCTRLP="VCTRLP", vtrip="vtrip"),
            X("x2", "STG2_V2", VDD="VDD", GND="GND", Vin_2="Vo_STG1", VCTRLP="VCTRLP", VCTRLN="VCTRLN",
              VDZP="mp_dz", VDZN="mn_dz"),
            X("xr", "REG_V2", VDD="VDD", GND="GND", IBIAS="IBIAS", nlo="nlo", VDZP="mp_dz", irn="irn",
              VCTRLN="VCTRLN"),
            X("xs", "SERVO_V2", VDD="VDD", GND="GND", IBIAS="IBIAS", nlo="nlo", Vo1="Vo_STG1", Vo1n="Vo1n",
              vtrip="vtrip", V1_CM="V1_CM"),
            M("M1", "nhv", "Vout", "mn_dz", "GND", "GND", 1.15, 1.0, 4),
            M("M2", "phv", "Vout", "mp_dz", "VDD", "VDD", 4.5, 0.5, 4),
            X("xd", "DUMMY_V2", VDD="VDD", GND="GND"),
        ]),
}

# --------------------------------------------------------------------------
# Matched placement (see ramp_lr_design.py for the conventions): a strip is a row of
# fingers of one kind and W/L, a segment one multi-finger PCell with shared diffusions,
# "D" a dummy finger on the rail.
# --------------------------------------------------------------------------
_P1, _DZ, _IN = "x2.MP_STG2_3P1", "x2.MP_DZ_STG2_3N", "x2.MN_STG2_3P1"
_T3, _T2 = "xt.MT3", "xt.MT2"
_A, _B = "x1.MN1", "x1.MN2"
_LA, _LB = "x1.MP1", "x1.MP2"


def _inverter_chain(single, dz, inv):
    """single (VDD side), then the starve devices and the inverter devices interleaved so
    that every diffusion is shared; 15 starve and 9 inverter fingers."""
    return [single] + [dz, inv, inv, dz, dz, dz] * 3 + [dz, inv, inv, dz] + [dz, inv]


STRIPS = {
    # NMOS bias mirror, 0.5/8 um, gates on IBIAS
    "nb0": dict(kind="nlv", w=WB, l=LB, segs=[["D", "xb.MB4", "xb.MB4", "xb.MB0"], ["xb.MB2", "xb.MB2", "D"],
                                              ["xb.MBL0", "D"]]),
    "nb1": dict(kind="nlv", w=WB, l=LB, segs=[["D", "xb.MB5", "xb.MB5", "xb.MB5"], ["xr.M7", "D", "xs.M7"]]),
    # trip-point replica NMOS
    "trn": dict(kind="nlv", w=0.15, l=0.13, segs=[["D", "xt.MT1"], ["D"]]),
    # nA divider: diode bank (14 units) with the integrator tail stacks at its ends
    "nlo_a": dict(kind="nhv", w=WU, l=LU, segs=[["D"], [f"xr.M5{c}" for c in "abcdef"] + ["xb.MBL3"] * 8 + ["D"]]),
    "nlo_b": dict(kind="nhv", w=WU, l=LU, segs=[["D"] + ["xb.MBL3"] * 6 + ["xs.M5c", "xs.M5b", "xs.M5a"], ["D"]]),
    # integrator input pairs (hv) and PMOS parts
    "rg_in": dict(kind="nhv", w=4.0, l=4.0, segs=[["D"], ["xr.M1", "xr.M2"], ["D"]]),
    "sv_in": dict(kind="nhv", w=3.0, l=3.0, segs=[["D"], ["xs.M1", "xs.M2"], ["D"]]),
    "pmir": dict(kind="phv", w=1.0, l=2.0, segs=[["D"], ["xr.M3", "xr.M4"], ["xs.M3", "xs.M4"], ["D"]]),
    "p11": dict(kind="phv", w=1.0, l=1.0, segs=[["D"], ["xr.M6"] + ["xb.MBL1"] * 6 + ["xb.MBL2"],
                                                ["xs.M6"] + ["xb.MBL1"] * 7, ["D"]]),
    # NMOS signal row
    "s1n": dict(kind="nlv", w=1.0, l=2.0, segs=[["D"], [_LA, _LB, _LB, _LA, _LA, _LB, _LB, _LA],
                                                ["x1.MPC1", "D", "x1.MPC2"], ["D"]]),
    "s2n": dict(kind="nlv", w=0.15, l=0.13, segs=[["D", "x2.MN_STG2_3N1", "x2.MN_STG2_3N1", "x2.MN_STG2_3N1"],
                                                  ["x2.MP_STG2_3P2"] * 6, ["D"]]),
    "dzn": dict(kind="nlv", w=0.15, l=0.3, segs=[["D"] + ["x2.MN_DZ_STG2_3P"] * 6 + ["D"]]),
    "out_n": dict(kind="nhv", w=1.15, l=1.0, segs=[["D", "M1", "M1", "M1", "M1", "D"]]),
    # PMOS signal row
    "s1p": dict(kind="plv", w=2.5, l=0.5, segs=[["D"], [_A, _B, _B, _A] * 8, ["D"]]),
    "s2p": dict(kind="plv", w=0.15, l=0.13, segs=[["D"], _inverter_chain(_P1, _DZ, _IN), ["D"]]),
    "out_p": dict(kind="phv", w=4.5, l=0.5, segs=[["D", "M2", "M2", "xr.MPR", "xr.MPR", "M2", "M2", "D"]]),
    # PMOS tail mirror, CMFB pair, trip-point replica PMOS
    "pt": dict(kind="plv", w=4.0, l=1.0, segs=[["D"], ["xb.MBP2"] + ["xb.MBP1"] * 10 + ["xb.MBP2"] * 2
                                               + ["xb.MBP1"] * 10 + ["xb.MBP2"] * 2, ["xb.MBP0", "D"]]),
    "cm": dict(kind="plv", w=2.0, l=1.0, segs=[["D"], ["x1.MC1", "x1.MC2", "x1.MC2", "x1.MC1"], ["D"]]),
    "trp": dict(kind="plv", w=0.15, l=0.13, segs=[["D"], ["xb.MD", _T3, _T2, _T2, _T3, _T3, _T3, _T3, _T2], ["D"]]),
}

# rhigh arrays (W = 0.5 um, segments of RU in series; LVS merges them)
RES_BLOCKS = {
    "rhigh_a": dict(w=0.5, lengths=None, order=["xr.RS"] * 30 + ["xr.RZ"] * 2 + ["xs.RZ"] * 2),
    "rhigh_b": dict(w=0.5, lengths=None, order=["xs.RTA"] * 30 + ["xs.RTB"] * 4),
    "rhigh_c": dict(w=0.5, lengths=None, order=["x1.R1", "x1.R3"]),
}
for _b in RES_BLOCKS.values():
    _b["lengths"] = [RU] * len(_b["order"])

# MIM capacitors over the circuit: (instance, top-plate net, bottom-plate net, side)
MIMS = [dict(ref="xr.CC", top="xr.o1", bottom="xr.z", side=CAP4),
        dict(ref="xs.CC", top="xs.o1", bottom="xs.z", side=CAP1)]

BANDS = [
    (["nb0"], "down"),
    (["nb1", "trn"], "up"),
    (["nlo_a", "nlo_b"], "down"),
    (["rg_in", "sv_in", "rhigh_a"], "up"),
    (["rhigh_b", "pmir", "p11"], "down"),
    (["rhigh_c", "s1n", "dzn", "s2n", "out_n"], "down"),
    (["s1p", "s2p", "out_p"], "up"),
    (["pt", "cm", "trp"], "down"),
]

TOP = "RAMP_V2"
DUMMY = "DUMMY_V2"
LABELS = ("V1_CM", "VCTRLN", "VCTRLP", "Vo_STG1", "Vo1n", "mn_dz", "mp_dz", "icm", "irn", "it1", "nlo", "vtrip",
          "xr.o1", "xs.o1", "xr.z", "xs.z")
PORT_EDGE = dict(IBIAS="bottom", minus="bottom", plus="bottom", Vout="top")


def dummy_cell():
    count = {}
    for st in STRIPS.values():
        n = sum(1 for seg in st["segs"] for f in seg if f == "D")
        if n:
            key = (st["kind"], st["w"], st["l"])
            count[key] = count.get(key, 0) + n
    items = []
    for i, ((kind, w, l), n) in enumerate(sorted(count.items())):
        rail = "GND" if kind.startswith("n") else "VDD"
        items.append(M(f"MD{i}", kind, rail, rail, rail, rail, w, l, n))
    return dict(title="Matching dummies (gates, drains and sources tied to the rail)",
                ports=["VDD", "GND"], dirs={}, items=items)


CELLS[DUMMY] = dummy_cell()


def flatten(cell=TOP, prefix="", conn=None):
    c = CELLS[cell]
    conn = conn or {p: p for p in c["ports"]}

    def net(n):
        return conn.get(n, prefix + n)

    out = []
    for it in c["items"]:
        if it["kind"] == "inst":
            sub = {p: net(n) for p, n in it["conn"].items()}
            out += flatten(it["cell"], prefix + it["name"] + ".", sub)
        else:
            d = dict(it)
            d["name"] = prefix + it["name"]
            d["pins"] = {p: net(n) for p, n in it["pins"].items()}
            if "body" in d:
                d["body"] = net(d["body"])
            out.append(d)
    return out


_DEVS = None


def _devs():
    global _DEVS
    if _DEVS is None:
        _DEVS = {d["name"]: d for d in flatten()}
    return _DEVS


def solve_segment(fingers, kind):
    devs = _devs()
    rail = "GND" if kind.startswith("n") else "VDD"

    def sd(f):
        if f == "D":
            return rail, rail
        return devs[f]["pins"]["S"], devs[f]["pins"]["D"]

    for first in (0, 1):
        a, b = sd(fingers[0])
        nets = [a, b] if first == 0 else [b, a]
        for f in fingers[1:]:
            s_, d_ = sd(f)
            if nets[-1] == s_:
                nets.append(d_)
            elif nets[-1] == d_:
                nets.append(s_)
            else:
                break
        else:
            return nets
    raise ValueError(f"fingers cannot share diffusions: {fingers}")


def gate_net(f, kind):
    if f == "D":
        return "GND" if kind.startswith("n") else "VDD"
    return _devs()[f]["pins"]["G"]


def check_rows():
    devs = {d["name"]: d for d in flatten() if d["kind"] in ("nlv", "plv", "nhv", "phv")}
    used = {}
    for name, st in STRIPS.items():
        for seg in st["segs"]:
            solve_segment(seg, st["kind"])
            for f in seg:
                if f == "D":
                    continue
                d = devs[f]
                assert (d["kind"], d["w"], d["l"]) == (st["kind"], st["w"], st["l"]), (f, name)
                used[f] = used.get(f, 0) + 1
    for n, d in devs.items():
        if n.startswith("xd."):
            continue
        assert used.get(n, 0) == d["m"], f"{n}: placed {used.get(n, 0)} of m={d['m']}"
    rs = {d["name"]: d for d in flatten() if d["kind"] == "rhigh"}
    placed = {}
    for blk in RES_BLOCKS.values():
        for o, l in zip(blk["order"], blk["lengths"]):
            placed[o] = placed.get(o, 0) + l
    for r, d in rs.items():
        assert abs(placed.get(r, 0) - d["l"]) < 1e-6, (r, placed.get(r), d["l"])
    caps = {d["name"] for d in flatten() if d["kind"] == "cmim"}
    assert caps == {m["ref"] for m in MIMS}, caps
    in_bands = [n for names, _ in BANDS for n in names]
    assert sorted(in_bands) == sorted(list(STRIPS) + list(RES_BLOCKS)), "BANDS must list every strip once"
    return True


if __name__ == "__main__":
    check_rows()
    devs = flatten()
    print(f"{len(devs)} primitive devices, "
          f"{sum(d['m'] for d in devs if d['kind'] not in ('rhigh', 'cmim'))} MOS units (incl. dummies), strips OK")
