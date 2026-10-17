#!/usr/bin/env python3
"""IEEE-style result figures from sim/results (run sim/ramp_pvt.py first).

Writes PNGs (and one GIF) to docs/figures/results/.  Colours: regulated bias
blue, fixed bias orange, references in grey/black; every series also has its
own line style or marker so the figures read in greyscale.
"""
import csv
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import animation  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
RES = REPO / "sim" / "results"
OUT = REPO / "docs" / "figures" / "results"
OUT.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
    "mathtext.fontset": "stix", "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9,
    "legend.fontsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
    "xtick.minor.visible": False, "axes.linewidth": 0.6, "lines.linewidth": 1.2,
    "grid.linewidth": 0.4, "grid.color": "#d4d4d4", "axes.grid": True, "legend.frameon": True,
    "legend.framealpha": 1.0, "legend.edgecolor": "#bdbdbd", "legend.fancybox": False,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})
COL1, COL2 = 3.5, 7.16
BLUE, ORANGE, INK, GREY = "#2a78d6", "#eb6834", "#2b2b2b", "#8c8c8c"
CORNERS = ["TT", "SS", "FF", "SF", "FS"]
CSTYLE = {"TT": (INK, "-", "o"), "SS": (BLUE, "-", "s"), "SF": (BLUE, "--", "^"),
          "FF": (ORANGE, "-", "D"), "FS": (ORANGE, "--", "v")}
BIAS = {"fix": (ORANGE, "o", "fixed bias (TT-tuned)"), "reg": (BLUE, "s", "deadzone regulation"),
        "ptat": (GREY, "^", "regulation + PTAT $I_{BIAS}$")}


def read(path):
    with open(path) as fh:
        names = fh.readline().split()
    data = np.loadtxt(path, skiprows=1, ndmin=2)
    return {n: data[:, i] for i, n in enumerate(names)}


def rows():
    out = []
    for r in csv.DictReader(open(RES / "pvt_summary.csv")):
        for k, v in r.items():
            try:
                r[k] = float(v)
            except ValueError:
                pass
        out.append(r)
    return out


ROWS = rows()


def pick(design="RAMP_LR", **kw):
    return [r for r in ROWS if r["design"] == design and all(r[k] == v for k, v in kw.items())]


def panel(ax, s):
    ax.text(0.015, 0.97, s, transform=ax.transAxes, va="top", ha="left",
            bbox=dict(fc="white", ec="none", pad=1.0))


def save(fig, name):
    fig.savefig(OUT / name)
    plt.close(fig)
    print("wrote", OUT / name)


# ----------------------------------------------------------------------------
def loop_tf(path):
    d = read(path)
    t = d["mbr"] + 1j * d["mbi"]
    ph = np.degrees(np.unwrap(np.angle(t)))
    ph -= 360 * np.round(ph[0] / 360)
    return d["frequency"], 20 * np.log10(np.abs(t)), ph


def fig_loopgain():
    fig, (a, b) = plt.subplots(1, 2, figsize=(COL2, 2.5))
    for path, lab, col, ls in ((RES / "loop_orig_tt_27.dat", "original (ideal bias sources)", GREY, "--"),
                               (RES / "loop_reg_tt_27.dat", "layout-ready RAMP_LR", BLUE, "-")):
        f, mag, ph = loop_tf(path)
        a.semilogx(f, mag, ls, color=col, label=lab)
        b.semilogx(f, ph, ls, color=col, label=lab)
    for r, col in ((pick("RAMP", corner="TT", temp_c=27)[0], GREY), (pick(bias="reg", corner="TT", temp_c=27, vdd=1.65)[0], BLUE)):
        a.plot(r["ugf_hz"], 0, "o", ms=5, mfc="white", mec=col, mew=1.2)
        b.plot(r["ugf_hz"], r["pm_deg"] - 180, "o", ms=5, mfc="white", mec=col, mew=1.2)
    r0, r1 = pick("RAMP", corner="TT", temp_c=27)[0], pick(bias="reg", corner="TT", temp_c=27, vdd=1.65)[0]
    a.text(0.97, 0.95, f"$A_0$ = {r0['a0_db']:.1f} / {r1['a0_db']:.1f} dB\n"
                       f"UGF = {r0['ugf_hz'] / 1e6:.1f} / {r1['ugf_hz'] / 1e6:.1f} MHz",
           transform=a.transAxes, ha="right", va="top")
    b.text(0.03, 0.05, f"PM = {r0['pm_deg']:.1f}$^\\circ$ / {r1['pm_deg']:.1f}$^\\circ$",
           transform=b.transAxes, ha="left", va="bottom")
    a.set(xlabel="Frequency (Hz)", ylabel="Loop gain $|T|$ (dB)", xlim=(1, 1e10), ylim=(-100, 100))
    b.set(xlabel="Frequency (Hz)", ylabel="Phase of $T$ (deg)", xlim=(1, 1e10), ylim=(-360, 10))
    b.set_yticks([-360, -270, -180, -90, 0])
    a.legend(loc="lower left")
    panel(a, "(a)")
    panel(b, "(b)")
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_loopgain.png")


