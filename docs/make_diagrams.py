#!/usr/bin/env python3
"""Architecture schematic of the layout-ready ring amplifier (docs/figures/diagrams/).

Journal-style line art: black on white, transistor level where the deadzone is set,
device names as in the schematics, sub-figure labels below the panels.  Coordinates
are in points (the figure is drawn 1:1, 7.16 in wide).
"""
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

OUT = Path(__file__).resolve().parent / "figures" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)
mpl.rcParams.update({"font.family": "serif", "font.serif": ["STIX Two Text", "STIXGeneral"],
                     "mathtext.fontset": "stix", "font.size": 9, "savefig.dpi": 400,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.03})
K = "black"
LW = 0.9


class S:
    """Minimal schematic primitives."""

    def __init__(self, ax):
        self.ax = ax

    def w(self, *pts, ls="-", lw=LW):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, ls, color=K, lw=lw, solid_capstyle="projecting", zorder=2)

    def dot(self, x, y):
        self.ax.add_patch(Circle((x, y), 1.5, color=K, zorder=4))

    def t(self, x, y, s, ha="center", va="center", it=False, size=9):
        self.ax.text(x, y, s, ha=ha, va=va, fontsize=size, style="italic" if it else "normal", zorder=5)

    def mos(self, xa, y, p=False, gate="left", name=""):
        """Vertical MOSFET, drain/source axis at xa, terminals at (xa, y +- 12).
        Returns the gate terminal (x, y)."""
        s = -1 if gate == "left" else 1
        xc = xa + s * 6
        self.w((xa, y + 12), (xa, y + 6), (xc, y + 6))
        self.w((xa, y - 12), (xa, y - 6), (xc, y - 6))
        self.w((xc, y - 8), (xc, y + 8), lw=1.5)
        xg = xc + s * 3
        self.w((xg, y - 6), (xg, y + 6), lw=1.2)
        if p:
            self.ax.add_patch(Circle((xg + s * 1.9, y), 1.9, fc="white", ec=K, lw=LW, zorder=3))
            self.w((xg + s * 3.8, y), (xg + s * 9, y))
        else:
            self.w((xg, y), (xg + s * 9, y))
        if name:
            self.t(xa - s * 3, y, name, ha="left" if s < 0 else "right", size=8)
        return xg + s * 9, y

    def vdd(self, x, y, label=True):
        self.w((x - 6, y), (x + 6, y), lw=1.2)
        if label:
            self.t(x, y + 2, "$V_{DD}$", va="bottom", size=8)

    def gnd(self, x, y):
        self.w((x, y), (x, y - 3))
        for k, h in enumerate((6, 4, 2)):
            self.w((x - h, y - 3 - 2 * k), (x + h, y - 3 - 2 * k), lw=1.0)

    def cap(self, x, ytop, ybot, label="", side="right"):
        ym = (ytop + ybot) / 2
        self.w((x, ytop), (x, ym + 2))
        self.w((x, ym - 2), (x, ybot))
        self.w((x - 6, ym + 2), (x + 6, ym + 2), lw=1.5)
        self.w((x - 6, ym - 2), (x + 6, ym - 2), lw=1.5)
        if label:
            self.t(x + (9 if side == "right" else -9), ym, label, ha="left" if side == "right" else "right")

    def isrc(self, x, ytop, ybot, label="", down=True):
        ym = (ytop + ybot) / 2
        self.w((x, ytop), (x, ym + 7))
        self.w((x, ym - 7), (x, ybot))
        self.ax.add_patch(Circle((x, ym), 7, fc="white", ec=K, lw=LW, zorder=3))
        self.ax.annotate("", xy=(x, ym - 4.5 if down else ym + 4.5), xytext=(x, ym + 4.5 if down else ym - 4.5),
                         arrowprops=dict(arrowstyle="-|>", color=K, lw=0.8, mutation_scale=6), zorder=4)
        if label:
            self.t(x + 10, ym, label, ha="left")

    def amp(self, x, y, wd, h, plus_top=True, label=""):
        """Amplifier triangle, inputs at (x, y +- h/4), output at (x + wd, y)."""
        self.ax.add_patch(Polygon([(x, y - h / 2), (x, y + h / 2), (x + wd, y)], closed=True,
                                  fc="white", ec=K, lw=1.1, zorder=3))
        top, bot = ("+", "−") if plus_top else ("−", "+")
        self.t(x + 5, y + h / 4, top, size=9)
        self.t(x + 5, y - h / 4, bot, size=9)
        if label:
            self.t(x + wd * 0.42, y, label, size=8)
        return (x, y + h / 4), (x, y - h / 4), (x + wd, y)

    def inv(self, x, y, h=16):
        self.ax.add_patch(Polygon([(x, y - h / 2), (x, y + h / 2), (x + h * 0.9, y)], closed=True,
                                  fc="white", ec=K, lw=1.1, zorder=3))
        self.ax.add_patch(Circle((x + h * 0.9 + 2, y), 2, fc="white", ec=K, lw=1.0, zorder=3))
        return x + h * 0.9 + 4

    def box(self, x0, y0, x1, y1, label, size=8):
        self.ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="white", ec=K, lw=1.0, zorder=3))
        self.t((x0 + x1) / 2, (y0 + y1) / 2, label, size=size)

    def group(self, x0, y0, x1, y1, label, where="top"):
        self.ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="#6a6a6a", lw=0.7, ls=(0, (4, 2)),
                                    zorder=1))
        if label:
            self.t(x0 + 3, y1 - 3 if where == "top" else y0 + 3, label, ha="left",
                   va="top" if where == "top" else "bottom", size=8)


