import re, sys, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ramp_pvt as rp, montecarlo as mc
OUT = Path(__file__).resolve().parents[1] / "build" / "redesign_attr"; OUT.mkdir(parents=True, exist_ok=True)
SPI = (Path.home() / ".spiceinit").read_text() + "\nset num_threads=1\n"
LIB = Path(sys.argv[1]) if len(sys.argv) > 1 else rp.BUILD / "lr_lib.spice"
N = 150
INST = {"BIAS_LR": "xb", "STG1_LR": "x1", "STG1_CM_LR": "x4", "STG2_LR": "x2", "STG2_REPLICA_LR": "x3",
        "POTA_LR": "x3.x1", "NOTA_LR": "x3.x2", "RAMP_LR": "", "DUMMY_LR": "xd"}
GROUPS = {
    "stage-1 input pair MN1/MN2": lambda s, d: s == "STG1_LR" and d in ("XMN1", "XMN2"),
    "stage-1 loads MP1/MP2": lambda s, d: s == "STG1_LR" and d in ("XMP1", "XMP2"),
    "CMFB pair, diodes, rhigh": lambda s, d: s == "STG1_LR" and d in ("XMC1", "XMC2", "XMPC1", "XMPC2", "XR1", "XR3"),
    "stage 2 (signal path)": lambda s, d: s == "STG2_LR",
    "trip-point replica": lambda s, d: s == "STG1_CM_LR",
    "stage-2 replica (loop)": lambda s, d: s == "STG2_REPLICA_LR" and "_R " not in d + " " and d.startswith("XM") and not d.endswith("_R") and d not in ("XMCN", "XMCP"),
    "MP3/MN3 and MP_R/MN_R": lambda s, d: (s == "RAMP_LR" and d in ("XM1", "XM2")) or (s == "STG2_REPLICA_LR" and d.endswith("_R")),
    "NOTA/POTA": lambda s, d: s in ("POTA_LR", "NOTA_LR"),
    "bias mirrors": lambda s, d: s == "BIAS_LR",
}

def lib_for(group):
    text = LIB.read_text()
    out, sub = [], None
    for line in text.splitlines():
        m = re.match(r"^\.subckt (\S+)", line)
        if m:
            sub = m.group(1)
        elif line.startswith(".ends"):
            sub = None
        elif sub and re.match(r"^X\S+ ", line) and (" sg13_" in line or " rhigh " in line or " cap_cmim " in line):
            dev = line.split()[0]
            keep = group == "all" or GROUPS[group](sub, dev)
            if not keep:
                line += " mm_ok=0"
        out.append(line)
    f = OUT / f"lib_{abs(hash(group))}.spice"; f.write_text("\n".join(out) + "\n"); return f

def run(args):
    group, lib, k = args
    d = OUT / f"{abs(hash(group))}_{k}"; d.mkdir(exist_ok=True); (d / ".spiceinit").write_text(SPI)
    (d / "tb.spice").write_text(f"""* attr
.options seed={k + 1}
.include {lib}
{mc.SETS['mismatch']}.temp 27
x1 VDD GND IBIAS VICM out out RAMP_LR
I_B VDD IBIAS 1u
V1 VICM GND dc 0.825
V2 VDD GND dc 1.65
.control
set wr_singlescale
set wr_vecnames
op
wrdata {d}/op.dat v(out) i(v.x1.viq)
quit
.endc
.end
""")
    subprocess.run(["ngspice", "-b", "tb.spice"], cwd=d, capture_output=True)
    try:
        o = rp.read(d / "op.dat"); return group, 1e3 * (float(o["v(out)"][0]) - 0.825), 1e6 * float(o["i(v.x1.viq)"][0])
    except Exception:
        return group, np.nan, np.nan

groups = list(GROUPS) + ["all"]
libs = {g: lib_for(g) for g in groups}
jobs = [(g, libs[g], k) for g in groups for k in range(N)]
with ThreadPoolExecutor(14) as ex:
    res = list(ex.map(run, jobs))
print(f"{'mismatch only in':30s} {'sigma(offset) mV':>16s} {'IQ P5..P95 (uA)':>18s} {'sigma(log10 IQ)':>15s} {'IQ in +-25%':>11s}")
for g in groups:
    off = np.array([r[1] for r in res if r[0] == g]); iq = np.array([r[2] for r in res if r[0] == g])
    ok = np.isfinite(off)
    li = np.log10(np.clip(iq[ok], 1e-6, None))
    print(f"{g:30s} {np.std(off[ok]):16.2f} {np.percentile(iq[ok],5):8.3g}..{np.percentile(iq[ok],95):<8.3g} {np.std(li):15.2f} {np.mean(np.abs(iq[ok]/4.22-1)<0.25)*100:10.0f}%")
