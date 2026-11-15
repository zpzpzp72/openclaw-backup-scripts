#!/usr/bin/env bash
# ═══ NAS 回收站清理 —— 带空间守卫的调度入口 ═══
#
# 用途:把已有的 scripts/nas-recycle-cleanup.sh 挂上排程,消除「靠 agent 恰好想起」
#      (2026-11-15 实测:脚本质量很高但无调度引用,NAS 断档 9 天靠 Scout 手动调用才解除)
#
# 【为什么要守卫】
#   清理是不可逆操作。直接每天 --execute 是危险的:
#   - NAS 空间充足时没必要删(删了就少一层保险)
#   - 无条件删会让「保留期」形同虚设
#   → 只在【可用空间低于阈值】时才触发,且保留期仍由脚本自己的 --days 控制
#
# 【安全边界(全部沿用被调脚本自身的,此处不新增删除逻辑)】
#   1. 仅调用 nas-recycle-cleanup.sh,不自己 rm 任何东西
#   2. 被调脚本默认 dry-run,必须显式 --execute 才删
#   3. 被调脚本只删 openclaw-*.tgz 备份归档
#   4. 被调脚本逐个删除并校验,任一失败立即停止
#   5. 本守卫另加:空间充足则完全不执行(不传 --execute)
set -uo pipefail

SCRIPT_DIR="/home/zhiping/.openclaw/workspace/scripts"
CLEANUP="$SCRIPT_DIR/nas-recycle-cleanup.sh"
LOG="/home/zhiping/.openclaw/logs/nas-recycle-guard.log"
NAS_MOUNT="/mnt/h"
THRESHOLD_GB=64      # 低于此可用空间才触发清理
DAYS=14             # 保留期(与 NAS 主备份的 30 天形成梯度)

mkdir -p "$(dirname "$LOG")"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"; }

[ -x "$CLEANUP" ] || [ -f "$CLEANUP" ] || { log "❌ 找不到 $CLEANUP,退出"; exit 1; }

AVAIL=$(df -BG "$NAS_MOUNT" 2>/dev/null | tail -1 | awk '{gsub("G","",$4); print $4}')
if [ -z "$AVAIL" ]; then
  log "❌ 读不到 NAS 可用空间,退出(不做任何删除)"
  exit 1
fi

if [ "$AVAIL" -ge "$THRESHOLD_GB" ]; then
  log "ℹ️ NAS 可用 ${AVAIL}G >= 阈值 ${THRESHOLD_GB}G,无需清理(跳过)"
  exit 0
fi

log "⚠️ NAS 可用仅 ${AVAIL}G < 阈值 ${THRESHOLD_GB}G,触发回收站清理(--days $DAYS)"
bash "$CLEANUP" --execute --days "$DAYS" >> "$LOG" 2>&1
RC=$?
log "清理脚本退出码: $RC"
exit $RC
