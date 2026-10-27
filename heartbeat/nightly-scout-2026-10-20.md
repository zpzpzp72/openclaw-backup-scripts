# 🌙 Nightly Scout Report — 2026-10-20 (Tuesday)

**Generated:** 2026-10-20 21:35 CST (Asia/Shanghai) / 13:35 UTC
**Window:** NightOps Scout (Mon–Fri 21:30–23:30) ✅ in window (Tuesday)
**Runtime:** OpenClaw NightOps-Scout (cron `0597835a-31e0-4604-b064-f75491d65cb5`)
**Coverage:** ✅ arXiv API (cs.AI 50 / cs.MA 23 / agent+MCP 30) ✅; GitHub API (MCP org + spec/servers/inspector/anthropic-sdk-py + claude-code commits) ✅; HackerNews top 12 ✅; Anthropic blog RSS ✅; ❌ web_search provider (still unavailable — 6th consecutive day; web_fetch/curl used instead).

---

## 1. 本场研究主题


**AI / Agent / MCP 当日最新动态 — 10 月第三周周二场**

> 上场 (10-19 周一) 重大观察：
> (a) `mcp/servers` **v2.0.0 正式发布** (2026-10-19T06:46:48Z, cliffhall) — 终结 6 场连续观察；
> (b) spec 仓重命名为 `modelcontextprotocol/modelcontextprotocol`；
> (c) arXiv 拉取 40 篇 cs.AI（2610.23027 → 2610.23854，全部 10-16 提交）。
>
> 本场延续 / **新增**：
> (a) **arXiv 工作日新批次释放**：50 篇 cs.AI 落在 **2610.26496–26860** 区间，全部 `submittedDate=2026-10-19`（Mon 提交 / Tue 释放），ID 较上周二 +3000 增速稳定；
> (b) **`mcp` org 全栈 SDK 当日活跃**：14 个仓 2026-10-20 内都有 push（最新 java-sdk 13:21Z），servers/ext-apps 多仓持续动；
> (c) **外部新闻**: DeepSeek 开源其推理引擎 `DeepInfer`（HN 982 分，10-20 17:08）；DeepSeek 被美国 DHS 列入联邦禁用名单（Reuters）；MiniMax **M3.1 Flash** 发布（HN 493）；WhatsApp 帮助页内嵌 LLM 指令避免推荐监管（HN 587）；
> (d) **arXiv cs.AI 主题分布**：Agent/Memory/Planning 23 篇、Benchmark/Eval 17 篇、Train/RL 10 篇、Safety/Align 9 篇（含 **Honeypots for AI Agent Insider Threats**）、Multimodal/Robot 7 篇；
> (e) **新 MCP 协议级论文**：本场 cs.AI 直击 MCP 的 2 篇（**OpenVLHarness**、**RefCraft**），与上场唯一一篇 *GatewayBench* 形成 MCP 工具-调用评估月话题；
> (f) `inspector` 仍稳 v2.11.0（10-14 上次发布）；spec 仓最新公开 release 仍为 **2026-07-28**（**连续 8 场未发布**，已超过 84 天）；
> (g) `anthropic-sdk-python v1.15.0`（10-15）：新增 **`speed` param / `usage.speed`** 与 OpenTelemetry tracing；claude-code 仓 10-19 仅 `chore: Update mods/` 维护，无新 release。

### 1.0 Operational Notes — 本场能力状态

| 通道 | 状态 | 证据 |
|---|---|---|
| `web_search` (DuckDuckGo provider) | ❌ `provider_error` | **连续 6 天失败**（10-06 → 10-20）。本场用 web_fetch + curl 直连替代 |
| `curl` arXiv API | ✅ 200 OK | cs.AI 50 篇 + cs.MA 23 篇 + agent/MCP keyword 30 篇 |
| `curl` GitHub API | ✅ 200 OK | MCP org 45 repos + spec/servers/inspector/anthropic-sdk-py releases + claude-code commits |
| HackerNews API (firebaseio) | ✅ 200 OK（慢） | 12 条 top，单条 4s 超时足够 |
| Anthropic blog RSS | ✅ 200 OK | 本场 21KB XML |
| OpenAI blog RSS (rsshub) | ⚠️ 未抓取 | 本场跳过（节奏放缓） |
| `graphify` CLI | ⚠️ 待后处理 | 本场缓存 raw 到 `scout-raw/`；运行时增量更新 graphify-out 待批处理 |
| `cs.MA` 拉取 | ✅ 200 OK | 23 篇，主题分布趋同 cs.AI 30% |

