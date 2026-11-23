# Scout NightOps — 2026-11-24

> 正常单夜窗口（宿主机自 11-22 21:38 起持续运行，第 28 小时）。上游三源恢复产出：arXiv **+173**（破两窗零静默）、The Decoder **+6**（本系列单窗最大跳变）、GitHub **9 新 tag**。本窗分析主线是**架构（loop transformer）与证明经济学**。

## 0. 心跳检查清单

| 项目 | 状态 | 证据 |
|---|---|---|
| DIRECTIVE.md | 无新指令（仅"暂无指令"） | 空扫描 |
| 每日新闻摘要 | 🟢 11-23 08:00 场成功：`news_digest_20261123_080344.html`（19,619 B）+ 飞书 `om_x100b7f0c60770ca0c1ffc9050ac3bae` + 邮件三收件人 | `~/.openclaw/logs/news-digest-cron.log` 尾部 |
| MiniMax API | ✅ 直连 200 / 0.28 s | curl 实测 `api.minimaxi.com` |
| OpenRouter API | 🔴 `total_credits: 0` — **连续第 10 窗为 0** | 从 finance agent 库提取 key 查 `/api/v1/credits` |
| 代理 25017 | ✅ TCP 可达 | `172.18.160.1:25017` TCP_OK |
| 端口 8080 FastAPI | ✅ 在监听 | TCP 探测通过 |
| NAS 备份 | 🟢 `openclaw-20261123-0300.tgz`（6,120,252,420 B）已落盘；/mnt/h 可用 198G | `WSL/` 目录；`backup-cron.log` 03:00:01 status=ok |
| 本机 native backup | 🟢 11-23 03:51 verify OK，归档数 8→7，剩余 779G | `native-backup.log` |
| NAS 回收站守卫 | 🟢 11-23 03:20 正确跳过（可用 368G ≥ 阈值 64G） | `nas-recycle-guard.log` |
| gateway RSS | 🟢 **2.61 GB**（PID 36001，uptime 20h50m）；watchdog 趋势 **−424 KB/h（负增长）** | ps + `cron-watchdog.log` |
| gateway CPU | 🟢 **5%**（较昨夜 222% 大幅回落） | watchdog |
| cron 总览 | 🟡 19 jobs 可见（含本场 running） | `openclaw cron list` |
| memory | ✅ 已新建 `agents/scout/memory/2026-11-24.md` | — |

### cron 失败情况
- `heartbeat:work` **error (24x)** — `SQLite session reclamation commit checkpoint expired. Sessions remain unavailable. Stop the Gateway, run "openclaw doctor --fix" ... and restart.`
- `Orchestrator NightOps` **error (2x)** — 同上
- 其余 `heartbeat:*` 全部 skipped（`empty-heartbeat-file` / `no-route` / `cron-in-progress`，属正常空转）
- `Scout NightOps`（本场）running；`Life NightOps` ok、`Coder NightOps` ok、`openclaw-news-digest` ok、`memory-weekly-audit` ok

### agent 库 mtime（写入冻结复核 —— 11-22/11-23 结论修正）
| agent | mtime | 判定 |
|---|---|---|
| scout | 11-24 01:34 | ✅ 正常（本场在写） |
| main | 11-23 23:30 | ✅ 正常 |
| coder | 11-23 04:42 | ✅ 正常 |
| life | 11-23 05:13 | ✅ 正常 |
| work | 11-23 04:42 | ✅ **正常**（此前一直判冻结，本窗起恢复写入） |
| **health** | **11-23 04:42** | 🟢 **已恢复**（此前 11-16 04:13 冻结，本窗跳到 11-23 04:42） |
| **finance** | **11-23 04:35** | 🟢 **已恢复**（此前 11-16 04:12 冻结） |
| **orchestrator** | **11-23 04:36** | 🟢 **已恢复**（此前 11-17 04:12 冻结） |

