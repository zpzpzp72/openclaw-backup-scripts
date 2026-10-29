# Coder 夜检存档 — 2026-10-30

- OpenClaw：本地 2026.10.5，npm latest 2026.10.9（⚠️ 10-29 23:46 CST 发布、0 天新鲜度，风险偏高）；升级前检查清单已备好（822f46fd），执行待 owner 授权 + 维护窗口；若求稳可观察 24~48h 或选浸泡 2 天的 10.8。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 服务：Gateway PID 497240 ✅；RSS 最新采样 12.25GB 且 2h 内 +0.46GB 持续上涨 ⚠️（根因=trajectory 事件 256KB 展开副本驻留内存）；/ ✅ 17%；/mnt/h NAS 98% ⚠️；/mnt/m 停挂载但 heartbeat-state 陈旧条目未修正 ⚠️。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- CI：仅 fork openclaw 有工作流且全部陈旧（最近 09-28）；backup 两仓无 CI。推送链正常：backup-scripts 10-30 00:41 CST 已推送。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 安全：无新增 npm 安装（未触发安装后审计）；无新增敏感跟踪文件；今晚已移除 .backups（434MB 备份+含凭据配置）——本日最重要安全修复。遗留：openclaw-zero-token vendored 陈旧 7 个月待清理。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 代码变化：备份 tar 排除修复、邮件日志短路修复、RSS 根因报告及口径修正×2、push 拒绝根因（>100MB blob pre-receive）、升级清单+ERR-003/004、scout 研究产出（graphify+语料，83b66920）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
