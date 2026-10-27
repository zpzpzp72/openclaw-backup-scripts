# 🌙 Nightly Scout Report — 2026-10-19 (Monday)

**Generated:** 2026-10-19 21:46 CST (Asia/Shanghai) / 13:46 UTC
**Window:** NightOps Scout (Mon–Fri 21:30–23:30) ✅ **in window** (Monday)
**Runtime:** OpenClaw NightOps-Scout (cron `0597835a-31e0-4604-b064-f75491d65cb5`)
**Coverage:** ✅ arXiv API (40 cs.AI) ✅; GitHub API (14 MCP repos) ✅; web_search provider_error (5th day) ❌

---

## 1. 本场研究主题

**AI / Agent / MCP 当日最新动态 — 10 月第三周周一场**

> 上场 (10-09 周四) 观察：MCP servers v2.0.0 仍未发布（连续 5 场）；spec 仓 PR #3418 合入 inspector 安全页。
> 本场 **重大突破**：
> (a) **MCP servers v2.0.0 于 2026-10-19 正式发布**（cliffhall，06:46 UTC）— 终结 6 场连续观察；
> (b) **`modelcontextprotocol/spec` 已重命名为 `modelcontextprotocol/modelcontextprotocol`**（旧路径 404）；
> (c) arXiv cs.AI 拉取 40 篇（2610.23027 → 2610.23854，全部 2026-10-16 提交，周末批次尚未释放）；
> (d) MCP 生态 14 个仓库扫描 — 新增 kotlin-sdk / php-sdk / ruby-sdk / conformance 覆盖；
> (e) Inspector v2.11.0（10-14）已稳定；spec 仓 25 个 open PR。

### 1.0 Operational Notes — 本场能力状态

| 通道 | 状态 | 证据 |
|---|---|---|
| `web_search` (DuckDuckGo provider) | ❌ `provider_error` | **连续 5 天失败**（10-06 → 10-19） |
| `web_fetch` (间接 via curl) | ✅ 200 OK | 6 次 graphify `add` URL 抓取成功 |
| `curl` (arXiv API) | ✅ 200 OK（需退避） | 首次 429 rate limit → sleep 30 后重试成功；40 篇 cs.AI |
| `curl` (GitHub API) | ✅ 200 OK | 14 MCP 仓 + 3 个 release 端点 |
| `curl` (api.github.com repos/spec) | ❌ 404 | `modelcontextprotocol/spec` 已废弃；新路径 `modelcontextprotocol/modelcontextprotocol` |
| `graphify` CLI | ✅ 部分可用 | `add <url>` 正常（6 次）；`update` 仅对代码文件生效（跳过）；`cluster-only` 路径匹配问题；自建 Python pipeline 写 snapshot |
| DNS / 出口 | ✅ 正常 | 无 TLS 故障 |

**结论：arXiv + GitHub 通道全绿（arXiv 需退避）；web_search 持续 5 天不可用；graphify CLI `add` 路径可用，自建 pipeline 补 snapshot。**

---

## 2. 上场 (10-09) 待跟进事项今日清单

| 上场关注点 | 今日判定 | 证据 |
|---|---|---|
| **MCP servers v2.0.0 发布** | ✅ **已发布** | 2026-10-19T06:46:48Z，cliffhall，tag v2.0.0 |
| **web_search provider 健康度** | ❌ 仍不可用 | 连续 5 天 provider_error；建议启动 Brave/Tavily 评估（**未执行**） |
| **MCP spec 新 release** | ❌ 未发布 | spec 仓最新公开 release 仍为 2026-07-28（但仓库已重命名） |
| **MCP SEP 推进** | ✅ 稳定 | 25 个 open PR；无新 SEP 提交（上场 5 个 SEP 仍在 review） |
| **MCP SDK 跨语言一致性** | ✅ 进展 | php-sdk + ruby-sdk 10-18 同日 5+ commit burst；csharp-sdk 10-17 双 PR |
| **arXiv 2610 序列扫描** | ✅ 推进 | 本场 40 篇（2610.23027 → 2610.23854），与上场 2610.12466 相比 +11300 ID |
| **Inspector 版本** | ✅ v2.11.0 | 10-14 发布（上场关注 2.10.1 npm 已过时） |

