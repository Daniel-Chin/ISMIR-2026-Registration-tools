import csv, collections, subprocess, sys
MODE = {'Onsite': 'In-person', 'Virtual': 'Virtual', 'Pending': ''}  # blank -> leave unchanged
f = open('papers.csv', newline='', encoding='utf-8')
rd = csv.DictReader(f); fields = rd.fieldnames; papers = list(rd); f.close()
by_uid = {p['uid']: p for p in papers}
sp = [r for r in list(csv.reader(open('speaker.csv', encoding='utf-8')))[1:] if r[3].startswith('Paper Author')]
changed = []; same = 0; pending = []; nouid = []
for row in sp:
    uid, name, mod = row[0].strip(), row[1].strip(), row[4].strip()
    p = by_uid.get(uid)
    if not p: nouid.append((uid, name, mod)); continue
    if mod not in MODE: pending.append((uid, name, mod)); continue
    if p['paper_presentation'] == MODE[mod]: same += 1; continue
    changed.append((uid, name, p['paper_presentation'], MODE[mod])); p['paper_presentation'] = MODE[mod]
print('== Changed ==');  [print(f'   {u} {n!r}: {a!r} -> {b!r}') for u, n, a, b in changed]
print('== uid not in papers.csv ==', nouid)
print('== Pending/blank (unchanged) ==', [(u, p['paper_presentation'] if (p := by_uid.get(u)) else None) for u, _, _ in pending])
print(f'== Stats: paper speakers {len(sp)}, changed {len(changed)}, already same {same}, pending {len(pending)} ==')
print('  result:', collections.Counter(p['paper_presentation'] for p in papers))
if '--write' in sys.argv:
    with open('papers.csv', 'w', newline='', encoding='utf-8') as o:
        w = csv.DictWriter(o, fields, quoting=csv.QUOTE_MINIMAL); w.writeheader(); w.writerows(papers)
subprocess.run(['wl-copy'], input='\n'.join(['paper_presentation'] + [p['paper_presentation'] for p in papers]), text=True)
