#!/usr/bin/env bash
# push 前密钥扫描闸门
# 背景: 2026-11-26 GitHub push protection 拦下含 Mapbox pk. token 的抓取产物,push 失败。
#       根因:Scout 抓网页原样入库,内容含 apiKey。
# 注: 不能用 grep -E 的 (?<!) 后顾断言(ERE 不支持)→ 会静默失效。改用 python。
set -uo pipefail
REPO="${1:-origin/feature/hot-backup}"
SCRIPT_DIR="/home/zhiping/.openclaw/workspace/scripts"
exec python3 "$SCRIPT_DIR/pre-push-secret-guard.py" "$REPO"
