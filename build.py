#!/usr/bin/env python3
"""Rebuild the dataset from the ItemList structured data of copy-aesthetic.com.

    python3 build.py <path-to-site-html> [output-dir]

<path-to-site-html> is a directory holding the site's .html files. Only the standard
library is used.
"""
import re, json, csv, glob, os, unicodedata, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = sys.argv[2] if len(sys.argv) > 2 else '.' 

# page slug -> (collection, subcollection)
CATS = {
    'symbols-stars': ('symbols', 'stars'), 'symbols-hearts': ('symbols', 'hearts'),
    'symbols-arrows': ('symbols', 'arrows'), 'symbols-music': ('symbols', 'music'),
    'symbols-weather': ('symbols', 'weather'), 'symbols-math': ('symbols', 'math'),
    'symbols-brackets': ('symbols', 'brackets'), 'symbols-checks': ('symbols', 'checks'),
    'symbols-currency': ('symbols', 'currency'), 'symbols-zodiac': ('symbols', 'zodiac'),
    'unicode-symbols': ('symbols', 'general'),
    'kaomoji': ('kaomoji', 'all'), 'kaomoji-happy': ('kaomoji', 'happy'),
    'kaomoji-sad': ('kaomoji', 'sad'), 'kaomoji-cat': ('kaomoji', 'cat'),
    'kaomoji-angry': ('kaomoji', 'angry'), 'kaomoji-love': ('kaomoji', 'love'),
    'kaomoji-bear': ('kaomoji', 'bear'),
    'text-dividers': ('text', 'dividers'), 'bullet-points': ('text', 'bullets'),
    'aesthetic-symbols-bio': ('text', 'bio-combos'),
    'text-decorator-generator': ('text', 'decorators'),
    'small-text-generator': ('text', 'small-text'),
    'glitch-text-generator': ('text', 'glitch'),
}

def itemlist(src):
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
        if '"numberOfItems"' not in m.group(1):
            continue
        d = json.loads(m.group(1))
        def walk(o):
            if isinstance(o, dict):
                if 'numberOfItems' in o:
                    return o
                for v in o.values():
                    r = walk(v)
                    if r:
                        return r
            elif isinstance(o, list):
                for v in o:
                    r = walk(v)
                    if r:
                        return r
        il = walk(d)
        if il:
            return il
    return None

def codepoints(ch):
    return ' '.join('U+%04X' % ord(c) for c in ch)

def is_single(ch):
    return len(ch) == 1

rows = []
for f in sorted(glob.glob(os.path.join(SRC, '*.html'))):
    slug = os.path.basename(f)[:-5]
    if slug not in CATS:
        continue
    il = itemlist(open(f, encoding='utf-8').read())
    if not il:
        continue
    coll, sub = CATS[slug]
    for e in il['itemListElement']:
        ch = e['item']['name']
        name = e['name']
        # 62 source entries carry the character itself as their name. When it is a
        # single code point the official UCD name is strictly better; multi-character
        # kaomoji stay as-is rather than being given an invented label.
        if name.strip() == ch.strip() and is_single(ch):
            ucd = unicodedata.name(ch, '')
            if ucd:
                name = ucd.title()
        rows.append({
            'character': ch,
            'name': name,
            'named': name.strip() != ch.strip(),
            'collection': coll,
            'category': sub,
            'codepoints': codepoints(ch),
            'char_length': len(ch),
            'unicode_name': (unicodedata.name(ch, '') if is_single(ch) else ''),
            'unicode_category': (unicodedata.category(ch) if is_single(ch) else ''),
            'source': f'https://copy-aesthetic.com/{"" if slug=="index" else slug}',
        })

os.makedirs(os.path.join(OUT, 'data'), exist_ok=True)

# full, ordered, with per-page duplicates kept (a symbol can belong to several collections)
with open(os.path.join(OUT, 'data', 'entries.json'), 'w', encoding='utf-8') as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=1)

with open(os.path.join(OUT, 'data', 'entries.csv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# deduplicated master list, collections merged
uniq = {}
for r in rows:
    k = r['character']
    if k not in uniq:
        uniq[k] = {**r, 'collections': []}
        del uniq[k]['collection'], uniq[k]['category'], uniq[k]['source']
    tag = f"{r['collection']}/{r['category']}"
    if tag not in uniq[k]['collections']:
        uniq[k]['collections'].append(tag)
master = list(uniq.values())
with open(os.path.join(OUT, 'data', 'characters.json'), 'w', encoding='utf-8') as fh:
    json.dump(master, fh, ensure_ascii=False, indent=1)

# split per collection
bycat = {}
for r in rows:
    bycat.setdefault(f"{r['collection']}-{r['category']}", []).append(r)
os.makedirs(os.path.join(OUT, 'data', 'by-category'), exist_ok=True)
for k, v in bycat.items():
    with open(os.path.join(OUT, 'data', 'by-category', k + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(v, fh, ensure_ascii=False, indent=1)

singles = sum(1 for r in master if r['char_length'] == 1)
named = sum(1 for r in master if r['unicode_name'])
print(f'entrees (avec doublons inter-collections) : {len(rows)}')
print(f'caracteres/sequences uniques              : {len(master)}')
print(f'  dont points de code uniques             : {singles} (nom UCD present sur {named})')
print(f'collections                               : {len(bycat)}')
for k in sorted(bycat): print(f'    {k:26} {len(bycat[k])}')
