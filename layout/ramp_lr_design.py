"""Single source of truth for the layout-ready ring amplifier (RAMP_LR).

The original schematics in Design Files/RAMP/Fully-Diff-RAMP use ideal current
sources, an ideal CMFB amplifier (E1) and ideal resistors.  RAMP_LR keeps the
same topology and device sizes but replaces those parts by transistors and PDK
devices, so that the circuit can be laid out and checked by DRC/LVS:

  * all bias currents are mirrored from one external reference IBIAS = 1 uA
    (BIAS_LR, unit devices 0.5 um / 8 um),
  * E1 becomes a transistor CMFB amplifier (MC1/MC2 + diode loads MPC1/MPC2,
    mirrored into the stage-1 loads MP1/MP2, which are m = 2 instead of 1),
  * R1/R3 become rhigh poly resistors,
  * the deadzone-control nodes VCTRLP/VCTRLN get 2 pF MIM decoupling, which
    stabilises the two regulation loops (phase margin -27 deg / 11 deg -> 83/88 deg),
  * the three NMOS whose body was tied to their source now have body = GND
    (a standard SG13G2 NMOS sits in the common p-substrate),
  * small MOS gate capacitors on VCTRLN/VCTRLP satisfy the antenna rules for
    the MIM plates (otherwise ~35000x the gate area of the 0.15/0.13 um gates).

gen_schematics.py turns CELLS into xschem schematics/symbols, gen_layout.py
turns ROWS into the matched layout; the LVS netlist comes from xschem.
"""

# device kinds -> (xschem symbol, PDK model, PCell name)
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


def C(name, a, b, w, l):
    return dict(name=name, kind="cmim", pins=dict(c0=a, c1=b), w=w, l=l, m=1)


def X(name, cell, **conn):
    return dict(name=name, kind="inst", cell=cell, conn=conn)


# Bias mirror unit (both NMOS and PMOS): 0.5 um / 8 um keeps every branch
# within 4 % of its nominal current (a 2 um long unit was 24-28 % off).
WB, LB = 0.5, 8.0

