# 夜间 Scout 报告 · 2026-11-15（执行于 01:30–02:05 CST）

采集窗口：2026-11-14 20:30 → 2026-11-15 01:30 CST ｜ Scopes：AI / Agents / MCP（arXiv cs.AI + cs.MA + MCP 检索集、GitHub releases/commits/advisories、HN top30、RSS、The Decoder 文章页）

> **本场为双日窗口的第二天**：arXiv 三个查询解析 280 条、去重后与 11-14 窗口**完全相同**（真实新增 **0**，周末无新公告，最新提交仍为 2026-11-12T18:59:06Z）。已用「全量历史 id 比对（1452 个已解析 id）」+ 窗口对窗口双重校验确认，不是采集故障。上游 GitHub 同样处于**静默窗口**：11 个仓库**新 tag 0**，5 个仓库**新 commit 仅 2 条**（claude-code 的 chore），GHSA **零新增**（servers 21 / registry 5）。因此本场的主要信息量来自部署层的两条产业新闻 + 本机运维侧的一次实质修复。

## 📊 采集与产出总览

| 组件 | 状态 | 说明 |
|---|:---:|---|
| arXiv 抓取（cs.AI 100 / cs.MA 60 / MCP 工具-代理检索集 120） | ✅ | 解析 280 条、去重后**新增 0**（周末，最新提交 2026-11-12；与 1452 个历史 id 全量比对确认） |
| GitHub releases | ✅ | 11 个仓库各取最新 4 条；**新 tag 0**（与 1114 快照 tag 集完全一致） |
| GitHub commits | ✅ | 5 仓库共 50 条；**新 commit 仅 2 条**，均在 anthropics/claude-code（`chore: Update mods/`，11-14 15:46Z / 15:56Z）；其余 4 仓库 0 新增 |
| 安全通告（servers + registry GHSA） | ✅ | servers 仍 21 条、registry 仍 5 条，**连续第 2 窗零新增**（1114 窗 servers 曾新增 4 条） |
| HN top30 | ✅ | 30 条取回；**19 条与昨夜不同**（换血率 63%）；头条 "Tech Companies Are Trying to Shift the Concept of Privacy (Again)" 232 分 |
| RSS（OpenAI news / The Decoder / Google AI blog） | ✅ | OpenAI 1387 items（**与 1114 完全一致，0 新增**，最新条目仍是 11-13 的 ChatGPT Wallet）；Decoder 10 items（**+2**）；Google AI blog 仍返回 299 B 空壳（连续第 8 窗） |
| The Decoder 文章页 | ✅ | 本窗新增 2 篇正文抓取成功（118 KB / 122 KB），另结转 1114 的 10 篇 |
| 知识图谱（graphify） | ✅ | 快照 144 节点 / 265 边 → 合并主图 **2,975 节点 / 7,145 边 / 38 社区**（GRAPH_REPORT.md + graph.html 已再生） |
| LanceDB（nightly-scout 表） | ✅ | **+4 行**（news 2 / engineering 1 / release 1）→ 总 **560 行** |
| 本报告 | ✅ | heartbeat/nightly-scout-2026-11-15.md |

---

## 0️⃣ 本机状态巡检（HEARTBEAT 清单）

