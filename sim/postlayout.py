#!/usr/bin/env python3
"""Schematic versus post-layout simulation of RAMP_LR (regulated bias, 1.65 V).

The post-layout netlist is magic's extraction of layout/RAMP_LR.gds (layout/run_pex.sh):
the devices as drawn plus 0.01 fF and larger area, fringe and coupling capacitances of
every net (no wire resistance).  For simulation it is turned into a library sub-circuit
RAMP_LR_PEX with
  * the same port order as the schematic RAMP_LR,
  * the same 0-V ammeter VIQ in the source connection of the output PMOS, and
  * a 1-TOhm resistor to ground on the nodes that only touch capacitors (e.g. the bodies
    of the rhigh resistors), which would otherwise leave the DC matrix singular.
Both views then run the testbenches of sim/ramp_pvt.py (operating point, loop gain, supply
rejection, buffer step, SC test) at the five corners and -40/27/125 degC.

Run sim/ramp_pvt.py and layout/run_pex.sh first.
A sensitivity run removes the parasitics of one net group at a time (TT/27 and SS/-40 degC).
Output: sim/results/postlayout_summary.csv, postlayout_sensitivity.csv and the post-layout waveforms
sim/results/{loop,psrr,tran,sc}_pex_<corner>_<T>.dat (the schematic ones are the *_reg_* files).
"""
import csv
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ramp_pvt as rp  # noqa: E402

PEX = rp.REPO / "layout" / "pex" / "RAMP_LR_pex.spice"
OUT = rp.BUILD / "postlayout"
PORTS = ["VDD", "GND", "IBIAS", "minus", "plus", "Vout"]


def pex_library() -> Path:
    text = PEX.read_text().replace("$", "_")
    cells = {m.group(1): (m.group(2).split(), m.group(3))
             for m in re.finditer(r"^\.subckt (\S+) (.*?)\n(.*?)^\.ends", text, re.M | re.S)}
    top_ports, body = cells.pop("RAMP_LR")
    assert sorted(p.lower() for p in top_ports) == sorted(p.lower() for p in PORTS), top_ports
    # ports of every cell that reach a device terminal (the rest only carry capacitance)
    dc_ports = {}
    devices = {}
    for name, (ports, cbody) in cells.items():
        devs = [l.split() for l in cbody.splitlines() if l.startswith("X")]
        terms = {t for d in devs for t in d[1:-1] if "=" not in t}
        dc_ports[name] = [p in terms for p in ports]
        devices[name] = devs
    lines, nets_dc, nets_all, n_iq = [], set(PORTS), set(), 0
    for line in body.splitlines():
        tok = line.split()
        if line.startswith("X") and tok[-1] in cells:
            cell, conn = tok[-1], tok[1:-1]
            ports = cells[cell][0]
            nets_all.update(conn)
            nets_dc.update(c for c, ok in zip(conn, dc_ports[cell]) if ok)
            pmap = dict(zip(ports, conn))
            for d in devices[cell]:
                dr, g, s, model = pmap.get(d[1]), pmap.get(d[2]), pmap.get(d[3]), d[5]
                # output PMOS (MP3): gate mp_dz, drain or source on Vout, the other on VDD
                if model == "sg13_hv_pmos" and g == "mp_dz" and {dr, s} == {"Vout", "VDD"}:
                    vdd_port = d[1] if dr == "VDD" else d[3]
                    conn = [("vdd_q" if (p == vdd_port and c == "VDD") else c) for p, c in zip(ports, conn)]
                    line = " ".join([tok[0]] + conn + [cell])
                    n_iq += 1
        elif line.startswith("C"):
            nets_all.update(tok[1:3])
        lines.append(line)
    assert n_iq, "output PMOS not found in the extracted netlist"
    floating = sorted(n for n in nets_all - nets_dc if n not in ("0", "GND"))
    lines.append("VIQ VDD vdd_q 0")
    lines += [f"RFLOAT{i} {n} GND 1T" for i, n in enumerate(floating)]
    sub = "\n".join(f".subckt {n} {' '.join(p)}\n{b}.ends\n" for n, (p, b) in cells.items())
    lib = (f"* RAMP_LR post-layout (magic PEX of layout/RAMP_LR.gds), built by sim/postlayout.py\n"
           f"* {n_iq} output-PMOS units on VIQ, {len(floating)} capacitor-only nodes tied to GND by 1 TOhm\n"
           f"{sub}\n.subckt RAMP_LR_PEX {' '.join(PORTS)}\n" + "\n".join(lines) + "\n.ends\n")
    f = OUT / "pex_lib.spice"
    f.write_text(lib)
    print(f"post-layout library: {len(cells)} cells, {n_iq} output-PMOS units, {len(floating)} floating nodes")
    return f


SENS = {"all parasitics removed": None, "Vo_STG1 (stage-1 output)": {"Vo_STG1"},
        "mp_dz, mn_dz (stage-2 outputs)": {"mp_dz", "mn_dz"}, "V1_CM (trip-point replica)": {"V1_CM"},
        "VCTRLP, VCTRLN": {"VCTRLP", "VCTRLN"}, "Vout": {"Vout"}}


