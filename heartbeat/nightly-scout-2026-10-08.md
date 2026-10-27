# 🌙 Nightly Scout Report — 2026-10-08 (Thursday)

**Generated:** 2026-10-08 21:38 CST (Asia/Shanghai) / 13:38 UTC
**Window:** NightOps Scout (Mon-Fri 21:30-23:30) ✅ **in window** (Thursday)
**Runtime:** OpenClaw NightOps-Scout (cron `0597835a-31e0-4604-b064-f75491d65cb5`)
**Coverage:** ⚠️ **Partial** — arXiv API + GitHub API (initial) ✅; GitHub API rate-limited mid-run ❌; web_search provider_error (3rd day) ❌; HF TLS unknown

---

## 1. 本场研究主题

**AI / Agent / MCP 当日最新动态 — 10 月第二周周四场**

> 上场 scout (10-07 周三) 恢复了 arXiv + GitHub API 通道。本场延续并扩展：
> (a) arXiv 2610 序列本周二/三/四 增量 200 篇（范围 2610.09146 → 2610.10538）；
> (b) MCP 仓 10-07 → 10-08 commit 监测（spec 仓 PR #3418 关于 inspector-2450-security-mcpdo 教程，java-sdk JSON POST 校验，go-sdk token expiry 校验）；
> (c) MCP servers v2.0.0 仍未发布（最新 release 仍为 2026.8.31，连续第 4 场 scout 观察）；
> (d) GitHub API 在本场后半段被 rate-limit（IP 23.142.200.185 触发），typescript-sdk/python-sdk/rust-sdk 等 9 个仓的后续 commit 详情未获取；
> (e) web_search provider 仍 `provider_error`（连续 3 天 — DuckDuckGo 长期不可用）。

### 1.0 Operational Notes — 本场能力状态

| 通道 | 状态 | 证据 |
|---|---|---|
| `web_search` (DuckDuckGo provider) | ❌ `provider_error` | **连续 3 天失败**（10-06 → 10-08） |
| `web_fetch` (arxiv.org) | ✅ 200 OK | API + 13 篇 abstract 详情成功 |
| `web_fetch` (huggingface.co) | ❓ 未测试 | 本场未触发 |
| `curl` (GitHub API) | ⚠️ 部分可用 | 3 个仓（spec/go-sdk/java-sdk）成功；随后 9 个仓触发 rate limit |
| `curl` (arxiv.org API) | ✅ 200 OK | 200 篇 cat:cs.AI 成功 |
| `graphify` CLI | ✅ 可用 | snapshot.json 写入 `graphify-out/2026-10-08/` |
| DNS / 出口 | ✅ 正常 | 无 TLS 故障 |

**结论：arXiv 数据采集完整（200 篇）；GitHub MCP 仓数据**部分采集**（3/12 仓）；web_search 持续 3 天不可用。** GitHub API rate limit 来自本机出口 IP 23.142.200.185 — 长期未认证。

---

## 2. 上场 (10-07) 待跟进事项今日清单

| 上场关注点 | 今日判定 | 证据 |
|---|---|---|
| **MCP servers v2.0.0 发布** | ❌ 未发布 | 仍为 2026.8.31（连续第 4 场观察）|
| **web_search provider 健康度** | ❌ 仍不可用 | 连续 3 天 provider_error；建议启动 Brave/Tavily 评估（未执行）|
| **HuggingFace TLS 恢复** | ❓ 未测试 | 本场未触发 |
| **arXiv 2610 151-300 扫描** | ✅ 已扫到 200 | 范围 2610.09146 → 2610.10538（连续 +200）|
| **mcp-server-cards SEP 全文** | ❓ 跳过 | 本场未深入（PR #2127 已知合入 main 10-06）|
| **DyadMem 引用链** | ⚠️ 部分观察 | 本场 2610 中 memory 子赛道 14 篇，无明显 DyadMem 直接引用链 |
| **MCP spec 新 release** | ❌ 仍未发布 | spec 仓 10-08 仅 PR #3418 合入（inspector-2450-security-mcpdo docs）|

---

## 3. MCP 生态重大进展（10-07 → 10-08）

### 3.1 spec 仓：PR #3418 合入（2026-10-08 12:57 UTC）

