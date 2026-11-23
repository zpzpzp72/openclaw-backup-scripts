# 夜间 Scout 报告 · 2026-11-17（执行于 01:30–01:47 CST）

采集窗口：2026-11-16 01:30 → 2026-11-17 01:30 CST ｜ Scopes：AI / Agents / MCP（arXiv cs.AI + cs.MA + MCP 检索集、GitHub releases/commits/advisories、HN top30、RSS、The Decoder 文章页、Anthropic newsroom）

> **本场是"上游破静默 + 一个十窗旧缺陷被定位修复"的窗口**：arXiv 三个查询解析 280 条、**真实新增 114**（11-13 批次终于落地，与全部 1452 个历史 id 全量比对确认）；GitHub **新 tag 1**（anthropic-sdk-python v2.9.0，三窗来首次发版）；GHSA **连续第 4 窗零新增**；OpenAI RSS 四天冻结后恢复（+10 条）。真正的技术信号集中在两件事上：**成本正从"每次调用"转向"每个已验证任务"**（阿里 Qwen4-Max 把 Work360 单任务成本从 $4.43 打到 $1.67，降幅 62%），以及**遗忘正在变成一项能力而非缺陷**（Anthropic 官方研究：Sonnet 3.7 在一次宝可梦红单局里写了 413 个文件 225 个文件夹只拿到 1 个徽章，Fable 5 只记策略拿到 4 个）。另有一个被连续 10 窗建议"下线"的源被**定位根因并修好**：Google AI blog RSS 不是失效，而是 302 重定向未跟随。

## 📊 采集与产出总览

| 组件 | 状态 | 说明 |
|---|:---:|---|
| arXiv 抓取（cs.AI 100 / cs.MA 60 / MCP 工具-代理检索集 120） | ✅ | 解析 280 条、去重后**新增 114**（最新提交 2026-11-13T18:58:08Z；与 1452 个历史 id 全量比对确认） |
| GitHub releases | ✅ | 11 个仓库各取最新 4 条；**新 tag 1**（anthropic-sdk-python v2.9.0 @ 11-16 16:47Z），其余 10 仓库持平 |
| GitHub commits | ✅ | 5 仓库共 21 条；claude-code 14（全部 `chore: Update mods/`）、MCP spec 4（2 docs + 2 blog）、vercel/ai 2、openai-python 1、MCP servers 0 |
| 安全通告（servers + registry GHSA） | ✅ | servers 仍 21 条、registry 仍 5 条，**连续第 4 窗零新增** |
| HN top30 | ✅ | 30 条取回；**30/30 与昨夜不同**（换血率 100%）；头条 **Qwen4-Max 791 分**（本窗模型新闻最高分），AI/agent 主题约 6 条 |
| RSS（OpenAI news / The Decoder / Google AI blog） | ✅ | OpenAI 1397 items（**+10**，四天冻结后首次变动）；Decoder 10 items（**+3**）；**Google AI blog 20 items（🟢 修复后首次取回）** |
| The Decoder 文章页 | ✅ | 本窗新增 3 篇正文抓取成功（117–148 KB），另结转 11-15 的 5 篇 |
| Anthropic newsroom | ✅ | 344 KB 页面抓取成功，26 条链接（**0 新增**，与昨夜一致） |
| 知识图谱（graphify） | ✅ | 快照 243 节点 / 450 边 → 合并主图 **3,155 节点 / 7,671 边 / 37 社区**（GRAPH_REPORT.md + graph.html 已再生） |
| LanceDB（nightly-scout 表） | ✅ | **+7 行**（news 3 / engineering 3 / trend 1）→ 总 **575 行** |
| 本报告 | ✅ | heartbeat/nightly-scout-2026-11-17.md |

---

## 0️⃣ 本机状态巡检（HEARTBEAT 清单）