CELLS = {
    "BIAS_LR": dict(
        title="Bias current mirrors (IBIAS = 1 uA in)",
        ports=["VDD", "GND", "IBIAS", "it1", "icm", "inota", "irn", "irp", "ipota"],
        dirs=dict(IBIAS="in"),
        items=[
            M("MB0", "nlv", "IBIAS", "IBIAS", "GND", "GND", WB, LB, 1),
            M("MB1", "nlv", "it1", "IBIAS", "GND", "GND", WB, LB, 10),
            M("MB2", "nlv", "icm", "IBIAS", "GND", "GND", WB, LB, 10),
            M("MB3", "nlv", "inota", "IBIAS", "GND", "GND", WB, LB, 2),
            M("MB4", "nlv", "irn", "IBIAS", "GND", "GND", WB, LB, 1),
            M("MB5", "nlv", "pb", "IBIAS", "GND", "GND", WB, LB, 1),
            M("MB6", "plv", "pb", "pb", "VDD", "VDD", WB, LB, 1),
            M("MB7", "plv", "irp", "pb", "VDD", "VDD", WB, LB, 1),
            M("MB8", "plv", "ipota", "pb", "VDD", "VDD", WB, LB, 2),
        ]),
    "STG1_LR": dict(
        title="Stage 1: input pair, rhigh CM sensing and transistor CMFB",
        ports=["VDD", "GND", "Vo1", "V1_CM", "Vin", "Vip", "it1", "icm"],
        dirs=dict(Vo1="out", V1_CM="in", Vin="in", Vip="in"),
        items=[
            R("R1", "net2", "net3", 0.5, 33.7),
            R("R3", "Vo1", "net3", 0.5, 33.7),
            M("MN1", "nlv", "net2", "Vip", "it1", "GND", 1.56, 0.5, 2),
            M("MN2", "nlv", "Vo1", "Vin", "it1", "GND", 1.56, 0.5, 2),
            M("MP1", "phv", "net2", "vcmfb", "VDD", "VDD", 0.5, 1.0, 2),
            M("MP2", "phv", "Vo1", "vcmfb", "VDD", "VDD", 0.5, 1.0, 2),
            M("MC1", "nlv", "vcmfb", "V1_CM", "icm", "GND", 1.56, 0.5, 2),
            M("MC2", "nlv", "dB", "net3", "icm", "GND", 1.56, 0.5, 2),
            M("MPC1", "phv", "vcmfb", "vcmfb", "VDD", "VDD", 0.5, 1.0, 2),
            M("MPC2", "phv", "dB", "dB", "VDD", "VDD", 0.5, 1.0, 2),
        ]),
    "STG1_CM_LR": dict(
        title="Stage-2 trip-point replica (CMFB reference)",
        ports=["VDD", "V_CM1", "GND"],
        dirs=dict(V_CM1="out"),
        items=[
            M("M9", "nlv", "V_CM1", "V_CM1", "GND", "GND", 0.15, 0.13),
            M("M10", "plv", "V_CM1", "V_CM1", "net1", "VDD", 0.15, 0.13, 3),
            M("M11", "plv", "net1", "GND", "VDD", "VDD", 0.15, 0.13, 5),
            M("M12", "nlv", "V_CM1", "V_CM1", "net2", "GND", 0.15, 0.13),
            M("M13", "plv", "V_CM1", "V_CM1", "VDD", "VDD", 0.15, 0.13),
            M("M14", "nlv", "net2", "VDD", "GND", "GND", 0.15, 0.13),
        ]),
    "STG2_LR": dict(
        title="Stage 2: current-starved inverters (deadzone)",
        ports=["VDD", "VCTRL_P", "VDZP", "Vin_2", "VDZN", "VCTRL_N", "GND"],
        dirs=dict(VCTRL_P="in", VCTRL_N="in", Vin_2="in", VDZP="out", VDZN="out"),
        items=[
            M("MN_STG2_3N1", "nlv", "VDZN", "Vin_2", "GND", "GND", 0.15, 0.13),
            M("MN_STG2_3P1", "plv", "VDZN", "Vin_2", "net1", "VDD", 0.15, 0.13, 3),
            M("MP_DZ_STG2_3N", "plv", "net1", "VCTRL_P", "VDD", "VDD", 0.15, 0.13, 5),
            M("MP_STG2_3P2", "nlv", "VDZP", "Vin_2", "net2", "GND", 0.15, 0.13),
            M("MP_STG2_3P1", "plv", "VDZP", "Vin_2", "VDD", "VDD", 0.15, 0.13),
            M("MN_DZ_STG2_3P", "nlv", "net2", "VCTRL_N", "GND", "GND", 0.15, 0.13),
        ]),
    "POTA_LR": dict(
        title="Error amplifier for VCTRLP (PMOS input)",
        ports=["VDD", "PLUS", "MINUS", "Vout", "GND", "tail"],
        dirs=dict(PLUS="in", MINUS="in", Vout="out"),
        items=[
            M("M2", "plv", "net2", "PLUS", "tail", "VDD", 1.2, 0.5, 2),
            M("M1", "plv", "Vout", "MINUS", "tail", "VDD", 1.2, 0.5, 2),
            M("M4", "nhv", "Vout", "net2", "GND", "GND", 0.5, 2.0, 2),
            M("M5", "nhv", "net2", "net2", "GND", "GND", 0.5, 2.0, 2),
        ]),
    "NOTA_LR": dict(
        title="Error amplifier for VCTRLN (NMOS input)",
        ports=["VDD", "Vout", "PLUS", "MINUS", "GND", "tail"],
        dirs=dict(PLUS="in", MINUS="in", Vout="out"),
        items=[
            M("M1", "nhv", "net2", "PLUS", "tail", "GND", 1.75, 1.0, 2),
            M("M2", "nhv", "Vout", "MINUS", "tail", "GND", 1.75, 1.0, 2),
            M("M3", "phv", "Vout", "net2", "VDD", "VDD", 0.5, 0.75),
            M("M4", "phv", "net2", "net2", "VDD", "VDD", 0.5, 0.75),
        ]),
    "STG2_REPLICA_LR": dict(
        title="Deadzone regulation loop (stage-2 replica + error amplifiers)",
        ports=["VDD", "VCTRLP", "Vin_STG2", "VCTRLN", "GND", "irn", "irp", "ipota", "inota"],
        dirs=dict(VCTRLP="out", VCTRLN="out", Vin_STG2="in"),
        items=[
            M("MN_STG2_3N1", "nlv", "net1", "Vin_STG2", "GND", "GND", 0.15, 0.13),
            M("MN_STG2_3P1", "plv", "net1", "Vin_STG2", "net2", "VDD", 0.15, 0.13, 3),
            M("MP_DZ_STG2_3N", "plv", "net2", "VCTRLP", "VDD", "VDD", 0.15, 0.13, 5),
            M("MP_STG2_3P2", "nlv", "net4", "Vin_STG2", "net3", "GND", 0.15, 0.13),
            M("MP_STG2_3P1", "plv", "net4", "Vin_STG2", "VDD", "VDD", 0.15, 0.13),
            M("MN_DZ_STG2_3P", "nlv", "net3", "VCTRLN", "GND", "GND", 0.15, 0.13),
            M("MN_STG2_3N_R", "nhv", "irp", "irp", "GND", "GND", 2.3, 1.0),
            M("MP_STG2_3P_R", "phv", "irn", "irn", "VDD", "VDD", 4.5, 0.5),
            X("x1", "POTA_LR", VDD="VDD", PLUS="net1", MINUS="irp", Vout="VCTRLP", GND="GND", tail="ipota"),
            X("x2", "NOTA_LR", VDD="VDD", Vout="VCTRLN", PLUS="net4", MINUS="irn", GND="GND", tail="inota"),
            C("CDP", "VDD", "VCTRLP", 36.5, 36.5),
            C("CDN", "GND", "VCTRLN", 36.5, 36.5),
            # MOS gate capacitors: keep the MIM plate / gate-area antenna ratio of
            # VCTRLN/VCTRLP below the SG13G2 limit (Ant.e, 20000 with diode)
            M("MCN", "nlv", "GND", "VCTRLN", "GND", "GND", 1.56, 0.5),
            M("MCP", "plv", "VDD", "VCTRLP", "VDD", "VDD", 1.2, 0.5),
        ]),
    "RAMP_LR": dict(
        title="Ring amplifier with deadzone regulation, layout-ready (IHP SG13G2)",
        ports=["VDD", "GND", "IBIAS", "minus", "plus", "Vout"],
        dirs=dict(IBIAS="in", minus="in", plus="in", Vout="out"),
        items=[
            X("xb", "BIAS_LR", VDD="VDD", GND="GND", IBIAS="IBIAS", it1="it1", icm="icm",
              inota="inota", irn="irn", irp="irp", ipota="ipota"),
            X("x1", "STG1_LR", VDD="VDD", GND="GND", Vo1="Vo_STG1", V1_CM="V1_CM", Vin="plus",
              Vip="minus", it1="it1", icm="icm"),
            X("x4", "STG1_CM_LR", VDD="VDD", V_CM1="V1_CM", GND="GND"),
            X("x2", "STG2_LR", VDD="VDD", VCTRL_P="VCTRLP", VDZP="mp_dz", Vin_2="Vo_STG1",
              VDZN="mn_dz", VCTRL_N="VCTRLN", GND="GND"),
            X("x3", "STG2_REPLICA_LR", VDD="VDD", VCTRLP="VCTRLP", Vin_STG2="V1_CM", VCTRLN="VCTRLN",
              GND="GND", irn="irn", irp="irp", ipota="ipota", inota="inota"),
            M("M1", "nhv", "Vout", "mn_dz", "GND", "GND", 2.3, 1.0, 4),
            M("M2", "phv", "Vout", "mp_dz", "VDD", "VDD", 4.5, 0.5, 4),
            X("xd", "DUMMY_LR", VDD="VDD", GND="GND"),
        ]),
}

