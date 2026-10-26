import csv, sys, datetime
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.identity import Person, find_person
CUTOFF = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(weeks=2)
def load(path):
    with open(path, newline='', encoding='utf-8-sig') as f: return list(csv.DictReader(f))
regs = load('registrants-live.csv')
details = load('Registrant Details - latest.csv')
# Emails live only in the details export; join on (name, registration date), which must be 1:1.
key = lambda r: (r['Full Name'], r['Last Registration Date (GMT)'])
email = {}
for d in details:
    k = key(d)
    if k in email: raise ValueError(f'duplicate registrant in details: {k}')
    if not d['Email Address'].strip(): raise ValueError(f'missing email: {k}')
    email[k] = d['Email Address'].strip()
if len(email) != len(regs): raise ValueError(f'row count mismatch: live {len(regs)} vs details {len(email)}')
emails_by_idx = {}
for i, r in enumerate(regs):
    if key(r) not in email: raise ValueError(f'registrant not in details: {key(r)}')
    emails_by_idx[i] = email[key(r)].lower()
if len(set(emails_by_idx.values())) != len(regs): raise ValueError('duplicate emails among registrants')
people = [Person.of([r['Full Name']], [emails_by_idx[i]]) for i, r in enumerate(regs)]
presenters = set()
for row in list(csv.reader(open('speaker.csv', encoding='utf-8')))[1:]:
    name = row[1].strip()
    if not name or 'not presenting' in row[5]: continue
    idx, fz = find_person(Person.of([name], []), people)
    if len(idx) > 1: raise ValueError(f'ambiguous speaker match: {name}')
    if fz: print(f'fuzzy: {name} -> {regs[idx[0]]["Full Name"]}', file=sys.stderr)
    presenters.update(idx)
out = []
for i, r in enumerate(regs):
    if i in presenters: continue
    t = datetime.datetime.fromisoformat(r['Last Registration Date (GMT)'].replace('Z', '+00:00'))
    if t < CUTOFF: out.append(emails_by_idx[i])
print(f'{len(presenters)} presenters matched, {len(out)} emails (registered before {CUTOFF:%Y-%m-%d %H:%M} UTC)', file=sys.stderr)
print('\n'.join(sorted(out)))
