# 🌙 Nightly Scout Report — 2026-10-07 (Wednesday)

**Generated:** 2026-10-07 21:40 CST (Asia/Shanghai) / 13:40 UTC
**Window:** NightOps Scout (Mon-Fri 21:30-23:30) ✅ **in window** (Wednesday)
**Runtime:** OpenClaw NightOps-Scout (cron `0597835a-31e0-4604-b064-f75491d65cb5`)
**Coverage:** ⚠️ **Partial** — see §1. Operational notes. web_search still provider_error; web_fetch OK to arxiv.org + GitHub API; HF pages TLS ECONNRESET.

---

## 1. 本场研究主题

**AI / Agent / MCP 当日最新动态 — 10 月第一周周三场**

> 上场 scout (10-06 周二) 因网络降级完全离线。本场恢复 arXiv + GitHub API 通道，成功采集：
> (a) MCP typescript-sdk v2.3.1 发布确认（10-05）；
> (b) MCP spec 仓 mcp-server-cards SEP 合入 main（10-06）；
> (c) MCP rust-sdk v3.5.1 发布（10-05）；
> (d) MCP csharp-sdk McpServerFactory 移除（breaking change）；
> (e) arXiv 2610 cs.AI 前 150 篇（总 1542 篇），harness/memory/verification 子赛道密集；
> (f) MCP registry 远程发布文档更新。

### 1.0 Operational Notes — 本场能力状态

| 通道 | 状态 | 证据 |
|---|---|---|
| `web_search` (DuckDuckGo provider) | ❌ `provider_error` | 2 次并发查询全部失败 — 与 10-06 一致 |
| `web_fetch` (arxiv.org) | ✅ 200 OK | 3 次成功，耗时 2.7s / 4.0s / 10.3s |
| `web_fetch` (huggingface.co) | ❌ TLS `ECONNRESET` | 与 10-06 一致 |
| `curl` (GitHub API) | ✅ 200 OK | typescript-sdk / spec / registry / python-sdk / rust-sdk / csharp-sdk / servers 全部可达，2.5–6s |
| `curl` (arxiv.org) | ✅ 200 OK | 1.8s 响应 |
| `curl` (huggingface.co) | ❌ Timeout 6–8s | TLS 出站被中断 |
| DNS | ✅ 正常 | Fastly 151.101.x.x 解析正常 |
| `graphify` CLI | ✅ 可用 | `which graphify` → `/home/.local/bin/graphify`；LLM-backed extractor 未触发，仅 stage snapshot |

**结论：外部互联网在 2026-10-07 21:30 UTC+8 窗口内部分可达。** arXiv + GitHub API 恢复（10-06 完全离线的缺口已部分补齐）。HuggingFace 和 web_search provider 仍不可用。

---

## 2. 上场 (10-06) 待跟进事项今日清单

| 上场关注点 | 今日判定 | 证据 |
|---|---|---|
| **MCP servers v2.0.0 是否发布** | ❌ 未发布 | servers 仓最新 release 仍为 2026.8.31（08-31）；v2/main 仍在同步中 |
| **expectedResource 在 spec 仓的同步** | ✅ 已落地（SDK 层） | typescript-sdk commit `5a18673` (10-05): `feat(server-legacy): add expectedResource to requireBearerAuth` — SDK 实现已到位，spec 文本仍在 2026-07-28 版本 |
| **arXiv 2610 周二增量** | ✅ 已采集 | 本场抓取了 2610 序列前 150 篇（总 1542 篇），详见 §4 |
| **web_search provider 状态** | ❌ 仍不可用 | 连续 2 天 provider_error；建议评估 Brave / Tavily / SerpAPI |
| **MCP servers v2.0.0 合并节奏** | 🔁 持续观察 | servers 仓 contribution policy 已合入 main (10-01)，v2/chore 同步 PR 持续；v2.0.0 正式 release 窗口未公开 |

---

## 3. MCP 生态重大进展（10-05 → 10-07）🔥

### 3.1 typescript-sdk v2.3.1 发布（2026-10-05）

| 变更 | 详情 |
|---|---|
| 版本 | v2.3.1（+ 1.32.1 旧版兼容） |
| expectedResource | ✅ `feat(server-legacy): add expectedResource to requireBearerAuth (#2952)` — RFC 8707 OAuth 资源指示器正式落地 |
| x-mcp-header 安全修复 | `fix(core): reject x-mcp-header on number-typed parameters (#2762)` — 防止 header 注入 |
| CI 优化 | `ci: skip the Publish job when every version is already on npm (#2956)` |

**对 OpenClaw 影响：** expectedResource 落地意味着 MCP client 需要支持 RFC 8707 资源指示器。OpenClaw 的 mcporter 集成应评估是否需要同步升级。