def fig_iq_temperature():
    fig, axs = plt.subplots(1, 3, figsize=(COL2, 2.55))
    for ax, bias, title in ((axs[0], "fix", "fixed bias"), (axs[1], "reg", "deadzone regulation")):
        for c in CORNERS:
            d = read(RES / f"tsweep_{bias}_{c.lower()}.dat")
            col, ls, mk = CSTYLE[c]
            ax.semilogy(d["temp-sweep"], 1e6 * d["i(v.x1.viq)"], ls, color=col, marker=mk, ms=3.5,
                        markevery=6, mfc="white", label=c)
        ax.set(xlabel="Temperature (°C)", ylabel="$I_Q$ of output stage (µA)", ylim=(0.01, 60), xlim=(-40, 125))
        ax.set_xticks([-40, 0, 40, 80, 125])
        ax.set_title(title)
    ax = axs[2]
    for c in CORNERS:
        d = read(RES / f"tsweep_reg_{c.lower()}.dat")
        col, ls, mk = CSTYLE[c]
        ax.plot(d["temp-sweep"], d["v(x1.vctrlp)"], ls, color=col, marker=mk, ms=3.5, markevery=6, mfc="white")
        ax.plot(d["temp-sweep"], d["v(x1.vctrln)"], ls, color=col, marker=mk, ms=3.5, markevery=6, mfc=col)
    ax.set(xlabel="Temperature (°C)", ylabel="Control voltage (V)", xlim=(-40, 125))
    ax.set_xticks([-40, 0, 40, 80, 125])
    ax.set_title("regulated $V_{CTRLP}$ (open), $V_{CTRLN}$ (filled)")
    axs[0].legend(loc="lower right", ncol=2, columnspacing=0.8, handlelength=1.8)
    for ax, s in zip(axs, "abc"):
        panel(ax, f"({s})")
    fig.tight_layout(w_pad=1.0)
    save(fig, "fig_iq_temperature.png")


def pvt_axis(ax, groups=True):
    """x axis: 5 corners x 3 temperatures; temperature under each tick, corner per group."""
    xs, labels = [], []
    for i, c in enumerate(CORNERS):
        for j, t in enumerate((-40, 27, 125)):
            xs.append(i * 4 + j)
            labels.append(f"{t}".replace("-", "\u2212"))
        if i:
            ax.axvline(i * 4 - 1, color="#bdbdbd", lw=0.6)
        if groups:
            ax.text(i * 4 + 1, -0.14, c, transform=ax.get_xaxis_transform(), ha="center", va="top")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.8, 18.8)
    ax.grid(axis="x", visible=False)
    return xs


