"""Mismatch attribution for the v2 prototype: mismatch on in one device group at a time (mm_ok=0 elsewhere)."""
import re, sys, json
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import v2, chk, montecarlo as mcm
GROUPS = {
    "input pair": ("XMN1", "XMN2"), "stage-1 loads": ("XMP1", "XMP2", "XRD"), "R1/R3": ("XR1", "XR3"),
    "CMFB": ("XMC1", "XMC2", "XMPC1", "XMPC2"), "stage 2": ("XMN_STG2", "XMP_STG2", "XMP_DZ", "XMN_DZ"),
    "trip replica": ("XMT",), "MP3/MN3/MP_R": ("XM1 ", "XM2 ", "XMP_R"), "reg. integrator": ("XXRG", "XRS"),
    "servo + trim": ("XXSV", "XRTA", "XRTB"), "bias": ("XMB", "XMD"),
}
def lib_for(f, group):
    out = []
    for line in f.read_text().splitlines():
        if re.match(r"^X\S+ ", line) and (" sg13_" in line or " rhigh " in line):
            keep = group == "all" or any(line.startswith(g) for g in GROUPS[group])
            if not keep:
                line += " mm_ok=0"
        out.append(line)
    g = f.with_name(f.stem + f"_mm{abs(hash(group)) % 10**6}.spice"); g.write_text("\n".join(out) + "\n"); return g
if __name__ == "__main__":
    k, val = sys.argv[1].split("=", 1); N = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    p = dict(chk.BASE, **json.loads(val)); f = v2.lib(p, "att_" + k)
    groups = (sys.argv[3].split(",") if len(sys.argv) > 3 else list(GROUPS)) + ["all"]
    libs = {g: lib_for(f, g) for g in groups}
    def one(j):
        g, s = j; d = v2.OUT / f"att_{k}_{abs(hash(g)) % 10**6}_{s}"
        v2.run(d, v2.tb(libs[g], d, "mos_tt", 27, seed=s + 1, models=mcm.SETS["mismatch"], tran=False, ac=False, ptat=p.get("ptat")))
        try:
            m = v2.metrics(d, tran=False); return g, m["off_mv"], m["iq"]
        except Exception:
            return g, np.nan, np.nan
    with ThreadPoolExecutor(15) as ex:
        res = list(ex.map(one, [(g, s) for g in groups for s in range(N)]))
    print(f"{'mismatch only in':18s} {'sigma off (mV)':>14s} {'sigma IQ/mean':>14s}")
    for g in groups:
        off = np.array([r[1] for r in res if r[0] == g]); iq = np.array([r[2] for r in res if r[0] == g]); ok = np.isfinite(off)
        print(f"{g:18s} {np.std(off[ok]):14.2f} {100 * np.std(iq[ok]) / np.mean(iq[ok]):13.1f}%  (n={ok.sum()})")
