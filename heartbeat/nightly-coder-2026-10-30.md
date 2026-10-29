# Coder 夜检要点 — 2026-10-30（01:20 CST 窗口，NightOps）

## 服务状态总表

| 项目 | 状态 | 说明 |
|---|---|---|
| Gateway 进程（PID 497240） | ✅ | 与预期实例一致，端口 18789 存活 |
| Gateway RSS | ⚠️ | 趋势文件最新采样（≈01:14 CST）12.25GB，2 小时内 11.79→12.25GB 持续上涨；根因已定位（trajectory 事件 256KB 展开副本驻留内存，不随磁盘删除释放），升级清单已备 |
| 根分区 / | ✅ | 17% 已用（155G/1007G），健康 |
| /mnt/h NAS | ⚠️ | 98% 已用（165G 余量），连续多日高位 |
| /mnt/m | ❌→⚠️ | 挂载点已消失（现仅 c/d/h/wsl/wslg/z），heartbeat-state 陈旧条目仍未修正 |
| GitHub CI | ✅(空转) | 仅 fork openclaw 有工作流，最近运行 09-28（Node 22 Compat skipped；CodeQL 系列止于 09-22 success/cancelled），无新触发 |
| 备份推送链 | ✅ | openclaw-backup-scripts 10-30 00:41 CST 成功推送（83b66920）；push 拒绝根因已入库 |

## GitHub CI / 仓库
- zpzpzp72 名下 30 仓库，近期推送：openclaw-backup-scripts（10-30 00:41 CST）、openclaw-backup（10-29 03:30 CST，私有）；其余低活跃。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- openclaw-backup / openclaw-backup-scripts 无 CI 工作流（与 10-28 报告一致）。fork openclaw 工作流全部为陈旧触发，无告警。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## OpenClaw 升级与构建风险
- 本地 2026.10.5 < npm latest **2026.10.9**；⚠️ 该版本 10-29 15:46 UTC（23:46 CST）发布，距本次检查仅约 2 小时，属 0 天新发布，回归风险偏高。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- dist-tags：latest=2026.10.9，extended-stable=2026.9.35，beta=2026.10.10-beta.4（上游高频迭代）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 建议：升级清单已于当晚备好（822f46fd，含 ERR-003/004）；执行仍需 owner 授权 + 维护窗口。若求稳可采用观察 24~48h 再升 10.9 的策略，或选已有 2 天浸泡期的 10.8。RSS 泄漏根因修复是否随包落地，升级前应 diff changelog 确认。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## 依赖与安全
- 当晚无新 npm 安装 → 未触发安装后安全审计条件。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- git ls-files 敏感文件扫描：无新增 .env/secret/credential/pem/key 类跟踪文件（仅命中 vendored 目录名）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- workspace 跟踪的 package.json/lock：无。vendored `openclaw-zero-token/` 依赖仍陈旧（2026.3.28，7 个月），待清理（持续遗留项）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## 代码库变化（10-29 20:18 → 10-30 00:41，共 20 提交）
- 备份链修复：tar 排除 workspace/.git 与 .backups；移除已入库的 .backups（434MB 数据库备份 + 含凭据配置备份）——  tonight 完成的关键安全修复；邮件成功日志改短路写法。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 诊断：Gateway RSS 11.5GB 根因报告（c3de59d6）+ 两次口径修正；push 被拒精确根因（pre-receive 拒绝 >100MB blob，822f46fd 补记）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 研究产出：scout 10-30 夜间研究入库（graphify 重建 + arxiv/新闻语料，83b66920）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 未提交遗留：nightly-scout-2026-10-30 两份、update_lancedb_1030.py、ERRORS.md / rss-trend / rss-memory 三处修改，归 scout 流程处置。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
