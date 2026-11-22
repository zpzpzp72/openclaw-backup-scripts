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
