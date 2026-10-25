import csv, collections, sys
from namematch import build_index, match
f = open('registrants-live.csv', newline='', encoding='utf-8')
rd = csv.DictReader(f); fields = rd.fieldnames; regs = list(rd); f.close()
by = build_index(r['Full Name'] for r in regs)
print('== Name collisions in registrants ==')
for k, v in by.items():
    if len(v) > 1: print('  ', [regs[i]['Full Name'] for i in v], [regs[i]['Registration Type'] for i in v])
sp = list(csv.reader(open('speaker.csv', encoding='utf-8')))[1:]
assigned = {}; notfound = []; conflicts = []; fuzzy = []; skipped = 0
for row in sp:
    name, mod = row[1].strip(), row[4].strip()
    if not name: skipped += 1; continue
    idx, fz = match(name, by)
    if fz: fuzzy.append((name, regs[idx[0]]['Full Name']))
    if not idx: notfound.append((row[0], name, row[3], mod)); continue
    if len(idx) > 1: print('  ambiguous:', name); continue
    i = idx[0]
    if not mod: continue
    if i in assigned and assigned[i] != mod: conflicts.append((name, assigned[i], mod))
    assigned[i] = mod
for i, m in assigned.items(): regs[i]['Latest attendance mode'] = m
print('== Fuzzy matches ==');  [print('  ', a, '->', b) for a, b in fuzzy]
print('== Modality conflicts ==', conflicts)
print(f'== Stats: speaker rows {len(sp)}, blank-name skipped {skipped}, registrants updated {len(assigned)}, not found {len(notfound)} ==')
print('  modality written:', collections.Counter(assigned.values()))
for n in notfound: print('  NOT FOUND:', n)
if '--write' in sys.argv:
    with open('registrants-live.csv', 'w', newline='', encoding='utf-8') as o:
        w = csv.DictWriter(o, fields, quoting=csv.QUOTE_MINIMAL); w.writeheader(); w.writerows(regs)