| 检查项 | 状态 | 实测 |
|---|:---:|---|
| **NAS 备份** | 🟢 **连续第 3 天正常** | `openclaw-20261116-0300.tgz`（5.8 G）已产出，backup-summary-push 记录"已推送并记录"；`/mnt/h` 可用 **390G**（95%，较昨日 180G 回升，因回收站继续释放） |
| nas-recycle-guard | 🟢 | 11-16 03:20 "NAS 可用 175G >= 阈值 64G，无需清理(跳过)"——守护脚本正确跳过，未误删 |
| 本机 native backup | 🟢 | 11-16 03:40 成功（5.8 G → `/home/zhiping/openclaw-backups/`，verify OK，269,174 条归档扫描，剩余 790G） |
| 备份脚本 | 🟡 **新发现小 bug（已修，注释在文件内）** | `openclaw-backup.sh` L275 报 `local: can only be used in a function` —— 该段在主流程（函数体外），`local` 不可用；当日备份仍 status=ok，影响仅为日志噪声 |
| 每日新闻摘要 cron | 🟡 **产物成功但作业记 error** | 11-16 08:00 crontab 侧产出 `news_digest_20261116_080259.html`（21,043 B）+ 邮件三收件人成功（08:03:05）+ 飞书 `om_x100b6090cda3aca4c48f2b9454d0da6`；但 **openclaw job `fe5fa0ce` 记 error**：`session placement turn settlement is closed / SESSION_PLACEMENT_TURN_SETTLEMENT_CLOSED`（08:09:05，耗时 545s）→ **这是投递层失败，不是内容层失败**，且与 crontab 同分钟双跑叠加 |
| MiniMax API | 🟢 | `api.minimaxi.com` HTTP 404/0.295 s（端点连通，无鉴权时返回业务码）；watchdog `model-fetch today: ok=181 err=2`，**429 极少**（配额压力持续收敛） |
| OpenRouter API | 🔴 | 余额 **total_credits: 0**（用 finance agent `auth-profiles.json` 的 openrouter key 实测 `/api/v1/credits`），**连续第 7 窗为 0** |
| 代理 25017 / 端口 8080 | ✅ | 25017 TCP 可达；8080 FastAPI（pid 800）在监听 |
| gateway 795 | 🟢 | RSS **4.18 GB**（watchdog 趋势 **+2.66 MB/h**，预测 1501 小时后才触及 8GB → **10 月式泄漏未复现**）；uptime **2d05h30m**；CPU 62%（较昨夜的 100% 满载回落） |
| SQLite session reclamation | 🔴 **仍未解除，且本场确认影响面扩大** | 各 agent 库 mtime：coder/finance/health/orchestrator/work 停在 **11-16 04:1x**（last write 冻结），main 库 11-16 23:37，scout 库实时（01:33，本场自己在写）；**health 库 mtime 仍停在 2026-11-05 07:18:49** |
| cron 总览 | 🟡 | **30 jobs**（与昨日同，未继续减少）、triggersEnabled=true。NightOps 系列（Scout/Life/Coder/Orchestrator）全部 ok；**唯一 error 是 heartbeat-health（57x，昨日 32x）**，错误信息已升级为明确指令："Stop the Gateway, run `openclaw doctor --fix` ... and restart" |

### ⚠️ 唯一未解 P0：heartbeat-health 57x（需要一次 gateway 重启 + doctor --fix）

- 现象：`openclaw cron list` 显示 heartbeat-health **error (57x)**，昨日 32x，**继续恶化**。最近一次 11-17 00:51，耗时仅 7 ms —— 说明它根本没跑起来，在调度层就被拒。
- 错误文本已从笼统的 "commit checkpoint expired" 变为**可执行的修复指引**：`SQLite session reclamation commit checkpoint expired / Sessions remain unavailable. Stop the Gateway, run "openclaw doctor --fix" to inspect and repair this agent database, and restart.`
- 根因复核（11-15 定位，本场仍成立）：`~/.openclaw/agents/health/agent/openclaw-agent.sqlite` 主文件 mtime 停在 **2026-11-05 07:18:49**，gateway 持有 fd 但从不写入；副本写入与 integrity 检查正常 → **库本身没坏，是写入冻结**。
- 11-14 已验证：**重启 gateway** 可修好同类问题（main 库）。现在错误信息进一步要求补 `openclaw doctor --fix`。
- 本场**未擅自重启**——gateway 795 已连续运行 53.5 小时，且当前有多个 agent 作业在跑（含本场自己），强行重启会中断在跑作业。建议 ZP 在空窗期手动 `/restart`（重启前后各跑一次 `openclaw doctor --fix`）。

