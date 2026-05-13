#!/bin/bash

#==========================================
# OpenClaw 升级脚本
# 用途：自动检查并升级 OpenClaw 到最新版本
#==========================================

set -e

# 配置
REPO_URL="https://github.com/openclaw/openclaw.git"
LOCAL_REPO="/home/zhiping/.openclaw/openclaw-source"
LOG_FILE="/home/zhiping/.openclaw/logs/upgrade_$(date +%Y%m%d_%H%M%S).log"
EMAIL_TO="9892890@qq.com"
EMAIL_SUBJECT="OpenClaw 升级报告 $(date +%Y-%m-%d\ %H:%M)"

# 创建日志目录
mkdir -p ~/.openclaw/logs

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" | tee -a "$LOG_FILE"
}

#==========================================
# 步骤 1: 获取版本信息
#==========================================
log "=========================================="
log "步骤 1: 检查版本信息"
log "=========================================="

# 获取本地已安装版本
LOCAL_VERSION=$(openclaw --version 2>/dev/null | awk '{print $2}')
log "本地已安装版本: $LOCAL_VERSION"

# 获取最新版本
cd "$LOCAL_REPO"
CUR_BRANCH=$(git branch --show-current)
log "Current git branch: $CUR_BRANCH "
log "执行: git checkout main"
if git checkout main >> "$LOG_FILE" 2>&1; then
    log "源码已切回: git checkout main"
fi
LATEST_VERSION=$(git show upstream/main:package.json | grep '"version"' | sed 's/.*"version": *"\([^"]*\)".*/\1/')
log "最新源码版本: $LATEST_VERSION"

#==========================================
# 步骤 2: 版本比较
#==========================================
log "=========================================="
log "步骤 2: 版本比较"
log "=========================================="

# 简单版本比较 (仅比较数字部分)
LOCAL_NUM=$(echo "$LOCAL_VERSION" | sed 's/[^0-9.]//g')
LATEST_NUM=$(echo "$LATEST_VERSION" | sed 's/[^0-9.]//g')

log "本地版本号: $LOCAL_NUM"
log "最新版本号: $LATEST_NUM"

# 使用 sort -V 进行版本排序
IS_NEWER=$(echo -e "$LOCAL_NUM\n$LATEST_NUM" | sort -V -r | head -1)
if [ "$IS_NEWER" != "$LATEST_NUM" ]; then
    log "最新版本 ($LATEST_NUM) 不比本地版本 ($LOCAL_NUM) 新，无需升级"
    log "升级脚本执行完成"
    exit 0
fi

log "检测到新版本! 开始升级流程..."

#==========================================
# 步骤 3: 备份配置
#==========================================
log "=========================================="
log "步骤 3: 备份当前配置"
log "=========================================="

BACKUP_FILE="$HOME/.openclaw/openclaw.json.bak.$(date +%Y%m%d_%H%M%S)"
cp ~/.openclaw/openclaw.json "$BACKUP_FILE"
log "配置已备份到: $BACKUP_FILE"

# 克隆/更新源码仓库
cd "$LOCAL_REPO"
if [ -d "$LOCAL_REPO/.git" ]; then
    log "更新源码仓库:git fetch origin main ..."
	if git fetch upstream main >> "$LOG_FILE" 2>&1; then
		log "git fetch upstream main - done!"
	else
		error "源码更新失败"
	fi
	git reset --hard upstream/main 
	log "源码已更新"
else
    log "克隆源码仓库:git clone ..."
	if git clone "$REPO_URL" "$LOCAL_REPO" >> "$LOG_FILE" 2>&1; then
		log "源码已克隆"
	else
		error "源码克隆失败"
	fi
fi

#==========================================
# 步骤 4: 停止 Gateway
#==========================================
log "=========================================="
log "步骤 4: 停止 Gateway"
log "=========================================="

log "执行: openclaw gateway stop"
if openclaw gateway stop >> "$LOG_FILE" 2>&1; then
    log "Gateway 已停止"
else
    error "Gateway 停止失败"
    # 继续尝试
fi

sleep 2

#==========================================
# 步骤 5: 编译
#==========================================
log "=========================================="
log "步骤 5: 编译 OpenClaw"
log "=========================================="

log "执行: pnpm install"
if pnpm install >> "$LOG_FILE" 2>&1; then
    log "依赖安装成功"
else
    error "依赖安装失败"
    COMPILE_ERROR=1
fi

if [ -z "$COMPILE_ERROR" ]; then
    log "执行: pnpm ui:build"
    if pnpm ui:build >> "$LOG_FILE" 2>&1; then
        log "UI 构建成功"
    else
        error "UI 构建失败"
        COMPILE_ERROR=1
    fi
fi

if [ -z "$COMPILE_ERROR" ]; then
    log "执行: pnpm build"
    if pnpm build >> "$LOG_FILE" 2>&1; then
        log "主程序编译成功"
    else
        error "主程序编译失败"
        COMPILE_ERROR=1
    fi
fi

#==========================================
# 步骤 6: 验证配置兼容性
#==========================================
log "=========================================="
log "步骤 6: 验证配置兼容性"
log "=========================================="

