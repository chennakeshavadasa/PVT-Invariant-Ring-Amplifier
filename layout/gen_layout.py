"""Compact matched layout of RAMP_LR in IHP SG13G2 (run with: klayout -b -r layout/gen_layout.py).

Floor plan (ramp_lr_design.BANDS), bottom to top: four rows of the NMOS bias mirror,
the PMOS bias mirror next to the rhigh sensing resistors, the NMOS signal row and the
PMOS signal row.  Both signal rows run in signal-flow order (error amplifiers, stage 1,
stage 2 with its replicas, output stage) so that the stage-1 and stage-2 outputs stay
short.  The two 2-pF MIM capacitors sit on Metal5/TopMetal1 over the circuit.

  * every strip (ramp_lr_design.STRIPS) is a row of multi-finger IHP PCells; the fingers
    of a segment share their source/drain diffusions (ABBA pairs, output devices around
    their replica, stage-2 chains), dummies at the ends, a substrate or well tie at both
    strip ends;
  * gate contacts face one channel, source/drain contacts the other; neighbouring rows
    are mirrored so that they share a channel;
  * channels hold Metal2 tracks assigned by a constrained left-edge router (nets share a
    track where their spans do not overlap), Metal1 stubs connect the contacts;
  * nets that change channel get a Metal3 column next to their pins; VDD and GND have
    columns at both block edges, which also carry the MIM top-plate straps;
  * ports and the named internal nets are labelled on Metal3.
"""
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(
    os.getcwd(), "layout")
sys.path.insert(0, HERE)
K = os.path.join(os.environ.get("PDK_ROOT", os.path.expanduser("~/.ciel")), "ihp-sg13g2", "libs.tech", "klayout")
for p in (K + "/python", K + "/python/pycell4klayout-api/source/python"):
    sys.path.insert(0, p)

import importlib  # noqa: E402

import pya  # noqa: E402
import sg13g2_pycell_lib  # noqa: E402,F401  (registers the SG13_dev PCell library)

# design module: RAMP_LR by default; klayout -b -r layout/gen_layout.py -rd design=ramp_v2_design
D = importlib.import_module(globals().get("design") or os.environ.get("RAMP_DESIGN", "ramp_lr_design"))

OUT_GDS = os.path.join(HERE, f"{D.TOP}.gds")
OUT_JSON = os.path.join(HERE, f"{D.TOP}_placement.json")
LY = pya.Layout()
LY.dbu = 0.001
TOP = LY.create_cell(D.TOP)
LIB = pya.Library.library_by_name("SG13_dev")

LAYERS = dict(Activ=(1, 0), GatPoly=(5, 0), Cont=(6, 0), Metal1=(8, 0), pSD=(14, 0), Metal2=(10, 0),
              Via1=(19, 0), Via2=(29, 0), Metal3=(30, 0), M3pin=(30, 2), M3text=(30, 25), NWell=(31, 0),
              ThickGateOx=(44, 0), Metal4=(50, 0), Metal5=(67, 0), TopMetal1=(126, 0), nSD=(7, 0),
              SalBlock=(28, 0), EXTBlock=(111, 0))
L = {k: LY.layer(*v) for k, v in LAYERS.items()}

# ---- dimensions (um) -------------------------------------------------------
SEG_GAP = 0.60       # Activ space between two segments (diffusion break)
TIE_GAP = 0.60       # segment Activ to tie Activ
TIE_W = 0.42         # tie Activ width
STRIP_GAP = 1.40     # tie to tie between strips of a row
GPAD = 0.50          # Activ edge to the gate contact
TRACK = 0.48         # Metal2 track pitch
M2W, PWRW = 0.20, 0.26
COL = 0.55           # Metal3 column pitch
M3W = 0.20
RES_PITCH = 0.80     # rhigh segments; implant and block layers merged over the array
MIM_W = 36.5
POWER = ("VDD", "GND")
PORTS = D.CELLS[D.TOP]["ports"]
LABELS = getattr(D, "LABELS", ("V1_CM", "VCTRLN", "VCTRLP", "Vo_STG1", "mn_dz", "mp_dz", "icm", "inota", "ipota",
                                "irn", "irp", "it1"))