> **重要修正**：11-22/11-23 两窗据 `openclaw-agent.sqlite` 主文件 mtime 判定 health/finance/orchestrator 三库"写入冻结第 6–7 天"。本窗复核发现这三个库 mtime **均已跳到 11-23 04:3x**，而当时正是宿主机 11-22 21:38 重启后的首次写入。
> → **结论推翻**：三库从未真正冻结，是 11-22 21:38 重启前的**陈旧 mtime 快照**被连续两窗误读为"冻结"。重启确实有效，只是生效时刻被误判为"无效"。
> **教训**：mtime 是弱证据。"库损坏"这类结论至少需要三个独立观测量交叉验证（本窗为 mtime + heartbeat 状态 + doctor 输出），不能只凭单一 mtime 连续两窗就升级为"重启已证伪"。

### `openclaw doctor` 实测（本窗新跑）
- 输出：无 error 级问题；仅提示 TOOLS.md 迁移预览（coder/work 各一条）、startup migration 提醒、以及一条 **secret runtime degradation**：`~/.openclaw/agents/work/agent/openclaw-agent.sqlite` 的 secret resolution failed，retry 建议 `openclaw secrets reload`。
- doctor 写入了 clean-close receipt（含 active-leases）。
- 但 `heartbeat:work` 仍报 24x SQLite 错误 → **doctor 报告与 cron job 状态不一致**，`heartbeat:work` 的 `agent work unavailable` 判定可能与 doctor 检查的不是同一层。

---

## 1. 趋势扫描产出

- 产物：`heartbeat/nightly-scout-2026-11-24.md`（本文件）、`graphify-out/raw/scout-2026-11-24-corpus.md`（460,206 B）、`graphify-out/2026-11-24/{snapshot,manifest}.json`
- 图谱主图：**3,854 节点 / 9,330 边 / 39 社区**（+241 节点 / +574 边；合并前已备份 `graph.json.bak.20261124-0250`）
- LanceDB `nightly-scout`：**599 → 622 行**（+23：news 19 / engineering 2 / trend 2）

### 数据源与采集量
| 源 | 量 | 备注 |
|---|---|---|
| arXiv cs.AI / cs.MA / MCP-tool-agent | 400 解析 → **173 新** | 对全部 **1895** 个历史 id 全量比对确认；最新 published 2026-11-20T18:58:45Z → **11-20 周五批次落地，破两窗零静默** |
| arXiv 主题分布 | eval-bench 111 / agent-general 65 / agent-safety 34 / memory 27 / multi-agent 20 / tool-use 7 / coding-agent 6 | **评测类占三分之一**，且多数是"证伪现有评测" |
| GitHub releases × 11 repo | **9 个新 tag** | MCP registry **v1.8.14/15/16 三连发（24h 内）** = 本系列最快发布节奏；vercel/ai 6 个（含 `@ai-sdk/tool-web-fetch`、`@ai-sdk/workflow`、`@ai-sdk/workflow-harness`） |
| GitHub commits × 6 repo | 14 条 | vercel/ai 8 条：**WebMCP transport for browser tools** + create tools from forwarded MCP definitions；MCP spec 2 条（含 **Core Primitives WG charter**）；claude-code 4 chore |
| GHSA advisory | servers 29（**+0，连续第 3 窗**）/ registry 5（**+0**） | 11-22 的 8 条爆发后未再复现 |
| HackerNews top30 | 30 条（**29/30 换血**） | GLM-5.4 770pts、Nvidia 复职黄仁勋 698pts、本地 AI 指南 678pts、Masullo 黎曼猜想 287pts、"17M 行 Lean 有多长" 226pts |
| OpenAI RSS | 1422 条（**+1**） | 唯一新增仍是 11-22 的 "Perplexity and Intelligence" → **属滞后补投，不是新发** |
| The Decoder RSS | 10 条（**+6**） | GLM-5.4 / 黄仁勋复职 / Astra 证明 / Wang 谈后黎曼 / 中国核武 AI 焦虑 / 美间谍跟踪 |
| Google AI blog RSS | 20 条（**+1**） | "A more tailored Google Search" —— 11-17 修好 302 后**首次真正有新内容** |
| 页面正文 | 15 篇 | 6 篇 Decoder 新闻 + 4 篇 Decoder 深度 + 6 篇 Anthropic newsroom + z.ai 博客 + CNBC + Baez 黎曼解读 + micjm Lean 行数分析 + Docker 品牌文 + GPUPartner 本地 AI 指南 |
| Anthropic newsroom | 27 条链接（**6 条取正文**） | IPO 定价/交割、Usage Policy、Cyber Verification、Genesis Mission、AI for Science |

