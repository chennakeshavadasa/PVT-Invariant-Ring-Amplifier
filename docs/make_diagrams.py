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
            self.txt(x + 1.3, y + h / 4, "+")
            self.txt(x + 1.3, y - h / 4, "−")
        if label:
            self.txt(x + wdt * 0.40, y, label)

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
            self.txt(x + 1.7, y, label, ha="left")

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
            self.txt(x + 1.7, y, label, ha="left")

    def region(self, x0, y0, x1, y1, label, color):
        self.ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=1.2",
                                         fc=color, ec="none", alpha=0.10, zorder=0))
        self.txt(x0 + 1.0, y1 - 0.8, label, ha="left", va="top", color="#3a3a3a")

    def box(self, x0, y0, x1, y1, label, size=9):
        self.ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.6",
                                         fc="white", ec=INK, lw=LW * 1.1, zorder=3))
        self.txt((x0 + x1) / 2, (y0 + y1) / 2, label, size=size)


def architecture():
    fig, ax = plt.subplots(figsize=(7.16, 5.0))
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 104.5)
    ax.set_aspect("equal")
    ax.axis("off")
    d = D(ax)
    d.region(1, 56, 149, 104, "(a) Signal path: three-stage ring amplifier", GREY)
    d.region(1, 1, 41, 53, "(b) Bias", ORANGE)
    d.region(44, 1, 149, 53, "(c) Deadzone regulation loop", BLUE)
    # ---- (a) stage 1 + CMFB ------------------------------------------------------
    d.amp(16, 82, 15, 15, signs=False)
    d.txt(22.0, 82, "St. 1")
    d.txt(17.3, 85.6, "−")            # plus is the inverting input of the original design
    d.txt(17.3, 78.4, "+")
    d.w((11, 85.6), (16, 85.6))
    d.txt(10.4, 85.6, "plus", ha="right", style="italic")
    d.w((11, 78.4), (16, 78.4))
    d.txt(10.4, 78.4, "minus", ha="right", style="italic")
    d.box(15, 60, 31, 68, "CMFB")
    d.w((23, 68), (23, 76.2), color=GREY)
    d.txt(24.2, 71.8, "$R_1$, $R_3$ sense", ha="left", color="#555555")
    d.w((11, 64), (15, 64))
    d.txt(10.4, 64, "$V_{1,CM}$", ha="right", style="italic")
    # ---- stage 2 (current-starved inverters) ---------------------------------------
    d.w((31, 82), (43, 82))
    d.net(34, 82.5, "$V_{o1}$")
    d.dot(43, 82)
    d.w((43, 82), (43, 91), (48, 91))
    d.w((43, 82), (43, 73), (48, 73))
    o1 = d.inv(48, 91, 5.0)
    o2 = d.inv(48, 73, 5.0)
    d.w((50.5, 93.5), (50.5, 96.0), color=BLUE)
    d.txt(50.5, 96.6, "$V_{CTRLN}$", va="bottom", style="italic", color=BLUE)
    d.w((50.5, 70.5), (50.5, 68.0), color=BLUE)
    d.txt(50.5, 67.4, "$V_{CTRLP}$", va="top", style="italic", color=BLUE)
    # ---- stage 3 -----------------------------------------------------------------
    d.w((o1, 91), (68, 91))
    d.net(58.5, 91.5, "$V_{GP}$")
    d.w((o2, 73), (68, 73))
    d.net(58.5, 73.5, "$V_{GN}$")
    xp = d.mos(68, 91, pmos=True)
    xn = d.mos(68, 73, pmos=False)
    d.w((xp, 94), (xp, 97))
    d.txt(xp, 97.6, "$V_{DD}$", va="bottom")
    d.w((xp, 88), (xp, 76))
    d.w((xn, 70), (xn, 67.5))
    d.gnd(xn, 67.5)
    d.txt(xp + 1.4, 93.2, "MP3", ha="left")
    d.txt(xp + 1.4, 70.8, "MN3", ha="left")
    d.dot(xp, 82)
    d.w((xp, 82), (100, 82))
    d.net(91, 82.5, "$V_{out}$")
    d.dot(84, 82)
    d.w((84, 82), (84, 78.6))
    d.cap(84, 78.0)
    d.w((84, 77.4), (84, 74.5))
    d.gnd(84, 74.5)
    d.txt(86.2, 78.0, "$C_L$ = 50 pF", ha="left")
    # trip-point replica
    d.box(113, 66, 146, 92, "Trip-point replica\n(stage-2 inverters,\ninput tied to output)")
    d.w((113, 72), (106, 72))
    d.txt(105.4, 72, "$V_{1,CM}$", ha="right", style="italic")
    # ---- (c) regulation loop -------------------------------------------------------
    d.txt(50.4, 28, "$V_{1,CM}$", ha="right", style="italic")
    d.w((51, 28), (55, 28))
    d.dot(55, 28)
    yn, yp = 34.0, 18.0                     # NOTA and POTA (inputs at y +- 3.25)
    d.w((55, 28), (55, yn + 3.25), (59, yn + 3.25))
    d.w((55, 28), (55, yp + 3.25), (59, yp + 3.25))
    r1 = d.inv(59, yn + 3.25, 5.0)
    r2 = d.inv(59, yp + 3.25, 5.0)
    d.txt(64.5, 29.0, "St.-2\nreplica")
    d.w((61.5, yn + 5.75), (61.5, yn + 8.0), color=BLUE)
    d.txt(61.5, yn + 8.6, "$V_{CTRLN}$", va="bottom", style="italic", color=BLUE)
    d.w((61.5, yp + 0.75), (61.5, yp - 1.5), color=BLUE)
    d.txt(61.5, yp - 2.1, "$V_{CTRLP}$", va="top", style="italic", color=BLUE)
    d.w((r1, yn + 3.25), (76, yn + 3.25))
    d.w((r2, yp + 3.25), (76, yp + 3.25))
    d.amp(76, yn, 16, 13)
    d.txt(82.5, yn, "NOTA")
    d.amp(76, yp, 16, 13)
    d.txt(82.5, yp, "POTA")
    d.w((76, yn - 3.25), (73, yn - 3.25), (73, 26.8), (96, 26.8))
    d.net(84.5, 27.3, "$V_{GP,REF}$", va="bottom")
    d.w((76, yp - 3.25), (73, yp - 3.25), (73, 7.0), (96, 7.0))
    d.net(77.5, 6.5, "$V_{GN,REF}$", va="top")
    d.box(96, 23.3, 127, 30.3, "MP_R diode, 1 µA")
    d.box(96, 3.5, 127, 10.5, "MN_R diode, 1 µA")
    d.w((92, yn), (140, yn), color=BLUE)
    d.dot(140, yn, color=BLUE)
    d.txt(110, yn + 0.6, "$V_{CTRLN}$ to stage 2", va="bottom", style="italic", color=BLUE)
    d.w((140, yn), (140, yn - 2.4), color=BLUE)
    d.cap(140, yn - 3.0)
    d.w((140, yn - 3.6), (140, yn - 6.0))
    d.gnd(140, yn - 6.0)
    d.txt(142.2, yn - 3.0, "2 pF", ha="left")
    d.w((92, yp), (140, yp), color=BLUE)
    d.dot(140, yp, color=BLUE)
    d.txt(110, yp + 0.6, "$V_{CTRLP}$ to stage 2", va="bottom", style="italic", color=BLUE)
    d.w((140, yp), (140, yp - 2.4), color=BLUE)
    d.cap(140, yp - 3.0)
    d.w((140, yp - 3.6), (140, yp - 6.0))
    d.txt(140, yp - 6.6, "$V_{DD}$", va="top")
    d.txt(142.2, yp - 3.0, "2 pF", ha="left")
    d.txt(96.5, 47.2, "MP3, MN3 = 4 × (MP_R, MN_R)   $\\Rightarrow$   $I_Q$ = 4 $I_{BIAS}$")
    # ---- (b) bias -------------------------------------------------------------------
    d.txt(11, 45.6, "$V_{DD}$", va="bottom")
    d.w((11, 45.3), (11, 42.7))
    d.isrc(11, 41.5, "", down=True)
    d.txt(13.6, 41.5, "$I_{BIAS}$ = 1 µA", ha="left")
    d.w((11, 40.3), (11, 36))
    d.box(4, 4, 38, 36, "Current mirrors\n(0.5/8-µm units)\n\nstage-1 tail 10 µA\nCMFB tail 10 µA\n"
                        "OTA tails 2 µA\nreplica refs 1 µA")
    fig.savefig(OUT / "fig_architecture.png")
    plt.close(fig)
    print("wrote", OUT / "fig_architecture.png")


if __name__ == "__main__":
    architecture()
