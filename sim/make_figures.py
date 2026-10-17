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


def top_legend(fig, handles, labels, ncol, y=1.0):
    """Legend above all axes (never on the data)."""
    fig.legend(handles, labels, loc="lower center", ncol=ncol, bbox_to_anchor=(0.5, y),
               columnspacing=1.2, handlelength=2.2)


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
    panel(a, "(a)")
    b.text(0.985, 0.97, "(b)", transform=b.transAxes, va="top", ha="right")
    fig.tight_layout(w_pad=1.5)
    top_legend(fig, *a.get_legend_handles_labels(), ncol=2)
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
    ax.set(xlabel="Temperature (°C)", ylabel="Control voltage (V)", xlim=(-40, 125), ylim=(0.72, 0.97))
    ax.set_xticks([-40, 0, 40, 80, 125])
    ax.set_title("regulated $V_{CTRLP}$ (open), $V_{CTRLN}$ (filled)")
    for ax, s in zip(axs, "abc"):
        panel(ax, f"({s})")
    fig.tight_layout(w_pad=1.0)
    top_legend(fig, *axs[0].get_legend_handles_labels(), ncol=5)
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
    panel(a, "(a)")
    panel(b, "(b)")
    fig.tight_layout(w_pad=1.5)
    top_legend(fig, *b.get_legend_handles_labels(), ncol=3)
    save(fig, "fig_sc_steps.png")


# ----------------------------------------------------------------------------
# phase colours (validated categorical slots): RC, large signal, small signal
PHASE_COL = ("#6250d6", "#eda100", "#1baf7a")
PHASE_TINT = ("#e4e1f8", "#fcefcf", "#d6f2e8")


def three_phase_data(bias="reg", corner="tt", temp=27):
    """Rising 200-mV step of the buffer and its three settling phases, from the waveforms:
    RC while a stage-3 gate is within 0.25 V of a rail (device fully on), large signal while
    |I_out| > 20 I_Q,TT (84 uA, about 15 % of the peak), small signal until 0.1 % settling."""
    d = read(RES / f"tran_{bias}_{corner}_{temp}.dat")
    t, v = d["time"], d["v(out)"]
    m = (t >= 95e-9) & (t <= 595e-9)
    t, v, vin = t[m], v[m], d["v(vicm)"][m]
    vgp, vgn = d["v(x1.mp_dz)"][m], d["v(x1.mn_dz)"][m]
    iout = 50e-12 * np.gradient(v, t) * 1e3      # mA, C_L dV/dt
    i_ls = 20 * float(pick(bias="reg", corner="TT", temp_c=27, vdd=1.65)[0]["iq_ua"]) * 1e-3
    t_ns = (t - 100e-9) * 1e9
    rail = ((vgp < 0.25) | (vgn > 1.40)) & (t_ns >= 0)
    t1 = t_ns[np.where(rail)[0][-1]] if rail.any() else 0.0
    big = (np.abs(iout) > i_ls) & (t_ns >= 0)
    t2 = max(t_ns[np.where(big)[0][-1]] if big.any() else t1, t1)
    ts = float(pick(bias=bias, corner=corner.upper(), temp_c=temp, vdd=1.65)[0]["ts01_rise_ns"])
    return t_ns, v, vin, vgp, vgn, iout, t1, t2, max(ts, t2)


def fig_three_phase():
    t, v, vin, vgp, vgn, iout, t1, t2, ts = three_phase_data()
    fig, axs = plt.subplots(3, 1, figsize=(COL1, 4.2), sharex=True)
    axs[0].plot(t, vin, ":", color=GREY, label="$V_{in}$")
    axs[0].plot(t, v, "-", color=BLUE, label="$V_{out}$")
    axs[0].set_ylabel("Voltage (V)")
    axs[1].plot(t, vgp, "-", color=INK, label="$V_{GP}$ (MP3 gate)")
    axs[1].plot(t, vgn, "--", color=ORANGE, label="$V_{GN}$ (MN3 gate)")
    axs[1].set(ylabel="Voltage (V)", ylim=(-0.1, 1.75))
    axs[2].plot(t, iout, "-", color=BLUE)
    axs[2].set(ylabel="$I_{out}=C_L\\,dV_{out}/dt$ (mA)", xlabel="Time after the input step (ns)")
    for ax in axs:
        ax.axvspan(0, t1, color=PHASE_TINT[0], lw=0)
        ax.axvspan(t1, t2, color=PHASE_TINT[1], lw=0)
        ax.axvspan(t2, ts, color=PHASE_TINT[2], lw=0)
        ax.set_xlim(-5, 120)
    for x, s in ((t1 / 2, "RC"), ((t1 + t2) / 2, "LS"), ((t2 + ts) / 2, "SS")):
        axs[0].text(x, 1.02, s, ha="center", va="bottom", transform=axs[0].get_xaxis_transform())
    for ax, s, y in zip(axs, "abc", (0.06, 0.94, 0.06)):
        ax.text(0.985, y, f"({s})", transform=ax.transAxes, ha="right", va="bottom" if y < 0.5 else "top")
    fig.tight_layout(h_pad=0.4)
    h0, l0 = axs[0].get_legend_handles_labels()
    h1, l1 = axs[1].get_legend_handles_labels()
    fig.legend(h0 + h1, l0 + l1, loc="upper center", ncol=2, bbox_to_anchor=(0.55, 0.0), handlelength=2.0)
    save(fig, "fig_three_phase.png")
    return t, v, vin, vgp, vgn, iout, t1, t2


