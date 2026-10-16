"""Matched layout of RAMP_LR in IHP SG13G2 (run with: klayout -b -r layout/gen_layout.py).

Floor plan (bottom to top): one row of unit transistors per matching group, each
row framed by a gate channel below it and a source/drain channel above it.
  * every MOS unit is an IHP PCell (ng = 1); all units of a row have the same
    W/L and orientation (source left, drain right), common-centroid/inter-
    digitated as listed in ramp_lr_design.ROWS, with dummies at the row ends,
  * gates are contacted below the unit, source/drain above, on Metal1 stubs,
  * each channel has one horizontal Metal2 track per net,
  * nets that appear in more than one channel get a vertical Metal3 column in
    a routing spine on the right; top-level pins are labelled on Metal3,
  * every row has a continuous substrate/well tie strip (LU rules),
  * the two 2 pF MIM capacitors sit on Metal5/TopMetal1 above the spine.
"""
import os
import sys
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(
    os.getcwd(), "layout")
sys.path.insert(0, HERE)
K = os.path.join(os.environ.get("PDK_ROOT", os.path.expanduser("~/.ciel")), "ihp-sg13g2", "libs.tech", "klayout")
for p in (K + "/python", K + "/python/pycell4klayout-api/source/python"):
    sys.path.insert(0, p)

import pya  # noqa: E402
import sg13g2_pycell_lib  # noqa: E402,F401  (registers the SG13_dev PCell library)
import ramp_lr_design as D  # noqa: E402

OUT_GDS = os.path.join(HERE, "RAMP_LR.gds")
LY = pya.Layout()
LY.dbu = 0.001
TOP = LY.create_cell(D.TOP)
LIB = pya.Library.library_by_name("SG13_dev")

LAYERS = dict(Activ=(1, 0), GatPoly=(5, 0), Cont=(6, 0), Metal1=(8, 0), pSD=(14, 0), Metal2=(10, 0),
              Via1=(19, 0), Via2=(29, 0), Metal3=(30, 0), M3pin=(30, 2), M3text=(30, 25), NWell=(31, 0),
              ThickGateOx=(44, 0), Metal5=(67, 0), TopMetal1=(126, 0))
L = {k: LY.layer(*v) for k, v in LAYERS.items()}


def um(x):
    return int(round(x * 1000))


def box(layer, x0, y0, x1, y1):
    TOP.shapes(L[layer]).insert(pya.Box(um(min(x0, x1)), um(min(y0, y1)), um(max(x0, x1)), um(max(y0, y1))))


_pc = {}


def pcell(name, **par):
    key = (name, tuple(sorted(par.items())))
    if key not in _pc:
        decl = LIB.layout().pcell_declaration(name)
        pv = [par.get(p.name, p.default) for p in decl.get_parameters()]
        _pc[key] = LY.add_pcell_variant(LIB, decl.id(), pv)
    return _pc[key]


def place(cell, x, y):
    TOP.insert(pya.CellInstArray(cell, pya.Trans(um(x), um(y))))


def shapes_of(cell, layer):
    return [p.bbox() for p in pya.Region(LY.cell(cell).begin_shapes_rec(L[layer])).each_merged()]


def via(x, y, bot, top, n=1):
    """n x n via stack centred at (x, y)."""
    c = pcell("via_stack", b_layer=bot, t_layer=top, vn_columns=n, vn_rows=n,
              vt1_columns=1, vt1_rows=1, vt2_columns=1, vt2_rows=1)
    place(c, x, y)
    return LY.cell(c).bbox()


# ----------------------------------------------------------------------------
# Netlist view
# ----------------------------------------------------------------------------
DEVS = {d["name"]: d for d in D.flatten()}
RAIL = {"n": "GND", "p": "VDD"}
POWER = {"VDD", "GND", "Vout"}
PORTS = D.CELLS[D.TOP]["ports"]

UNIT_GAP = 0.60          # Activ-to-Activ space between units
TRACK_PITCH = 0.90       # Metal2 track pitch in a channel
TAP_GAP = 0.80           # unit Activ to tie strip
TAP_W = 0.40             # tie strip width (Activ)
COL_PITCH = 1.20         # Metal3 spine column pitch

