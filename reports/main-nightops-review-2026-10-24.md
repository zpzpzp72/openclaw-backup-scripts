# Main NightOps 全局复盘 — 2026-10-24 05:05 CST

*Main agent 汇总 8 个子 Agent 报告 + 实测复核 + 升级审核*

---

## 📊 服务状态总览

| 服务 / 组件 | 状态 | 实测证据 | 负责人 |
|---|---|---|---|
| Gateway 进程 | 🟡 可用但劣化中 | PID 281814, uptime 2h37m, **RSS 5.9GB**（01:19 重启后 3.75GB → 现 5.9GB）, CPU 278% | Main |
| MiniMax M2.7 (主) | 🟢 正常 | 05:03 起连续 status=200, elapsedMs 1294-2497 | — |
| MiniMax M3 | 🔴 burst 额度耗尽 | status=429 至 05:01:34, 今日 402 次 429 | 需决策 |
| ollama (本地兜底) | 🟢 **唯一可用 fallback** | /v1/models 200; qwen3:4b-instruct → "OK" 3.0s; qwen3.6:27b 200 | — |
| LiteLLM @ NAS | 🔴 **DB 挂** | http=400 {"error":{"message":"No connected db.","code":"no_db_connection"}} | 需决策 |
| longcat | 🔴 无 key | 401 | — |
| siliconflow | 🔴 key 失效 | 30014 Token is invalid | — |
| openrouter | 🔴 余额 0 | 402 / total_credits=0 | 需决策 |
| cron 引擎 | 🟢 正常 | 31 jobs, triggersEnabled=true | — |
| 备份 (NAS) | 🟢 正常 | 03:21 生成 8.9GB, status=ok, 40 份 / 202G | — |
| NAS 容量 | 🟡 偏高 | 7.2T 用 97%, 剩 288G | P1 |
| 代理 :25017 | 🟡 半瘫 | TCP 通但 CONNECT 到 news.ycombinator.com / theverge.com 挂死 8-11s | P2 |
| Feishu 推送 | 🟢 正常 | 01:17 digest 推送成功 | — |
| News Digest cron | 🟡 仍 error(5x) | 10-24 01:11 手工跑通, 08:00 定时待验证 | Scout |
| M365_Copilot_Playwright_Proxy | 🟡 解冻待定型 | commit e5f498e, 但仍 HISTORY_DIVERGED | Coder |
| Life / Health / Finance | 🔴 无产出 | Life 最后 09-08, Health memory 空, Finance 最后 04-07 | 需决策 |
| openclaw-weixin 插件 | 🔴 不兼容 | v2.4.9 vs core 2026.10.5, 启动刷 10 条 ERR_PACKAGE_PATH_NOT_EXPORTED | P2 |

---

## 🔴 P0 — 升级审核（需 Main 决策）

### P0-1【配置冲突】fallback 链被两个 Agent 改成了互相矛盾的状态
- **Signal**: Scout (01:28-02:05) 把 **所有 8 个 agent** 的 fallback 首选项改成 `litellm/MiniMax-M3`；Orchestrator (04:50) 判定 LiteLLM NAS DB 挂，**已把 litellm 从链中移除**并改为 `ollama/qwen3:4b-instruct` 优先。
- **实测现状（05:05 读 openclaw.json）**：
  - `agents.defaults.model.fallbacks` = `['ollama/qwen3:4b-instruct','ollama/qwen3.6:27b','longcat/LongCat-2.0']` ✅ 无 litellm
  - `agents.entries.{main,orchestrator,scout,coder,life,finance,work}` = `['litellm/MiniMax-M3', 'ollama/qwen3.6:27b', 'longcat/LongCat-2.0']` 🔴 **首选项 litellm 已死**
  - `agents.entries.health` = `['litellm/MiniMax-M3','ollama/qwen3.6:27b','minimax/MiniMax-M2.7']` 🔴 同上
- **Impact**: 7/8 agent 的 fallback 第一棒是已确认 `no_db_connection` 的死链。每当主模型 429，链路会先浪费一次请求去撞 LiteLLM，再落到 ollama —— 增加失败延迟，且在 LiteLLM 恢复前这条死链会持续存在。
- **Next Step**: 把 8 个 agent 的 fallback 统一收敛为 `['ollama/qwen3:4b-instruct','ollama/qwen3.6:27b','minimax/MiniMax-M2.7']`（去掉 litellm 与 longcat 两个当前不可用项），与 `defaults` 对齐。
- **归属**: Scout / Orchestrator 各自只改了一半，没有全局收敛机制。**这正是需要 Main 统一裁决的升级项。**