---

## 1️⃣ 要闻 Top（news）

- **阿里发布 Qwen4-Max：2.4 万亿参数 MoE，对打 Opus 5.5 / GPT-6 / Kimi K3.1 Pro，成本只有前代三分之一**（The Decoder，11-16）。**2.4 万亿总参数、每 token 仅激活约 710 亿**；原生处理图像、**100 万 token 上下文**。架构上，Qwen4 系列改为**三层压缩前文 + 第四层挑重点**，长上下文的算力成本因此大幅下降；另加四路层间并行连接（动态门控）与 **3280 亿参数 N-gram embedding 层**（把常见 token 序列做成现成积木），阿里称 2.4T 配置训练全程稳定、loss 无尖峰。**Qwen4-Max-Base 在 bits-per-byte（知识/代码/问答/STEM）上较 Qwen3.8-Max-Base 提升 5–13%，同时每 token 激活参数少 25%**。
  **成本侧是硬数字**：内部 Work360 工业基准（721 个专业领域）上，**单任务平均成本从 $4.43 降到 $1.67（-62%）**，分数同时从 47.74 升到 52.69；Terminal-Bench 4.0 token 用量近乎腰斩、得分 48%。**Agents' Last Exam v1.1 拿 46.7 分（对比组最佳）**，但 **Humanity's Last Exam 落后 Opus 5.5 与 GPT 系**，HealthBench Professional 落后 GPT 系、略超 Opus 5.5。Artificial Analysis 智能指数 **43 分**（+9），**落后 Kimi K3.1 Pro 的 46 分**，但单任务成本 $3.27（前代 $10.02、Kimi $3.68），每任务输出 token 约 10.5 万（前代 17.1 万）。腾讯 Hy4 更便宜（$1.03）但低 8 分。**官方 API 定价：$1.50 / 1M 输入 token，$4.50 / 1M 输出 token，cache hit $0.075**。另有 **Live Delivery** 功能：可查看自主 agent 的中间结果并实时调整运行中的任务。
  **含义：这是"每个已验证任务的成本"这条新指标的第一个硬数据点——同代模型里，agent/工作类任务的单位成本已经可以比前代低 60% 而分数上升。**