def phase_panels(axs, bias, corner, temp, show_legend=False):
    """Three stacked panels (output, stage-3 gates, load current) with the phases shaded."""
    t, v, vin, vgp, vgn, iout, t1, t2, ts = three_phase_data(bias, corner, temp)
    col = BIAS[bias][0]
    axs[0].plot(t, vin, ":", color=GREY, label="$V_{in}$")
    axs[0].plot(t, v, "-", color=col, label="$V_{out}$")
    axs[1].plot(t, vgp, "-", color=INK, label="$V_{GP}$")
    axs[1].plot(t, vgn, "--", color=col, label="$V_{GN}$")
    axs[2].plot(t, iout, "-", color=col)
    for ax in axs:
        for (a, b), tint in zip(((0, t1), (t1, t2), (t2, ts)), PHASE_TINT):
            ax.axvspan(a, b, color=tint, lw=0)
    axs[0].set_ylim(0.70, 0.96)
    axs[1].set_ylim(-0.1, 1.75)
    axs[2].set_ylim(-0.42, 0.85)
    iq = pick(bias=bias, corner=corner.upper(), temp_c=temp, vdd=1.65)[0]["iq_ua"]
    axs[2].text(0.97, 0.93, f"$I_Q$ = {iq:.3g} µA\n0.1 % at {ts:.0f} ns", transform=axs[2].transAxes,
                ha="right", va="top", bbox=dict(fc="white", ec="none", pad=1.0))
    return t1, t2, ts


THREE_PT = (("ss", -40), ("tt", 27), ("ff", 125))


def fig_three_phase_corners():
    fig, axs = plt.subplots(6, 3, figsize=(COL2, 7.6), sharex=True)
    for r, bias in enumerate(("fix", "reg")):
        for j, (c, t) in enumerate(THREE_PT):
            phase_panels(axs[3 * r:3 * r + 3, j], bias, c, t, show_legend=(j == 0))
            if j:
                for ax in axs[3 * r:3 * r + 3, j]:
                    ax.set_yticklabels([])
        axs[3 * r, 0].set_ylabel("$V_{out}$ (V)")
        axs[3 * r + 1, 0].set_ylabel("Gates (V)")
        axs[3 * r + 2, 0].set_ylabel("$I_{out}$ (mA)")
    for j, (c, t) in enumerate(THREE_PT):
        axs[0, j].set_title(f"{c.upper()}, {t} °C".replace("-", "−"))
        axs[-1, j].set(xlabel="Time after the input step (ns)", xlim=(-5, 120))
    for n, ax in enumerate(axs.flat):
        ax.text(0.97, 0.06, f"({chr(97 + n)})", transform=ax.transAxes, ha="right", va="bottom")
    fig.tight_layout(h_pad=0.25, w_pad=0.4, rect=(0.025, 0, 1, 0.965))
    h = [mpl.patches.Patch(color=c) for c in PHASE_TINT]
    h += [mpl.lines.Line2D([], [], color=GREY, ls=":"), mpl.lines.Line2D([], [], color=INK, ls="-"),
          mpl.lines.Line2D([], [], color=GREY, ls="--")]
    fig.legend(h, ["RC phase (stage-3 device fully on)", "large-signal phase", "small-signal phase to 0.1 %",
                   "$V_{in}$", "$V_{GP}$ (MP3 gate)", "$V_{GN}$ (MN3 gate)"],
               loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.965), handlelength=1.6)
    row_label(fig, axs[0:3, 0], BIAS_ROW["fix"])
    row_label(fig, axs[3:6, 0], BIAS_ROW["reg"])
    save(fig, "fig_three_phase_corners.png")


