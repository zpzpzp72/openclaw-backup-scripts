# Tomorrow_Action_Plan — 2026-11-08

> NightOps 2026-11-07 02:40 CST 汇总 · 输入：scout 11-07(02:30)、life 11-07(02:05)、coder 11-07(02:24)、orchestrator 自查
> 归一化：Signal / Impact / Blocker / Opportunity / Next Step

---

## 🔴 P0 — 需 Main 今晚拍板（今晚 03:00 是硬时间点）

- **P0-1 NAS 备份断档 2 晚，今晚 03:00 第 3 次预检拦截**
  - Signal: `/mnt/h` 7.2T 已 100%，仅剩 3.8G；`~/.openclaw-backup.heartbeat` status=error，detail=「可用 4G < 需要 6G」，last_backup 仍停在 `openclaw-20261105-0300.tgz`
  - Impact: 备份链已连续 2 晚失败，仓库/会话无异地副本；今晚 03:00 将是第 3 次拦截
  - Blocker: `/mnt/h/#recycle/AI/openclaw.zone/WSL/` 28 份 ≈123GB 全是 08-27~10-10 过期包；NAS(SMB) 上 `rm` 只是移入回收站，`RETAIN_DAYS=30` 清理**从不释放空间**
  - Opportunity: 一次清空回收站即可回收 ~123GB，足够连续备份 10+ 场
  - Next Step: **授权删除回收站 28 份旧 tgz**（不可逆，需 owner 明确点头）→ 再把 `RETAIN_DAYS` 30→14 并让清理脚本绕过回收站 → 再删 `WSL/` 中 10 月下旬前的 14 份（~108GB）
  - **✅ 旁路已建成本地副本（无需授权，已完成 03:27）**: 原生 `openclaw backup create --verify` → `~/openclaw-backups/2026-11-07T03-15-37.095+08-00-openclaw-backup.tar.gz`（**6.71GB**），`openclaw backup verify` → **Backup archive OK**（276,007 entries / 871 symlinks / SQLite inventory verified）。备份链已不再依赖 NAS，root 分区 797G 可用。**建议后续** `openclaw backup enable` 接成 Gateway 自动任务，彻底绕开「SMB rm 只进回收站」的坑；NAS 那套仍需你授权清回收站
  - 注: heartbeat 文件里 `recycle_backups=0 / recycle_gb=0` 是**假阴性**（脚本自身 rm 后不感知 SMB 回收站），不能作为「无需清理」的依据

- **P0-2 SQLite 回收提交超时（⚠️ 03:20 根因修正：不是租约泄漏，重启无效）**
  - Signal: 源码定位 `dist/session-accessor.sqlite-reclamation-commit-BX3N0u2L.mjs` → `COMMIT_DECISION_TIMEOUT_MS = 5e3`。回收 worker 申请提交授权，需同进程同步写入者在 **5 秒内**完成 `Atomics.compareExchange(shared,0,REQUESTED,COMMITTING)`，否则抛 "checkpoint expired"。main 库 **272MB**（`transcript_events` 99.4MB + `trajectory_runtime_events` 67.9MB + `session_transcript_active_events` 70,714 行）→ 回收事务持写锁 > 5s → **必然**错过窗口 → 每分钟失败（11-06 22x → 11-07 46x）
  - **证伪（旧结论）**: 实测 `agent_database_leases` 10 行，**全部 owner_pid=897835（当前存活进程）、owner_start_time=146381859（与 /proc 一致）、零 stale**；`cron-authority.lock` flock 实测**可自由获取**；`main.sqlite` integrity_check = **ok**（未损坏）→ 是时序/容量问题，不是泄漏、不是损坏、不是锁死
  - Impact: main 侧心跳全线不可用；target=isolated 的 NightOps 与 news-digest 正常，故障面仍限制在 main
  - Blocker: 压缩/瘦身 main 库需要停 Gateway
  - Opportunity: `openclaw doctor --session-sqlite inspect --session-sqlite-all-agents` → **8 agent 全 0 issue**（数据本身干净，只是体积大）；doctor 同时指出 systemd `--max-old-space-size=4096` 偏低（建议 8192，物理 30892MiB）→ 当前 VmRSS 3.29GB / VmHWM 3.59GB 已贴上限，GC 压力会进一步挤掉 5s 窗口
  - Next Step: **停 Gateway → ① `openclaw doctor --session-sqlite compact --session-sqlite-agent main`（无 --dry-run，先自行备份）→ ② systemd 堆 4096→8192 → ③ `openclaw doctor --fix` → ④ 重启** → 30 分钟内验证 `Cron maintenance failed` 与 `Memory Dreaming Promotion` 错误计数是否归零。**单靠重启无效**（无 stale lease 可清，且 272MB 库照旧）

