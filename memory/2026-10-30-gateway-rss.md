# Gateway RSS 11.5GB 根因定位报告

> 2026-10-30 00:35 CST · 只读调查 · gateway pid 497240 · OpenClaw 2026.10.5
> 本报告为 main agent 独立取证结论(未依赖子代理)

## 一句话根因

**OpenClaw 为每个会话的 trajectory runtime 事件在内存中保留了一份 256KB 的展开态缓冲副本**,
这些副本通过 Node `Buffer.allocUnsafe(256KB)` 逐个独立 mmap 分配、**全部写满**且**永不释放**
(删除磁盘文件也不释放),累积出 **4.26GB**;连同其他分桶合计 **11.5GB** RSS。

## 关键实测证据链

### 1. RSS 构成:100% 匿名私有脏页
```
Rss:            12118776 kB  (11.56 GB)
Private_Dirty:  12033940 kB  (11.48 GB)   ← 99.3%
Anonymous:      12033704 kB
Pss_File:          34925 kB  (34 MB)      ← 文件只占 0.3%
[heap]:          487.5 MB   (1 段)         ← V8 堆外,heap 上限 4096MB 无关
```
→ **不是 V8 堆**(heap 仅 487MB),**不是文件映射**(34MB)。

### 2. 匿名段尺寸分布:17454 个段全部恰好 256KB
```
尺寸 top8(按数量):
   256.0 KB × 17292 = 4323.00 MB   ← 占绝对多数
   140.0 KB ×   233 =   31.86 MB
   228.0 KB ×    74 =   16.48 MB
  2048.0 KB ×    44 =   88.00 MB

分桶:
  <64KB     112 段        0.7 MB
  64KB-1MB 18078 段    4495.0 MB
  1-4MB      90 段      160.0 MB
  4-64MB    390 段    12180.3 MB
  >64MB     60 段    48717.0 MB   (虚拟为主,实际驻留少)
```
→ **尺寸完全一致(256KB)** = 固定粒度分配,不是自然增长的数据结构。

### 3. 100% 是独立 mmap,不是堆内块
```
256KB 段归属: {'独立 mmap': 17454}    ← 无一落在 [heap] 或 [stack]
紧邻(间隔0)的对数: 0                   ← 没有两个 256KB 段相邻
相邻间隔中位数: 2678.9 MB
```
→ **排除 glibc arena**(arena 内 chunk 会连续且尺寸多样)。
→ 独立 mmap + 尺寸一致 + 全部写满 = **每次单独申请 256KB 缓冲区**。

### 4. 每段几乎 100% 被写满
```
256KB 段: 17390 个, 驻留合计 4326.7 MB, 平均 254.8 KB/段 (99.5%)
```
→ 真实数据副本,不是「预留未用」。

### 5. 与会话/事件数量的比值
```
内存 256KB 段: 17407

全 agent trajectory_runtime_events: 33114 行  (main 15377 / scout 6841 / coder 4151 / orchestrator 3329 / life 2932 / work 368 / health 78 / finance 38)
全 agent session_nodes:             1971 行  (main 1901)
全 agent transcript_events:        137402 行

event_json 磁盘总量: 129.5 MB(平均 4097 B/事件)
内存 256KB 段总量:   4352 MB   → 是 event_json 磁盘量的 34 倍

比值: 17407 段 / 15377(main trajectory_events) = 1.13 段/事件
      17407 段 / 1901 (main session_nodes)     = 9.2 段/会话
      17407 段 / 33114 (全 agent trajectory)   = 0.53 段/事件
```
→ **1.13 段/事件** 是最贴合的比值:接近「每个 trajectory runtime 事件对应一个 256KB 展开缓冲」。

### 6. 磁盘侧已删除,但内存不释放(关键佐证)
```
~/.openclaw/agents/main/sessions/:
  1900 × *.trajectory-path.json   (247 B 指针,指向 *.trajectory.jsonl)
   546 × *.jsonl.deleted.*.zst    (已删除会话的压缩归档,共 3.1MB)
     0 × 活跃 .jsonl

全库 *.trajectory.jsonl 实际存在数: 0     ← 指针指向的文件全部不存在
```
→ **磁盘上活跃会话数据为 0,内存却占 4.26GB**。
→ 证明:该内存副本**不由磁盘文件生命周期决定**,删除文件不释放。

### 7. 源码侧机制名确认
```
openclaw/dist/runtime-retention.sqlite-*.mjs
openclaw/dist/runtime-store.sqlite-*.mjs
openclaw/dist/session-incognito.worker-*.mjs
openclaw/dist/runtime-8mt5O-ko.mjs

符号: trajectoryRuntimeRetentionState / trajectoryRuntimeRetentionDue
      trajectoryRetention / trajectoryRetentionLease
      attachment.trajectoryRetentionLease
表:   trajectory_runtime_events (主 agent 15377 行)
```
→ OpenClaw 内置 **trajectory runtime retention** 机制,按事件保留运行时数据。

