#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
get(){ curl -sS -L -A "$UA" --max-time 40 "$2" -o "scout-raw/$1"; echo "$1 $(wc -c < scout-raw/$1)"; sleep 0.5; }
get dec-perplexity-agent.html "https://the-decoder.com/perplexity-now-has-its-own-always-on-ai-agent/"
get dec-frontier-radar5.html "https://the-decoder.com/frontier-radar-5-if-agi-is-so-close-why-is-everyone-leaving-the-neolabs-and-their-bets/"
get dec-metr-anthropic.html "https://the-decoder.com/metr-finds-anthropic-may-have-crossed-its-own-ai-acceleration-warning-threshold-back-in-july/"
get dec-inkling2.html "https://the-decoder.com/thinking-machines-inkling-2-small-claims-top-spot-among-western-open-weight-models/"
get dec-anth-ipo.html "https://the-decoder.com/anthropics-1-5-trillion-ipo-hits-resistance-as-investors-balk-at-valuation/"
get dec-anth-bank.html "https://the-decoder.com/anthropic-adds-bank-account-access-to-claude-so-users-can-track-their-spending/"
get dec-gpt6cyber.html "https://the-decoder.com/openais-gpt-6-cyber-can-both-break-into-systems-and-propose-how-to-fix-them/"
get dec-gemini-omni.html "https://the-decoder.com/googles-gemini-omni-1-2-flash-stretches-ai-video-clips-to-15-seconds-and-cuts-pricing-by-30-percent/"
get dec-ernie55.html "https://the-decoder.com/baidu-releases-ernie-5-5-flash-base-with-280-billion-parameters-as-an-open-source-foundation-model/"
get anth-news-1107.html "https://www.anthropic.com/news"
echo PAGES_DONE
