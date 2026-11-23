#!/bin/bash
# NightOps-Scout raw collection for 2026-11-23 (window 11-17 -> 11-22, host was down 11-17 20:06 -> 11-22 21:38)
cd /home/zhiping/.openclaw/workspace
S=1123
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"

grab() { # $1=url $2=out
  for i in 1 2 3; do
    if curl -sSL --max-time 60 -A "$UA" "$1" -o "$2" && [ -s "$2" ] && [ "$(wc -c < "$2")" -gt 200 ]; then
      echo "OK $(wc -c < "$2") $2"; return 0
    fi
    echo "  retry$i $2" >&2
    sleep 4
  done
  echo "FAIL $2" >&2
  return 1
}

grab "https://export.arxiv.org/api/query?search_query=cat:cs.MA&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending" scout-raw/arxiv-csMA-$S.xml
sleep 3
grab "https://export.arxiv.org/api/query?search_query=all:%22model+context+protocol%22+OR+all:%22MCP+server%22+OR+all:%22tool+use%22+OR+all:%22multi-agent%22+OR+all:%22agent+memory%22&start=0&max_results=150&sortBy=submittedDate&sortOrder=descending" scout-raw/arxiv-mcp-raw-$S.xml
sleep 3
grab "https://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=150&sortBy=submittedDate&sortOrder=descending" scout-raw/arxiv-csAI-$S.xml

grab "https://hacker-news.firebaseio.com/v0/topstories.json" scout-raw/hn-top-$S.json
python3 - <<'PY'
import json,urllib.request,time
ids=json.load(open('scout-raw/hn-top-1123.json'))[:30]
out=[];deadline=time.time()+90
for i in ids:
    if time.time()>deadline: break
    try:
        d=json.load(urllib.request.urlopen('https://hacker-news.firebaseio.com/v0/item/%s.json'%i,timeout=8))
        out.append(d); time.sleep(0.1)
    except Exception: pass
json.dump(out,open('scout-raw/hn-items-1123.json','w'),ensure_ascii=False)
print('hn items',len(out))
PY

grab "https://openai.com/news/rss.xml" scout-raw/rss-openai-$S.xml
grab "https://the-decoder.com/feed/" scout-raw/rss-decoder-$S.xml
grab "https://blog.google/technology/ai/rss/" scout-raw/rss-gai-$S.xml
echo FETCH_DONE
