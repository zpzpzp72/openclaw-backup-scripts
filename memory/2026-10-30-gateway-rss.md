# Gateway RSS 异常增长根因诊断报告（终版）
**日期**: 2026-10-30 00:19–02:49 GMT+8　**PID**: 497240（`pgrep -f 'openclaw.*gateway'` 实测）
**进程**: systemd user unit `openclaw-gateway.service`，2026-10-27 01:13:09 启动，运行近 3 天，node v26.10.0
**合规**: 全程只读。未重启/未改配置(仅我自建的 /tmp 实验脚本与临时进程，结束后已 kill 并清理)。SIGUSR1+CDP 只读采样是任务书明文授权的手段。

---

## 一句话根因结论

**原诊断的前提是错的。** 活体 inspector 实测(只读 CDP)证明：**V8 堆不是 496MB，而是 heapUsed ≈3.90GB、heapTotal ≈4.06GB、old_space 3.57/3.67GB，已达 4096MB 上限的 96%**——"堆外 9.9GB"这个分割本身就不成立。真实构成是：
①**约 4.2–4.4GB = V8 堆本体**，即那 17,400+ 个"恰好 256KB"匿名段(V8 堆页=256KB，计数与 heapTotal/256KB 吻合)；
②**约 7–9GB = glibc 每线程 arena**（209 个 64MB 对齐的 64MB 区间，碎片化后永不归还，由线程剧烈 churn 驱动，corr(RSS,maps)=0.917）；
③不存在"每会话一份内存副本"——会话数回归纯属巧合。

---

## 二、实测数据表

### 1. RSS 时间线（采样器 /tmp/rss_sampler2.log，每 20s 一行，节选）
| 时刻 | VmRSS kB | anon kB | maps 行数 | 线程数 |
|---|---|---|---|---|
| 00:30 | 12,251,472 | 12,167,092 | 19,377 | 112 |
| 01:07 | 12,872,200 | 12,786,108 | 20,470 | 112 |
| 01:23 | 13,110,804 | 13,024,536 | 20,472 | 139 |
| 02:15 | 13,477,~(峰值) | — | — | 102 |
| 02:48（终测） | 13,168,172 | 13,081,768 | ~19,600 | 56 |
VmHWM 一路爬到 13,695,764 kB。短分钟内 RSS 在 ±0.5GB 区间随活动震荡、峰值缓慢抬升（棘轮式），swap 几乎未用（32–33MB）。

### 2. smaps_rollup（02:48）
Rss 13,169,452 kB；Anonymous 13,082,992 kB；Private_Dirty 13,082,~；RssFile ≈84MB；Swap 32.8MB；AnonHugePages 0；Shared_Dirty 0。

### 3. 匿名 VMA 分桶（终态，Size 字段分类）
| 类 | 尺寸 | 段数 | RSS | 标志特征 |
|---|---|---|---|---|
| **A** | 恰好 256KB | **17,400–17,900** | **4.25 GB** | 全部 `rd wr mr mw me dc ac sd`，**无一相邻** |
| B | 64KB–1MB | ~810 | 0.17 GB | 大多带 dc |
| C | 1–4MB | ~60 | 0.05 GB | |
| **D** | 4–64MB | ~380 | **6.0 GB** | 90–93 个连续群；**无 dc**（3 个例外）；两型：`rd wr mr mw me ac sd` 与 `mr mw me sd` |
| E | ≥64MB | ~50–60 | 1.39 GB | 详见下 |

### 4. V8 堆活体读数（SIGUSR1 → CDP Runtime.evaluate，只读）
```
process.memoryUsage: rss 12.42–12.55 GB, heapTotal ≈4.056 GB,
                     heapUsed 3.82–3.90 GB, external 196–219 MB, arrayBuffers 15–28 MB
getHeapStatistics:   heap_size_limit 4,395,630,592 B (4.09GB), used_heap_size 3.903 GB,
                     total_physical_size 4.034 GB, malloced_memory 8.6 MB,
                     peak_malloced 120.6 MB, native_contexts 2, external_memory ≈206 MB
getHeapSpaceStatistics（关键项）:
  old_space   size 3.669 GB | used 3.572 GB | physical 3.647 GB
  new_space   64 MB / used 23 MB
  large_object_space used 178 MB;  code_space used 69 MB;  trusted_space used 60 MB
```
25 秒 Sampling Allocation Profiler（间隔 64KB）窗口内**仅采到 7.0 MB 新分配**：`transports.mjs:195 request` 3.67MB、`crypto/hash` 0.31MB、`decodeSqliteWorkerReplyValue`（sqlite-worker-store）0.19MB——说明 3.9GB 是**早已驻留的存量**，不是正在喷发的分配流。