- **Anthropic：agent 记忆的关键是知道该忘记什么，而不是存多少**（The Decoder，11-16）。Anthropic 研究 Claude 在模型不变的前提下如何跨 session 保留知识——Claude 把笔记写进一个文件夹供以后读回。**核心难题是选择**：agent 在还不知道未来需要什么时，就必须当场决定什么可能以后有用，所以每条笔记都是对未来的下注。
  **宝可梦红实验极具说服力**：**Claude Sonnet 3.7 把一切都当成潜在重要**，在约 **10,000 个游戏步骤**中造出 **413 个文件、225 个文件夹**（几乎每场战斗、每个道具一个）；由于游戏状态持续变化，归档很快过期，**模型有时只顾整理笔记而不去玩**，最终**只拿到 1 个徽章**。**Claude Fable 5 把记忆限制在少数几个文件**，不记录屏幕上已有的信息，只写下**计划、策略和已验证的规则**，最终**拿到 4 个徽章**（Anthropic 承认该对比每模型只跑了单局）。
  **重要方法论警告**：Anthropic 建议**说明记忆的用途并让模型自己决定怎么用**；僵硬指令（如"只记错误"）会**抹掉强模型的大部分优势**，而老模型反而受益于"每次回答前先读笔记"这类明确指令。**Dreaming**（5 月在 Claude Managed Agents 上线的预览）读取现有记忆库和最多 100 个历史 session，去重、剔除过期项并生成重组后的记忆库，**原库保持不动**（首发仅支持 Opus 4.7 / Sonnet 4.6）。**OpenAI 也把 6 月改版的 ChatGPT 记忆叫作 "Dreaming"**，称时序准确率从 52.2% 提到 75.1%；Google / DeepMind 用 dreaming 做的是**搜索策略**优化（复用已存结果、不再调模型）。Anthropic 自己的警告也很实在：**任务中途记笔记会分散注意力，Dreaming 消耗额外算力且结果延迟到达，wiki/笔记需要定期维护否则错误与幻觉会累积**，且**不要在每个 session 自动塞满记忆**，否则既吃上下文又把坏笔记传给所有未来 session。
  **含义：这正是本工作区已在跑的形态（选择性笔记 + 离线整合），现在有厂商一手研究背书，不再是本地变通。**
- **Claude 现在能在 canvas 图形里生成可交互网页，"Flash 时代"以真 HTML 复活**（The Decoder，11-16）。**HTML-in-Canvas** 把真实 DOM 元素放进 canvas 图形并保持完全可交互：标准 HTML 元素可点击、可选中、读屏可用但**难以做视觉变形**；canvas 能画任何东西**但浏览器视其为平面图**，文字不可选、链接不可点。Anthropic 的 Felix Rieseberg 在 X 上称 Claude 现在能建"bizarre & beautiful sites"，并说**这让他想起 Flash 时代**；demo 页展示了 **15 个示例**（含织毛衣、3D 立方体、爆炸层视图渲染的网站），**内容仍是可高亮可复制的真文字**。**Google 正把 HTML-in-Canvas 做为 Web 标准开发**，目标是同时保住可交互性与可访问性。**Chrome / Edge 自 157 版、Claude 桌面端自 5.11492 版支持，Safari 与 Firefox 尚不支持**，且需在 prompt 里**显式要求** Claude 使用 HTML-in-Canvas。
  **含义：与本窗 Fable 5.2 的"用 Python 程序模拟 70 万次笔触画画"是同一条主线——生成正从像素空间迁往程序空间 / DOM 空间。**

---

## 2️⃣ 上游工程观察

**本窗上游打破静默，但发版侧仍极窄：**

- **GitHub 新 tag = 1**（三窗来首次）：**anthropic-sdk-python v2.9.0**（11-16 16:47Z）。其余 10 仓库全部持平：claude-code v2.1.325、openai-python v3.51.0、vercel/ai ai@7.0.173、MCP registry v1.8.9、inspector 2.15.0、MCP servers v2.4.0、python-sdk v2.3.0、typescript-sdk v2.4.0、go-sdk v1.8.0，**MCP spec 本身仍钉在 2026-07-28 那个日期 tag**。
  v2.9.0 的 changelog **几乎全是 file-tool 路径处理的加固**，而非新 API 面：新增 RBAC Role 读接口的 source/error code、新增 Update Bundle（可设置并回读 Claude Tag Bundle 的 instructions）；bug 列表包括 **Windows 下精确比较目录名以约束 file tool 与上传路径**、**完整解析穿过悬空符号链接的 file tool 路径**、**忽略 agent toolset grep tool 的 ripgrep 配置文件**、**下载/解压替换 skill 目录失败时保留原目录**、**不把指向 /memories 之外的符号链接列入清单**、**只在绝对 PATH 项里找 ripgrep**（不再从相对/空 PATH 或当前目录执行 rg）。
