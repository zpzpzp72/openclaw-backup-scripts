# 🔭 NightOps Scout Report — 2026-07-29 (Wednesday)

**Generated:** 2026-07-29 21:30 CST (13:30 UTC)
**Window:** NightOps Scout (Mon-Fri 21:30-23:30) ✅ In window
**Sources:** arXiv cs.AI (260 entries), OpenAI Blog, MCP GitHub Releases, GitHub MCP SDK

---

## 📡 AI/Agent/MCP 领域当日动态

### 🔥 重要产品发布

| 项目 | 详情 | 日期 |
|------|------|------|
| **OpenAI: Scientific Computing in the Age of Agentic AI** | 发布 AI Agent 在科学计算领域的实地报告，8个生命科学项目案例，Codex + Claude Code 组合使用 | 2026-07-28 |
| **OpenAI: How AI expands work** | 发布 AI 如何扩展人类工作能力的报告 | 2026-07-27 |
| **OpenAI Health in ChatGPT** | ChatGPT 健康功能上线 | 2026-07-23 |
| **OpenAI Presence** | 新发布 OpenAI Presence 产品 | 2026-07-22 |
| **OpenAI ChatGPT for Small Business** | 小型企业计划发布 | 2026-07-21 |
| **OpenAI × Hugging Face 安全事件** | 联合应对安全事件 | 2026-07-21 |

### 📋 MCP (Model Context Protocol) 最新进展

**MCP TypeScript SDK v1.30.0 发布（稳定版）：**
- **Protocol 基类导出恢复**：`Protocol` 和 `mergeCapabilities` 从 client/server 包根导出（PR #2501）
- **Schema 模块统一**：spec schemas、OAuth schemas、protocol constants 移入 `@modelcontextprotocol/core`（PR #2477）
- **SSE keep-alive 修复**：修复 Streamable HTTP server transport 的 SSE keep-alive 定时器生命周期（PR #2547）
- **安全修复**：升级 @hono/node-server 修复 GHSA-frvp-7c67-39w9（PR #2549）
- **E2E 测试套件**：新增端到端测试（PR #2167）
- **Bearer 认证**：runtime-neutral Bearer authentication（PR #2420）
- **OAuth 发现服务**：runtime-neutral OAuth discovery serving（PR #2422）
- **Zod 3.25 支持**：支持 Zod 3.25 method literals（PR #2368）

**MCP SDK v2.0.0-beta 首次发布（重大里程碑！）：**
- **支持 MCP 2026-07-28 规范修订版**（PR #2402）
- **CommonJS + ESM 双格式构建**（PR #2405）
- **提供 v1→v2 迁移指南**（docs/migration/upgrade-to-v2.md）
- **提供 2026-07-28 修订版适配指南**（docs/migration/support-2026-07-28.md）

**MCP Spec PR #3002 已合并（2026-07-16，SDK 跟进中）：**
- `serverInfo` 从 DiscoverResult body 移至 result `_meta`
- `clientInfo` 从 required 降级为 SHOULD
- 新增公共常量 `SERVER_INFO_META_KEY` ('io.modelcontextprotocol/serverInfo')
- 修复了现代-only 服务器的连接失败问题

**关键影响：** v2.0.0-beta 的发布是 MCP 生态的重要里程碑，标志着协议从 v1 向支持 2026-07-28 规范的新版本演进。CommonJS 支持大幅扩展了 Node.js 生态兼容性。

---

## 📄 arXiv 热门论文精选（2026-07-29 新提交，共260篇）

### 🤖 Agent 相关

