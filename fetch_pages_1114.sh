#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
get(){ for i in 1 2; do curl -sS -L -A "$UA" --max-time 45 "$2" -o "scout-raw/$1" && [ -s "scout-raw/$1" ] && break; sleep 3; done; echo "$1 $(wc -c < scout-raw/$1 2>/dev/null)"; sleep 0.4; }

get dec-1114-openai-robotics.html "https://the-decoder.com/openai-reassigns-robotics-researchers-to-other-teams-as-general-purpose-models-might-make-specialized-robotics-unnecessary/"
get dec-1114-mythos-retrain.html "https://the-decoder.com/anthropic-can-already-retrain-mythos-with-a-fraction-of-the-compute-originally-needed-says-former-researcher/"
get dec-1114-praxis1.html "https://the-decoder.com/runways-open-source-praxis-1-turns-video-ai-into-a-robot-controller/"
get dec-1114-jensen-huang.html "https://the-decoder.com/jensen-huangs-ouster-likely-traces-back-to-nvidias-risky-business-practices-more-than-his-personal-life/"
get dec-1114-chatgpt-wallet.html "https://the-decoder.com/openai-rebuilt-ai-shopping-from-scratch-with-chatgpt-wallet/"
get dec-1114-anth-ipo-banks.html "https://the-decoder.com/banks-bar-chinese-and-hong-kong-investors-from-anthropic-ipo-over-us-export-controls/"
get dec-1114-claude-manufacturing.html "https://the-decoder.com/anthropics-claude-for-manufacturing-plugs-ai-directly-into-factory-software-to-automate-industrial-workflows/"
get dec-1114-us-agencies.html "https://the-decoder.com/nearly-70-percent-of-us-agencies-use-generative-ai-and-unions-are-finally-catching-up-with-guardrails/"
get dec-1114-blackwell-fingerprints.html "https://the-decoder.com/former-openai-researcher-says-he-found-nvidia-blackwell-fingerprints-hidden-inside-six-chinese-ai-models/"
get dec-1114-anth-ipo-oversubscribed.html "https://the-decoder.com/anthropics-ipo-is-six-times-oversubscribed-and-on-track-to-become-the-largest-public-offering-in-history/"
get anth-news-1114.html "https://www.anthropic.com/news"
echo PAGES_DONE
