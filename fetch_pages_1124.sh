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

grab "https://z.ai/blog/glm-5.4" scout-raw/glm-1124.html
sleep 2
grab "https://www.cnbc.com/2026/11/23/nvidia-jensen-huang-ceo.html" scout-raw/nvda-1124.html
sleep 2
grab "https://micjm.com/blog/yes-17m-lines-of-lean-is-a-lot/" scout-raw/lean-1124.html
sleep 2
grab "https://johncarlosbaez.wordpress.com/2026/11/22/masullo-on-the-riemann-hypothesis/" scout-raw/riemann-1124.html
sleep 2
grab "https://www.docker.com/blog/meet-the-new-docker-built-to-run-on-trust/" scout-raw/docker-1124.html
sleep 2
grab "https://the-decoder.com/gpt-6-2-astra-solved-a-math-theorem-no-other-ai-could-crack-then-invented-its-own-proof-strategy/" scout-raw/dec-1124-astra.html
sleep 2
grab "https://the-decoder.com/z-ai-follows-openai-into-loop-transformer-territory-with-its-new-750b-flagship-model/" scout-raw/dec-1124-glm.html
sleep 2
grab "https://the-decoder.com/nvidia-tried-life-without-jensen-huang-and-it-lasted-about-two-weeks/" scout-raw/dec-1124-nvda.html
sleep 2
grab "https://the-decoder.com/metas-alexandr-wang-warns-the-ai-industry-isnt-ready-for-whats-coming-after-riemann-breakthrough/" scout-raw/dec-1124-wang.html
sleep 2
grab "https://the-decoder.com/chinese-military-fears-ai-could-let-the-us-find-and-destroy-its-nuclear-missiles/" scout-raw/dec-1124-mil.html
echo PAGES_DONE
