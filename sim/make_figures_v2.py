#!/usr/bin/env python3
"""IEEE-style result figures of RAMP_V2 from sim/results/v2 (run sim/v2_sim.py,
sim/v2_montecarlo.py and sim/v2_postlayout.py first).

Writes PNGs to docs/figures/v2/.  Same style as make_figures.py: RAMP_V2 blue, RAMP_LR (v1,
deadzone regulation through a replica) orange, references in grey/black; every series also
has its own line style or marker so the figures read in greyscale.
"""
import csv
import sys
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_figures as mf  # noqa: E402  (rcParams, palette, helpers)
from ramp_pvt import CF, CS, SC_EDGES  # noqa: E402

REPO = mf.REPO
RES = REPO / "sim" / "results" / "v2"
RES1 = REPO / "sim" / "results"
OUT = REPO / "docs" / "figures" / "v2"
OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, INK, GREY = mf.BLUE, mf.ORANGE, mf.INK, mf.GREY
COL1, COL2 = mf.COL1, mf.COL2
CORNERS, CSTYLE, TEMPS = mf.CORNERS, mf.CSTYLE, mf.TEMPS
V1 = (ORANGE, "o", "v1 (RAMP_LR, replica regulation)")
V2 = (BLUE, "s", "v2 (RAMP_V2)")


def rows(path):
    out = []
    for r in csv.DictReader(open(path)):
        for k, v in r.items():
            try:
                r[k] = float(v)
            except (TypeError, ValueError):
                pass
        out.append(r)
    return out


PVT = rows(RES / "pvt_summary.csv")


def pick(rs, **kw):
    return [r for r in rs if all(r[k] == v for k, v in kw.items())]


def save(fig, name):
    fig.savefig(OUT / name)
    plt.close(fig)
    print("wrote", OUT / name)


def panel(ax, s, right=False):
    ax.text(0.985 if right else 0.015, 0.97, s, transform=ax.transAxes, va="top", ha="right" if right else "left",
            bbox=dict(fc="white", ec="none", pad=1.0))


def sc_edge(path, k):
    d = mf.read(path)
    t, v = d["time"], d["v(out)"]
    t0, dv, win = SC_EDGES[k]
    v0 = np.interp(t0 - 1e-9, t, v)
    m = (t >= t0 - 50e-9) & (t <= t0 + win)
    return (t[m] - t0) * 1e9, (v[m] - v0) / (-CS / CF * dv)


# ----------------------------------------------------------------------------
def fig_bode_corners():
    """Loop gain at 5 corners x 3 temperatures (schematic, 1.65 V)."""
    fig, axs = plt.subplots(2, 3, figsize=(COL2, 3.7), sharex=True)
    for j, t in enumerate(TEMPS):
        am, ap = axs[0, j], axs[1, j]
        for c in CORNERS:
            col, ls, mk = CSTYLE[c]
            f, mag, ph = mf.loop_tf(RES / f"loop_{c.lower()}_{t}.dat")
            am.semilogx(f, mag, ls, color=col)
            ap.semilogx(f, ph, ls, color=col)
            p = pick(PVT, corner=c, temp_c=t, vdd=1.65)[0]
            am.plot(p["ugf_hz"], 0, mk, ms=4.5, mfc="white", mec=col, mew=1.0)
            ap.plot(p["ugf_hz"], p["pm_deg"] - 180, mk, ms=4.5, mfc="white", mec=col, mew=1.0)
        pts = pick(PVT, temp_c=t, vdd=1.65)
        u = [q["ugf_hz"] / 1e6 for q in pts]
        m = [q["pm_deg"] for q in pts]
        am.text(0.97, 0.95, f"UGF {min(u):.3g}–{max(u):.3g} MHz", transform=am.transAxes, ha="right", va="top")
        ap.text(0.03, 0.05, f"PM {min(m):.0f}–{max(m):.0f}$^\\circ$", transform=ap.transAxes, ha="left", va="bottom")
        am.set(ylim=(-40, 140))
        ap.set(ylim=(-360, 10))
        ap.set_yticks([-360, -270, -180, -90, 0])
        ap.axhline(-180, color=GREY, lw=0.6, ls=":")
        am.axhline(0, color=GREY, lw=0.6, ls=":")
        if j:
            am.set_yticklabels([])
            ap.set_yticklabels([])
        am.set_title(f"{t} °C".replace("-", "−"))
        ap.set(xlabel="Frequency (Hz)", xlim=(1, 1e9))
        ap.set_xticks([1, 1e2, 1e4, 1e6, 1e8])
    axs[0, 0].set_ylabel("$|T|$ (dB)")
    axs[1, 0].set_ylabel("$\\angle T$ (deg)")
    for k, ax in enumerate(axs.flat):
        mag = k < 3
        ax.text(0.03 if mag else 0.97, 0.05 if mag else 0.95, f"({'abcdef'[k]})", transform=ax.transAxes,
                ha="left" if mag else "right", va="bottom" if mag else "top")
    fig.tight_layout(h_pad=0.3, w_pad=0.4, rect=(0, 0, 1, 0.93))
    mf.corner_legend(fig, 0.93)
    save(fig, "fig_v2_bode_corners.png")