if [ -z "$COMPILE_ERROR" ]; then
    log "执行: openclaw doctor --non-interactive"
    DOCTOR_OUTPUT=$(openclaw doctor --non-interactive 2>&1 || echo "")
    
    if echo "$DOCTOR_OUTPUT" | grep -qi "error\|invalid\|failed"; then
        log "检测到配置问题，尝试修复..."
        log "执行: openclaw doctor --fix"
        openclaw doctor --fix --non-interactive >> "$LOG_FILE" 2>&1 || true
    else
        log "配置验证通过"
    fi
fi

#==========================================
# 步骤 7: 启动 Gateway
#==========================================
log "=========================================="
log "步骤 7: 启动 Gateway"
log "=========================================="

if [ -z "$COMPILE_ERROR" ]; then
    log "执行: openclaw gateway start"
    if openclaw gateway start >> "$LOG_FILE" 2>&1; then
        log "Gateway 已启动"
    else
        error "Gateway 启动失败"
    fi
    
    sleep 3
else
    log "由于编译错误，跳过 Gateway 启动"
fi

#==========================================
# 步骤 8: 收集状态信息并发送邮件
#==========================================
log "=========================================="
log "步骤 8: 收集状态并发送邮件"
log "=========================================="

# 获取状态
GATEWAY_STATUS=$(openclaw gateway status 2>&1 || echo "无法获取状态")
OPENCLAW_STATUS=$(openclaw status 2>&1 || echo "无法获取状态")

# 检查状态是否正常，如有问题则运行 doctor 修复
log "检查 OpenClaw 状态..."
STATUS_OK=true
if echo "$GATEWAY_STATUS" | grep -qi "error\|failed\|not running\|stopped"; then
    STATUS_OK=false
fi

if echo "$OPENCLAW_STATUS" | grep -qi "error\|failed"; then
    STATUS_OK=false
fi

if [ "$STATUS_OK" = false ]; then
    log "状态异常，尝试修复..."
    log "执行: openclaw doctor"
    DOCTOR_OUTPUT=$(openclaw doctor 2>&1 || echo "doctor 执行失败")
    log "Doctor 输出: $DOCTOR_OUTPUT"
    
    # 修复后重新启动 Gateway
    log "重新启动 Gateway..."
    openclaw gateway restart >> "$LOG_FILE" 2>&1
    sleep 2
    
    # 再次收集状态
    log "重新收集状态信息..."
    GATEWAY_STATUS=$(openclaw gateway status 2>&1 || echo "无法获取状态")
    OPENCLAW_STATUS=$(openclaw status 2>&1 || echo "无法获取状态")
fi

# 生成邮件内容
EMAIL_BODY="OpenClaw 升级报告

==========================================
基本信息
==========================================
升级时间: $(date '+%Y-%m-%d %H:%M:%S')
本地原版本: $LOCAL_VERSION
最新源码版本: $LATEST_VERSION
编译结果: $([ -z "$COMPILE_ERROR" ] && echo "成功" || echo "失败")

==========================================
Gateway 状态
==========================================
$GATEWAY_STATUS

==========================================
OpenClaw 状态
==========================================
$OPENCLAW_STATUS

==========================================
日志文件路径
==========================================
$LOG_FILE

==========================================
Doctor 修复信息
==========================================
$(if [ "$STATUS_OK" = false ]; then
    echo "$DOCTOR_OUTPUT"
else
    echo "无需修复"
fi)

==========================================
编译错误信息
==========================================
$(if [ -n "$COMPILE_ERROR" ]; then
    echo "编译过程中出现错误，请查看日志文件: $LOG_FILE"
    echo ""
    echo "=== 最后 50 行日志 ==="
    tail -50 "$LOG_FILE"
else
    echo "无编译错误"
fi)

==========================================
脚本执行完成
==========================================
"

# 发送邮件 (使用 Python)
python3 << EOF
import smtplib
from email.mime.text import MIMEText
import os

msg = MIMEText("""$EMAIL_BODY""", 'plain', 'utf-8')
msg['Subject'] = '$EMAIL_SUBJECT'
msg['From'] = 'openclaw@localhost'
msg['To'] = '$EMAIL_TO'

try:
    # 使用本地 SMTP (如果是 WSL 或有 SMTP 配置)
    server = smtplib.SMTP('localhost')
    server.send_message(msg)
    server.quit()
    print("邮件发送成功")
except Exception as e:
    # 尝试使用 Gmail SMTP
    try:
        import getpass
        sender = os.environ.get('GMAIL_SENDER')
        password = os.environ.get('GMAIL_APP_PASSWORD')
        if sender and password:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            print("邮件发送成功 (Gmail)")
        else:
            print(f"邮件发送失败: {e}")
            print("请设置 GMAIL_SENDER 和 GMAIL_APP_PASSWORD 环境变量")
    except Exception as e2:
        print(f"邮件发送失败: {e2}")
EOF

log "邮件发送完成"
log "=========================================="
log "升级脚本执行完成"
log "=========================================="