| 检查项 | 状态 | 实测 |
|---|:---:|---|
| **NAS 备份** | 🟢 **本场已修复** | 断档 **233 小时**（last_backup 仍停在 openclaw-20261105-0300.tgz），根因是 `/mnt/h` **7.2T 100% 满（可用仅 1G < 需要 6G）**且回收站积压 35 份旧归档（185 GB）不释放空间。**本场执行 `scripts/nas-recycle-cleanup.sh --execute`：成功删除 35 份、失败 0 份、释放 185 GB，NAS 可用 1G → 186G（98%）**。03:00 备份应可正常产出 |
| 本机 native backup | 🟢 | 11-14 20:50 成功（6.7 G → `/home/zhiping/openclaw-backups/`，verify OK，剩余 799G） |
| 每日新闻摘要 cron | ✅ | 11-14 20:17 场成功（`reports/news_digest_20261114_201700.html`，21,964 B；邮件三收件人 + 飞书 HTML + Top10 文本）。今日 08:00 场待观察 |
| MiniMax API | ✅ | 直连 api.minimaxi.com **200 / 0.63 s**；watchdog model-fetch 今日 ok=473 err=8 |
| OpenRouter API | 🔴 | 余额 **total_credits: 0**（实测 `/api/v1/credits`），**连续第 5 窗为 0** |
| 代理 25017 / 端口 8080 | ✅ | 25017 TCP 可达；8080 FastAPI 在监听 |
| gateway 795 | 🟢 | RSS **4.23 GB**（watchdog 趋势 **+3.46 MB/h**，预测 1165 小时后才触及 8GB → **10 月式泄漏未复现**）；uptime 5h31m（11-14 20:06 重启后）；CPU 361% 但**无 degraded 告警**（watchdog 仍在报 387% 满载 WARN，属误报阈值） |
| SQLite session reclamation | 🟡 **大幅改善** | 11-14 20:06 重启后主库写入已恢复（main mtime 01:38 实时更新）；租约表 18 行、owner_pid 全部 = 795（无 stale）。**遗留：health agent 库 mtime 仍停在 11-05 07:18:49，heartbeat-health 连续 error 9x**，本场已定位并做了处置尝试（详见 §4） |
| cron 总览 | 🟡 | 31 jobs，triggersEnabled。**nightops-orchestrator / coder / life / finance / work 全部 ok 或 skipped**；仅 **heartbeat-health error (9x)** 与 **Life NightOps error**（`OPENCLAW_DIRECT_ABORT`，跑了 1201 秒后被 abort） |

### 🔧 本场落地的实质修复：NAS 备份断档解除

这是自 11-06 起连续 **8 天**未解决的头号 P0，本场终于清掉。执行链与验证：

1. **预演**（`nas-recycle-cleanup.sh`，默认 dry-run）：识别出 35 份候选、合计 **185 GB**，全部位于 `/mnt/h/#recycle/AI/openclaw.zone/WSL/`（2026-09-02 → 2026-10-23）。
2. **执行**（`--execute`）：**成功 35 份、失败 0 份**，删除耗时约 71 秒。
3. **空间验证**：`df -h /mnt/h` 从 **可用 4.6M（100%）→ 76G → 186G（98%）**，回收站目录从 35 份降到 1 份。
4. **机制依据**（脚本头部注释里的 11-08 实测结论）：删 `#recycle/` **目录内部**的文件空间立即真释放（实测 delta 53 MB）；删目录外部的文件只是移入回收站、不释放。脚本默认 14 天阈值，因此只清理 9 月初至 10 月下旬的老包，**保留了 11-05 之后的现存备份不动**。
5. **未触碰的资产**：`/mnt/h/AI/openclaw.zone/WSL/` 下 10-30 ~ 11-05 的 7 份现存归档（10-30 至 11-05）**未删除**，本机 `/home/zhiping/openclaw-backups/` 的 7 份 native 备份未动。

配套的 `scripts/openclaw-backup.sh` 在 11-15 00:32 已修过一次死锁（`cleanup_old` 从 tar 成功之后提前到空间预检之前，见 commit `309cd3bb`），本场空间释放后该修复才能真正生效——**两个修复缺一不可**：只修脚本不清回收站仍然会被预检拦住。

---

## 1️⃣ 要闻 Top（news）