def fig_pvt_ugf_pm():
    fig, (a, b) = plt.subplots(2, 1, figsize=(COL2, 4.1), sharex=True)
    for ax, key, scale in ((a, "ugf_hz", 1e-6), (b, "pm_deg", 1.0)):
        xs = pvt_axis(ax, groups=ax is b)
        for k, (bias, off) in enumerate((("fix", -0.22), ("reg", 0.0), ("ptat", 0.22))):
            col, mk, lab = BIAS[bias]
            for x, (c, t) in zip(xs, [(c, t) for c in CORNERS for t in (-40, 27, 125)]):
                pts = pick(bias=bias, corner=c, temp_c=t)
                vals = [p[key] * scale for p in pts]
                nom = [p[key] * scale for p in pts if p["vdd"] == 1.65][0]
                if len(vals) > 1:
                    ax.plot([x + off] * 2, [min(vals), max(vals)], "-", color=col, lw=1.0)
                ax.plot(x + off, nom, mk, color=col, ms=5, mfc="white" if bias == "ptat" else col,
                        mec=col, label=lab if (c, t) == ("TT", -40) else None)
    a.set_yscale("log")
    a.set(ylabel="Unity-gain freq. (MHz)", ylim=(0.1, 80))
    b.set(ylabel="Phase margin (deg)", ylim=(30, 95))
    b.set_xlabel("Temperature (°C) and process corner; bars: $V_{DD}$ = 1.65 V ± 5 %", labelpad=16)
    a.legend(loc="lower center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    panel(a, "(a)")
    panel(b, "(b)")
    fig.tight_layout(h_pad=0.6)
    save(fig, "fig_pvt_ugf_pm.png")


def fig_settling_pvt():
    fig, axs = plt.subplots(2, 1, figsize=(COL2, 4.1), sharex=True)
    for ax, tag, title in ((axs[0], "Lr", "200 mV step (large signal)"), (axs[1], "Sr", "4 mV step (small signal)")):
        xs = pvt_axis(ax, groups=ax is axs[1])
        for bias, off in (("fix", -0.18), ("reg", 0.18)):
            col, mk, lab = BIAS[bias]
            ys = [pick(bias=bias, corner=c, temp_c=t, vdd=1.65)[0][f"sc_err250_{tag}_pct"]
                  for c in CORNERS for t in (-40, 27, 125)]
            ax.semilogy(np.array(xs) + off, ys, mk, color=col, ms=5, label=lab, ls="none")
        ax.axhline(0.1, color=INK, lw=0.8, ls=":")
        ax.text(-0.5, 0.115, "0.1 %", ha="left", va="bottom")
        ax.text(0.985, 0.95, title, transform=ax.transAxes, ha="right", va="top",
                bbox=dict(fc="white", ec="none", pad=1.0))
        ax.set(ylabel="Error at 250 ns (%)", ylim=(3e-3, 80))
    axs[0].legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, 1.0))
    for ax, s in zip(axs, "ab"):
        panel(ax, f"({s})")
    axs[1].set_xlabel("Temperature (°C) and process corner, $V_{DD}$ = 1.65 V", labelpad=16)
    fig.tight_layout(h_pad=0.6)
    save(fig, "fig_settling_pvt.png")


def sc_edge(path, k):
    """Normalised response to SC edge k: 0 before, 1 = ideal final value."""
    from ramp_pvt import SC_EDGES, CS, CF  # noqa: E402
    d = read(path)
    t, v = d["time"], d["v(out)"]
    t0, dv, win = SC_EDGES[k]
    v0 = np.interp(t0 - 1e-9, t, v)
    m = (t >= t0 - 50e-9) & (t <= t0 + win)
    return (t[m] - t0) * 1e9, (v[m] - v0) / (-CS / CF * dv)


