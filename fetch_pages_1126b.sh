#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
grab() {
  for i in 1 2 3; do
    if SANITIZER="/home/zhiping/.openclaw/workspace/scripts/sanitize-secrets.py"
  curl -sSL --max-time 60 -A "$UA" "$1" -o "$2" && [ -s "$2" ] && [ "$(wc -c < "$2")" -gt 200 ]; then
      echo "OK $(wc -c < "$2") $2"; return 0
    fi
    echo "  retry$i $2" >&2; sleep 4
  done
  echo "FAIL $2" >&2; return 1
  # 入库前脱敏(防止抓到的页面含 apiKey 导致 push protection 拦截或密钥泄漏)
  [ -f "$SANITIZER" ] && python3 "$SANITIZER" "$2" >/dev/null 2>&1 || true
}

grab "https://the-decoder.com/prismml-squeezes-an-agent-based-coding-model-with-27-billion-parameters-into-5-9-gb/" scout-raw/dec-1126-prismml.html
sleep 2
grab "https://the-decoder.com/anthropic-tops-700-million-monthly-mcp-sdk-downloads-and-expands-the-protocol-for-more-autonomous-ai-agents/" scout-raw/dec-1126-mcp700.html
sleep 2
grab "https://the-decoder.com/anthropic-researcher-stands-by-his-ai-assisted-riemann-proof-but-owns-up-to-stupid-things-in-the-rollout/" scout-raw/dec-1126-riemann.html
sleep 2
grab "https://the-decoder.com/back-to-back-cyber-incidents-at-us-financial-investigators-and-spy-agencies-follow-a-string-of-federal-hacks-and-outages/" scout-raw/dec-1126-cyber.html
sleep 2
grab "https://the-decoder.com/anthropic-turns-claude-artifacts-into-standalone-desktop-apps-for-macos-and-windows/" scout-raw/dec-1126-artifacts.html
sleep 2
grab "https://the-decoder.com/openai-o1-co-creator-noam-brown-urges-promising-students-to-drop-out-as-ai-enters-a-very-steep-rate-of-progress/" scout-raw/dec-1126-brown.html
sleep 2
grab "https://the-decoder.com/mit-team-discovers-that-unrealistic-training-data-makes-ai-climate-predictions-more-reliable/" scout-raw/dec-1126-mit.html
sleep 2
grab "https://the-decoder.com/ai-agents-now-control-part-of-deepminds-compute-for-gemini-experiments-but-recursive-self-improvement-remains-distant/" scout-raw/dec-1126-deepmind.html
sleep 2
grab "https://the-decoder.com/anthropic-study-shows-the-hardest-part-of-adopting-ai-at-work-has-little-to-do-with-learning-the-tools/" scout-raw/dec-1126-anthropic-adopt.html
sleep 2
grab "https://the-decoder.com/novartis-ceo-says-ai-will-shave-four-years-off-drug-development-not-cure-all-disease/" scout-raw/dec-1126-novartis.html
echo PAGES2_DONE