def starved_stack(d, xa, ytop, vin, p_ctrl, n_ctrl, names, out_label):
    """Current-starved inverter: three devices in series between VDD (top) and GND.
    p_ctrl/n_ctrl: control-voltage label on the top (PMOS) or bottom (NMOS) device.
    Returns the gate terminals of the signal devices and the output node."""
    y1, y2, y3 = ytop - 12, ytop - 36, ytop - 60
    d.vdd(xa, ytop)
    if p_ctrl:       # VDD | MP_DZ (ctrl) | MP (in) | out | MN (in) | GND
        g1 = d.mos(xa, y1, p=True, name=names[0])
        g2 = d.mos(xa, y2, p=True, name=names[1])
        g3 = d.mos(xa, y3, p=False, name=names[2])
        out = (xa, (y2 + y3) / 2)
        d.t(g1[0] - 2, g1[1], p_ctrl, ha="right", it=True)
        gin = [g2, g3]
    else:            # VDD | MP (in) | out | MN (in) | MN_DZ (ctrl) | GND
        g1 = d.mos(xa, y1, p=True, name=names[0])
        g2 = d.mos(xa, y2, p=False, name=names[1])
        g3 = d.mos(xa, y3, p=False, name=names[2])
        out = (xa, (y1 + y2) / 2)
        d.t(g3[0] - 2, g3[1], n_ctrl, ha="right", it=True)
        gin = [g1, g2]
    d.gnd(xa, y3 - 12)
    d.dot(*out)
    return gin, out


