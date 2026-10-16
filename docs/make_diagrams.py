#!/usr/bin/env python3
"""Architecture diagram of the layout-ready ring amplifier (docs/figures/diagrams/)."""
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon  # noqa: E402

OUT = Path(__file__).resolve().parent / "figures" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)
mpl.rcParams.update({"font.family": "serif", "font.serif": ["STIX Two Text", "STIXGeneral"],
                     "mathtext.fontset": "stix", "font.size": 9, "savefig.dpi": 300,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.04})
INK, BLUE, ORANGE, GREY = "#2b2b2b", "#2a78d6", "#eb6834", "#8c8c8c"
LW = 1.0


class D:
    def __init__(self, ax):
        self.ax = ax

    def w(self, *pts, color=INK, ls="-", lw=LW):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, ls, color=color, lw=lw, solid_capstyle="butt", zorder=2)

    def dot(self, x, y, color=INK):
        self.ax.add_patch(Circle((x, y), 0.45, color=color, zorder=4))

    def net(self, x, y, s, ha="left", va="bottom", color=INK, size=9):
        self.ax.text(x, y, s, ha=ha, va=va, style="italic", color=color, fontsize=size, zorder=5)

    def txt(self, x, y, s, ha="center", va="center", size=9, color=INK, **kw):
        self.ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color, zorder=5, **kw)

    def amp(self, x, y, wdt, h, label="", signs=True, color=INK):
        """Amplifier triangle pointing right; inputs at x, output at x + wdt."""
        self.ax.add_patch(Polygon([(x, y - h / 2), (x, y + h / 2), (x + wdt, y)], closed=True,
                                  fc="white", ec=color, lw=LW * 1.2, zorder=3))
        if signs:
            self.txt(x + 1.0, y + h / 4, "+", size=8)
            self.txt(x + 1.0, y - h / 4, "−", size=8)
        if label:
            self.txt(x + wdt * 0.40, y, label, size=8)

    def inv(self, x, y, s=3.0, color=INK):
        """Inverter: triangle + bubble; input at x, output at x + s + 0.9."""
        self.ax.add_patch(Polygon([(x, y - s / 2), (x, y + s / 2), (x + s, y)], closed=True,
                                  fc="white", ec=color, lw=LW * 1.2, zorder=3))
        self.ax.add_patch(Circle((x + s + 0.45, y), 0.45, fc="white", ec=color, lw=LW * 1.2, zorder=3))
        return x + s + 0.9

    def cap(self, x, y, vertical=True, label=""):
        g = 0.55
        self.w((x - 1.3, y + g), (x + 1.3, y + g), lw=1.6)
        self.w((x - 1.3, y - g), (x + 1.3, y - g), lw=1.6)
        if label:
            self.txt(x + 1.7, y, label, ha="left", size=8)

    def gnd(self, x, y):
        self.w((x - 1.2, y), (x + 1.2, y), lw=1.2)
        self.w((x - 0.75, y - 0.45), (x + 0.75, y - 0.45), lw=1.0)
        self.w((x - 0.3, y - 0.9), (x + 0.3, y - 0.9), lw=0.8)

    def mos(self, x, y, pmos):
        """Simplified MOSFET: gate at x (input), channel at x + 1.6, drain/source vertical."""
        self.w((x, y), (x + 1.0 - (0.5 if pmos else 0), y))
        if pmos:
            self.ax.add_patch(Circle((x + 0.75, y), 0.25, fc="white", ec=INK, lw=LW, zorder=3))
        self.w((x + 1.0, y - 1.4), (x + 1.0, y + 1.4), lw=1.4)
        self.w((x + 1.5, y - 1.6), (x + 1.5, y + 1.6), lw=1.4)
        self.w((x + 1.5, y + 1.3), (x + 2.8, y + 1.3), (x + 2.8, y + 3.0))
        self.w((x + 1.5, y - 1.3), (x + 2.8, y - 1.3), (x + 2.8, y - 3.0))
        return x + 2.8

    def isrc(self, x, y, label="", down=True):
        self.ax.add_patch(Circle((x, y), 1.2, fc="white", ec=INK, lw=LW * 1.2, zorder=3))
        self.ax.annotate("", xy=(x, y - 0.7 if down else y + 0.7), xytext=(x, y + 0.7 if down else y - 0.7),
                         arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=7), zorder=4)
        if label:
            self.txt(x + 1.7, y, label, ha="left", size=8)

    def region(self, x0, y0, x1, y1, label, color):
        self.ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=1.2",
                                         fc=color, ec="none", alpha=0.10, zorder=0))
        self.txt(x0 + 0.8, y1 - 0.6, label, ha="left", va="top", size=8, color="#4a4a4a")

    def box(self, x0, y0, x1, y1, label, size=8):
        self.ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.6",
                                         fc="white", ec=INK, lw=LW * 1.1, zorder=3))
        self.txt((x0 + x1) / 2, (y0 + y1) / 2, label, size=size)