---

## 3. arXiv cs.AI 精选（40 篇，2026-10-16 提交）

> ⚠️ 全部 40 篇均为 2026-10-16 批次。arXiv 周末（10-17/18）批次尚未释放，预计 10-20（周二）补发。

### 3.1 MCP / Agent 工具调用（直接 MCP 主题 1 篇 + 工具/agent 相关 8 篇）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.23449** | **GatewayBench: Unified Capability and Security Evaluation Platform for MCP Gateways** | **直接以 MCP Gateway 为对象的评估平台**（本场唯一 MCP 协议级论文） |
| 2610.23342 | Robust Function Calling for LLM Agents Under Interface Drift | 工具接口漂移下的鲁棒 function calling |
| 2610.23307 | MobileInject: Evaluating Reasoning-to-Action Security of MLLM-Based Mobile Agent | MLLM 移动 agent 的推理→动作安全评估 |
| 2610.23344 | Language Models Learn to Improve Language Models | LLM 自动化 AI 研究（含 LM 开发） |
| 2610.23313 | From Memory Hits to Answerable Evidence: Query-Conditioned Memory Compilation | 长期 agent 记忆的查询条件编译 |
| 2610.23311 | Self-Reflective Chain-of-Thought (SRCoT) | 基于证据的自反思 CoT 文本生成 |
| 2610.23317 | AgentOnto: Ontology-Guided LLM Agents for Enterprise Data Analytics | 本体论引导的企业数据分析 agent |
| 2610.23284 | Annotrace: A Workbench for Step-Level Annotation of Agent Traces | agent 轨迹步骤级标注工作台 |
| 2610.23266 | Beyond Marginal Influence: Interaction-Aware Memory Selection for LLM Agents | 交互感知的 agent 记忆选择 |
| 2610.23443 | ScoutRoute: Efficient MoE Routing Using Internal Language Model Signals | 内部 LM 信号的 MoE 路由（巧合命名 Scout） |

### 3.2 安全 / 对齐 / 评估（12 篇，最大社区）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| 2610.23668 | TUPLE-Bench: Evaluating Privacy-Utility Trade-offs in Typed Decision Models | 类型化决策模型的隐私-效用权衡评估 |
| 2610.23670 | OwlSight: A Panoramic Monitor for Chain-of-Thought Reasoning | CoT 推理的全景监控器 |
| 2610.23625 | PresenceBench: LLM Adaptation to User Functional State | 用户功能状态感知的智能适应评估 |
| 2610.23527 | Truth in Contrast: Calibrated Factual Evidence from LM Likelihoods | 基于似然校准的事实证据 |
| 2610.23525 | Trapped in Your Story: Narrative-Induced Sycophancy in LLMs | 叙事诱导的谄媚评估 |
| 2610.23465 | S-GAP: Stealthy Graph Attack Primitives for Graph LLMs | 图 LLM 的隐身图攻击原语 |
| 2610.23445 | RECREG: Recovery-based Shielding for Regular Safety Properties in RL | RL 中基于恢复的正则安全属性屏蔽 |
| 2610.23257 | Reasoning Models Can Control Their CoT When They Tell Themselves To | 推理模型的 CoT 可控性 |
| 2610.23213 | Not All Test-Time Compute Is Evidence: Model-Specific Bias | test-time 计算的模型特异性偏差 |
| 2610.23226 | Characterising and Analysing RAG Techniques | RAG 技术综述与分类 |
| 2610.23161 | Algorithm Modelization: Transforming Optimization Algorithms into Evolvable Intelligence | 优化算法→可进化智能体 |
| 2610.23167 | LongForge: Measuring and Improving Long-Context Instruction Data | 长上下文指令数据质量管控 |