### P0-2【账单】MiniMax Token Plan burst 额度与 NightOps 时段完全重叠
- **Signal**: 今日 02:00-05:01 共 **402 次 429**（"已达到 Token Plan 用量上限"），峰值集中在 04:53-05:01（本次 NightOps 窗口）。06:05 Orchestrator 复测 200 已恢复，但窗口内会再次耗尽。
- **Impact**: 5 路 NightOps cron（Main 05:00 / Scout 04:00 / Life 04:20 / Coder 04:40 / Orchestrator 04:50）**恰好落在耗尽峰值** —— 这是「连续失败 5-6 次」的直接推手，而非配置问题。
- **Next Step（择一或并行）**:
  a) 升级 Token Plan 套餐（需付费，需 ZP 批准）
  b) **把 5 路 NightOps 错峰到 00:30-03:30**（避开 02:00-05:00 高峰）← 零成本，推荐
  c) 确认额度重置周期后重排

### P0-3【账单】OpenRouter 余额 0，LiteLLM DB 挂 — 两条云端兜底同时失效
- **Signal**: OpenRouter `/api/v1/credits` → `total_credits: 0`；LiteLLM `no_db_connection`。
- **Impact**: 当前唯一可用 fallback 是**本地 ollama 单点**。MiniMax 一旦 429，NightOps 立刻退化为本地 4B 小模型，质量断崖下降（qwen3:4b-instruct 适合 cron 摘要，不适合复杂推理）。
- **Next Step**: a) 修 LiteLLM@NAS 的 DB 挂载（一次修复即恢复 11 个模型，含 deepseek 系）；b) OpenRouter 充值或从链中移除；c) 换 SiliconFlow key。
- **注意**: 这两项都涉及**付费/凭证**，属于 ZP 的决策，不在 agent 自动处理范围。

### P0-4【基建】LiteLLM@NAS DB 挂的根因未定位
- **Signal**: 持续 `no_db_connection`，与 Orchestrator 报告一致。
- **Impact**: 长期失去 deepseek 系 fallback 与 11 个模型的云端冗余。
- **Next Step**: NAS 侧检查 LiteLLM 容器的 postgres 挂载/volume（非本机 WSL 范围，需 NAS 侧操作或 ZP 确认）。

---

## 🟡 P1 — 明日处理

### P1-1 Life / Health / Finance 三个 Agent 长期无产出
- **Signal**: Life memory 最后写入 2026-09-08（46 天，仅 dreaming 目录有 10-02/10-09/10-20 记录，说明 dreaming 任务活着但主任务死了）；Health `memory/` 目录**完全为空**（只有 .dreams/dreaming 子目录，无任何日报）；Finance 最后产出 04-07。
- **Impact**: 三个 Agent 的 cron 全部 error（Life NightOps error 6x、Health-Weekly-IMA-Scan error 4x），属于"进程活着、任务空转"。
- **Next Step**: 逐一 ping 确认 agent 存活 + 检查其 HEARTBEAT checklist 是否被触发。Health memory 为空需确认是 BOOTSTRAP 未完成还是路径迁移（`agents/health/memory/` 存在但无 md 文件）。

### P1-2 M365_Copilot_Playwright_Proxy：解冻后仍需定型
- **Signal**: Coder 已修 `browser.py` bare except + .gitignore + commit `e5f498e`（终止 220 天冻结）。但 **HISTORY_DIVERGED 仍未解决** —— origin/main 的 `d2af52a` ("Recreate" commit) 不在本地 HEAD，`git push` 是 non-fast-forward。
- **Impact**: 4 个本地 NightOps commit 仍推不上 origin（无凭证 + 分叉）。修 bare except 解决了代码质量，但没解决历史分叉。
- **Next Step**: 决定复活还是归档。若复活：(a) `.gitignore` + `git rm --cached` 清 .pyc（已做）；(b) `git pull --rebase origin main` 或 fresh clone；(c) rebase NightOps commits；(d) push --force-with-lease。**归档窗口 2026-11-07 到期（剩 14 天）。**

### P1-3 NAS 保留策略缺失
- **Signal**: 40 份备份共 202G，单份 8-9GB，NAS 已用 97%（剩 288G）。无任何保留/轮转策略。
- **Impact**: 按当前速率，约 30 天内会写满 NAS，届时备份全部失败。
- **Next Step**: 加保留策略（建议保留最近 7 份 + 每周 1 份 + 月度 1 份，预计压到 ~70G）。

### P1-4 Gateway RSS 二次劣化趋势
- **Signal**: 01:19 重启后 RSS 3.75GB → 05:05 已 **5.9GB**（+2.15GB / 3.7h），CPU 278%。这是 Scout 记录的老问题（4d13h 涨到 10.8GB）的复现初期。
- **Impact**: 若不干预，按此前速率约 1-2 天会再次触发 fetch dispatcher 劣化 → 全线 model-fetch 失败。
- **Next Step**: 观察 24h RSS 曲线；若 12h 内破 8GB 立即重启。Scout 已增强的 cron-watchdog.sh 已能报 RSS>8GB 与 model-fetch 成功率，**接入告警**。

