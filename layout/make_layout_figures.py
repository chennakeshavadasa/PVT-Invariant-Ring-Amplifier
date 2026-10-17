#!/usr/bin/env python3
"""Annotated layout figures from layout/RAMP_LR.gds (RAMP_V2.gds with the argument v2) and the
placement file written by gen_layout.py.

Renders views with KLayout (layout/render.py) and labels the blocks and, in the
close-ups, the device of every finger.  Output: docs/figures/layout/.
Run after gen_layout.py:  python3 layout/make_layout_figures.py [v2]
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT = REPO / "docs" / "figures" / "layout"
OUT.mkdir(parents=True, exist_ok=True)
V2 = len(sys.argv) > 1 and sys.argv[1] == "v2"
TOP = "RAMP_V2" if V2 else "RAMP_LR"
GDS = HERE / f"{TOP}.gds"
P = json.load(open(HERE / f"{TOP}_placement.json"))
TOPM = "50/0,49/0,66/0,67/0,126/0,129/0,36/0,125/0"                 # Metal4 and above (MIM)
UPPER = "10/0,19/0,29/0,30/0,30/25,30/2," + TOPM                     # Metal2 and above

mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
    "mathtext.fontset": "stix", "font.size": 9, "savefig.dpi": 300, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})
INK, BLUE, ORANGE, GREY = "#2b2b2b", "#2a78d6", "#eb6834", "#8c8c8c"

ROLE = {"bn0": None, "bp": "PMOS bias mirror", "pota_ld": "POTA load",
        "nota_in": "NOTA input pair", "rhigh": "rhigh CM sense (R1/R3)", "s1_n": "stage-1 + CMFB pairs",
        "s2_n": "stage 2 / replicas (N)", "out_n": "output NMOS", "pota_in": "POTA input pair",
        "nota_ld": "NOTA load", "s1_p": "stage-1 loads", "s2_p": "stage 2 / replicas (P)", "out_p": "output PMOS"}


def render(box, width, hide=None):
    tmp = Path(tempfile.mkdtemp()) / "v.png"
    cmd = ["klayout", "-b", "-r", str(HERE / "render.py"), "-rd", f"gds={GDS}", "-rd", f"png={tmp}",
           "-rd", "box=" + ",".join(f"{v:.3f}" for v in box), "-rd", f"w={width}"]
    if hide:
        cmd += ["-rd", f"hide={hide}"]
    subprocess.run(cmd, check=True, capture_output=True)
    return mpimg.imread(tmp)


def lab(ax, x, y, s, va="center", ha="center", color=INK, size=9):
    ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color,
            bbox=dict(fc="white", ec="#9a9a9a", lw=0.4, pad=1.2, alpha=0.92))


def fig_full():
    x0, y0, x1, y1 = P["bbox"]
    box = (x0 - 0.5, y0 - 0.5, x1 + 0.5, y1 + 0.5)
    img = render(box, 2400, TOPM)
    w = 7.16
    fig = plt.figure(figsize=(w, w * (box[3] - box[1]) / (box[2] - box[0]) + 0.95))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.imshow(img, extent=(box[0], box[2], box[1], box[3]), interpolation="lanczos")
    ax.set_xlim(box[0], box[2])
    ax.set_ylim(box[1] - 7.0, box[3] + 3.5)
    ax.set_axis_off()
    S = P["strips"]
    for m in P["mims"]:
        ax.add_patch(Rectangle((m["x0"], m["y0"]), m["x1"] - m["x0"], m["y1"] - m["y0"], fill=False,
                               ec=ORANGE, lw=1.0, ls="--"))
    name = {"x3.CDP": "2-pF MIM on $V_{CTRLP}$ (dashed)", "x3.CDN": "2-pF MIM on $V_{CTRLN}$ (dashed)"}
    for m in P["mims"]:
        ax.text((m["x0"] + m["x1"]) / 2, box[1] - 0.4, name[m["ref"]], ha="center", va="top", color=ORANGE)
    # PMOS signal row: labels above the block; the other rows: labels on the strips
    top = max(s["y1"] for s in S.values())
    for k in ("pota_in", "nota_ld", "s1_p", "s2_p", "out_p"):
        s = S[k]
        ax.text((s["x0"] + s["x1"]) / 2, box[3] + 0.3, ROLE[k], ha="center", va="bottom")
        ax.plot([(s["x0"] + s["x1"]) / 2] * 2, [box[3] + 0.25, top + 0.6], "-", color=GREY, lw=0.5)
    for k in ("nota_in", "rhigh", "s1_n", "s2_n", "out_n", "bp", "pota_ld"):
        s = S[k]
        lab(ax, (s["x0"] + s["x1"]) / 2, s["y0"] - 1.6, ROLE[k])
    bn = [S[f"bn{i}"] for i in range(4)]
    lab(ax, (bn[0]["x0"] + bn[0]["x1"]) / 2, (bn[1]["y1"] + bn[2]["y0"]) / 2,
        "NMOS bias mirror: 4 rows × 0.5/8-µm fingers, interdigitated")
    ax.plot([x0 + 1, x0 + 11], [box[1] - 4.4] * 2, "-", color=INK, lw=2)
    ax.text(x0 + 6, box[1] - 4.8, "10 µm", ha="center", va="top")
    ax.text(x1, box[1] - 4.8, f"{x1 - x0:.1f} µm × {y1 - y0:.1f} µm = {(x1 - x0) * (y1 - y0) / 1e6:.4f} mm²",
            ha="right", va="top")
    fig.savefig(OUT / "fig_layout_full.png")
    plt.close(fig)
    print("wrote", OUT / "fig_layout_full.png")


def zoom(ax, names, pad=0.8, hide=UPPER, width=1400, ytop=1.4, ybot=1.4):
    xs = [S for n in names for S in (P["strips"][n]["x0"], P["strips"][n]["x1"])]
    ys = [S for n in names for S in (P["strips"][n]["y0"], P["strips"][n]["y1"])]
    box = (min(xs) - pad, min(ys) - ybot, max(xs) + pad, max(ys) + ytop)
    ax.imshow(render(box, width, hide), extent=(box[0], box[2], box[1], box[3]), interpolation="lanczos")
    ax.set_xlim(box[0], box[2])
    ax.set_ylim(box[1], box[3])
    ax.tick_params(direction="in", top=True, right=True)
    return box


def label_fingers(ax, strip, names, y, size=9):
    for f in P["strips"][strip]["fingers"]:
        s = "D" if f["ref"] == "D" else names.get(f["ref"], "?")
        ax.text(f["x"], y, s, ha="center", va="bottom", fontsize=size, fontweight="bold",
                color=ORANGE if s == "D" else INK, bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.85))


def fig_matching():
    fig = plt.figure(figsize=(7.16, 8.8))
    gs = fig.add_gridspec(5, 2, height_ratios=[1.35, 1, 2.0, 1, 1], hspace=0.75, wspace=0.12)
    bias = {"xb.MB0": "R", "xb.MB1": "T", "xb.MB2": "C", "xb.MB3": "N", "xb.MB4": "Q", "xb.MB5": "P"}
    a = fig.add_subplot(gs[0, :])
    zoom(a, [f"bn{i}" for i in range(4)], width=2400, ytop=1.2, ybot=1.0)
    for i in range(4):
        s = P["strips"][f"bn{i}"]
        label_fingers(a, f"bn{i}", bias, s["y1"] + 0.05 if i % 2 == 0 else s["y0"] - 0.75)
    a.set_title("(a) NMOS bias mirror: R reference (MB0), T stage-1 tail (×10), C CMFB tail (×10), N NOTA tail (×2), "
                "Q, P 1-µA branches, D dummy", fontsize=9)
    panels = [("s1_n", {"x1.MN1": "A", "x1.MN2": "B", "x1.MC1": "C", "x1.MC2": "E", "x3.MCN": "K"},
               "(b) stage-1 pair A/B and CMFB pair C/E, ABBA"),
              ("s1_p", {"x1.MP1": "A", "x1.MP2": "B", "x1.MPC1": "C", "x1.MPC2": "E"},
               "(c) stage-1 loads A/B and CMFB diodes C/E, ABBA"),
              ("out_n", {"M1": "M", "x3.MN_STG2_3N_R": "R"}, "(d) MN3 (M, ×4) next to its replica R"),
              ("out_p", {"M2": "M", "x3.MP_STG2_3P_R": "R"}, "(e) MP3 (M, ×4) next to its replica R"),
              ("pota_in", {"x3.x1.M2": "A", "x3.x1.M1": "B", "x3.MCP": "K"}, "(f) POTA input pair A/B, ABBA"),
              ("nota_in", {"x3.x2.M1": "A", "x3.x2.M2": "B"}, "(g) NOTA input pair A/B, ABBA")]
    for k, (st, names, title) in enumerate(panels):
        ax = fig.add_subplot(gs[1 + k // 2, k % 2])
        zoom(ax, [st], ytop=1.0 if st == "out_p" else 1.4, ybot=1.2 if st == "out_p" else 1.4)
        s = P["strips"][st]
        up = st in ("s1_n", "out_n", "nota_in")
        label_fingers(ax, st, names, s["y1"] + 0.1 if up else s["y0"] - 1.0)
        ax.set_title(title, fontsize=9)
    ax = fig.add_subplot(gs[4, :])
    zoom(ax, ["s2_p"], width=2400, ytop=1.0, ybot=1.5)
    s = P["strips"]["s2_p"]
    groups = {}
    for f in s["fingers"]:
        if f["ref"] != "D":
            groups.setdefault(f["ref"].split(".")[0], []).append(f["x"])
    title = {"x2": "stage 2", "x3": "stage-2 replica", "x4": "trip-point replica"}
    for g, xs in groups.items():
        ax.text((min(xs) + max(xs)) / 2, s["y0"] - 1.3, title[g], ha="center", va="bottom", fontsize=9,
                bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.9))
    ax.set_title("(h) stage-2 PMOS chains, 0.15/0.13 µm: every diffusion shared, replica next to the signal path",
                 fontsize=9)
    ax.set_xlabel("x (µm)")
    fig.savefig(OUT / "fig_layout_matching.png")
    plt.close(fig)
    print("wrote", OUT / "fig_layout_matching.png")


ROLE2 = {"nb0": "NMOS bias mirror (0.5/8 µm)", "nb1": "bias mirror, integrator sinks", "trn": "trip NMOS",
         "nlo_a": "nA divider + regulation tail", "nlo_b": "nA divider + servo tail",
         "rg_in": "regulation pair (hv 4/4)", "sv_in": "servo pair (hv 3/3)", "rhigh_a": "R_S, R_Z",
         "rhigh_b": "R_TA, R_TB", "pmir": "integrator mirrors", "p11": "PMOS divider, integrator outputs",
         "rhigh_c": "R1/R3", "s1n": "stage-1 loads", "s2n": "st.-2 N", "dzn": "starve", "out_n": "MN3",
         "s1p": "stage-1 PMOS input pair (ABBA)", "s2p": "stage 2 (P)", "out_p": "MP3 + MP_R",
         "pt": "PMOS tail mirror (stage 1, CMFB)", "cm": "CMFB pair", "trp": "trip PMOS"}


def fig_full_v2():
    x0, y0, x1, y1 = P["bbox"]
    box = (x0 - 0.5, y0 - 0.5, x1 + 0.5, y1 + 0.5)
    img = render(box, 2400, TOPM)
    w = 7.16
    fig = plt.figure(figsize=(w, w * (box[3] - box[1] + 12) / (box[2] - box[0])))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.imshow(img, extent=(box[0], box[2], box[1], box[3]), interpolation="lanczos")
    ax.set_xlim(box[0], box[2])
    ax.set_ylim(box[1] - 8.5, box[3] + 1.0)
    ax.set_axis_off()
    S = P["strips"]
    for m in P["mims"]:
        ax.add_patch(Rectangle((m["x0"], m["y0"]), m["x1"] - m["x0"], m["y1"] - m["y0"], fill=False,
                               ec=ORANGE, lw=1.0, ls="--"))
    cap = {"xr.CC": "4-pF MIM of the regulation integrator (dashed)", "xs.CC": "1-pF MIM of the servo (dashed)"}
    for m in P["mims"]:
        ax.text((m["x0"] + m["x1"]) / 2, box[1] - 0.4, cap[m["ref"]], ha="center", va="top", color=ORANGE)
    for k, s in S.items():
        if k not in ROLE2:
            continue
        lab(ax, (s["x0"] + s["x1"]) / 2, (s["y0"] + s["y1"]) / 2, ROLE2[k], size=7)
    ax.plot([x0 + 1, x0 + 11], [box[1] - 5.0] * 2, "-", color=INK, lw=2)
    ax.text(x0 + 6, box[1] - 5.4, "10 µm", ha="center", va="top")
    ax.text(x1, box[1] - 5.4, f"{x1 - x0:.1f} µm × {y1 - y0:.1f} µm = {(x1 - x0) * (y1 - y0) / 1e6:.4f} mm²",
            ha="right", va="top")
    fig.savefig(OUT / "fig_layout_v2_full.png")
    plt.close(fig)
    print("wrote", OUT / "fig_layout_v2_full.png")


def fig_matching_v2():
    fig = plt.figure(figsize=(7.16, 8.2))
    gs = fig.add_gridspec(5, 2, height_ratios=[1.0, 0.75, 1.5, 0.75, 0.9], hspace=0.85, wspace=0.15)
    a = fig.add_subplot(gs[0, :])
    zoom(a, ["s1p"], width=2400, ytop=1.0, ybot=1.4)
    label_fingers(a, "s1p", {"x1.MN1": "A", "x1.MN2": "B"}, P["strips"]["s1p"]["y0"] - 1.0, size=7)
    a.set_title("(a) stage-1 PMOS input pair, 16 + 16 fingers of 2.5/0.5 µm, ABBA × 8, dummies D", fontsize=9)
    b = fig.add_subplot(gs[1, :])
    zoom(b, ["s1n"], width=2400, ytop=1.6, ybot=1.0)
    label_fingers(b, "s1n", {"x1.MP1": "A", "x1.MP2": "B", "x1.MPC1": "C", "x1.MPC2": "E"},
                  P["strips"]["s1n"]["y1"] + 0.1, size=7)
    b.set_title("(b) stage-1 NMOS loads A/B (ABBA) and the CMFB diodes C/E (1/2 µm)", fontsize=9)
    c = fig.add_subplot(gs[2, 0])
    zoom(c, ["out_p"], ytop=1.0, ybot=1.4)
    label_fingers(c, "out_p", {"M2": "M", "xr.MPR": "R"}, P["strips"]["out_p"]["y0"] - 1.0, size=7)
    c.set_title("(c) MP3 (M, ×4) around MP_R (R, ×2)", fontsize=9)
    e = fig.add_subplot(gs[2, 1])
    zoom(e, ["rg_in"], ytop=1.6, ybot=1.4)
    label_fingers(e, "rg_in", {"xr.M1": "A", "xr.M2": "B"}, P["strips"]["rg_in"]["y1"] + 0.1, size=8)
    e.set_title("(d) regulation-integrator pair A/B (hv 4/4 µm)", fontsize=9)
    d = fig.add_subplot(gs[3, :])
    zoom(d, ["nb0"], width=2400, ytop=1.6, ybot=1.0)
    label_fingers(d, "nb0", {"xb.MB4": "Q", "xb.MB0": "R", "xb.MB2": "P", "xb.MBL0": "L"},
                  P["strips"]["nb0"]["y1"] + 0.1, size=7)
    d.set_title("(e) NMOS bias row (0.5/8 µm): I_Q reference Q (×2) next to the I_BIAS diode R; P, L: tail and "
                "nA-divider feeds", fontsize=9)
    f = fig.add_subplot(gs[4, :])
    zoom(f, ["nlo_a"], width=2400, ytop=1.6, ybot=1.0)
    names = {f"xr.M5{ch}": "T" for ch in "abcdef"}
    names["xb.MBL3"] = "U"
    label_fingers(f, "nlo_a", names, P["strips"]["nlo_a"]["y1"] + 0.1, size=7)
    f.set_title("(f) nA divider: diode units U (hv 0.3/2 µm) and the six-unit series tail T of the regulation "
                "integrator", fontsize=9)
    f.set_xlabel("x (µm)")
    fig.savefig(OUT / "fig_layout_v2_matching.png")
    plt.close(fig)
    print("wrote", OUT / "fig_layout_v2_matching.png")


if __name__ == "__main__":
    if V2:
        fig_full_v2()
        fig_matching_v2()
    else:
        fig_full()
        fig_matching()
