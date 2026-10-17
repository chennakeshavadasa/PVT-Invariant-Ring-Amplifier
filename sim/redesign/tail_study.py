"""Settling tail of the SC amplifier versus the crossover of the I_Q regulation loop (v2 prototype).

The regulation integrator integrates the swing of the MP3 gate during every step; the correction that
follows moves the offset and leaves a tail on the output.  This study varies only the tail current of
the regulation integrator (parallel or series units of the nA divider, 4-pF Miller capacitor) and
records, at TT 27 degC and FF 125 degC:
  f_reg   crossover of the regulation loop (regloop.py),
  tail    largest |error| 0.2-1.9 us after a 4-mV SC step (sctest.py deck),
  ugf_hz  crossover of the main loop, and A_fast, its DC gain with the slow loops frozen (fastgain.py).
Output: sim/results/v2/tail_study.csv and two waveforms (tail_fast_*.dat: the fastest integrator, about the
85-nA tail of the first transistor-level version; tail_final_*.dat: RAMP_V2).
"""
import csv
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chk  # noqa: E402
import fastgain  # noqa: E402
import regloop  # noqa: E402
import sctest  # noqa: E402
import v2  # noqa: E402

RES = Path(__file__).resolve().parents[1] / "results" / "v2"
FINAL = json.load(open(Path(__file__).resolve().parent / "v2_final.json"))
VARIANTS = {"fast": "p:16", "p4": "p:4", "p1": "p:1", "u2": "u:2", "final": "u:6", "u12": "u:12"}
CORNERS = (("mos_tt", 27), ("mos_ff", 125))


def one(job):
    name, tail, (c, t) = job
    p = dict(chk.BASE, **dict(FINAL, reg_l=tail))
    tag = f"ts_{name}"
    lm = regloop.loop_at(p, tag, c, t, "reg")
    f = v2.with_par(v2.lib(p, tag + "_sc"))
    d = v2.OUT / f"{tag}_sc_{c[4:]}_{t}"
    v2.run(d, sctest.sc_deck(f, d, c, t, ptat=p.get("ptat")))
    r = v2.rp.read(d / "sc.dat")
    tt, v = r["time"], r["v(out)"]
    t0, dv, _ = v2.rp.SC_EDGES[0]
    target = np.interp(t0 - 1e-9, tt, v) - dv
    m = (tt > t0 + 200e-9) & (tt < t0 + 1900e-9)
    tail_uv = 1e6 * np.max(np.abs(v[m] - target))
    fg = fastgain.run(p, tag + "_fg", c, t)
    return dict(name=name, reg_tail=tail, corner=c[4:], temp_c=t, f_reg_hz=lm["ugf_hz"], reg_pm_deg=lm["pm_deg"],
                tail_uv=tail_uv, afast_db=fg["T"]), d


def main():
    jobs = [(n, tl, ct) for n, tl in VARIANTS.items() for ct in CORNERS]
    with ThreadPoolExecutor(10) as ex:
        res = list(ex.map(one, jobs))
    # main-loop crossover (schematic + proxy) from one loop-gain run per corner
    ugf = {}
    for c, t in CORNERS:
        out, _ = v2.evaluate(dict(chk.BASE, **FINAL), "ts_ugf", corners=((c, t),))
        ugf[(c[4:], t)] = out[(c, t)]["ugf"] * 1e6
    rows = []
    for (row, d) in res:
        row["ugf_hz"] = ugf[(row["corner"], row["temp_c"])]
        rows.append(row)
        if row["name"] in ("fast", "final"):
            r = v2.rp.read(d / "sc.dat")
            m = r["time"] < 2.2e-6
            np.savetxt(RES / f"tail_{row['name']}_{row['corner']}_{row['temp_c']}.dat",
                       np.column_stack([r["time"][m], r["v(out)"][m]]), fmt="%.10g", header="time v(out)", comments="")
    with open(RES / "tail_study.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    for r in rows:
        print(f"{r['name']:6} {r['reg_tail']:5} {r['corner']} {r['temp_c']:4}: f_reg {r['f_reg_hz'] / 1e3:8.2f} kHz "
              f"tail {r['tail_uv']:7.2f} uV  A_fast {r['afast_db']:.1f} dB  UGF {r['ugf_hz'] / 1e6:.1f} MHz")


if __name__ == "__main__":
    main()