### P1-5 全仓残留 127.0.0.1:25017 清理
- **Signal**: Orchestrator 已修 `openclaw_news_digest.py`(3处) + `run_news_digest.sh`(2处)。state/*.sqlite、backup jsonl 等非活跃文件仍含旧地址。
- **Next Step**: grep -rn '127.0.0.1:25017' ~/.openclaw --include='*.py' --include='*.sh' 全量清理并加 pre-commit 门禁。

---

## 🟢 P2 — 持续关注

- **P2** News Digest 补跑 10-22 ~ 10-23 缺失（08:00 自动恢复，待验证）
- **P2** memory-lancedb-pro 23:00 超时告警 / auto-recall 被治理过滤（05:03 有 suppressedFiltered=4）
- **P2** openclaw-weixin v2.4.9 与 core 2026.10.5 不兼容，每次启动刷 10 条错误
- **P2** api.minimaxi.com vs api.minimax.io 域名混用（DNS 同时解析两者）
- **P2** Feishu APP_SECRET 在 send_digest_feishu.py 里仍是明文，与 gateway 侧 SecretRef 形成双份凭证，建议统一走 SecretRef
- **P2** 代理 :25017 端口通但 CONNECT 挂死，建议要么重启上游代理进程，要么让 digest 全走直连
- **P2** News Digest 源站可用性实测（01:55）：✅ Bilibili(20)/小红书(3)/HN(3)/MS AI(3)/TechCrunch(2)；❌ Reddit×3、OpenAI Blog、Google AI Blog(SSL EOF)、Meta AI(SSL EOF)、36kr、机器之心、量子位、爱范儿、少数派、极客公园、知乎×3

---

## 📋 需 ZP 决策汇总

| # | 决策项 | 紧迫度 | 是否涉及付费 | 建议 |
|---|--------|--------|-------------|------|
| 1 | **8 个 agent 的 fallback 链统一收敛**（去掉死链 litellm/longcat） | 🔴 P0 | 否 | 直接做，无需等 |
| 2 | **NightOps 5 路错峰到 00:30-03:30** | 🔴 P0 | 否 | 直接做，零成本 |
| 3 | LiteLLM@NAS DB 修复 | 🔴 P0 | 否 | NAS 侧操作 |
| 4 | MiniMax Token Plan 升级 / 换供应商 | 🔴 P0 | **是** | 需 ZP 批准 |
| 5 | OpenRouter 充值 / 移除 | 🔴 P0 | **是** | 需 ZP 批准 |
| 6 | Life/Health/Finance 唤醒 | 🟡 P1 | 否 | 日间处理 |
| 7 | M365 repo 复活 vs 归档（11-07 到期） | 🟡 P1 | 否 | 日间处理 |
| 8 | NAS 备份保留策略 | 🟡 P1 | 否 | 日间处理 |

---

## 📝 本次复盘的关键发现

> **1. 本轮 NightOps「失败」的真实原因已彻底澄清：不是代码问题，是三个叠加的外部因素**
> - 代理地址硬编码（Scout/Orchestrator 已修）
> - gateway 长驻进程劣化（Scout 已重启解决）
> - **MiniMax burst 额度在 NightOps 时段耗尽**（尚未解决，是当前唯一还在起作用的杀手）
>
> **2. 但两个子 Agent 的修复互相覆盖，留下了一个新的、更隐蔽的问题**
> Scout 把 litellm 提到 fallback 首位（因为当时 LAN litellm 能直连），Orchestrator 稍后又把它移除（因为 NAS DB 挂了）。
> **两人都没做全局收敛** —— 7/8 个 agent 的 fallback 第一棒目前是死链。
> **教训：多 Agent 并行改同一份全局配置时，必须有单一裁决者，否则后写的覆盖先写的。**
>
> **3. Scout 报告中的一个细节值得肯定但需修正**
> Scout 修正了「之前误判代理宕机 12 天」和「cron-watchdog.sh 是空文件」的记录 —— 这正是可复现实测优于推断的体现。
> 但 Scout 把 fallback 首选指向一个**已经确认 DB 挂**的 provider，这个动作本身缺少实测复核（Scout 的实测发生在 01:28，Orchestrator 的 DB 挂判定在 04:50，Scout 没看到后者）。
>
> **4. 本地 ollama 是当前唯一的救命稻草，实测可用**
> qwen3:4b-instruct 3.0s 返回正确内容，qwen3.6:27b 也能出内容但只吐 reasoning。
> 建议：把 qwen3:4b-instruct 保留为 cron 类任务首选兜底，qwen3.6:27b 留作深度任务。

---

*Main NightOps — 2026-10-24 05:05 CST*