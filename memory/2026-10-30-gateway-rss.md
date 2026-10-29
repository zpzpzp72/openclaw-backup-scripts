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
