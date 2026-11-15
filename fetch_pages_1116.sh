#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
get(){ for i in 1 2; do curl -sS -L -A "$UA" --max-time 45 "$2" -o "scout-raw/$1" && [ -s "scout-raw/$1" ] && break; sleep 3; done; echo "$1 $(wc -c < scout-raw/$1 2>/dev/null)"; sleep 0.4; }
get dec-1116-fable52.html "https://the-decoder.com/anthropics-claude-fable-5-2-doesnt-generate-images-it-paints-them/"
get dec-1116-nvidia-china.html "https://the-decoder.com/firm-linked-to-jensen-huangs-ex-lover-reportedly-brokered-nearly-12-billion-in-nvidia-chip-orders-for-china/"
get dec-1116-au-central-bank.html "https://the-decoder.com/australias-central-bank-finds-ai-hitting-young-workers-first-especially-in-software-and-customer-service/"
get dec-1116-meituan.html "https://the-decoder.com/meituan-releases-a-1-6-trillion-parameter-agent-model-that-never-touched-an-nvidia-gpu/"
get dec-1116-amodei.html "https://the-decoder.com/anthropic-ceo-amodei-admits-theres-a-huge-uncertainty-in-whats-going-to-happen-next-year-days-before-a-record-ipo/"
get anth-news-1116.html "https://www.anthropic.com/news"
echo PAGES_DONE
