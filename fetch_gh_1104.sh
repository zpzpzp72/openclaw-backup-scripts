#!/bin/bash
cd /home/zhiping/.openclaw/workspace
S=1104
REPOS="modelcontextprotocol/servers modelcontextprotocol/modelcontextprotocol modelcontextprotocol/registry modelcontextprotocol/inspector modelcontextprotocol/python-sdk modelcontextprotocol/typescript-sdk modelcontextprotocol/go-sdk anthropics/anthropic-sdk-python anthropics/claude-code openai/openai-python vercel/ai"
for r in $REPOS; do
  tag=$(echo $r | tr '/' '-')
  gh api "repos/$r/releases?per_page=4" > scout-raw/gh-$S-$tag-releases.json 2>/dev/null
  sleep 0.4
done
for r in modelcontextprotocol/servers modelcontextprotocol/modelcontextprotocol openai/openai-python vercel/ai anthropics/claude-code; do
  tag=$(echo $r | tr '/' '-')
  gh api "repos/$r/commits?since=2026-11-02T00:00:00Z&per_page=15" > scout-raw/gh-$S-$tag-commits.json 2>/dev/null
  sleep 0.4
done
gh api "repos/modelcontextprotocol/servers/security-advisories?per_page=30" > scout-raw/gh-$S-servers-advisories.json 2>/dev/null
sleep 0.5
gh api "repos/modelcontextprotocol/registry/security-advisories?per_page=30" > scout-raw/gh-$S-registry-advisories.json 2>/dev/null
echo GH_DONE
for f in scout-raw/gh-1104-*; do echo "$f $(wc -c < $f)"; done