# --------------------------------------------------------------------------
# Compact matched placement.  A *strip* is a row of transistor fingers of one
# kind and W/L; each *segment* of a strip is one multi-finger PCell, so the
# fingers of a segment share their source/drain diffusions.  Segments are
# separated by a diffusion break.  "D" is a dummy finger (gate, source and drain
# on the rail).  The diffusion nets are solved from the device pins
# (solve_segment), so a segment only lists its fingers left to right.
# Devices with m = k appear k times.  Device references are hierarchical names.
# --------------------------------------------------------------------------
_T, _C, _N = "xb.MB1", "xb.MB2", "xb.MB3"           # it1 (x10), icm (x10), inota (x2)
_R, _Q, _P = "xb.MB0", "xb.MB4", "xb.MB5"           # IBIAS diode, irn, pb


def _chain(blk, dev, n_dz=5, n_in=3):
    """Stage-2 PMOS chain of x2/x3 (or the trip-point replica x4): one finger of the
    single PMOS, then the deadzone devices and the inverter devices interleaved so
    that every diffusion is shared: OUT_P |P1| VDD |DZ| n1 |DZ| VDD ... n1 |IN| OUT_N."""
    p1, dz, inv = dev
    return [f"{blk}.{p1}"] + [f"{blk}.{dz}"] * n_dz + [f"{blk}.{inv}"] * n_in


