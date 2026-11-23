#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
get(){ for i in 1 2 3; do curl -sS -L -A "$UA" --max-time 45 "$2" -o "scout-raw/$1" && [ -s "scout-raw/$1" ] && break; sleep 3; done; echo "$1 $(wc -c < scout-raw/$1 2>/dev/null)"; sleep 0.4; }
get dec-1117-qwen4max.html "https://the-decoder.com/alibabas-qwen4-max-takes-on-opus-5-5-gpt-6-and-kimi-k3-1-pro-at-much-lower-prices/"
get dec-1117-canvas.html "https://the-decoder.com/claude-now-builds-interactive-websites-inside-canvas-graphics-reviving-the-flash-era-with-real-html/"
get dec-1117-agentmemory.html "https://the-decoder.com/anthropic-says-the-key-to-agent-memory-is-knowing-what-to-forget-not-how-much-to-store/"
get dec-1117-fable52.html "https://the-decoder.com/anthropics-claude-fable-5-2-doesnt-generate-images-it-paints-them/"
get dec-1117-nvidia-china.html "https://the-decoder.com/firm-linked-to-jensen-huangs-ex-lover-reportedly-brokered-nearly-12-billion-in-nvidia-chip-orders-for-china/"
get dec-1117-au-central-bank.html "https://the-decoder.com/australias-central-bank-finds-ai-hitting-young-workers-first-especially-in-software-and-customer-service/"
get dec-1117-meituan.html "https://the-decoder.com/meituan-releases-a-1-6-trillion-parameter-agent-model-that-never-touched-an-nvidia-gpu/"
get dec-1117-amodei.html "https://the-decoder.com/anthropic-ceo-amodei-admits-theras-a-huge-uncertainty-in-whats-going-to-happen-next-year-days-before-a-record-ipo/"
get anth-news-1117.html "https://www.anthropic.com/news"
echo PAGES_DONE