- **P0-2b（新增）cron registry total=1 矛盾已定位**
  - Signal: `~/.openclaw/cron/jobs.json` **文件不存在**（只剩 `jobs.json.migrated` / `jobs-state.json.migrated` / 3×`.bak` + 遗留 `jobs.json.110748.8c98649a303aee88.tmp`）；但 `state.sqlite.cron_jobs` 表里**实有 30 条 job**（NightOps-Orchestrator / Heartbeat(main) / Memory Dreaming Promotion 均在）
  - Impact: Scout 场读到 DB 得 31 条，Life/Orchestrator 场读到缺失的 jobs.json 得 1 条 → **两个 agent 看的是两个不同的源**，此前所有「registry 只暴露 1 条」的推论全部作废
  - Blocker: 无需授权（由 `doctor --fix` 重建）
  - Next Step: 随 P0-2 的 `doctor --fix` 一并重建 jobs.json；**错峰/合并方案要等 jobs.json 恢复后才能验证**

- **P0-2c（新增）无人有权操作 Gateway**
  - Signal: doctor 报 `commands.ownerAllowFrom` **未配置** → 无人可执行 `/update`、重启 Gateway、改配置、批准命令
  - Next Step: `openclaw config set commands.ownerAllowFrom '["<你的 channel user id>"]'`（需你提供 id），配置前 P0-2 的停机操作只能由你手动执行
  - 注：我**不能**自行重启本 Gateway（宿主即被重启对象），P0-2 的停机步骤必须由你执行

- **P0-3 M365 push 授权（本地已就绪，技术上可行）**
  - Signal: HEAD `40b27fc`（stdlib 遮蔽已修 + ruff/CI 落地），ahead 2 / behind 0，非分叉；`git ls-remote` ×5 → 4×rc=0 / 1×rc=128 gnutls_handshake → **判定为间歇性，非凭证缺失、非出站封锁**
  - Impact: 两个已验证修复仍困在本地；远端 pushed_at 停在 2026-03-18，外部停滞 ~2 周（D14+）
  - Blocker: 无需授权即可执行技术动作，但推送到远端属外部副作用，需 owner 点头
  - Next Step: 授权 `git push origin HEAD`（建议重试循环：rc≠0 时 sleep 20s 重试，最多 5 次，命中间歇窗口即成功）

---

## 🟡 P1 — 可自动派发 / 次日跟进