STRIPS = {
    # NMOS bias mirror, 0.5/8 um: sources on GND shared by finger pairs, every row
    # symmetric about its centre, reference MB0 in the middle of the last row
    "bn0": dict(kind="nlv", w=WB, l=LB, segs=[["D", _T, _T, _C, _C, _T, _T, "D"]]),
    "bn1": dict(kind="nlv", w=WB, l=LB, segs=[["D", _C, _C, _N, _N, _C, _C, "D", _P]]),
    "bn2": dict(kind="nlv", w=WB, l=LB, segs=[["D", _C, _C, _T, _T, _C, _C, "D"]]),
    "bn3": dict(kind="nlv", w=WB, l=LB, segs=[["D", _T, _T], [_R, _Q], [_T, _T, "D"]]),
    # PMOS bias mirror, 0.5/8 um
    "bp": dict(kind="plv", w=WB, l=LB, segs=[["D", "xb.MB8", "xb.MB8", "D"], ["xb.MB6", "xb.MB7"]]),
    # NMOS rows: POTA load (next to the PMOS bias mirror); NOTA input pair, stage 1, stage 2, output
    "pota_ld": dict(kind="nhv", w=0.5, l=2.0,
                    segs=[["D"], ["x3.x1.M4", "x3.x1.M5", "x3.x1.M5", "x3.x1.M4"], ["D"]]),
    "nota_in": dict(kind="nhv", w=1.75, l=1.0,
                    segs=[["D"], ["x3.x2.M1", "x3.x2.M2", "x3.x2.M2", "x3.x2.M1"], ["D"]]),
    "s1_n": dict(kind="nlv", w=1.56, l=0.5,
                 segs=[["D"], ["x1.MN1", "x1.MN2", "x1.MN2", "x1.MN1"], ["D"],
                       ["x1.MC1", "x1.MC2", "x1.MC2", "x1.MC1"], ["D", "x3.MCN", "D"]]),
    "s2_n": dict(kind="nlv", w=0.15, l=0.13,
                 segs=[["D"], ["x2.MP_STG2_3P2", "x2.MN_DZ_STG2_3P", "x2.MN_STG2_3N1"],
                       ["x3.MN_STG2_3N1", "x3.MN_DZ_STG2_3P", "x3.MP_STG2_3P2"],
                       ["x4.M12", "x4.M14", "x4.M9"], ["D"]]),
    "out_n": dict(kind="nhv", w=2.3, l=1.0, segs=[["D", "M1", "M1", "x3.MN_STG2_3N_R"], ["M1", "M1", "D"]]),
    # PMOS signal row (POTA input pair, NOTA load, stage-1 loads, stage 2, output)
    "pota_in": dict(kind="plv", w=1.2, l=0.5,
                    segs=[["D"], ["x3.x1.M2", "x3.x1.M1", "x3.x1.M1", "x3.x1.M2"], ["D", "x3.MCP", "D"]]),
    "nota_ld": dict(kind="phv", w=0.5, l=0.75, segs=[["D"], ["x3.x2.M3", "x3.x2.M4"], ["D"]]),
    "s1_p": dict(kind="phv", w=0.5, l=1.0,
                 segs=[["D"], ["x1.MP1", "x1.MP2", "x1.MP2", "x1.MP1"],
                       ["x1.MPC1", "x1.MPC2", "x1.MPC2", "x1.MPC1"], ["D"]]),
    "s2_p": dict(kind="plv", w=0.15, l=0.13,
                 segs=[["D"], _chain("x2", ("MP_STG2_3P1", "MP_DZ_STG2_3N", "MN_STG2_3P1")),
                       _chain("x3", ("MP_STG2_3P1", "MP_DZ_STG2_3N", "MN_STG2_3P1"))[::-1],
                       _chain("x4", ("M13", "M11", "M10")), ["D"]]),
    "out_p": dict(kind="phv", w=4.5, l=0.5, segs=[["D", "M2", "M2", "x3.MP_STG2_3P_R"], ["M2", "M2", "D"]]),
}

