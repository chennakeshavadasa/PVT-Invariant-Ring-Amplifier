import re, sys, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ramp_pvt as rp
OUT = Path(__file__).resolve().parents[1] / "build" / "redesign_stages"
OUT.mkdir(parents=True, exist_ok=True)
SPI = (Path.home() / ".spiceinit").read_text() + "\nset num_threads=1\n"
BASE = (rp.BUILD / "lr_lib.spice").read_text()

def setm(text, sub, dev, m):
    blk = re.search(rf"^\.subckt {sub} .*?^\.ends", text, re.M | re.S).group(0)
    new = re.sub(rf"^(X{dev} .*? ng=1)( m=\d+)?$", rf"\1 m={m}", blk, flags=re.M)
    assert new != blk or f"m={m}" in blk, (sub, dev)
    return text.replace(blk, new)

def setw(text, line_start, w):
    out, n = re.subn(rf"^({re.escape(line_start)} .*? )w=[0-9.]+u", rf"\g<1>w={w}u", text, flags=re.M)
    assert n, line_start
    return out

def variant(name):
    t = BASE
    k = {"p2": 2, "p3": 3}.get(name.split("+")[0], 1) if name.startswith("p") else 1
    for part in name.split("+"):
        if part in ("p2", "p3"):
            kk = int(part[1])
            for sub in ("STG2_LR", "STG2_REPLICA_LR"):
                for dev in ("MP_STG2_3P2", "MP_STG2_3P1", "MN_DZ_STG2_3P"):
                    t = setm(t, sub, dev, kk)
            for dev in ("M12", "M13", "M14"):
                t = setm(t, "STG1_CM_LR", dev, kk)
        if part == "mp3h":      # MP3 and its replica MP_R at half width
            t = setw(t, "XM2 Vout mp_dz vdd_q VDD", 2.25)
            t = setw(t, "XMP_STG2_3P_R irn irn VDD VDD", 2.25)
        if part == "r50":       # stage-1 sense/load resistors 100k -> 50k
            t = re.sub(r"(rhigh w=0.5e-6 l=)33.7e-6", r"\g<1>16.85e-6", t)
            assert "l=16.85e-6" in t, "rhigh"
        if part == "n2":        # VDZN inverter x2
            for sub in ("STG2_LR", "STG2_REPLICA_LR"):
                for dev, m in (("MN_STG2_3N1", 2), ("MN_STG2_3P1", 6), ("MP_DZ_STG2_3N", 10)):
                    t = setm(t, sub, dev, m)
            for dev, m in (("M9", 2), ("M10", 6), ("M11", 10)):
                t = setm(t, "STG1_CM_LR", dev, m)
    f = OUT / f"lib_{name}.spice"; f.write_text(t); return f

PAR = "Cp1 Vo_STG1 GND 19f\nCp2 mp_dz GND 14f\nCp3 mn_dz GND 10f\n"


def with_par(lib):
    t = Path(lib).read_text()
    blk = re.search(r"^\.subckt RAMP_LR .*?^\.ends", t, re.M | re.S).group(0)
    f = Path(str(lib).replace(".spice", "_par.spice"))
    f.write_text(t.replace(blk, blk.replace(".ends", PAR + ".ends")))
    return f

def job(args):
    name, lib, par, corner, temp = args
    if par:
        lib = with_par(lib)
    ibias = rp.ibias_src(ptat="ptat" in name.split("+")).replace("1u", "0.5u") if "ib05" in name.split("+") \
        else rp.ibias_src(ptat="ptat" in name.split("+"))
    tag = f"{name}_{'par' if par else 'sch'}_{corner[4:]}_{temp}"
    d = OUT / tag; d.mkdir(exist_ok=True); (d / ".spiceinit").write_text(SPI)
    lo, hi = 0.725, 0.925
    (d / "tb.spice").write_text(f"""* {tag}
.include {lib}
{rp.models(corner)}.temp {temp}
x1 VDD GND IBIAS VICM inp out RAMP_LR
{ibias}
V1 VICM GND dc 0.825 ac 0 pwl(0 {lo} 100n {lo} 101n {hi} 1u {hi})
V2 VDD GND dc 1.65
C1 out GND 50p
Vprobe2 probe inp 0
Vprobe1 probe out dc 0 ac 1
Iprobe1 GND probe dc 0 ac 0
.control
set wr_singlescale
set wr_vecnames
op
wrdata {d}/op.dat v(out) i(v.x1.viq) i(v2)
{rp.CTRL_AC.format(d=d)}
alter @vprobe1[acmag]=0
tran 0.1n 1.6u 0 0.25n
wrdata {d}/tran.dat v(out)
quit
.endc
.end
""")
    subprocess.run(["ngspice", "-b", "tb.spice"], cwd=d, capture_output=True)
    try:
        lm = rp.loop_metrics(d)
        op = rp.read(d / "op.dat"); tr = rp.read(d / "tran.dat")
        t, v = tr["time"], tr["v(out)"]
        final = v[-1]
        err = np.abs(v - final) / 0.2
        m = t > 100e-9
        bad = np.where(err[m] > 1e-3)[0]
        ts = (t[m][bad[-1]] - 100e-9) * 1e9 if len(bad) else 0.0
        osc = np.ptp(v[t > 1.3e-6]) * 1e3
        return name, par, corner, temp, lm["ugf_hz"] / 1e6, lm["pm_deg"], lm["gm_db"], float(op["i(v.x1.viq)"][0]) * 1e6, \
            -float(op["i(v2)"][0]) * 1e6, ts, osc
    except Exception as e:
        return name, par, corner, temp, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

if __name__ == "__main__":
    names = sys.argv[1].split(",")
    libs = {n: variant(n) for n in names}
    jobs = [(n, libs[n], par, c, t) for n in names for par in (False, True)
            for c, t in (("mos_ss", -40), ("mos_tt", 27), ("mos_ff", 125), ("mos_sf", -40))]
    with ThreadPoolExecutor(14) as ex:
        res = list(ex.map(job, jobs))
    print(f"{'variant':12s} {'view':4s} {'corner':7s} {'UGF':>6s} {'PM':>6s} {'GM':>6s} {'IQ':>6s} {'Itot':>6s} {'ts01':>7s} {'osc_mV':>7s}")
    for r in res:
        n, par, c, t, u, pm, gm, iq, it, ts, osc = r
        print(f"{n:12s} {'+Cp' if par else 'sch':4s} {c[4:]}{t:>4} {u:6.1f} {pm:6.1f} {gm:6.1f} {iq:6.2f} {it:6.0f} {ts:7.0f} {osc:7.2f}")
