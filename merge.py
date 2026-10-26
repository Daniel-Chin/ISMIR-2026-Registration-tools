import csv, collections, sys
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.identity import Person, find_person, names_match
f = open('registrants-live.csv', newline='', encoding='utf-8')
rd = csv.DictReader(f); fields = rd.fieldnames; regs = list(rd); f.close()
people = [Person.of([r['Full Name']], []) for r in regs]
print('== Name collisions in registrants ==')
for i, j in ((i, j) for i in range(len(regs)) for j in range(i)):
    if names_match(regs[i]['Full Name'], regs[j]['Full Name']):
        print('  ', [regs[i]['Full Name'], regs[j]['Full Name']], [regs[i]['Registration Type'], regs[j]['Registration Type']])
sp = list(csv.reader(open('speaker.csv', encoding='utf-8')))[1:]
assigned = {}; notfound = []; conflicts = []; fuzzy = []; skipped = 0
for row in sp:
    name, mod = row[1].strip(), row[4].strip()
    if not name: skipped += 1; continue
    idx, fz = find_person(Person.of([name], []), people)
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