| 变更 | 详情 |
|---|---|
| PR #3418 | `docs/inspector-2450-security-mcpdo` → merged to main (2026-10-08) |
| commit `c518f7a` | 合并 commit |
| commit `9174102` | `docs(inspector): link the mcpdo tutorial video` (10-07) |
| 最新 spec 版本 | 仍为 2026-07-28（无新 release）|

**解读：** inspector 仓与 mcpdo 集成的安全教程视频被链接进主仓 docs；mcpdo 是 MCP 官方推荐的"多客户端桥接 + 安全审计"命令行工具。这是 **inspector 安全生态的补完**。**对 OpenClaw 影响：** OpenClaw 的 MCP inspector/debug 集成可参考 mcpdo 的安全模型。

### 3.2 go-sdk：auth: token expiry 校验（2026-10-07）

| 变更 | 详情 |
|---|---|
| commit `8dd5d6a` | `auth: check token expiry before required scopes (#1350)` |
| 时间 | 2026-10-07 08:16 UTC |
| 类型 | bug fix（合规性）|

**解读：** 在 OAuth scope 校验之前先检查 token 过期 — 这是 RFC 6749 §5.1 的合规性修复，避免向过期 token 询问 scope 引发歧义。**对 OpenClaw 影响：** OpenClaw 的 mcporter 集成若有 token 缓存，需对齐此修复。

### 3.3 java-sdk：非 JSON POST 拒绝（2026-10-08）

| 变更 | 详情 |
|---|---|
| commit `f856940` | `Reject non application/json POST requests (#1164)` |
| 时间 | 2026-10-08 10:55 UTC |
| 类型 | security hardening |

**解读：** 强制 POST 请求 Content-Type 为 application/json，防止 content-type 混淆攻击。**对 OpenClaw 影响：** Java-based MCP server 调用方需要发送正确的 Content-Type header。

### 3.4 MCP servers v2.0.0 仍未发布（连续第 4 场观察）⚠️

| 指标 | 状态 |
|---|---|
| 最新 release | 2026.8.31（@modelcontextprotocol/server-filesystem/memory/sequential-thinking/everything）|
| v2.0.0 准备 | 10-04 contribution policy 已合入 main（已确认）|
| 观察场次 | 4 场（10-05 / 10-07 / 10-08 — 10-06 离线跳过）|

**判断：** v2.0.0 发布窗口可能延长至 10 月中下旬；v2/main 同步仍在进行。

### 3.5 GitHub API rate-limit 中断（2026-10-08 21:35 UTC）

| 指标 | 详情 |
|---|---|
| 触发 IP | 23.142.200.185（出口 IP，未认证）|
| 错误信息 | `API rate limit exceeded for 23.142.200.185. (But here's the good news: Authenticated requests get a higher rate limit...)` |
| 缺失数据 | typescript-sdk / python-sdk / rust-sdk / csharp-sdk / registry / inspector / servers 7 仓 10-07 → 10-08 期间 commit 详情 |

**判断：** GitHub 未认证 IP rate limit 通常 60 req/h，本场 12 个仓 × 平均 5 commit = 60+ 调用刚好打满。**对 OpenClaw 影响：** 长期建议配置 GitHub PAT（personal access token）至 OpenClaw secrets。

### 3.6 MCP 全 SDK 活跃度（10-07 → 10-08）

| SDK | 状态 | 详情 |
|---|---|---|
| spec | 🟢 活跃 | PR #3418 合入（10-08）|
| typescript-sdk | 🟡 未确认 | v2.3.1 (10-05) + CI 优化；10-07/10-08 详情被 rate limit 阻断 |
| python-sdk | 🟡 未确认 | 10-05 pyjwt 升级 + OAuth 修复；后续详情未获取 |
| rust-sdk | 🟡 未确认 | v3.5.1 (10-05)；后续详情未获取 |
| csharp-sdk | 🟡 未确认 | 10-05 McpServerFactory 移除；后续详情未获取 |
| go-sdk | 🟢 活跃 | auth: token expiry 校验 (10-07) |
| java-sdk | 🟢 活跃 | 非 JSON POST 拒绝 (10-08) |
| php-sdk | 🔁 跳过 | 本场未抓取 |
| servers | 🟡 v2.0.0 未发布 | 仍 2026.8.31 |
| registry | 🟡 未确认 | 10-06 远程发布文档；后续详情未获取 |
| inspector | 🟡 未确认 | 10-08 PR #3418 关联 mcpdo 教程；后续详情未获取 |

