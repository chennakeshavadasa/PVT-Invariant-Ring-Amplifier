#!/usr/bin/env python3
"""Audit README.md before a commit: every image and relative link resolves, figures and
tables are numbered 1..N without gaps, every figure caption sits right under its image,
every cited reference exists and every listed reference is cited."""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
text = (REPO / "README.md").read_text()
errors = []

# 1. images and relative links
for target in re.findall(r'src="([^"]+)"', text) + re.findall(r"\]\(([^)\s]+)\)", text):
    if target.startswith(("http://", "https://", "#", "mailto:")):
        continue
    if not (REPO / unquote(target.split("#")[0])).exists():
        errors.append(f"missing file: {target}")

# 2. figure numbering and caption placement
figs = [int(n) for n in re.findall(r"<b>Fig\. (\d+)\.</b>", text)]
if figs != list(range(1, len(figs) + 1)):
    errors.append(f"figure captions not numbered 1..N: {figs}")
blocks = text.split("\n")
for i, line in enumerate(blocks):
    if "<b>Fig." in line and i and "<img" not in blocks[i - 1] and "</p>" not in blocks[i - 1]:
        errors.append(f"caption of line {i + 1} is not directly under an image block")
for n in set(int(m) for m in re.findall(r"Fig\. (\d+)", text)):
    if n not in figs:
        errors.append(f"reference to non-existent Fig. {n}")

# 3. tables
roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
tabs = re.findall(r"TABLE ([IVX]+)<br>", text)
if tabs != roman[:len(tabs)]:
    errors.append(f"tables not numbered I..N: {tabs}")
for t in set(re.findall(r"Table ([IVX]+)\b", text)):
    if t not in tabs:
        errors.append(f"reference to non-existent Table {t}")

# 4. references
listed = [int(n) for n in re.findall(r"^\[(\d+)\] ", text, re.M)]
if listed != list(range(1, len(listed) + 1)):
    errors.append(f"reference list not numbered 1..N: {listed}")
body = text.split("## References")[0]
cited = set()
for grp in re.findall(r"\[(\d+(?:\]?[,–-]\s*\[?\d+)*)", body):
    for a, b in re.findall(r"(\d+)\]?[–-]\[?(\d+)", grp):
        cited.update(range(int(a), int(b) + 1))
    cited.update(int(x) for x in re.findall(r"\d+", grp))
for n in sorted(cited - set(listed)):
    errors.append(f"cited but not listed: [{n}]")
for n in sorted(set(listed) - cited):
    errors.append(f"listed but never cited: [{n}]")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"README audit OK: {len(figs)} figures, {len(tabs)} tables, {len(listed)} references, all paths resolve")
