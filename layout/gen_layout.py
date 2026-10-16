"""Matched layout of RAMP_LR in IHP SG13G2 (run with: klayout -b -r layout/gen_layout.py).

Floor plan: two columns of rows with a Metal3 routing spine between them.  The
rows are grouped in bands (ramp_lr_design.BANDS); the left and right row of a
band share one gate channel below them and one source/drain channel above them.
  * every MOS unit is an IHP PCell (ng = 1); all units of a row have the same
    W/L and orientation (source left, drain right), common-centroid/inter-
    digitated as listed in ramp_lr_design.ROWS, with dummies at the row ends,
  * gates are contacted below the unit, source/drain above, on Metal1 stubs,
  * each channel has one horizontal Metal2 track per net,
  * nets that appear in more than one channel get a vertical Metal3 column in
    the spine; top-level pins are labelled on Metal3,
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
OUT_JSON = os.path.join(HERE, "RAMP_LR_placement.json")
PLACEMENT = {"rows": {}, "mims": [], "spine": None, "bands": []}
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
ROWDEF = {r["name"]: r for r in D.ROWS}

UNIT_GAP = 0.60          # Activ-to-Activ space between units
TRACK_PITCH = 0.90       # Metal2 track pitch in a channel
TAP_GAP = 0.80           # unit Activ to tie strip
TAP_W = 0.40             # tie strip width (Activ)
COL_PITCH = 1.20         # Metal3 spine column pitch
END = 1.2                # row end margin (tie contact)
RES_PITCH = 2.4          # rhigh segment pitch
X0 = 2.0


class Channel:
    def __init__(self, cid):
        self.cid = cid
        self.terms = []          # (net, x, y_term, width)
        self.order = []          # nets in track order (from the dry run)

    def add(self, net, x, y, w):
        self.terms.append((net, x, y, w))


CH = OrderedDict()


def channel(cid):
    if cid not in CH:
        CH[cid] = Channel(cid)
    return CH[cid]


def mos_cell(r):
    return pcell(D.KINDS[r["kind"]][2], w=f"{r['w']}u", l=f"{r['l']}u", ng="1")


def res_cell():
    rr = D.RES_ROW
    return pcell("rhigh", w=f"{rr['w']}u", l=f"{rr['l']:.4f}u")


def res_nets():
    """(bottom net, top net) of each rhigh segment: 4 segments in series per resistor."""
    seen, out = defaultdict(int), []
    for u in D.RES_ROW["units"]:
        k = seen[u]
        seen[u] += 1
        p, m = DEVS[u]["pins"]["P"], DEVS[u]["pins"]["M"]
        bot = [p, f"{u}.mid1", f"{u}.mid1", m][k]
        top = [f"{u}.mid0", f"{u}.mid0", f"{u}.mid2", f"{u}.mid2"][k]
        out.append((bot, top))
    return out


def row_nets(name):
    """Nets a row puts into its gate channel and its source/drain channel (dry run)."""
    if name == "cm_res":
        rn = res_nets()
        return [b for b, _ in rn], [t for _, t in rn]
    r = ROWDEF[name]
    rail = RAIL[r["kind"][0]]
    g, sd = [], [rail]
    for u in r["units"]:
        pins = dict(S=rail, D=rail, G=rail) if u == "D" else DEVS[u]["pins"]
        g.append(pins["G"])
        sd += [pins["S"], pins["D"]]
    return g, sd


def row_width(name):
    if name is None:
        return 0.0
    if name == "cm_res":
        return END + len(D.RES_ROW["units"]) * RES_PITCH
    r = ROWDEF[name]
    aw = shapes_of(mos_cell(r), "Activ")[0].width() / 1000
    return 2 * END + len(r["units"]) * (aw + UNIT_GAP) - UNIT_GAP


# ----------------------------------------------------------------------------
# Rows of unit transistors
# ----------------------------------------------------------------------------
def build_row(r, y, x_start, gch, sch):
    """Place one row at (x_start, y); gate terminals go to gch, S/D terminals to sch."""
    kind = r["kind"]
    pol = kind[0]
    cell = mos_cell(r)
    act = shapes_of(cell, "Activ")[0]
    gate = shapes_of(cell, "GatPoly")[0]
    m1 = sorted(shapes_of(cell, "Metal1"), key=lambda b: b.left)
    aw, ah = act.width() / 1000, act.height() / 1000
    x = x_start + END                  # room for the tie contact at the left end
    gaps, units = [], []
    for u in r["units"]:
        place(cell, x, y)
        units.append(dict(ref=u, x0=round(x, 3), x1=round(x + aw, 3)))
        nets = dict(S=RAIL[pol], D=RAIL[pol], G=RAIL[pol]) if u == "D" else DEVS[u]["pins"]
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
    tx0, tx1 = x_start, x_end + END
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
    ux0, ux1 = x_start + END, x_end
    if pol == "p":
        e = 0.62 if kind.endswith("hv") else 0.31
        box("NWell", tx0 - e, y - 0.40 - e, tx1 + e, ty0 + TAP_W + e)
        box("pSD", ux0 - 0.18, y - 0.40, ux1 + 0.18, y + ah + 0.40)
    if kind.endswith("hv"):
        box("ThickGateOx", tx0 - 0.7, y - 1.2, tx1 + 0.7, ty0 + TAP_W + 0.7)
    PLACEMENT["rows"][r["name"]] = dict(kind=kind, w=r["w"], l=r["l"], y0=round(y, 3), y1=round(y + ah, 3),
                                        tap=[round(ty0, 3), round(ty0 + TAP_W, 3)], units=units)
    return ty0 + TAP_W     # top of the row (tie strip)


def build_res(y, x_start, gch, sch):
    """rhigh segments, ABBAABBA; bottom terminals to gch, top terminals to sch."""
    rr = D.RES_ROW
    cell = res_cell()
    m1 = sorted(shapes_of(cell, "Metal1"), key=lambda b: b.bottom)
    rb = LY.cell(cell).bbox()
    x = x_start + END
    units = []
    for u, (bot, top) in zip(rr["units"], res_nets()):
        place(cell, x, y)
        units.append(dict(ref=u, x0=round(x + rb.left / 1000, 3), x1=round(x + rb.right / 1000, 3)))
        cx = x + m1[0].center().x / 1000
        gch.add(bot, cx, y + m1[0].bottom / 1000, 0.30)
        sch.add(top, cx, y + m1[1].top / 1000, 0.30)
        x += RES_PITCH
    top = y + rb.top / 1000
    PLACEMENT["rows"]["cm_res"] = dict(kind="rhigh", w=rr["w"], l=rr["l"], y0=round(y, 3), y1=round(top, 3),
                                       units=units)
    return top


# ----------------------------------------------------------------------------
# Channel routing
# ----------------------------------------------------------------------------
def net_width(n):
    return 0.50 if n in POWER else 0.30


track_y = {}      # (cid, net) -> y


def assign_tracks(ch, y0):
    """Tracks bottom-up from y0 in the dry-run net order; return the channel top."""
    for i, n in enumerate(ch.order):
        track_y[(ch.cid, n)] = y0 + 0.5 + i * TRACK_PITCH
    return y0 + 0.6 + TRACK_PITCH * len(ch.order)


MIM_DEF = (("x3.CDP", "VCTRLP", "VDD"), ("x3.CDN", "VCTRLN", "GND"))
MIM_W = 36.5


def mim_geom(i):
    """MIM origin, bottom-plate via y and top-plate strap via y (stacked above y = 4 um)."""
    bb = LY.cell(pcell("cmim", w=f"{MIM_W}u", l=f"{MIM_W}u")).bbox()
    y0 = 4.0 + i * (bb.height() / 1000 + 5.0)
    return y0, y0 + MIM_W / 2, y0 + bb.top / 1000 + 2.4


def main():
    # 1) dry run: nets of every channel -> spine nets and column positions
    bands = []
    for i, (left, right) in enumerate(D.BANDS):
        g, sd = channel(f"b{i}.g"), channel(f"b{i}.sd")
        for name in (left, right):
            if name:
                gn, sn = row_nets(name)
                for ch, nets in ((g, gn), (sd, sn)):
                    for n in nets:
                        if n not in ch.order:
                            ch.order.append(n)
        bands.append((left, right, g, sd))
    where = defaultdict(set)
    for ch in CH.values():
        for n in ch.order:
            where[n].add(ch.cid)
    spine_nets = list(PORTS) + sorted(n for n, s in where.items() if len(s) > 1 and n not in PORTS)
    wl = max(row_width(l) for l, *_ in bands)
    spine_x0 = X0 + wl + 2.0
    col_x = {n: spine_x0 + i * COL_PITCH for i, n in enumerate(spine_nets)}
    xr0 = spine_x0 + (len(spine_nets) - 1) * COL_PITCH + 2.0

    # 2) place bands bottom-up
    y = 2.0
    for left, right, g, sd in bands:
        y_g = y
        ry = assign_tracks(g, y) + (1.2 if "cm_res" in (left, right) else 1.0)
        tops = []
        for name, x0 in ((left, X0), (right, xr0)):
            if name == "cm_res":
                tops.append(build_res(ry, x0, g, sd))
            elif name:
                tops.append(build_row(ROWDEF[name], ry, x0, g, sd))
        y = assign_tracks(sd, max(tops) + 0.6) + 0.8
        PLACEMENT["bands"].append(dict(left=left, right=right, y0=round(y_g, 3), y1=round(y, 3)))
    height = y

    # 3) stubs, tracks and vias
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
                x0, x1 = min(x0, col_x[n]), max(x1, col_x[n])
                via(col_x[n], ty, "Metal2", "Metal3")
            hw = net_width(n) / 2
            box("Metal2", x0 - 0.2, ty - hw, x1 + 0.2, ty + hw)
    # Metal3 columns spanning their tracks (and the MIM plate contacts)
    ys = defaultdict(list)
    for i, (_, plate, top_net) in enumerate(MIM_DEF):
        _, yp, ysv = mim_geom(i)
        ys[plate].append(yp)
        ys[top_net].append(ysv)
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

    # 4) MIM decoupling capacitors over the spine (Metal5 / TopMetal1 only)
    c = pcell("cmim", w=f"{MIM_W}u", l=f"{MIM_W}u")
    xm = (spine_x0 + col_x[spine_nets[-1]]) / 2 - MIM_W / 2
    for i, (name, plate, top_net) in enumerate(MIM_DEF):
        y0, yp, sy = mim_geom(i)
        place(c, xm, y0)
        PLACEMENT["mims"].append(dict(ref=name, x0=xm, y0=y0, x1=xm + MIM_W, y1=y0 + MIM_W))
        # bottom plate: via stack Metal3 -> Metal5 under the plate on the VCTRL column
        via(col_x[plate], yp, "Metal3", "Metal5", 2)
        # top plate: TopMetal1 strap out of the plate to a stack on the rail column
        box("TopMetal1", col_x[top_net] - 1.0, y0 + MIM_W - 6.0, col_x[top_net] + 1.0, sy + 1.0)
        via(col_x[top_net], sy, "Metal3", "TopMetal1", 2)

    LY.write(OUT_GDS)
    import json
    PLACEMENT["spine"] = dict(x0=spine_x0, x1=col_x[spine_nets[-1]], nets=spine_nets)
    bb = TOP.bbox()
    PLACEMENT["bbox"] = [bb.left / 1000, bb.bottom / 1000, bb.right / 1000, bb.top / 1000]
    with open(OUT_JSON, "w") as fh:
        json.dump(PLACEMENT, fh, indent=1)
    print(f"RAMP_LR: {bb.width() / 1000:.1f} um x {bb.height() / 1000:.1f} um "
          f"({bb.width() * bb.height() / 1e6:.0f} um^2), {len(spine_nets)} spine columns, "
          f"{sum(len(c.terms) for c in CH.values())} stubs -> {OUT_GDS}")


main()
