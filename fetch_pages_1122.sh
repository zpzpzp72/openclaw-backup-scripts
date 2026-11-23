#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
g(){ curl -sSL --max-time 45 -A "$UA" "$1" -o "$2" && echo "OK $(wc -c < "$2") $2"; }
g "https://the-decoder.com/ai-is-getting-better-faster-than-experts-can-reliably-test-whether-new-systems-are-safe-metr-warns/" scout-raw/dec-1122-metr.html
g "https://the-decoder.com/security-researchers-show-how-cheap-ai-inference-providers-steal-keys-and-snoop-on-users/" scout-raw/dec-1122-inference-keys.html
g "https://the-decoder.com/gpt-6-2-astra-and-sol-get-to-the-point-faster-but-score-lower-on-transparency-than-claude/" scout-raw/dec-1122-gpt62.html
g "https://the-decoder.com/nvidia-researchers-argue-huge-ai-context-windows-are-a-dead-end/" scout-raw/dec-1122-nvidia-context.html
g "https://the-decoder.com/hours-after-anthropic-claims-a-claude-proof-of-the-riemann-hypothesis-stanford-releases-an-all-human-competing-draft/" scout-raw/dec-1122-riemann-stanford.html
g "https://the-decoder.com/openai-shares-new-prompting-tips-for-gpt-6-2-astra-and-sol-to-fix-brief-answers-and-unnecessary-questions/" scout-raw/dec-1122-prompting-tips.html
g "https://the-decoder.com/us-technology-stocks-suffer-their-worst-weekly-loss-since-the-pandemic-as-ai-doubts-pile-up/" scout-raw/dec-1122-techstocks.html
g "https://the-decoder.com/lean-and-mathlib-community-officially-confirms-levent-alpoges-proof-of-the-riemann-hypothesis-is-correct/" scout-raw/dec-1122-riemann-lean.html
g "https://the-decoder.com/new-open-model-inkling-2-mini-thinks-in-loops-to-solve-problems-with-fewer-words-and-still-runs-on-a-laptop/" scout-raw/dec-1122-inkling.html
g "https://openai.com/index/introducing-gpt-6-2-astra-sol" scout-raw/oai-1122-gpt62.html
g "https://openai.com/index/combatting-adversarial-distillation" scout-raw/oai-1122-distill.html
g "https://openai.com/index/inside-the-codex-sandbox" scout-raw/oai-1122-codexsandbox.html
g "https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/" scout-raw/or-1122-dataproc.html
g "https://betterdatacenterproject.com/2026/11/16/how-ai-is-powered-a-breakdown-of-byop-and-grid/" scout-raw/bdp-1122-power.html
g "https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-tool-retrieval/" scout-raw/gai-1122-toolretr.html