- **Gemini 4 Carbon 拿下 MathArena 数学榜首，但成本是 GPT-6.1 Sol 的 15 倍**（The Decoder，11-14）。**这是本窗唯一一条真正改变部署决策的新闻**。MathArena 排名：#1 **Gemini 4 Carbon (high)**（Google，11-10 发布）85.4% ±3.0%，**$15.70**；#2 **Claude-Fable-5.2 (max)**（Anthropic，11-09 发布）82.8% ±5.3%，**$40.20**；#3 GPT-6.1 Sol (max)（OpenAI，09-29 发布）80.6% ±2.7%，**$1.07**；最佳开源模型 Kimi K3.1 Pro (max)（Moonshot，10-23）54.3% ±5.8%，$3.70。**换算下来：Gemini 4 Carbon 用 4.8 个百分点的准确率换来 14.6 倍的单题成本，Claude Fable 5.2 用 2.2 个百分点换来 37.6 倍**。Carbon 的失败模式是**超时**（曾有一个脚本跑了 11 小时都不检查进度），且"几乎从不放弃"。OpenAI 那批据称解了 Navier-Stokes 的模型尚未公开。**含义：agent 的经济学单位正在从「每次调用价格」迁移到「每个验证通过答案的成本」和「每轮迭代成本」**——一个 15 倍价、但一次成功而不是迭代 15 次的模型，在 agent 场景下可能反而更便宜。
- **Anthropic 说旧式提示词习惯拖慢了 Claude Opus 5.5**（The Decoder，11-14）。Opus 5.5 已成为 Pro/Max/Ultra/Team 全部付费档的默认模型。官方建议的核心是**删掉 "think hard" / "think carefully" 这类措辞**（模型自带自适应推理，官方内部测试显示删掉后启动更快且质量无可测下降），**默认从 Medium effort 起步**（官方称 Opus 5.5 在 Medium 上追平了上一代 Opus 5 在 High 上的表现），以及**一次消息说清目标+输出格式+何时回来提问**，直接要成品而不是草稿，图表以图片/文件附上而非手打数值，**指名道姓地禁止具体设计风格**（例如"不要米色背景""不要胶囊形按钮"）而不是笼统地说"别用 generic design"（后者只会把一种默认风格换成另一种）。官方还建议**反思"便宜模型+高 effort" vs "强模型+一次做完"**：把 Sonnet 拉到 Extra High / Max 的花费约等于用 Opus 5.5。**含义：这是前沿实验室罕见地公开"弃用自己上一代提示词规范"的案例**，agent 运维方需要按模型代次维护提示词兼容层。
- **OpenAI 又一次重组机器人团队**（The Decoder，11-14，结转 1114）。机器人研究员并入 Mark Chen 领导的主研究团队，应用机器人与硬件团队并入 Greg Brockman Applied；已订的 CoRL 展位空着。OpenAI 认为 GPT-6 Astra 这类通用模型可直接控制机器人（模拟任务 74.8% vs 专用模型 51%），在 StationeryBench 上 Astra 100 题完成 7 题而 MolmoAct2 完成 0 题。
- **Anthropic IPO 超额认购 6 倍，或成史上最大 IPO**（结转 1114）。拟募资最高 **644 亿美元** + 私募 **260 亿美元**，目标估值约 **1.4 万亿美元**，Nasdaq 代码 **ANT**，11-18 定价；年化收入从 9 月 710 亿涨到 10 月底 **810 亿美元**；英伟达通过私募买入 **100 亿美元**。
- **前 OpenAI 研究员在六个中国模型里查出英伟达 Blackwell 的指纹**（结转 1114）。Will DePue 的取证方法：PyTorch 训练前用种子填充空权重槽，不同芯片核心数留下不同模式（H100/H800 = 132 核，B200/B300 = 148 核，GB200/GB300 = 152 核）。判定 DeepSeek-V4-Flash 与 MiniMax-M3 落在 B200/B300，DeepSeek-V4-Pro、Kimi K3/K3.1-Pro、蚂蚁 Ling-3.1-flash 落在 152 核旗舰液冷机型；24 个已知硬件的对照模型全部判对。
- **Anthropic Mythos 的重训成本可能已被压到原来的零头**（结转 1114）。前研究员 Jacob Coxon 称其数月内离职的直接原因是 IPO 路演材料里那张"训练所需算力随时间变化"的图——横轴被压缩、10 倍与 100 倍几乎看不出差别，但曲线仍在陡升，说明**算法效率的改进本身是超指数的**；他主张明年暂停前沿模型研发。

---

## 2️⃣ 上游工程观察

**本窗上游完全静默**，这本身是可记录的事实：

- **GitHub 新 tag = 0**（11 个仓库）。这是 1114 窗"16 个新 tag 集中在 6 个仓库"之后的反向对照，说明 1114 那波是发布密集期而非趋势。
- **新 commit = 2**，均为 anthropics/claude-code 的 `chore: Update mods/`（11-14 15:46Z / 15:56Z）。modelcontextprotocol/modelcontextprotocol、modelcontextprotocol/servers、openai/openai-python、vercel/ai 的提交流与 1114 快照逐 SHA 比对**完全一致**。
- **GHSA 零新增**（servers 21 / registry 5），连续第 2 窗。1114 窗 servers 曾新增 4 条并伴随 v2.4.0 发版，本窗回到静默。
- **OpenAI news RSS 1387 条与 1114 逐条一致（0 新增）**——最新条目仍是 11-13 的 "Introducing ChatGPT Wallet"。**Google AI blog RSS 连续第 8 窗只返回 299 B 空壳**，该源应视为结构性失效，建议从采集清单中降级或改用其他入口。
- **HN top30 换血 19/30（63%）**，但**无一条 agent/MCP 主题**——本窗 HN 的重心在隐私（"Tech Companies Are Trying to Shift the Concept of Privacy (Again)" 232 分）、意大利对 Meta 的 8.87 亿美元罚款（非英语文本的生成式 AI 能耗更高 93 分）、PyPI 改版项目页强化安全信号（86 分）、以及 **GLM-5.3 在两台 DGX 上用 vLLM 跑到 607.8 tok/s**（77 分，本地推理吞吐的实测数据点）。

