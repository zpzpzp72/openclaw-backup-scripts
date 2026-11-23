#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
grab() { for i in 1 2 3; do if curl -sSL --max-time 60 -A "$UA" "$1" -o "$2" && [ -s "$2" ] && [ "$(wc -c < "$2")" -gt 200 ]; then echo "OK $(wc -c < "$2") $2"; return 0; fi; echo " retry$i $2" >&2; sleep 4; done; echo "FAIL $2" >&2; return 1; }
grab "https://the-decoder.com/new-open-model-inkling-2-mini-thinks-in-loops-to-solve-problems-with-fewer-words-and-still-runs-on-a-laptop/" scout-raw/dec-1124-inkling.html
sleep 2
grab "https://www.gpupartner.com/blog/beginners-guide-local-ai-inkling-qwen-unsloth" scout-raw/local-1124.html
sleep 2
grab "https://the-decoder.com/hours-after-anthropic-claims-a-claude-proof-of-the-riemann-hypothesis-stanford-releases-an-all-human-competing-draft/" scout-raw/dec-1124-stanford.html
sleep 2
grab "https://www.nytimes.com/2026/11/23/world/asia/china-nuclear-missiles-ai.html" scout-raw/nyt-1124.html
echo PAGES3_DONE
