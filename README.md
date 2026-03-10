# OpenClaw Backup Scripts

OpenClaw 自动备份脚本与配置。

## 功能

- 自动检测源目录是否有修改
- 有修改时才执行备份（增量备份逻辑）
- 备份前停止 Gateway，备份后自动重启
- 邮件通知备份结果（成功/失败）
- 备份文件命名：`openclaw-YYYYMMDD-HHMM.tgz`

## 文件说明

| 文件 | 说明 |
|------|------|
| `openclaw-backup.sh` | 主备份脚本 |
| `crontab.example` | 定时任务配置示例 |
| `README.md` | 说明文档 |

## 配置

### 1. 备份目录

确保备份目标目录存在：
```bash
mkdir -p /mnt/h/AI/openclaw.zone/WSL
```

### 2. 定时任务

添加 crontab 任务（每天凌晨 3 点执行）：
```bash
# 查看当前 crontab
crontab -l

# 编辑 crontab
crontab -e
# 添加以下行：
# 0 3 * * * /home/zhiping/.openclaw/workspace/scripts/openclaw-backup.sh >> /home/zhiping/.openclaw-backup-cron.log 2>&1
```

### 3. 邮件配置

脚本使用 `agents/finance/send_email.py` 发送邮件，确保：
- 该脚本存在且可执行
- QQ 邮箱 SMTP 配置正确

## 日志

- 备份日志：`~/.openclaw-backup.log`
- Crontab 日志：`~/.openclaw-backup-cron.log`

## 还原

```bash
# 停止 gateway
openclaw gateway stop

# 还原
cd ~
tar -xzf /mnt/h/AI/openclaw.zone/WSL/openclaw-YYYYMMDD-HHMM.tgz

# 重启 gateway
openclaw gateway start
```