def fig_iq_temperature():
    """(a) I_Q versus temperature against its target 4 I_BIAS; (b) UGF versus temperature."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(COL2, 2.6))
    for c in CORNERS:
        col, ls, mk = CSTYLE[c]
        d = mf.read(RES / f"tsweep_{c.lower()}.dat")
        t = d["temp-sweep"] if "temp-sweep" in d else d[list(d)[0]]
        iq = 1e6 * d["i(v.x1.viq)"]
        ibias = (t + 273.15) / 300.15 * 1e5 * np.abs(d["i(vrref)"])          # I_BIAS in uA
        a.plot(t, iq, ls, color=col, marker=mk, ms=3.5, markevery=6, mfc="white", label=f"{c}")
        a.plot(t, 4 * ibias, ":", color=col, lw=0.8)
        pts = sorted(pick(PVT, corner=c, vdd=1.65), key=lambda r: r["temp_c"])
        b.plot([p["temp_c"] for p in pts], [p["ugf_hz"] / 1e6 for p in pts], ls, color=col, marker=mk, ms=4,
               mfc="white")
    a.set(xlabel="Temperature (°C)", ylabel="$I_Q$ of output stage (µA)", xlim=(-40, 125), ylim=(0, 10))
    a.text(0.03, 0.95, "dotted: target $4\\,I_{BIAS}$", transform=a.transAxes, ha="left", va="top",
           bbox=dict(fc="white", ec="none", pad=1.0))
    b.set(xlabel="Temperature (°C)", ylabel="Unity-gain frequency (MHz)", xlim=(-50, 135), ylim=(0, 25))
    u = [p["ugf_hz"] / 1e6 for p in PVT]
    b.text(0.97, 0.95, f"45 PVT points: {min(u):.1f}–{max(u):.1f} MHz", transform=b.transAxes, ha="right", va="top",
           bbox=dict(fc="white", ec="none", pad=1.0))
    panel(a, "(a)", right=True)
    a.texts[-1].set_position((0.985, 0.03))
    a.texts[-1].set_va("bottom")
    panel(b, "(b)")
    b.texts[-1].set_position((0.015, 0.03))
    b.texts[-1].set_va("bottom")
    fig.tight_layout(w_pad=1.5, rect=(0, 0, 1, 0.9))
    mf.corner_legend(fig, 0.9)
    save(fig, "fig_v2_iq_temperature.png")


def fig_pvt_ugf_pm():
    """UGF, phase margin and gain margin over the 45 PVT points, v1 (RAMP_LR) and v2."""
    v1 = mf.ROWS
    fig, axs = plt.subplots(3, 1, figsize=(COL2, 5.4), sharex=True)
    for ax, key, scale, lab in ((axs[0], "ugf_hz", 1e-6, "Unity-gain freq. (MHz)"), (axs[1], "pm_deg", 1, "Phase margin (deg)"),
                                (axs[2], "gm_db", 1, "Gain margin (dB)")):
        xs = mf.pvt_axis(ax, groups=ax is axs[2])
        for (col, mk, name), data, off in ((V1, [r for r in v1 if r["design"] == "RAMP_LR" and r["bias"] == "reg"], -0.18),
                                           (V2, PVT, 0.18)):
            for x, (c, t) in zip(xs, [(c, t) for c in CORNERS for t in TEMPS]):
                pts = [r for r in data if r["corner"] == c and r["temp_c"] == t]
                vals = [p[key] * scale for p in pts]
                nom = [p[key] * scale for p in pts if p["vdd"] == 1.65][0]
                ax.plot([x + off] * 2, [min(vals), max(vals)], "-", color=col, lw=1.0)
                ax.plot(x + off, nom, mk, color=col, ms=4.5, label=name if (c, t) == ("TT", -40) else None)
        ax.set_ylabel(lab)
    axs[0].set(ylim=(0, 36))
    axs[1].set(ylim=(30, 95))
    axs[2].set(ylim=(0, 40))
    axs[2].axhline(15, color=INK, lw=0.8, ls=":")
    axs[2].text(18.6, 15.8, "15 dB", ha="right", va="bottom")
    axs[2].set_xlabel("Temperature (°C) and process corner; bars: $V_{DD}$ = 1.65 V ± 5 % (schematic)", labelpad=16)
    axs[0].legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, 1.0))
    for ax, s in zip(axs, "abc"):
        panel(ax, f"({s})")
    fig.tight_layout(h_pad=0.5)
    save(fig, "fig_v2_pvt_ugf_pm.png")


def fig_settling_pvt():
    """SC error 250 ns after a 200-mV and a 4-mV step, v1 versus v2 (schematic, 1.65 V)."""
    v1 = [r for r in mf.ROWS if r["design"] == "RAMP_LR" and r["bias"] == "reg"]
    fig, axs = plt.subplots(2, 1, figsize=(COL2, 3.9), sharex=True)
    for ax, tag, title in ((axs[0], "Lr", "200-mV step (large signal)"), (axs[1], "Sr", "4-mV step (small signal)")):
        xs = mf.pvt_axis(ax, groups=ax is axs[1])
        for (col, mk, name), data, off in ((V1, v1, -0.18), (V2, PVT, 0.18)):
            ys = [pick(data, corner=c, temp_c=t, vdd=1.65)[0][f"sc_err250_{tag}_pct"] for c in CORNERS for t in TEMPS]
            ax.semilogy(np.array(xs) + off, ys, mk, color=col, ms=4.5, label=name, ls="none")
        ax.axhline(0.1, color=INK, lw=0.8, ls=":")
        ax.text(-0.5, 0.115, "0.1 %", ha="left", va="bottom")
        ax.text(0.985, 0.95, title, transform=ax.transAxes, ha="right", va="top", bbox=dict(fc="white", ec="none", pad=1.0))
        ax.set(ylabel="Error at 250 ns (%)", ylim=(3e-3, 10))
    axs[0].legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, 1.0))
    for ax, s in zip(axs, "ab"):
        panel(ax, f"({s})")
    axs[1].set_xlabel("Temperature (°C) and process corner, $V_{DD}$ = 1.65 V", labelpad=16)
    fig.tight_layout(h_pad=0.6)
    save(fig, "fig_v2_settling_pvt.png")


def fig_steps():
    """SC 200-mV and 4-mV steps at 5 corners x 3 temperatures: normalised output and error."""
    fig, axs = plt.subplots(2, 3, figsize=(COL2, 3.8), sharex=True)
    for j, t in enumerate(TEMPS):
        aw, ae = axs[0, j], axs[1, j]
        for i, c in enumerate(CORNERS):
            col, ls, mk = CSTYLE[c]
            for k, lw in ((2, 1.2), (0, 0.8)):
                tt, y = sc_edge(RES / f"sc_{c.lower()}_{t}.dat", k)
                every = max(1, len(tt) // 7)
                mark = dict(marker=mk, ms=3.0, mfc="white", markevery=((i + 1) * every // 6, every))
                if k == 2:
                    aw.plot(tt, y, ls, color=col, lw=lw, **mark)
                ae.semilogy(tt[tt >= 0], 100 * np.abs(1 - y[tt >= 0]), ls if k == 2 else ":", color=col, lw=lw,
                            **(mark if k == 2 else {}))
        err = max(pick(PVT, corner=c, temp_c=t, vdd=1.65)[0]["sc_err250_Lr_pct"] for c in CORNERS)
        aw.text(0.97, 0.05, f"worst error at 250 ns: {err:.2g} %", transform=aw.transAxes, ha="right", va="bottom",
                bbox=dict(fc="white", ec="none", pad=1.0))
        aw.set(ylim=(-0.08, 1.25))
        ae.set(ylim=(1e-3, 300))
        ae.set_yticks([1e-3, 1e-2, 1e-1, 1, 10, 100])
        ae.axhline(0.1, color=INK, lw=0.8, ls=":")
        for ax in (aw, ae):
            ax.axvline(250, color=GREY, lw=0.6, ls="--")
        if j:
            aw.set_yticklabels([])
            ae.set_yticklabels([])
        aw.set_title(f"{t} °C".replace("-", "−"))
        ae.set(xlabel="Time after the step (ns)", xlim=(-50, 1000))
    axs[0, 0].set_ylabel("Normalised $V_{out}$")
    axs[1, 0].set_ylabel("Settling error (%)")
    for n, ax in enumerate(axs.flat):
        ax.text(0.97, 0.95, f"({'abcdef'[n]})", transform=ax.transAxes, ha="right", va="top")
    fig.tight_layout(h_pad=0.3, w_pad=0.4, rect=(0, 0, 1, 0.93))
    mf.corner_legend(fig, 0.93, extra=(("4-mV step", dict(color=INK, lw=0.8, ls=":")),))
    save(fig, "fig_v2_sc_steps.png")


def fig_limit_cycle():
    """Buffer steps at SS, -40 degC: v1 post-layout ends in a limit cycle, v2 (+-10 ... +-200 mV) does not."""
    fig, axs = plt.subplots(2, 1, figsize=(COL2, 3.9))
    d1 = mf.read(RES1 / "tran_pex_ss_-40.dat")
    t1 = d1["time"] * 1e6
    axs[0].plot(t1, d1["v(vicm)"], "-", color=GREY, lw=0.8)
    axs[0].plot(t1, d1["v(out)"], "-", color=ORANGE, lw=0.9)
    axs[0].set(ylabel="Voltage (V)", xlim=(0, 1.1), ylim=(0.66, 1.0))
    axs[0].set_title("(a) v1 (RAMP_LR), post-layout, SS, −40 °C: a 200-mV step ends in a limit cycle", fontsize=9)
    for view, col, ls in (("", BLUE, "-"), ("pex_", INK, "--")):
        f = RES / f"lc_{view}ss_-40.dat"
        if f.exists():
            d = mf.read(f)
            axs[1].plot(d["time"] * 1e6, d["v(out)"], ls, color=col, lw=0.9)
    d = mf.read(RES / "lc_ss_-40.dat")
    axs[1].plot(d["time"] * 1e6, d["v(vicm)"], "-", color=GREY, lw=0.8)
    axs[1].set(xlabel="Time (µs)", ylabel="Voltage (V)", xlim=(0, 5.1), ylim=(0.78, 1.06))
    axs[1].set_title("(b) v2 (RAMP_V2), SS, −40 °C: steps of ±10, ±20, ±50, ±100 and ±200 mV", fontsize=9)
    fig.tight_layout(h_pad=0.8, rect=(0, 0, 1, 0.92))
    h = [mpl.lines.Line2D([], [], color=c, ls=l, lw=0.9) for c, l in ((GREY, "-"), (ORANGE, "-"), (BLUE, "-"), (INK, "--"))]
    mf.top_legend(fig, h, ["input", "v1 output (post-layout)", "v2 output (schematic)", "v2 output (post-layout)"],
                  ncol=4, y=0.92)
    save(fig, "fig_v2_limit_cycle.png")


def fig_startup():
    """Power-up: the slow loops (regulation, servo) settle in about 1 ms."""
    pts = (("tt", 27), ("ss", -40), ("sf", -40), ("ff", 125), ("fs", 125))
    fig, axs = plt.subplots(1, 3, figsize=(COL2, 2.5), sharex=True)
    for c, t in pts:
        col, ls, mk = CSTYLE[c.upper()]
        d = mf.read(RES / f"startup_{c}_{t}.dat")
        tm = d["time"] * 1e3
        lab = f"{c.upper()}, {t} °C".replace("-", "−")
        kw = dict(color=col, ls=ls, marker=mk, ms=3.5, markevery=300, mfc="white", label=lab)
        axs[0].semilogy(tm, 1e6 * np.abs(d["i(v.x1.viq)"]), **kw)
        axs[1].plot(tm, d["v(x1.vctrln)"], **kw)
        axs[2].plot(tm, 1e3 * (d["v(out)"] - 0.825), **kw)
    axs[0].set(ylabel="$I_Q$ (µA)", ylim=(0.5, 1000))
    axs[1].set(ylabel="$V_{CTRLN}$ (V)", ylim=(0.3, 0.9))
    axs[2].set(ylabel="$V_{out} - V_{in}$ (mV)", ylim=(-20, 20))
    for ax, s in zip(axs, "abc"):
        ax.set(xlabel="Time after power-up (ms)", xlim=(0, 3))
        panel(ax, f"({s})", right=True)
    fig.tight_layout(w_pad=0.8, rect=(0, 0, 1, 0.88))
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5, bbox_to_anchor=(0.5, 0.88))
    save(fig, "fig_v2_startup.png")


def fig_power():
    """Supply current by block, v1 and v2 side by side (TT, 27 degC, 1.65 V, at rest)."""
    d1 = mf.read(RES1 / "power_tt_27.dat")
    d2 = mf.read(RES / "power_tt_27.dat")
    ua1 = lambda k: 1e6 * float(d1[k][0])
    ua2 = lambda k: 1e6 * float(d2[k][0])
    ib2 = 1e5 * abs(float(d2["i(vrref)"][0]))           # I_BIAS in uA at 27 degC
    v1 = [("Output stage ($I_Q$)", ua1("i(v.x1.viq)")), ("Stage 1 + CMFB", ua1("i(v.x1.v_x1)")),
          ("Stage 2 (deadzone)", ua1("i(v.x1.v_x2)")), ("Trip-point replica", ua1("i(v.x1.v_x4)")),
          ("Deadzone regulation", ua1("i(v.x1.v_x3)")), ("Bias + $I_{BIAS}$", ua1("i(v.x1.v_xb)") + 1.0)]
    # v2: the stage-1 and CMFB tails (40 + 10 uA) are sourced by the bias block's PMOS mirror
    s1 = 50.0 * ib2
    v2 = [("Output stage ($I_Q$)", ua2("i(v.x1.viq)")), ("Stage 1 + CMFB", s1),
          ("Stage 2 (deadzone)", ua2("i(v.x1.v_x2)")), ("Trip-point replica", ua2("i(v.x1.v_xt)")),
          ("Regulation + servo", ua2("i(v.x1.v_xr)") + ua2("i(v.x1.v_xs)")),
          ("Bias + $I_{BIAS}$", ua2("i(v.x1.v_xb)") - s1 + ib2)]
    hues = [BLUE, ORANGE, "#1baf7a", "#eda100", "#6250d6", "#e87ba4"]
    fig, axs = plt.subplots(1, 2, figsize=(COL2, 2.6))
    for ax, blocks, d, title in ((axs[0], v1, d1, "(a) v1 (RAMP_LR)"), (axs[1], v2, d2, "(b) v2 (RAMP_V2)")):
        total = -1e6 * float(d["i(v2)"][0])
        wedges, _ = ax.pie([max(b[1], 0) for b in blocks], colors=hues, startangle=90, counterclock=False,
                           wedgeprops=dict(width=0.36, edgecolor="white", linewidth=1.5))
        ax.text(0, 0.08, f"{total:.0f} µA", ha="center", va="center", fontsize=11)
        ax.text(0, -0.16, f"{total * 1.65:.0f} µW", ha="center", va="center")
        ax.set_aspect("equal")
        ax.set_title(title, y=-0.08, va="top")
        ax.legend(wedges, [f"{n}: {v:.1f} µA" for n, v in blocks], loc="center left", bbox_to_anchor=(0.92, 0.5),
                  frameon=False, handlelength=1.0)
        ax.grid(False)
    fig.tight_layout(w_pad=6.0)
    save(fig, "fig_v2_power.png")


def fig_psrr():
    fig, ax = plt.subplots(figsize=(COL1, 2.3))
    for c in CORNERS:
        d = mf.read(RES / f"psrr_{c.lower()}_27.dat")
        a = np.abs(d["psrr_re"] + 1j * d["psrr_im"])
        col, ls, mk = CSTYLE[c]
        ax.semilogx(d["frequency"], -20 * np.log10(a), ls, color=col, marker=mk, ms=3.5, markevery=40, mfc="white",
                    label=c)
    ax.set(xlabel="Frequency (Hz)", ylabel="PSRR (dB)", xlim=(1, 1e10), ylim=(0, 110))
    fig.tight_layout()
    mf.top_legend(fig, *ax.get_legend_handles_labels(), ncol=5)
    save(fig, "fig_v2_psrr.png")


# ----------------------------------------------------------------------------
MC_SETS = (("process", "global process"), ("mismatch", "local mismatch"), ("both", "process + mismatch"))


def mc2():
    return [r for r in rows(RES / "mc_summary.csv") if r["ok"] == 1]


def mc1():
    return [r for r in rows(RES1 / "mc_summary.csv") if r["ok"] == 1 and r["bias"] == "reg"]


def fig_mc_offset_iq():
    """Offset and I_Q of the buffer, v1 (RAMP_LR, regulated) versus v2, for the three MC sets."""
    r1, r2 = mc1(), mc2()
    fig, axs = plt.subplots(2, 3, figsize=(COL2, 4.2))
    ob = np.linspace(-30, 30, 61)
    ib = np.logspace(-3, 2, 51)
    for j, (mset, title) in enumerate(MC_SETS):
        for (col, mk, name), data, alpha in ((V1, r1, 0.5), (V2, r2, 0.75)):
            off = np.array([r["offset_mv"] for r in data if r["set"] == mset])
            iq = np.array([r["iq_ua"] for r in data if r["set"] == mset])
            s = off.std()
            axs[0, j].hist(np.clip(off, ob[0] + 1e-6, ob[-1] - 1e-6), bins=ob, color=col, alpha=alpha,
                           histtype="stepfilled", edgecolor=col, lw=0.8,
                           label=f"{name}: σ = {s:.2f} mV")
            axs[1, j].hist(np.clip(iq, ib[0] * 1.01, ib[-1] * 0.99), bins=ib, color=col, alpha=alpha,
                           histtype="stepfilled", edgecolor=col, lw=0.8,
                           label=f"{name}: σ/mean = {100 * iq.std() / iq.mean():.0f} %")
        axs[0, j].axvspan(-5, 5, color="#ececec", zorder=0)
        axs[0, j].set(xlabel="Buffer offset (mV)", xlim=(-30, 30), title=title)
        axs[1, j].set(xlabel="$I_Q$ of output stage (µA)", xscale="log", xlim=(1e-3, 1e2))
        for i in range(2):
            h, l = axs[i, j].get_legend_handles_labels()
            axs[i, j].legend(h, [x.split(": ")[1] for x in l], loc="upper left", bbox_to_anchor=(0.0, 1.0),
                             frameon=False, handlelength=1.0, fontsize=8)
    axs[0, 0].set_ylabel("Samples")
    axs[1, 0].set_ylabel("Samples")
    for n, ax in enumerate(axs.flat):
        ax.text(0.97, 0.95, f"({'abcdef'[n]})", transform=ax.transAxes, ha="right", va="top")
    fig.tight_layout(h_pad=0.8, w_pad=0.6, rect=(0, 0, 1, 0.92))
    h = [mpl.patches.Patch(fc=ORANGE, alpha=0.5, ec=ORANGE), mpl.patches.Patch(fc=BLUE, alpha=0.75, ec=BLUE),
         mpl.patches.Patch(fc="#ececec", ec="none")]
    fig.legend(h, [V1[2], V2[2], "±5-mV target"], loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.92))
    save(fig, "fig_v2_mc_offset_iq.png")


def fig_mc_perf():
    """v2, process + mismatch: UGF, PM, GM and SC error at 250 ns (200 mV)."""
    r2 = [r for r in mc2() if r["set"] == "both"]
    r1 = [r for r in mc1() if r["set"] == "both"]
    fig, axs = plt.subplots(1, 4, figsize=(COL2, 2.4))
    spec = (("ugf_hz", 1e-6, "Unity-gain freq. (MHz)", np.linspace(0, 30, 31), False),
            ("pm_deg", 1.0, "Phase margin (deg)", np.linspace(0, 95, 39), False),
            ("gm_db", 1.0, "Gain margin (dB)", np.linspace(0, 40, 41), False),
            ("sc_err250_Lr_pct", 1.0, "SC error at 250 ns (%)", np.logspace(-3, 1, 41), True))
    for ax, (key, sc, lab, bins, logx) in zip(axs, spec):
        for (col, mk, name), data, alpha in ((V1, r1, 0.5), (V2, r2, 0.75)):
            v = np.array([r[key] * sc for r in data if key in r and isinstance(r[key], float)])
            v = v[np.isfinite(v)]
            v = np.clip(v, bins[0] * (1.01 if logx else 1) + (0 if logx else 1e-9), bins[-1] * (0.99 if logx else 1) - (0 if logx else 1e-9))
            ax.hist(v, bins=bins, color=col, alpha=alpha, histtype="stepfilled", edgecolor=col, lw=0.8, label=name)
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
    save(fig, "fig_v2_mc_perf.png")


def fig_mc_waves():
    """Loop gain and 200-mV SC step of the first 100 process + mismatch samples (v2)."""
    w = np.load(RES / "mc_waves.npz")
    fig, axs = plt.subplots(1, 2, figsize=(COL2, 2.5))
    f, loop = w["f"], w["both_t"]
    tt, v = w["tt"], w["both_v"]
    t0 = SC_EDGES[2][0]
    for k in range(loop.shape[0]):
        axs[0].semilogx(f, 20 * np.log10(np.abs(loop[k])), "-", color=BLUE, lw=0.5, alpha=0.3)
        y = (v[k] - v[k][0]) / -0.2
        axs[1].plot((tt - t0) * 1e9, y, "-", color=BLUE, lw=0.5, alpha=0.3)
    f0, mag, _ = mf.loop_tf(RES / "loop_tt_27.dat")
    axs[0].semilogx(f0, mag, "-", color=INK, lw=1.0)
    tn, yn = sc_edge(RES / "sc_tt_27.dat", 2)
    axs[1].plot(tn, yn, "-", color=INK, lw=1.0)
    axs[0].set(xlabel="Frequency (Hz)", ylabel="$|T|$ (dB)", xlim=(1, 1e9), ylim=(-40, 140))
    axs[0].axhline(0, color=GREY, lw=0.6, ls=":")
    axs[1].set(xlabel="Time after the 200-mV step (ns)", ylabel="Normalised $V_{out}$", xlim=(-20, 600), ylim=(-0.1, 1.25))
    for ax, s in zip(axs, "ab"):
        panel(ax, f"({s})", right=True)
    fig.tight_layout(w_pad=1.2, rect=(0, 0, 1, 0.9))
    mf.top_legend(fig, [mpl.lines.Line2D([], [], color=INK, lw=1.0), mpl.lines.Line2D([], [], color=BLUE, lw=0.8)],
                  ["nominal (TT, 27 °C)", "100 process + mismatch samples"], ncol=2, y=0.9)
    save(fig, "fig_v2_mc_waves.png")


# ----------------------------------------------------------------------------
VIEW = {"sch": (BLUE, "-", "o", "schematic"), "pex": (ORANGE, "--", "s", "post-layout (magic PEX, C only)")}
PL_PTS = (("ss", -40), ("tt", 27), ("ff", 125))


def pl_rows():
    return rows(RES / "postlayout_summary.csv")


def view_file(kind, view, c, t):
    return RES / (f"{kind}_{c}_{t}.dat" if view == "sch" else f"{kind}_pex_{c}_{t}.dat")


def fig_postlayout_bode():
    pl = pl_rows()
    fig, axs = plt.subplots(2, 3, figsize=(COL2, 3.7), sharex=True)
    for j, (c, t) in enumerate(PL_PTS):
        for view, (col, ls, mk, lab) in VIEW.items():
            f, mag, ph = mf.loop_tf(view_file("loop", view, c, t))
            axs[0, j].semilogx(f, mag, ls, color=col, label=lab)
            axs[1, j].semilogx(f, ph, ls, color=col)
            p = pick(pl, view=view, corner=c.upper(), temp_c=t)[0]
            axs[0, j].plot(p["ugf_hz"], 0, mk, ms=4.5, mfc="white", mec=col)
            axs[1, j].plot(p["ugf_hz"], p["pm_deg"] - 180, mk, ms=4.5, mfc="white", mec=col)
        a, b = (pick(pl, view=v, corner=c.upper(), temp_c=t)[0] for v in ("sch", "pex"))
        axs[1, j].text(0.03, 0.05, f"PM {a['pm_deg']:.0f}$^\\circ$ $\\rightarrow$ {b['pm_deg']:.0f}$^\\circ$\n"
                                   f"GM {a['gm_db']:.0f} $\\rightarrow$ {b['gm_db']:.0f} dB",
                       transform=axs[1, j].transAxes, ha="left", va="bottom")
        axs[0, j].set_title(f"{c.upper()}, {t} °C".replace("-", "−"))
        axs[0, j].set(ylim=(-40, 140))
        axs[1, j].set(ylim=(-360, 10), xlabel="Frequency (Hz)", xlim=(1, 1e9))
        axs[1, j].set_yticks([-360, -270, -180, -90, 0])
        axs[1, j].set_xticks([1, 1e2, 1e4, 1e6, 1e8])
        axs[1, j].axhline(-180, color=GREY, lw=0.6, ls=":")
        axs[0, j].axhline(0, color=GREY, lw=0.6, ls=":")
        if j:
            axs[0, j].set_yticklabels([])
            axs[1, j].set_yticklabels([])
    axs[0, 0].set_ylabel("$|T|$ (dB)")
    axs[1, 0].set_ylabel("$\\angle T$ (deg)")
    for k, ax in enumerate(axs.flat):
        ax.text(0.97, 0.95, f"({'abcdef'[k]})", transform=ax.transAxes, ha="right", va="top")
    fig.tight_layout(h_pad=0.3, w_pad=0.4, rect=(0, 0, 1, 0.93))
    mf.top_legend(fig, *axs[0, 0].get_legend_handles_labels(), ncol=2, y=0.93)
    save(fig, "fig_v2_postlayout_bode.png")


def fig_postlayout_steps():
    fig, axs = plt.subplots(2, 3, figsize=(COL2, 3.7))
    for j, (c, t) in enumerate(PL_PTS):
        for view, (col, ls, mk, lab) in VIEW.items():
            d = mf.read(view_file("tran", view, c, t))
            axs[0, j].plot(d["time"] * 1e9 - 100, d["v(out)"], ls, color=col, lw=1.0, label=lab)
            tt, y = sc_edge(view_file("sc", view, c, t), 2)
            axs[1, j].plot(tt, y, ls, color=col, lw=1.0)
        d = mf.read(view_file("tran", "sch", c, t))
        axs[0, j].plot(d["time"] * 1e9 - 100, d["v(vicm)"], "-", color=GREY, lw=0.7, label="input")
        axs[0, j].set(xlim=(-20, 400), ylim=(0.7, 0.97), title=f"{c.upper()}, {t} °C".replace("-", "−"))
        axs[1, j].set(xlim=(-20, 400), ylim=(-0.08, 1.25), xlabel="Time after the step (ns)")
        if j:
            axs[0, j].set_yticklabels([])
            axs[1, j].set_yticklabels([])
    axs[0, 0].set_ylabel("Buffer $V_{out}$ (V)")
    axs[1, 0].set_ylabel("SC, normalised $V_{out}$")
    for k, ax in enumerate(axs.flat):
        ax.text(0.97, 0.05, f"({'abcdef'[k]})", transform=ax.transAxes, ha="right", va="bottom")
    fig.tight_layout(h_pad=0.4, w_pad=0.4, rect=(0, 0, 1, 0.93))
    mf.top_legend(fig, *axs[0, 0].get_legend_handles_labels(), ncol=3, y=0.93)
    save(fig, "fig_v2_postlayout_steps.png")


def fig_postlayout_pvt():
    pl = pl_rows()
    fig, axs = plt.subplots(3, 1, figsize=(COL2, 5.0), sharex=True)
    for ax, key, scale, lab in ((axs[0], "ugf_hz", 1e-6, "UGF (MHz)"), (axs[1], "pm_deg", 1, "Phase margin (deg)"),
                                (axs[2], "gm_db", 1, "Gain margin (dB)")):
        xs = mf.pvt_axis(ax, groups=ax is axs[2])
        for view, (col, ls, mk, vlab), off in (("sch", VIEW["sch"], -0.15), ("pex", VIEW["pex"], 0.15)):
            ys = [pick(pl, view=view, corner=c, temp_c=t)[0][key] * scale for c in CORNERS for t in TEMPS]
            ax.plot(np.array(xs) + off, ys, mk, color=col, ms=4.5, ls="none", label=vlab)
        ax.set_ylabel(lab)
    axs[0].set(ylim=(0, 25))
    axs[1].set(ylim=(30, 95))
    axs[2].set(ylim=(0, 40))
    axs[2].axhline(15, color=INK, lw=0.8, ls=":")
    axs[2].set_xlabel("Temperature (°C) and process corner, $V_{DD}$ = 1.65 V", labelpad=16)
    axs[0].legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, 1.0))
    for ax, s in zip(axs, "abc"):
        panel(ax, f"({s})")
    fig.tight_layout(h_pad=0.5)
    save(fig, "fig_v2_postlayout_pvt.png")


def fig_postlayout_sens():
    s = rows(RES / "postlayout_sensitivity.csv")
    pl = pl_rows()
    labels = list(dict.fromkeys(r["removed"] for r in s))
    fig, ax = plt.subplots(figsize=(COL2, 2.6))
    y = np.arange(len(labels) + 1)
    for (c, t), col, mk, off in ((("TT", 27), INK, "o", -0.15), (("SS", -40), BLUE, "s", 0.15)):
        full = pick(pl, view="pex", corner=c, temp_c=t)[0]["pm_deg"]
        vals = [full] + [pick(s, removed=l, corner=c, temp_c=t)[0]["pm_deg"] for l in labels]
        ax.barh(y + off, vals, height=0.28, color=col, alpha=0.8, label=f"{c}, {t} °C".replace("-", "−"))
        for yy, v in zip(y + off, vals):
            ax.text(v + 0.5, yy, f"{v:.1f}", va="center", ha="left", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(["full extraction"] + labels)
    ax.invert_yaxis()
    ax.set(xlabel="Post-layout phase margin (deg)", xlim=(30, 90), ylabel="Capacitances removed")
    ax.grid(axis="y", visible=False)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    mf.top_legend(fig, *ax.get_legend_handles_labels(), ncol=2, y=0.9)
    save(fig, "fig_v2_postlayout_sens.png")


def fig_tail_study():
    """SC settling tail after a 4-mV step versus the crossover of the regulation loop
    (sim/redesign/tail_study.py)."""
    f = RES / "tail_study.csv"
    if not f.exists():
        return
    s = rows(f)
    fig, (a, b) = plt.subplots(1, 2, figsize=(COL2, 2.7))
    for (c, t), col, mk in ((("tt", 27), INK, "o"), (("ff", 125), ORANGE, "D")):
        pts = sorted([r for r in s if r["corner"] == c and r["temp_c"] == t], key=lambda r: r["f_reg_hz"])
        fr = np.array([r["f_reg_hz"] for r in pts])
        a.loglog(fr / 1e3, [r["tail_uv"] for r in pts], "-", color=col, marker=mk, mfc="white",
                 label=f"{c.upper()}, {t} °C".replace("-", "\u2212"))
        a.loglog(fr / 1e3, [4e-3 * x / (0.5 * r["ugf_hz"]) * 1e6 for x, r in zip(fr, pts)], ":", color=col, lw=0.8)
        a.loglog(fr / 1e3, [4e-3 / (0.5 * 10 ** (r["afast_db"] / 20)) * 1e6 for r in pts], "--", color=col, lw=0.6)
    a.set(xlabel="Regulation-loop crossover (kHz)", ylabel="Tail after a 4-mV step (µV)", ylim=(0.5, 500))
    a.text(0.03, 0.97, "dotted: $\\Delta V f_{reg}/(\\beta f_{UGF})$\ndashed: $\\Delta V/(\\beta A_{fast})$",
           transform=a.transAxes, ha="left", va="top", fontsize=8, bbox=dict(fc="white", ec="none", pad=1.0))
    freg = {r["name"]: r["f_reg_hz"] for r in s if r["corner"] == "tt"}
    t0 = SC_EDGES[0][0]
    for name, col in (("fast", ORANGE), ("final", BLUE)):
        p = RES / f"tail_{name}_tt_27.dat"
        if p.exists():
            d = mf.read(p)
            tt = (d["time"] - t0) * 1e9
            m = (tt > -20) & (tt < 2000)
            v0 = np.interp(-1, tt, d["v(out)"])
            b.plot(tt[m], 1e6 * (d["v(out)"][m] - (v0 - 0.004)), "-", color=col, lw=1.0,
                   label=f"{freg[name] / 1e3:.3g}-kHz loop" + (" (RAMP_V2)" if name == "final" else ""))
    b.set(xlabel="Time after the 4-mV step (ns)", ylabel="Error (µV)", xlim=(-20, 2000), ylim=(-150, 150))
    b.axhline(0, color=GREY, lw=0.6, ls=":")
    panel(a, "(a)", right=True)
    a.texts[-1].set_position((0.985, 0.03))
    a.texts[-1].set_va("bottom")
    panel(b, "(b)", right=True)
    fig.tight_layout(w_pad=1.5, rect=(0, 0, 1, 0.9))
    h1, l1 = a.get_legend_handles_labels()
    h2, l2 = b.get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.9))
    save(fig, "fig_v2_tail_study.png")


if __name__ == "__main__":
    fig_bode_corners()
    fig_iq_temperature()
    fig_pvt_ugf_pm()
    fig_settling_pvt()
    fig_steps()
    fig_limit_cycle()
    fig_startup()
    fig_power()
    fig_psrr()
    if (RES / "mc_summary.csv").exists() and (RES / "mc_waves.npz").exists():
        fig_mc_offset_iq()
        fig_mc_perf()
        fig_mc_waves()
    if (RES / "postlayout_summary.csv").exists():
        fig_postlayout_bode()
        fig_postlayout_steps()
        fig_postlayout_pvt()
        fig_postlayout_sens()
    fig_tail_study()