PORT_EDGE = getattr(D, "PORT_EDGE", dict(IBIAS="bottom", minus="bottom", plus="bottom", Vout="top"))
# RAMP_V2: MIM capacitors with both plates on signal nets (Miller capacitors); RAMP_LR: two
# decoupling capacitors with the top plate on a rail
SIGNAL_MIMS = isinstance(getattr(D, "MIMS", None), list) and bool(D.MIMS) and isinstance(D.MIMS[0], dict)
MIM_NETS = {m[k] for m in D.MIMS for k in ("top", "bottom")} if SIGNAL_MIMS else set()
MIM_GAP = 6.0        # between the Metal5 plates of neighbouring MIMs: via stacks to TopMetal1
# optional extra spacing for high-impedance nets: a track of their own with an empty track
# on either side and twice the column spacing.  {"Vo_STG1", "mp_dz", "mn_dz"} cuts their
# routing capacitance by 25-45 % and gains about 5 deg of post-layout phase margin, for 17 %
# more area (README Section VI-D); off in the compact layout.
CRIT = set()
PLACEMENT = {"strips": {}, "bands": [], "channels": [], "mims": [], "columns": {}}


def um(x):
    return int(round(x * 1000))


def g(x):
    """Snap to the 5-nm manufacturing grid."""
    return round(round(x / 0.005) * 0.005, 3)


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
    return sorted([p.bbox() for p in pya.Region(LY.cell(cell).begin_shapes_rec(L[layer])).each_merged()],
                  key=lambda b: (b.left, b.bottom))


def via(x, y, bot, top, n=1):
    c = pcell("via_stack", b_layer=bot, t_layer=top, vn_columns=n, vn_rows=n,
              vt1_columns=1, vt1_rows=1, vt2_columns=1, vt2_rows=1)
    place(c, x, y)


DEVS = {d["name"]: d for d in D.flatten()}


