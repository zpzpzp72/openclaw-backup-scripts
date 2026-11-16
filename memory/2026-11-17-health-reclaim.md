# health agent SQLite reclaim 死锁 —— 独立核查报告

> 2026-11-17 05:30 · 依据 orchestrator 03:45 的源码级分析,**独立复核后**:
> 根因链**成立**,但**速率说法有误**,并**发现了第三条路(不停机)**。

## ✅ 复核结论:orchestrator 的根因链成立

### 租约分布(核心证据)
`agent_database_leases` 表在**全局** `state/openclaw.sqlite`(不在 per-agent 库里):

| agent | lease | gateway 句柄 | session_nodes |
|------|------:|------------:|------------:|
| main | 5 | 28 | 1897 |
| scout | 4 | 23 | 39 |
| coder | 5 | 24 | 3 |
| life | 4 | 23 | 10 |
| work | 5 | 19 | 4 |
| finance | 5 | 18 | 1 |
| orchestrator | 4 | 21 | 11 |
| **health** | **0** | 6 | **1** |

全部 32 条 lease 的 `owner_pid` 都是 **795**(现役 gateway)。
**health 零 lease** = 从未取得过租约 → reclaim 握手无人授权 → 必然 5 秒超时。

### 机制源码(复核确认)
`dist/session-accessor.sqlite-reclamation-commit-BX3N0u2L.mjs`:
```js
Atomics.compareExchange(shared, 0, WAITING, REQUESTED)   // 请求授权
Atomics.wait(shared, 0, REQUESTED, COMMIT_DECISION_TIMEOUT_MS)  // 等 5 秒
if (Atomics.load(shared, 0) !== COMMITTING) {
  rejectCommit(shared);
  throw new SqliteReclamationRequestRefusedError("SQLite session reclamation commit was not authorized");
}
```
授权方必须是**同进程内持有该 DB 的活跃写入方**。health 无 lease → 无授权方 → 必然超时。

### 决定性验证:连 dry-run 都写不进去
```
$ openclaw sessions delete --agent health --dry-run 'agent:health:cron:310b4f57-...'
  delete agent:health:cron:310b4f57-...: SQLite session reclamation commit checkpoint expired
  Sessions remain unavailable. Stop the Gateway, run "openclaw doctor --fix" ...
```
→ **任何写操作都先卡在 reclaim 上** → health 的 DB **自我死锁**,不只是心跳失败。
这解释了 orchestrator 说的「child session patch failed」——health agent 连 spawn 都做不到。

### 触发源:一个 33 天前的孤儿 session
```
session_key : agent:health:cron:310b4f57-d4ef-4d58-910b-3d6b9da251
created    : 2026-10-01 14:44:29   updated: 2026-10-15 14:50:53
对应 cron job 310b4f57 : ★ 已不存在(当前 18 个任务中无此 id)
内容: transcript_events 48 行 / trajectory_runtime_events 78 行 / cold_archives 0
```
→ 该 job 已被删除,但 session 残留 → 维护循环仍在尝试回收它 → 触发 reclaim → 死锁。

## ⚠️ 需要纠正 orchestrator 的两点

### 1. 速率不是 60/小时,是 ~1/小时
```
50 条 error 跨 47.6 小时 → 1.05 条/小时
相邻间隔中位数 60 分钟(最小 12,最大 60)
最近 6 次: 23:51:47 → 00:51:47 → 01:51:48 → 02:51:48 → 03:19:00 → 05:19:02
```
`consecutiveErrors=62` 是**累计连续失败次数**,不是速率。
→ **严重性评级应下调**:这是每小时一次的慢性失败,不是 60/分钟的洪泛。
但**它 100% 复现**,且 health agent 完全不可用(任何写操作都死锁)。

### 2. 「disable heartbeat-health 不可执行」属实,但结论可以更强
实测:
```
$ openclaw cron disable 775e24db-adf4-4c25-868f-6b84f2e15888
  Error: system-owned monitor jobs cannot be edited by cron clients
```
`declarationKey=heartbeat:health` → 系统按 agent 自动生成,非 cron client 可编辑。属实。

## 🔍 额外发现:第三条路(可能不必停机)

orchestrator 给的 A(停机 doctor --fix)/B(移除 health)都需要停 Gateway 或改配置。
但实测显示:**真正需要被 reclaim 的,只是那 1 条孤儿 session**。
若能把它从库里去掉,reclaim 就没有对象 → 不再触发握手 → 错误自然归零。

阻碍:`sessions delete` 自身也要过 reclaim → 死锁(实测已验证)。
→ 但**直接改 DB 绕开 reclaim 是可行的**:health 库 1.2MB、`quick_check=ok`、
`BEGIN IMMEDIATE` 取写锁 **0.0001s**(无其他写入方占锁)。

### 风险评估
| 项 | 评估 |
|----|------|
| 数据损失 | 该 session 的 cron job 已不存在,48 条 transcript + 78 条 trajectory 事件属**不可达的历史残留** |
| 库完整性 | quick_check=ok;操作前已有备份 `/tmp/openclaw/health-agent.sqlite.bak.20261117`(1253376 B) |
| 可逆性 | 备份可回滚;且删除的是「job 已不存在的 session」,与任何现存任务无关联 |
| 副作用 | 若判断有误,最坏情况是从备份恢复 |

## 📌 待 Owner 决策

**方案 C(新,推荐先试)**:
1. 备份 health 库(已有 `/tmp/openclaw/health-agent.sqlite.bak.20261117`,建议再存一份到 workspace)
2. 停 `heartbeat-health`(系统任务不可 disable → 改为让 gateway 忽略 health agent,或直接做第 3 步)
3. 用 sqlite3 直接删除 `session_nodes` 中那条 `310b4f57` 及其级联行
4. 恢复 gateway 后观察 2 个小时:错误是否归零、health 是否恢复可用

**方案 A(orchestrator 提的)**:停 Gateway → `openclaw doctor --fix` → 重启。
实测 compact 也需停机:`failed to acquire gateway state ownership ... holder 795 ... stop it first`。

**方案 B(orchestrator 提的)**:从 `agents.entries` 移除 health。
health 已休眠 117 天+、零产出 → 移除后维护循环不再遍历其 store → 错误归零。
⚠️ 影响面未完全核查:配置中 `health` 出现 2 次(entries 条目 + fallback 链上下文),
`heartbeat-health` 系统任务会随之消失,需确认无其它依赖。

**建议顺序**:先 C(可逆、影响面最小),失败再 A,最后 B。

## 其它待办(orchestrator 提出,已复核状态)

- Gateway RSS 4.36GB,heap 上限仍 4096MB(doctor 建议 8192)—— **注意**:`MALLOC_ARENA_MAX=2` 已在 `gateway.systemd.env` 预置但**需重启才生效**
- `/mnt/c` 96% 满(剩 22G):Windows 侧问题,`Windows/System` 在长
- `commands.ownerAllowFrom` 未设 → `/update`、重启、配置变更、命令批准均不可用(实测确认 `ownerAllowFrom: None`)
- QQ SMTP 授权码失效(535 Login fail)→ 备份邮件断链
- OpenRouter credits = 0
