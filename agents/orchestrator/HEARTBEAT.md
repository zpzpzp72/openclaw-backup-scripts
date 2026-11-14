# HEARTBEAT.md — Orchestrator 心跳检查清单

> *Last updated: 2026-11-07 04:05 CST — 已重写。此前版本停留在 2026-09-06（32 天前），多项指标已过时。*

## 每次心跳执行

### Phase 1：数据收集
- [ ] 读取 Coder 最新 code_report（agents/coder/code_report.md）
- [ ] 读取 Life 最新报告（agents/life/memory/ 最近）
- [ ] 读取 Scout 最新扫描（agents/scout/memory/ 最近）
- [ ] 检查 Finance / Health / Work 是否有新产出
- [ ] 读取 shared-memory/active-tasks.md（**当前不存在** — 只有 cross-agent-log.md）
- [ ] 读 `openclaw cron list`（真源是 `state.sqlite` 的 `cron_jobs` 表，非 `cron/jobs.json`）

### Phase 2：关键指标追踪
- [ ] **Session DB 健康（新增，最高优先级）**：per-agent `openclaw-agent.sqlite` 大小
      + `state.json` 里各 job 的 `consecutiveErrors` 与 `lastError`
- [ ] **NightOps 双轨状态（新增）**：per-agent 版（Scout/Life/Coder/Orchestrator NightOps）
      vs legacy `NightOps-*`（agent=main）
- [ ] Cron job 失败计数与归因（`agent main unavailable` vs 其他 agent）
- [ ] 代理连通性：**直连出口优先测**（github/npm 200 即够用，代理非必需）
- [ ] 各 agent 24h 产出文件数
- [ ] Repo 状态：M365 ahead/behind、openclaw-source 冻结天数
- [ ] 备份：archives 数量、timer 下次运行、`Result=success`

### Phase 3：输出
- [ ] memory/YYYY-MM-DD.md
- [ ] Tomorrow_Action_Plan_YYYY-MM-DD.md
- [ ] cross-agent-log.md（有新结论时）
- [ ] 推送给 Main — ⚠️ `tools.agentToAgent` 未配置，sessions_send 不可用；需 Main 主动联系

---

## 当前基线（2026-11-08 03:15）

| 指标 | 状态 |
|---|---|
| NightOps per-agent（4 路） | 🟢 11-08 全部 ok（Scout 01:30 / Life 01:50 / Coder 02:20 / Orch 02:40）|
| NightOps legacy（4 路） | ⏸️ 已 disable（11-07 起）→ 11-08 确认有效：legacy 不再产生失败 |
| Session DB | 🔴 仅 main 的 261MB 超时；scout 82M / life 54M / coder 50M / orch 47M 正常 |
| 今日 reclaim 错误 | 🔴 575 条（11-08 00:00→03:10），全部归因 `agent main unavailable` |
| heartbeat:main | 🔴 consecutiveErrors **49 → 72**（持续恶化）|
| NAS 回收站 | 🔴 27 份 / **123GB**；NAS 可用仅 4G → NAS 备份连跳 3 天 |
| 备份邮件 | 🔴 QQ SMTP 授权码失效（服务器回 535 Login fail，非网络）→ 3 天断链 |
| 代理 | 🟡 25017 TCP 可连但 HTTP 代理失败；**直连 github 200、npm 200 → 非阻塞** |
| Agent 活跃 | 🟢 coder/scout/life/orchestrator 有产出；**fin · health · work 仍休眠** |
| M365 repo | HEAD 40b27fc，ahead 2 / behind 0，.gitignore 已存在，.pyc staged 0 |
| openclaw-source | 🔴 冻结 111 天（0790d9f593a, 2026-07-18）|
| 备份 | 🟢 2 份归档，native timer 11-08 03:40，NAS timer 11-08 03:00（NAS 连跳）|

### 11-08 夜间实测结论
- ✅ 删「#recycle 目录**内部**」的文件 → 空间**立即真释放**（字节级 delta 53,223,424）
- ❌ 删「#recycle 目录外部」的文件 → 只移入 #recycle，**不释放**（NAS 主备份的 rm 正是这种）
- ❌ `':'` 前缀**不能**绕过回收站（实测同名文件仍落在 #recycle）
- ⇒ 唯一有效解：直接删 #recycle 里的老归档。工具 `scripts/nas-recycle-cleanup.sh` 已备好（默认预演）
- ⚠️ `du` 在 9p(SMB) 挂载上会挂起 → 统计体积一律逐文件 `stat -c %s`
- ⚠️ SMTP "Connection unexpectedly closed" ≠ 网络问题 → 用 `set_debuglevel(2)` 看服务器真实返回码

### 仍需 Main / Owner 决策
1. 🔴 **P0**：停 Gateway → `doctor --session-sqlite compact --session-sqlite-agent main` → heap 4096→8192 → `doctor --fix` → 重启
2. 🔴 `/reset` `agent:orchestrator:main`（495 msg / 204,801 tokens，overflow 2013）
3. 🔴 授权执行 NAS 回收站清理：`bash scripts/nas-recycle-cleanup.sh --execute`（释放 123GB）
4. 🔴 重新生成 QQ SMTP 授权码 → 更新 `~/.secrets/qq_smtp_password`
5. 🟡 `git push origin HEAD`（M365）
6. 🟡 设置 `commands.ownerAllowFrom`