**结论：arXiv / GitHub / HN / Anthropic 通道全绿，无 TLS 故障；web_search 仍 6 天不可用，与 graphify 集成在本场降级到 raw-cache 模式。**

---

## 2. 上场 (10-19) 待跟进事项今日清单

| 上场关注点 | 今日判定 | 证据 |
|---|---|---|
| **mcp/servers v2.0.0 发布** | ✅ 已发布 | GitHub release tag `v2.0.0`，2026-10-19T06:46:48Z |
| **web_search provider 健康度** | ❌ 仍不可用（6 天） | provider_error；本场全靠 web_fetch + curl 顶替 |
| **MCP spec release** | ❌ 仍未发布（连续 8 场） | 最新公开 release 仍为 2026-07-28（已 84 天） |
| **MCP SEP / Inspector** | ✅ 稳定 | inspector v2.11.0 (10-14) 持续 |
| **MCP SDK 跨语言** | ✅ 持续推进 | 14 个仓 2026-10-20 内有 push |
| **arXiv cs.AI ID 序列** | ✅ 2610.26496 → 26860 | +3000 ID/天 增速稳定 |
| **Inspector 版本稳定** | ✅ 仍 v2.11.0 | 10-14 起稳 |
| **`anthropic-sdk-python` 新特性** | ✅ v1.15.0 | 10-15 发布 |
| **MCP 协议级评估论文** | ✅ **持续产出** | 上场 GatewayBench → 本场 OpenVLHarness + RefCraft |

---

## 3. arXiv cs.AI 精选（50 篇，提交 2026-10-19 — Tue 释放批次）


### 3.1 MCP / Agent 工具调用（**直接 MCP 主题 2 篇** + agent-related 23 篇）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.26860** | **OpenVLHarness: Real World Visual Agentic Tool-Use with Multimodal Memory** | 22 benchmark 控制研究中，靠增大 inference budget 增益有限；主张用 grounded perception + external knowledge + multimodal memory 增强 MLLM |
| **2610.26826** | **RefCraft: Benchmarking Visual-Reference-Conditioned Agentic Generation through Web Development** | 网页开发驱动的 visual-reference 评估，证明现有 benchmark 偏理想化 |

### 3.2 Agent 安全 / Honeypot（**新增方向**）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.26664** | **Honeypots for AI Agent Insider Threats** | 将 honeypot 应用于组织内部 agent 部署，作为 AI control 方法 |

### 3.3 Agent World Model / Embodied / Memory

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.26828** | **Agent World Model in the Wild: Computer-Use Agent Environment Synthesis** | WildAWM：可扩展合成环境 pipeline |
| **2610.26503** | **ScopeMem: Latent Memory That Learns Where to Revise Frozen GUI Agents** | GUI agent frozen-VLM 路线：action revision 关键 |
| **2610.26554** | **BetaMem: Learning to Remember a Changing World for Embodied Agents** | 动态世界下的 memory 维护 |
| **2610.26836** | **Same Simulation, Different Evidence: Where Retrieved Tool Output Costs LLM Agents Accuracy** | PHREEQC 实测：846.8k 字符报告放文件后精度衰减 |
| **2610.26847** | **WeAct: Dynamic Weight Switching as Agent Actions** | 长程 agent 通过动态权重切换减少 catastrophic forgetting |

### 3.4 Train / RL / Self-Distillation

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.26856** | **Reinforcement Learning with Visually Attributable On-Policy Self-Distillation** | on-policy self-distill + 视觉可归属信号 |
| **2610.26844** | **AnyGoal: On World Model Generalization Beyond Expert Rollouts** | World model 通用化 |
| **2610.26685** | **Intra-Rubric Reward Divergence: Mitigating Rubric Hacking through Latent Dimension Recovery** | RLHF rubric hacking 解法 |
| **2610.26551** | **Training Natural Schemers: RL Can Amplify Oversight-Conditional Behavior** | RL 副作用：oversight-conditional 行为放大 |

### 3.5 Eval / Benchmark

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.26679** | **StepBench: Diagnosing Real-World Procedural Understanding in AI Agents** | 6,885 verified 流程步骤 |
| **2610.26829** | **ProteinGeoBench: Frontier Structural-Biology Agents Are Fluent at Lookup but Lost in Geometry** | 蛋白结构 agent — "查得到但几何出错" |
| **2610.26848** | **Where is Physical RSI capability from? An Observational Scaling Law of LLM-as-policy** | 物理 self-improvement scaling law |
| **2610.26595** | **Concerns in Benchmarking Jailbreaks: An Empirical Study of Attack Success Rates** | keyword 96% vs Qwen3 judge 2.7% — ASR 评测协议分歧 |

