import json, os, glob, sys

W = '/home/zhiping/.openclaw/workspace'
os.chdir(W)
sys.path.insert(0, W)

import importlib.util
spec = importlib.util.spec_from_file_location('pa', 'parse_arxiv_1107.py')
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)

S = '1108'
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

# previous ids from all parsed files before 1108
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

# new ids this window (vs 1107 window specifically preferred, fallback to all prev)
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

# also compute vs 1107 only (window-over-window)
prev7 = set()
for pf in glob.glob('scout-raw/arxiv-*-parsed-1107.json'):
    for x in json.load(open(pf)):
        prev7.add(x['id'].split('v')[0])
new7 = [x for x in new if x['id_base'] not in prev7]
print('new arxiv vs 1107-window:', len(new7))
