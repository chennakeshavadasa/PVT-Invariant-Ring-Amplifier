# Figures reproduced from the Venkatachala (2019) dissertation

The images in this directory are reproduced from the following dissertation for use in this repository's report:

> P. K. Venkatachala, "Design Considerations and Circuit Techniques for Robust ringamps," Ph.D. dissertation, Oregon State Univ., Corvallis, OR, USA, 2019.

All copyright remains with the original author. Each figure was rendered from the PDF
(`Thesis/VenkatachalaPraveenkumar2019.pdf`) at 300 dpi and cropped to the drawing only, so the thesis
caption, page number and body text are not included. Each image has a 20 px white margin.
"PDF page" is the 1-based page index in the PDF file. "Thesis page" is the page number printed in the
thesis (PDF page minus 13).

| File | Thesis figure | Thesis page | PDF page | Original caption (verbatim) |
|---|---|---|---|---|
| `fig1_1_ringamp_basic.png` | Fig. 1.1 | 1 (not printed on the page; from the List of Figures) | 14 | Ringamp: Basic structure and operation |
| `fig2_1_sc_amplifier.png` | Fig. 2.1 | 8 | 21 | Switched capacitor amplifier setup |
| `fig2_9_ringamp_schematic.png` | Fig. 2.9 | 14 | 27 | Schematic of a ringamp |
| `fig2_10_ringamp_iv.png` | Fig. 2.10 | 15 | 28 | I-V characteristics of a ringamp |
| `fig2_11_vv_transfer.png` | Fig. 2.11 | 15 | 28 | V-V transfer characteristics of the first two stages of a ringamp |
| `fig2_12_ringamp_transient.png` | Fig. 2.12 | 17 | 30 | Ringamp transient response (a) Differential virtual ground node (b) Single-ended output voltage of the second-stage (b) Differential output current (c) Differential Output Voltage |
| `fig2_13_ringamp_overshoot.png` | Fig. 2.13 | 19 | 32 | Ringamp transient response with overshoot (a) Differential virtual ground node (b) Single-ended output voltage of the second-stage (b) Differential output current (c) Differential Output Voltage |
| `fig2_18_small_signal_model.png` | Fig. 2.18 | 28 | 41 | RC model for initial large-signal step response. (a) Positive output step (b) Negative output step [see note 1] |
| `fig2_19_rc_model.png` | Fig. 2.19 | 33 | 46 | RC model for initial large-signal step response. (a) Positive output step (b) Negative output step |
| `fig2_20_settling_vs_ota.png` | Fig. 2.20 | 40 | 53 | Settling response for a ringamp compared to single-stage OTA (y-axis normalized to final value) |
| `fig2_21_current_starved_ringamp.png` | Fig. 2.21 | 47 | 60 | Current-starved-inverter based ring-amplifier used for design example. (Single-ended schematic shown for simplicity. First-stage biased with tail current sources for differential implementation) |
| `fig2_22_settling_example.png` | Fig. 2.22 | 48 | 61 | Settling response of the ring-amplifier. (a) Differential output voltage step of 800mV (b) Dynamic and static errors illustrating the fast large-signal slope and slow small-signal slope sections (c) Derivative of output voltage representing the exponential decay of current through the load capacitor |
| `fig3_1_traditional_ringamp.png` | Fig. 3.1 | 51 | 64 | Traditional ringamp in a switched capacitor negative feedback |
| `fig3_2_resistor_deadzone.png` | Fig. 3.2 | 52 | 65 | Ringamp using a resistor for deadzone biasing |
| `fig3_3_current_starved_deadzone.png` | Fig. 3.3 | 53 | 66 | Ringamp using current starved inverters for deadzone biasing. |
| `fig3_4_sc_setup.png` | Fig. 3.4 | 53 | 66 | Switched capacitor amplifier setup |
| `fig3_5_transient_fixed_bias.png` | Fig. 3.5 | 56 | 69 | Transient response with fixed deadzone bias |
| `fig3_6_deadzone_regulation.png` | Fig. 3.6 | 57 | 70 | Deadzone regulation circuit for current starved inverter based ring amplifier |
| `fig3_7_transient_regulated.png` | Fig. 3.7 | 60 | 73 | Transient response with the deadzone regulation circuit |
| `fig4_1_passive_compensation.png` | Fig. 4.1 | 63 | 76 | Passive compensation of ring amplifier using switches in the feedback network |

Captions spread over several lines in the PDF were joined with spaces, and words that LaTeX split across a line break were rejoined ("out-put" became "output" in Fig. 2.13, "ring am-plifier" became "ring amplifier" in Fig. 3.6). Nothing else was changed, including errors in the original.

## Notes

1. **Fig. 2.18 caption error in the original.** The thesis prints the same caption for Fig. 2.18 and Fig. 2.19, both in the figure itself and in the List of Figures. The Fig. 2.18 drawing is the small-signal model of the three-stage ringamp (Stage1 to Stage3 with gm, rds, cgs, cgd, cdd, plus CS, CF and CL), as the body text says: "Fig. 2.18, shows the small signal model of a ringamp during the charge transfer phase of a SC amplifier." A suitable caption for the report: *"Small-signal model of a ringamp during the charge-transfer phase of an SC amplifier."*
2. **Figs. 2.12 and 2.13 panel letters.** The drawings label four panels (a) to (d), but the original captions list them as (a), (b), (b), (c). In the drawings, (c) is the output current and (d) is the output voltage.
3. **Raster content.** Most figures are vector line art rendered at 300 dpi. The exceptions:
   - `fig2_20_settling_vs_ota.png` comes from a single embedded JPEG (about 227 ppi), including all of its text. It shows slight JPEG compression artefacts and is the lowest-quality image in the set.
   - In `fig2_10_ringamp_iv.png` and `fig2_11_vv_transfer.png`, the curves and grid lines are embedded raster images (about 354 ppi, good quality). The axis labels and annotations are vector text.
   - `fig2_22_settling_example.png` is vector, but each panel sits on a blank embedded raster background. That background left thin light-grey 1 px frame lines at the panel edges, and these were removed during cropping. The "(a)/(b)/(c)" panel labels use a different font from the axis labels in the original as well.