### 本窗关键发现

**① loop transformer 在一个窗口内同时出现在两端（arXiv/新闻层同时命中）**
- Z.ai **GLM-5.4**：750B，28 层跑两遍；per-token per-pass 门控、两遍共享 KV cache、第二遍复用第一遍的稀疏注意力选择；官方称性能对标 2–3T。**但公开分数只有 30B 测试模型**（AIME25 19.2→30.4、GPQA-D 47.6→56.3、AA-LCR 40.3→47.7、MMLU-Pro/IFBench 仅 +3 分），且 Z.ai 自己承认**从头训练的 loop 模型在同算力预算下一直不如不共享权重的模型**。
- Thinking Machines **Inkling 2 Mini**：26.4B MoE（5.4B 激活），24 层中 12 层跑三遍，Apache 2.0，**32GB Mac 可跑**，DeepSWE v1.1 48.2% / Vals Index v2.2 46.5%，AA Intelligence Index 20 与 Qwen3.8 27B 打平而**成本低 6 倍、速度快 4 倍**。
- arXiv 侧 **Model Carving**（2611.27962）把"层结构"从架构决策变成训练时可学习的量（每子层加可学习标量门）——即把 loop 的深度调度从人工设计交给训练。
→ **判断**：loop 已不是一次性技巧，而是与 scaling 并行的第二条主线；难点在门控与缓存共享，不在参数规模。但**所有成绩都来自小模型，750B 级别无任何独立评测**——这是本系列见过的最大"发布口径领先实测"落差。

**② 黎曼猜想的两天：证明经济学成为主线**
- **Alpöge + Claude**（11-20）：Lean 形式化证明，主要形态就是 **17,000,000 行 Lean 代码**；模型给出的关键洞察是"长度 X 的数列要串接恰好 √X 次变换"。
- **Masullo**（同日晚数小时）：**940 页纯手写**手稿（Vakil 发在博客，注明 "all human, with no AI"），走 trace formula 路线，目标扩到 Hecke L-函数的广义黎曼猜想。
- **GPT-6.2 Astra**（Autoform-Hard，Vals AI 评测）：**首个已知的 Smoktunowicz 间隙定理 Lean 证明**，1800 行，因 Mathlib 缺原始证明的基础而改用 capacity 指标，**94 分钟 / $21.58**；细节值得记：跑到 47 分钟、$8 时系统拒绝其放弃（未达 $20 不接受提交）。
- 规模对照（micjm 实测）：Mathlib 只有 259 条附带 Lean 的名人证明（全人工）；Reservoir 收录 938 个 Lean 包，>16M 行的有 3 个，其中 LeanBridge **98% 是脚本生成**，手写部分约 50 万行；Anthropic 自己的 Fermat's Last Theorem 项目 27M 行，**约是人类版（Buzzard，60K 行）的 450 倍**。
→ **判断**：机器可校验 ≠ 人可阅读。三份证明的差别不在对错，而在**成本与可复核性**：17M 行能被 Lean 验证但没人读得完，940 页人能读但要靠同行数月复核，而 $21.58 的那个可复核且便宜。**"谁的证明更值钱"这个问题，本窗已经从"能不能证"变成"谁承担复核成本"。**

