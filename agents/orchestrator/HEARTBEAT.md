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

## 当前基线（2026-11-26 01:36）

| 指标 | 状态 |
|---|---|
| **work agent** | 🔴 **唯一 P0**：heartbeat-work err **73**；24h reclaim **1728 条，1727 条归因 work**；`agent_database_leases` work **0 行**；库 mtime 停 11-23 04:42；**work 无 HEARTBEAT/DIRECTIVE**（与 11-16 health 同模具）|
| 故障蔓延 | 🔴 孤儿投递 `4c89a409…` retry **416** pending → 72h 内 826 次 delivery 失败 → **发往 work 的消息送不到**（第三种表现面）|
| 故障轮转 | 🟡 health(11-15)→orchestrator+finance(11-22)→**work(11-25)**；8 库 integrity_check 全 ok → 是网关租约机制，不是库损坏；**一次重启只解当前受害者**|
| Orchestrator NightOps | 🟢 本场 01:36 恢复（11-22→11-25 连败 4 次，8 天空窗）；legacy `NightOps-Orchestrator`(10972380) 仍 enabled=0 → 二选一 |
| heartbeat 其他 6 路 | 🟢 err=0（health/finance/orchestrator 11-23 重启后已归零）|
| fin / work / health | ⚠️ 均未配置（无 HEARTBEAT/DIRECTIVE）；finance 断更 7.5 月、health 0 篇 daily |
| 备份 | 🟢 双链连续 3 轮全绿：NAS `openclaw-20261125-0300.tgz`(6.27G) status=ok；native 11-25 03:40 verify OK(5.9G)，归档 8→7，剩 779G |
| 备份脚本语义 | 🟡 tar 退出码 1 已实证**非损坏**（3 库 integrity_check=ok），但 `BACKUP_STATUS<=1` 吞掉「归档与源瞬时不一致」→ 建议 `.sync-staging/` 加 exclude（需授权）|
| 存储 | 🟡 /mnt/c **23G/96%**（11-23 曾 44G）；/mnt/h **263G/97%**（3 天 -110G）；/ 779G/19% |
| Gateway | 🟡 RSS **4.69GB**，pid 36001 uptime 3.2d，CPU 27.6%；heap 上限仍 4096MB（openclaw.json 无 maxOldSpaceSize）|
| OpenRouter credits | 🔴 0（第 11 窗）；key 已移至 `agents/finance/agent/openclaw-agent.sqlite → auth_profile_store` |
| 备份邮件 | 🔴 QQ SMTP 授权码失效（实测 Connection unexpectedly closed；secret mtime 2026-05-25）|
| M365 repo | 🔴 HEAD 700f8a3，ahead **11** / behind 0；ruff 全绿 + 回归 10/10 → 待 push（第 8 轮）|

### 🔍 health P0 的根因链（已实测到源码级）
1. `cron/maintenance` 每 **60s** 遍历**所有** agent store（`maintenance-CGA2ytB4.mjs`）
2. health 的 DB 从未被真正使用过 → **从未取得租约**（唯一 leases=0 的 agent）
3. `withSqliteReclamationAuthorization` 需要该 DB 上有活写入方才 `authorize()`；
   无 → `Atomics.wait(...,5000)` 超时 → `commit checkpoint expired`
4. ⇒ 停 Gateway → `doctor --fix` → 重启（compact 也需停机；holder=795 alive）

### ⚠️ 复核同伴结论时的两个坑
- **scratch 在 `cron_job_scratch` 表里，不是文件** → 别用 `ls HEARTBEAT.md` 推断心跳行为
- **system-owned monitor job 不可用 cron 客户端 disable**
  （`declaration_key = heartbeat:<agent>` → `cannot be edited by cron clients`）

### 2026-11-14 夜间实测结论
- ✅ **重启 = 最有效的 SQLite 修复手段**：一次重启同时解决 stale 租约与库写冻结，无需 doctor --fix
- ❌ health 库不随重启恢复（无作业触发 → 无租约 → 仍未被清理），需单独 `doctor --fix --session-sqlite-agent health`
- ⚠️ `openclaw-backup.sh` 回收站探测必须**早于**空间预检，否则最该告警的场景报 `recycle_backups=0`（11-14 已修）
- ⚠️ NAS `rm` 仍是移入回收站；只有删 `#recycle` **内部**文件才真释放

### 仍需 Main / Owner 决策（2026-11-26 更新）
1. 🔴 **work agent**：补 HEARTBEAT.md + DIRECTIVE.md **或** 停用 `heartbeat-work` → 停 Gateway → `doctor --fix --session-sqlite-agent work` → 重启（回收 28 条泄漏租约）。**单修库只解一半**
2. 🔴 孤儿投递 `4c89a409…`：`doctor --state-sqlite compact`（CLI ≥300s，禁 timeout 强杀）；**禁止手工改 `delivery_queue_entries`**
3. 🔴 NightOps 双路互斥：启用 legacy `10972380` 或保持本路，二选一
4. 🔴 OpenRouter 充值（第 11 窗）
5. 🔴 重生成 QQ SMTP 授权码 → 更新 `~/.secrets/qq_smtp_password`；备份脚本补「失败即告警」分支
6. 🔴 `git push origin HEAD`（M365，11 commit）
7. 🟡 4 个未配置 agent（main/finance/health/work）统一补配置或停用 job
8. 🟡 `/mnt/c` 23G、`/mnt/h` 263G 持续下降；NAS 回收站清理授权
9. 🟡 Gateway heap 4096→8192 后择机重启（与 P0-1 停机窗口合并）
10. 🟡 备份脚本 `.sync-staging/` 加 exclude
11. 🟡 `commands.ownerAllowFrom` 设置（心跳投递 no-route）
12. 🟡 全局 MEMORY.md 瘦身（43KB → ≤10,000 字符）；playwright 浏览器二进制安装 + 仓库内 `.nightops-venv/`

## 历史基线（2026-11-08 03:15）

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