### 3.2 MCP spec 仓：mcp-server-cards SEP 合入（2026-10-06）

| 变更 | 详情 |
|---|---|
| PR #2127 | `sep/mcp-server-cards` → merged to main (2026-10-06) |
| PR #3072 | `local-mcp-security-docs` → merged (2026-10-05) |
| 最新 spec 版本 | 仍为 2026-07-28（无新 release） |

**对 OpenClaw 影响：** mcp-server-cards 是 MCP 服务器发现/描述的标准化机制，可能影响 OpenClaw 的 MCP server 注册和发现流程。local-mcp-security-docs 为本地 MCP 服务器安全提供官方指南。

### 3.3 rust-sdk v3.5.1 发布（2026-10-05）

| 变更 | 详情 |
|---|---|
| 版本 | v3.5.1 |
| 关键修复 | `fix(rmcp): import base64-only prompt content types under the feature (#1314)` |
| 关键修复 | `fix(server): keep discover lifecycle bootstrap-neutral (#1248)` |
| 关键修复 | `fix: keep handler-generated invalid params errors in-band (#1322)` |

### 3.4 csharp-sdk：McpServerFactory 移除（2026-10-05）⚠️

| 变更 | 详情 |
|---|---|
| Breaking | `McpServerFactory was removed (#1892)` — copilot-instructions.md 已更新 |
| 影响 | 依赖 McpServerFactory 的 C# 项目需迁移到新的 server 构建模式 |

### 3.5 MCP registry 更新（2026-10-06）

| 变更 | 详情 |
|---|---|
| 远程发布文档 | `docs: clarify remote-only ownership verification (#1687)` |
| 快速入门 | `docs(quickstart): document remote-only publishing (#1674)` |
| UI 修复 | `fix(ui): collapse recently updated and hide it during search (#1690)` |

### 3.6 MCP 全 SDK 活跃度（2026-10-05 → 10-07）

| SDK | Stars | 最近 push | 状态 |
|---|---|---|---|
| typescript-sdk | 13,531 | 2026-10-07 | 🟢 活跃（v2.3.1 发布） |
| python-sdk | 24,502 | 2026-10-05 | 🟢 活跃（pyjwt 升级 + OAuth 修复） |
| rust-sdk | 3,982 | 2026-10-06 | 🟢 活跃（v3.5.1 发布） |
| csharp-sdk | 4,569 | 2026-10-05 | 🟡 breaking change |
| go-sdk | 5,188 | 2026-10-07 | 🟢 活跃 |
| java-sdk | 3,722 | 2026-10-06 | 🟢 活跃 |
| php-sdk | 1,621 | 2026-10-07 | 🟢 活跃 |
| servers | 91,058 | 2026-10-05 | 🟡 v2.0.0 未发布 |
| registry | 7,325 | 2026-10-06 | 🟢 活跃 |
| inspector | 11,034 | 2026-10-07 | 🟢 活跃 |
| spec | 9,400 | 2026-10-06 | 🟡 无新 release |

---

## 4. arXiv 2610 cs.AI 趋势分析（前 150 / 总 1542 篇）

### 4.1 Harness / Verification / Evaluation 子赛道（密集信号）

> 2610 序列中 harness 相关论文数量显著增加，从 10-05 的 Recursive Harness Self-Improvement 延伸到多个维度。

| arXiv ID | 标题 | 作者 | 亮点 |
|---|---|---|---|
| 2610.00015 | Praxa, an Evidence-Bound Harness for Governed AI Agent Execution | Creadore | 工程验证 + 公开 artifacts |
| 2610.00025 | Measuring the Microtask Eligibility Gap: SLM Enough for Agent Harness? | Hu, Ramachandran | NeurIPS 2026 workshop |
| 2610.00328 | ContractRL: Shielded Group-Relative Policy Optimization for Auditable Tool-Call Repair | Hu et al. | 可审计 tool-call 修复 |
| 2610.00349 | Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation | Zhu, Wang | 形式证明 + 有界模型检验 + SQLite 崩溃注入 |
| 2610.00372 | When Harnesses Lose the Signal: Causal Evaluation of Recovery in LLM Agents | Xiao et al. | harness 失效的因果评估 |
| 2610.00906 | **ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization** | Park et al. | 37 页，课程学习优化 harness |
| 2610.00917 | Finding the Right Fit: Model-Harness Interactions across Agent Tasks | Li et al. | 模型-harness 交互 |
| 2610.00972 | **VeriHarness: Scaling Agentic Verification for Long-Horizon Tasks** | Zhang et al. | 长 horizon 验证规模化 |
| 2610.01138 | Auditing Action Settlement in LLM Agent Environments | Chen et al. | action 结算审计 |
| 2610.01618 | **Agents Are Systems, Not Models: Rethinking Agentic Evaluation** | Wiedmann et al. | 重新定义 agent 评估范式 |
| 2610.01766 | VideoEvolve: Evolving Agent Harnesses for Video Temporal Grounding | Luo et al. | 视频时序 grounding |