def fig_phase_bars():
    """Duration of the three phases at every corner and temperature, fixed vs regulated."""
    pts = [(c, t) for c in CORNERS for t in (-40, 27, 125)]
    fig, axs = plt.subplots(1, 2, figsize=(COL2, 4.3), sharey=True)
    y = np.arange(len(pts))[::-1] + np.repeat(np.arange(len(CORNERS))[::-1] * 0.6, 3)
    for ax, bias, title in ((axs[0], "fix", "Fixed bias (TT-tuned)"), (axs[1], "reg", "Deadzone regulation")):
        for yy, (c, t) in zip(y, pts):
            _, *_, t1, t2, ts = three_phase_data(bias, c.lower(), t)
            left = 0.0
            for w, col in zip((t1, t2 - t1, ts - t2), PHASE_COL):
                ax.barh(yy, w, left=left, height=0.78, color=col, edgecolor="white", linewidth=1.0)
                left += w
            ax.text(ts + 4, yy, f"{ts:.0f}", va="center", ha="left")
        ax.set_title(title)
        ax.set(xlabel="Time after the input step (ns)", xlim=(0, 330))
        ax.grid(axis="y", visible=False)
    axs[0].set_yticks(y)
    axs[0].set_yticklabels([f"{c} {t:>4} °C".replace("-", "−") for c, t in pts])
    for ax, s in zip(axs, "ab"):
        ax.text(0.985, 0.985, f"({s})", transform=ax.transAxes, ha="right", va="top")
    h = [mpl.patches.Patch(color=c) for c in PHASE_COL]
    fig.legend(h, ["RC", "large signal", "small signal to 0.1 %"], loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, 0.97), handlelength=1.4)
    fig.tight_layout(w_pad=1.0, rect=(0, 0, 1, 0.97))
    save(fig, "fig_phase_bars.png")


# ----------------------------------------------------------------------------
# schematic versus post-layout (sim/postlayout.py)
def rows_csv(name):
    out = []
    for r in csv.DictReader(open(RES / name)):
        for k, v in r.items():
            try:
                r[k] = float(v)
            except ValueError:
                pass
        out.append(r)
    return out


VIEW = {"sch": (BLUE, "-", "o", "schematic"), "pex": (ORANGE, "--", "s", "post-layout (magic PEX, C only)")}


def view_file(kind, view, corner, temp):
    return RES / f"{kind}_{'reg' if view == 'sch' else 'pex'}_{corner}_{temp}.dat"


def fig_postlayout_bode():
    pl = rows_csv("postlayout_summary.csv")
    fig, axs = plt.subplots(2, 3, figsize=(COL2, 3.9), sharex=True)
    for j, (c, t) in enumerate(THREE_PT):
        txt = []
        for v in ("sch", "pex"):
            col, ls, mk, lab = VIEW[v]
            f, mag, ph = loop_tf(view_file("loop", v, c, t))
            axs[0, j].semilogx(f, mag, ls, color=col, label=lab)
            axs[1, j].semilogx(f, ph, ls, color=col)
            r = [q for q in pl if q["view"] == v and q["corner"] == c.upper() and q["temp_c"] == t][0]
            axs[0, j].plot(r["ugf_hz"], 0, mk, ms=4.5, mfc="white", mec=col, mew=1.0)
            axs[1, j].plot(r["ugf_hz"], r["pm_deg"] - 180, mk, ms=4.5, mfc="white", mec=col, mew=1.0)
            txt.append(r)
        axs[0, j].text(0.97, 0.95, f"UGF {txt[0]['ugf_hz'] / 1e6:.1f} $\\rightarrow$ {txt[1]['ugf_hz'] / 1e6:.1f} MHz",
                       transform=axs[0, j].transAxes, ha="right", va="top")
        axs[1, j].text(0.03, 0.05, f"PM {txt[0]['pm_deg']:.0f}° $\\rightarrow$ {txt[1]['pm_deg']:.0f}°",
                       transform=axs[1, j].transAxes, ha="left", va="bottom",
                       bbox=dict(fc="white", ec="none", pad=1.0))
        axs[0, j].set(ylim=(-40, 100), title=f"{c.upper()}, {t} °C".replace("-", "−"))
        axs[1, j].set(ylim=(-360, 10), xlabel="Frequency (Hz)", xlim=(10, 1e9))
        axs[1, j].set_yticks([-360, -270, -180, -90, 0])
        axs[1, j].set_xticks([1e1, 1e3, 1e5, 1e7, 1e9])
        axs[1, j].axhline(-180, color=GREY, lw=0.6, ls=":")
        axs[0, j].axhline(0, color=GREY, lw=0.6, ls=":")
        if j:
            axs[0, j].set_yticklabels([])
            axs[1, j].set_yticklabels([])
    axs[0, 0].set_ylabel("$|T|$ (dB)")
    axs[1, 0].set_ylabel("$\\angle T$ (deg)")
    for n, ax in enumerate(axs.flat):
        ax.text(0.03 if n < 3 else 0.97, 0.05 if n < 3 else 0.95, f"({chr(97 + n)})", transform=ax.transAxes,
                ha="left" if n < 3 else "right", va="bottom" if n < 3 else "top")
    fig.tight_layout(h_pad=0.3, w_pad=0.4, rect=(0, 0, 1, 0.94))
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.94))
    save(fig, "fig_postlayout_bode.png")


