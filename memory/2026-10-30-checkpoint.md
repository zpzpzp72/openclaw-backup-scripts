# SQLite session reclamation commit checkpoint expired — 完整因果链

> 2026-10-30 · gateway pid 648941 · 结构性缺陷,非数据库损坏

## 结论一句话

**每 30 分钟无条件触发一次的磁盘预算检查 → 每次都尝试会话回收 → 回收提交需主线程在 5 秒内应答 → 主线程因 V8 堆 96% 上限而繁忙 → 必然超时。**

## 证据链

### 1. 报错与影响面
```
"SQLite session reclamation commit checkpoint expired
 Sessions remain unavailable. Stop the Gateway, run openclaw doctor --fix ... and restart."

10-30 07:30 heartbeat-orchestrator | 07:38 heartbeat-scout | 08:00 openclaw-news-digest
10-30 08:30 heartbeat-orchestrator | 08:38 heartbeat-scout | 09:30 heartbeat-orchestrator
10-30 09:38 heartbeat-scout
→ 恰好每 30 分钟复发一次
```

### 2. 数据库本体健康(排除损坏)
```
全部 8 个 agent 库 quick_check = ok,freelist=0
三个 pre-startup-migration-*.bak 的 quick_check 也都 ok
state/openclaw.sqlite 的 wal_checkpoint(PASSIVE) = (0,102,102) 正常
→ 「disk I/O error」只是并发写 WAL 时的瞬时 I/O 错误
```

### 3. 源码级因果链
```
cleanup-service-jgpZZYRh.mjs
 └ enforceSqliteSessionHistoryDiskBudget (session-history-eviction-BFbGpe_H.mjs:1235)
   └ if (now < blockedUntil || now - lastCheckAt < interval) return;
     const interval = input.force ? 6e4 : PHYSICAL_BUDGET_CHECK_INTERVAL_MS /* 18e5 = 30 分钟 */
     → **只看时间间隔,不看实际用量** → 每 30 分钟无条件触发
   └ withSqliteReclamationAuthorization (session-history-eviction:371)
     └ COMMIT_DECISION_TIMEOUT_MS = 5e3   ← 回收线程等主线程 5 秒
       → Atomics.wait(shared, 0, REQUESTED, 5000)
       → Atomics.compareExchange(...) !== REQUESTED
         → throw "SQLite session reclamation commit checkpoint expired"
```

### 4. 为什么主线程来不及应答
```
gateway RSS 4.5GB · V8 堆 heapUsed 3.90GB(上限 4096MB 的 96%)
主线程 CPU 时间 79:47 / 5.8 小时(≈23% 均值)
main agent 库规模: session_nodes 1902 · transcript_events 70665 · trajectory_runtime_events 16151
             (全部 8 个 agent 库里 main 占绝对多数)
```
→ 每次预算检查要回收的量大 → 回收耗时长 → 超过 5 秒握手窗口。

### 5. 磁盘用量并未超预算
```
main agent 库 = 252MB,远低于默认 maxDiskBytes = 10GB
→ 「预算检查」只是定期看一眼,不代表真超了;但它每次都会尝试回收
```

## 结构性判断

三个参数叠加导致**必然**失败:
| 参数 | 值 | 问题 |
|------|-----|------|
| 检查周期 | 30 分钟 | 与用量无关,无条件触发 |
| 握手窗口 | 5 秒 | 相对主线程繁忙度太短 |
| 主线程负载 | V8 堆 96% | 无余量应答 |

**因此这是 RSS/堆压力问题的下游症状**,不是独立的数据库故障。
清理会话表规模能减少回收量、缓解;根治需 `doctor --fix`(修 agent database)+ 重启,或升级。

## 修复路径(均需 ZP 授权)

| # | 手段 | 说明 |
|:--:|------|------|
| 1 | `openclaw doctor --fix` + 重启 | 报错原文指定的官方路径(**会改数据库,需授权**) |
| 2 | `MALLOC_ARENA_MAX=2` + 重启 | 降 arena 碎片 → 降主线程压力 → 缓解握手超时 |
| 3 | 清理会话表规模 | 减少回收量(main: session_nodes 1902 / trajectory_events 16151) |
| 4 | 升级 2026.10.9 | 可能已包含相关修复,升级前看 changelog |

## 备注:doctor 在本环境的执行障碍
```
openclaw doctor        → 非 TTY 下只输出表头「┌ OpenClaw doctor」后退出
openclaw doctor --json → 输出 0 字节
用 script(1) 提供 pty 后能跑,但耗时数分钟且日志缓冲未实时刷新
→ 本机诊断需给 doctor 分配 pty 并给足超时(≥300s)
```
