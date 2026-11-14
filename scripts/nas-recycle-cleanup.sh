#!/usr/bin/env bash
# =============================================================================
# nas-recycle-cleanup.sh — 清空 NAS SMB 回收站里的过期备份归档（释放空间）
#
# 【为什么需要它】
#   NAS 通过 9p(drvfs) 挂载，删除文件不会真删，而是移入 `#recycle/` 回收站，
#   于是空间被回收站静默吃满。2026-11-08 实测：#recycle 里积压 27 份归档 / 123GB，
#   /mnt/h 可用仅剩 4G → NAS 备份脚本每天 03:00 因空间预检失败而跳过（连着 3 天）。
#
# 【关键实测结论 —— 2026-11-08】
#   ✅ 删除「#recycle 目录内部」的文件 → 空间【立即真释放】（实测 delta 53,223,424 字节）
#   ❌ 删除「#recycle 目录外部」的文件 → 只是移入 #recycle，空间【不释放】
#   ❌ 用 ':' 前缀创建文件 → 并不会绕过回收站拦截（实测 ':bypass.bin' 同样落在 #recycle）
#
#   ⇒ 所以：必须直接删 #recycle 里已经没用的老归档，才真正腾出空间。
#
# 【安全设计】
#   1. 默认 DRY RUN：只打印将要删除的文件与可释放体积，不做任何删除
#   2. 必须显式传 --execute 才真正删除
#   3. 只删 openclaw-*.tgz 备份归档，不碰其他任何文件
#   4. 只删「N 天前」的（默认 14 天，与 NAS 主备份的 30 天保留期形成梯度）
#   5. 逐个删除并校验，任一失败立即停止
#   6. 删除前后都打印 NAS 可用空间
#
# 【用法】
#   bash nas-recycle-cleanup.sh                 # 预演（默认，不删）
#   bash nas-recycle-cleanup.sh --days 7        # 只处理 7 天前的
#   bash nas-recycle-cleanup.sh --execute       # 真正执行
# =============================================================================
set -uo pipefail

RECYCLE_DIR="/mnt/h/#recycle/AI/openclaw.zone/WSL"
NAS_MOUNT="/mnt/h"
EXECUTE=0
DAYS=14

while [ $# -gt 0 ]; do
    case "$1" in
        --execute) EXECUTE=1; shift;;
        --days)    DAYS="$2"; shift 2;;
        -h|--help) sed -n '2,30p' "$0"; exit 0;;
        *) echo "未知参数: $1"; exit 2;;
    esac
done

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

if [ ! -d "$RECYCLE_DIR" ]; then
    log "❌ 回收站目录不存在: $RECYCLE_DIR"
    exit 1
fi

free_gb() { df -BG "$NAS_MOUNT" 2>/dev/null | tail -1 | awk '{gsub("G","",$4); print $4}'; }

BEFORE_GB=$(free_gb)
log "回收站: $RECYCLE_DIR"
log "NAS 可用空间（删除前）: ${BEFORE_GB}G"
log "模式: $([ "$EXECUTE" = "1" ] && echo '★ 执行删除' || echo '预演（不删除）')  保留天数阈值: ${DAYS} 天"

# 收集候选：仅 openclaw-*.tgz，且 mtime 超过阈值
CANDIDATES=()
while IFS= read -r f; do
    [ -n "$f" ] && CANDIDATES+=("$f")
done < <(find "$RECYCLE_DIR" -maxdepth 1 -name 'openclaw-*.tgz' -type f -mtime "+$DAYS" 2>/dev/null | sort)

if [ "${#CANDIDATES[@]}" -eq 0 ]; then
    log "✓ 无符合条件的归档（无 openclaw-*.tgz 超过 ${DAYS} 天）"
    log "  提示：若要释放更多空间，可放宽 --days（回收站内最新一份见下）"
    find "$RECYCLE_DIR" -maxdepth 1 -name 'openclaw-*.tgz' -type f -printf '%TY-%Tm-%Td %10s %f\n' 2>/dev/null | sort -r | head -5
    exit 0
fi

# 统计体积（逐文件 stat，避免 du 在 9p 上挂起）
TOTAL=0
log "候选 ${#CANDIDATES[@]} 份："
for f in "${CANDIDATES[@]}"; do
    s=$(stat -c %s "$f" 2>/dev/null) || s=0
    TOTAL=$((TOTAL + s))
    printf '  %s  %10s  %s\n' "$(date -r "$f" '+%Y-%m-%d')" "$(numfmt --to=iec "$s" 2>/dev/null || echo "$s")" "$(basename "$f")"
done
log "合计可释放: $((TOTAL / 1024 / 1024 / 1024)) GB (${TOTAL} 字节)"

if [ "$EXECUTE" != "1" ]; then
    log "—— 预演结束，未删除任何文件。真正执行请加 --execute ——"
    exit 0
fi

log "开始删除（逐个校验，失败即停）..."
DELETED=0; FAILED=0; FREED=0
for f in "${CANDIDATES[@]}"; do
    s=$(stat -c %s "$f" 2>/dev/null) || s=0
    if rm -f "$f" 2>/dev/null && [ ! -e "$f" ]; then
        DELETED=$((DELETED + 1)); FREED=$((FREED + s))
        log "  ✅ $(basename "$f")"
    else
        FAILED=$((FAILED + 1))
        log "  ❌ 删除失败: $f —— 停止"
        break
    fi
done

AFTER_GB=$(free_gb)
log "删除完成: 成功 ${DELETED} 份, 失败 ${FAILED} 份, 文件体积合计 $((FREED / 1024 / 1024 / 1024)) GB"
log "NAS 可用空间（删除后）: ${AFTER_GB}G （删除前 ${BEFORE_GB}G）"
log "下一步：NAS 备份脚本需要约 6G 可用空间，现在应可正常产出归档"