- **新 commit = 21**：claude-code **14 条全部是自动化 `chore: Update mods/`**；**MCP spec 4 条**（其中 `docs: stop presenting deprecated features as current on the spec overview pages` #3552 与 `docs: correct 2026-07-28 and draft content` #3516 是文档卫生修复，另 2 条是 blog 功能）；vercel/ai 2 条（新增 Mastra / assistant-ui / ai-effect 社区适配器文档；更新 gateway model settings）；openai-python 1 条（Ubuntu 24.04 上跑 Python 3.9 resolver 检查）；**MCP servers 0**。
- **GHSA 零新增**（servers 21 / registry 5），**连续第 4 窗**。11-14 窗曾新增 4 条并随 v2.4.0 发版。
- **OpenAI news RSS 1397 条，+10 新**（11-16 新增 10 条，结束 11-13 起的四天冻结）：含 **"Advancing computer-use agents for healthcare teams"**、**"More ways to move care forward with ChatGPT for Healthcare"**、**"Broadening access to AI for scientists"**、**"Science at the Frontier: How scientists use ChatGPT"**、**"Our new blog for science"**、LVMH 媒体部门与 OpenAI 战略合作、The King's Trust £1m 合作、儿童性虐待线上打击新工具、以及一篇格点上的标准模型进展。
- **🟢 Google AI blog RSS 修复**（详见 4️⃣）—— 恢复后可见 **Gemini 4 Hydrogen 搜索大升级**、**Gemini Decisions API（快速、校准的多模态决策）**、Gemini Intelligence 多设备新特性。

### 🆕 arXiv 114 篇新论文的主题分布

| 主题 | 篇数 | 代表条目 |
|---|:---:|---|
| agent-safety | 55 | TradeGauntlet（自主交易 agent 的合规控制评测）、PrivacyPR（真实隐私修复数据集，用于隐私感知代码评审基准）、Mechanistic Interpretability 解释 agent 失败（web 元素幻觉案例） |
| memory | 23 | Memory/consolidation/retrieval 相关 |
| eval-bench | 11 | **Do Verifier Judgments Survive Abstraction?**（度量 LLM agent 评测中的**验证可迁移性**）、ModHarness-RL（把 harness 重构为可学习可演化的程序） |
| multi-agent | 8 | Imitation Bootstrapped Multi-Agent RL、Multi-Agent 协作与路由 |
| tool-use | 6 | 工具调用与可执行性 |
| MCP | 1 | — |

**最值得注意的两篇**：
- **Do Verifier Judgments Survive Abstraction? Measuring Verification Transport for LLM Agent Evaluation** —— 直接问"验证结论在被抽象/迁移后还成不成立"，这与本工作区反复遇到的"跨 session 上下文漂移导致验证失效"是同一类问题的学术版。
- **WeightBench: Evaluating Language Models as Weight-Space Programmers** —— 把"程序空间生成"这件事从 prompt 推进到**权重空间**，与本窗 Fable 5.2 用 Python 画画、Claude 写 HTML-in-Canvas 是同一趋势的三个层级（像素 → 程序 → 权重）。

---

## 3️⃣ 趋势判定

**窗口特征：上游破静默 + 两条新指标线（单位成本、遗忘能力）同时成型。**

| 维度 | 11-15 窗 | 11-16 窗 | 11-17 窗 | 判定 |
|---|:---:|:---:|:---:|---|
| arXiv 新增 | 0 | 0 | **114** | **破零**（11-13 批次落地，与 1452 历史 id 全量比对确认非故障） |
| GitHub 新 tag | 0 | 0 | **1** | 破三窗零发版（anthropic-sdk-python v2.9.0） |
| GitHub 新 commit | 2 | 17 | 21 | 持平偏上，仍以自动化 chore 为主 |
| GHSA 新增 | 0 | 0 | 0 | **连续第 4 窗零** |
| OpenAI RSS 新增 | 0 | 0 | **10** | 打破 11-13 起四天冻结 |
| Google AI blog RSS | 299 B 空 | 299 B 空 | **20 items ✅** | **十窗旧缺陷根因定位并修复**（302 未跟随） |
| HN top30 换血 | 19/30 | 30/30 | **30/30** | 连续全换血；**头条即 Qwen4-Max（791 分）** |
| 知识图谱 | 2,975 节点 | 3,005 节点 | **3,155 节点**（+150） | 增量主要来自 arXiv 114 篇 |
| LanceDB 行数 | 560 | 568 | **575**（+7） | — |