- **P1-1 云端 fallback 全断**：OpenRouter 余额 0（连续第 3 窗确认）/ LiteLLM@NAS 无鉴权且后端 DB 挂 / SiliconFlow key 失效 / LongCat 无 key → 本地 `ollama/qwen3.6:27b` 与 `qwen3:4b-instruct`（实测 3.5s）是唯一兜底。**需 owner 充值或换 key**，否则单点风险长期挂账。
- **P1-2 web_search(duckduckgo) 连续第 17 次 provider_error**；`alignment.openai.com` 直连 SSL_ERROR_SYSCALL → OpenAI misalignment 报告改由 The Decoder 转述（已成既定降级方案，可从「异常」降为「已知降级」）。
- **P1-3 Life 报告连续性**：11-07 场 run ok / delivered=true / 852.7s，产物三份落盘且无残留标记 —— 连续性恢复成立（非「偶发」）。但 852.7s 远高于 360s abort 阈值，需在 11-08 场确认阈值是否已放宽，否则随时可能再断。
- **P1-4 cron registry 可见性矛盾**：Scout 场 31 jobs，Life 场与本场均显示 total=1（已持续 2 场）。**需 owner 在 Control UI 核对真实 job 数与 triggersEnabled 状态**——若 registry 真的只暴露 1 条，NightOps 错峰与合并方案全部无法执行。
- **P1-5 Health agent 仍处停摆**：memory 目录只有 dreaming/，无任何 nightly 产出，cron registry 中查无该 agent 作业。**待 owner 拍板去留**（与 Finance 停摆近 7 个月同属一类挂账项）。
- **P1-6 Finance 停摆近 7 个月**（最后报告 04-07）：待 owner 拍板去留，不再每场占用注意力。

## 🟢 P2 — 观察项

- Life：微博 AI 归零（0/52，观察项①闭环）→ 11-08 核对是否回归；知乎 AI 13.3%↑，产出物化三档口径（作品型 29.63% / 资讯型 1.48% / 猎奇型 0.11%，基线 4.29%）下场面复算。
- Scout：LanceDB 464→516 行，主图 2,565 节点 / 6,058 边 / 38 社区；GHSA 连续 6 窗零新增，但 MCP spec 本窗修了 oneOf 类型检查绕过 → 安全压力在验证逻辑而非已知 CVE。
- 中间产物清理：`scout-raw/`、`graphify-out/` 仅保留最近 7 天。
- BILIBILI_COOKIES / OPENROUTER_API_KEY 仍未配置。

---

## ✅ 本场已闭环（不再占用注意力）

- M365 stdlib 遮蔽（`selectors.py`）→ 已修 + 验证 + 提交本地 `40b27fc`；ruff 34→0 违规 + CI（lint / import-smoke）已落地。
- News Digest 11-06 08:00 场 20,854B 推送成功，作业状态回到 ok。
- 代理 25017 / 8080 FastAPI / ollama 11434（172.18.160.1）双端口可达。
- 根分区 17%、M365 bare-except 0 hits、tracked .pyc = 0、Coder 卫生归档完成。
- MiniMax 直连正常（watchdog err=1，无 429 峰值）；错峰方案优先级下调（实测 heartbeat 相位跨度 26/30 分钟，同相并不严重）。

---

## 📌 明日（11-08）需 Main 拍板的事（按紧急度）

1. **Gateway 停机修复序列**（P0-2，改）—— **不再是「重启一下」**，而是：停 Gateway → `openclaw doctor --session-sqlite compact --session-sqlite-agent main` → 堆 4096→8192 → `openclaw doctor --fix` → 重启 → 30 分钟内验证错误计数归零。**单靠重启无效**。
2. **NAS 回收站清理授权**（P0-1）—— 已断档 2 晚；**但旁路已就绪**（本地原生备份 6.71GB 已验证 OK），不再紧急
3. **M365 `git push` 授权**（P0-3）—— 修复已就绪，仅差一次 push（本次 dry-run rc=0，`d2af52a..40b27fc`）
4. **配置 `commands.ownerAllowFrom`**（P0-2c）—— 否则后续所有 Gateway 操作都要你手动介入

### 🆕 03:20-03:30 实测结论摘要（推翻此前两处判断）
- ❌「SQLite 租约泄漏」→ **错**。零 stale lease，flock 可获取，integrity_check=ok。真因是 `COMMIT_DECISION_TIMEOUT_MS=5e3` 遇上 272MB 的 main 库
- ❌「重启 Gateway 即可修复」→ **错**。无 stale lease 可清，库体积照旧，重启不会改变任何东西
- ✅「cron total=1 矛盾」→ **已定位**：`cron/jobs.json` 文件缺失（DB 里实有 30 条），两个 agent 读的是两个不同的源
- ✅ 备份单点 → **已解除**：原生备份 6.71GB 验证 OK