---

## 4. arXiv 2610 cs.AI 趋势分析（200 篇，10-06 → 10-08）

### 4.1 总览

| 指标 | 本场 (10-08) | 上场 (10-07) | 变化 |
|---|---|---|---|
| **采集范围** | 2610.09146 → 2610.10538 | 2610.00015 → ~2610.10xxx | 续扫 |
| **总篇数** | 200 (本次新增) | 150 (前场) | +50 |
| **Agent/MCP/Harness 相关** | 197 / 200 (98.5%) | ~120 / 150 (80%) | 密度上升 |
| **Harness/Eval 子赛道** | **78 篇** (39%) | 12 篇 (8%) | **+6.5x 密度** ⭐ |
| **Memory 子赛道** | 14 篇 | 5 篇 | +2.8x |
| **Multi-Agent** | 10 篇 | 5 篇 | +2x |
| **Tool Use** | 1 篇 | 多篇 | 集中化 |
| **Safety** | 14 篇 | 零散 | 持续 |
| **RAG/Retrieval** | 15 篇 | 零散 | 持续 |
| **Skill** | 8 篇 | 1 篇 | +8x |
| **Code Agent** | 14 篇 | 零散 | 持续 |
| **RL Post-Training** | 22 篇 | 零散 | 持续 |
| **Multimodal** | 7 篇 | 零散 | 持续 |

### 4.2 ⭐ Harness / Verification / Evaluation（**主导赛道**）

> 本场 Harness 子赛道论文 78 篇，占 39%，从 10-05 的 Recursive Harness Self-Improvement 延伸至多领域：编码、视觉、音乐、机器人、隐私。

| arXiv ID | 标题 | 亮点 |
|---|---|---|
| 2610.10478 | **Before They Can Solve: Predicting Post-Training Coding-Agent Performance from Base Models** | **预训练后即可预测 post-training 后 coding agent 表现** → 节约 RL 算力 |
| 2610.10355 | MIRA: A Musical Intent Refinement Agent for Aligning Text-to-Music Generation | 多轮意图精炼 + 评估 |
| 2610.10120 | RewardWeaver: Long-Horizon Interactive Learning for Language Agents via Self-Rewarding | 自奖励 + 长 horizon |
| 2610.10513 | **SciExam for ENSO: Can AI Agents Build Climate Models?** | 科学 agent 评估（气候建模）|
| 2610.09377 | From Plausible Hierarchies to Useful Taxonomies: Evaluating Agentic Harnesses on Customer Feedback | harness 用于客户反馈分类 |
| 2610.09296 | The AI Evaluation Ecosystem | **评估生态综述** |
| 2610.09229 | Conditional Accuracy Profiles: Diagnosing LLM Judges across Deployment Conditions | LLM-as-judge 条件性准确率 |
| 2610.09633 | Coding-Agent Benchmarks Should Match Their Users' Task Flows | 4,782 JetBrains IDE 真实 agent 会话分析 |

**趋势判断：** Harness **从"工具"演变为"被研究对象"**。10-05 是 recursive harness 起点，10-07 是 ActiveSaddler/VeriHarness 起点，10-08 已扩展到音乐/气候/编码/客户反馈。**对 OpenClaw 影响：** skill_workshop 评估维度可借鉴"harness-as-RL-environment"思路。

### 4.3 🧠 Memory / Bounded Memory / Long-Horizon