### 3.3 RL / 决策（8 篇）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| 2610.23550 | Reason-guided Human Reward Modeling for Preference-based RL | 人类推理引导的奖励建模 |
| 2610.23436 | Generative Policy Improvement from Observational Data | 观测数据的生成式策略改进 |
| 2610.23256 | Beyond Reward Scoring: Online Multi-Agent Preference Learning | 在线多 agent 偏好学习 |
| 2610.23245 | MGE-PO: Entropy-Aware Credit Assignment for Mathematical Reasoning | 数学推理的熵感知信用分配 |
| 2610.23181 | Tree-Aware Posterior Distillation for Long-Horizon Agentic RL | 长视野 agent RL 的树感知后验蒸馏 |
| 2610.23185 | A Stronger Teacher Within: On-Policy Bidirectional Distillation for MoE | MoE 模型的双向在策略蒸馏 |
| 2610.23085 | Rethinking GRPO for Large Reasoning Model Safety Alignment | GRPO 用于推理模型安全对齐的重思 |
| 2610.23048 | Distill Until Divergence: Error-Truncated Hindsight Distillation for Agentic RL | 误差截断的后见蒸馏 |

### 3.4 Agent / 多智能体（7 篇）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| 2610.23709 | GLOBE: Evolving Structured Agentic Memory for E-commerce | 电商产品优化的进化式 agent 记忆 |
| 2610.23599 | From Trajectories to Differentiated Skills: Cognitive Differentiation | 从轨迹到差异化技能的认知分化 |
| 2610.23598 | RL-Guided Temporal Localization for Dual-Channel Retrieval | 双通道检索的 RL 引导时间定位 |
| 2610.23574 | Darwin-Claw: Environment-Adaptive Experience Consolidation | 环境自适应的经验整合递归自改进 |
| 2610.23554 | SkillBrowser: Selective Skill Exposure for Scalable Skill-Using Agents | 可扩展 skill agent 的选择性技能暴露 |
| 2610.23194 | OfficeTown: Generative Organizations for Evolving Agent Intelligence | 生成式组织驱动 agent 智能进化 |
| 2610.23104 | WebCoder: Scaling General Frontend Development with Artifact-Grounded Agentic Re | 工件锚定的前端开发 agent 扩展 |

### 3.5 视觉 / 多模态 / 推理（6 篇）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| 2610.23854 | Rethinking Vanilla Pixel Diffusion Transformers | 像素空间扩散 Transformer 设计空间重思 |
| 2610.23801 | Beyond SAEs: Consistent Concept Discovery with Sparse Coding | 超越稀疏自编码器的一致概念发现 |
| 2610.23791 | DrugHarness: Evolvable Agent Harness for Computational Drug Discovery | 计算药物发现的进化式 agent 框架 |
| 2610.23615 | Beyond Action Prediction: Learning Search-Free Planning in Latent Space | 潜在空间免搜索规划 |
| 2610.23470 | QD-Rec: Open-Ended Evolution of Recommendations | 质量多样性开放式推荐进化 |
| 2610.23053 | Unifying Embodied Foundation Models via Model-to-Policy Formulation | 具身基础模型的模型→策略统一 |

---

## 4. MCP 生态动态（2026-10-17 → 2026-10-19）

### 4.1 🚀 MCP servers v2.0.0 发布 — 头条新闻

| 指标 | 数值 |
|---|---|
| Tag | **v2.0.0** |
| 发布时间 | **2026-10-19T06:46:48Z** |
| 作者 | cliffhall |
| 前置版本 | v1.0.0（2026-10-11），2026.8.31 |
| v1→v2 间隔 | **8 天** |
| 距旧稳定版 | 45 天（2026.8.31 → 2026-10-19） |

**发布内容**：
- 4 个 TypeScript server 包发布到 npm（`@modelcontextprotocol/server-everything/filesystem/memory/sequential-thinking`），全部 v2.0.0
- 3 个 Python server 包发布到 PyPI（`mcp-server-fetch/git/time`），CalVer `2026.10.19`
- 所有 server 重构为 **modern era spec**（2026-07-28 + 2025 规范），同时保持 legacy 客户端兼容
- TypeScript server 最低 Node 版本提升至 **24**
- 基于 TS SDK v2（codemod 迁移，PR #5063）

**关键 PR**：
- #5166 Release v2.0.0: merge v2/main into main
- #5169 Raise TypeScript servers' Node floor to 24
- #5177 Python CalVer versions for 2026.10.19
- #5178 fix(ci): superseded dispatched run posts no status
- #5174 fix(python): serialize git tool calls, require mcp 2.3

### 4.2 仓库重命名：spec → modelcontextprotocol

