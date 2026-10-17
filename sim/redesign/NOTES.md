# RAMP v2 redesign — working notes

Work in progress; the results in the main README still describe RAMP_LR (v1). These scripts are the
study that leads to v2. Run from this directory; outputs go to `sim/build/redesign*`.

| Script | What it does |
|:--|:--|
| `stages.py` | Stage-by-stage gain, bandwidth and phase at crossover from one loop-broken AC run |
| `variants.py` | v1 netlist variants (stage-2 strength, MP3 size, PTAT, R, I_Q) with a lumped post-layout proxy |
| `mc_attr.py` | Monte Carlo with mismatch enabled in one device group at a time (PDK `mm_ok` switch) |
| `v2.py` | Parametric v2 netlist (PMOS-input stage 1, direct deadzone regulation, optional cascode, CMFB reference options, offset servo) and its evaluation |
| `pgrid.py` | Runs many `v2.py` configurations in one process pool and ranks them |

## Findings on v1 (RAMP_LR)

1. **Oscillation at SS, −40 °C (post-layout).** The pole at the MP3 gate (`mp_dz`, driven by one
   minimum-size PMOS) is at 24 MHz — below the 30-MHz crossover already in the schematic (−52°).
   The layout adds 19 fF on `Vo_STG1` (stage-1 pole 188 → 56 MHz) and loads `mp_dz` (24 → 16 MHz):
   PM 18°, GM 4.8 dB, and every step ≥ 10 mV ends in a 43-MHz limit cycle.
2. **Offset σ = 8.1 mV** (mismatch, TT): stage-1 pair 4.5 mV, stage 2 4.6 mV, stage-2 replica 4.6 mV,
   CMFB 2.3 mV, loads 2.1 mV, bias 1.5 mV. The input pair is small and stage-1 gain is only 3–5, so the
   trip-point mismatch of the minimum-size stage-2 inverters reaches the input almost undivided.
3. **I_Q spread (σ of log10 I_Q ≈ 1.8)** comes only from stage 2 and its replica: the loop regulates the
   replica, not the signal path, and stage 2 amplifies the replica/signal-path trip mismatch ~20×.

## v2 status (prototype `v2.py`, post-layout proxy: 12/10/8 fF on Vo_STG1/mp_dz/mn_dz)

Main loop — done (configuration `chk.BASE` with `cmfb="diode"`):

| | Result |
|:--|:--|
| Topology | PMOS input pair 8 × 2.5/0.5 µm, NMOS loads, 25 kΩ rhigh loads, 40 µA tail (wide 4/1 tail devices), diode CMFB |
| Stage 2 | MN3-gate inverter ×3; MP3-gate inverter 1 P : 6 N : 6 starve (L = 0.3 µm) |
| Output | MN3 4 × 1.15/0.5 µm (was 2.3/1), MP3 unchanged |
| Reference | constant-gm I_BIAS ∝ T/R (ideal input; tracks rhigh) — flattens the crossover over PVT |
| UGF at TT | 18.1 MHz |
| Worst PM / GM (7 corners) | 52° / 15.9 dB, no limit cycle for 10–200-mV steps |
| Supply current | 153 µA |
| Systematic offset | ≤ 0.9 mV over corners (with servo) |
| Buffer gain error | 0.6–1.3 % at hot corners (v1: 1.46 %); not present in SC use (fixed input CM) |

With ideal slow loops: I_Q P5–P95 1.9–2.3 µA under mismatch (σ ≈ 17–20 %), offset σ ≈ 1.6 mV.

Open:
* **Regulation integrator.** The transistor-level two-stage Miller integrator works, but the control path
  VCTRLN → V_GP has a gain of ~12, so even a 0.33-µA integrator with 1 pF crosses over at 3–18 MHz
  (unstable against the main loop). Needed: ≤ ~300 kHz → weaker control path (partial starve control) or a
  tens-of-nA integrator.
* **Offset servo** (transistor level): stable, 72–118 kHz, PM 86°; DC gain 37–45 dB (enough).
* Then: VDD ± 5 %, Monte Carlo (process / mismatch / both), schematic, layout, extraction, report.

Rejected on the way: high stage-1 gain (A1 ≥ 10, with or without cascode) — large-signal limit cycle at cold
corners even with 70° PM; high-gain CMFB — its loop shares Vo_STG1 with the main loop and is unstable in every
variant tried (net3 or net2 sensing, split load gates); CMFB referenced to a low-passed Vo_STG1 — bistable.
