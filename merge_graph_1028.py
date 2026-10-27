import json, os, datetime

MAIN = 'graphify-out/graph.json'
STAMP = '2026-10-28'
SNAP = f'graphify-out/{STAMP}/snapshot.json'
CORPUS = f'graphify-out/raw/scout-{STAMP}-corpus.md'
CAPTURED = '2026-10-27T16:30:00+00:00'

FILE_TYPE = {'arxiv': 'paper', 'release': 'document', 'commit': 'document',
             'news': 'document', 'repo': 'document', 'org': 'document',
             'advisory': 'document', 'theme': 'document', 'cluster': 'document'}

g = json.load(open(MAIN))
snap = json.load(open(SNAP))
nodes = g['nodes']
links = g['links']
existing_ids = {n['id'] for n in nodes}
existing_keys = {(l.get('source'), l.get('target'), l.get('relation')) for l in links}

added_n = 0
for n in snap['nodes']:
    if n['id'] in existing_ids:
        continue
    attrs = dict(n.get('attrs') or {})
    node = {
        'id': n['id'],
        'label': n.get('label') or n['id'],
        'file_type': FILE_TYPE.get(n.get('kind'), 'document'),
        'source_file': CORPUS,
        'source_location': None,
        'source_url': None,
        'captured_at': CAPTURED,
        'author': None,
        'contributor': None,
        'theme': attrs.get('theme'),
        'tags': attrs,
    }
    nodes.append(node)
    existing_ids.add(n['id'])
    added_n += 1

added_l = 0
for l in snap['links']:
    s, t, r = l['source'], l['target'], l['relation']
    if s not in existing_ids or t not in existing_ids:
        continue
    key = (s, t, r)
    if key in existing_keys:
        continue
    conf = l.get('confidence', 'EXTRACTED')
    links.append({
        'relation': r,
        'confidence': conf,
        'confidence_score': 1.0 if conf == 'EXTRACTED' else (0.75 if conf == 'INFERRED' else 0.5),
        'source_file': CORPUS,
        'source_location': None,
        'weight': 1.0,
        '_src': s,
        '_tgt': t,
        'source': s,
        'target': t,
    })
    existing_keys.add(key)
    added_l += 1

g['nodes'] = nodes
g['links'] = links
json.dump(g, open(MAIN, 'w'), ensure_ascii=False, indent=2)
print('main graph: nodes', len(nodes), '(+%d)' % added_n, 'links', len(links), '(+%d)' % added_l)