def fig_postlayout_steps():
    import ramp_pvt as rp
    fig, axs = plt.subplots(2, 3, figsize=(COL2, 3.9))
    for j, (c, t) in enumerate(THREE_PT):
        for v in ("sch", "pex"):
            col, ls, mk, lab = VIEW[v]
            d = read(view_file("tran", v, c, t))
            m = (d["time"] >= 95e-9) & (d["time"] <= 595e-9)
            axs[0, j].plot((d["time"][m] - 100e-9) * 1e9, d["v(out)"][m], ls, color=col, label=lab)
            tt, y = sc_edge(view_file("sc", v, c, t), 0)
            k = tt >= 0
            axs[1, j].semilogy(tt[k], 100 * np.abs(1 - y[k]), ls, color=col, lw=1.0)
        axs[0, j].plot((d["time"][m] - 100e-9) * 1e9, d["v(vicm)"][m], ":", color=GREY, lw=0.9)
        axs[0, j].set(xlim=(-5, 300), ylim=(0.70, 0.98), title=f"{c.upper()}, {t} °C".replace("-", "−"))
        axs[1, j].set(xlim=(-20, 1000), ylim=(1e-3, 300), xlabel="Time after the step (ns)")
        axs[1, j].set_yticks([1e-3, 1e-2, 1e-1, 1, 10, 100])
        axs[1, j].axhline(0.1, color=INK, lw=0.8, ls=":")
        if j:
            axs[0, j].set_yticklabels([])
            axs[1, j].set_yticklabels([])
    axs[0, 0].set_ylabel("Buffer $V_{out}$ (V)")
    axs[1, 0].set_ylabel("4-mV SC step\nsettling error (%)")
    for n, ax in enumerate(axs.flat):
        ax.text(0.97, 0.05 if n < 3 else 0.95, f"({chr(97 + n)})", transform=ax.transAxes, ha="right",
                va="bottom" if n < 3 else "top")
    fig.tight_layout(h_pad=0.6, w_pad=0.4, rect=(0, 0, 1, 0.94))
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.94))
    save(fig, "fig_postlayout_steps.png")


def fig_postlayout_pvt():
    """UGF and phase margin of schematic and post-layout over corners and temperature."""
    pl = rows_csv("postlayout_summary.csv")
    fig, axs = plt.subplots(2, 1, figsize=(COL2, 3.9), sharex=True)
    for ax, key, scale in ((axs[0], "ugf_hz", 1e-6), (axs[1], "pm_deg", 1.0)):
        xs = pvt_axis(ax, groups=ax is axs[1])
        for v, off in (("sch", -0.15), ("pex", 0.15)):
            col, ls, mk, lab = VIEW[v]
            ys = [[q for q in pl if q["view"] == v and q["corner"] == c and q["temp_c"] == t][0][key] * scale
                  for c in CORNERS for t in (-40, 27, 125)]
            ax.plot(np.array(xs) + off, ys, mk, color=col, ms=5, mfc=col if v == "sch" else "white", label=lab)
    axs[0].set(ylabel="Unity-gain freq. (MHz)", ylim=(0, 35))
    axs[1].set(ylabel="Phase margin (deg)", ylim=(0, 95))
    axs[1].axhline(45, color=INK, lw=0.8, ls=":")
    axs[1].set_xlabel("Temperature (°C) and process corner, $V_{DD}$ = 1.65 V", labelpad=16)
    axs[0].legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, 1.0))
    panel(axs[0], "(a)")
    panel(axs[1], "(b)")
    fig.tight_layout(h_pad=0.6)
    save(fig, "fig_postlayout_pvt.png")


def fig_postlayout_sens():
    """Phase margin when the parasitics of one net group are removed from the extraction."""
    pl = rows_csv("postlayout_summary.csv")
    sens = rows_csv("postlayout_sensitivity.csv")
    labels = [r["removed"] for r in sens if r["corner"] == "TT"]
    order = ["post-layout"] + labels[1:] + ["all parasitics removed"]
    pm = {}
    for corner, t in (("TT", 27), ("SS", -40)):
        base = [q for q in pl if q["view"] == "pex" and q["corner"] == corner and q["temp_c"] == t][0]["pm_deg"]
        pm[corner] = {"post-layout": base, **{r["removed"]: r["pm_deg"] for r in sens if r["corner"] == corner}}
    fig, ax = plt.subplots(figsize=(COL1 + 0.6, 2.9))
    y = np.arange(len(order))[::-1]
    for corner, dy, col, lab in (("TT", 0.19, BLUE, "TT, 27 °C"), ("SS", -0.19, ORANGE, "SS, \u221240 °C")):
        vals = [pm[corner][k] for k in order]
        ax.barh(y + dy, vals, height=0.36, color=col, label=lab)
        for yy, v in zip(y, vals):
            ax.text(v + 0.8, yy + dy, f"{v:.0f}", va="center", ha="left")
    short = {"post-layout": "all extracted C", "all parasitics removed": "no parasitics (= schematic)"}
    ax.set_yticks(y)
    ax.set_yticklabels([short.get(k, "without " + k.split(" (")[0]) for k in order])
    ax.set(xlabel="Phase margin (deg)", xlim=(0, 72))
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    save(fig, "fig_postlayout_sens.png")

