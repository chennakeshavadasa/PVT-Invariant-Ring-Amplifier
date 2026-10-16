#!/usr/bin/env python3
"""Multi-panel figures for the README: panels of one row get the same height, rows get the
same width, and every panel gets a centred "(a)", "(b)", ... label underneath.

Output: docs/figures/composites/.  Run after export_schematics.sh.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FIG = Path(__file__).resolve().parent / "figures"
OUT = FIG / "composites"
OUT.mkdir(parents=True, exist_ok=True)
FONT = "/usr/share/fonts/stix-fonts/STIXTwoText-Regular.otf"
W = 2400            # composite width in pixels
GAP = 60            # space between panels
LABEL_H = 70        # height reserved for the panel label


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def scaled_row(paths, width):
    """Scale the images of a row to a common height so that the row is `width` wide."""
    ims = [Image.open(p).convert("RGB") for p in paths]
    aspect = sum(im.width / im.height for im in ims)
    h = int((width - GAP * (len(ims) - 1)) / aspect)
    return [im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS) for im in ims], h


def compose(name, rows, row_widths=None, labels=None):
    """rows: list of lists of image paths; row_widths: fraction of W per row;
    labels: optional list of label strings (default "(a)", "(b)", ...)."""
    row_widths = row_widths or [1.0] * len(rows)
    built, letter = [], ord("a")
    for paths, frac in zip(rows, row_widths):
        ims, h = scaled_row(paths, int(W * frac))
        labs = []
        for _ in ims:
            labs.append(labels.pop(0) if labels else f"({chr(letter)})")
            letter += 1
        built.append((ims, h, labs))
    total_h = sum(h + LABEL_H for _, h, _ in built) + GAP * (len(built) - 1)
    canvas = Image.new("RGB", (W, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    f = font(46)
    y = 0
    for ims, h, labels in built:
        row_w = sum(im.width for im in ims) + GAP * (len(ims) - 1)
        x = (W - row_w) // 2
        for im, lab in zip(ims, labels):
            canvas.paste(im, (x, y))
            tw = draw.textlength(lab, font=f)
            draw.text((x + (im.width - tw) / 2, y + h + 10), lab, fill="#2b2b2b", font=f)
            x += im.width + GAP
        y += h + LABEL_H + GAP
    canvas.save(OUT / name, optimize=True)
    print("wrote", OUT / name, canvas.size)


def compose_left_tall(name, left, right_top, right_bottom):
    """One tall panel on the left, two stacked panels on the right, same total height."""
    L = Image.open(left).convert("RGB")
    R1 = Image.open(right_top).convert("RGB")
    R2 = Image.open(right_bottom).convert("RGB")
    # widths: wl + wr + GAP = W, with H = wl / aL and H = (wr / a1) + (wr / a2) + GAP + LABEL_H
    a_l, a_1, a_2 = L.width / L.height, R1.width / R1.height, R2.width / R2.height
    best = None
    for wl in range(400, W - 400, 4):
        wr = W - GAP - wl
        h_left = wl / a_l
        h_right = wr / a_1 + wr / a_2 + GAP + LABEL_H
        if best is None or abs(h_left - h_right) < best[0]:
            best = (abs(h_left - h_right), wl, wr)
    _, wl, wr = best
    L = L.resize((wl, int(wl / a_l)), Image.LANCZOS)
    R1 = R1.resize((wr, int(wr / a_1)), Image.LANCZOS)
    R2 = R2.resize((wr, int(wr / a_2)), Image.LANCZOS)
    H = max(L.height, R1.height + R2.height + GAP + LABEL_H)
    canvas = Image.new("RGB", (W, H + LABEL_H), "white")
    draw = ImageDraw.Draw(canvas)
    f = font(46)
    canvas.paste(L, (0, 0))
    canvas.paste(R1, (wl + GAP, 0))
    canvas.paste(R2, (wl + GAP, R1.height + LABEL_H + GAP))
    for lab, (x, w, y) in zip(("(a)", "(b)", "(c)"),
                              ((0, wl, L.height), (wl + GAP, wr, R1.height),
                               (wl + GAP, wr, R1.height + LABEL_H + GAP + R2.height))):
        tw = draw.textlength(lab, font=f)
        draw.text((x + (w - tw) / 2, y + 10), lab, fill="#2b2b2b", font=f)
    canvas.save(OUT / name, optimize=True)
    print("wrote", OUT / name, canvas.size)


def crop_frac(src, dst, x0, x1):
    """Keep the horizontal fraction [x0, x1] of an image (used for the hero figure)."""
    im = Image.open(src).convert("RGB")
    im.crop((int(im.width * x0), 0, int(im.width * x1), im.height)).save(dst)
    return dst


T = FIG / "thesis"
S = FIG / "schematics"
compose("fig_deadzone_operation.png",
        [[T / "fig2_9_ringamp_schematic.png", T / "fig2_10_ringamp_iv.png", T / "fig2_11_vv_transfer.png"]])
compose("fig_deadzone_structures.png",
        [[T / "fig3_1_traditional_ringamp.png", T / "fig3_2_resistor_deadzone.png",
          T / "fig3_3_current_starved_deadzone.png"]])
compose_left_tall("fig_regulation_thesis.png", T / "fig3_6_deadzone_regulation.png",
                  T / "fig3_5_transient_fixed_bias.png", T / "fig3_7_transient_regulated.png")
compose("fig_sch_stages.png", [[S / "sch_stg1.png", S / "sch_stg1_cm.png"], [S / "sch_stg2.png"]], [1.0, 0.62])
compose("fig_sch_regulation.png", [[S / "sch_stg2_replica.png"], [S / "sch_pota.png", S / "sch_nota.png"]],
        [1.0, 0.8])

# hero figure: quiescent current with fixed bias and with regulation, next to the layout
tmp = OUT / "_iq_ab.png"
crop_frac(FIG / "results" / "fig_iq_temperature.png", tmp, 0.0, 0.655)
compose("fig_hero.png", [[tmp, FIG / "layout" / "fig_layout_plain.png"]],
        labels=["output-stage quiescent current: fixed deadzone vs. deadzone regulation",
                "layout (109 × 183 µm)"])
tmp.unlink()