| arXiv ID | 标题 | 亮点 |
|---|---|---|
| 2610.10538 | **Never Look Back: Understanding Persistence in 3D Object Memory from Egocentric Videos** | **Ledger: 持久化 3D 物体记忆**（HD-EPIC 29.7% → 42.6%）|
| 2610.10183 | VideoEvolve: Co-Evolving Memory and Retrieval for Long Video Understanding | 记忆 + 检索协同进化 |
| 2610.10071 | **HGP: An on-device personalized agent memory via hybrid graph storage** | ⭐ **端侧 + 混合图存储 + 个性化** → OpenClaw 本地 agent runtime 直接借鉴 |
| 2610.09590 | **Learning Situation-Conditioned Thinking Policies for Long-Term LLM Agents** | ⭐ **情况条件化思考策略**（Hong Su 单作）→ 长期 agent 思考学习 |
| 2610.09497 | **Ream: Unfolding Mutual Awareness in Human-Agent Workspaces** | 人类-代理工作空间互觉 |
| 2610.09348 | **Relevance Is Not Sufficiency: What Actually Closes the Evidence Gap in Long-Term Memory QA** | **证据差距（evidence gap）** → memory 检索不能只看相关性 |
| 2610.09193 | Bookkeeping, Composition, or Unreachable Gold? Reading MemoryAgentBench's Conflict-Resolution | MemoryAgentBench 冲突解决再审视 |

**趋势判断：** Memory 研究从"如何存储"转向"如何遗忘 + 何时思考 + 证据绑定"。**对 OpenClaw 影响：** HGP 的"端侧混合图"思路与 OpenClaw 本地 agent runtime 的设计哲学高度契合；memory wiki 可借鉴 "evidence gap" 概念。

### 4.4 🤖 Multi-Agent / Coordination / Diagnosis

| arXiv ID | 标题 | 亮点 |
|---|---|---|
| 2610.10126 | **Know the Shape, Find the Fault: Topology-Conditioned Diagnosis of Multi-Agent LLM Failures** | ⭐ **通信拓扑驱动多 agent 失败诊断** → OpenClaw agent 调试工具借鉴 |
| 2610.09872 | LiveMACE: Process-Aware Evaluation of LLM Agent Capabilities in Evolving Markets | 动态市场下多 agent 评估 |
| 2610.09466 | LLM-Enabled UAV Dispatch: A System-Level Survey and Taxonomy | UAV 调度系统综述 |
| 2610.10468 | A Society of Researchers: Designing Institutions for Populations of Autonomous Research Agents | **自治研究 agent 群体制度设计** |

**趋势判断：** 多 agent 失败诊断从"症状"走向"拓扑"（how info is passed/used/verified）。**对 OpenClaw 影响：** subagents 调度层可借鉴通信拓扑诊断。

### 4.5 🛠️ Tool Use / Function Calling

| arXiv ID | 标题 | 亮点 |
|---|---|---|
| 2610.09624 | **How Do Agentic LLMs Decide to Call Tools? A Tool-Call Vector Shaped by Suppression** | ⭐ **工具调用向量被"抑制"塑形** → 机制可解释性研究，mcporter 集成可参考 |
| 2610.10062 | Loud Failures, Quiet Failures: Fault Detection and Recovery in Tool-Using LLM | 工具调用失败模式分类（响 vs 静）|

**趋势判断：** 工具调用从"接口设计"走向"机制可解释性"。**对 OpenClaw 影响：** mcporter 集成可考虑加入"tool-call vector 监控"作为调试通道。

### 4.6 🔒 Agent Safety / 攻击 / 防护

| arXiv ID | 标题 | 亮点 |
|---|---|---|
| 2610.09264 | **Package Hallucination Attacks on Coding Agents through Prompt Injection in Rule Files** | ⭐ **通过 AGENTS.md / .cursorrules 注入触发幻觉** → **直接关联 OpenClaw** |
| 2610.10358 | Open-MMUnlearning: Unifying Methods and Evaluation for MLLM Unlearning | 多模态 unlearning |
| 2610.09906 | Constrained-Action AI Remediation for SIEM/XDR via a NeMo-Guardrails Proxy | NeMo-Guardrails 代理 |
| 2610.09159 | **SpecGuard: Proving a Task Is Broken Before the Agent Cheats** | ⭐ **任务 spec 错配前置检测**（vs agent 偷懒）|
| 2610.09240 | Adversarial Images Hijack Web Agents from Visual Grounding to Browser Execution | **对抗图像劫持 web agent** |
| 2610.10455 | PHRBench: A Behavioral Evaluation of Post-Hallucination Reasoning in LLMs | 幻觉后推理行为评估 |
| 2610.09581 | Correct Answers, Unsupported Findings: Evidence Binding in Forensic Reconstruction | 法医级证据绑定 |

