# session SQLite lease 机制 —— 通用判据与检测方法

> **本文档是机制级判据，不绑定任何单一 agent。**
> 案例见 `2026-11-17-health-reclaim.md`（health）与本文件下文的迁移记录（finance/orchestrator）。
> 依据来源：NightOps 讨论纪要 v38（2026-11-23 00:25）第十二/第八条结论。

## 判据（一句话）

> **某 agent 的 session SQLite 报「SQLite session reclamation commit checkpoint expired」，
> 当且仅当：该 agent 在 `agent_database_leases` 里【没有当前 gateway 进程持有的 lease】。**

**与以下因素全部无关**：
- 库大小（health 库仅 1.2MB 也照样失败）
- 库完整性（失败者 `quick_check` 均为 ok）
- session 数量（finance 只有 1 个 session 也失败）

**强相关于**：该 agent 是否被当前 gateway 真正打开过（lease 是打开 DB 时产生的）。

## 检测方法（一条查询）

```sql
-- 库:/home/zhiping/.openclaw/state/openclaw.sqlite
-- 表:agent_database_leases
SELECT agent_id, COUNT(*), owner_pid FROM agent_database_leases GROUP BY agent_id, owner_pid;
```

- `owner_pid` = 现役 gateway 进程（`pgrep -f 'openclaw.*dist/index.js'`）→ **正常**
- 缺失该 agent，或 `owner_pid` 是旧进程 → **会失败**

> 差集 = 即将（或正在）失败的 agent 集合。
> 2026-11-22 23:23 实测：差集 {finance, orchestrator} 与实际失败的 3 个任务**完全吻合**。

## 机制原理（源码级）

`dist/session-accessor.sqlite-reclamation-commit-BX3N0u2L.mjs`：

```js
Atomics.compareExchange(shared, 0, WAITING, REQUESTED)          // 请求授权
Atomics.wait(shared, 0, REQUESTED, COMMIT_DECISION_TIMEOUT_MS)  // 等 5 秒
if (Atomics.load(shared, 0) !== COMMITTING) {
  rejectCommit(shared);
  throw new SqliteReclamationRequestRefusedError(
    "SQLite session reclamation commit was not authorized");
}
```

授权方必须是**同进程内持有该 DB 的活跃写入方**。
没有 lease ⇒ 没有活跃写入方 ⇒ 授权请求无人应答 ⇒ 5 秒后必然超时。

## 触发源：孤儿 session

失败的那个 agent 里通常残留着**已删除任务的 session**：

```
10-01 14:44  cron 310b4f57 创建 session
10-15 14:50  最后更新
10-16 14:48  文件层已删(.deleted.zst 归档)  ← 清理只做了文件层
       ↓      但 agent DB 的 session_nodes 仍残留
       ↓      该 cron job 已从任务列表消失
       ↓      维护循环仍遍历到这条记录 → 触发 reclaim → 无授权 → 5s 超时
```

→ **清理只做文件层、不做 DB 层**，是这类死锁的常见上游成因。

## 已观察到的迁移记录（证明这是机制问题，非单点）

| 时间 | 失败 agent | lease | 说明 |
|------|-----------|-------|------|
| 2026-11-14 ~ 11-17 | health | 0 | 孤儿 session（cron 310b4f57）残留 |
| 2026-11-17 ~ 11-22 | health | 3 | 已恢复 |
| 2026-11-22 ~ | finance, orchestrator | 0 | **同类故障在别的 agent 上原样复现** |

→ **health 当时是被「移除 agent」或「doctor --fix」治好的 —— 治的是对象不是机制，
所以故障立刻迁移到下一批没有 lease 的 agent。**

## 修复方向

| 方案 | 说明 | 是否需停机 | 可逆性 |
|------|------|:---:|------|
| **让 agent 被打开一次** | 触发一次该 agent 的真实活动，产生 lease | 否 | 完全可逆 |
| 清 DB 里的孤儿 session | 直连 sqlite 删级联行（先备份 + md5 校验） | 否 | 备份可回滚 |
| `openclaw doctor --fix` | 官方修复路径 | **是**（compact 需 `holder <pid> stop it first`） | — |
| 从 `agents.entries` 移除 agent | 维护循环不再遍历其 store | 否（需重启） | 需确认无依赖 |