### 5. A 类 = V8 堆页：隔离复现实测
| 实验（独立 node 进程） | 堆规模 | 恰好-256KB 段数 | 其中 RSS | 256KB 段 VmFlags |
|---|---|---|---|---|
| Buffer.allocUnsafe(256KB)×2000 | ~40MB | 21 | ~4MB | rd wr mr mw me **dc** ac sd |
| ArrayBuffer / Uint8Array×2000 | ~40MB | 19 / 20 | ~ | 同 |
| "x".repeat×2000 / allocUnsafeSlow | ~ | 28 / 21 | | 同 |
| JS 对象堆 ~70–110MB | ~100MB | 134 / 292 | 32–72MB | 同 |
| **A/B 结论** | | **1 VMA ≈ 1 V8 堆页（256KB=kPageSize）**，段数≈(heap物理)/256KB；gateway 侧 4.06GB→理论≈16k 页 ≈ 实测 17.4k | | gateway 与复现完全一致 |

原"V8 堆仅 496MB"的测量对象采错（很可能采到 worker isolate 或把 physical 部分读错），本次用主 isolate 直读推翻。

### 6. D 类 = glibc per-thread arena：吻合度检验（终态）
- 在 maps 中检测 **209 个"起点 64MB 对齐、覆盖≥95%×64MB"的区间**：rw 已提交合计 **8,824 MB**，区间内 ---p 余量 **4,552 MB**；无一个区间内含 V8 256KB 堆页（两套体系空间上分离）。
- 直方图（8MB 桶）：0MB:11 · 8:11 · 16:23 · 24:21 · 32:11 · 40:25 · **48:61** · 56:27 · **64:19**；完全长满(≥63MB)者 27–43 个。**平均每 arena 已提交 42.2MB**。
- 组内段尺寸呈**二峰配对**：20.x+43.x、44.x+17.x、15.6+48.4、22.9+41.1……相邻两段之和几乎恒 ≈64.0MB —— 正是 glibc arena「PROT_NONE 保留 64MB，随 growth mprotect 转 rw，顶部余 ---p」的指纹。10/24 首轮观察到的">1MB 段相邻补整 64MB"由此得解。
- D 类两组标志：`rd wr mr mw me ac sd`（rw 段）与 `mr mw me sd`（**不可读的已分配未 touch** 堆补齐段），均无 dc —— 排除 V8（V8 段全 dc）。
- 非堆（maps 里不在 heap/arena/V8 区间内）的 rw 匿名仅剩 ~0.1GB 量级 → **非 V8 匿名 RSS ≈9.0GB ≈ arena rw 合计 8.8GB，账目闭合**（差额≈E 类 19 块满占 64MB，见下）。

### 7. [heap] / 线程 / 栈
- [heap]（主 arena brk）仅一块 0x3082f000-0x50a83000，RSS ~0.5GB 量级。
- 线程数 51↔139 剧烈 churn；终态普查 53–56：**tokio-runtime-w ×24**（LanceDB 插件的 Rust tokio 线程池）、WorkerThread ×12–15（node worker_threads：sqlite/state worker）、**lance-cpu ×5**（Lance rayon CPU 池）、node-V8Worker ×4、libuv-worker ×4、MainThread、fs-safe-watch、SignalInspector、InspectorIo 等。
- 全进程仅 1 个 [stack] VMA（主线程，0.1MB）；**无线程栈异常**，VmStk 132KB。

### 8. E 类明细
- PROT_NONE 预留 321 段共 **43.18GB（虚拟，RSS=0）**：含 3–4 个 8GB 块（per-isolate V8 沙箱/code 预留）。
- 4 份重复的 node r-xp 映射 + 各伴随 ~512MB rwxp 码区（V8 ShortBuiltinCalls 每个 isolate 重映射 embedded blob）→ 主进程内有 **4–5 个 isolate**（主 + sqlite/state/plugin worker），其中 2 个 native_context。
- 19 块满占 64MB rw 段（0x771fe8…–0x77204c… 相邻连续 ~1.5GB 区内，RSS 1.19GB，标志无 dc）：**最可能属于 LanceDB 侧（二进制内实测存在 DuckDB/datafusion memory_pool 符号），与 arena "满 grown"形态也可重叠，是全案唯一低置信角落** → 见"残留验证"。

