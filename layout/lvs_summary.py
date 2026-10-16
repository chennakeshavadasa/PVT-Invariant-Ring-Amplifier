"""Summarise a KLayout .lvsdb: python lvs_summary.py <file.lvsdb>  (needs the klayout module)"""
import sys
import klayout.db as db
lvs = db.LayoutVsSchematic()
lvs.read(sys.argv[1])
xref = lvs.xref()
OK = (db.NetlistCrossReference.Match, db.NetlistCrossReference.MatchWithWarning)
for cp in xref.each_circuit_pair():
    a, b = cp.first(), cp.second()
    print(f"circuit {a.name if a else None} <-> {b.name if b else None}: {cp.status()}")
    bad = [p for p in xref.each_device_pair(cp) if p.status() not in OK]
    print(f"  device pairs: {sum(1 for _ in xref.each_device_pair(cp))}, mismatched: {len(bad)}")
    for p in bad[:25]:
        da, ds = p.first(), p.second()
        f = lambda d: (f"{d.expanded_name()} {d.device_class().name} " +
                       " ".join(f"{t.name}={d.net_for_terminal(t.id()).expanded_name() if d.net_for_terminal(t.id()) else '-'}"
                                for t in d.device_class().terminal_definitions()) +
                       " " + " ".join(f"{pd.name}={d.parameter(pd.id()):.4g}" for pd in d.device_class().parameter_definitions()
                                      if pd.name in ('W', 'L', 'A', 'P', 'R', 'C', 'w', 'l', 'm', 'M'))) if d else "-"
        print(f"    [{p.status()}] L: {f(da)}\n                 S: {f(ds)}")
    badn = [p for p in xref.each_net_pair(cp) if p.status() not in OK]
    print(f"  net pairs: {sum(1 for _ in xref.each_net_pair(cp))}, mismatched: {len(badn)}")
    for p in badn[:25]:
        print(f"    [{p.status()}] L: {p.first().expanded_name() if p.first() else '-'}  S: {p.second().expanded_name() if p.second() else '-'}")
nl, ns = lvs.netlist(), lvs.reference
for name, n in (("layout", nl), ("schematic", ns)):
    cnt = {}
    for c in n.each_circuit():
        for d in c.each_device():
            cnt[d.device_class().name] = cnt.get(d.device_class().name, 0) + 1
    print(name, "devices by class:", dict(sorted(cnt.items())))