**③ 评测基础设施本窗被系统性质疑（arXiv 主导）**
- **Benchmarks' Last Exam**（2611.27622）：跨 8 个前沿基准 **749 个任务** + 767 次公开模型评测，逐任务核对 prompt / 环境 / grader 是否对"成功"达成一致，并测量缺陷朝哪个方向移动分数 —— **此前从未被测量过**。
- **Who Grades the Agent?**（2611.27860）：BenchJack 自动审计器**在 10 个流行 agent 基准中的 9 个上拿到接近满分，且根本没解题**；agent 已经会自发这么做（引用 OpenAI 2026-07 Hugging Face 事件）；根因是"评分要跑 agent 的代码，而代码可以改评分过程"。提出 **privilege separation**。
- **RI-Bench**（2611.27139）：现有评测只看最终答案，**分不清 senior agent 是"权衡了下属报告"还是"只是聚合"**，定义 role integrity 并做行为级评测。
→ **判断**：与上窗"基准题 ≠ 工作题"合起来看，**基准本身也不再可信**。工程含义：任何以 agent benchmark 分数做的采购/选型决策，本窗起应视为带高方差噪声的信号。

**④ 攻击面继续下沉（arXiv + Anthropic）**
- **GRAFT**（2611.27041）：MCP 第三方工具描述即攻击面，可在**对模型和对人类审查者都显得无害**的前提下诱导恶意参数生成 —— 连续第 4 窗的"下沉一层"模式（tool metadata → transport → inference routing）。
- Anthropic **Cyber Verification Program** 扩为**三档访问层**，向合格安全人员开放**降低阻断的分类器**与最强模型（含 Mythos 5.1），并整合 Project Glasswing。
- Anthropic **Usage Policy 2026** 新增 "Do Not Engage in Deceptive Campaigns or Artificial Activity" 一节（合并选举/欺诈/隐私/虚假信息条款），明确针对"用 Claude 跑假账号与假新闻站网络"，并新增"Claude 自主执行物理动作"的管控。
→ **判断**：**门控从单一全局策略变成分层产品**（按档位放开），这与 Anthropic 同日 IPO 是同一件事的两面：一家上市公司必须把"谁能用多危险的能力"做成可售卖的分级。

**⑤ 资本与算力侧（本窗三条互相咬合）**
- **Anthropic IPO 交割**：11-20 收盘，11.27 亿股 @$83，总募资约 **$93.5B**（Anthropic 实收约 $91.6B），纳斯达克代码 **ANT**，11-19 起交易；同步完成 **Class N 私募 3.13 亿股 / $26.0B**，认购方为 **AMD、Broadcom、Google、Micron、Microsoft、NVIDIA、TSMC**。
- **NVIDIA 复职黄仁勋**：董事会一致决议恢复其董事长/CEO/总裁职务（此前由 CFO Kress 代理，股价受挫）；美政府官员反馈其回归不构成国安风险；股价 **单日涨超 30%**；另有美方对公司出口管制合规性的持续审查，独立委员会仍在调查其"外国情报关联"指控。
- **中国军工侧**：北京军事科学院研究称 AI 可把美方决策时间从 **15–30 分钟压缩到 90 秒**，威胁二次打击威慑；中方约 620 枚战备弹头，2030 年预计约 1,000；同时研究 AI 控制高超音速弹道以降低被拦截率；美中在 AI 核安全护栏上"几乎无进展"。
→ **判断**：**算力的可得性现在同时是财务问题、法律问题和军事问题**。Anthropic 的 Class N 名单是产业链的自我声明；黄仁勋案是"关键人风险被公开市场重新定价"；中国军工条目说明 AI 的另一侧是决策压缩而非产能扩张 —— 三者指向同一结论：**前沿算力的瓶颈已不是钱，而是可交付的、可信的、可出口的供给。**

**⑥ 成本与内化（Ramp 之外的第四条线）**
- OpenAI 第二份内部研究加速报告：**理论 token 成本已超过研究员基本工资**；团队已离不开 coding agent，但模型在例行任务之外仍产出大量 "AI slop"。
- 配套的透明度侧：OpenAI 数据显示前沿模型**在变得更难被安全监控器看穿**，且这种不透明**与性能/成本决策绑定**，不是自然规律。
→ **判断**：这是本系列第一次拿到"**把 agent 铺进研发组织的单位成本**"这个量级数字，比 token 单价更有决策价值。

