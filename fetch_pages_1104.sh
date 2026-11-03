#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
get(){ curl -sS -L -A "$UA" --max-time 40 "$2" -o "scout-raw/$1"; echo "$1 $(wc -c < scout-raw/$1)"; sleep 0.5; }

get dec-openai-army.html "https://the-decoder.com/openai-hires-ex-army-secretary-gaining-bipartisan-reach-just-as-midterms-loom/"
get dec-anth-threads.html "https://the-decoder.com/anthropics-message-threads-cut-time-to-first-token-by-35-percent-for-long-conversations/"
get dec-nvidia-china.html "https://the-decoder.com/nvidia-pushes-cloud-customers-to-cut-back-on-china-business/"
get dec-huawei-mem.html "https://the-decoder.com/huawei-tells-customers-to-find-their-own-ai-chip-memory-effectively-outsourcing-procurement-to-the-black-market/"
get dec-openai-bounty.html "https://the-decoder.com/bug-hunters-can-now-earn-up-to-172000-from-openai-as-company-ramps-up-security/"
get dec-anth-gameclone.html "https://the-decoder.com/anthropic-cracks-down-on-game-cloning-in-claude-code-after-wave-of-ai-built-knockoffs/"
get dec-goldman.html "https://the-decoder.com/goldman-sachs-pulls-ai-coding-tools-from-traders-and-bankers/"
get dec-spacex-grok.html "https://the-decoder.com/spacexsi-apparently-cuts-grok-bot-quotas-weeks-after-musk-called-it-his-fastest-growing-product/"
get dec-ai-hoard.html "https://the-decoder.com/ai-elites-might-hoard-intelligence-like-mercantilists-hoarded-gold/"

get anth-news-1104.html "https://www.anthropic.com/news"
get openai-securitysprint.html "https://openai.com/index/preparing-our-next-security-sprint-to-harden-openai"
get openai-bounty.html "https://openai.com/index/rewarding-defenders-with-bigger-bug-bounties"
get openai-git.html "https://openai.com/index/scaling-git-at-openai"
get openai-lifeval.html "https://openai.com/index/lifeval"
get openai-heimstaden.html "https://openai.com/index/heimstaden"
get openai-misalign.html "https://openai.com/index/how-we-detect-frontier-model-misalignment"
get openai-modelspec.html "https://openai.com/index/updated-model-spec"
get openai-driscoll.html "https://openai.com/index/dan-driscoll-joins-openai"
get hn-astra.html "https://honnibal.dev/blog/astra-read-write-misleading"
echo PAGES_DONE
