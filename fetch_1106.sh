#!/bin/bash
# NightOps-Scout raw collection for 2026-11-05 -> 2026-11-06
cd /home/zhiping/.openclaw/workspace
S=1106
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
C="curl -sS --max-time 45 -A $UA"

# ---- arXiv ----
$C "https://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending" -o scout-raw/arxiv-csAI-$S.xml
sleep 3
$C "https://export.arxiv.org/api/query?search_query=cat:cs.MA&start=0&max_results=60&sortBy=submittedDate&sortOrder=descending" -o scout-raw/arxiv-csMA-$S.xml
sleep 3
$C "https://export.arxiv.org/api/query?search_query=all:%22model+context+protocol%22+OR+all:%22MCP+server%22+OR+all:%22tool+use%22+OR+all:%22multi-agent%22+OR+all:%22agent+memory%22&start=0&max_results=120&sortBy=submittedDate&sortOrder=descending" -o scout-raw/arxiv-mcp-raw-$S.xml

# ---- HN ----
$C "https://hacker-news.firebaseio.com/v0/topstories.json" -o scout-raw/hn-top-$S.json
python3 - <<'PY'
import json,urllib.request,time
ids=json.load(open('scout-raw/hn-top-1106.json'))[:30]
out=[]
deadline=time.time()+90
for i in ids:
    if time.time()>deadline: break
    try:
        d=json.load(urllib.request.urlopen('https://hacker-news.firebaseio.com/v0/item/%s.json'%i,timeout=8))
        out.append(d); time.sleep(0.1)
    except Exception as e:
        pass
json.dump(out,open('scout-raw/hn-items-1106.json','w'),ensure_ascii=False)
print('hn items',len(out))
PY

# ---- RSS ----
$C "https://openai.com/news/rss.xml" -o scout-raw/rss-openai-$S.xml
$C "https://the-decoder.com/feed/" -o scout-raw/rss-decoder-$S.xml
$C "https://blog.google/technology/ai/rss/" -o scout-raw/rss-gai-$S.xml

echo FETCH_DONE
for f in scout-raw/*-1106.* ; do echo "$f $(wc -c < $f)"; done