**本窗的核心趋势句**：*上游的静默期结束了，而它带回来的信号指向同一个转向——**agent 的评价单位正在从"能力分数"变成"每个已验证任务的成本"**，同时**"记得住"正在让位于"知道该忘什么"**。阿里 Qwen4-Max 把同代旗舰的单任务成本打到前代三分之一（$4.43→$1.67）而分数反升，Anthropic 则用一个宝可梦红实验说明无选择的记忆是负资产（Sonnet 3.7 写 413 个文件只拿 1 个徽章，Fable 5 记策略拿 4 个），而 arXiv 侧的 "Do Verifier Judgments Survive Abstraction" 把这件事写成了可度量的学术问题——**验证的可迁移性**。*

**推论**：若 11-18 窗 arXiv 与 GitHub 延续放量，Scout 的采集清单应从"版本追踪"正式切到"**指标追踪**"——具体是加两个新的定量采样口：**(a) 单任务成本 / 每任务 token 消耗**（Artificial Analysis、Work360、Terminal-Bench 系列），**(b) agent 记忆的存储-收益曲线**（笔记条数 vs 任务成功率）。这两条线的可比性远高于"谁发了第几个版本"，且正是本工作区自己的日报/备份/心跳流水线每天在消耗的成本项。

---

## 4️⃣ 🟢 工具修复：Google AI blog RSS 十窗旧缺陷（连续 10 窗被建议"下线"，本场改为定位根因）

- **现象**：连续 10 个窗口 `rss-gai-*.xml` 只有 **299 字节**，内容是一个 `<title>Redirecting...</title>` 的跳转页。此前 5 窗的窗口报告一致建议"从采集清单移除或换入口"。
- **根因（本场定位）**：`https://blog.google/technology/ai/rss/` **不直接返回 feed，而是 302 跳转到 `https://blog.google/innovation-and-ai/technology/ai/rss/`**；采集脚本用 `curl` **未加 `-L`**，所以每次只抓到跳转壳。**不是源失效，是采集器不跟随重定向。**
- **验证**：加 `-L` 后 `HTTP 200 / 30,392 bytes / 20 items`，最新条目为 2026-11-16 的 "New Ask Maps features to help with holiday travel and prep"。
- **修复**：`fetch_1117.sh` 的 `grab()` 函数已改为 `curl -sSL`（**同一脚本内的 arXiv / HackerNews / OpenAI RSS / Decoder RSS 调用一并受益于该保护**，此前它们若遇到重定向也会静默失真）。已重跑 `rss-gai-1117.xml` 并入本窗语料（30392 B，20 items）。
- **产出价值**：恢复后即见 Gemini 4 Hydrogen 搜索升级、Gemini Decisions API、Gemini Intelligence 多设备特性——**这是 Google 侧与 Qwen4-Max / Anthropic 记忆研究同窗的对位信号**。此前 10 窗报告把它列为"建议下线"，是**误判**：应当先修再下。

---

## 5️⃣ 产物清单

