#!/bin/bash
# NightOps-Scout raw collection for 2026-11-04
cd /home/zhiping/.openclaw/workspace
S=1105
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"

# ---- arXiv ----
curl -sS -A "$UA" "https://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending" -o scout-raw/arxiv-csAI-$S.xml
sleep 3
curl -sS -A "$UA" "https://export.arxiv.org/api/query?search_query=cat:cs.MA&start=0&max_results=60&sortBy=submittedDate&sortOrder=descending" -o scout-raw/arxiv-csMA-$S.xml
sleep 3
curl -sS -A "$UA" "https://export.arxiv.org/api/query?search_query=all:%22model+context+protocol%22+OR+all:%22MCP+server%22+OR+all:%22tool+use%22+OR+all:%22multi-agent%22+OR+all:%22agent+memory%22&start=0&max_results=120&sortBy=submittedDate&sortOrder=descending" -o scout-raw/arxiv-mcp-raw-$S.xml

# ---- HN ----
curl -sS "https://hacker-news.firebaseio.com/v0/topstories.json" -o scout-raw/hn-top-$S.json
python3 - <<'PY'
import json,urllib.request,time
ids=json.load(open('scout-raw/hn-top-1105.json'))[:30]
out=[]
for i in ids:
    try:
        d=json.load(urllib.request.urlopen('https://hacker-news.firebaseio.com/v0/item/%s.json'%i,timeout=15))
        out.append(d); time.sleep(0.15)
    except Exception as e:
        pass
json.dump(out,open('scout-raw/hn-items-1105.json','w'),ensure_ascii=False)
print('hn items',len(out))
PY

# ---- RSS ----
curl -sS -A "$UA" "https://openai.com/news/rss.xml" -o scout-raw/rss-openai-$S.xml
curl -sS -A "$UA" "https://the-decoder.com/feed/" -o scout-raw/rss-decoder-$S.xml
curl -sS -A "$UA" "https://blog.google/technology/ai/rss/" -o scout-raw/rss-gai-$S.xml

echo FETCH_DONE