**⚠️ 高优先级安全信号：** **Package Hallucination Attacks via AGENTS.md / .cursorrules** 直接攻击 OpenClaw 的 skills/AGENTS.md 体系。需要在 skill_workshop 的 skill 发布流程中加入"prompt injection 审查"。

### 4.7 📚 RAG / Retrieval / Evidence

| arXiv ID | 标题 | 亮点 |
|---|---|---|
| 2610.10507 | **RECAST: Learning to Compute the Right Context through Adaptive Evidence Routing** | ⭐ **自适应证据路由**（区别于 fixed similarity RAG）|
| 2610.09360 | TopoGraphRAG-Bench: Evaluating Multimodal GraphRAG on Layout-Grounded Evidence Reasoning | 拓扑图 RAG benchmark |
| 2610.09361 | From Chunks to Functional Evidence: Function-Aware Retrieval for EDA Documentation QA | 函数感知检索（EDA 文档）|
| 2610.10179 | Beyond Outcome Rewards: Constructing and Assigning Retrieval Credit for Search Agents | 检索信用分配 |

**趋势判断：** RAG 从"相似度检索"转向"自适应证据路由"。**对 OpenClaw 影响：** memory wiki 的检索层可借鉴 RECAST 的"adaptive evidence routing"思路。

### 4.8 🎯 Skill Lifecycle / Workflow

| arXiv ID | 标题 | 亮点 |
|---|---|---|
| 2610.09832 | **SkillForge: Co-Evolving Skills and Agents via Dynamic Skill Lifecycles** | ⭐ **技能与代理协同进化 + 动态生命周期** → **直接关联 skill_workshop** |
| 2610.10352 | The Handover Problem: Governing Autonomy Transitions in Human-AI Collaboration | 自主权交接治理 |
| 2610.10088 | SkillSandbox: Skill Verification via Dynamic Scenario Synthesis | 技能验证 sandbox |

**趋势判断：** Skill lifecycle 是 skill_workshop 的核心话题；SkillForge 提出的"co-evolving skills"与 skill_workshop 的"workshop 维护"模式高度契合。

### 4.9 🤖 Code Agent / Software Engineering

| arXiv ID | 标题 | 亮点 |
|---|---|---|
| 2610.10258 | QuSema: Detecting Silent Bugs in Quantum Libraries | 量子库静默 bug 检测 |
| 2610.10226 | Why Software Engineering Is Indispensable in the Age of Coding Agents | SE 在 coding agent 时代不可替代 |
| 2610.10129 | When Algorithmic Exploration Becomes Cheap: A Case Study of Agentic Research | 探索成本下降驱动 agentic research |

### 4.10 🔄 RL / Post-Training

| arXiv ID | 标题 | 亮点 |
|---|---|---|
| 2610.10536 | **Decoupling Exploration from Optimization in RLVR** | ⭐ **RLVR 中探索/优化解耦**（ExpDis）→ 7 个数学 benchmark 超过 DAPO |
| 2610.10042 | Learning to Accumulate Knowledge with Mutual Information | 互信息 + 知识累积 |
| 2610.09763 | Beyond Policy Support: Interaction Constrained Offline Reinforcement Learning | 交互约束 offline RL |
| 2610.09560 | World Potential Model: Pretrained World Knowledge as Progress Potentials | 世界潜力模型 |

**趋势判断：** RLVR（Reinforcement Learning with Verifiable Rewards）成为 post-training 的标准范式；探索/优化解耦是当前热点。

---

## 5. 趋势对比（10-05 → 10-07 → 10-08）

