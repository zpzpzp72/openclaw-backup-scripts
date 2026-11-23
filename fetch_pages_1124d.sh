#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
grab() { for i in 1 2 3; do if curl -sSL --max-time 60 -A "$UA" "$1" -o "$2" && [ -s "$2" ] && [ "$(wc -c < "$2")" -gt 200 ]; then echo "OK $(wc -c < "$2") $2"; return 0; fi; echo " retry$i $2" >&2; sleep 4; done; echo "FAIL $2" >&2; return 1; }
grab "https://www.anthropic.com/news/ipo-close" scout-raw/anth-ipo-1124.html
sleep 2
grab "https://www.anthropic.com/news/anthropic-prices-initial-public-offering" scout-raw/anth-price-1124.html
sleep 2
grab "https://www.anthropic.com/news/2026-usage-policy-update" scout-raw/anth-policy-1124.html
sleep 2
grab "https://www.anthropic.com/news/cyber-verification-program" scout-raw/anth-cyber-1124.html
sleep 2
grab "https://www.anthropic.com/news/genesis-mission-commitment" scout-raw/anth-genesis-1124.html
sleep 2
grab "https://www.anthropic.com/news/ai-for-science-expands-foundations-research-institutions" scout-raw/anth-science-1124.html
echo PAGES4_DONE
