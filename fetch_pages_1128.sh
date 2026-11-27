#!/bin/bash
cd /home/zhiping/.openclaw/workspace
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
SANITIZER="/home/zhiping/.openclaw/workspace/scripts/sanitize-secrets.py"
grab() {
  for i in 1 2 3; do
    if curl -sSL --max-time 60 -A "$UA" "$1" -o "$2" && [ -s "$2" ] && [ "$(wc -c < "$2")" -gt 200 ]; then
      echo "OK $(wc -c < "$2") $2"
      [ -f "$SANITIZER" ] && python3 "$SANITIZER" "$2" >/dev/null 2>&1 || true
      return 0
    fi
    echo "  retry$i $2" >&2; sleep 4
  done
  echo "FAIL $2" >&2; return 1
}
# --- The Decoder: 6 new articles (11-27 batch) ---
grab "https://the-decoder.com/hackers-breached-the-us-air-forces-flagship-cloud-one-platform-report-says/" scout-raw/dec-1128-cloudone.html
sleep 2
grab "https://the-decoder.com/openai-is-building-athena-data-platform-to-cut-down-on-ai-agent-guesswork/" scout-raw/dec-1128-athena.html
sleep 2
grab "https://the-decoder.com/rockstars-ai-dilemma-can-gta-6s-staggered-release-model-survive-coding-agents/" scout-raw/dec-1128-gta6.html
sleep 2
grab "https://the-decoder.com/sap-plans-to-cut-at-least-10000-jobs-as-it-pivots-to-ai/" scout-raw/dec-1128-sap.html
sleep 2
grab "https://the-decoder.com/former-openai-researcher-says-the-riemann-proof-matters-less-than-the-fact-that-an-ai-system-can-produce-it/" scout-raw/dec-1128-riemann.html
sleep 2
grab "https://the-decoder.com/gpt-6-2-astra-users-now-hit-limits-40-faster-after-openai-patched-a-pricing-error/" scout-raw/dec-1128-limits.html
sleep 2
# --- HN-linked primary sources ---
grab "https://cr.yp.to/proofs/falseccp.html" scout-raw/hn-1128-falseccp.html
sleep 2
grab "https://eprint.iacr.org/2026/3020.pdf" scout-raw/hn-1128-dlp.pdf
sleep 2
grab "https://devnull.land/amd-specific-llama-cpp" scout-raw/hn-1128-amd-llamacpp.html
sleep 2
grab "https://techstackups.com/articles/google-workspace-ai-agents-mcp/" scout-raw/hn-1128-google-mcp.html
sleep 2
grab "https://generativehistory.substack.com/p/gpt-62-astra-solves-a-historical" scout-raw/hn-1128-astra-mystery.html
sleep 2
grab "https://www.kimi.ai/news/kimi-for-science-program" scout-raw/hn-1128-kimi-science.html
sleep 2
grab "https://construct22.com/" scout-raw/hn-1128-construct22.html
sleep 2
grab "https://janlukas.blog/posts/ai-self-hosting" scout-raw/hn-1128-selfhosting.html
sleep 2
grab "https://www.eff.org/deeplinks/2026/11/new-york-and-california-age-gating-rules-go-into-effect-in-the-new-year" scout-raw/hn-1128-agegating.html
sleep 2
grab "https://thequantuminsider.com/2026/11/26/stanford-physicist-uses-ai-to-tackle-quantum-gravity-problem/" scout-raw/hn-1128-quantumgravity.html
sleep 2
grab "https://chrhenning.com/blog/2026/introduction-to-uncertainty/" scout-raw/hn-1128-uncertainty.html
sleep 2
grab "https://www.infohawk.com/news/2026-11-27-black-friday-webrtc-skimmer" scout-raw/hn-1128-webrtc-skimmer.html
sleep 2
grab "https://news.sky.com/story/us-air-forces-cloud-computing-platform-hacked-1361716" scout-raw/hn-1128-sky-af.html
sleep 2
# --- Google MCP / Workspace agents (context) ---
grab "https://developers.googleblog.com/en/" scout-raw/gb-1128-devblog.html
sleep 2
echo PAGES_DONE