def fig_small_step():
    import sys
    sys.path.insert(0, str(REPO / "sim"))
    fig, (a, b) = plt.subplots(1, 2, figsize=(COL2, 2.5))
    for path, lab, col, ls in ((RES / "sc_fix_ss_-40.dat", "fixed bias, SS, −40 °C", ORANGE, "-"),
                               (RES / "sc_reg_ss_-40.dat", "regulated, SS, −40 °C", BLUE, "-"),
                               (RES / "sc_reg_tt_27.dat", "regulated, TT, 27 °C", INK, "--")):
        for ax, k in ((a, 2), (b, 0)):
            t, y = sc_edge(path, k)
            ax.plot(t, y, ls, color=col, label=lab)
    a.set(xlabel="Time after the step (ns)", ylabel="Normalised output", xlim=(-50, 1000), ylim=(-0.05, 1.25))
    b.set(xlabel="Time after the step (ns)", ylabel="Normalised output", xlim=(-50, 2000), ylim=(-0.05, 1.25))
    a.set_title("200 mV input step")
    b.set_title("4 mV input step")
    b.legend(loc="lower right")
    panel(a, "(a)")
    panel(b, "(b)")
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_sc_steps.png")


# ----------------------------------------------------------------------------
def three_phase_data():
    d = read(RES / "tran_reg_tt_27.dat")
    t, v = d["time"], d["v(out)"]
    m = (t >= 95e-9) & (t <= 260e-9)
    t, v, vin = t[m], v[m], d["v(vicm)"][m]
    vgp, vgn = d["v(x1.mp_dz)"][m], d["v(x1.mn_dz)"][m]
    iout = 50e-12 * np.gradient(v, t) * 1e3      # mA, C_L dV/dt
    iq = float(pick(bias="reg", corner="TT", temp_c=27, vdd=1.65)[0]["iq_ua"]) * 1e-3
    t_ns = (t - 100e-9) * 1e9
    # phases from the waveforms: RC while a stage-3 gate is near a rail,
    # large-signal while |I_out| >> I_Q, small-signal afterwards
    rail = (vgp < 0.25) | (vgn > 1.40)
    t1 = t_ns[np.where(rail)[0][-1]] if rail.any() else 0.0
    big = np.abs(iout) > 20 * iq
    t2 = t_ns[np.where(big)[0][-1]] if big.any() else t1
    return t_ns, v, vin, vgp, vgn, iout, t1, max(t2, t1)


def fig_three_phase():
    t, v, vin, vgp, vgn, iout, t1, t2 = three_phase_data()
    fig, axs = plt.subplots(3, 1, figsize=(COL1, 4.2), sharex=True)
    axs[0].plot(t, vin, ":", color=GREY, label="$V_{in}$")
    axs[0].plot(t, v, "-", color=BLUE, label="$V_{out}$")
    axs[0].set_ylabel("Voltage (V)")
    axs[0].legend(loc="center right")
    axs[1].plot(t, vgp, "-", color=INK, label="$V_{GP}$ (MP3 gate)")
    axs[1].plot(t, vgn, "--", color=ORANGE, label="$V_{GN}$ (MN3 gate)")
    axs[1].set(ylabel="Voltage (V)", ylim=(-0.1, 1.75))
    axs[1].legend(loc="lower right")
    axs[2].plot(t, iout, "-", color=BLUE)
    axs[2].set(ylabel="$I_{out}=C_L\\,dV_{out}/dt$ (mA)", xlabel="Time after the input step (ns)")
    for ax in axs:
        ax.axvspan(0, t1, color="#e8e8e8", lw=0)
        ax.axvspan(t1, t2, color="#f4f4f4", lw=0)
        ax.set_xlim(-5, 120)
    for x, s in ((t1 / 2, "RC"), ((t1 + t2) / 2, "LS"), ((t2 + 120) / 2, "small signal")):
        axs[0].text(x, 1.02, s, ha="center", va="bottom", transform=axs[0].get_xaxis_transform())
    for ax, s, y in zip(axs, "abc", (0.06, 0.94, 0.06)):
        ax.text(0.985, y, f"({s})", transform=ax.transAxes, ha="right", va="bottom" if y < 0.5 else "top")
    fig.tight_layout(h_pad=0.4)
    save(fig, "fig_three_phase.png")
    return t, v, vin, vgp, vgn, iout, t1, t2


