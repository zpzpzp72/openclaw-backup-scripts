import json, collections, lancedb

DB = '/home/zhiping/.openclaw/memory/lancedb-pro'
DATE = '2026-11-15'

ROWS = json.load(open('/home/zhiping/.openclaw/workspace/rows_1115.json'))

db = lancedb.connect(DB)
tbl = db.open_table('nightly-scout')
before = tbl.count_rows()

existing = set(tbl.to_pandas()['id'].tolist())
new_rows = []
for r in ROWS:
    rid = r[0]
    if rid in existing:
        continue
    new_rows.append({
        'id': rid,
        'date': DATE,
        'category': r[1],
        'title': r[2],
        'arxiv_id': r[3],
        'summary': r[4],
        'relevance': r[5],
        'tags': list(r[6]),
    })

if new_rows:
    tbl.add(new_rows)

after = tbl.count_rows()
df = tbl.to_pandas()
print('before', before, 'after', after, 'added', len(new_rows))
print('category counts for today:', collections.Counter(df[df['date'] == DATE]['category']))
today = df[df['date'] == DATE]
assert len(today) == len(new_rows), (len(today), len(new_rows))
print('sample:', today.iloc[0]['id'], '|', today.iloc[0]['title'][:70])