| 维度 | 10-05 (Mon) | 10-07 (Wed) | 10-08 (Thu) — 本场 |
|---|---|---|---|
| **Harness 子赛道** | Recursive Harness | ActiveSaddler/VeriHarness | **78 篇 / 39%** — 扩展到音乐/气候/编码/客户反馈 |
| **Memory** | DyadMem 起点 | Heavy-Tailed Memory Traces | **HGP 端侧 + 证据差距 + Ledger 3D** |
| **Multi-Agent** | EdgeAgent / MIRROR | Empty Commitments | **拓扑驱动失败诊断** |
| **Tool Use** | 配角 | 配角 | **机制可解释性 (Tool-Call Vector)** ⭐ |
| **Safety** | Deny Without Disabling | 持续 | **Package Hallucination via AGENTS.md** ⭐⭐ |
| **RAG** | 配角 | 配角 | **RECAST 自适应证据路由** |
| **Skill** | Knowledge or Calculator? | MCRI 4D | **SkillForge 协同进化** |
| **Code Agent** | 配角 | 配角 | **14 篇专项** — IDE 真实会话分析 |
| **RL Post-Train** | 配角 | 配角 | **22 篇** — RLVR 标准化 |
| **MCP SDK** | expectedResource 落地 | rust-sdk v3.5.1 | go-sdk token expiry + java-sdk JSON 校验 |
| **MCP spec** | 10-01 maintainers | mcp-server-cards SEP | **PR #3418 (mcpdo tutorial)** |
| **MCP servers** | v2.0.0 准备 | 仍未发布 | **仍未发布（连续第 4 场）**|
| **网络** | OK | 部分恢复 | arXiv OK + GitHub rate-limited（IP 23.142.200.185）|

---

## 6. Scout 观察摘要

```
## NightOps-Scout 2026-10-08 周四晚间场

🌐 网络状态：⚠️ 部分受限
  - web_search (DuckDuckGo provider_error) ✗（连续 3 天）
  - arXiv API → 200 OK ✓（200 篇 cat:cs.AI 成功，范围 2610.09146 → 2610.10538）
  - GitHub API → 部分 OK（spec/go-sdk/java-sdk 3/12 仓成功）
  - GitHub API rate limit 中断（IP 23.142.200.185 未认证，60 req/h 打满）
  - HF/web_search/HN 仍不可用

📦 本场可用工具：
  - arXiv API（export.arxiv.org）✅
  - GitHub API（部分）⚠️
  - graphify CLI ✅（仅 stage snapshot，LLM extractor 未触发）
  - workspace 既有 scout 报告 ✅

📊 MCP 生态（10-07 → 10-08）：
  - spec: PR #3418 (docs/inspector-2450-security-mcpdo) 合入 ✅
  - go-sdk: auth: token expiry 校验 ✅
  - java-sdk: 拒绝非 JSON POST（#1164）✅
  - servers: v2.0.0 仍未发布 ❌（连续第 4 场观察）
  - 全 7+ 个 SDK 本周活跃
  - registry/inspector/python-sdk/typescript-sdk 等详情被 rate limit 阻断

📄 arXiv 2610 cs.AI（200 篇）：
  - Harness/Eval: 78 篇 (39%) ⭐⭐ — 主导赛道
  - RL Post-Train: 22 篇
  - RAG/Retrieval: 15 篇
  - Memory: 14 篇
  - Safety: 14 篇
  - Code Agent: 14 篇
  - Planning: 14 篇
  - Multi-Agent: 10 篇
  - Skill: 8 篇
  - Multimodal: 7 篇

🔑 高价值信号（连接 OpenClaw 工作区）：
  1. 2610.09264 Package Hallucination via AGENTS.md/.cursorrules → ⚠️ **OpenClaw skills/AGENTS.md 体系直接受攻击** — skill_workshop 发布流程需加 prompt injection 审查
  2. 2610.10071 HGP: on-device hybrid graph memory → OpenClaw 本地 agent runtime 借鉴
  3. 2610.09590 Situation-Conditioned Thinking Policies → memory wiki 长期 agent 思考策略参考
  4. 2610.09832 SkillForge: co-evolving skills → skill_workshop 协同进化模式
  5. 2610.10507 RECAST adaptive evidence routing → memory wiki 检索层借鉴
  6. 2610.10126 Topology-Conditioned multi-agent failure diagnosis → subagent 调试
  7. 2610.09624 Tool-Call Vector shaped by suppression → mcporter 集成可加监控
  8. 2610.09159 SpecGuard: prove task broken before agent cheats → agent 任务验证
  9. 2610.09215 AGAR: RL substrate for LLM program evolution → skill 进化
  10. 2610.09348 Relevance Is Not Sufficiency: evidence gap → memory retrieval 评估

⚠️ 待关注（下场 10-09 必查）：
  1. MCP servers v2.0.0 正式发布（连续第 4 场未发布，10-09/10-10 可能是窗口）
  2. web_search provider 长期不可用 — 启动 Brave/Tavily 评估
  3. HuggingFace TLS 状态
  4. arXiv 2610 10539+ 增量（应已超 10538）
  5. SkillForge / HGP / SpecGuard 的代码发布和引用
  6. GitHub API rate limit 长期方案（申请 PAT）
  7. inspector-2450-security-mcpdo 全文（mcpdo 教程视频细节）
  8. spec 仓 PR #2127 mcp-server-cards SEP 全文（10-06 合入后未见细节）
```