def gif_three_phase():
    t, v, vin, vgp, vgn, iout, t1, t2 = three_phase_data()
    fig, axs = plt.subplots(3, 1, figsize=(4.6, 4.6), sharex=True, dpi=110)
    axs[0].plot(t, vin, ":", color=GREY)
    axs[0].plot(t, v, "-", color=BLUE)
    axs[1].plot(t, vgp, "-", color=INK)
    axs[1].plot(t, vgn, "--", color=ORANGE)
    axs[2].plot(t, iout, "-", color=BLUE)
    axs[0].set_ylabel("$V_{in}$, $V_{out}$ (V)")
    axs[1].set_ylabel("$V_{GP}$, $V_{GN}$ (V)")
    axs[2].set_ylabel("$I_{out}$ (mA)")
    axs[2].set_xlabel("Time after the input step (ns)")
    for ax in axs:
        ax.set_xlim(-5, 120)
    cur = [ax.axvline(0, color=INK, lw=0.8) for ax in axs]
    label = axs[0].text(0.98, 0.08, "", transform=axs[0].transAxes, ha="right", va="bottom",
                        bbox=dict(fc="white", ec="#bdbdbd", pad=2))
    fig.suptitle("Ring amplifier step response: three settling phases (TT, 27 °C)", fontsize=9)
    fig.tight_layout()
    frames = np.linspace(-5, 120, 90)

    def upd(x):
        for c in cur:
            c.set_xdata([x, x])
        phase = "RC settling: MP3 fully on" if 0 <= x < t1 else \
            "large-signal settling" if t1 <= x < t2 else \
            "small-signal settling at $I_Q$" if x >= t2 else "before the step: $I_Q$ only"
        label.set_text(phase)
        return cur + [label]

    ani = animation.FuncAnimation(fig, upd, frames=frames, blit=False)
    ani.save(OUT / "three_phase.gif", writer=animation.PillowWriter(fps=12))
    plt.close(fig)
    print("wrote", OUT / "three_phase.gif")


def fig_power():
    d = read(RES / "power_tt_27.dat")
    ua = lambda k: 1e6 * float(d[k][0])
    blocks = [("Output stage ($I_Q$)", ua("i(v.x1.viq)")),
              ("Stage 1 + CMFB", ua("i(v.x1.v_x1)")),
              ("Stage 2 (deadzone)", ua("i(v.x1.v_x2)")),
              ("Trip-point replica", ua("i(v.x1.v_x4)")),
              ("Deadzone regulation", ua("i(v.x1.v_x3)")),
              ("Bias mirrors + $I_{BIAS}$", ua("i(v.x1.v_xb)") + 1.0)]
    total = -1e6 * float(d["i(v2)"][0])
    # one distinct hue per block, in an order that passes the colour-vision checks for
    # neighbouring wedges (including last-to-first)
    hues = [BLUE, ORANGE, "#1baf7a", "#eda100", "#6250d6", "#e87ba4"]
    fig, ax = plt.subplots(figsize=(COL1, 2.5))
    wedges, _ = ax.pie([b[1] for b in blocks], colors=hues, startangle=90, counterclock=False,
                       wedgeprops=dict(width=0.36, edgecolor="white", linewidth=1.5))
    ax.text(0, 0.08, f"{total:.0f} µA", ha="center", va="center", fontsize=11)
    ax.text(0, -0.16, f"{total * 1.65:.0f} µW", ha="center", va="center")
    ax.set_aspect("equal")
    ax.legend(wedges, [f"{n}: {v:.1f} µA ({100 * v / total:.0f} %)" for n, v in blocks],
              loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False, handlelength=1.0)
    ax.grid(False)
    save(fig, "fig_power.png")


def fig_psrr():
    fig, ax = plt.subplots(figsize=(COL1, 2.3))
    for c in CORNERS:
        d = read(RES / f"psrr_reg_{c.lower()}_27.dat")
        a = np.abs(d["psrr_re"] + 1j * d["psrr_im"])
        col, ls, mk = CSTYLE[c]
        ax.semilogx(d["frequency"], -20 * np.log10(a), ls, color=col, marker=mk, ms=3.5, markevery=40,
                    mfc="white", label=c)
    ax.set(xlabel="Frequency (Hz)", ylabel="PSRR (dB)", xlim=(1, 1e10), ylim=(0, 110))
    ax.legend(loc="lower left", ncol=3, columnspacing=0.8)
    save(fig, "fig_psrr.png")


