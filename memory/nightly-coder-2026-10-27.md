# Coder NightOps 记忆条目 — 2026-10-27

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
<!-- Night Coder · 2026-10-27 01:30 CST · 回写 heartbeat/nightly-coder-2026-10-27.md -->

## 事实沉淀（可 recall）

### 1. 落盘恢复
- nightly-coder 间隔 7 天（10-21~10-26 六晚）后本场恢复落盘（Night #79）
- cron 本体存活（a38acaaa，Mon-Fri 01:20），缺席为间歇性而非 cron 死亡

### 2. 版本面
- 运行 **2026.10.5** (1b58cb9)；npm **latest 2026.10.7**（10-24 上线）；extended-stable 2026.9.34；beta 2026.10.10-beta.3 → 按纪律不采纳 beta

### 3. Gateway
- 01:15 watchdog 新 pid **497240** / RSS 2GB / **CPU 148%** / uptime 1:51 → 重启后内存大降（10-26 曾 11GB），但需白天复核 148% 满载（CPU 阈值告警可能因运行时高 CPU 基线正常波动出现）
- watchdog 阈值：RSS>6GB / CPU>80%；10-26 23:15 曾记录 11GB @ 81% uptime 2d13h
- gateway-restart.log 记录 10-27 00:15~01:15 之间发生重启（319857 → 497240）

### 4. 备份链路
- 10-26 tgz 8.8GB @ 03:13，近 5 日连续（08 起 0300 系列稳定）
- tar 退出码 1 皆因热备份良性（`.memory-write.lock.lock` 文件在扫描窗口消失）
- **排除规则失效疑点**：`--exclude='.openclaw/memory/lancedb-pro'` 匹配不到实际路径（tar 日志仍含 lancedb-pro 文件）→ 每份备份仍 8.5~9 GB
- **/mnt/h 98%**（186G 空闲），39 份归档（20261001→1026），RETAIN_DAYS=30 未生效，10-05 之前的归档仍在 → 白天决定保留策略

### 5. 工作区漂移（最大白天风险点）
- **579 untracked**（agents/、heartbeat/、memory/、reports/、.graphify-* JSON、openclaw-zero-token/ 内多 service 子包）
- 11 modified/deleted；feature/hot-backup **ahead 25**（10-20 后累计，含 backup 幂等化、LanceDB MVCC 分析、记忆体系讨论纪要 v24-v26）
- 建议白天一次 `git add -A && git commit` 收口后再 push
- **openclaw-zero-token 是主要 untracked 仓**（node_modules 类依赖），收口时优先排查

### 6. CI/CD
- 所有 GitHub 仓库最近窗口内无 workflow run（既无失败也无修复）；memory-lancedb-pro 最后红灯仍在案（10-05），持续 ~175 天
- backup-scripts 仓 PR #4/#2 仍开放（建议关）

### 7. 内容与通知通道
- AMAT **双通道验证成功**（10-26 21:30 开盘班次：飞书 message_id + Gmail）→ feishu_push.py 排队逻辑工作正常
- news digest 邮件成功（Gmail 17 条），但 OpenRouter 402（缺积分）→ BILIBILI_COOKIES / OPENROUTER_API_KEY 待补
- minimax_429 凌晨峰值 83%（2056 用量上限）→ 配额管理非认证故障；查余量 mmx quota（CN key→api.minimaxi.com)
- fallback 链 4b→27b→M2.7：27b ECONNREFUSED 待修；P1-5b 临时链待 ZP 拍板
- identity_templates ≈110 天占位；group_policy P0-1 仍无回执

### 8. NightOps 窗口纪律
- 本场 01:20 触发，符合工作日凌晨 00:30-03:00 错峰窗口
- 心跳 30 分钟周期（main/coder/finance/health/life/orchestrator/scout/work）在位

## 明日白天优先动作
1. push feature/hot-backup 25 个未推送 commits
2. Gateway CPU 148% 告警复核（是否稳态高 CPU 基线，必要时调 CPU 告警阈值到 150%+）
3. workspace 收口：579 untracked + 11 modified 一次 commit，再 push
4. 评估升级 2026.10.7（不采纳 beta；升级前跑 doctor + security audit）
5. 修 backup.sh 排除规则（`.memory-write.lock.lock`）+ RETAIN_DAYS 逻辑（39 份未清理）+ 备份盘 98% 容量告警处置
6. memory-lancedb-pro CI 红灯复核
7. AMAT 10-27 05:00 次班次复测双通道稳定性
8. 27b fallback ECONNREFUSED 复测

## 未执行说明
本场全程只读（git / gh api / openclaw status / df / tail / cat / ls / grep）。未做任何配置修改、未安装 npm 包、未触发重启 —— NightOps Coder 角色定位为观测与上报，变更留待白天人工窗口。
