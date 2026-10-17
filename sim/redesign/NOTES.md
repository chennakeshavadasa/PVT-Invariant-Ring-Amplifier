# RAMP v2 redesign — working notes

The final design and its verification are in the main README (RAMP_V2, Sections V-VII). These scripts are the
study that leads to v2. Run from this directory; outputs go to `sim/build/redesign*`.

| Script | What it does |
|:--|:--|
| `stages.py` | Stage-by-stage gain, bandwidth and phase at crossover from one loop-broken AC run |
| `variants.py` | v1 netlist variants (stage-2 strength, MP3 size, PTAT, R, I_Q) with a lumped post-layout proxy |
| `mc_attr.py` | Monte Carlo with mismatch enabled in one device group at a time (PDK `mm_ok` switch) |
| `v2.py` | Parametric v2 netlist (PMOS-input stage 1, direct deadzone regulation, optional cascode, CMFB reference options, offset servo) and its evaluation |
| `pgrid.py` | Runs many `v2.py` configurations in one process pool and ranks them |
| `chk.py`, `dcsw.py`, `cmloop.py`, `regloop.py` | Corner check of one configuration; DC input sweep (gain error); CMFB loop gain; regulation/servo loop gains |
| `grid*.py`, `range.py`, `servo_*.py`, `bw2.py` | The parameter studies in the order they were run (each prints one line per configuration) |

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

## v2 status (prototype `v2.py`, parameters in `v2_final.json`, post-layout proxy 12/10/8 fF)

Frozen v2 (`chk.BASE` + `v2_final.json`):

| | Result |
|:--|:--|
| Stage 1 | PMOS pair 16 x 2.5/0.5 um per side, 40 uA tail; NMOS loads 4 x 1/2 um; 17-kOhm rhigh loads; diode CMFB |
| Stage 2 / output | as BASE; MN3 4 x 1.15/1.0 um (L = 1 um adds 5 dB of fast-loop DC gain), MP3 4 x 4.5/0.5 um |
| Reference | constant-gm I_BIAS proportional to T/R (ideal input, tracks rhigh) |
| I_Q regulation | MP3 gate (via R_S = 510 kOhm) vs. MP_R (2 fingers, 2 x I_BIAS); two-stage Miller integrator, hv devices, 4/4-um pair, 0.9-nA tail (6 series hv units on the nA divider), 4-pF MIM; crossover 1.0-4.0 kHz, PM >= 88.7 deg |
| Offset servo | integrates Vo1 - net2, trims V1_CM through 510 k / 68 k; hv 3/3-um pair, 1.7-nA tail, 1-pF MIM; crossover 0.5-1.3 kHz |
| nA divider | I_BIAS -> 13 hv PMOS 1/1 (77 nA) -> 14 hv NMOS 0.3/2 units (5.5 nA each); hv units keep the ratio within +-8 % (lv units at FF 125 degC pass nA at V_GS = 45 mV and are off by 1.7x) |
| Main loop (7 corners) | PM >= 54 deg, GM >= 14.6 dB, UGF 14.2 MHz TT (max 18.2), buffer ts(0.1 %) <= 119 ns, systematic offset <= 0.23 mV, 157 uA |
| SC, 200-mV step | error at 250 ns <= 0.055 % (FF 125 degC: 0.13 %) |
| Monte Carlo (TT, 300 samples per set, xschem netlist) | offset sigma 1.53 mV (process + mismatch, +-3 sigma -4.4 ... +4.8 mV), I_Q sigma/mean 15 %, PM >= 64.8 deg |
| Start-up | the slow loops settle in about 1 ms from power-up |

Why the slow loops are slow: a continuous-time loop that moves the offset or the deadzone integrates the transient
excursion of the node it senses and leaves a settling tail. Above the fast loop's own pole (5-30 kHz) the tail is
about step x f_slow / (beta x f_UGF); below it the error between fast settling and slow-loop convergence is the fast
loop's DC gain, 1 / (beta x A_fast). A_fast (slow loops frozen, `fastgain.py`) is 68 dB at FF 125 degC and 82 dB at
SS -40 degC; it sets the SC accuracy at hot corners.

Known limitation: in the unity-gain buffer the fast loop has a common-mode-dependent error (about 1 % of an input-CM
change) that only the slow servo removes; the DC transfer is exact (`dcsw2.py`), and the SC configuration (fixed
input CM) does not see it.

Scripts added for this step: `sctest.py` (SC test), `sc_diag.py` (tail diagnosis), `rl_scan.py` (slow-loop gains),
`iprobe.py` (nA currents), `fastgain.py` (fast-loop stage gains), `lctest.py` (limit-cycle steps), `dcsw2.py`,
`mc_attr2.py` (mismatch attribution), `startup.py` (power-up).

Rejected on the way: high stage-1 gain (A1 >= 10, with or without cascode) - large-signal limit cycle at cold
corners even with 70 deg PM; high-gain CMFB - its loop shares Vo_STG1 with the main loop and is unstable in every
variant tried; CMFB referenced to a low-passed Vo_STG1 - bistable; integrators of tens of nA - regulation tail of
2 % after a 4-mV SC step; lv devices at nA currents - leakage-dependent offsets at 125 degC; longer stage-1 loads or
load degeneration - GM below 12.5 dB.