def architecture():
    fig, ax = plt.subplots(figsize=(7.16, 4.75))
    ax.set_xlim(0, 140)
    ax.set_ylim(0, 93)
    ax.set_aspect("equal")
    ax.axis("off")
    d = D(ax)
    d.region(1, 51, 139, 92, "Signal path: three-stage ring amplifier", GREY)
    d.region(38, 3, 139, 48, "Deadzone regulation loop (thesis Fig. 3.6)", BLUE)
    d.region(1, 3, 35, 48, "Bias (external $I_{BIAS}$)", ORANGE)
    # ---- stage 1 + CMFB --------------------------------------------------------
    d.amp(14, 74, 13, 13, signs=False)
    d.txt(19.2, 74, "St. 1", size=8)
    d.txt(15.1, 77.2, "−", size=8)      # plus is the inverting input of the original design
    d.txt(15.1, 70.8, "+", size=8)
    d.w((9, 77.2), (14, 77.2))
    d.txt(8.5, 77.2, "plus", ha="right", style="italic")
    d.w((9, 70.8), (14, 70.8))
    d.txt(8.5, 70.8, "minus", ha="right", style="italic")
    d.box(13, 55, 28, 62, "CMFB", size=8)
    d.w((20.5, 62), (20.5, 68.5), color=GREY)
    d.txt(21.5, 65.2, "$R_1, R_3$ sense", ha="left", size=7.5, color="#555555")
    d.w((9, 58.5), (13, 58.5))
    d.txt(8.5, 58.5, "$V_{1,CM}$", ha="right", style="italic")
    # ---- stage 2 ---------------------------------------------------------------
    d.w((27, 74), (38, 74))
    d.net(29.5, 74.5, "$V_{o1}$")
    d.dot(38, 74)
    d.w((38, 74), (38, 82), (43, 82))
    d.w((38, 74), (38, 66), (43, 66))
    o1 = d.inv(43, 82, 4.0)
    o2 = d.inv(43, 66, 4.0)
    d.w((45, 84), (45, 85.6), color=BLUE)
    d.txt(45.6, 85.4, "$V_{CTRLN}$", ha="left", va="bottom", style="italic", color=BLUE, size=8)
    d.w((45, 64), (45, 62.4), color=BLUE)
    d.txt(45.6, 62.6, "$V_{CTRLP}$", ha="left", va="top", style="italic", color=BLUE, size=8)
    # ---- stage 3 ---------------------------------------------------------------
    d.w((o1, 82), (60, 82))
    d.net(52.5, 82.5, "$V_{GP}$")
    d.w((o2, 66), (60, 66))
    d.net(52.5, 66.5, "$V_{GN}$")
    xp = d.mos(60, 82, pmos=True)
    xn = d.mos(60, 66, pmos=False)
    d.w((xp, 85), (xp, 88))
    d.txt(xp, 88.6, "$V_{DD}$", va="bottom", size=8)
    d.w((xp, 79), (xp, 69))
    d.w((xn, 63), (xn, 61))
    d.gnd(xn, 61)
    d.txt(xp + 1.2, 84.3, "MP3", ha="left", size=8)
    d.txt(xp + 1.2, 63.5, "MN3", ha="left", size=8)
    d.dot(xp, 74)
    d.w((xp, 74), (88, 74))
    d.net(80.5, 74.5, "$V_{out}$")
    d.dot(75, 74)
    d.w((75, 74), (75, 70.6))
    d.cap(75, 70.0)
    d.w((75, 69.4), (75, 67))
    d.gnd(75, 67)
    d.txt(77.0, 70.0, "$C_L$", ha="left", size=8)
    # trip-point replica
    d.box(95, 62, 136, 82, "Trip-point replica (STG1_CM)\n\nSt.-2 inverters, input = output\n"
                           "$\\Rightarrow$ $V_{1,CM}$ = switching point of St. 2", size=7.5)
    d.w((95, 66), (91, 66))
    d.txt(90.5, 66, "$V_{1,CM}$", ha="right", style="italic")
    # ---- regulation loop ------------------------------------------------------
    d.txt(42.5, 31, "$V_{1,CM}$", ha="right", style="italic")
    d.w((43, 31), (48, 31))
    d.dot(48, 31)
    d.w((48, 31), (48, 38), (52, 38))
    d.w((48, 31), (48, 18), (52, 18))
    r1 = d.inv(52, 38, 4.0)
    r2 = d.inv(52, 18, 4.0)
    d.txt(57, 28, "St.-2\nreplica", size=7.5)
    d.w((54, 40), (54, 41.6), color=BLUE)
    d.txt(54.6, 41.4, "$V_{CTRLN}$", ha="left", va="bottom", style="italic", color=BLUE, size=7.5)
    d.w((54, 16), (54, 14.4), color=BLUE)
    d.txt(54.6, 14.6, "$V_{CTRLP}$", ha="left", va="top", style="italic", color=BLUE, size=7.5)
    d.w((r1, 38), (66, 38))
    d.w((r2, 18), (66, 18))
    d.amp(66, 36, 13, 11)
    d.txt(70.8, 36, "NOTA", size=7.5)
    d.amp(66, 20, 13, 11)
    d.txt(70.8, 20, "POTA", size=7.5)
    # references (replicas of MP3 / MN3)
    d.box(88, 26, 110, 33, "MP_R diode, 1 µA", size=7.5)
    d.box(88, 8, 110, 15, "MN_R diode, 1 µA", size=7.5)
    d.w((66, 33.3), (63, 33.3), (63, 29.5), (88, 29.5))
    d.net(69, 29.0, "$V_{GP,REF}$", va="top", size=8)
    d.w((66, 17.3), (63, 17.3), (63, 11.5), (88, 11.5))
    d.net(69, 11.0, "$V_{GN,REF}$", va="top", size=8)
    # outputs with decoupling
    d.w((79, 36), (118, 36), color=BLUE)
    d.dot(118, 36, color=BLUE)
    d.txt(96, 36.6, "$V_{CTRLN} \\rightarrow$ St. 2", ha="left", va="bottom", style="italic", color=BLUE, size=8)
    d.w((118, 36), (118, 32.6), color=BLUE)
    d.cap(118, 32.0)
    d.w((118, 31.4), (118, 29))
    d.gnd(118, 29)
    d.txt(119.8, 32.0, "2 pF", ha="left", size=7.5)
    d.w((79, 20), (124, 20), color=BLUE)
    d.dot(124, 20, color=BLUE)
    d.txt(96, 20.6, "$V_{CTRLP} \\rightarrow$ St. 2", ha="left", va="bottom", style="italic", color=BLUE, size=8)
    d.w((124, 20), (124, 16.6), color=BLUE)
    d.cap(124, 16.0)
    d.w((124, 15.4), (124, 12.5))
    d.txt(124, 12.0, "$V_{DD}$", va="top", size=7.5)
    d.txt(125.8, 16.0, "2 pF", ha="left", size=7.5)
    d.txt(137, 5.2, "MP3, MN3 = 4 × (MP_R, MN_R)  $\\Rightarrow$  $I_Q$ = 4 $I_{BIAS}$",
          ha="right", size=8)
    # ---- bias -----------------------------------------------------------------
    d.txt(9, 41.5, "$V_{DD}$", size=7.5)
    d.w((9, 40.5), (9, 38.2))
    d.isrc(9, 37, "$I_{BIAS}$ = 1 µA", down=True)
    d.w((9, 35.8), (9, 31))
    d.box(4, 7, 32, 31, "NMOS / PMOS mirrors\n(0.5/8 µm units,\ncommon centroid)\n\n"
                        "St.-1 tail 10 µA\nCMFB tail 10 µA\nOTA tails 2 µA\nreplica refs 1 µA", size=7.5)
    fig.savefig(OUT / "fig_architecture.png")
    plt.close(fig)
    print("wrote", OUT / "fig_architecture.png")


if __name__ == "__main__":
    architecture()
