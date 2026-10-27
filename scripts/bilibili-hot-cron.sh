#!/usr/bin/env bash
# =============================================================================
# B站热门视频日报 - 每日 cron 入口脚本
#
# 调用 ~/.openclaw/workspace/scripts/bilibili_daily.py 执行。
# 优雅降级：
#   - 无 BILIBILI_COOKIES      → 匿名热门模式（无字幕/AI）
#   - 无 OPENROUTER_API_KEY    → 跳过 AI 总结/点评
#   - 无 SMTP_* / BILIBILI_RECIPIENTS → 仅生成本地报告
#
# 凭据全部通过环境变量传入，绝不硬编码。
# 推荐用法（写入 ~/.bashrc 或 systemd 环境文件）：
#   export BILIBILI_COOKIES="..."
#   export OPENROUTER_API_KEY="..."
#   export SMTP_EMAIL="..."
#   export SMTP_PASSWORD="..."
#   export BILIBILI_RECIPIENTS="a@b.com, c@d.com"
#
# Cron 行：
#   0 10 * * * /home/zhiping/.openclaw/workspace/scripts/bilibili-hot-cron.sh
# =============================================================================

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAILY_SCRIPT="$SCRIPT_DIR/bilibili_daily.py"
LOG_DIR="$HOME/.openclaw/workspace/logs"
LOG_FILE="$LOG_DIR/bilibili-hot-cron.log"

mkdir -p "$LOG_DIR"

{
  echo "============================================================"
  echo "📺 B站热门视频日报 cron 入口 - $(date '+%Y-%m-%d %H:%M:%S')"
  echo "============================================================"

  if [ ! -f "$DAILY_SCRIPT" ]; then
    echo "❌ 找不到 $DAILY_SCRIPT"
    exit 2
  fi

  python3 "$DAILY_SCRIPT"
  rc=$?

  echo "📋 退出码: $rc"
  echo "============================================================"
  exit $rc
} >> "$LOG_FILE" 2>&1