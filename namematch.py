import unicodedata, re, collections
try: from aliases import ALIAS  # gitignored: maps speaker-sheet names to registrant names
except ImportError: ALIAS = {}
def toks(n):
    if ',' in n:
        last, first = n.split(',', 1); n = first + ' ' + last
    n = n.replace('ı', 'i')
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower()
    n = re.sub(r'\bdr\.?\s', ' ', n)
    return frozenset(re.findall(r'[a-z]+', n))
def build_index(names):
    by = collections.defaultdict(list)
    for i, n in enumerate(names): by[toks(n)].append(i)
    return by
def match(name, by):
    """Return (indices, fuzzy). Exact token-set match first, else a unique subset match sharing >= 2 tokens."""
    k = toks(ALIAS.get(name, name)); idx = by.get(k)
    if idx: return idx, False
    c = [i for kk, v in by.items() for i in v if kk and (k <= kk or kk <= k) and len(k & kk) >= 2]
    return (c, True) if len(c) == 1 else ([], False)
