#!/usr/bin/env bash
# =============================================================================
# native-backup.sh — 原生备份兜底（绕开 NAS 的 4G 限制与 SMB rm 只进回收站的坑）
#
# 为什么需要它（2026-11-07 实测）:
#   - NAS 那套 openclaw-backup.sh 连续 2 晚被「可用 4G < 需要 6G」预检拦截
#   - NAS 是 SMB 挂载, rm 只把文件移进 #recycle, RETAIN_DAYS 清理从不释放空间
#   - 原生 `openclaw backup create` 输出到 root 分区（797G 可用）, 与 NAS 完全解耦
#
# 关键约束:
#   - 输出目录**不能**位于 ~/.openclaw 内（工具会拒绝: "Backup output must not be
#     written inside a source path"）
#   - 必须用 --verify, 保证归档可还原
#
# 保留策略: 保留最近 KEEP 个归档（每个约 6.7GB），超出则删最旧的。
#   日期前缀文件名保证按字典序 == 按时间序。
# =============================================================================
set -uo pipefail

BACKUP_DIR="${BACKUP_DIR:-/home/zhiping/openclaw-backups}"
KEEP="${KEEP:-7}"
LOG_FILE="${LOG_FILE:-/home/zhiping/.openclaw/logs/native-backup.log}"

mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

# ★ 修复 (2026-11-07): 被杀掉的运行会留下 .openclaw-backup-publish-* staging 目录。
#   用 EXIT trap 保证无论正常结束、失败还是被 SIGTERM/SIGINT 打断，都清掉本次的 staging 目录。
#   （staging 目录名由 openclaw 生成，形如 .openclaw-backup-publish-<uuid>-<rand>，
#    运行开始时不存在、运行中由 openclaw 创建 —— 所以按 mtime 增量清理最安全）
STAGING_GLOB="$BACKUP_DIR/.openclaw-backup-publish-*"
cleanup_staging() {
  local d
  for d in $STAGING_GLOB; do
    [ -d "$d" ] || continue
    rm -rf "$d" 2>/dev/null && log "🧹 清理 staging 残留: $(basename "$d")"
  done
}
trap cleanup_staging EXIT INT TERM

log "=== native backup start (dir=$BACKUP_DIR keep=$KEEP) ==="

# 清理上一次残留的 staging 目录（上次被中断时会留下）
find "$BACKUP_DIR" -maxdepth 1 -name '.openclaw-backup-publish-*' -type d -mtime +1 \
  -exec rm -rf {} + 2>/dev/null
log "staging 残留检查完成（>1 天的已清理）"

BEFORE=$(df -BG --output=avail "$BACKUP_DIR" 2>/dev/null | tail -1 | tr -dc '0-9')
log "可用空间: ${BEFORE:-?}G"

if ! command -v openclaw >/dev/null 2>&1; then
  log "❌ openclaw 不在 PATH"
  exit 1
fi

OUT=$(timeout 3000 openclaw backup create --verify --output "$BACKUP_DIR" 2>&1)
RC=$?

if [ $RC -ne 0 ]; then
  log "❌ 备份失败 (rc=$RC)"
  echo "$OUT" | tail -20 | tee -a "$LOG_FILE"
  exit $RC
fi

ARCHIVE=$(echo "$OUT" | grep -oE "$BACKUP_DIR/[^ ]+\.tar\.gz" | tail -1)
if [ -z "$ARCHIVE" ] || [ ! -f "$ARCHIVE" ]; then
  log "❌ 未找到归档文件"
  echo "$OUT" | tail -20 | tee -a "$LOG_FILE"
  exit 1
fi

SIZE=$(du -h "$ARCHIVE" 2>/dev/null | cut -f1)
log "✅ 备份成功: $ARCHIVE ($SIZE)"

# 校验
if timeout 900 openclaw backup verify "$ARCHIVE" >>"$LOG_FILE" 2>&1; then
  log "✅ verify OK: $ARCHIVE"
else
  log "⚠️ verify 未通过（归档仍保留，请人工检查）: $ARCHIVE"
fi

# 保留策略：只留最近 KEEP 个
COUNT=$(ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
if [ "$COUNT" -gt "$KEEP" ]; then
  log "归档数 $COUNT > $KEEP，删除最旧的 $((COUNT - KEEP)) 个"
  ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -n $((COUNT - KEEP)) | while read -r old; do
    rm -f "$old" && log "  已删除旧归档: $(basename "$old")"
  done
fi

AFTER=$(df -BG --output=avail "$BACKUP_DIR" 2>/dev/null | tail -1 | tr -dc '0-9')
log "剩余空间: ${AFTER:-?}G"
log "=== native backup done ==="
exit 0