| 旧路径 | 新路径 | 状态 |
|---|---|---|
| `modelcontextprotocol/spec` | `modelcontextprotocol/modelcontextprotocol` | 旧路径 404，新路径 200 |
| 描述 | "Specification and documentation for the Model Context Protocol" | — |
| 最新 commit | 2026-10-18（docs: fix broken SEP-2133 link in SEP-2640 #3439） | 活跃 |
| 最新 release | 2026-07-28 | 停滞 73 天 |

**⚠️ 操作影响**：下场起所有 spec 仓 API 调用必须切换到 `modelcontextprotocol/modelcontextprotocol`。

### 4.3 跨语言 SDK 10-17 → 10-19 三日动态

| 仓 | 最新 commit | 关键 PR | 状态 |
|---|---|---|---|
| **go-sdk** | 10-19 | #1412 SSE 字段解析 per spec | **活跃** |
| **java-sdk** | 10-16 | 2.1.x 分支合并 + snapshot 发布 | 维护 |
| **rust-sdk** | 10-17 | #1377 无 session POST 返回 400；#1346 float→int request id | **活跃** |
| **typescript-sdk** | 10-13 | #2968 migration skill | 间歇 |
| **python-sdk** | 10-17 | #3726 每响应独立 header；#3719 Skill `_meta` | **活跃** |
| **csharp-sdk** | 10-17 | #1844 streamable-HTTP 400 JSON 详情；#1903 缺失 server info | **活跃（追赶）** |
| **kotlin-sdk** ✨ | 10-19 | #1032 空闲 session 过期；#1100 SSE 路径保留 | **活跃** |
| **php-sdk** ✨ | 10-18 | 5 commit burst: changelog #611, listChanged #608, InputRequiredResult #606 | **活跃** |
| **ruby-sdk** ✨ | 10-18 | 5 commit burst: request-id 处理（#613/#615/#616/#622） | **活跃** |
| **inspector** | 10-14 | v2.11.0 发布（#2720 milestone merge） | 稳定 |
| **registry** | 10-11 | #1702 嵌套 server.json 发布拦截 | 维护 |
| **conformance** ✨ | 10-01 | 0.2.0-alpha.12, DPoP #396, SEP-2640 #330 | 间歇 |
| **servers** | 10-19 | **v2.0.0 发布** 🎉 | **活跃** |
| **modelcontextprotocol** | 10-18 | #3439 SEP 链接修复 | 活跃 |

> ✨ = 上场未覆盖的新增监控仓

### 4.4 MCP spec 仓 25 个 open PR