### 9. 会话维度交叉验证（否定"每会话成本"）
- 会话文件 2,571 个、合计 **3.08MB**（几乎全为元数据 json，无 .jsonl transcript；正文在 sqlite：main 库 252MB、state 54MB）。分布：main 2450、coder 41、scout 46、life 15、orchestrator 14、其余个位数。
- 比值检验：10/24 ≈9388 映射 /1300 会话=7.2；10/26 ≈15194/2571=**5.91**；10/30 ≈18975/2571=**7.38**。
  **10/26→10/30 会话数零增长而映射 +25%** → 比值非常数，映射数不随会话数，随**运行时长/活动量**走。比例吻合系巧合。
- 且 A 类段数≈heap/256KB（跟堆走），D 类段数≈arena 累积（跟线程 churn 走）——都与会话数无机制关联。

### 10. 内存型相关系数（16 个采样点）
corr(RSS,maps)=**0.917**（棘轮同涨）、corr(maps,threads)=0.668、corr(RSS,threads)=0.571 —— 线程 churn 拉动 arena 创建/碎片→maps 与 RSS 棘轮上行。

### 11. 配套发现（非 RSS 但同病根）
memory-lancedb-pro 插件（config：autoCapture+autoRecall，bge-m3@1024 维，记忆压缩 minAgeDays=7）在 `~/.openclaw/memory/lancedb-pro/memories.lance`：**_versions 目录 7,137MB**（data 仅 166MB）——版本清单/垃圾未被清理的**写入放大**病灶磁盘版。每次会话触发 capture→Lance 提交→tokio 写突发+sqlite worker 回包解析（sampling profiler 中可见 decodeSqliteWorkerReplyValue）→分配风暴→arena 加速碎片化。

---

## 三、根因链（现象→机制）
1. **前提修正**：V8 堆已 3.9/4.06GB（inspector 直读+17.4k×256KB 段+隔离复现三方一致）。"9.9GB 堆外"实为「V8 之外还有 ~9GB」，其中几乎全部是①。
2. **A 类=V8 堆页**（256KB=kPageSize，1 VMA/页；数千万次页级 mmap/munmap 是 V8 常规操作，非泄漏本体）。
3. **D 类=glibc 每线程 arena 的碎片棘轮**：
   - glibc 主进程 arena 上限 8×nproc(24)=192 个，每 64MB；每线程首次 malloc 绑定一个 arena（round-robin），**线程死亡其 arena 不回收重用**→churn 越多，活跃 arena 越多；
   - arena 内碎片只有 top chunk 才 trim，中部空洞永不归还内核→每 arena 稳态"已提交 40–60MB"但活数据可能只有几 MB；
   - gateway 的负载恰好是"短命大分配风暴"（每请求 JSON 解析、sqlite worker 大回包、Lance 写入 buffer），把 arena 碎得最狠。
4. **增长的本质**：V8 老生代逼近上限（3.57/3.67GB，可用仅 0.47GB）→ 靠 full GC 挤空间、增长放缓但仍棘轮；arena 高水位随线程池波动单调抬升（corr 0.917）。两者叠加 = RSS 每 2–3 小时 +0.5–1GB。**heap_size_limit 4.39GB，V8 会先 OOM crash**（systemd Restart=always 会自动拉起，算是隐式减压阀）。
5. **"每会话为什么留 X MB"之问的正面回答**：没有这份副本，所以问句不成立。真正与会话相关的堆内结构是：fs-safe watch 的文件哈希 Set（监听整个 ~/.openclaw 树，2.5k+会话文件在内）、session watcher/state 索引、以及 lancedb-pro 对每个会话的 autoCapture 写路径（影响的是 arena 碎片与磁盘版本膨胀，不是"每会话驻留一份 transcript"）。**清理旧会话文件不会显著降 RSS。**

---

## 四、可执行建议（只出建议，未实施）

