#!/bin/bash
# 会话/链路体检 —— 只读,不消耗任何模型 token。
# 由 crontab 每日 07:00 调用(避开 03:00 备份与 08:00 news-digest 窗口)。
#
# 背景 (2026-11-28): 三个静默劣化型故障都是「不报错直到爆」才发现的:
#   1. 会话 contextTokens 被小上下文模型钉死(8192) -> 必然 overflow
#   2. 全局 fallback 链末位是小上下文模型 -> 落到末位就必炸
#   3. agent lease 失效 -> 写操作 100% 失败
#
# ★ 2026-11-28 修: cron 默认 PATH 是 /usr/bin:/bin,不含 /usr/local/bin,
#   而 openclaw CLI 在 /usr/local/bin/openclaw -> 之前 openclaw sessions
#   静默 rc=127,检查器却打印「未发现风险」(假阴性!)。本次加显式 PATH + 失败即报错。
set -uo pipefail

export PATH="/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"
export OPENCLAW_GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18789}"

WS=/home/zhiping/.openclaw/workspace
LOG="$WS/logs/session-health.log"
mkdir -p "$WS/logs"

{
  echo "===== $(date '+%Y-%m-%d %H:%M:%S %Z') ====="

  if ! command -v openclaw >/dev/null 2>&1; then
    echo "❌ 体检失败: PATH 里找不到 openclaw CLI (PATH=$PATH)"
    echo "   → 这是【检查器自身故障】,不是「系统无风险」。不要把这次结果当成正常。"
  else
    timeout 300 python3 "$WS/scripts/session-health-checker.py" 2>&1
    RC=$?
    echo "  [checker rc=$RC]"
    if [ "$RC" -eq 2 ]; then
      echo "  ❌ 体检未取得有效数据(rc=2),本轮结论【无效】,不要当成「无风险」。"
    fi
  fi
  echo
} >> "$LOG" 2>&1

# 保留最近 30 天
find "$WS/logs" -name 'session-health.log' -mtime +30 -delete 2>/dev/null
exit 0