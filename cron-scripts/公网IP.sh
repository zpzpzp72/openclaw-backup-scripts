#!/bin/bash
# 公网IP检查脚本
# 执行时间: 2026-07-25 05:30 CST

echo "=== 公网IP检查 $(date '+%Y-%m-%d %H:%M:%S CST') ==="

# 获取公网IP（多个备用源）
PUBLIC_IP=""
for url in "https://api.ipify.org" "https://icanhazip.com" "http://checkip.amazonaws.com" "https://ipecho.net/plain"; do
    PUBLIC_IP=$(curl -s --max-time 10 "$url" 2>/dev/null | tr -d '\n\r ')
    if [ -n "$PUBLIC_IP" ] && echo "$PUBLIC_IP" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
        break
    fi
    PUBLIC_IP=""
done

if [ -z "$PUBLIC_IP" ]; then
    echo "❌ 获取公网IP失败"
    exit 1
fi

echo "✅ 公网IP: $PUBLIC_IP"

# 检查IP变化（与上次记录对比）
LAST_IP_FILE="/home/zhiping/.openclaw/workspace/cron-scripts/.last_public_ip"
if [ -f "$LAST_IP_FILE" ]; then
    LAST_IP=$(cat "$LAST_IP_FILE")
    if [ "$PUBLIC_IP" != "$LAST_IP" ]; then
        echo "⚠️ IP已变更: $LAST_IP → $PUBLIC_IP"
        echo "$PUBLIC_IP" > "$LAST_IP_FILE"
    else
        echo "ℹ️ IP未变化"
    fi
else
    echo "ℹ️ 首次记录IP: $PUBLIC_IP"
    echo "$PUBLIC_IP" > "$LAST_IP_FILE"
fi

# 记录最后成功运行时刻(即使 IP 未变也写)
# 用途:区分「IP 没变」与「cron 任务失败/未执行」——
#      11-01 曾因该 cron 连续失败,导致 IP 实际已换(10-31 18:17)却 11 小时无人察觉。
LAST_RUN_FILE="/home/zhiping/.openclaw/workspace/cron-scripts/.last_public_ip_run"
date '+%Y-%m-%d %H:%M:%S' > "$LAST_RUN_FILE"

echo "=== 检查完成 ==="
