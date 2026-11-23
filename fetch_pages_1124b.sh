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
grab "https://the-decoder.com/nvidia-researchers-argue-huge-ai-context-windows-are-a-dead-end/" scout-raw/dec-1124-ctx.html
sleep 2
grab "https://the-decoder.com/openais-own-researchers-now-say-they-value-their-ai-tools-more-than-nearly-half-their-colleagues/" scout-raw/dec-1124-tools.html
sleep 2
grab "https://the-decoder.com/meta-new-frontier-model-muse-wonder-full-breaks-into-the-ai-top-tier/" scout-raw/dec-1124-muse.html
sleep 2
grab "https://the-decoder.com/openais-data-suggests-that-frontier-models-are-hiding-their-thoughts-because-developers-optimize-for-capability-and-compute/" scout-raw/dec-1124-hide.html
sleep 2
grab "https://www.anthropic.com/news" scout-raw/anth-news-1124.html
sleep 2
grab "https://z.ai/blog/glm-5.4" scout-raw/glm-1124b.html
echo PAGES2_DONE