stubs = []   # (channel_id, net, x, y_terminal, width)
channels = OrderedDict()   # id -> dict(y0=..., nets=[...])


class Channel:
    def __init__(self, cid):
        self.cid = cid
        self.terms = []          # (net, x, y_term, width)

    def add(self, net, x, y, w):
        self.terms.append((net, x, y, w))

    def nets(self):
        seen = OrderedDict()
        for n, *_ in self.terms:
            seen[n] = 1
        return list(seen)


CH = OrderedDict()


def channel(cid):
    if cid not in CH:
        CH[cid] = Channel(cid)
    return CH[cid]


# ----------------------------------------------------------------------------
# Rows of unit transistors
# ----------------------------------------------------------------------------
ROW_ORDER = ["bias_n0", "bias_n1", "bias_n2", "bias_p", "pota_ld", "nota_in", "out_n",
             "pota_in", "nota_ld", "in_pairs", "s1_loads", "min_n", "min_p", "out_p"]
ROWDEF = {r["name"]: r for r in D.ROWS}
X0 = 2.0
row_extent = {}


def build_row(r, y):
    """Place one row with its bottom (gate) channel below y and S/D channel above."""
    kind = r["kind"]
    pol = kind[0]
    cell = pcell(D.KINDS[kind][2], w=f"{r['w']}u", l=f"{r['l']}u", ng="1")
    act = shapes_of(cell, "Activ")[0]
    gate = shapes_of(cell, "GatPoly")[0]
    m1 = sorted(shapes_of(cell, "Metal1"), key=lambda b: b.left)
    aw, ah = act.width() / 1000, act.height() / 1000
    gch, sch = channel(r["name"] + ".g"), channel(r["name"] + ".sd")
    x = X0 + 1.2                       # room for the tie contact at the left end
    gaps = []                          # x centres of the gaps between units
    for u in r["units"]:
        place(cell, x, y)
        if u == "D":
            nets = dict(S=RAIL[pol], D=RAIL[pol], G=RAIL[pol])
        else:
            nets = DEVS[u]["pins"]
        for side, b in zip(("S", "D"), m1):
            sch.add(nets[side], x + b.center().x / 1000, y + b.top / 1000, 0.16)
        # gate contact below the unit: poly neck + pad, Cont, Metal1 pad
        gx = x + gate.center().x / 1000
        gw = max(gate.width() / 1000, 0.30)
        gb = y + gate.bottom / 1000
        cy1 = y - 0.62                 # top of the gate contact
        box("GatPoly", x + gate.left / 1000, gb, x + gate.right / 1000, cy1)
        box("GatPoly", gx - gw / 2, cy1 + 0.07, gx + gw / 2, cy1 - 0.16 - 0.07)
        box("Cont", gx - 0.08, cy1, gx + 0.08, cy1 - 0.16)
        box("Metal1", gx - 0.13, cy1 + 0.05, gx + 0.13, cy1 - 0.16 - 0.10)
        gch.add(nets["G"], gx, cy1 - 0.16 - 0.10, 0.26)
        x += aw + UNIT_GAP
        gaps.append(x - UNIT_GAP / 2)
    x_end = x - UNIT_GAP
    gaps = gaps[:-1]
    # tie strip above the units, contacted at both ends
    ty0 = y + ah + TAP_GAP
    tx0, tx1 = X0, x_end + 1.2
    box("Activ", tx0, ty0, tx1, ty0 + TAP_W)
    if pol == "n":
        box("pSD", tx0 - 0.1, ty0 - 0.1, tx1 + 0.1, ty0 + TAP_W + 0.1)
    for cx in (tx0 + 0.3, tx1 - 0.3):
        box("Cont", cx - 0.08, ty0 + 0.12, cx + 0.08, ty0 + 0.28)
        box("Metal1", cx - 0.13, ty0 + 0.07, cx + 0.13, ty0 + 0.33)
        sch.add(RAIL[pol], cx, ty0 + 0.33, 0.26)
    # extra tie contacts in the unit gaps (LU.d: <= 6 um of tie beyond a Cont);
    # their Metal1 pads sit between the source/drain stubs and stay local
    for cx in gaps:
        box("Cont", cx - 0.08, ty0 + 0.12, cx + 0.08, ty0 + 0.28)
        box("Metal1", cx - 0.13, ty0 + 0.02, cx + 0.13, ty0 + 0.38)
    # row-level implant / well / oxide so that unit shapes merge cleanly
    ux0, ux1 = X0 + 1.2, x_end
    if pol == "p":
        e = 0.62 if kind.endswith("hv") else 0.31
        box("NWell", tx0 - e, y - 0.40 - e, tx1 + e, ty0 + TAP_W + e)
        box("pSD", ux0 - 0.18, y - 0.40, ux1 + 0.18, y + ah + 0.40)
    if kind.endswith("hv"):
        box("ThickGateOx", tx0 - 0.7, y - 1.2, tx1 + 0.7, ty0 + TAP_W + 0.7)
    row_extent[r["name"]] = (X0, tx1, y - 1.0, ty0 + TAP_W)
    return ty0 + TAP_W     # top of the row (tie strip)


