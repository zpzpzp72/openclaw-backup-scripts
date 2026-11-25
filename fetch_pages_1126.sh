#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
grab() {
  for i in 1 2 3; do
    if curl -sSL --max-time 60 -A "$UA" "$1" -o "$2" && [ -s "$2" ] && [ "$(wc -c < "$2")" -gt 200 ]; then
      echo "OK $(wc -c < "$2") $2"; return 0
    fi
    echo "  retry$i $2" >&2; sleep 4
  done
  echo "FAIL $2" >&2; return 1
}
grab "https://the-decoder.com/ai-agents-now-control-part-of-deepminds-compute-for-gemini-experiments-but-recursive-self-improvement-stays-elusive/" scout-raw/dec-1126-deepmind.html
sleep 2
grab "https://the-decoder.com/anthropic-study-shows-the-hardest-part-of-adopting-ai-at-work-has-little-to-do-with-learning-the-tools/" scout-raw/dec-1126-anthropic-adopt.html
sleep 2
grab "https://the-decoder.com/prismml-squeezes-an-agent-based-coding-model-with-27-billion-parameters-into-5-9-gigabytes/" scout-raw/dec-1126-prismml.html
sleep 2
grab "https://the-decoder.com/anthropic-tops-700-million-monthly-mcp-sdk-downloads-and-expands-the-protocol-for-more-autonomous-ai/" scout-raw/dec-1126-mcp700.html
sleep 2
grab "https://the-decoder.com/novartis-ceo-says-ai-will-shave-four-years-off-drug-development-not-cure-all-disease/" scout-raw/dec-1126-novartis.html
sleep 2
grab "https://the-decoder.com/anthropic-researcher-stands-by-his-ai-assisted-riemann-proof-but-owns-up-to-stupid-things/" scout-raw/dec-1126-riemann.html
sleep 2
grab "https://openai.com/index/gpt-6-models-demonstrate-intrinsic-protein-design-capabilities/" scout-raw/openai-1126-protein.html
sleep 2
grab "https://openai.com/index/searching-for-distant-planets-with-astra/" scout-raw/openai-1126-astra.html
sleep 2
grab "https://openai.com/index/introducing-shirudo/" scout-raw/openai-1126-shirudo.html
sleep 2
grab "https://openai.com/business/customer-stories/ifood" scout-raw/openai-1126-ifood.html
sleep 2
grab "https://prismml.com/news/bonsai-2-5-27b" scout-raw/bonsai-1126.html
sleep 2
grab "https://github.com/google-research/google-research/tree/master/cogentic_research_papers" scout-raw/cogentic-1126.html
sleep 2
grab "https://www.lesswrong.com/posts/7wzWuLP3HhyBLmKfo/models-can-communicate-via-inference-servers-despite-being-sandboxed" scout-raw/lw-1126-sandbox.html
sleep 2
grab "https://www.intruder.io/research/taking-over-us-treasury-subdomains-for-3-each" scout-raw/intruder-1126.html
sleep 2
grab "https://the-decoder.com/back-to-back-cyber-incidents-at-us-financial-investigators-and-spy-agencies-follow-a-string-of-federal-investigations/" scout-raw/dec-1126-cyber.html
sleep 2
grab "https://the-decoder.com/anthropic-turns-claude-artifacts-into-standalone-desktop-apps-for-macos-and-windows/" scout-raw/dec-1126-artifacts.html
echo PAGES_DONE
