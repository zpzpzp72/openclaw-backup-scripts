#!/bin/bash
# NightOps-Scout GitHub raw collection — 2026-11-14 (window 11-08 -> 11-14)
cd /home/zhiping/.openclaw/workspace
S=1117
UA="Mozilla/5.0 (X11; Linux x86_64) NightOps-Scout/1.0"
REPOS="modelcontextprotocol/servers modelcontextprotocol/modelcontextprotocol modelcontextprotocol/registry modelcontextprotocol/inspector modelcontextprotocol/python-sdk modelcontextprotocol/typescript-sdk modelcontextprotocol/go-sdk anthropics/anthropic-sdk-python anthropics/claude-code openai/openai-python vercel/ai"
SINCE="2026-11-15T00:00:00Z"

fetch_api() {
  local path="$1" out="$2" tmp="/tmp/ghout.$$" url="https://api.github.com/repos/$1"
  for i in 1 2 3; do
    : > "$tmp"
    timeout 40 curl -sS -H "Accept: application/vnd.github+json" -A "$UA" "$url" -o "$tmp" 2>/dev/null
    if [ -s "$tmp" ] && [ "$(wc -c < "$tmp")" -gt 100 ]; then
      mv "$tmp" "$out"; echo "OK curl $(wc -c < "$out") $out"; return 0
    fi
    if [ -s "$tmp" ] && [ "$(wc -c < "$tmp")" -le 100 ]; then
      mv "$tmp" "$out"; echo "OK small-response $(wc -c < "$out") $out"; return 0
    fi
    : > "$tmp"
    timeout 30 gh api "repos/$1" > "$tmp" 2>/dev/null
    if [ -s "$tmp" ] && [ "$(wc -c < "$tmp")" -gt 100 ]; then
      mv "$tmp" "$out"; echo "OK gh $(wc -c < "$out") $out"; return 0
    fi
    if [ -s "$tmp" ] && [ "$(wc -c < "$tmp")" -le 100 ]; then
      mv "$tmp" "$out"; echo "OK small-response(gh) $(wc -c < "$out") $out"; return 0
    fi
    echo "  retry$i empty $out" >&2
    sleep 3
  done
  rm -f "$tmp"
  echo "FAIL $out" >&2
  return 1
}

for r in $REPOS; do
  tag=$(echo $r | tr '/' '-')
  fetch_api "$r/releases?per_page=4" "scout-raw/gh-$S-$tag-releases.json"
  sleep 0.4
done

for r in modelcontextprotocol/servers modelcontextprotocol/modelcontextprotocol openai/openai-python vercel/ai anthropics/claude-code; do
  tag=$(echo $r | tr '/' '-')
  fetch_api "$r/commits?since=$SINCE&per_page=15" "scout-raw/gh-$S-$tag-commits.json"
  sleep 0.4
done

fetch_api "modelcontextprotocol/servers/security-advisories?per_page=30" "scout-raw/gh-$S-servers-advisories.json"
sleep 0.5
fetch_api "modelcontextprotocol/registry/security-advisories?per_page=30" "scout-raw/gh-$S-registry-advisories.json"

echo GH_DONE
for f in scout-raw/gh-$S-*; do echo "$f $(wc -c < $f)"; done