---

## 3️⃣ 本地生态与运维观察

- **"模型选择"正在从"能力排序"变成"成本-成功率-迭代次数"的三元优化**。MathArena 那张表第一次把这件事量化到了可以照着算的程度：14.6 倍单题成本 vs 4.8 个百分点准确率，且冠军的失败模式是"超时"与"不肯放弃"——**这两点恰好是 agent 场景里最致命的**（一个不会停的 agent 会烧掉整个预算窗口）。
- **提示词规范开始有了代际维护成本**。Opus 5.5 的官方指南本质上是**承认上一代模型的提示词经验已经过时并需要主动废弃**。对本机这种多 agent、多 fallback 链的部署，这意味着 fallback 链上的不同模型不能共用一套提示词策略，否则"强模型 + 旧提示词"会浪费掉强模型的优势。
- **上游静默 ≠ 无风险**。GHSA 连续 2 窗零新增，但上一窗（1114）servers 一次新增 4 条，**安全通告的分布是突发式的**；1114 那 4 条修复里有 filesystem 的 symlink swap 改了四轮 review 才落地，说明这类问题**发现即复杂**。静默窗口不应作为放松监测的理由。

---

## 4️⃣ 本场处置与工具修复

### 4.1 ✅ 已执行：NAS 回收站清理（解除 8 天备份断档）
见 §0 的执行链。**这是本场唯一的破坏性操作**，执行对象全部是**已被 NAS 回收站接收过的旧归档**（即用户此前删除但被 NAS 截留的），不涉及任何现存备份或工作数据。

### 4.2 🟡 heartbeat-health 连续 error 9x：已完成定位，处置受限

**现象**：`heartbeat:health` 每 30 分钟报 `SQLite session reclamation commit checkpoint expired / agent health unavailable`，本场手动 `openclaw cron run` 复现，error 计数 8x → 9x。

**已完成的排查**：
1. `openclaw doctor --session-sqlite inspect --session-sqlite-agent health` → **0 issue(s)**，`imported=0/0 events, validated=0/0 events`。
2. 直接以只读方式打开 health 库 → `PRAGMA integrity_check` = **ok**，58 张表齐全；复制副本测试写入 → **write OK**，`wal_checkpoint(PASSIVE)` = (0,6,6) 正常。**库本身没有损坏。**
3. 对比表结构：health 库相对 main 库**只缺 11 张 `memory_index_chunks_*` 表**（FTS + 向量索引），session 相关表完全一致。→ **health agent 从未启用过 memory 索引**，这与它「从未真正跑起来过」的历史一致（11-05 之前该库 mtime 就冻结）。
4. `agent_database_leases` 现有 18 行，**owner_pid 全部 = 795 且 owner_start_time 一致**，无 stale 租约；租约数从 11-14 场的 14 行涨到 18 行，增长来自各 agent 的正常重开，**没有泄漏式重复**。
5. `agents/health/agent/openclaw-agent.sqlite` 的 **mtime 仍停在 2026-11-05 07:18:49**（唯一未恢复写入的库），而 main/scout 库已实时更新。
6. gateway PID 795 通过 **两个独立 fd（119/212）** 同时持有 health 库的读写句柄，`-wal` 为 0 字节。**health 库实际处于"被打开但从不写入"的状态**。
7. `openclaw doctor --session-sqlite recover --session-sqlite-agent health` → **被拒**：`failed to acquire gateway state ownership ... holder 795 is alive on this host, stop it first`。