**立即可做（不动 gateway）**
1. **把监控指标换掉**：弃用任何"堆 496MB"口径；以 `kill -USR1 <pid>`+CDP 直读 `heapUsed/old_space.used/external/malloced` 为准（本次已跑通脚本逻辑，命令清单见下）。配合每 5–10 分钟一行 `grep VmRSS /proc/<pid>/status` + `wc -l /proc/<pid>/maps`。
2. 观察 arena 数量拐点：数 "64MB 对齐且 rw" 区间数（本报告脚本逻辑），>150 即 arena 耗尽预警。
3. 检查 D 类唯一低置信角落（19×64MB 满占块）：`lsof -p <pid>` 看是否有 .lance/.arrow fd 与地址段邻接；一次 `HeapProfiler.takeHeapSnapshot` 差分可终裁（采样动作本身就是任务授权的只读操作，但快照 dump 写盘，故列为需授权）。

**需 ZP 授权（会改动配置/进程/数据）**
1. **env 层治 arena**：在 `/home/zhiping/.openclaw/gateway.systemd.env`（已有 EnvironmentFile）加 `MALLOC_ARENA_MAX=2`（或 `MALLOC_TRIM_THRESHOLD_=...`），一次重启生效。预期直接砍掉 D 类大头的一半以上；代价是多线程 malloc 锁竞争略增（node 负载下通常可忽略）。这是**本案性价比最高的一刀**。
2. **给 V8 留出 GC 空间**：`--max-old-space-size=3072`（现 4096 已 96%，0.47GB 余量撑不了几次大请求）；或低峰期计划性重启（systemd timer）。heap 到 4.39GB 会 OOM crash，Restart=always 虽能拉起，但属"事故式自愈"，会丢运行态。
3. **治理 lancedb-pro**：关闭/节流 autoCapture（或提高批量阈值）；对 memories.lance 做一次 optimize/compaction 并清理 _versions（当前 _versions 7.1GB vs data 166MB，纯病灶）；确认版本保留策略。
4. **收窄 fs-safe watch 范围**（watch-hints 的 file-hash Set 随监听文件数线性涨），至少不监听会话存档目录。
5. **向上游报 issue**：随附本报告第 2、4、5 节实测法，建议官方在 /status 暴露 process.memoryUsage 与线程数，避免"496MB"式误诊复发；并建议文档默认给出 MALLOC_ARENA_MAX 建议。
6. （保守）宿主 swap 8→16GB，给 V8 OOM 与 arena 棘轮留缓冲——纯系统层操作。

---

## 五、可复现命令清单
```bash
# RSS 构成
grep -E '^(VmRSS|RssAnon|RssFile|VmHWM|VmSwap|Threads)' /proc/497240/status
cat /proc/497240/smaps_rollup
# V8 堆真实占用（主 isolate）
kill -USR1 497240   # 任务授权的只读采样入口（注意：执行后 inspector 9229 保持开启，见附录副作用）
# CDP 只读采样表达式：
#   JSON.stringify(process.memoryUsage())
#   JSON.stringify(process.getBuiltinModule("v8").getHeapSpaceStatistics())
#   JSON.stringify(process.getBuiltinModule("v8").getHeapStatistics())
# 每线程 arena 来源证据
for t in /proc/497240/task/*/comm; do cat $t; done | sort | uniq -c | sort -rn
# 256KB 段 = V8 堆页 的 A/B 复现（对照实验，独立进程）
node --max-old-space-size=4096 /tmp/bigheap.js &   # 造 ~100–4000MB JS 堆后数 smaps 中恰好-256KB 段
# arena 检测：起点%64MB==0 且覆盖≥95%×64MB 区间内的 rw/---p 合计
# 会话账目
find ~/.openclaw/agents -path '*/sessions/*' -type f | wc -l   # 2571
du -sm ~/.openclaw/memory/lancedb-pro/memories.lance/_versions # 7137MB
```

## 六、残留不确定点（如实声明）
1. 19×64MB 满占段的归属：arena "满 grown" 或 Lance/DuckDB buffer slab，二选一未终裁（判据见四-立即-3）。不影响主结论量级。
2. `--inspect` 侧效应：SIGUSR1 打开的 inspector 未被成功关闭（进程内 `require` 不可用，inspector.close() 调用失败），目前 9229 仅监听 127.0.0.1。属只读调查的遗留副作用，建议列入下次重启计划一并消除；再次强调本次采样为任务书明文授权动作。
3. 线程-arena 因果链是机制推断+强相关(0.917/0.668)+形态指纹（二峰配对、PROT_NONE 余量、64MB 对齐）支撑；无 allocator 源码级断点证明（需 strace/gdb，超出本次只读授权）。