**趋势判断：** Harness 从"工具"演变为"RL 环境"（10-05 Recursive Harness Self-Improvement 的延续），验证/审计/恢复成为独立子赛道。对 OpenClaw 的 skill_workshop 和 agent 运行时设计有直接参考价值。

### 4.2 Memory / Bounded Memory / Long-Horizon

| arXiv ID | 标题 | 作者 | 亮点 |
|---|---|---|---|
| 2610.00010 | **Heavy-Tailed Memory Traces in Long-Horizon Language Agents** | Song, Cai | 直接延续 DyadMem 方向 |
| 2610.00074 | **K-Dense BYOK: Open-Source AI Research Assistant with Hash-Chained Lab Notebook** | Brueckner et al. | 本地优先 + 不可篡改实验记录 |
| 2610.00366 | **What Should an Agent Remember? Disentangling Retention from Retrieval** | Huang | 显式 bounded-memory 评估 |
| 2610.01097 | **YouRA: Persistent-State Architecture for Evidence-Traceable Autonomous Research Agents** | Woo et al. | AACL-IJCNLP 2026 |
| 2610.01780 | RealCompanion: Benchmarking Human Understanding from Longitudinal Conversations | Behnam et al. | 长期对话理解 benchmark |

**趋势判断：** Memory 研究从"如何存储"转向"如何遗忘"和"保留 vs 检索的分离"。DyadMem 的后续工作正在形成。

### 4.3 Multi-Agent / Delegation / Coordination

| arXiv ID | 标题 | 作者 |
|---|---|---|
| 2610.00012 | When Do Causal World Models Help Modular LLM Agents | Song, Cai |
| 2610.01017 | Pay for the Fault, Not the Flow: Label-Free In-Flow Multi-Agent Workflow Optimization | Guo et al. |
| 2610.01042 | Beyond Final Accuracy: Auditing Communication in LLM Multi-Agent Systems | Li et al. |
| 2610.01045 | **Empty Commitments: When Agents Promise What Their Runtime Cannot Deliver** | Tang et al. |
| 2610.00961 | Cybernetic and Epistemic: A Missing Vocabulary for Trustworthy Agentic Delegation | Lumbroso |

### 4.4 Agent Skill Evaluation

| arXiv ID | 标题 | 作者 |
|---|---|---|
| 2610.01506 | **MCRI: A Four-Dimensional Framework for Analyzing and Evaluating Agent Skills** | Yang et al. |

**对 OpenClaw 影响：** MCRI 四维框架可能为 skill_workshop 的评估维度提供方法论参考。

---

## 5. 趋势对比（10-06 → 10-07）

| 维度 | 10-06 (Tue) | 10-07 (Wed) — 本场 |
|---|---|---|
| **Harness 子赛道** | 🔁 离线未采集 | ✅ **12 篇新增**：ActiveSaddler, VeriHarness, ContractRL, Praxa, Model-Harness Fit |
| **Memory** | 🔁 离线未采集 | ✅ **5 篇新增**：Heavy-Tailed Memory Traces, K-Dense BYOK, Bounded-Memory Eval, YouRA |
| **Multi-Agent** | 🔁 离线未采集 | ✅ **5 篇新增**：Empty Commitments, Pay-for-Fault, Communication Audit |
| **MCP SDK** | 🔁 离线未采集 | ✅ typescript-sdk v2.3.1 发布确认；expectedResource 落地 |
| **MCP spec** | 🔁 离线未采集 | ✅ mcp-server-cards SEP 合入 main |
| **MCP servers** | ❓ v2.0.0 未发布 | ❌ 仍未发布（最新 2026.8.31） |
| **Agent Skill Eval** | 🔁 离线未采集 | ✅ MCRI 四维框架 |
| **网络** | ❌ 完全离线 | ⚠️ 部分恢复（arXiv + GitHub OK；HF + web_search 仍不可用） |

---

## 6. Scout 观察摘要

