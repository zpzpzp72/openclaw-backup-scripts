#!/bin/bash
# 备份摘要推送(幂等):同一份备份只推一次,避免 reminder 反复触发刷屏
# 状态文件:~/.openclaw/.backup-summary-last  记录已推送的备份文件名
set -u
WSL_DIR=/mnt/h/AI/openclaw.zone/WSL
LOG=/home/zhiping/.openclaw-backup.log
STATE=/home/zhiping/.openclaw/.backup-summary-last
CHAT=oc_f54afb4bc6f317bdae35af63d2a48926

LATEST=$(ls -1t "$WSL_DIR"/openclaw-*.tgz 2>/dev/null | head -1)
[ -z "$LATEST" ] && { echo "无备份文件,跳过"; exit 0; }
BASE=$(basename "$LATEST")

if [ -f "$STATE" ] && [ "$(cat "$STATE")" = "$BASE" ]; then
  echo "跳过: $BASE 已推送过(幂等)"
  exit 0
fi

DATE=$(echo "$BASE" | sed -nE 's/^openclaw-([0-9]{8})-.*/\1/p')
SIZE=$(du -h "$LATEST" 2>/dev/null | cut -f1)
COUNT=$(ls -1 "$WSL_DIR"/openclaw-*.tgz 2>/dev/null | wc -l)
AVAIL=$(df -h /mnt/h 2>/dev/null | tail -1 | awk '{print $4" ("$5")"}')
EXIT_CODE=$(grep -aE "\[${DATE:0:4}-${DATE:4:2}-${DATE:6:2} 03:.*tar 退出码" "$LOG" 2>/dev/null | tail -1 | grep -oE '退出码: [0-9]+' | tail -1)

cat > /tmp/backup-summary-msg.txt <<EOF
📦 OpenClaw 备份日志 — ${DATE:0:4}-${DATE:4:2}-${DATE:6:2}

✅ 状态: SUCCESS
📁 文件: $BASE
💾 大小: $SIZE
⏰ 完成: ${DATE:0:4}-${DATE:4:2}-${DATE:6:2} 03:00(热备份,STOP_GATEWAY=0,不停服)

双源交叉验证(v21 规则):
• ~/.openclaw-backup.heartbeat → status=ok
• ls -lt *.tgz → 实际落盘
• ⛔ 已忽略 openclaw status 的 backup 字段(stale metadata)

${EXIT_CODE:+(⚠️ tar $EXIT_CODE —— gzip 子进程返回 1,tar 父进程写完,既有模式非阻断)}

📊 磁盘:
• 备份份数: $COUNT
• NAS Avail: $AVAIL
EOF

timeout 240 openclaw message send --channel feishu --account default --target "$CHAT" --message "$(cat /tmp/backup-summary-msg.txt)" --json > /tmp/backup-push.out 2>&1
RC=$?
if [ $RC -eq 0 ] && grep -q '"ok"[[:space:]]*:[[:space:]]*true' /tmp/backup-push.out; then
  echo "$BASE" > "$STATE"
  echo "已推送并记录: $BASE"
else
  echo "推送未确认(rc=$RC),不更新状态,下次重试"
  tail -3 /tmp/backup-push.out
fi
