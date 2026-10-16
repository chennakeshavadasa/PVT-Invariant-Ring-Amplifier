#!/usr/bin/env python3
"""Annotated layout figures from layout/RAMP_LR.gds and RAMP_LR_placement.json.

Renders views with KLayout (layout/render.py) and labels the matched arrays
with the role of every unit.  Output: docs/figures/layout/.
Run after gen_layout.py:  python3 layout/make_layout_figures.py
"""
import json
import subprocess
import tempfile
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT = REPO / "docs" / "figures" / "layout"
OUT.mkdir(parents=True, exist_ok=True)
GDS = HERE / "RAMP_LR.gds"
P = json.load(open(HERE / "RAMP_LR_placement.json"))
UPPER = "10/0,19/0,29/0,30/0,30/25,49/0,50/0,66/0,67/0,126/0,129/0,36/0,125/0"

mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
    "mathtext.fontset": "stix", "font.size": 9, "savefig.dpi": 300, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})
INK, BLUE, ORANGE = "#2b2b2b", "#2a78d6", "#eb6834"


def render(box, width, hide=None):
    tmp = Path(tempfile.mkdtemp()) / "v.png"
    cmd = ["klayout", "-b", "-r", str(HERE / "render.py"), "-rd", f"gds={GDS}", "-rd", f"png={tmp}",
           "-rd", "box=" + ",".join(f"{v:.3f}" for v in box), "-rd", f"w={width}"]
    if hide:
        cmd += ["-rd", f"hide={hide}"]
    subprocess.run(cmd, check=True, capture_output=True)
    return mpimg.imread(tmp)


ROLE = {"rows": {
    "bias_n0": "", "bias_n1": "", "bias_n2": "IBIAS mirror (6 x 5 common centroid)", "bias_n3": "",
    "bias_n4": "", "bias_n5": "", "bias_p0": "PMOS bias mirror (2 x 3)", "bias_p1": "", "pota_ld": "POTA load mirror", "nota_in": "NOTA input pair",
    "out_n": "output NMOS + replica (MN3, MN_R)", "pota_in": "POTA input pair",
    "nota_ld": "NOTA load mirror", "in_pairs": "stage-1 & CMFB input pairs",
    "cm_res": "CM-sense rhigh (R1/R3)", "s1_loads": "stage-1 loads + CMFB diodes",
    "min_n": "stage-2 / replica NMOS", "min_p": "stage-2 / replica PMOS",
    "out_p": "output PMOS + replica (MP3, MP_R)"}}


LEFT = {r for band in P["bands"] for r in [band["left"]] if r}


def fig_full():
    x0, y0, x1, y1 = P["bbox"]
    img = render((x0 - 1, y0 - 1, x1 + 1, y1 + 1), 1500)
    w = 7.16
    fig = plt.figure(figsize=(w, w * 0.92))
    ax = fig.add_axes([0.25, 0.04, 0.50, 0.92])
    ax.imshow(img, extent=(x0 - 1, x1 + 1, y0 - 1, y1 + 1), interpolation="lanczos")
    ax.set_xlim(x0 - 1, x1 + 1)
    ax.set_ylim(y0 - 1, y1 + 1)
    ax.set_axis_off()
    for band in P["bands"]:
        for side in ("left", "right"):
            name = band[side]
            lab = ROLE["rows"].get(name, "") if name else ""
            if not lab:
                continue
            r = P["rows"][name]
            yc = (r["y0"] + r["y1"]) / 2
            if side == "left":
                ax.annotate(lab, xy=(r["units"][0]["x0"], yc), xytext=(-0.02, yc), textcoords=("axes fraction", "data"),
                            ha="right", va="center", arrowprops=dict(arrowstyle="-", color="#9a9a9a", lw=0.5))
            else:
                ax.annotate(lab, xy=(r["units"][-1]["x1"], yc), xytext=(1.02, yc), textcoords=("axes fraction", "data"),
                            ha="left", va="center", arrowprops=dict(arrowstyle="-", color="#9a9a9a", lw=0.5))
    for m in P["mims"]:
        name = {"x3.CDP": "2 pF MIM ($V_{CTRLP}$)", "x3.CDN": "2 pF MIM ($V_{CTRLN}$)"}[m["ref"]]
        ax.text((m["x0"] + m["x1"]) / 2, (m["y0"] + m["y1"]) / 2, name, ha="center", va="center",
                bbox=dict(fc="white", ec="#9a9a9a", lw=0.5, pad=1.5))
    sp = P["spine"]
    ax.text((sp["x0"] + sp["x1"]) / 2, y1 + 3, "Metal3 spine", ha="center", va="bottom")
    # scale bar
    ax.plot([x0 + 2, x0 + 22], [y0 - 4, y0 - 4], "-", color=INK, lw=2, clip_on=False)
    ax.text(x0 + 12, y0 - 5.5, "20 µm", ha="center", va="top")
    ax.text(x1, y0 - 5.5, f"{x1 - x0:.0f} µm × {y1 - y0:.0f} µm", ha="right", va="top")
    fig.savefig(OUT / "fig_layout_full.png")
    plt.close(fig)
    print("wrote", OUT / "fig_layout_full.png")


