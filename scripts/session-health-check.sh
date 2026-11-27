#!/bin/bash
# 会话/链路体检 —— 只读,不消耗任何模型 token。
# 由 crontab 每日 07:40 调用(避开 03:00 备份与 08:00 news-digest 窗口)。
# 背景 (2026-11-28): 三个静默劣化型故障都是「不报错直到爆」才发现的:
#   1. 会话 contextTokens 被小上下文模型钉死(8192)→ 必然 overflow
#   2. 全局 fallback 链末位是小上下文模型 → 落到末位就必炸
#   3. agent lease 失效 → 写操作 100% 失败
# 这三个都可以用只读检查提前发现。
set -uo pipefail
WS=/home/zhiping/.openclaw/workspace
LOG="$WS/logs/session-health.log"
mkdir -p "$WS/logs"
{
  echo "===== $(date '+%Y-%m-%d %H:%M:%S %Z') ====="
  timeout 300 python3 "$WS/scripts/session-health-checker.py" 2>&1
  echo
} >> "$LOG" 2>&1
# 保留最近 30 天
find "$WS/logs" -name 'session-health.log' -mtime +30 -delete 2>/dev/null
exit 0
