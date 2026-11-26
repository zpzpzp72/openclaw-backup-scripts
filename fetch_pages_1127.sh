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
grab "https://the-decoder.com/after-openai-and-anthropic-shut-the-door-on-their-data-a-chinese-ai-developer-is-turning-to-google-and-meta-instead/" scout-raw/dec-1127-cndata.html
sleep 2
grab "https://the-decoder.com/fcc-clears-spacex-to-deploy-up-to-1-million-starmind-satellites-for-orbital-ai-data-centers-by-2040/" scout-raw/dec-1127-starmind.html
sleep 2
grab "https://the-decoder.com/microsoft-details-how-state-backed-hackers-use-the-artex-ai-framework-to-automate-cyberattacks/" scout-raw/dec-1127-artex.html
sleep 2
grab "https://the-decoder.com/nvidia-halts-server-shipments-to-malaysia-singapore-thailand-and-indonesia-after-tighter-us-export-controls/" scout-raw/dec-1127-nv-export.html
sleep 2
grab "https://the-decoder.com/us-chip-access-curbs-and-anti-distillation-measures-are-reportedly-already-slowing-chinese-ai-labs/" scout-raw/dec-1127-china-slow.html
sleep 2
grab "https://the-decoder.com/anthropic-ceo-dario-amodei-says-letting-ai-govern-society-would-be-a-bad-idea/" scout-raw/dec-1127-amodei.html
sleep 2
grab "https://the-decoder.com/openai-wants-companies-to-trust-it-with-sensitive-work-by-promising-not-to-look-at-their-data/" scout-raw/dec-1127-openai-noread.html
sleep 2
grab "https://the-decoder.com/amazon-and-meta-are-in-talks-to-end-the-block-on-metas-ai-shopping-agent-muse-in-amazons-online-store/" scout-raw/dec-1127-muse.html
sleep 2
grab "https://1password.com/blog/update-on-nov-2026-security-incident" scout-raw/op-1127-1password.html
sleep 2
grab "https://opensec.in/blog/nfs2root-cve-2026-99362" scout-raw/op-1127-nfs2root.html
sleep 2
grab "https://scottaaronson.blog/?p=10379" scout-raw/aaronson-1127.html
sleep 2
grab "https://bjin.github.io/go-codegolf-benchmark/" scout-raw/codegolf-1127.html
sleep 2
grab "https://github.com/alesha-pro/llm.asm/tree/main/02-baremetal-os" scout-raw/baremetal-qwen-1127.html
sleep 2
grab "https://www.theverge.com/ai-artificial-intelligence/1041227/the-new-york-times-warns-photographers-not-to-update-photoshop-over-ai-features" scout-raw/verge-nyt-1127.html
sleep 2
grab "https://github.com/lsernau/grh-lean" scout-raw/grh-lean-1127.html
sleep 2
grab "https://github.com/google-research/google-research/tree/4a7bc8ab0bc770e71a259b7966c500496b" scout-raw/cogentic-1127.html
echo PAGES_DONE