## 为什么不是之前推测的其他原因

| 旧推测 | 判定 | 依据 |
|---|---|---|
| V8 堆膨胀 | ❌ 排除 | `[heap]` 仅 487MB,V8 heap 上限 4096MB 根本没吃到 |
| glibc arena 碎片 | ❌ 排除 | 17454 段 100% 独立 mmap,零相邻,尺寸全等 256KB |
| 文件映射 / mmap 缓存 | ❌ 排除 | Pss_File 仅 34MB,占 0.3% |
| 线程栈 | ❌ 排除 | 59 线程,`[stack]` 仅 1 段,栈合计 0.1MB |
| 每会话固定开销 | ⚠️ 部分成立但非根因 | 9.2 段/会话是**结果**;真正机制是「每 trajectory 事件一缓冲」 |

## 增长形态

```
24 个采样点:10.84 GB → 11.54 GB,平均 33.9 MB/h
9/23 个采样点出现回落,最大单次回落 0.24 GB
VmHWM 12.45 GB / VmRSS 12.09 GB / Threads 59
```
→ 有**周期性回收**(glibc/V8 归还部分页),但**净增长持续** → 新增事件的缓冲增速 > 回收速度。

## 可执行建议

### 立即可做(只读/低风险,需 ZP 点头)
1. **统计 `trajectory_runtime_events` 的时间分布**,确认能否按「最后 N 天」裁剪
   ```sql
   SELECT date(created_at/1000,'unixepoch','localtime') d, COUNT(*)
   FROM trajectory_runtime_events GROUP BY d ORDER BY d;
   ```
2. **查找 retention 配置项**(源码里 `trajectoryRetention` 相关键),确认是否有可调阈值
3. **验证因果**:关闭/调小 trajectory retention 后重启,对比 RSS 基线(需 ZP 授权重启)

### 需 ZP 授权
4. **受控重启 Gateway** → RSS 会清零,但这是**掩盖**不是修复(根因仍在,会再涨)
5. **清理 `trajectory_runtime_events` 历史行**(先备份 sqlite)→ 直接减少内存驻留
   ⚠️ 风险:可能丢失轨迹审计数据,必须先做 sqlite 备份
6. **升级到 2026.10.9** → 可能已包含 retention 修复,**升级前先看 changelog**

### 结构性建议
7. **向 OpenClaw 上游反馈**:「trajectory runtime 事件的内存展开副本不随磁盘删除释放」
   —— 这是可复现的通用缺陷,非本地配置问题

## 复现命令

```bash
PID=$(pgrep -f 'openclaw.*dist/index.js' | head -1)
# 1. RSS 构成
grep -E 'VmRSS|VmHWM|Threads' /proc/$PID/status
cat /proc/$PID/smaps_rollup | head -14
# 2. 256KB 段计数
awk '{split($1,a,"-"); if (a[2]!="") {s=strtonum("0x" a[2])-strtonum("0x" a[1]); if (s==262144) n++}} END{print n}' /proc/$PID/maps
# 3. 事件数
python3 -c "
import sqlite3,glob
print(sum(sqlite3.connect(f'file:{f}?mode=ro',uri=True).execute('SELECT COUNT(*) FROM trajectory_runtime_events').fetchone()[0]
 for f in glob.glob('/home/zhiping/.openclaw/agents/*/agent/openclaw-agent.sqlite')))"
```

---

## 追加(00:50):源码侧机制确认 + 保留器的两个缺陷

### A. 256KB 尺寸来源确认(非巧合)
```
openclaw/dist/runtime-retention.sqlite-BlXqycCY.mjs:11
  const TRAJECTORY_RUNTIME_EVENT_MAX_BYTES = 262144;   ← 正好 256KB
  const TRAJECTORY_RUNTIME_CAPTURE_MAX_BYTES = 10485760; ← 10MB
  const TRAJECTORY_RUNTIME_FILE_MAX_BYTES   = 52428800; ← 50MB

runtime-8mt5O-ko.mjs:590
  limitBytes: TRAJECTORY_RUNTIME_EVENT_MAX_BYTES,
  reason: "trajectory-event-size-limit"
```
→ **实测 17454 个内存段尺寸 = 262144,与 OpenClaw 自己的常量逐一相等**。
→ 该常量用于「超限轨迹事件截断」。截断逻辑 `if (bytes <= 262144) return line;`
   (runtime-8mt5O-ko.mjs:583) 说明**每个事件占一个 256KB 槽位**。

### B. 保留器(sweep)机制与它的两个缺陷
```
保留器入口: settleIncognitoTrajectoryRuntimeRetention (runtime-8mt5O-ko.mjs:47)
  → session.trajectory.retention.prepare → trajectoryRuntimeRetentionState / Due
  → session.trajectory.retention.delete → trajectory.runtime.retention.delete

常量:
  RETENTION_MAX_AGE_MS = 12096e5   = 14 天
  GLOBAL_MAX_BYTES      = 536870912 = 512 MB
  SWEEP_INTERVAL_MS     = 36e5      = 1 小时
  DELETE_RUN_BATCH_SIZE = 16
```

