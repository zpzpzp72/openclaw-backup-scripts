#!/bin/bash
cd /home/zhiping/.openclaw/workspace
S=1123
REPOS="modelcontextprotocol/servers modelcontextprotocol/modelcontextprotocol modelcontextprotocol/registry modelcontextprotocol/inspector modelcontextprotocol/python-sdk modelcontextprotocol/typescript-sdk modelcontextprotocol/go-sdk anthropics/anthropic-sdk-python anthropics/claude-code openai/openai-python vercel/ai"
SINCE="2026-11-22T00:00:00Z"
fetch_api() {
  local path="$1" out="$2" tmp="/tmp/ghb.$$"
  for i in 1 2 3; do
    : > "$tmp"
    timeout 45 gh api "$path" > "$tmp" 2>/dev/null
    if [ -s "$tmp" ]; then
      if head -c 200 "$tmp" | grep -q 'rate limit exceeded'; then echo "  ratelimited $path"; sleep 5; continue; fi
      mv "$tmp" "$out"; echo "OK $(wc -c < "$out") $out"; return 0
    fi
    sleep 3
  done
  rm -f "$tmp"; echo "FAIL $out" >&2; return 1
}
for r in $REPOS; do
  tag=$(echo $r | tr '/' '-')
  fetch_api "repos/$r/releases?per_page=6" "scout-raw/gh-$S-$tag-releases.json"
  sleep 0.3
done
for r in modelcontextprotocol/servers modelcontextprotocol/modelcontextprotocol openai/openai-python vercel/ai anthropics/claude-code anthropics/anthropic-sdk-python; do
  tag=$(echo $r | tr '/' '-')
  fetch_api "repos/$r/commits?since=$SINCE&per_page=20" "scout-raw/gh-$S-$tag-commits.json"
  sleep 0.3
done
fetch_api "repos/modelcontextprotocol/servers/security-advisories?per_page=30" "scout-raw/gh-$S-servers-advisories.json"
sleep 0.5
fetch_api "repos/modelcontextprotocol/registry/security-advisories?per_page=30" "scout-raw/gh-$S-registry-advisories.json"
echo GH_DONE