# ----------------------------------------------------------------------------
# Strips: geometry in strip coordinates (x from the left tie, y = 0 on the
# source/drain edge of the Activ, +1 towards the source/drain channel)
# ----------------------------------------------------------------------------
class Strip:
    def __init__(self, name):
        self.name = name
        st = D.STRIPS[name]
        self.kind, self.w, self.l, self.segs = st["kind"], st["w"], st["l"], st["segs"]
        self.pol = self.kind[0]
        self.rail = "GND" if self.pol == "n" else "VDD"
        self.hv = self.kind.endswith("hv")
        # the PCell takes the total width of all fingers
        self.cells = [pcell(D.KINDS[self.kind][2], w=f"{round(self.w * len(s), 4)}u", l=f"{self.l}u", ng=str(len(s)))
                      for s in self.segs]
        a = [shapes_of(c, "Activ")[0] for c in self.cells]
        self.aw = [b.width() / 1000 for b in a]
        self.ah = a[0].height() / 1000
        # long PMOS strips get a well tie in every diffusion break (LU.a: tie within 20 um)
        self.mid_ties = self.pol == "p" and sum(self.aw) > 30
        brk = 2 * TIE_GAP + TIE_W if self.mid_ties else SEG_GAP
        self.brk = brk
        self.width = 2 * (TIE_W + TIE_GAP) + sum(self.aw) + brk * (len(self.segs) - 1)
        self.gpad_out = self.ah + GPAD + 0.23          # gate side: farthest feature from y = 0
        self.sd_out = 0.0

    def build(self, x0, yl, gside):
        """Place at x0 with the source/drain Activ edge on y = yl; gside = -1 puts the gate
        contacts below the Activ (source/drain channel above), +1 above."""
        s = -gside                    # direction from the Activ towards the S/D channel
        ya0, ya1 = (yl - self.ah, yl) if s > 0 else (yl, yl + self.ah)
        pins_sd, pins_g, fingers = [], [], []
        th = max(self.ah, TIE_W)
        ty0, ty1 = (yl - th, yl) if s > 0 else (yl, yl + th)
        tie_x = [x0, x0 + self.width - TIE_W]
        if self.mid_ties:
            xx = x0 + TIE_W + TIE_GAP
            for aw in self.aw[:-1]:
                xx += aw
                tie_x.append(g(xx + TIE_GAP))
                xx += self.brk
        for x in tie_x:
            box("Activ", x, ty0, x + TIE_W, ty1)
            if self.pol == "n":
                box("pSD", x - 0.10, ty0 - 0.10, x + TIE_W + 0.10, ty1 + 0.10)
            ncont = max(1, int((th - 0.14) / 0.36))
            cy = g((ty0 + ty1) / 2 - (ncont - 1) * 0.18)
            for k in range(ncont):
                box("Cont", x + TIE_W / 2 - 0.08, cy + k * 0.36 - 0.08, x + TIE_W / 2 + 0.08, cy + k * 0.36 + 0.08)
            box("Metal1", x + 0.08, ty0, x + TIE_W - 0.08, ty1)
            pins_sd.append(dict(net=self.rail, x=x + TIE_W / 2, y=yl, w=0.26))
        x = x0 + TIE_W + TIE_GAP
        seg_x = []
        for seg, cell, aw in zip(self.segs, self.cells, self.aw):
            place(cell, x, ya0)
            seg_x.append((x, x + aw))
            nets = D.solve_segment(seg, self.kind)
            stripes = shapes_of(cell, "Metal1")
            gates = shapes_of(cell, "GatPoly")
            assert len(stripes) == len(seg) + 1 and len(gates) == len(seg), self.name
            for n, b in zip(nets, stripes):
                pins_sd.append(dict(net=n, x=x + b.center().x / 1000, y=yl - s * 0.1, w=0.16))
            for f, gt in zip(seg, gates):
                gx, gl, gr = x + gt.center().x / 1000, x + gt.left / 1000, x + gt.right / 1000
                net = D.gate_net(f, self.kind)
                if s > 0:      # gate contact below
                    yc1 = ya0 - GPAD
                    box("GatPoly", gl, yc1, gr, ya0)
                    box("GatPoly", gx - 0.15, yc1 - 0.23, gx + 0.15, yc1 + 0.07)
                    box("Cont", gx - 0.08, yc1 - 0.16, gx + 0.08, yc1)
                    box("Metal1", gx - 0.13, yc1 - 0.21, gx + 0.13, yc1 + 0.05)
                    pins_g.append(dict(net=net, x=gx, y=yc1 - 0.21, w=0.16))
                else:          # gate contact above
                    yc0 = ya1 + GPAD
                    box("GatPoly", gl, ya1, gr, yc0)
                    box("GatPoly", gx - 0.15, yc0 - 0.07, gx + 0.15, yc0 + 0.23)
                    box("Cont", gx - 0.08, yc0, gx + 0.08, yc0 + 0.16)
                    box("Metal1", gx - 0.13, yc0 - 0.05, gx + 0.13, yc0 + 0.21)
                    pins_g.append(dict(net=net, x=gx, y=yc0 + 0.21, w=0.16))
                fingers.append(dict(ref=f, x=round(gx, 3)))
            x += aw + self.brk
        # implants, well and thick oxide over the whole strip
        sx0, sx1 = seg_x[0][0], seg_x[-1][1]
        y_lo, y_hi = min(ya0, ty0), max(ya1, ty1)
        if self.pol == "p":
            ext = 0.40
            for a, b in seg_x:
                box("pSD", a - 0.18, ya0 - ext, b + 0.18, ya1 + ext)
            if not self.mid_ties:
                box("pSD", sx0 - 0.18, ya0 - ext, sx1 + 0.18, ya1 + ext)
        if self.hv:
            gl0 = ya0 - GPAD - 0.30 if s > 0 else ya0 - 0.7
            gl1 = ya1 + 0.7 if s > 0 else ya1 + GPAD + 0.30
            box("ThickGateOx", x0 - 0.7, min(gl0, y_lo - 0.7), x0 + self.width + 0.7, max(gl1, y_hi + 0.7))
        PLACEMENT["strips"][self.name] = dict(kind=self.kind, w=self.w, l=self.l, x0=round(x0, 3),
                                              x1=round(x0 + self.width, 3), y0=round(min(ya0, ty0), 3),
                                              y1=round(max(ya1, ty1), 3), fingers=fingers,
                                              segments=[[round(a, 3), round(b, 3)] for a, b in seg_x])
        return pins_sd, pins_g

    def extent(self, gside):
        """(min, max) of the drawn features relative to the S/D edge."""
        s = -gside
        far_g = self.ah + GPAD + 0.23
        if s > 0:
            return -max(far_g, TIE_W) - (0.7 if self.hv else 0.0), 0.0
        return 0.0, max(far_g, TIE_W) + (0.7 if self.hv else 0.0)