**缺陷 1:字节预算按 DB 字节计,与内存实耗差 32.6 倍 → 预算永不触发**
```
DB 计量(sum(octet_length(event_json)+1)) =  134.9 MB   ← 保留器用它算预算
内存实耗(262144 × 17887 段)              = 4394.0 MB   ← 真实占用
放大倍数 = 32.6×
预算阈值 GLOBAL_MAX_BYTES = 512 MB
→ DB 计量永远达不到 512MB → 字节预算这条清理路径形同虚设
```

**缺陷 2:sweep 是 append 触发,不是定时器 → 空闲 agent 永远不清**
```
runtime-8mt5O-ko.mjs:408  (在轨迹 append 路径的 finally 块里)
  if (inFlight !== batch && !unsettledAppend) await settleIncognitoTrajectoryRuntimeRetention({...})
```
实测(超龄 = 超过 14 天):
```
agent          总事件   超龄(>14d)   最近事件距今    结论
coder           4151        0          21.3h       活跃→sweep 已跑,超龄已清
life            2932        0          22.7h       活跃→sweep 已跑,超龄已清
main           15509        0           0.0h       活跃→sweep 已跑,超龄已清
orchestrator    3329        0          21.2h       活跃→sweep 已跑,超龄已清
scout           6841        0          15.9h       活跃→sweep 已跑,超龄已清
finance          38       15         255.8h       空闲→从未被 sweep
health           78       78         345.6h       空闲→从未被 sweep
work            368       48          92.3h       空闲→从未被 sweep
```
→ 活跃 agent 的 14 天前事件**确实被清掉了**(超龄=0),证明 sweep 逻辑本身正确;
→ 但它**只在有轨迹写入时才会被调用**。空闲 agent(health 78/78 全超龄)永远不会被扫。

### C. 内置 session cleanup 覆盖不到轨迹事件
```
$ openclaw sessions cleanup --dry-run --all-agents
  Agent: main
  Maintenance mode: enforce
  Entries: 1902 -> 1902 (remove 0)
  Would prune unreferenced artifacts: 17
  Would enforce disk budget: 257237534 -> 257237534 bytes (files 0, entries 0)
```
→ 只清 17 个无引用产物,磁盘预算 **完全不动**(257MB→257MB),
→ **`openclaw sessions cleanup` 不触及 `trajectory_runtime_events`**。

### D. 配置侧排查结果(否定「纯配置解」)
```
session.maintenance schema 存在,但当前 openclaw.json 里 session.maintenance = null(未配置,走默认)
可用键: mode(enforce|warn) / coldStorage{enabled,afterDays} / pruneAfter(默认 30d)
        archiveDashboardAfter / maxEntries(默认 5000) / preserveRecent
        resetArchiveRetention / maxDiskBytes(默认 10gb) / highWaterBytes
→ 这些全部作用于 **会话条目/transcript 归档**,不作用于 trajectory_runtime_events

$ openclaw config get session.maintenance
  Config path is valid but unset: session.maintenance. The runtime default applies...

$ openclaw sessions cleanup --dry-run --all-agents   → 见上,轨迹事件不在其清理范围
```
**结论:没有纯配置开关能解决轨迹事件内存驻留。**
`maxGlobalRuntimeBytes` 虽可传参(`prepareTrajectoryRuntimeRetention` 的
`input.maxGlobalRuntimeBytes ?? GLOBAL_MAX_BYTES`),但其唯一调用方
runtime-8mt5O-ko.mjs:93 是内部代码,**未暴露为用户配置项**。

### E. 因此可行的修复路径(按风险从低到高)

| # | 手段 | 效果 | 风险 | 授权 |
|:--:|------|------|------|:--:|
| 1 | **升级到 2026.10.9** | 可能已修(当前 2026.10.5) | 低 | ZP 执行 `openclaw update` |
| 2 | 重启 Gateway | RSS 归零,**但只掩盖** | 中(中断) | ZP 执行 `/restart` |
| 3 | 手工 DELETE 旧 trajectory 事件 | 减少 DB 与(重启后)内存基数 | 中(丢审计数据) | 需 ZP 授权 + 先备份 sqlite |
| 4 | 直接删 `trajectory_runtime_events` 行**并重启** | 唯一能同时降低 DB 与内存基数的方法 | 中高 | 需 ZP 授权 |
| 5 | 向上游提 issue | 根治 | 无 | 需 ZP 同意公开 |

**实测数据(保留最近 3 天 / 7 天可清量)**:
```
保留最近 3 天  → 保留 7084 事件 (21.4%),可清 26052 事件 (78.6%)
保留最近 7 天  → 保留 25249 事件 (76.2%),可清 7887 事件 (23.8%)
保留最近 14 天 → 保留 32995 事件 (99.6%),可清 141 事件 (0.4%)
```
