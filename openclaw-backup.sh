#!/bin/bash
# OpenClaw 自动备份脚本
# 每天凌晨执行，检查目录修改后备份并发送邮件

BACKUP_DIR="/mnt/h/AI/openclaw.zone/WSL"
SOURCE_DIR="$HOME/.openclaw"
LOG_FILE="$HOME/.openclaw-backup.log"

# 获取当前时间
NOW=$(date "+%Y%m%d-%H%M")
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 查找最新备份文件
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/openclaw-*.tgz 2>/dev/null | head -1)

# 检查是否需要备份
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

if [ "$NEED_BACKUP" = true ]; then
    log "开始备份，源目录自 $LAST_MOD_TIME 后有修改"
    
    # 停止 gateway
    openclaw gateway stop >> "$LOG_FILE" 2>&1
    sleep 2
    
    # 执行备份
    tar -czf "$BACKUP_DIR/openclaw-$NOW.tgz" -C "$HOME" .openclaw 2>> "$LOG_FILE"
    
    BACKUP_STATUS=$?
    
    # 重启 gateway
    openclaw gateway start >> "$LOG_FILE" 2>&1
    
    if [ $BACKUP_STATUS -eq 0 ]; then
        FILE_SIZE=$(du -h "$BACKUP_DIR/openclaw-$NOW.tgz" | cut -f1)
        log "备份成功: openclaw-$NOW.tgz ($FILE_SIZE)"
        
        # 发送邮件 via Gmail
        cd ~/.openclaw/workspace/agents/finance && \
        python3 send_email.py \
            --provider qq \
            --to "9892890@qq.com" \
            --subject "OpenClaw 备份完成 - $NOW" \
            --body "备份成功！

文件: openclaw-$NOW.tgz
大小: $FILE_SIZE
时间: $TIMESTAMP

源目录自 $LAST_MOD_TIME 后有修改，已自动备份。"
        
        log "邮件已发送"
    else
        log "备份失败"
        
        # 发送失败邮件
        cd ~/.openclaw/workspace/agents/finance && \
        python3 send_email.py \
            --provider qq \
            --to "9892890@qq.com" \
            --subject "OpenClaw 备份失败 - $NOW" \
            --body "备份失败！

时间: $TIMESTAMP
请检查日志: $LOG_FILE"
    fi
else
    log "无需备份，源目录自 $LAST_MOD_TIME 后无修改"
    # 不发送通知
fi