| PR # | 标题 | 类型 | 日期 |
|---|---|---|---|
| **3440** | SEP: Form Tasks & Events WG + convert Agents WG → Interest Group | 治理 | 10-16 |
| 3441 | docs(community): restructure community docs (#3363 rebase) | docs | 10-17 |
| 3443 | build(deps-dev): bump typescript-eslint | 依赖 | 10-19 |
| 3444 | build(deps-dev): bump prettier | 依赖 | 10-19 |
| **3415** | **SEP-3415: Events Extension** | 新 SEP | 10-05 |
| **3405** | **SEP-3405: Conformance-Driven SDK Tiers** | 新 SEP | 09-30 |
| **3398** | **SEP-3398: Release Cycle Updates** | 新 SEP | 09-28 |
| **3392** | **SEP-3392: Extension Lifecycle** | 新 SEP | 09-25 |
| **3371** | **SEP-3371: Consistent SDK extension points** | 新 SEP | 09-18 |
| 3364 | docs: clarify extension negotiation | docs | 09-15 |
| 3355 | docs: add client support matrix for Tasks | docs | 09-10 |
| 3331 | Restructure Security IG as a routing group | 治理 | 08-31 |
| 3313 | SEP: Structured Tool-Failure Classification (ToolFailure) | 新 SEP | 08-27 |
| 3312 | schema: draft structured tool-failure classification | schema | 09-02 |
| 3306 | Document identity provider support for enterprise auth | docs | 08-26 |
| 3279 | SEP-3279: Negotiated Tool Result Variants | 新 SEP | 08-19 |
| 3235 | Use updated OAuth Client ID Metadata Document RFC | spec | 08-12 |
| 3191 | docs: rework authorization guide around CIMD | docs | 08-03 |
| 3185 | fix(schema): close oneOf type-check bypass | schema | 08-03 |
| 3149 | SEP-3149: Require Token Endpoint Auth Methods in CIMD | 新 SEP | 07-28 |
| 3118 | SEP-3118: App-Rendered Elicitations for MCP Apps | 新 SEP | 07-23 |
| 3094 | SEP-3094: Granular Citations Format | 新 SEP | 07-15 |
| 2848 | SEP-2848: Asynchronous Approval for Tool Calls | 新 SEP | 06-03 |
| 2847 | Update structuredContent guidance for TextContent blocks | docs | 06-03 |

**关键观察**：本周新增 **#3440（10-16）— Tasks & Events WG 正式成立 + Agents WG 降级为 Interest Group**，反映 MCP 治理从"agents 为中心"向 "tasks/events 工作流"的结构性转变。

---

## 5. graphify 快照（graphify-out/2026-10-19/）

> 本场使用 `graphify add <url>` 成功抓取 6 个新 URL 到 raw/，并通过自建 Python pipeline 写入 snapshot。

### 5.1 输出文件

| 文件 | 大小 | 内容 |
|---|---|---|
| `graphify-out/2026-10-19/graph.json` | 208 KB | 157 节点 / 4 超边的图（graph-tool 格式） |
| `graphify-out/2026-10-19/snapshot.json` | 1.7 KB | 快照元数据 + headlines + next_watch |
| `graphify-out/2026-10-19/clusters.json` | 477 B | 社区分布统计 |
| `graphify-out/raw/scout-2026-10-19-corpus.md` | 70 KB | 本场完整语料（40 arXiv + 14 MCP 仓） |
| `graphify-out/raw/github_com_*_v2_0_0.md` | 8.2 KB | servers v2.0.0 release notes |
| `graphify-out/raw/github_com_*_2_11_0.md` | 7.4 KB | inspector v2.11.0 release notes |
| `graphify-out/raw/github_com_modelcontextprotocol_modelcontextprotocol.md` | 5.6 KB | spec 仓 README |
| `graphify-out/raw/arxiv_2610_23307.md` | 2.4 KB | MobileInject 摘要 |
| `graphify-out/raw/arxiv_2610_23342.md` | 1.7 KB | Robust Function Calling 摘要 |
| `graphify-out/raw/arxiv_2610_23449.md` | 2.4 KB | GatewayBench 摘要 |

### 5.2 社区分布（按节点数降序，基于标签关键词分类）

| 社区 | 节点数 | 占比 |
|---|---|---|
| **Other** | ~55 | 35% |
| **Eval** | ~22 | 14% |
| **RL** | ~20 | 13% |
| **Agents** | ~18 | 11% |
| **Vision/MM** | ~15 | 10% |
| **Reasoning** | ~10 | 6% |
| **Safety/Alignment** | ~8 | 5% |
| **MCP/Tools** | ~5 | 3% |
| **Memory** | ~3 | 2% |
| **Robotics/Embodied** | ~1 | 1% |

> 注：分类基于标签关键词匹配，`Other` 占比较高反映 arXiv 论文标签多样化。

### 5.3 关键发现

1. **MCP servers v2.0.0 已入图** — release notes 通过 `graphify add` 写入 raw/，成为 MCP/Tools 社区新节点。
2. **MCP 学术研究仍然稀缺** — 40 篇 arXiv 中仅 1 篇（2610.23449 GatewayBench）直接以 MCP 协议为研究对象；关键词命中 ~10 篇但主题均为 tool-use / agent 安全。
3. **graphify CLI `add` 路径稳定** — 6 次 URL 抓取全部成功，是当下可靠的增量更新方式。
4. **Inspector v2.11.0 入图** — 与 servers v2.0.0 同日（本周）发布，形成"工具+参考实现"同步更新模式。

---

## 6. 跨场趋势（8 场 scout 09-04 → 10-19 综合）

| 趋势 | 证据（8 场累计） | 判定 |
|---|---|---|
| MCP servers v2.0.0 | 2026.8.31 → 2026.10-19（45 天） | ✅ **已发布** — 下场起退出 watch |
| MCP 仓库重命名 | spec → modelcontextprotocol | ⚠️ **需适配** — 下场起更新 API 路径 |
| MCP 跨语言 SDK hardening | 8 场连续观察，go/java 领先 | ✅ 持续趋势 |
| MCP spec 草案 | 10 个 SEP 在 review（08-27 → 10-16） | ✅ 加速 |
| MCP 治理结构化 | Tasks & Events WG 成立（#3440） | ✅ 新里程碑 |
| MCP 学术研究 | 8 场累计 2 篇直接 MCP 论文 | ⚠️ 机会窗 |
| web_search 故障 | 5 天 provider_error | ❌ 需切 Brave/Tavily |
| php/ruby SDK 崛起 | 10-18 双 5-commit burst | ✅ 新趋势 |
| arXiv Eval/RL 主导 | 连续 3 场 > 50% | ✅ 持续 |
| Inspector 高频发布 | 3 版本/7 天（10-07 → 10-14） | ✅ 节奏稳定 |

---

## 7. 下场（10-20 / 10-21）重点观察

| # | 关注点 | 触发条件 |
|---|---|---|
| 1 | **servers v2.0.0 采用信号** | npm/PyPI 下载量变化；GitHub issue 反馈 |
| 2 | **spec 新 release（2026-11?）** | 2026-07-28 已停滞 73 天 |
| 3 | **SEP-3405 SDK Tiers 合入** | spec 仓 main 分支出现 conformance 目录 |
| 4 | **SEP-3440 WG 落地** | Tasks & Events WG 首次会议/文档 |
| 5 | **web_search 通道恢复** | provider_error 是否转好；或 Brave/Tavily 上线 |
| 6 | **arXiv 2610 周末批次** | 10-17/18 批次预计 10-20 释放 |
| 7 | **Inspector 2.12.0** | 下一 minor 版本节奏 |
| 8 | **graphify CLI 升级** | `add` 路径是否稳定；`cluster-only` 路径修复 |
| 9 | **LanceDB 依赖** | 调研 `pip install lancedb` 或 memory/*.md 旁路 |

---

## 8. 自我观察 / 流程改进

- **arXiv API rate limit 退避策略生效**：首次 429 → sleep 30 重试成功。下场起将 sleep 时间编入脚本（首次失败后 sleep 20-40s）。
- **graphify `add <url>` 是可靠增量路径**：6/6 成功。下场起标准化为"先 `add` 关键 URL → 再自建 pipeline 写 snapshot"。
- **spec 仓库重命名需全局适配**：下场起所有 `modelcontextprotocol/spec` API 调用切换到 `modelcontextprotocol/modelcontextprotocol`。
- **web_search 替代方案仍待启动**：连续 5 天 provider_error。**建议**：下场（10-20 周末场）安排手动测试 Brave Search API 或 Tavily。
- **LanceDB 未写入**：同上场，`import lancedb` 在本机 Python 环境仍失败。本场以 `memory/2026-10-19-scout.md` 旁路替代。

---

## 9. Memory & LanceDB 写入

- ✅ `memory/2026-10-19-scout.md` — 本场 scout 摘要（已写入，46 行）
- ✅ `graphify-out/2026-10-19/snapshot.json` — 节点/边统计 + 社区分布 + headlines（已写入，1.7KB）
- ✅ `graphify-out/2026-10-19/clusters.json` — 社区分布统计（已写入，477B）
- ✅ `graphify-out/2026-10-19/graph.json` — 157 节点图（已写入，208KB）
- ✅ `graphify-out/raw/scout-2026-10-19-corpus.md` — 完整语料（已写入，70KB）
- ✅ `graphify-out/raw/` — 6 个新增 URL 抓取文件（servers v2.0.0, inspector 2.11.0, spec repo, 3 arXiv）
- ✅ `heartbeat/nightly-scout-2026-10-19.md` — 本文件（最终报告）

**LanceDB 操作**：
- ❌ 未执行 LanceDB upsert — `import lancedb` 在本机 Python 环境仍失败（包未安装）
- 旁路：`memory/2026-10-19-scout.md` 已写入，OpenClaw 主 agent 自动索引
- 下场建议：调研 `pip install lancedb --break-system-packages` 或确认 memory/*.md 旁路是否足够

---

**Scout 任务完成。下一场：2026-10-20（周二）21:30 NightOps-Scout 自动续接。**