| # | 论文 | 核心贡献 |
|---|------|----------|
| 1 | **[Desktop-Delta Bench (DDB)](https://arxiv.org/abs/2607.26041)** | 桌面 GUI 转换理解评测基准，2013个人工验证实例，覆盖~15个Linux应用。评测8个模型家族，最佳排序准确率仅65.1%，揭示 CUA 在状态验证、源跟踪方面的系统性差距 |
| 2 | **[Interactive Reward Agent (IRA)](https://arxiv.org/abs/2607.25904)** | 基于 propose-then-verify 框架的 GUI 任务评估 Agent，通过调用系统/应用工具验证环境状态。GUI-RewardBench 上 86.9% 准确率，RL 训练 GUI Agent 达 34.0% OSWorld 成功率 |
| 3 | **[Messier: Cross-Benchmark Agent Corpus](https://arxiv.org/abs/2607.25891)** | 统一语料库，957,253条记录，覆盖30个基准、714个Agent、11,891个任务。发现 "function calling" 饱和、"programming" 进步最快、"enterprise workflows" 仍最具挑战 |
| 4 | **[HiSkill: Hierarchical Skill Graphs](https://arxiv.org/abs/2607.25853)** | 将交互轨迹组织为有向图层级结构，连接高层技能与可执行动作模板。在三个交互环境中超越 SOTA 基线，同时减少推理 token 消耗 |
| 5 | **[Self-Speculating Agent](https://arxiv.org/abs/2607.25816)** | 统一 Agent 与 Speculator 的单一模型，通过联合 RL 训练预测下一个工具调用。Qwen3-4B Hit@1 从 44.1→61.2，Qwen3.5-4B 从 48.9→66.3 |
| 6 | **[AgentToolMO: Cross-Vendor Agent Tool Trust](https://arxiv.org/abs/2607.25914)** | 3GPP NRM 信息模型，用于跨厂商 Agent 工具信任管理。形式化信任状态机 + 阻尼级联传播，在现有 3GPP 管理基础设施内运行 |

### 🔒 AI 安全与对齐

| # | 论文 | 核心贡献 |
|---|------|----------|
| 7 | **[Falling Behind Drives Unsafe Dev](https://arxiv.org/abs/2607.26034)** | 行为实验表明 AI 不安全开发源于竞争压力和"落后恐惧"，而非风险偏好。提出减少竞争压力、促进合作的政策建议 |
| 8 | **[SHarD: Secure Harness Distribution](https://arxiv.org/abs/2607.25890)** | 通过自定义 Agent Harness 分发安全控制（OS沙箱、技能扫描、工具限制），单命令安装，100% 安全评分，与商业 Agent 直接安装等效 |

### 🧠 LLM 推理与部署

| # | 论文 | 核心贡献 |
|---|------|----------|
| 9 | **[Penelope: Localized Latent Recurrence](https://arxiv.org/abs/2607.25915)** | 将循环计算定位到选定解码器区间，通过渐进 CoT-to-latent 课程将可见推理转为内部循环路径。竞争性精度同时降低推理延迟 |
| 10 | **[dtControl2+ε](https://arxiv.org/abs/2607.25925)** | MDP 控制器决策树可解释性，允许 ε-最优性换取可解释性。生成比 SOTA 小几个数量级的决策树，FMCAD26 接收 |
| 11 | **[Runtime Uncertainty Monitoring for MAS](https://arxiv.org/abs/2607.25877)** | 使用贝叶斯网络和 token-level log-probability 量化 LLM 多Agent系统的不确定性传播，应用于精算风险建模 |

### 🌐 多模态与基础模型

| # | 论文 | 核心贡献 |
|---|------|----------|
| 12 | **[CHARM: Multimodal Graph Foundation Model](https://arxiv.org/abs/2607.26023)** | 层次化上下文建模的多模态图基础模型，零样本迁移。将领域特定节点模式映射到共享高层概念，减少对目标域监督的依赖 |
| 13 | **[ClinPRISM: Clinical Time Series QA](https://arxiv.org/abs/2607.25947)** | 4B 参数 LLM 骨干，仅16个时间序列 token，0.15秒推理延迟，在临床不规则时间序列问答上达到 SOTA |

### 🔍 AI 应用

| # | 论文 | 核心贡献 |
|---|------|----------|
| 14 | **[LLM for OR Formulation Selection](https://arxiv.org/abs/2607.25956)** | 京东多仓库库存分配：LLM 选择最优 MIP 公式。GRPO 训练使 Hit Ratio@1 从 21.45%→50.42%，超越最佳固定公式 12.57 个百分点 |
| 15 | **[DCOP for Satellite Scheduling](https://arxiv.org/abs/2607.25835)** | 大规模卫星调度分布式约束优化，结合在线学习与迭代定价，满足 99% 观测请求（基线 87%） |

### 📊 arXiv 统计
- **今日新提交：** 260 篇（cs.AI，含跨领域）
- **对比昨日：** 406 篇(7/28) → 260 篇(7/29)（-36%，周三通常较少）
- **趋势：** Agent 评估基准（DDB、IRA、Messier）成为今日焦点

---

## 🏢 行业动态摘要

### OpenAI
- **2026-07-28:** Scientific Computing in the Age of Agentic AI — 8个生命科学项目案例研究，Codex + Claude Code 组合使用，研究者角色从实现转向验证与编排
- **2026-07-27:** How AI is expanding what people do at work
- **2026-07-23:** Launching Health in ChatGPT
- **2026-07-22:** Introducing OpenAI Presence
- **2026-07-22:** Introducing the ChatGPT for small business program
- **2026-07-21:** OpenAI and Hugging Face address security incident
- **2026-07-21:** David Vélez and Robin Vince join OpenAI boards
- **2026-07-20:** Safety and alignment in an era of long-horizon models

### MCP 生态
- **TypeScript SDK v1.30.0** 稳定版发布（2026-07-28 wire 规范对齐）
- **SDK v2.0.0-beta** 首次发布，支持 MCP 2026-07-28 规范修订版
- CommonJS + ESM 双格式构建，大幅扩展 Node.js 生态兼容性
- Bearer 认证和 OAuth 发现服务的 runtime-neutral 实现

---

## 🔍 趋势洞察

1. **Agent 评估进入精细化时代**：Desktop-Delta Bench（GUI 转换理解）、IRA（交互式奖励评估）、Messier（跨基准统一语料库）三篇论文从不同维度解决 Agent 评估的盲区
2. **MCP v2.0.0-beta 是生态里程碑**：首次 beta 发布，支持 2026-07-28 规范修订版，CommonJS 支持扩展生态
3. **Agent 效率优化新范式**：Self-Speculating Agent 通过联合 RL 实现工具调用预测，HiSkill 通过层级技能图减少 token 消耗
4. **AI 安全从理论走向工程实践**：SHarD 证明安全控制可通过 Harness 单命令分发；Falling Behind 实验揭示竞争压力是安全风险的根源
5. **LLM 推理效率持续突破**：Penelope 的局部循环推理、dtControl2+ε 的可解释性-最优性权衡
6. **科学计算 Agent 化**：OpenAI 报告展示 Agent 在生命科学领域的实际应用，研究者角色从实现转向验证
7. **多模态图学习**：CHARM 提出多模态图基础模型零样本迁移方法

---

## 📌 待跟踪事项

- [ ] MCP SDK v2.0.0 正式版发布时间
- [ ] OpenAI Scientific Computing 报告中 Agent 项目的后续进展
- [ ] Desktop-Delta Bench 开源代码与评测框架
- [ ] Messier 语料库的定期更新与 Agent 排名
- [ ] Self-Speculating Agent 在更多 Agent 框架中的集成
- [ ] HiSkill 层级技能图与 MCP 工具生态的结合
- [ ] SHarD 安全 Harness 的企业级部署案例
- [ ] Penelope 局部循环推理的实际部署性能

---

*Report by NightOps Scout Agent | Next run: 2026-07-30 21:30 CST*