# ----------------------------------------------------------------------------
# cross-corner waveforms: 5 process corners overlaid, one panel per temperature
TEMPS = (-40, 27, 125)
BIAS_ROW = {"fix": "Fixed bias (TT-tuned)", "reg": "Deadzone regulation"}


def corner_legend(fig, y=1.0, extra=()):
    h = [mpl.lines.Line2D([], [], color=CSTYLE[c][0], ls=CSTYLE[c][1], marker=CSTYLE[c][2], ms=4,
                          mfc="white") for c in CORNERS]
    labels = [f"{c} corner" for c in CORNERS]
    for lab, kw in extra:
        h.append(mpl.lines.Line2D([], [], **kw))
        labels.append(lab)
    fig.legend(h, labels, loc="lower center", ncol=len(h), bbox_to_anchor=(0.5, y),
               columnspacing=1.0 if extra else 1.4, handlelength=2.0 if extra else 2.4)


def row_label(fig, axs, text):
    """Bias label to the left of a group of rows."""
    fig.canvas.draw()
    top, bot = axs[0].get_position().y1, axs[-1].get_position().y0
    fig.text(0.004, (top + bot) / 2, text, rotation=90, ha="left", va="center", fontweight="bold")


def fig_bode_corners():
    fig, axs = plt.subplots(4, 3, figsize=(COL2, 6.7), sharex=True)
    for r, bias in enumerate(("fix", "reg")):
        am, ap = axs[2 * r], axs[2 * r + 1]
        for j, t in enumerate(TEMPS):
            for c in CORNERS:
                col, ls, mk = CSTYLE[c]
                f, mag, ph = loop_tf(RES / f"loop_{bias}_{c.lower()}_{t}.dat")
                am[j].semilogx(f, mag, ls, color=col)
                ap[j].semilogx(f, ph, ls, color=col)
                p = pick(bias=bias, corner=c, temp_c=t, vdd=1.65)[0]
                am[j].plot(p["ugf_hz"], 0, mk, ms=4.5, mfc="white", mec=col, mew=1.0)
                ap[j].plot(p["ugf_hz"], p["pm_deg"] - 180, mk, ms=4.5, mfc="white", mec=col, mew=1.0)
            pts = pick(bias=bias, temp_c=t, vdd=1.65)
            u = [q["ugf_hz"] / 1e6 for q in pts]
            m = [q["pm_deg"] for q in pts]
            am[j].text(0.97, 0.95, f"UGF {min(u):.2g}–{max(u):.2g} MHz", transform=am[j].transAxes,
                       ha="right", va="top")
            ap[j].text(0.03, 0.05, f"PM {min(m):.0f}–{max(m):.0f}$^\\circ$", transform=ap[j].transAxes,
                       ha="left", va="bottom")
            am[j].set(ylim=(-40, 100))
            ap[j].set(ylim=(-360, 10))
            ap[j].set_yticks([-360, -270, -180, -90, 0])
            ap[j].axhline(-180, color=GREY, lw=0.6, ls=":")
            am[j].axhline(0, color=GREY, lw=0.6, ls=":")
            if j:
                am[j].set_yticklabels([])
                ap[j].set_yticklabels([])
        am[0].set_ylabel("$|T|$ (dB)")
        ap[0].set_ylabel("$\\angle T$ (deg)")
    for j, t in enumerate(TEMPS):
        axs[0, j].set_title(f"{t} °C".replace("-", "\u2212"))
        axs[-1, j].set(xlabel="Frequency (Hz)", xlim=(10, 1e9))
        axs[-1, j].set_xticks([1e1, 1e3, 1e5, 1e7, 1e9])
    for k, ax in enumerate(axs.flat):
        ax.text(0.03, 0.05 if k // 3 % 2 == 0 else 0.30, f"({'abcdefghijkl'[k]})", transform=ax.transAxes,
                ha="left", va="bottom" if k // 3 % 2 == 0 else "top")
    fig.tight_layout(h_pad=0.3, w_pad=0.4, rect=(0.025, 0, 1, 0.965))
    corner_legend(fig, 0.965)
    row_label(fig, axs[0:2, 0], BIAS_ROW["fix"])
    row_label(fig, axs[2:4, 0], BIAS_ROW["reg"])
    save(fig, "fig_bode_corners.png")


def fig_step_corners(k, name, xlim):
    """SC step response (edge k of SC_EDGES) for 5 corners x 3 temperatures, fixed vs regulated:
    normalised output and its settling error |1 - V_out/V_ideal| on a log scale."""
    tag = ("S" if k < 2 else "L") + "r"
    fig, axs = plt.subplots(4, 3, figsize=(COL2, 6.7), sharex=True)
    for r, bias in enumerate(("fix", "reg")):
        aw, ae = axs[2 * r], axs[2 * r + 1]
        for j, t in enumerate(TEMPS):
            for i, c in enumerate(CORNERS):
                col, ls, mk = CSTYLE[c]
                tt, y = sc_edge(RES / f"sc_{bias}_{c.lower()}_{t}.dat", k)
                every = max(1, len(tt) // 7)
                mark = dict(marker=mk, ms=3.5, mfc="white", markevery=((i + 1) * every // 6, every))
                aw[j].plot(tt, y, ls, color=col, **mark)
                ae[j].semilogy(tt[tt >= 0], 100 * np.abs(1 - y[tt >= 0]), ls, color=col, lw=1.0, **mark)
            err = max(pick(bias=bias, corner=c, temp_c=t, vdd=1.65)[0][f"sc_err250_{tag}_pct"] for c in CORNERS)
            aw[j].text(0.97, 0.05, f"worst error at 250 ns: {err:.2g} %", transform=aw[j].transAxes,
                       ha="right", va="bottom", bbox=dict(fc="white", ec="none", pad=1.0))
            aw[j].set(ylim=(-0.08, 1.25))
            ae[j].set(ylim=(1e-3, 300))
            ae[j].set_yticks([1e-3, 1e-2, 1e-1, 1, 10, 100])
            ae[j].axhline(0.1, color=INK, lw=0.8, ls=":")
            for ax in (aw[j], ae[j]):
                ax.axvline(250, color=GREY, lw=0.6, ls="--")
            if j:
                aw[j].set_yticklabels([])
                ae[j].set_yticklabels([])
        aw[0].set_ylabel("Normalised $V_{out}$")
        ae[0].set_ylabel("Settling error (%)")
    for j, t in enumerate(TEMPS):
        axs[0, j].set_title(f"{t} °C".replace("-", "\u2212"))
        axs[-1, j].set(xlabel="Time after the step (ns)", xlim=xlim)
    for n, ax in enumerate(axs.flat):
        ax.text(0.03, 0.95, f"({'abcdefghijkl'[n]})", transform=ax.transAxes, ha="left", va="top",
                bbox=dict(fc="white", ec="none", pad=1.0))
    fig.tight_layout(h_pad=0.3, w_pad=0.4, rect=(0.025, 0, 1, 0.965))
    corner_legend(fig, 0.965, extra=(("0.1 % error", dict(color=INK, lw=0.8, ls=":")),
                                     ("250 ns", dict(color=GREY, lw=0.6, ls="--"))))
    row_label(fig, axs[0:2, 0], BIAS_ROW["fix"])
    row_label(fig, axs[2:4, 0], BIAS_ROW["reg"])
    save(fig, name)

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(REPO / "sim"))
    fig_loopgain()
    fig_iq_temperature()
    fig_pvt_ugf_pm()
    fig_settling_pvt()
    fig_small_step()
    fig_three_phase()
    gif_three_phase()
    fig_power()
    fig_psrr()
    fig_bode_corners()
    fig_step_corners(2, "fig_step_corners_large.png", (-50, 600))
    fig_step_corners(0, "fig_step_corners_small.png", (-50, 2000))