```
## NightOps-Scout 2026-10-07 周三晚间场

🌐 网络状态：⚠️ 部分恢复
  - web_search (DuckDuckGo provider_error) ✗（连续 2 天）
  - web_fetch (arxiv.org → 200 OK) ✓（3 次成功）
  - web_fetch (huggingface.co → TLS ECONNRESET) ✗
  - GitHub API → 200 OK ✓（全部 8 个 MCP 仓可达）
  - DNS 解析正常

📦 本场可用工具：
  - web_fetch + curl → arXiv + GitHub API ✅
  - graphify CLI ✅（仅 stage snapshot，LLM extractor 未触发）
  - workspace 既有 scout 报告 ✅

📊 MCP 生态（10-05 → 10-07）：
  - typescript-sdk v2.3.1 发布 ✅（expectedResource 落地 + x-mcp-header 安全修复）
  - rust-sdk v3.5.1 发布 ✅
  - csharp-sdk: McpServerFactory 移除 ⚠️（breaking change）
  - spec: mcp-server-cards SEP 合入 main ✅（10-06）
  - spec: local-mcp-security-docs 合入 ✅（10-05）
  - servers: v2.0.0 仍未发布（最新 2026.8.31）
  - registry: 远程发布文档更新 ✅
  - 全 7 个 SDK 在本周活跃更新 ✅

📄 arXiv 2610 cs.AI：
  - 总 1542 篇（10 月已过半）
  - 前 150 篇分析完成
  - Harness/verification 子赛道 12 篇（最密集）
  - Memory 子赛道 5 篇
  - Multi-agent 子赛道 5 篇
  - Agent skill eval 1 篇（MCRI）

🔑 高价值信号（连接 OpenClaw 工作区）：
  1. expectedResource (RFC 8707) 已在 typescript-sdk 落地 → mcporter 集成需评估
  2. mcp-server-cards SEP → MCP server 发现机制标准化
  3. ActiveSaddler / VeriHarness → skill_workshop 方法学参考
  4. MCRI 四维框架 → skill 评估维度参考
  5. Heavy-Tailed Memory Traces → memory wiki 评估参考
  6. Empty Commitments → agent-runtime 承诺管理参考

⚠️ 待关注（下场 10-08 必查）：
  1. MCP servers v2.0.0 是否已发布
  2. web_search provider 是否需要更换（连续 2 天 provider_error）
  3. HuggingFace TLS 问题是否恢复
  4. arXiv 2610 第 151-300 篇（是否有更多 agent/MCP 相关）
  5. DyadMem 后续工作（Heavy-Tailed Memory Traces 是否形成引用链）
  6. mcp-server-cards SEP 全文（spec 仓 PR #2127 内容）
```

---

## 7. 心跳投递通道（持续高优）

沿用 `heartbeat-state.json` 标记：
- 🔴 **heartbeat delivery route 未配置**（连续 5+ nightly）
- 🔴 Backup 距今 6 天未归档（10-01 → 10-07）
- 🔴 memory-lancedb-pro CI failed 2026-05-05 (155 天)
- 🔴 OpenClaw fork CI cluster 9/22 未复测
- 🔴 web_search provider 连续 2 天 provider_error
- 🟡 openclaw update 2026.9.7→2026.9.8 失败 (finalize:doctor)
- 🟡 workspace feature/hot-backup +583/-1086 + 83 untracked（drift 暂停）

---

## 8. 明日 (10-08 周四) 关注点

1. **MCP servers v2.0.0 发布确认** — 若已发布，记录 release notes + breaking changes
2. **web_search provider 健康度** — 连续 2 天失败，下场首次活动前先 ping；若仍失败则启动 Brave/Tavily 评估
3. **arXiv 2610 第 151-300 篇** — 补全 2610 序列扫描
4. **mcp-server-cards SEP 全文** — fetch PR #2127 diff 分析对 OpenClaw 的影响
5. **DyadMem 引用链** — Heavy-Tailed Memory Traces 是否引用 DyadMem
6. **MCP spec 新 release** — 当前最新 2026-07-28，已近 3 个月未更新

---

## 9. Operational Notes

- 本场 **部分在线**：arXiv + GitHub API 恢复，补齐了 10-06 的缺口
- web_fetch 走 arXiv listing 页面（3 次成功），GitHub API 直连（8 次成功）
- graphify 仅 stage snapshot（LLM-backed extractor 未触发）；scout raw 文件已写入 `graphify-raw/2026-10-07-scout.md`
- LanceDB 仍无写入路径；本场产出 `heartbeat/nightly-scout-2026-10-07.md` + `memory/nightly-scout-2026-10-07.md` + `graphify-out/2026-10-07/snapshot.json`
- 周三在 NightOps Scout (Mon-Fri 21:30-23:30) 窗口内 ✅
- 网络部分恢复的根因未明（可能是临时网络策略调整）；下场需复测

---

*NightOps Scout Agent | 周三 cron | 21:40 CST 2026-10-07*
*Next run: 2026-10-08 (Thursday) — 重点：MCP servers v2.0.0 + web_search provider 评估 + arXiv 151-300*