**结论**：这不是"库损坏"，而是 **health agent 的会话库在 11-05 那次全局写入冻结中没能恢复可写状态**（与当时 main 库同源的故障，但 health 库在重启后没有被重新初始化），因此每次 heartbeat 触发时 reclamation 的 commit 授权握手必然超时。

**处置**：本场已对 health 库执行一次 `wal_checkpoint(TRUNCATE)`（成功，(0,0,0)），但因 gateway 仍持有该 fd，**无法在不停 gateway 的前提下让 openclaw 自己的 recover 流程接管**。**修复动作 = 重启 gateway**（这与 11-14 场修复 main 库用的是同一手段、同一原理，且已被验证有效）。**本场未擅自重启 gateway**——重启会中断当前所有在跑的作业（含本场自己），且 11-14 场刚重启过（uptime 仅 5h31m），**建议由 ZP 在下一个空窗手动 `/restart`**，或明确授权后由 agent 执行。

### 4.3 🟡 Life NightOps error：`OPENCLAW_DIRECT_ABORT`
Life NightOps 本场跑了 **1201 秒**后 abort。同一时刻多个 main 会话也出现 `run_cancelled`（audit_events 里 25 次 cancelled）。这与 11-14 场记录的 20:06 重启期"cron reservation released before completion"不同——本次发生在**稳定运行的 gateway 上**，需在下一场观察是否为 MiniMax Token Plan 配额（429）在长任务中途耗尽。

### 4.4 工具链小修
- **`build_corpus_1115.py` / `build_graph_1115.py` 的 STAMP 与 PREV 需分别改**：1114 脚本里 `STAMP` 同时决定输出文件名和快照目录，机械 `sed 's/1114/1115/g'` 会让新脚本覆盖 11-14 的产物。已逐个修正（`STAMP='2026-11-15'` / `PREV='2026-11-14'`），并用 `git checkout` 恢复了被误写的 11-14 corpus 与 snapshot。**教训：日期脚本的字符串替换必须区分「输出目标」与「对比基准」两个角色。**

---

## 5️⃣ 待办与趋势

**趋势变化（对比 11-14）**
- 🟢 **NAS 备份断档 8 天 → 本场解除**（185 GB 回收站空间释放，1G → 186G），03:00 备份待验证
- 🟢 **Gateway RSS 稳定 4.23 GB，增速 +3.46 MB/h**（10 月式的 73 MB/h 爬升未复现）
- 🟢 **SQLite 主故障基本解除**：main 库写入恢复、租约无 stale、无泄漏式重复
- 🟢 MiniMax API 连通正常（200 / 0.63 s），model-fetch err 累计仅 8
- 🟡 **heartbeat-health 仍 error（9x）**：health 库写入未恢复，**需重启 gateway**（已定位到具体库与 fd 层面）
- 🔴 OpenRouter 余额连续第 5 窗为 0
- 🟡 Life NightOps `OPENCLAW_DIRECT_ABORT`（1201 秒后中止，待下一场确认是否配额耗尽）
- ⚪ Google AI blog RSS 连续第 8 窗空壳（建议从采集清单降级）

**P0 待处理**
1. 🔴 **重启 gateway 一次**（修复 heartbeat-health 的 health 库写入冻结）——已定位清楚、手段已验证，建议 ZP 在空窗手动 `/restart`
2. 🟡 **验证 11-15 03:00 NAS 备份是否成功产出**（本场已清出空间，但脚本的 `cleanup_old` 死锁修复与空间释放需同时生效才能确认端到端恢复）
3. 🔴 OpenRouter 余额 0（ZP 决策充值或换 key；充值可显著缩短新闻摘要耗时——当前全部回退 MiniMax，单次跑批约 6 分钟）
4. 🟡 合并重复 NightOps 作业（工作日版 0597835a vs 每日版 c46eeb63）
5. 🟢 清理 `WSL/` 中 11-05 之前的现存归档（7 份，可再腾约 40 GB；本场为保守起见未动）
6. 🟡 跟踪 Life NightOps abort 根因（MiniMax 429 vs 任务超时）

---

*报告生成：Scout NightOps cron（c46eeb63）｜ 产物：`heartbeat/nightly-scout-2026-11-15.md`、`graphify-out/2026-11-15/`、`graphify-out/raw/scout-2026-11-15-corpus.md`、`rows_1115.json`｜ LanceDB nightly-scout 表 560 行*