# rhigh: each 100-kOhm resistor (W = 0.5 um, L = 33.7 um) is split into ten series
# segments of 3.37 um, interleaved ABBA x 5; both terminals of each resistor sit on the
# heads that face the stage-1 channel; LVS merges the series segments.
RES = dict(w=0.5, lengths=[3.37] * 10, order=["x1.R1", "x1.R3", "x1.R3", "x1.R1"] * 5)
MIMS = ["x3.CDN", "x3.CDP"]

# floor plan, bottom to top: (strip names left to right, side of the gate contacts)
BANDS = [
    (["bn0"], "down"), (["bn1"], "up"), (["bn2"], "down"), (["bn3"], "up"),
    (["bp", "pota_ld"], "down"),
    (["nota_in", "rhigh", "s1_n", "s2_n", "out_n"], "down"),
    (["pota_in", "nota_ld", "s1_p", "s2_p", "out_p"], "up"),
]


def dummy_cell():
    """DUMMY_LR: one dummy device per (kind, W, L) with m = number of dummy fingers."""
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


CELLS["DUMMY_LR"] = dummy_cell()
TOP = "RAMP_LR"


def flatten(cell=TOP, prefix="", conn=None):
    """Flat list of primitive devices with hierarchical names and top-level nets."""
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


def solve_segment(fingers, kind):
    """Diffusion nets (len(fingers) + 1) of one shared-diffusion segment: every finger
    connects the diffusions on its two sides to its source and drain."""
    devs = {d["name"]: d for d in flatten()}
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
    return {d["name"]: d for d in flatten()}[f]["pins"]["G"]


def check_rows():
    """Every MOS device appears exactly m times in the strips, with the strip's W/L,
    and every segment can share its diffusions."""
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
    for r, d in rs.items():
        tot = sum(l for o, l in zip(RES["order"], RES["lengths"] * 2) if o == r)
        assert abs(tot - d["l"]) < 1e-6, (r, tot)
    return True


if __name__ == "__main__":
    check_rows()
    devs = flatten()
    print(f"{len(devs)} primitive devices, "
          f"{sum(d['m'] for d in devs if d['kind'] not in ('rhigh', 'cmim'))} MOS units "
          f"(incl. dummies), strips OK")