# ----------------------------------------------------------------------------
# Resistor block (rhigh, common centroid R1a R3a R3b R1b)
# ----------------------------------------------------------------------------
def build_res(y):
    rr = D.RES_ROW
    cell = pcell("rhigh", w=f"{rr['w']}u", l=f"{rr['l']:.3f}u")
    m1 = sorted(shapes_of(cell, "Metal1"), key=lambda b: b.bottom)
    gch, sch = channel("cm_res.g"), channel("cm_res.sd")
    x = X0 + 1.2
    seen = defaultdict(int)
    for u in rr["units"]:
        place(cell, x, y)
        d = DEVS[u]
        k = seen[u]
        seen[u] += 1
        mid = u + ".mid"
        a, b = d["pins"]["P"], d["pins"]["M"]
        bot_net = a if k == 0 else b         # first half: P..mid, second half: mid..M
        cx = x + m1[0].center().x / 1000
        gch.add(bot_net, cx, y + m1[0].bottom / 1000, 0.30)
        sch.add(mid, cx, y + m1[1].top / 1000, 0.30)
        x += 2.4
    top = y + LY.cell(cell).bbox().top / 1000
    row_extent["cm_res"] = (X0, x, y + LY.cell(cell).bbox().bottom / 1000, top)
    return top


# ----------------------------------------------------------------------------
# Channel routing
# ----------------------------------------------------------------------------
def net_width(n):
    return 0.50 if n in POWER else 0.30


def channel_height(ch):
    return 0.6 + TRACK_PITCH * len(ch.nets())


track_y = {}      # (cid, net) -> y


def lay_channel(ch, y0):
    """Assign tracks bottom-up starting at y0; return the channel top."""
    for i, n in enumerate(ch.nets()):
        track_y[(ch.cid, n)] = y0 + 0.5 + i * TRACK_PITCH
    return y0 + channel_height(ch)