| 产物 | 路径 |
|---|---|
| 本报告 | `heartbeat/nightly-scout-2026-11-17.md` |
| 原始语料 | `graphify-out/raw/scout-2026-11-17-corpus.md`（313,265 B，含恢复后的 Google AI blog 20 条） |
| 图谱快照 | `graphify-out/2026-11-17/snapshot.json`（243 节点 / 450 边）+ `manifest.json` |
| 主图谱 | `graphify-out/graph.json`（**3,155 节点 / 7,671 边 / 37 社区**，合并前已备份 `graph.json.bak.20261117-0140`） |
| 图谱报告 / HTML | `graphify-out/GRAPH_REPORT.md`（前版备份 `.bak.20261117`）+ `graphify-out/graph.html`（3.25 MB） |
| LanceDB 行 | `rows_1117.json`（7 行）→ `~/.openclaw/memory/lancedb-pro` 表 `nightly-scout`（568 → **575 行**） |
| 采集脚本 | `fetch_1117.sh`（**已加 `-L`**）/ `fetch_gh_1117.sh` / `fetch_pages_1117.sh` |
| 构建脚本 | `prep_arxiv_1117.py` / `build_corpus_1117.py` / `build_graph_1117.py` / `merge_graph_1117.py` / `build_rows_1117.py` / `update_lancedb_1117.py` / `regen_report_1117.py` |
| 每日笔记 | `agents/scout/memory/2026-11-17.md` |

---

## 6️⃣ P0 / P1 清单

**P0**
1. 🔴 **重启 gateway 一次 + `openclaw doctor --fix`** —— 修 `heartbeat-health` **57x** error（昨日 32x，持续恶化）。错误信息已给出明确修复路径："Stop the Gateway, run `openclaw doctor --fix` to inspect and repair this agent database, and restart"。根因仍是 health 库写入冻结（mtime 停在 11-05 07:18:49），11-14 同手段已验证有效。**ZP 空窗手动 `/restart`**。
2. 🔴 **OpenRouter 余额 0**（连续第 7 窗）—— 充值可把新闻摘要从全 MiniMax 兜底的 ~6 分钟压下来，属 ZP 决策。

**P1**
3. 🟡 **新闻摘要作业双跑 + 投递层失败** —— crontab `0 8 * * *` 与 openclaw job `fe5fa0ce` 同分钟触发；11-16 crontab 侧产出成功（HTML + 邮件 + 飞书均达），但 openclaw 作业因 `SESSION_PLACEMENT_TURN_SETTLEMENT_CLOSED` 记 error。**建议二选一：删 crontab 那条只留 openclaw job，或错峰（如 crontab 改 `5 8`）**。
4. 🟡 **`openclaw-backup.sh` L275 `local` 报错** —— 该段在函数体外，`local` 不可用（11-16 03:00 日志可见）。当日备份仍 status=ok，属日志噪声但会干扰故障判断，已在文件内注释说明。
5. 🟡 **健康库写入冻结影响面扩大** —— 本场发现 coder/finance/health/orchestrator/work 五个 agent 库 mtime 均停在 11-16 04:1x（而非仅 health 一个）。若非本场 scout 库在写，可能已扩散为"多个 agent 库同时冻结"，重启后应逐库复核 mtime 是否恢复。
6. 🟡 **跟踪 Anthropic 记忆研究的完整一手材料** —— 找 Anthropic 官方研究原文（含 Dreaming 在 Managed Agents 上的实现细节、Sonnet 3.7 vs Fable 5 的完整多局对比），本窗报道明确承认"每模型只跑了单局"。
7. 🟡 **新增两个定量采样口**（建议）：**(a) 单任务成本 / 每任务 token 消耗**（Artificial Analysis、Work360、Terminal-Bench）；**(b) agent 记忆的存储-收益曲线**（笔记条数 vs 任务成功率）。详见第 3️⃣ 推论。

**已闭环**
- ✅ **Google AI blog RSS 十窗旧缺陷** —— 根因是 302 未跟随，`curl -L` 已修，20 条内容恢复入语料。
- ✅ NAS 备份断档（233 小时）—— 已连续 3 天正常（11-15 / 11-16 均产出并推送）。
- ✅ MiniMax 429 配额压力持续收敛（当前 ok=181 / err=2）。
- ✅ Gateway 10 月式内存泄漏未复现（4.18 GB，+2.66 MB/h，预测 1501 小时后触阈）。