# ----------------------------------------------------------------------------
# Monte Carlo (sim/montecarlo.py)
MC_SETS = (("process", "global process"), ("mismatch", "local mismatch"), ("both", "process + mismatch"))


def mc_rows():
    return [r for r in rows_csv("mc_summary.csv") if r["ok"] == 1]


def mc_vals(rows, mset, bias, key, scale=1.0):
    return np.array([r[key] * scale for r in rows if r["set"] == mset and r["bias"] == bias])


def fig_mc_iq():
    rows = mc_rows()
    fig, axs = plt.subplots(1, 3, figsize=(COL2, 2.5), sharey=True)
    bins = np.logspace(-4, 3, 50)
    for ax, (mset, title) in zip(axs, MC_SETS):
        for bias in ("fix", "reg"):
            col, mk, lab = BIAS[bias]
            v = np.clip(mc_vals(rows, mset, bias, "iq_ua"), 1.1e-4, 900)
            ax.hist(v, bins=bins, color=col, alpha=0.55 if bias == "fix" else 0.75, label=lab,
                    histtype="stepfilled", edgecolor=col, linewidth=0.8)
        ax.axvline(4.2, color=INK, lw=0.8, ls=":")
        ax.set_xscale("log")
        ax.set(xlim=(1e-4, 1e3), xlabel="$I_Q$ of output stage (µA)", title=title)
        ax.set_xticks([1e-4, 1e-2, 1, 1e2])
    axs[0].set_ylabel("Samples")
    for ax, sl in zip(axs, "abc"):
        ax.text(0.03, 0.96, f"({sl})", transform=ax.transAxes, ha="left", va="top")
    fig.tight_layout(w_pad=0.6, rect=(0, 0, 1, 0.9))
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.9))
    save(fig, "fig_mc_iq.png")


def fig_mc_perf():
    """Distributions of UGF, PM, buffer offset and SC small-step error (process + mismatch)."""
    rows = mc_rows()
    fig, axs = plt.subplots(1, 4, figsize=(COL2, 2.4))
    spec = (("ugf_hz", 1e-6, "Unity-gain freq. (MHz)", np.logspace(-3, 2.5, 40), True),
            ("pm_deg", 1.0, "Phase margin (deg)", np.linspace(0, 95, 39), False),
            ("offset_mv", 1.0, "Buffer offset (mV)", np.linspace(-60, 60, 41), False),
            ("sc_err250_Sr_pct", 1.0, "Error at 250 ns (%)", np.logspace(-2.5, 2.5, 41), True))
    for ax, (key, sc, lab, bins, logx) in zip(axs, spec):
        for bias in ("fix", "reg"):
            col, mk, blab = BIAS[bias]
            v = mc_vals(rows, "both", bias, key, sc)
            v = v[np.isfinite(v)]
            v = np.clip(v, bins[0] * 1.01, bins[-1] * 0.99) if logx else np.clip(v, bins[0] + 1e-9, bins[-1] - 1e-9)
            ax.hist(v, bins=bins, color=col, alpha=0.55 if bias == "fix" else 0.75, histtype="stepfilled",
                    edgecolor=col, linewidth=0.8, label=blab)
        if logx:
            ax.set_xscale("log")
        ax.set(xlabel=lab)
    axs[0].set_ylabel("Samples")
    axs[3].axvline(0.1, color=INK, lw=0.8, ls=":")
    for ax, sl in zip(axs, "abcd"):
        ax.text(0.04, 0.96, f"({sl})", transform=ax.transAxes, ha="left", va="top")
    fig.tight_layout(w_pad=0.5, rect=(0, 0, 1, 0.88))
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.88))
    save(fig, "fig_mc_perf.png")