def main():
    y = 2.0
    order = []
    for name in ROW_ORDER[:10]:
        order.append(("row", name))
    order.append(("res", "cm_res"))
    for name in ROW_ORDER[10:]:
        order.append(("row", name))
    tops = {}
    for kind, name in order:
        gate_ch_y0 = y
        if kind == "row":
            r = ROWDEF[name]
            # gate channel height from the number of distinct gate nets
            gnets = OrderedDict()
            for u in r["units"]:
                gnets[RAIL[r["kind"][0]] if u == "D" else DEVS[u]["pins"]["G"]] = 1
            gh = 0.6 + TRACK_PITCH * len(gnets)
            for i, n in enumerate(gnets):
                track_y[(name + ".g", n)] = y + 0.5 + i * TRACK_PITCH
            ry = y + gh + 1.0
            rtop = build_row(r, ry)
        else:
            nets = OrderedDict()
            for u in D.RES_ROW["units"]:
                nets.setdefault(u, 0)
            bn = []
            seen = defaultdict(int)
            for u in D.RES_ROW["units"]:
                k = seen[u]
                seen[u] += 1
                bn.append(DEVS[u]["pins"]["P"] if k == 0 else DEVS[u]["pins"]["M"])
            bn = list(OrderedDict.fromkeys(bn))
            gh = 0.6 + TRACK_PITCH * len(bn)
            for i, n in enumerate(bn):
                track_y[("cm_res.g", n)] = y + 0.5 + i * TRACK_PITCH
            ry = y + gh + 1.2
            rtop = build_res(ry)
        sd = CH[name + ".sd"]
        y = lay_channel(sd, rtop + 0.6)
        tops[name] = y
        y += 0.8
    height = y

    # spine columns for nets in more than one channel (and all top ports)
    where = defaultdict(set)
    for ch in CH.values():
        for n in ch.nets():
            where[n].add(ch.cid)
    spine_nets = [n for n in PORTS] + sorted(n for n, s in where.items() if len(s) > 1 and n not in PORTS)
    xmax = max(e[1] for e in row_extent.values())
    spine_x0 = xmax + 2.0
    col_x = {n: spine_x0 + i * COL_PITCH for i, n in enumerate(spine_nets)}

    # stubs, tracks and vias
    for ch in CH.values():
        span = defaultdict(list)
        for n, x, yt, w in ch.terms:
            ty = track_y[(ch.cid, n)]
            box("Metal1", x - w / 2, yt, x + w / 2, ty)
            via(x, ty, "Metal1", "Metal2")
            span[n].append(x)
        for n, xs in span.items():
            ty = track_y[(ch.cid, n)]
            x0, x1 = min(xs), max(xs)
            if n in col_x:
                x1 = max(x1, col_x[n])
                via(col_x[n], ty, "Metal2", "Metal3")
            hw = net_width(n) / 2
            box("Metal2", x0 - 0.2, ty - hw, x1 + 0.2, ty + hw)
    # Metal3 columns spanning their tracks (and the MIM plate contacts)
    ys = defaultdict(list)
    for n, yv in mim_points(spine_x0, height):
        ys[n].append(yv)
    for (cid, n), ty in track_y.items():
        if n in col_x:
            ys[n].append(ty)
    for n, x in col_x.items():
        lo, hi = min(ys[n]), max(ys[n])
        if n in PORTS:
            hi = height + 1.0
        hw = (0.8 if n in POWER else 0.4) / 2
        box("Metal3", x - hw, lo - 0.3, x + hw, hi + 0.3)
        if n in PORTS:
            box("M3pin", x - hw, hi - 0.5, x + hw, hi + 0.3)
            TOP.shapes(L["M3text"]).insert(pya.Text(n, pya.Trans(um(x), um(hi - 0.1))))

    # MIM decoupling capacitors above the spine
    mims(col_x, spine_x0, height)
    LY.write(OUT_GDS)
    bb = TOP.bbox()
    print(f"RAMP_LR: {bb.width() / 1000:.1f} um x {bb.height() / 1000:.1f} um, "
          f"{len(spine_nets)} spine columns, {sum(len(c.terms) for c in CH.values())} stubs -> {OUT_GDS}")


MIM_DEF = (("x3.CDP", "VCTRLP", "VDD"), ("x3.CDN", "VCTRLN", "GND"))


def mim_geom(i):
    bb = LY.cell(pcell("cmim", w="36.5u", l="36.5u")).bbox()
    y0 = 10.0 + i * 50.0
    return y0, y0 + 18.0, y0 + bb.top / 1000 + 3.0      # origin, plate via, strap via


def mim_points(spine_x0, height):
    pts = []
    for i, (_, plate, top_net) in enumerate(MIM_DEF):
        y0, yp, ys_ = mim_geom(i)
        pts += [(plate, yp), (top_net, ys_)]
    return pts


def mims(col_x, spine_x0, height):
    """CDP: VCTRLP / VDD, CDN: VCTRLN / GND.  Bottom plate (Metal5) on VCTRL."""
    c = pcell("cmim", w="36.5u", l="36.5u")
    for i, (name, plate, top_net) in enumerate(MIM_DEF):
        x0 = spine_x0 - 4.0
        y0, yp, sy = mim_geom(i)
        place(c, x0, y0)
        # bottom plate: via stack Metal3 -> Metal5 under the plate on the VCTRL column
        via(col_x[plate], yp, "Metal3", "Metal5", 2)
        # top plate: TopMetal1 strap out of the plate to a stack on the rail column
        box("TopMetal1", col_x[top_net] - 1.0, y0 + 30.0, col_x[top_net] + 1.0, sy + 1.0)
        via(col_x[top_net], sy, "Metal3", "TopMetal1", 2)


main()