def label_units(ax, row, names, y, color=INK, size=9):
    for u in P["rows"][row]["units"]:
        s = names.get(u["ref"], "D" if u["ref"] == "D" else "?")
        ax.text((u["x0"] + u["x1"]) / 2, y, s, ha="center", va="bottom", fontsize=size,
                color=ORANGE if s == "D" else color, fontweight="bold",
                bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))


def zoom(ax, rows, pad=1.2, hide=UPPER, width=1600):
    xs = [u[k] for r in rows for u in P["rows"][r]["units"] for k in ("x0", "x1")]
    ys = [P["rows"][r]["y0"] for r in rows] + [P["rows"][r].get("tap", [0, P["rows"][r]["y1"]])[1] for r in rows]
    box = (min(xs) - pad, min(ys) - 1.6, max(xs) + pad, max(ys) + 2.2)
    ax.imshow(render(box, width, hide), extent=(box[0], box[2], box[1], box[3]), interpolation="lanczos")
    ax.set_xlim(box[0], box[2])
    ax.set_ylim(box[1], box[3])
    ax.tick_params(direction="in", top=True, right=True)
    return box


def fig_matching():
    fig = plt.figure(figsize=(7.16, 7.4))
    gs = fig.add_gridspec(4, 2, width_ratios=[0.95, 1.1], hspace=0.62, wspace=0.16)
    # (a) bias mirror 6 x 5 common centroid
    a = fig.add_subplot(gs[:, 0])
    rows = [f"bias_n{i}" for i in range(6)]
    zoom(a, rows, width=1100)
    bias = {"xb.MB0": "R", "xb.MB1": "T", "xb.MB2": "C", "xb.MB3": "N", "xb.MB4": "Q", "xb.MB5": "P"}
    for r in rows:
        label_units(a, r, bias, P["rows"][r]["y1"] + 0.15)
    a.set_title("(a) IBIAS mirror, 6 × 5 common centroid", fontsize=9)
    a.set_xlabel("x (µm)")
    a.set_ylabel("y (µm)")
    panels = [("in_pairs", {"x1.MN1": "A", "x1.MN2": "B", "x1.MC1": "C", "x1.MC2": "E", "x3.MCN": "K"},
               "(b) stage-1 pair A/B, CMFB pair C/E (ABBA)"),
              ("s1_loads", {"x1.MP1": "A", "x1.MP2": "B", "x1.MPC1": "C", "x1.MPC2": "E"},
               "(c) stage-1 loads A/B, CMFB diodes C/E"),
              ("out_n", {"M1": "M", "x3.MN_STG2_3N_R": "R"}, "(d) MN3 (M, ×4) around replica R"),
              ("out_p", {"M2": "M", "x3.MP_STG2_3P_R": "R"}, "(e) MP3 (M, ×4) around replica R")]
    for k, (row, names, title) in enumerate(panels):
        ax = fig.add_subplot(gs[k, 1])
        zoom(ax, [row])
        label_units(ax, row, names, P["rows"][row]["y1"] + 0.15)
        ax.set_title(title, fontsize=9)
        if k == 3:
            ax.set_xlabel("x (µm)")
    fig.savefig(OUT / "fig_layout_matching.png")
    plt.close(fig)
    print("wrote", OUT / "fig_layout_matching.png")


if __name__ == "__main__":
    fig_full()
    fig_matching()