def architecture():
    W, H = 516, 300
    fig = plt.figure(figsize=(W / 72, (H - 14) / 72))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(14, H)
    ax.set_aspect("equal")
    ax.axis("off")
    d = S(ax)

    # ======================= (a) signal path =====================================
    # stage 1 and its CMFB
    (ix1, iy1), (ix2, iy2), (ox, oy) = d.amp(40, 170, 44, 50, plus_top=False, label="St. 1")
    d.w((22, iy1), (ix1, iy1))
    d.t(20, iy1, "plus", ha="right", it=True)
    d.w((22, iy2), (ix1, iy2))
    d.t(20, iy2, "minus", ha="right", it=True)
    d.box(36, 92, 80, 114, "CMFB")
    d.w((58, 114), (58, 157.5))
    d.w((26, 103), (36, 103))
    d.t(24, 103, "$V_{1,CM}$", ha="right", it=True)
    # stage 2: two current-starved inverters fed by V_o1
    xbus = 112
    d.w((ox, oy), (xbus, oy))
    d.dot(xbus, oy)
    d.t(96, oy + 3, "$V_{o1}$", va="bottom", it=True)
    xa = 160
    gA, outA = starved_stack(d, xa, 288, "", "", "$V_{CTRLN}$", ("", "", "M$_{DZN}$"), "")
    gB, outB = starved_stack(d, xa, 140, "", "$V_{CTRLP}$", "", ("M$_{DZP}$", "", ""), "")
    ys = [g[1] for g in gA + gB]
    d.w((xbus, min(ys)), (xbus, max(ys)))
    for gx, gy in gA + gB:
        d.w((xbus, gy), (gx, gy))
        d.dot(xbus, gy) if gy not in (min(ys), max(ys)) else None
    # stage 3
    xo = 252
    d.vdd(xo, 262)
    gP = d.mos(xo, 250, p=True, name="MP3")
    gN = d.mos(xo, 104, p=False, name="MN3")
    d.gnd(xo, 92)
    d.w((xo, 238), (xo, 116))
    d.w(outA, (210, outA[1]), (210, gP[1]), gP)
    d.t(213, outA[1] + 3, "$V_{GP}$", ha="left", va="bottom", it=True)
    d.w(outB, (210, outB[1]), (210, gN[1]), gN)
    d.t(213, outB[1] + 3, "$V_{GN}$", ha="left", va="bottom", it=True)
    yo = 177
    d.dot(xo, yo)
    d.w((xo, yo), (300, yo))
    d.t(300, yo + 3, "$V_{out}$", ha="right", va="bottom", it=True)
    d.dot(284, yo)
    d.cap(284, yo, 146, "$C_L$")
    d.gnd(284, 146)
    d.group(124, 48, 236, 296, "")
    d.t(180, 44, "stage 2 (deadzone)", va="top", size=8)
    d.t(160, 26, "(a)", va="top")

    # ======================= (b) deadzone regulation =============================
    x0 = 330
    # trip-point replica: inverter with input tied to output -> V1,CM
    yt = 276
    xi = d.inv(x0 + 8, yt, 16)
    d.w((xi, yt), (xi + 8, yt), (xi + 8, yt + 14), (x0, yt + 14), (x0, yt), (x0 + 8, yt))
    d.t(x0 + 18, yt + 17, "trip-point replica", va="bottom", size=8)
    d.w((xi + 8, yt), (xi + 26, yt))
    d.t(xi + 28, yt, "$V_{1,CM}$ (to CMFB)", ha="left", it=True)
    d.dot(xi + 8, yt)
    # stage-2 replicas (same devices as in (a)) driven by V1,CM
    vb = x0 + 14
    d.w((xi + 8, yt), (xi + 8, 262), (vb, 262), (vb, 127))
    rows = ((237, "$V_{GP}'$", "$V_{CTRLN}$", "NOTA", "MP_R", True),
            (127, "$V_{GN}'$", "$V_{CTRLP}$", "POTA", "MN_R", False))
    xn, xr, xc = 452, 424, W - 12
    for yr, vout, ctrl, amp, ref, top in rows:
        d.box(vb + 10, yr - 15, vb + 64, yr + 15, "St.-2 replica\n(as in (a))")
        d.w((vb, yr), (vb + 10, yr))
        if yr != 127:
            d.dot(vb, yr)
        if top:
            d.w((vb + 37, yr + 15), (vb + 37, yr + 19))
            d.t(vb + 37, yr + 20, ctrl, va="bottom", it=True)
        else:
            d.w((vb + 37, yr - 15), (vb + 37, yr - 19))
            d.t(vb + 37, yr - 20, ctrl, va="top", it=True)
        pin, min_, out = d.amp(xn, yr - 9, 34, 36, plus_top=True, label=amp)
        d.w((vb + 64, yr), pin)
        d.t(vb + 67, yr + 3, vout, ha="left", va="bottom", it=True)
        # reference diode (replica of MP3 / MN3) on its 1-uA bias current
        if top:          # VDD | MP_R diode | node | 1 uA sink | GND
            d.vdd(xr, 202)
            gr = d.mos(xr, 190, p=True, gate="right")
            node = 178
            d.isrc(xr, node, 156, down=True)
            d.gnd(xr, 156)
            d.t(xr - 10, 167, "1 µA", ha="right", size=8)
        else:            # VDD | 1 uA source | node | MN_R diode | GND
            d.vdd(xr, 100)
            d.isrc(xr, 100, 78, down=True)
            node = 78
            gr = d.mos(xr, 66, p=False, gate="right")
            d.gnd(xr, 54)
            d.t(xr - 10, 89, "1 µA", ha="right", size=8)
        d.t(xr - 9, 190 if top else 66, ref, ha="right", size=8)
        # diode connection and reference output on one wire through the gate terminal
        d.w((xr, node), (gr[0], node))
        d.w((gr[0], min(gr[1], node)), (gr[0], min_[1]), min_)
        d.dot(xr, node)
        if gr[1] < node:          # T-junction (MN_R); for MP_R the node is the corner
            d.dot(gr[0], node)
        d.t(gr[0] + 3, node + 18 if top else node + 10, "$V_{GP,REF}$" if top else "$V_{GN,REF}$",
            ha="left", it=True)
        # output with its 2-pF decoupling capacitor
        d.w(out, (xc, out[1]))
        d.dot(xc, out[1])
        d.t(out[0] + 3, out[1] + 3, ctrl, ha="left", va="bottom", it=True)
        d.cap(xc, out[1], out[1] - 24, "2 pF", side="left")
        if top:
            d.gnd(xc, out[1] - 24)
        else:
            d.vdd(xc, out[1] - 24, label=False)
            d.t(xc, out[1] - 28, "$V_{DD}$", va="top", size=8)
    d.t(x0 + 95, 26, "(b)", va="top")
    fig.savefig(OUT / "fig_architecture.png")
    plt.close(fig)
    print("wrote", OUT / "fig_architecture.png")


if __name__ == "__main__":
    architecture()
