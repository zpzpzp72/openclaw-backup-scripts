#!/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/zhiping/.local/share/pnpm:/home/zhiping/.openclaw/workspace/scripts

# OpenClaw 自动备份脚本（带旧文件清理）
# 每天凌晨执行，检查目录修改后备份并发送邮件
#
# 修复记录 (2026-03-13):
# - 改回使用 openclaw gateway stop/start（避免 systemctl）
# - 屏蔽 systemctl 报错
# - 自动清理旧备份 (新增)
# - 优化 gateway stop/start 稳定性

BACKUP_DIR="/mnt/h/AI/openclaw.zone/WSL"
SOURCE_DIR="$HOME/.openclaw"
LOG_FILE="$HOME/.openclaw-backup.log"
RETAIN_DAYS=30   # ⭐ 保留天数，可以改为 14/30
# 获取当前时间
NOW=$(date "+%Y%m%d-%H%M")
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 查找最新备份文件
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/openclaw-*.tgz 2>/dev/null | head -1)

# 判断是否需要备份
if [ -z "$LATEST_BACKUP" ]; then
    # 没有历史备份，需要备份
    NEED_BACKUP=true
    LAST_MOD_TIME="1970-01-01"
else
    # 获取上次备份的时间
    LAST_MOD_TIME=$(stat -c %y "$LATEST_BACKUP" | cut -d'.' -f1)
    # 获取源目录的最近修改时间
    SOURCE_MOD_TIME=$(find "$SOURCE_DIR" -type f -newer "$LATEST_BACKUP" -printf "%T+\n" 2>/dev/null | head -1)

    if [ -n "$SOURCE_MOD_TIME" ]; then
        NEED_BACKUP=true
    else
        NEED_BACKUP=false
    fi
fi

log() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# 邮件通知
send_mail() {
    local subject="$1"
    local body="$2"
    cd ~/.openclaw/workspace/agents/finance && \
    python3 send_email.py \
        --provider qq \
        --to "9892890@qq.com" \
        --subject "$subject" \
        --body "$body" 2>> "$LOG_FILE"
}

##############################################
# 自动清理旧备份（新增）
##############################################
cleanup_old() {
    find "$BACKUP_DIR" -name "openclaw-*.tgz" -mtime +$RETAIN_DAYS \
        -exec rm -f {} \;

    log "清理超过 $RETAIN_DAYS 天的旧备份完成"
}

##############################################
# 停止 gateway
##############################################
stop_gateway() {
    log "Checking gateway process..."

    # Gateway 实际进程匹配（更稳健）
    gateway_pid=$(pgrep -f "openclaw-gateway" || true)

    if [ -z "$gateway_pid" ]; then
        log "Gateway process not running"
        return 0
    fi

    log "Gateway running (PID=$gateway_pid), sending stop..."

    # 直接调用 openclaw gateway stop
    timeout 20s openclaw gateway stop 2>&1 | grep -v "systemctl is-enabled unavailable" >> "$LOG_FILE"
    stop_result=$?

    if [ $stop_result -eq 0 ]; then
        log "Gateway stop command completed"
    else
        log "Gateway stop timeout/failed, forcing kill..."
        kill "$gateway_pid" 2>/dev/null || true
        sleep 1

        if kill -0 "$gateway_pid" 2>/dev/null; then
            log "Force killing with SIGKILL..."
            kill -9 "$gateway_pid" 2>/dev/null || true
        fi
    fi

    sleep 2
    # 确认已停止
    if kill -0 "$gateway_pid" 2>/dev/null; then
        log "Gateway stop failed"
        return 1
    fi

    log "Gateway stopped successfully"
    return 0
}

##############################################
# 重启 gateway
##############################################
restart_gateway() {
    log "Starting gateway..."

    timeout 60s openclaw gateway start 2>&1 \
        | grep -v "systemctl" >> "$LOG_FILE"

    # 等待进程启动
    sleep 5

    # 验证是否已启动
    if openclaw gateway status 2>/dev/null \
         | grep -q "RPC probe: ok"; then
        log "Gateway started successfully"
        return 0
    fi

    log "Gateway failed to start"
    return 1
}

##############################################
# 主备份流程
##############################################

log "上次备份文件: $LATEST_BACKUP"

if [ "$NEED_BACKUP" = true ]; then
    log "开始备份，源目录自 $LAST_MOD_TIME 后有修改"

    send_mail "OpenClaw 备份开始 - $NOW" \
              "备份开始于 $TIMESTAMP，源目录自 $LAST_MOD_TIME 后已修改。日志：$LOG_FILE"

    log "备份开始邮件已发送"

    if ! stop_gateway; then
        log "停止 gateway 失败"
        send_mail "OpenClaw 备份失败 - $NOW" "停止 gateway 失败！
时间: $TIMESTAMP
日志: $LOG_FILE"
        restart_gateway
        exit 1
    fi

    # 等待一下确保进程完全退出
    sleep 3
    
    # 执行备份
    log "执行 tar 备份..."
    ARCHIVE="$BACKUP_DIR/openclaw-$NOW.tgz"
	log "tar -czf $ARCHIVE -C $HOME .openclaw 2>> $LOG_FILE"
    #tar -czf "$ARCHIVE" -C "$HOME" .openclaw 2>>"$LOG_FILE"
    BACKUP_STATUS=$?

    if ! restart_gateway; then
        FILE_SIZE=$(du -h "$ARCHIVE" 2>/dev/null | cut -f1)
        log "备份成功但 gateway 重启失败: $ARCHIVE ($FILE_SIZE)"
        send_mail "OpenClaw 备份部分成功 - $NOW" \
                  "备份成功但 gateway 重启失败：
文件: $ARCHIVE
大小: $FILE_SIZE
时间: $TIMESTAMP

⚠️ 请手动检查 gateway 状态: openclaw status"
        exit 1
    fi

    if [ $BACKUP_STATUS -eq 0 ]; then
        FILE_SIZE=$(du -h "$ARCHIVE" | cut -f1)
        log "备份成功: $ARCHIVE ($FILE_SIZE)"

        send_mail "OpenClaw 备份完成 - $NOW" \
                  "源目录自 $LAST_MOD_TIME后有修改，备份成功：

文件: $ARCHIVE
大小: $FILE_SIZE
时间: $TIMESTAMP"
        log "备份完成邮件已发送"

        ############ 清理旧备份（新增）############
        cleanup_old

    else
        log "备份失败"
        send_mail "OpenClaw 备份失败 - $NOW" "tar 出错，请检查日志：$LOG_FILE"
    fi

else
    log "无需备份，源目录自 $LAST_MOD_TIME 后无修改"
    # 不发送通知
fi