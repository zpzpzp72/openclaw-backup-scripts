import json, os, glob, sys

W = '/home/zhiping/.openclaw/workspace'
os.chdir(W)
sys.path.insert(0, W)

import importlib.util
spec = importlib.util.spec_from_file_location('pa', 'parse_arxiv_1107.py')
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)

S = '1124'
sets = [('scout-raw/arxiv-csAI-%s.xml' % S, 'scout-raw/arxiv-csAI-parsed-%s.json' % S),
        ('scout-raw/arxiv-csMA-%s.xml' % S, 'scout-raw/arxiv-csMA-parsed-%s.json' % S),
        ('scout-raw/arxiv-mcp-raw-%s.xml' % S, 'scout-raw/arxiv-mcp-parsed-%s.json' % S)]

for src, dst in sets:
    if not os.path.exists(src):
        print('MISSING', src)
        continue
    data = pa.parse(src)
    json.dump(data, open(dst, 'w'), ensure_ascii=False, indent=1)
    print(dst, len(data))

# previous ids: all parsed files before 1117
prev_ids = set()
for pf in glob.glob('scout-raw/arxiv-*-parsed-*.json'):
    tag = pf.rsplit('-', 1)[-1].replace('.json', '')
    if tag == S:
        continue
    try:
        for x in json.load(open(pf)):
            prev_ids.add(x['id'].split('v')[0])
    except Exception:
        pass
print('prev ids', len(prev_ids))

seen = set()
new = []
for src, dst in sets:
    if not os.path.exists(dst):
        continue
    for x in json.load(open(dst)):
        b = x['id'].split('v')[0]
        if b in seen:
            continue
        seen.add(b)
        x['id_base'] = b
        if b not in prev_ids:
            new.append(x)

json.dump(new, open('scout-raw/arxiv-%s-newids.json' % S, 'w'), ensure_ascii=False, indent=1)
print('new arxiv vs all-prev:', len(new))

# window-over-window vs 1108
prev8 = set()
for pf in glob.glob('scout-raw/arxiv-*-parsed-1117.json'):
    for x in json.load(open(pf)):
        prev8.add(x['id'].split('v')[0])
new8 = [x for x in new if x['id_base'] not in prev8]
print('new arxiv vs 1117-window:', len(new8))
json.dump(new8, open('scout-raw/arxiv-%s-newids-vs1108.json' % S, 'w'), ensure_ascii=False, indent=1)

# newest published date
alld = []
for _, dst in sets:
    if os.path.exists(dst):
        alld.extend(json.load(open(dst)))
if alld:
    alld.sort(key=lambda x: x['published'], reverse=True)
    print('newest published:', alld[0]['published'], alld[0]['title'][:90])
    pubs = {}
    for x in alld:
        pubs[x['published'][:10]] = pubs.get(x['published'][:10], 0) + 1
    print('published-date histogram (top 15):', sorted(pubs.items(), reverse=True)[:15])