def fig_mc_waves():
    """Loop gain and 4-mV SC step of the first 100 samples (process + mismatch)."""
    w = np.load(RES / "mc_waves.npz")
    fig, axs = plt.subplots(2, 2, figsize=(COL2, 3.9), sharex="col")
    for r, bias in enumerate(("fix", "reg")):
        col = BIAS[bias][0]
        f, loop = w[f"both_{bias}_f"], w[f"both_{bias}_loop"]
        t, v = w[f"both_{bias}_t"], w[f"both_{bias}_vout"]
        for k in range(loop.shape[0]):
            axs[r, 0].semilogx(f, 20 * np.log10(np.abs(loop[k])), "-", color=col, lw=0.5, alpha=0.35)
            y = (v[k] - v[k][0]) / -0.004
            axs[r, 1].plot((t - 100e-9) * 1e9, y, "-", color=col, lw=0.5, alpha=0.35)
        _, mag, _ = loop_tf(RES / "loop_reg_tt_27.dat")
        f0, _, _ = loop_tf(RES / "loop_reg_tt_27.dat")
        axs[r, 0].semilogx(f0, mag, "-", color=INK, lw=1.0, label="nominal (TT, 27 °C)")
        axs[r, 0].set(ylim=(-40, 110), ylabel="$|T|$ (dB)")
        axs[r, 0].axhline(0, color=GREY, lw=0.6, ls=":")
        axs[r, 1].set(ylim=(-0.1, 1.3), ylabel="Normalised $V_{out}$")
        axs[r, 0].text(0.97, 0.95, BIAS_ROW[bias], transform=axs[r, 0].transAxes, ha="right", va="top",
                       bbox=dict(fc="white", ec="none", pad=1.0))
    axs[1, 0].set(xlabel="Frequency (Hz)", xlim=(10, 1e9))
    axs[1, 1].set(xlabel="Time after the 4-mV step (ns)", xlim=(-20, 1000))

    for ax, sl in zip(axs.flat, "abcd"):
        left = ax in axs[:, 0]
        ax.text(0.03 if left else 0.97, 0.95, f"({sl})", transform=ax.transAxes, ha="left" if left else "right",
                va="top", bbox=dict(fc="white", ec="none", pad=1.0))
    fig.tight_layout(h_pad=0.4, w_pad=1.0)
    top_legend(fig, [mpl.lines.Line2D([], [], color=INK, lw=1.0), mpl.lines.Line2D([], [], color=ORANGE, lw=0.8),
                     mpl.lines.Line2D([], [], color=BLUE, lw=0.8)],
               ["nominal (TT, 27 °C)", "samples, fixed bias", "samples, deadzone regulation"], ncol=3)
    save(fig, "fig_mc_waves.png")