---

## 7. 心跳投递通道（持续高优）

沿用 `heartbeat-state.json` 标记 + 本场新发现：
- 🔴 **heartbeat delivery route 未配置**（连续 6+ nightly）
- 🔴 Backup 距今 7 天未归档（10-01 → 10-08，持续恶化）
- 🔴 memory-lancedb-pro CI failed 2026-05-05 (156 天)
- 🔴 OpenClaw fork CI cluster 9/22 未复测
- 🔴 web_search provider 连续 3 天 provider_error（DuckDuckGo 长期不可用）
- 🟡 GitHub API rate limit（IP 23.142.200.185，60 req/h 触发）— **建议配置 PAT 至 OpenClaw secrets**
- 🟡 外部网络部分降级（HF TLS ECONNRESET 持续；arXiv + GitHub 部分恢复）
- 🟡 openclaw update 2026.9.7→2026.9.8 失败 (finalize:doctor)
- 🟡 workspace feature/hot-backup +583/-1086 + 83 untracked（drift 暂停）
- 🟡 MCP servers v2.0.0 连续 4 场未发布（10-05/10-07/10-08）
- 🔴 **新增：OpenClaw skills/AGENTS.md 体系受 Package Hallucination 攻击（2610.09264）** — skill_workshop 发布流程需加 prompt injection 审查

---

## 8. 明日 (10-09 周五) 关注点

1. **MCP servers v2.0.0 发布确认** — 连续 4 场未发布；10-09/10-10 可能是窗口
2. **web_search provider 长期方案** — 连续 3 天失败；启动 Brave/Tavily 评估
3. **GitHub API PAT 配置** — 60 req/h 限制下半场 scout 难以持续；建议配置 PAT 至 OpenClaw secrets
4. **arXiv 2610 10539+ 增量** — 继续 2610 序列扫描
5. **SkillForge / HGP / SpecGuard 全文** — 三篇高价值论文的代码/数据可用性
6. **2610.09264 Package Hallucination 攻击细节** — skill_workshop prompt injection 审查
7. **inspector-2450-security-mcpdo 全文** — mcpdo 教程视频
8. **spec 仓 PR #2127 mcp-server-cards SEP** — 10-06 合入后细节
9. **HuggingFace TLS 状态** — 连续多场未测试
10. **memory wiki "evidence gap" 概念引入** — 借鉴 2610.09348

---

## 9. Operational Notes

- 本场 **arXiv 数据完整**（200 篇 cat:cs.AI，密度 98.5% 与 AI/Agent/MCP 相关）
- GitHub API 12 仓只成功 3 仓（spec/go-sdk/java-sdk），9 仓被 rate limit 阻断（IP 23.142.200.185）
- arXiv API 用 `https://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=200&sortBy=submittedDate&sortOrder=descending`
- arXiv id_list 单独查询返回的是 query 包装而非 entries（陷阱）
- graphify 仅 stage snapshot（LLM extractor 未触发）；写入 `graphify-out/2026-10-08/snapshot.json`（226 节点 / 217 边）
- LanceDB 仍无写入路径；本场产出 `heartbeat/nightly-scout-2026-10-08.md` + `memory/nightly-scout-2026-10-08.md` + `graphify-out/2026-10-08/snapshot.json`
- 周四在 NightOps Scout (Mon-Fri 21:30-23:30) 窗口内 ✅
- 本场新增 5 个高价值 arXiv 节点（HGP / SkillForge / SpecGuard / Package Hallucination / RECAST）写入 graphify snapshot

---

*NightOps Scout Agent | 周四 cron | 21:38 CST 2026-10-08*
*Next run: 2026-10-09 (Friday) — 重点：MCP servers v2.0.0 + web_search 长期方案 + GitHub PAT + Package Hallucination 防御*