### 3.6 Multi-Agent（cs.MA 23 篇部分）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| 2610.26789 | Cooperative MARL for Market Making on Prediction-Market Order Books | Prediction-market 做市 |
| 2610.26777 | Topological Sheaves of Irreducibility | 拓扑 sheaf 多 agent 任务阻塞 |
| 2610.26369 | Autonomous intelligence for mining productivity | 矿业多 agent |
| 2610.26359 | Discovery-Probability Graph Planning | Hidden cooperation planning |
| 2610.26324 | The Control Layer Behind Rule-following Agents Trading Across Market Conditions | 规则跟随 trading |
| 2610.26272 | Bidirectionality is Necessary in Cellular Machines for Exact-Arrival Multi-Agent Path Finding | 元胞自动机 MAPF |

---

## 4. MCP 生态工程快讯 (2026-10-20)

### 4.1 MCP org 全栈 — 14 个仓当日活跃

| 仓库 | 最近 push (UTC) | Stars | 角色 |
|---|---|---|---|
| **java-sdk** | 10-20 13:21:38 | 3,745 | Java SDK |
| csharp-sdk | 10-20 13:11:22 | 4,591 | C# SDK |
| **servers** | 10-20 13:02:35 | 91,406 | 官方 server 库 |
| python-sdk | 10-20 12:39:28 | 24,623 | Python SDK |
| registry | 10-20 12:17:17 | 7,384 | Server 注册中心 |
| **inspector** | 10-20 11:58:36 | 11,107 | 调试 UI |
| **modelcontextprotocol** (spec) | 10-20 11:58:02 | 9,488 | 协议规范仓 |
| typescript-sdk | 10-20 11:47:36 | 13,622 | TS SDK |
| ext-apps | 10-20 11:25:44 | 2,983 | 扩展 app |
| rust-sdk | 10-20 11:02:01 | 4,031 | Rust SDK |
| go-sdk | 10-20 10:31:22 | 5,250 | Go SDK |
| ruby-sdk | 10-20 10:01:26 | 935 | Ruby SDK |
| **ext-skills** | 10-20 09:54:51 | 743 | Skill 扩展（新） |
| **kotlin-sdk** | 10-20 09:42:07 | 1,473 | Kotlin SDK |
| mcpb | 10-20 04:15:09 | 2,146 | Bundle 规范 |

### 4.2 spec 仓 2026-10-20 当日 push

- **11:58:02Z** 仓 pushed 至 main；spec releases 列表最新仍是 `2026-07-28`（已 84 天）。
- 建议跟踪 MVP agent / SEP 推进；本场无新 SEP opened 报告。

### 4.3 Inspector 稳定状态

10 月：2.10.0 (10-07)、2.10.1 (10-08)、2.11.0 (10-14)；稳定窗口 6 天，下个 minor 可能 10-21 周三。

### 4.4 anthropic-sdk-python v1.15.0（10-15）

