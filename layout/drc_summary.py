"""Summarise a KLayout DRC report: python3 drc_summary.py <report.lyrdb> [max_items]"""
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 3
desc = {c.findtext("name"): (c.findtext("description") or "") for c in root.iter("category")}
items = {}
for it in root.iter("item"):
    cat = it.findtext("category").strip("'")
    vals = [v.text for v in it.iter("value")]
    items.setdefault(cat, []).append(vals)
if not items:
    print("DRC clean: 0 violations")
for cat, lst in sorted(items.items()):
    print(f"{cat}: {len(lst)}  -- {desc.get(cat, desc.get(chr(39) + cat + chr(39), ''))}")
    for v in lst[:nmax]:
        print("     ", (v[0] or "")[:160])