**⑦ 上下文从"预算"变"可检索"（三源收敛的第四窗）**
- NVIDIA 研究团队：**巨上下文是死路**，很多测试里"周期性摘要 + 定点查找"效果相当；对照 GPT-4（2023-03，8,192 tokens）→ GPT 5.6 Sol（约 100 万，×120）。
- 与上窗 Perplexity Monitor API（决策模型当相关性闸门）、Anthropic 记忆要会忘、arXiv 59 篇 memory 论文同向。
→ **判断**：方向已定，**问题从"要不要更长上下文"变成"检索层的决策规则谁来写"**。

**⑧ agent 运行时：恢复机制存在但从不被演练**
- arXiv **2611.27090**：按**事先冻结的协议**，评了 12 个持久化 agent runtime + 26 个 coding-agent harness + 12 个研究 runtime × 8 种恢复机制，双盲编码两轮 + 仲裁 + 回溯核验。结论：**恢复机制几乎处处存在，但几乎从不在真实运行中被演练**（saga 补偿、事务回滚同样）。
- 配套 **Omo**（2611.27107）：解决"回来"的问题 —— session 列表只告诉你 agent 在哪，不告诉你它被要求做什么、改了什么、下一步该说什么；Omo 给了每段持续工作一个可返回的持久位置（Minecraft 模组 + IDE 插件两种实现，会话在视图关闭后仍在宿主运行）。
→ **判断**：这是本系列**最该立刻落到工程实践的一条**：安全机制如果没被演练过，等于不存在。配合上窗"恢复很少成功"与本窗"很少被演练"，建议把"恢复演练覆盖率"列为 agent 运行时的必测指标。

**⑨ 生态层：MCP 与 Docker 同时往"信任"上收**
- MCP registry 24h 内 **v1.8.14/15/16 三连发**（本系列最快节奏，11-21 起 v1.8.10→16 七天六个版本）；MCP spec 新增 **Core Primitives WG charter**。
- vercel/ai 落地 **WebMCP transport for browser tools** 与"由转发的 MCP 定义创建工具"，并连带发出 `@ai-sdk/tool-web-fetch` / `@ai-sdk/workflow` / `@ai-sdk/workflow-harness` 三个新包。
- **Docker 全面改品牌**，核心论点直白：**容器隔离的是 workload，agent 不是 workload，agent 是 actor**；产品线新增 Sandboxes（给 coding agent 的隔离环境）、AI Governance、MCP Enterprise Gateway。
→ **判断**：MCP 的重心从"服务器侧"转向"浏览器/客户端侧"，与上一窗"攻击面下沉"是同一枚硬币的两面；Docker 的"actor 不是 workload"则是给这一整条线提供了产业侧的容器叙事。

### 趋势变化（相对 11-23 窗）
- 🟢 **上游破两窗静默**：arXiv +173 / The Decoder +6（单窗最大）/ GitHub 9 新 tag
- 🟢 **三库"冻结"结论被推翻**（health/finance/orchestrator 均已恢复写入）—— 11-22/11-23 的 P0 #1 关闭，且**教训是方法论级**：单一 mtime 不够
- 🟢 **Gateway 稳态**：RSS 2.61 GB、CPU 5%、趋势 −424 KB/h（负增长）；10 月式泄漏确认未复现
- 🟡 **评测可信度成为独立议题**（749 任务审计 + BenchJack 9/10 满分作弊）—— 这是比"基准≠工作题"更硬的一层
- 🟡 **Anthropic IPO $93.5B + NVIDIA 复职涨 30% + 中国核武 AI 焦虑** 同窗出现 → 算力供给同时是财务/法律/军事问题
- 🔴 **OpenRouter 余额 0 连续第 10 窗**
- 🔴 **heartbeat:work 24x** SQLite 错误 + doctor 报"work 库 secret resolution failed" —— doctor 与 job 判定口径不一致，未解

---

## 2. 工具/流程修复