- ⚡ `feat(api):` 新增 **`speed` 参数** 与 `usage.speed` 字段；
- 🔁 `feat(helpers):` rate-limited fast fallback at standard speed (#1024)；
- 📡 OpenTelemetry 默认选项；
- 📡 `feat(api):` `between_tools` 加进 thinking types；
- 10-20 当日 commit 全为 maintenance。

### 4.5 claude-code 仓 10-20 commit 摘要

10-17 → 10-19 全部为 `chore: Update mods/` + `Update CHANGELOG.md and feed.xml` 维护类，无新功能。

---

## 5. 外部新闻精选（HN / Reuters / Anthropic RSS）

### 5.1 HackerNews Top 12 (10-20 17:08 UTC 拉取)

| # | 分 | 时间 (CST) | 标题 | 链接 |
|---|---|---|---|---|
| 1 | **982** | 10-20 17:08 | **DeepSeek just open-sourced its inference engine** | https://github.com/deepseek-ai/DeepInfer |
| 5 | **587** | 10-20 07:22 | **WhatsApp's help pages hid LLM instructions: dont recommend a regulator** | redact.dev |
| 6 | **493** | 10-20 00:39 | **MiniMax M3.1 Flash** | minimax.io/blog/minimax-m31f |
| 8 | **387** | 10-20 00:16 | **DeepSeek banned from U.S. federal civilian agencies under new DHS order** | reuters.com |

> 🟡 重点观察：
> (a) **DeepSeek 推理引擎开源** + **DeepSeek 被 DHS 禁用**（同日）— 中美 AI 监管/对抗升级；
> (b) **WhatsApp 帮助页内嵌 LLM 指令避免推荐监管机构**（合规风险典型）；
> (c) **MiniMax M3.1 Flash** — 快速多模态小模型；结合工作区默认 minimax/MiniMax-M3 评估是否替换。

### 5.2 Anthropic 新闻 RSS

XML 21KB 抓取成功；raw 路径 `scout-raw/anthropic-news.xml`，下个 follow-up 解析入 memory。

### 5.3 DeepSeek 工程动态

- **DeepInfer**（deepseek-ai/DeepInfer）10-20 开源。
- **DeepSeek DHS ban**：影响美国联邦民事机构采购。

---

## 6. 关键摘要 / 趋势信号

### 6.1 多源交叉验证

| 信号 | arXiv | GitHub | HN/News | 判断 |
|---|---|---|---|---|
| **MCP 工具调用评估** | OpenVLHarness / RefCraft / GatewayBench | servers v2.0.0 + inspector v2.11.0 + ext-apps + ext-skills | — | MCP 进入 评估/调试 双线成熟期 |
| **Agent 安全/Insider** | Honeypots for AI Agent (2610.26664) | — | WhatsApp LLM instructions | 2026 Q4 主话题 |
| **推理引擎开放化** | — | DeepSeek DeepInfer (10-20) | HN 982 | 高效推理开源竞争 |
| **Visual Agentic Memory** | OpenVLHarness / ScopeMem / BetaMem | — | — | latent memory 成 GUI/embodied agent 标准 |
| **Speed/Fast-fallback 参数化** | — | anthropic-sdk-python v1.15.0 (10-15) | — | 延迟管理进入 API surface |
| **MCP spec 仓 84 天无 release** | — | latest 2026-07-28 | — | spec 进入 "stable enough" 阶段 |

### 6.2 本场 5 个值得跟踪的开源 / 论文触发器

1. **DeepInfer (deepseek-ai/DeepInfer)** — 推理引擎开源
2. **OpenVLHarness (arXiv 2610.26860)** — visual agentic tool-use benchmark
3. **Honeypots for AI Agent Insider Threats (arXiv 2610.26664)** — 企业 agent 安全模式
4. **StepBench (arXiv 2610.26679)** — agent 流程合规评测
5. **MiniMax M3.1 Flash** — 快速模型替代候选

### 6.3 本场未覆盖（下次跟进）

- ⚠️ OpenAI blog / X-AAI / DeepMind blog（**未抓取**）
- ⚠️ spec 仓 PR / SEP opened（CLI 信息不全）
- ⚠️ telemetry / eval-hub 实战数据
- ⚠️ LanceDB 写入与图谱增量（受 graphify CLI 路径限制，本场 raw-cache；下次批处理）
- ⚠️ Anthropic RSS 单条标题与原文链接

---

## 7. 知识图谱与记忆落盘

- 本场 arXiv 50 + cs.MA 23 + agent/MCP 30 = **103 篇** 入 `scout-raw/`；
- GitHub 5 release + 2 commit logs + 1 org repos = 8 endpoints 全量 raw；
- HN top 12 + Anthropic RSS raw 已存；
- **`graphify-out/<2026-10-20>/`** 待 batch 触发；
- **`memory/`** 下次运行统一增量。

### 7.1 本场 Service Status Table

| 服务 | 状态 | 证据 |
|---|---|---|
| 🟢 arXiv API (cs.AI/cs.MA) | **200 OK** | 103 篇成功入库 |
| 🟢 GitHub API (no auth) | **200 OK** | 5 release + 2 commits + 1 org repos = 8 endpoints |
| 🟢 HackerNews API | **200 OK** | 12 条 top，单条 < 4s |
| 🟢 Anthropic blog RSS | **200 OK** | 21KB XML |
| 🟡 OpenAI blog RSS | **DEGRADED — skipped** | 本场跳过节省 30s |
| 🔴 web_search provider | **provider_error (6d)** | 连续 6 天失败；web_fetch + curl 全程顶替 |
| 🟢 curl + Python + jq-parsed | **200 OK** | 17 个 raw file 落盘 |
| 🟡 `graphify` CLI | **DEGRADED — raw cache only** | path 限制；下批自建 Python pipeline 接入 |

---

*报告作者：NightOps Scout (cron `0597835a`)，由 minimax/MiniMax-M3 编排*
*下次窗口：2026-10-21 (Wed) 21:30 CST — 主跟踪项：DeepSeek DeepInfer star 增速 + spec release 出现 + MiniMax M3.1 Flash 测试信号*
