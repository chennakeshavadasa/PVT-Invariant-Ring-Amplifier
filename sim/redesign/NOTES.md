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

## v2 direction (so far)

* PMOS input pair (lv PMOS matches 1.8× better per area; NMOS pair is in triode at FF 125 °C), NMOS loads,
  PMOS-pair CMFB, stage-1 load 25 kΩ, tail 40 µA.
* Direct deadzone regulation of the signal-path MP3 gate (sensed through 1 MΩ), replica removed:
  I_Q σ/mean ≈ 17–20 % under mismatch instead of five decades.
* PTAT reference: removes the cold-corner crossover rise (constant g_m3).
* Offset servo: integrates the stage-1 differential output and trims the CMFB reference (bounded range):
  systematic offset ≈ 0.1–0.4 mV, mismatch σ ≈ 1.6 mV where the trim range suffices.
* Rejected: high stage-1 gain (A1 ≥ 10) — it shrinks the input-referred deadzone and creates a
  large-signal limit cycle at cold corners even with 70° PM; CMFB referenced to a low-passed Vo_STG1 —
  bistable (dead state).

Still to do: transistor-level regulation OTA and servo (nA transconductors, integrating capacitors),
trim range, full PVT/VDD/Monte Carlo verification, then schematic, layout, extraction and the report.