def gif_three_phase():
    """Animation of the 200-mV buffer step (TT, 27 degC): the waveforms are traced in time,
    the three settling phases are shaded as they happen, and a live view of the output
    stage shows which device conducts and how much current flows into C_L."""
    from matplotlib.patches import Circle, FancyArrow, Rectangle
    t, v, vin, vgp, vgn, iout, t1, t2, ts = three_phase_data()
    d = read(RES / "tran_reg_tt_27.dat")
    m = (d["time"] >= 95e-9) & (d["time"] <= 595e-9)
    ip = d["i(v.x1.viq)"][m] * 1e6                 # MP3 current (uA)
    io = iout * 1e3                                 # C_L current (uA)
    i_n = np.maximum(ip - io, 0.0)                  # MN3 current by KCL at V_out (uA)
    T_END = 100.0
    keep = t <= T_END
    t, v, vin, vgp, vgn, io, ip, i_n = (x[keep] for x in (t, v, vin, vgp, vgn, io, ip, i_n))
    phases = [(0, t1, "RC phase", "Stage 2 pulls the MP3 gate to the\nrail: MP3 is fully on and charges\n"
                                  "$C_L$ with about 0.5 mA."),
              (t1, t2, "Large-signal phase", "The gates leave the rails; the\noutput current falls steeply and\n"
                                             "overshoots slightly."),
              (t2, ts, "Small-signal phase", "Both gates are in the deadzone;\nthe loop settles linearly with\n"
                                             "only $I_Q$ in the output stage."),
              (ts, T_END, "Settled", "Within 0.1 % of the final value;\nMP3 and MN3 carry only the\n"
                                     "quiescent current $I_Q$ = 4.2 µA.")]

    mpl.rcParams.update({"font.size": 10, "axes.labelsize": 10, "legend.fontsize": 10,
                         "xtick.labelsize": 10, "ytick.labelsize": 10})
    fig = plt.figure(figsize=(9.6, 5.4), dpi=120)
    gs = fig.add_gridspec(3, 2, width_ratios=(1.9, 1.0), hspace=0.18, wspace=0.04,
                          left=0.08, right=0.985, top=0.83, bottom=0.10)
    axs = [fig.add_subplot(gs[i, 0]) for i in range(3)]
    for ax in axs[1:]:
        ax.sharex(axs[0])
    sch = fig.add_subplot(gs[:, 1])
    fig.text(0.5, 0.975, "Ring amplifier: the three settling phases of a 200-mV step (TT, 27 °C, $C_L$ = 50 pF)",
             ha="center", va="top", fontsize=11)
    # static axes setup
    axs[0].set(ylabel="Voltage (V)", ylim=(0.70, 0.96))
    axs[1].set(ylabel="Gates (V)", ylim=(-0.1, 1.75))
    axs[2].set(ylabel="Current (µA)", ylim=(-150, 650), xlabel="Time after the input step (ns)")
    for ax in axs:
        ax.set_xlim(-5, T_END)
    for ax in axs[:2]:
        plt.setp(ax.get_xticklabels(), visible=False)
    lines = dict(vin=axs[0].plot([], [], ":", color=GREY, lw=1.2)[0],
                 vout=axs[0].plot([], [], "-", color=BLUE, lw=1.6)[0],
                 vgp=axs[1].plot([], [], "-", color=INK, lw=1.4)[0],
                 vgn=axs[1].plot([], [], "--", color=ORANGE, lw=1.4)[0],
                 io=axs[2].plot([], [], "-", color=BLUE, lw=1.6)[0],
                 ip=axs[2].plot([], [], "-", color=INK, lw=1.0, alpha=0.6)[0])
    dots = [ax.plot([], [], "o", ms=5, color=c, zorder=6)[0] for ax, c in
            ((axs[0], BLUE), (axs[1], INK), (axs[1], ORANGE), (axs[2], BLUE))]
    shades = [[ax.axvspan(0, 0, color=PHASE_TINT[min(k, 2)], lw=0, alpha=1.0 if k < 3 else 0.0) for k in range(4)]
              for ax in axs]
    h = [mpl.lines.Line2D([], [], color=GREY, ls=":", lw=1.2), mpl.lines.Line2D([], [], color=BLUE, lw=1.6),
         mpl.lines.Line2D([], [], color=INK, lw=1.4), mpl.lines.Line2D([], [], color=ORANGE, ls="--", lw=1.4),
         mpl.lines.Line2D([], [], color=INK, lw=1.0, alpha=0.6)]
    fig.legend(h, ["$V_{in}$", "$V_{out}$, $I_{C_L}$", "$V_{GP}$ (MP3 gate)", "$V_{GN}$ (MN3 gate)",
                   "$I_{MP3}$"], loc="lower center", ncol=5, bbox_to_anchor=(0.5, 0.855), frameon=False,
               handlelength=2.0, columnspacing=1.4)
    # output-stage view
    sch.set_xlim(0.6, 10.6)
    sch.set_ylim(0, 14.2)
    sch.axis("off")
    k = dict(color=INK, lw=1.4, solid_capstyle="round")
    sch.plot([3.2, 6.2], [9.6, 9.6], **k)
    sch.text(4.7, 9.75, "$V_{DD}$", ha="center", va="bottom")
    sch.plot([4.7, 4.7], [9.6, 8.6], **k)
    sch.plot([4.7, 4.7], [6.6, 4.4], **k)
    sch.plot([4.7, 4.7], [2.4, 1.4], **k)
    for yy in (1.4, 1.15, 0.9):
        w = {1.4: 0.6, 1.15: 0.38, 0.9: 0.16}[yy]
        sch.plot([4.7 - w, 4.7 + w], [yy, yy], **k)
    sch.plot([4.7, 8.2], [5.5, 5.5], **k)
    sch.add_patch(Circle((4.7, 5.5), 0.09, color=INK, zorder=5))
    sch.text(6.2, 5.62, "$V_{out}$", ha="center", va="bottom")
    sch.plot([8.2, 8.2], [5.5, 4.0], **k)
    sch.plot([7.6, 8.8], [4.0, 4.0], color=INK, lw=2.2)
    sch.plot([7.6, 8.8], [3.6, 3.6], color=INK, lw=2.2)
    sch.plot([8.2, 8.2], [3.6, 2.6], **k)
    for yy, w in ((2.6, 0.5), (2.38, 0.32), (2.16, 0.14)):
        sch.plot([8.2 - w, 8.2 + w], [yy, yy], **k)
    sch.text(9.0, 3.8, "$C_L$", ha="left", va="center")
    dev = {}
    for name, y0, lab in (("MP3", 6.6, "MP3"), ("MN3", 2.4, "MN3")):
        dev[name] = Rectangle((4.1, y0), 1.2, 2.0, fc="white", ec=INK, lw=1.4, zorder=3)
        sch.add_patch(dev[name])
        sch.text(4.7, y0 + 1.0, lab, ha="center", va="center", zorder=4)
        sch.plot([2.7, 4.1], [y0 + 1.0, y0 + 1.0], **k)
    sch.text(2.6, 7.6, "$V_{GP}$", ha="right", va="bottom")
    sch.text(2.6, 3.4, "$V_{GN}$", ha="right", va="bottom")
    val_gp = sch.text(2.6, 7.5, "", ha="right", va="top", fontsize=10, color=INK)
    val_gn = sch.text(2.6, 3.3, "", ha="right", va="top", fontsize=10, color=ORANGE)
    val_p = sch.text(5.5, 8.15, "", ha="left", va="center", fontsize=10)
    val_n = sch.text(5.5, 2.85, "", ha="left", va="center", fontsize=10)
    val_c = sch.text(7.25, 4.6, "", ha="right", va="center", fontsize=10, color=BLUE)
    arrow = [None]
    title = sch.text(5.6, 14.1, "", ha="center", va="top", fontsize=11, fontweight="bold")
    expl = sch.text(5.6, 13.15, "", ha="center", va="top", fontsize=10, linespacing=1.25)
    on_col = "#f6c3a5"

    def shade_alpha(i_ua):
        return min(1.0, max(0.0, np.log10(max(i_ua, 1e-3) / 4.2) / np.log10(600 / 4.2)))

    frames = list(np.linspace(-5, T_END, 150)) + [T_END] * 18      # hold the last frame

    def upd(x):
        sel = t <= x
        lines["vin"].set_data(t[sel], vin[sel])
        lines["vout"].set_data(t[sel], v[sel])
        lines["vgp"].set_data(t[sel], vgp[sel])
        lines["vgn"].set_data(t[sel], vgn[sel])
        lines["io"].set_data(t[sel], io[sel])
        lines["ip"].set_data(t[sel], ip[sel])
        j = max(int(np.searchsorted(t, x)) - 1, 0)
        for dot, yy in zip(dots, (v[j], vgp[j], vgn[j], io[j])):
            dot.set_data([t[j]], [yy])
        for ax_sh in shades:
            for kk, (a0, a1, _, _) in enumerate(phases[:3]):
                lo, hi = a0, min(a1, x)
                ax_sh[kk].set_x(lo)
                ax_sh[kk].set_width(max(hi - lo, 0.0))
        ph = next((p for p in phases if p[0] <= x < p[1]), phases[-1]) if x >= 0 else \
            (None, None, "Before the step", "The amplifier is at rest: both gates sit in the deadzone and only\n"
                                            "$I_Q$ = 4.2 µA flows through MP3 and MN3.")
        title.set_text(ph[2])
        expl.set_text(ph[3])
        for name, cur in (("MP3", ip[j]), ("MN3", i_n[j])):
            a_ = shade_alpha(abs(cur))
            col = np.array(mpl.colors.to_rgb(on_col)) * a_ + np.ones(3) * (1 - a_)
            dev[name].set_facecolor(col)
        val_gp.set_text(f"{vgp[j]:.2f} V")
        val_gn.set_text(f"{vgn[j]:.2f} V")
        val_p.set_text(f"{ip[j]:6.0f} µA" if abs(ip[j]) >= 10 else f"{ip[j]:6.1f} µA")
        val_n.set_text(f"{i_n[j]:6.0f} µA" if abs(i_n[j]) >= 10 else f"{i_n[j]:6.1f} µA")
        val_c.set_text(f"{io[j]:+.0f} µA" if abs(io[j]) >= 10 else f"{io[j]:+.1f} µA")
        if arrow[0] is not None:
            arrow[0].remove()
            arrow[0] = None
        if abs(io[j]) > 5:            # on the wire between V_out and C_L, length ~ |I_CL|
            ln = 0.45 + 0.75 * min(abs(io[j]) / 550, 1.0)
            y0_ = 5.25 if io[j] > 0 else 4.15
            arrow[0] = sch.add_patch(FancyArrow(7.75, y0_, 0, -ln if io[j] > 0 else ln, width=0.08,
                                                head_width=0.35, head_length=0.3, color=BLUE, zorder=6,
                                                length_includes_head=True))
        return []

    ani = animation.FuncAnimation(fig, upd, frames=frames, blit=False)
    ani.save(OUT / "three_phase.gif", writer=animation.PillowWriter(fps=15), dpi=120)
    plt.close(fig)
    mpl.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 9,
                         "xtick.labelsize": 9, "ytick.labelsize": 9})
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
    fig.tight_layout()
    top_legend(fig, *ax.get_legend_handles_labels(), ncol=5)
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
        mag = k // 3 % 2 == 0
        ax.text(0.03 if mag else 0.97, 0.05 if mag else 0.95, f"({'abcdefghijkl'[k]})", transform=ax.transAxes,
                ha="left" if mag else "right", va="bottom" if mag else "top")
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
        ax.text(0.97, 0.95, f"({'abcdefghijkl'[n]})", transform=ax.transAxes, ha="right", va="top")
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
    fig_three_phase_corners()
    fig_phase_bars()
    fig_postlayout_bode()
    fig_postlayout_steps()
    fig_postlayout_pvt()
    fig_postlayout_sens()
    if (RES / "mc_summary.csv").exists():      # written by sim/montecarlo.py
        fig_mc_iq()
        fig_mc_perf()
        fig_mc_waves()
    fig_step_corners(2, "fig_step_corners_large.png", (-50, 600))
    fig_step_corners(0, "fig_step_corners_small.png", (-50, 2000))