**注意**：直接用 `openclaw sessions delete` **也会被同一个死锁挡住**
（任何写操作都先卡在 reclaim 上）—— 这本身就是「自我死锁」的决定性证据。

## 预防

1. agent 启动/续跑前检查自身 DB 能否取得写锁（`BEGIN IMMEDIATE`，实测 <1ms）；
   拿不到就**明确报「本轮不产出」**，而不是跑 5 分钟后报 reclaim 超时。
2. 任务删除时**同时清理 agent DB 的 session 记录**，不要只删文件层。
3. 定期跑一次 lease 覆盖扫描（上面的那条 SQL），差集非空即预警。

## 相关

- 案例：`memory/2026-11-17-health-reclaim.md`
- 讨论纪要：`memory/2026-04-15.md` v38（2026-11-23 00:25）
- 备份：`memory/backups/health-agent.sqlite.*.bak`

---

## 补充（2026-11-23 05:30）：第三次验证 —— 判据再次 100% 预测成功

### 观察
| 时点 | 失败 agent | lease 差集 | 吻合 |
|------|-----------|-----------|:---:|
| 11-22 23:23 | finance, orchestrator | {finance, orchestrator} | ✅ |
| 11-23 05:31 | work, orchestrator(旧) | {scout, work} | ✅ |

**每 6 小时换一批 agent 失败，而判据始终精确命中。**

### 关键新事实：故障迁移与「gateway 重启」强相关

```
work  : session 最后更新 04:42:10 → gateway 04:42:22 重启 → 05:31 heartbeat-work 失败
scout : session 最后更新 01:40     → 早于重启              → 同样无 lease
orchestrator NightOps : 02:40 失败(重启前) → 现已有 lease(05:30:46) → 可自愈
```

**机制**：
- lease 表的 `owner_pid` + `owner_start_time` + `provenance=process-v1:<hash>`
  → lease **绑定具体进程实例**（`agentDatabaseLeaseStaleReason` 判定 pid 死亡或 start_time 变化即 stale）
- lease 只在 **gateway 真正首次打开该 agent 的 DB 时**才产生
- gateway 重启 → 旧 lease 全部 stale → 新进程需为每个 agent **重新 claim**
- **重启后尚未被打开过 DB 的 agent**，其 cron 任务若先跑 → 无 lease → reclaim 握手无人授权 → 5s 超时

### 已排除的其它假设
| 假设 | 排除依据 |
|------|---------|
| agent-db maintenance 锁占用 | `state_leases` 只有 `gateway-owner` 全局锁（正常），无 agent-db maintenance 锁 |
| inode 冲突（`mayShareAgentDatabaseFile`） | scout inode=2267865、work=2267825，与 6 条已 lease 的 path 全部不同 |
| 库损坏 | 全部 `quick_check=ok` |
| 库过大 | work 仅 16MB 也失败；scout 81MB 有句柄但无 lease |

### 检测方法的强化
```sql
-- 现役 gateway pid
SELECT agent_id, COUNT(*) FROM agent_database_leases WHERE owner_pid = <gw_pid> GROUP BY agent_id;
-- 差集 = 缺 lease 的 agent = 会失败的对象
-- ★ 再加一条:owner_pid != 现役 pid 的行 = stale lease(重启后未重新 claim)
```

### 对修复方案的影响（重要修正）

原「方案 A：停机 `doctor --fix`」仍有效，但**新增一条更轻的**：

> **让缺失 lease 的 agent 被 gateway 打开一次**（例如对该 agent 跑一个极轻的任务 / 触发一次 session），
> lease 即产生，死锁自然解除，**无需停机**。
>
> 2026-11-22 health 的恢复正是这个机制的结果（health 现有 3 条 lease、consecutiveErrors=0）。

### 预防
1. gateway 每次重启后，**主动为全部 agent 预热 lease**（逐一打开其 DB），
   避免「重启后第一批任务必撞死锁」这一稳定复现模式。
