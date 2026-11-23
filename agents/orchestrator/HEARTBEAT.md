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

## 当前基线（2026-11-17 03:20）

| 指标 | 状态 |
|---|---|
| **health agent** | 🔴 **唯一 P0**：leases=0 → 回收提交无人授权 → 每 60s 超时（60/h）|
| main agent | 🟢 已恢复：reclaim 错误 0（11-14 曾 180/h）|
| 其余 6 agent | 🟢 正常，leases 4~6；scout/life/coder/orchestrator 有产出 |
| fin / work / health | ⚠️ 均休眠 117d+（health 因 P0 无法工作）|
| 备份 timer | 🟢 已加 OnBootSec（native 12min / NAS 25min）→ 消除开机抢 IO 误判 |
| native backup | 🟢 archives 4 份，11-14/11-15 verify OK |
| NAS 备份 | 🟢 已恢复产出（11-15/11-16）；回收站 36 份 / 185GB（清理待授权）|
| M365 repo | HEAD d9f53b0，ahead 7 / behind 0；`/mnt/c` 96% 满（剩 21G）|
| Gateway | RSS 4.53GB，heap 上限仍 4096MB（doctor 建议 8192）|
| OpenRouter credits | 🔴 0 |
| 备份邮件 | 🔴 QQ SMTP 授权码失效（535 Login fail，非网络）|

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

### 仍需 Main / Owner 决策
1. 🔴 授权 NAS 回收站清理：`bash scripts/nas-recycle-cleanup.sh --execute`（释放 185GB）
2. 🔴 health 库 doctor --fix + 重启；顺手处理 startup migrations
3. 🔴 重生成 QQ SMTP 授权码 → 更新 `~/.secrets/qq_smtp_password`
4. 🟡 确认本地原生备份 11-14 那轮收尾 `verify OK`
5. 🟡 `git push origin HEAD`（M365）
6. 🟡 Gateway heap 4096→8192 后择机重启
7. 🟡 设置 `commands.ownerAllowFrom`

---

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