class ResBlock:
    """rhigh segments side by side, ABBA..., all terminals at the heads that face the
    source/drain channel of the row (a single-segment resistor has one terminal per head)."""

    def __init__(self, name="rhigh"):
        self.name = name
        self.spec = getattr(D, "RES_BLOCKS", {}).get(name) or D.RES
        order, lengths = self.spec["order"], self.spec["lengths"]
        self.lengths = lengths if len(lengths) == len(order) else lengths * (len(order) // len(lengths))
        self.order = order
        self.cells = [pcell("rhigh", w=f"{self.spec['w']}u", l=f"{l}u") for l in self.lengths]
        self.width = RES_PITCH * (len(order) - 1) + 0.9 + 0.4
        self.lmax = max(self.lengths)

    def head_nets(self):
        """(far-head net, near-head net) of each segment: series chain per resistor with
        both terminals on the near heads."""
        out = [None] * len(self.order)
        for r in dict.fromkeys(self.order):
            pos = [i for i, o in enumerate(self.order) if o == r]
            p, m = DEVS[r]["pins"]["P"], DEVS[r]["pins"]["M"]
            for k, i in enumerate(pos):
                if len(pos) == 1:
                    near, far = p, m
                elif k == 0:
                    near, far = p, f"{r}.n0"
                elif k == len(pos) - 1:
                    near, far = m, f"{r}.n{k - 1}"
                elif k % 2 == 1:
                    near, far = f"{r}.n{k}", f"{r}.n{k - 1}"
                else:
                    near, far = f"{r}.n{k - 1}", f"{r}.n{k}"
                out[i] = (far, near)
        return out

    def extent(self, gside):
        h = self.lmax + 0.86
        return (-h, 0.0) if gside < 0 else (0.0, h)

    def build(self, x0, yl, gside):
        s = -gside
        pins_near, pins_far, units = [], [], []
        x = x0 + 0.2
        for cell, l, (far, near), ref in zip(self.cells, self.lengths, self.head_nets(), self.order):
            m1 = shapes_of(cell, "Metal1")       # [bottom head, top head]
            if s > 0:    # near heads on top: top-head M1 top edge on yl
                y = yl - m1[1].top / 1000
                pins_near.append(dict(net=near, x=x + 0.25, y=yl, w=0.30))
                pins_far.append(dict(net=far, x=x + 0.25, y=y + m1[0].bottom / 1000, w=0.30))
            else:        # near heads at the bottom
                y = yl - m1[0].bottom / 1000
                pins_near.append(dict(net=near, x=x + 0.25, y=yl, w=0.30))
                pins_far.append(dict(net=far, x=x + 0.25, y=y + m1[1].top / 1000, w=0.30))
            place(cell, x, g(y))
            units.append(dict(ref=ref, x=round(x + 0.25, 3)))
            lay = {k: shapes_of(cell, k)[0] for k in ("EXTBlock", "SalBlock", "pSD", "nSD")}
            x += RES_PITCH
        xa, xb = x0 + 0.2, x - RES_PITCH
        for k, b in lay.items():
            box(k, xa + b.left / 1000, g(y) + b.bottom / 1000, xb + b.right / 1000, g(y) + b.top / 1000)
        e = self.extent(gside)
        PLACEMENT["strips"][self.name] = dict(kind="rhigh", x0=round(x0, 3), x1=round(x0 + self.width, 3),
                                            y0=round(yl + e[0], 3), y1=round(yl + e[1], 3), fingers=units)
        return pins_near, pins_far


# ----------------------------------------------------------------------------
# Channel routing
# ----------------------------------------------------------------------------
def assign_tracks(pins, cols):
    """Constrained left-edge: pins = list of dict(net, x, side) with side 'below' or
    'above'; cols = {net: x of its Metal3 column}.  Returns {net: track index}."""
    span = defaultdict(list)
    for p in pins:
        span[p["net"]].append(p["x"])
    for n, x in cols.items():
        span[n].append(x)
    iv = {}
    for n, xs in span.items():
        a, b = min(xs), max(xs)
        if b - a < 0.45:
            a, b = g((a + b) / 2 - 0.225), g((a + b) / 2 + 0.225)
        iv[n] = (a, b)
    for n in POWER:
        if n in iv:          # rails run to the edge columns
            iv[n] = (XL_COL[n], XR_COL[n])
    pred = defaultdict(set)
    below = [p for p in pins if p["side"] == "below"]
    above = [p for p in pins if p["side"] == "above"]
    for a in below:
        for b in above:
            if a["net"] != b["net"] and abs(a["x"] - b["x"]) < 0.5:
                pred[b["net"]].add(a["net"])
    track, todo, t = {}, set(iv), 0
    exclusive = set()
    while todo:
        ready = sorted((n for n in todo if pred[n] <= set(track)), key=lambda n: iv[n][0])
        if not ready:
            raise RuntimeError(f"cyclic vertical constraints: {sorted(todo)}")
        end, excl = -1e9, False
        for n in ready:
            if n in CRIT:
                if end == -1e9:          # alone on this track
                    track[n] = t
                    excl = True
                    break
                continue
            if iv[n][0] > end + 0.55:
                track[n] = t
                end = iv[n][1]
        if excl:
            exclusive.add(t)
        todo -= {n for n in track}
        t += 1
    # spread: an empty track on either side of every exclusive track
    newidx, k, prev_spacer = {}, 0, False
    for tt in range(t):
        if tt in exclusive:
            if not prev_spacer:
                k += 1
            newidx[tt] = k
            k += 2
            prev_spacer = True
        else:
            newidx[tt] = k
            k += 1
            prev_spacer = False
    track = {n: newidx[v] for n, v in track.items()}
    return track, iv


XL_COL, XR_COL = {}, {}


def main():
    bands = []
    for names, gs in D.BANDS:
        objs = [ResBlock(n) if n.startswith("rhigh") else Strip(n) for n in names]
        bands.append((objs, -1 if gs == "down" else 1))

    # 1) horizontal placement: strips left to right, power columns at both edges
    x_left = 3.0
    XL_COL.update(GND=1.0, VDD=2.0)
    row_w = max(sum(o.width for o in objs) + STRIP_GAP * (len(objs) - 1) for objs, _ in bands)
    mim_w = (sum(m["side"] + 1.2 for m in D.MIMS) + MIM_GAP * (len(D.MIMS) - 1) if SIGNAL_MIMS
             else 2 * (MIM_W + 1.2) + 1.0)
    width = g(max(2 * x_left + row_w, mim_w + 2 * (x_left + 0.8)))
    XR_COL.update(VDD=width - 2.0, GND=width - 1.0)
    xs = []
    for objs, gs in bands:
        w = sum(o.width for o in objs) + STRIP_GAP * (len(objs) - 1)
        x = x_left + (width - 2 * x_left - w) / 2
        pos = []
        for o in objs:
            pos.append(g(x))
            x += o.width + STRIP_GAP
        xs.append(pos)

    # dry run of the pins (x only) to find which nets change channel
    nch = len(bands) + 1
    chpins = [[] for _ in range(nch)]

    def collect(dry):
        for ch in chpins:
            ch.clear()
        for bi, ((objs, gs), pos) in enumerate(zip(bands, xs)):
            yl = 0.0 if dry else YL[bi]
            for o, x in zip(objs, pos):
                a, b = o.build(x, yl, gs) if not dry else dry_pins(o, x, gs)
                # a: source/drain (or near-head) pins, b: gate (or far-head) pins
                sd_ch = bi + 1 if gs < 0 else bi
                g_ch = bi if gs < 0 else bi + 1
                for p in a:
                    chpins[sd_ch].append(dict(p, side="below" if sd_ch == bi + 1 else "above"))
                for p in b:
                    chpins[g_ch].append(dict(p, side="below" if g_ch == bi + 1 else "above"))

    def dry_pins(o, x, gs):
        # build into a scratch cell and discard the shapes
        global TOP
        keep = TOP
        TOP = LY.create_cell("_dry")
        try:
            a, b = o.build(x, 0.0, gs)
        finally:
            LY.delete_cell(TOP.cell_index())
            TOP = keep
        return a, b

    collect(dry=True)
    PLACEMENT["strips"].clear()
    where = defaultdict(set)
    for ci, ch in enumerate(chpins):
        for p in ch:
            where[p["net"]].add(ci)

    # 2) Metal3 columns
    cols = {}            # net -> list of (x, ch_lo, ch_hi)
    occupied = []        # (x, lo, hi)
    for n in POWER:
        cols[n] = [(XL_COL[n], 0, nch - 1), (XR_COL[n], 0, nch - 1)]
        occupied += [(XL_COL[n], -1, nch, n), (XR_COL[n], -1, nch, n)]
    need = [n for n in where if n not in POWER and (len(where[n]) > 1 or n in PORTS or n in MIM_NETS)]
    need.sort(key=lambda n: -(max(where[n]) - min(where[n])))
    for n in need:
        lo, hi = min(where[n]), max(where[n])
        if PORT_EDGE.get(n) == "bottom":
            lo = -1
        elif PORT_EDGE.get(n) == "top":
            hi = nch
        pxs = sorted(p["x"] for ch in chpins for p in ch if p["net"] == n)
        target = g(pxs[len(pxs) // 2])
        best = None
        for k in range(0, 4000):
            for xc in (g(target + k * 0.05), g(target - k * 0.05)):
                if not (x_left - 0.3 < xc < width - x_left + 0.3):
                    continue
                if all(abs(xc - ox) >= (2 * COL if (n in CRIT or on in CRIT) else COL) or ohi < lo or olo > hi
                       for ox, olo, ohi, on in occupied):
                    best = xc
                    break
            if best is not None:
                break
        cols[n] = [(best, lo, hi)]
        occupied.append((best, lo, hi, n))

    # 3) tracks per channel
    tracks, ivs, ntr = [], [], []
    for ci, ch in enumerate(chpins):
        cc = {}
        for n, lst in cols.items():
            for xc, lo, hi in lst:
                if lo <= ci <= hi and ci in where.get(n, set()):
                    cc.setdefault(n, xc)
        if not ch:
            tracks.append({})
            ivs.append({})
            ntr.append(0)
            continue
        tr, iv = assign_tracks(ch, cc)
        tracks.append(tr)
        ivs.append(iv)
        ntr.append(max(tr.values()) + 1)

    # 4) vertical placement
    global YL
    YL = []
    ch_y = []
    y = 0.6
    for bi, (objs, gs) in enumerate(bands):
        h = ntr[bi] * TRACK + 0.7 if ntr[bi] else 0.4
        ch_y.append((y, y + h))
        y += h
        lo = min(o.extent(gs)[0] for o in objs)
        hi = max(o.extent(gs)[1] for o in objs)
        yl = g(y - lo)
        YL.append(yl)
        y = yl + hi
    h = ntr[-1] * TRACK + 0.7 if ntr[-1] else 0.4
    ch_y.append((y, y + h))
    height = y + h + 0.6

    # 5) build for real
    collect(dry=False)
    for ci, ch in enumerate(chpins):
        if not ch:
            continue
        y0, y1 = ch_y[ci]
        ty = {n: g(y0 + 0.35 + TRACK * t + M2W / 2) for n, t in tracks[ci].items()}
        vias = defaultdict(list)
        for p in sorted(ch, key=lambda q: q["x"]):
            yt = ty[p["net"]]
            w = p["w"]
            box("Metal1", p["x"] - w / 2, p["y"], p["x"] + w / 2, yt)
            near = [vx for vx in vias[p["net"]] if abs(vx - p["x"]) < 0.45]
            if near:          # share the neighbouring via of the same net (Via1 spacing)
                box("Metal1", min(near[0], p["x"]) - 0.08, yt - 0.105, max(near[0], p["x"]) + 0.08, yt + 0.105)
            else:
                via(p["x"], yt, "Metal1", "Metal2")
                vias[p["net"]].append(p["x"])
        for n, (a, b) in ivs[ci].items():
            hw = (PWRW if n in POWER else M2W) / 2
            box("Metal2", a - 0.145, ty[n] - hw, b + 0.145, ty[n] + hw)
        for n, lst in cols.items():
            for xc, lo, hi in lst:
                if lo <= ci <= hi and n in ty:
                    via(xc, ty[n], "Metal2", "Metal3")
        PLACEMENT["channels"].append(dict(y0=round(y0, 3), y1=round(y1, 3), tracks=ntr[ci]))

    def ch_mid(ci):
        if ci < 0:
            return 0.0
        if ci >= nch:
            return height
        return None

    col_y = {}
    for n, lst in cols.items():
        for xc, lo, hi in lst:
            ys = []
            for ci in range(max(lo, 0), min(hi, nch - 1) + 1):
                if ci in where.get(n, set()) and n in tracks[ci]:
                    ys.append(g(ch_y[ci][0] + 0.35 + TRACK * tracks[ci][n] + M2W / 2))
            if lo < 0:
                ys.append(0.0)
            if hi >= nch:
                ys.append(height)
            if n in POWER:
                ys += [0.0, height]
            y0, y1 = min(ys), max(ys)
            hw = 0.3 if n in POWER else M3W / 2
            box("Metal3", xc - hw, y0 - (0 if y0 == 0.0 else 0.15), xc + hw, y1 + (0 if y1 == height else 0.15))
            col_y.setdefault(n, []).append((xc, y0, y1))
    PLACEMENT["columns"] = {n: [[round(a, 3), round(b, 3), round(c, 3)] for a, b, c in v] for n, v in col_y.items()}

    # 6) ports and labels on Metal3
    for n in PORTS:
        for xc, y0, y1 in col_y[n]:
            hw = 0.3 if n in POWER else M3W / 2
            if n == "VDD" or PORT_EDGE.get(n) == "top":
                box("M3pin", xc - hw, height - 0.6, xc + hw, height)
                TOP.shapes(L["M3text"]).insert(pya.Text(n, pya.Trans(um(xc), um(height - 0.3))))
            else:
                box("M3pin", xc - hw, 0.0, xc + hw, 0.6)
                TOP.shapes(L["M3text"]).insert(pya.Text(n, pya.Trans(um(xc), um(0.3))))
            break
    for n in LABELS:
        if n in col_y:
            xc, y0, y1 = col_y[n][0]
            TOP.shapes(L["M3text"]).insert(pya.Text(n, pya.Trans(um(xc), um((y0 + y1) / 2))))

    # 7) wells over the PMOS rows (one NWell per row of PMOS strips)
    for bi, (objs, gs) in enumerate(bands):
        ps = [o for o in objs if isinstance(o, Strip) and o.pol == "p"]
        if not ps:
            continue
        ex = 0.9 if any(o.hv for o in ps) else 0.5
        x0 = min(PLACEMENT["strips"][o.name]["x0"] for o in ps) - ex
        x1 = max(PLACEMENT["strips"][o.name]["x1"] for o in ps) + ex
        y0 = YL[bi] + min(o.extent(gs)[0] for o in ps) - ex
        y1 = YL[bi] + max(o.extent(gs)[1] for o in ps) + ex
        box("NWell", x0, y0, x1, y1)

    if SIGNAL_MIMS:
        signal_mims(width, height, col_y)
    else:
        rail_mims(width, height, col_y)

    LY.write(OUT_GDS)
    import json
    bb = TOP.bbox()
    PLACEMENT["bbox"] = [bb.left / 1000, bb.bottom / 1000, bb.right / 1000, bb.top / 1000]
    PLACEMENT["bands"] = [dict(strips=[o.name for o in objs], gates="down" if gs < 0 else "up",
                               yl=round(YL[i], 3)) for i, (objs, gs) in enumerate(bands)]
    with open(OUT_JSON, "w") as fh:
        json.dump(PLACEMENT, fh, indent=1)
    print(f"{D.TOP}: {bb.width() / 1000:.1f} um x {bb.height() / 1000:.1f} um "
          f"({bb.width() * bb.height() / 1e6:.0f} um^2), {sum(ntr)} tracks in {nch} channels, "
          f"{len([n for n in cols if n not in POWER])} Metal3 columns -> layout/{os.path.basename(OUT_GDS)}")


def m4_path(pts, w=0.6):
    """Metal4 wire through the points (horizontal/vertical segments)."""
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        box("Metal4", min(xa, xb) - w / 2, min(ya, yb) - w / 2, max(xa, xb) + w / 2, max(ya, yb) + w / 2)


def signal_mims(width, height, col_y):
    """MIM (Miller) capacitors side by side over the circuit, centred.  Bottom plate (Metal5):
    from its net's Metal3 column by a Metal4 L to a Via4 stack inside the plate.  Top plate
    (TopMetal1 of the PCell): from its column by a Metal4 L to a via stack in the gap between
    the capacitors, then a TopMetal1 strap onto the plate.  Metal4 wires of different nets
    keep 1.5 um apart."""
    cells = [pcell("cmim", w=f"{m['side']}u", l=f"{m['side']}u") for m in D.MIMS]
    total = sum(m["side"] + 1.2 for m in D.MIMS) + MIM_GAP * (len(D.MIMS) - 1)
    x = g((width - total) / 2 + 0.6)
    ytop = g((height + D.MIMS[0]["side"]) / 2)
    wires = []          # (net, x0, y0, x1, y1) of the Metal4 segments
    tm1_y = []          # y of the TopMetal1 via stacks

    def segs(pts):
        return [(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for a, b in zip(pts, pts[1:])]

    def clear(net, pts):
        for sx0, sy0, sx1, sy1 in segs(pts):
            for n, wx0, wy0, wx1, wy1 in wires:
                if n != net and sx0 - 1.5 < wx1 and wx0 < sx1 + 1.5 and sy0 - 1.5 < wy1 and wy0 < sy1 + 1.5:
                    return False
        return True

    def route(net, col, target_x, target_y_range, via_top):
        """Metal4 L from the column to (target_x, y) with y in target_y_range."""
        xc, y0, y1 = col
        lo, hi = target_y_range
        mid = (lo + hi) / 2
        span = [y0 + 0.5 + 0.25 * k for k in range(int((y1 - y0 - 1.0) / 0.25) + 1)] if y1 - y0 > 1.0 else [y0]
        cands = sorted({g(y) for y in span}, key=lambda y: abs(y - mid))
        for ya in cands:
            for k in range(int((hi - lo) / 0.25) + 1):
                yt = g(min(max(ya, lo), hi)) if k == 0 else g(lo + 0.25 * k)
                pts = [(xc, ya), (target_x, ya), (target_x, yt)]
                # TopMetal1 pads of different nets: 1.64 um space around the 2-um straps
                if via_top == "TopMetal1" and any(abs(yt - u) < 4.0 for u in tm1_y):
                    continue
                if clear(net, pts):
                    if via_top == "TopMetal1":
                        tm1_y.append(yt)
                    if y1 - y0 < 0.6:      # a column that touches one channel only: Metal3 min. area
                        box("Metal3", xc - M3W / 2, ya - 0.4, xc + M3W / 2, ya + 0.4)
                    via(xc, ya, "Metal3", "Metal4")
                    m4_path(pts)
                    via(target_x, yt, "Metal4", via_top)
                    wires.extend((net, *sg) for sg in segs(pts))
                    return yt
        raise RuntimeError(f"no Metal4 route for the MIM net {net}: column {col}, target x {target_x}, y {target_y_range}, wires {wires}")

    gaps = []
    for i, (m, c) in enumerate(zip(D.MIMS, cells)):
        side = m["side"]
        cx0, cy0 = x, g(ytop - side)
        cx1, cy1 = cx0 + side, ytop
        place(c, cx0, cy0)
        PLACEMENT["mims"].append(dict(ref=m["ref"], x0=round(cx0, 3), y0=round(cy0, 3), x1=round(cx1, 3),
                                      y1=round(cy1, 3), top=m["top"], bottom=m["bottom"]))
        m["_box"] = (cx0, cy0, cx1, cy1)
        if i < len(D.MIMS) - 1:
            gaps.append(cx1 + 0.6 + MIM_GAP / 2)
        x = cx1 + 0.6 + MIM_GAP + 0.6
    for i, m in enumerate(D.MIMS):
        cx0, cy0, cx1, cy1 = m["_box"]
        # bottom plate: Via4 stack inside the plate, near the column
        xc = col_y[m["bottom"]][0][0]
        route(m["bottom"], col_y[m["bottom"]][0], g(min(max(xc, cx0 + 1.5), cx1 - 1.5)),
              (cy0 + 1.5, cy1 - 1.5), "Metal5")
        # top plate: via stack in the neighbouring gap (left/right of its centre), TopMetal1 strap
        gx = gaps[min(i, len(gaps) - 1)]
        xg = g(gx - 1.2) if i < len(gaps) else g(gx + 1.2)
        ys = route(m["top"], col_y[m["top"]][0], xg, (max(cy0, cy0) + 2.0, cy1 - 2.0), "TopMetal1")
        xa, xb = (xg, cx0 + 2.0) if xg < cx0 else (cx1 - 2.0, xg)
        box("TopMetal1", min(xa, xb) - 0.82, ys - 1.0, max(xa, xb) + 0.82, ys + 1.0)


def rail_mims(width, height, col_y):
    # 8) MIM capacitors over the circuit; bottom plates to VCTRLN/VCTRLP through Metal4,
    #    top plates to the GND/VDD edge columns through TopMetal1 straps
    c = pcell("cmim", w=f"{MIM_W}u", l=f"{MIM_W}u")
    bb = LY.cell(c).bbox()
    cw = bb.width() / 1000
    gap = 1.0
    mx0 = g((width - (2 * cw + gap)) / 2 - bb.left / 1000)
    my0 = g((height - bb.height() / 1000) / 2 - bb.bottom / 1000)
    for i, (ref, plate_net, top_net) in enumerate((("x3.CDN", "VCTRLN", "GND"), ("x3.CDP", "VCTRLP", "VDD"))):
        cx = mx0 + i * (cw + gap)
        place(c, cx, my0)
        PLACEMENT["mims"].append(dict(ref=ref, x0=round(cx, 3), y0=round(my0, 3),
                                      x1=round(cx + MIM_W, 3), y1=round(my0 + MIM_W, 3)))
        # bottom plate: Metal3 column -> Metal4 strap -> Metal5 plate
        xc, cy0, cy1 = col_y[plate_net][0]
        yv = g(min(max((cy0 + cy1) / 2 + 1.5 * i, my0 + 2.0), my0 + MIM_W - 2.0))
        xt = g(min(max(xc + 1.0, cx + 2.0), cx + MIM_W - 2.0))
        via(xc, yv, "Metal3", "Metal4")
        box("Metal4", min(xc, xt) - 0.3, yv - 0.3, max(xc, xt) + 0.3, yv + 0.3)
        via(xt, yv, "Metal4", "Metal5")
        # top plate: TopMetal1 strap to the edge column of its rail
        xe = XL_COL[top_net] if i == 0 else XR_COL[top_net]
        ys = g(my0 + MIM_W / 2)
        xa, xb = (xe - 0.82, cx + 2.0) if i == 0 else (cx + MIM_W - 2.0, xe + 0.82)
        box("TopMetal1", xa, ys - 1.0, xb, ys + 1.0)
        via(xe, ys, "Metal3", "TopMetal1")
        box("Metal4", xe - 0.3, ys - 0.3, xe + 0.3, ys + 0.3)


YL = []
main()