2. 监控时把 **stale lease**（owner_pid ≠ 现役 pid）也纳入告警，
   而不只是看「差集为空」。

---

## 分层说明：本文档只放【判据】，不放【快照】（v39 补充）

判据是**不随系统状态变化**的结论；快照是**每次都过期**的观测值。混在一起会让读者
把「今天的差集」当成「永久结论」。

### 判据层（本文档，长期有效）

1. **无 lease ⇒ 该 agent 的写操作必失败**（reclaim 握手无人授权 → 5s 超时）
2. **lease 绑定具体进程实例**（owner_pid + owner_start_time + provenance=process-v1:<hash>）
3. **lease 在 gateway 首次打开该 agent 的 DB 时顺带登记**，不是按需申请
4. **stale lease**（owner_pid 已死 / owner_start_time 已变）= 重启后未重新 claim，等价于无 lease
5. 与库大小、完整性、session 数量**全部无关**

### 快照层（每日记录，会过期）

- 当前哪些 agent 缺 lease → 记在 `memory/YYYY-MM-DD.md`，标注「快照时间」
- 当前 cron error 分布 → 同上

> 2026-11-23 23:20 的快照：差集 = {orchestrator, work}；
> heartbeat-work consecutiveErrors=21，Orchestrator NightOps=2。
> **这份快照预计数小时内即失效**（agent 被打开一次就会自愈）。

### 三个集合（监控应同时看）

```sql
-- 现役 gateway pid
SELECT agent_id, COUNT(*) FROM agent_database_leases WHERE owner_pid = <gw_pid> GROUP BY agent_id;   -- A 正常
SELECT DISTINCT agent_id FROM agent_database_leases WHERE owner_pid IS NOT NULL AND owner_pid != <gw_pid>; -- B stale(高危)
-- C = 完全没有 lease 的 agent(高危)
-- 差集 = B ∪ C  →  这些 agent 的写操作会失败
```

### 自愈机制（scout 的实测证据）

```
scout: lease opened_at = 2026-11-23 08:00:01
      session updated  = 2026-11-23 08:06:42  ← 它的 cron 首次打开 DB
      → lease 顺带产生 → 死锁消失
```

> **自愈不是「修好了」，而是「恰好被用了一次」。**
> 对真正休眠的 agent（如 11-23 的 orchestrator，6 天无人触碰），自愈**永不发生**。

---

## 修正（2026-11-24 10:40）：免停机路径对休眠 agent 不可行

v38/v39 曾提出「让缺失 lease 的 agent 被 gateway 打开一次」作为免停机修复。
**该方案对真正休眠的 agent 不成立**，实测：

```
$ openclaw sessions archive --agent work --dry-run 'agent:work:recovered:9880f4fe-...'
  archive ...: SQLite session reclamation commit checkpoint expired
```

archive 是写路径（走 running gateway），同样需要 lease；而 lease 只在写成功后才产生
→ **鸡生蛋死锁**。

### 自愈的前提条件（此前遗漏）

> **只有「该 agent 有一个会成功跑的任务」时，自愈才可能发生。**
> scout 2026-11-23 08:00 能自愈，正是因为它**自己的 cron 那天跑成功了**
> （写成功 → lease 顺带产生）。
> 而 work 的 4 个 session 最新只到 11-23 04:42，其 cron 每次都失败 → 永远自愈不了。

### 修正后的方案表

| 方案 | 适用 | 是否需停机 |
|------|------|:---:|
| 等该 agent 自己的任务成功跑一次 | agent 有活跃任务 | 否（但休眠则永不发生） |
| 停机 `openclaw doctor --fix` + 重启 | 通用 | **是** |
| 从 `agents.entries` 移除该 agent | 确认无依赖后 | 否（需重启生效） |
| 接受现状 | 错误率低时可接受 | 否 |

### 判据补充

「差集非空」要进一步区分：

| 情形 | 判断 | 处置 |
|------|------|------|
| 该 agent 有活跃 cron 且曾成功过 | 可能在下次成功跑时自愈 | 观察即可 |
| 该 agent 长期无成功运行记录 | **惰性自锁，不会自愈** | 需人工介入 |