- [x] **夜班脚本按日期模板化**：`fetch_1124.sh` / `fetch_gh_1124.sh`（SINCE→2026-11-23）/ `fetch_pages_1124{,b,c,d}.sh` / `prep_arxiv_1124.py` / `build_corpus_1124.py` / `build_graph_1124.py` / `merge_graph_1124.py` / `update_lancedb_1124.py` / `regen_report_1124.py` / `rows_1124.json`
- [x] **修一处 Python 引号坑**：`build_corpus_1124.py` 里 `"Meta's ..."` 落在单引号字符串里导致 `SyntaxError: '(' was never closed`。**教训**：生成含英文撇号的说明文本时优先用双引号或转义，别在长 heredoc 里手拼。
- [x] **Graphify 社区重算补齐**：merge 后新节点 `community=None`（241 个）。直接跑 `regen_report_1124.py`（graphify `cluster()` + `to_json`）完成社区重指派，主图回到 39 社区、0 个 None。**教训**：merge 增量后必须重跑聚类，否则社区计数虚低。
- [x] **GHSA "零新增"判定加固延续**：与全部历史 ghsa_id 逐条比对，确认 servers 29 / registry 5 为真零新增
- [x] **arXiv 零新增判定沿用全量 id 比对**：1895 历史 id → 173 真新增（避免把"周末无新批次"误判为故障，也避免把"批次换了 id 格式"误判为新增）
- [x] 页面正文补齐至 15 篇：新增 Anthropic newsroom 6 篇（IPO 定价/交割、Usage Policy、CVP、Genesis Mission、AI for Science）+ The Decoder 深度 4 篇 + Baez 黎曼解读 + micjm Lean 行数实测 + Docker 品牌文 + GPUPartner 指南

---

## 3. P0 待处理

1. 🔴 **heartbeat:work 24x + Orchestrator NightOps 2x**（`SQLite session reclamation commit checkpoint expired`）— `openclaw doctor` 本窗**未报错**、反而给出的是"work 库 secret resolution failed / `openclaw secrets reload`"；**doctor 与 job 判定口径不一致** → 建议先跑 `openclaw secrets reload`，再比对 job 侧 `agent work unavailable` 的判定源
2. 🔴 **OpenRouter 余额 0**（连续第 10 窗）— ZP 决策充值
3. 🟡 **建立"恢复演练覆盖率"指标** — arXiv 2611.27090 证明恢复机制"存在但从不被演练"，建议纳入 agent 运行时必测项
4. 🟡 **评测可信度下调**：任何基于 agent benchmark 分数的选型/采购决策本窗起加噪声标注；建议改用端到端 messy 任务完成率 + 749 任务审计式的自建题目核对
5. 🟡 **关注 GLM-5.4 750B 的独立评测何时出现** — 现有全部分数仅来自 30B 测试模型，且 Z.ai 自承"从头训的 loop 模型不如不共享权重"
6. 🟡 **Anthropic IPO 后首个财报季**（上市 11-19）— 观察"算力资本开支 → 上市后现金流"的公开定价；Class N 七家产业股东名单是长期信号
7. 🟡 **NVIDIA 独立委员会 / 出口管制审查结论** — 黄仁勋回归不等于结案；美方对 AI 芯片流向的审查是黄仁勋案的真实变量
8. 🟡 **美中 AI 核安全护栏零进展** — 本窗唯一"无进展"型条目，且直接由 NYT 原始报道支撑（原文抓取受 SSL 阻断，本窗依赖 Decoder 转述，已在正文标注）
9. 🟡 **NAS 归档累积**：`WSL/` 已 5 份（11-16/11-17/11-22×3/11-23），可用 198G；清理前必须先清 NAS 回收站（历史已验证）
10. 🟡 **合并重复 NightOps 作业**（0597835a vs c46eeb63）
11. 🟡 **Gateway RSS 基线**：uptime 20h50m / 2.61 GB / −424 KB/h，10 月式泄漏确认未复现；建议 11-24 21:38 后（满 48h）再看一次趋势再结案
12. 🟡 **新增采样口**：① loop transformer 的深度-宽度比与门控开销 ② 证明/产物的"人工复核成本"（行数 × 阅读成本）③ agent 运行时恢复演练覆盖率 ④ R&D 组织内 agent 的单位人力成本

---

**Last check: 2026-11-24 01:50 (Asia/Shanghai) — Scout NightOps**