def sensitivity(pexlib: Path) -> list:
    """Loop gain at TT/27 degC and SS/-40 degC with the parasitic capacitors of one net group
    removed (all of them for the first entry): which routing costs the phase margin."""
    src = pexlib.read_text()
    i = src.index(".subckt RAMP_LR_PEX")
    cells, top = src[:i], src[i:]
    jobs = []
    for k, (label, nets) in enumerate(SENS.items()):
        if nets is None:
            text = re.sub(r"^C\d+ .*\n", "", cells, flags=re.M) + re.sub(r"^C\S* .*\n", "", top, flags=re.M)
        else:
            text = cells + "".join(l for l in top.splitlines(True)
                                   if not (l.startswith("C") and set(l.split()[1:3]) & nets))
        lib = OUT / f"pex_sens{k}.spice"
        lib.write_text(text)
        for c, t in (("mos_tt", 27), ("mos_ss", -40)):
            jobs.append((label, c, t, rp.testbench(f"sens{k}_{c[4:]}_{t}", "RAMP_LR_PEX", c, t, rp.VDD0,
                                                   transient=False, psrr=False, netlib=lib, build=OUT)))
    with ThreadPoolExecutor(max_workers=rp.os.cpu_count()) as ex:
        assert all(ex.map(lambda j: rp.ngspice(j[3]), jobs))
    return [dict(removed=label, corner=c[4:].upper(), temp_c=t, **rp.loop_metrics(d.parent))
            for label, c, t, d in jobs]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pexlib = pex_library()
    views = {"sch": ("RAMP_LR", None), "pex": ("RAMP_LR_PEX", pexlib)}
    jobs = []
    for view, (sub, lib) in views.items():
        for c in rp.CORNERS:
            for t in rp.TEMPS:
                tag = f"{view}_{c[4:]}_{t}"
                jobs.append((view, c, t, "tb", rp.testbench(tag, sub, c, t, rp.VDD0, netlib=lib, build=OUT)))
                jobs.append((view, c, t, "sc", rp.sc_deck("sc_" + tag, sub, c, t, rp.VDD0, 0, 0,
                                                         netlib=lib, build=OUT)))
    with ThreadPoolExecutor(max_workers=rp.os.cpu_count()) as ex:
        ok = list(ex.map(lambda j: rp.ngspice(j[4]), jobs))
    bad = [j[4].parent.name for j, k in zip(jobs, ok) if not k]
    assert not bad, f"ngspice failed: {bad}"
    rows = {}
    for view, c, t, kind, deck in jobs:
        d = deck.parent
        row = rows.setdefault((view, c, t), dict(view=view, corner=c[4:].upper(), temp_c=t, vdd=rp.VDD0))
        if kind == "tb":
            row.update(rp.op_metrics(d))
            row.update(rp.loop_metrics(d))
            row.update(rp.tran_metrics(d))
            row["offset_mv"] = 1e3 * (row["vout"] - rp.VCM)
            if view == "pex":
                tag = f"pex_{c[4:]}_{t}"
                shutil.copy(d / "loop.dat", rp.RESULTS / f"loop_{tag}.dat")
                if t == 27:
                    shutil.copy(d / "psrr.dat", rp.RESULTS / f"psrr_{tag}.dat")
                rp.save_resampled(d / "tran.dat", rp.RESULTS / f"tran_{tag}.dat", 0.5e-9)
        else:
            row.update(rp.sc_metrics(d))
            if view == "pex":
                rp.save_resampled(d / "sc.dat", rp.RESULTS / f"sc_pex_{c[4:]}_{t}.dat", 2e-9,
                                  keep=("time", "v(out)"), fmt="%.9g")
    rows = list(rows.values())
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(rp.RESULTS / "postlayout_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    sens = sensitivity(pexlib)
    with open(rp.RESULTS / "postlayout_sensitivity.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sens[0]))
        w.writeheader()
        for r in sens:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    for r in sens:
        print(f"parasitics of {r['removed']:32s} removed, {r['corner']} {r['temp_c']:4}: "
              f"UGF {r['ugf_hz'] / 1e6:6.2f} MHz, PM {r['pm_deg']:5.1f} deg")
    print(f"{'corner':6} {'T':>4}  {'I_Q sch/pex uA':>15} {'UGF sch/pex MHz':>16} {'PM sch/pex deg':>15} "
          f"{'ts0.1% sch/pex ns':>18} {'SC err250 S sch/pex %':>22}")
    for c in rp.CORNERS:
        for t in rp.TEMPS:
            a, b = (next(r for r in rows if r["view"] == v and r["corner"] == c[4:].upper() and r["temp_c"] == t)
                    for v in ("sch", "pex"))
            print(f"{c[4:]:6} {t:4}  {a['iq_ua']:7.3f}/{b['iq_ua']:<7.3f} {a['ugf_hz'] / 1e6:7.2f}/{b['ugf_hz'] / 1e6:<8.2f} "
                  f"{a['pm_deg']:6.1f}/{b['pm_deg']:<8.1f} {a['ts01_rise_ns']:8.1f}/{b['ts01_rise_ns']:<9.1f} "
                  f"{a['sc_err250_Sr_pct']:9.3f}/{b['sc_err250_Sr_pct']:<9.3f}")


if __name__ == "__main__":
    main()
