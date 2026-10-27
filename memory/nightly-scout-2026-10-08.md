# 🛰️ NightOps Scout — 2026-10-08 (Thursday)

> Companion memory entry for `heartbeat/nightly-scout-2026-10-08.md`. Compact, machine-scannable, links to the long report and graphify snapshot.

**Run window:** Thu 2026-10-08 21:30–21:38 CST (Asia/Shanghai)  
**Mode:** standard-weekday (Mon-Fri 21:30-23:30)  
**Coverage:** ⚠️ partial — arXiv 200/200; GitHub 3/12 SDKs (rate-limited IP 23.142.200.185); web_search 3-day provider_error  
**Source files:**
- Report: `heartbeat/nightly-scout-2026-10-08.md`
- Graphify: `graphify-out/2026-10-08/snapshot.json` (226 nodes, 217 edges)

---

## 1. Operational — Service Status (visual)

| Channel | Status | Evidence |
|---|---|---|
| arXiv API | 🟢 200 OK | 200 cat:cs.AI papers (2610.09146 → 2610.10538) |
| GitHub API (initial) | 🟢 partial | spec/go-sdk/java-sdk 3/12 仓 OK |
| GitHub API (later) | 🔴 rate-limited | IP 23.142.200.185 — 60 req/h, 9 仓阻断 |
| `web_search` (DuckDuckGo) | 🔴 provider_error | **连续 3 天** 失败 |
| HuggingFace web_fetch | 🟡 unknown | 本场未测试 |
| `graphify` CLI | 🟢 OK | snapshot.json stage 完成 |
| DNS / outbound | 🟢 OK | 无 TLS 故障 |
| LanceDB write | 🟡 n/a | 无写入路径（沿用） |

---

## 2. Key signals (curated, priority order)

### 2.1 ⚠️ Critical — OpenClaw security

- **arXiv 2610.09264 — Package Hallucination Attacks on Coding Agents through Prompt Injection in Rule Files** (Yupu Wang, Zhengyuan Jiang et al., 2026-10-07). 
  - **攻击面**：通过 `AGENTS.md` / `.cursorrules` 注入触发 package hallucination。
  - **直接命中**：OpenClaw 的 skills/AGENTS.md 体系。
  - **行动项**：skill_workshop 发布流程加 prompt injection 审查；建议 security audit 触发。

### 2.2 🟢 High value — Agent / Memory / MCP architecture

- **arXiv 2610.10071 — HGP: on-device personalized agent memory via hybrid graph storage** (Ran Zhou, Xueming Han et al., 2026-10-07). 端侧 + 混合图 + 个性化。→ OpenClaw 本地 agent runtime 设计参考。
- **arXiv 2610.09590 — Learning Situation-Conditioned Thinking Policies for Long-Term LLM Agents** (Hong Su, 2026-10-07). 长期 agent 思考策略学习。→ memory wiki 长期 agent 思考参考。
- **arXiv 2610.09832 — SkillForge: Co-Evolving Skills and Agents via Dynamic Skill Lifecycles** (Yuyao Ge, Yiwei Wang et al., 2026-10-07). 技能与代理协同进化 + 动态生命周期。→ skill_workshop 协同进化模式。
- **arXiv 2610.10126 — Know the Shape, Find the Fault: Topology-Conditioned Diagnosis of Multi-Agent LLM Failures** (Xinwen Liu et al., 2026-10-07). 通信拓扑驱动多 agent 失败诊断。→ subagent 调试工具。
- **arXiv 2610.10507 — RECAST: Learning to Compute the Right Context through Adaptive Evidence Routing** (Yilun Hao et al., 2026-10-07). 自适应证据路由（区别于 fixed similarity RAG）。→ memory wiki 检索层借鉴。
- **arXiv 2610.09624 — How Do Agentic LLMs Decide to Call Tools? A Tool-Call Vector Shaped by Suppression** (Xijie Gong et al., 2026-10-07). 工具调用向量被"抑制"塑形。→ mcporter 集成可加监控。
- **arXiv 2610.09159 — SpecGuard: Proving a Task Is Broken Before the Agent Cheats** (Param Biyani, Krishnamurthy Dvijotham, 2026-10-06). 任务 spec 错配前置检测。→ agent 任务验证。
- **arXiv 2610.09348 — Relevance Is Not Sufficiency: What Actually Closes the Evidence Gap in Long-Term Memory QA**. 证据差距。→ memory retrieval 评估维度。
- **arXiv 2610.09215 — AGAR: a reinforcement learning substrate for LLM program evolution**. RL 程序进化。→ skill 进化参考。

### 2.3 🟡 MCP ecosystem (10-07 → 10-08)

- **spec 仓 PR #3418 `docs/inspector-2450-security-mcpdo` 合入** (10-08 12:57 UTC, commit `c518f7a`)。mcpdo 是 MCP 推荐的"多客户端桥接 + 安全审计" CLI；其教程视频被链接进主仓 docs。→ OpenClaw MCP inspector/debug 集成可参考。
- **go-sdk `8dd5d6a` auth: check token expiry before required scopes** (10-07)。RFC 6749 §5.1 合规性修复。→ OpenClaw mcporter 集成需对齐。
- **java-sdk `f856940` Reject non application/json POST requests #1164** (10-08)。强制 Content-Type 校验。→ Java MCP client 兼容性。
- **MCP servers v2.0.0 仍未发布**（连续第 4 场观察）。最新 release 仍 2026.8.31。
- **GitHub API rate-limit** 来自本机出口 IP 23.142.200.185（未认证，60 req/h）。→ 长期建议配置 GitHub PAT 至 OpenClaw secrets。

### 2.4 📈 Trends

- **Harness/Eval 子赛道 78 篇 / 39%** — 主导赛道。10-05 Recursive Harness → 10-07 ActiveSaddler/VeriHarness → 10-08 扩展到音乐（MIRA）/ 气候（SciExam ENSO）/ 编码（Coding-Agent Bench）/ 客户反馈。
- **RL Post-Train 22 篇** — RLVR 标准化；ExpDis（解耦探索/优化）7 个数学 benchmark 超 DAPO。
- **Memory 14 篇** — HGP（端侧混合图）/ Ledger 3D（HD-EPIC 29.7%→42.6%）/ VideoEvolve（记忆+检索协同进化）。
- **Safety 14 篇** — Package Hallucination（攻击 AGENTS.md）首次出现；PHRBench、SpecGuard、Adversarial Images 持续。
- **Multi-Agent 10 篇** — 拓扑驱动失败诊断首次系统化（Know the Shape, Find the Fault）。

---

## 3. Cross-references to OpenClaw

| arXiv | 关联 OpenClaw 组件 | 行动项 |
|---|---|---|
| 2610.09264 | skills/AGENTS.md 体系 | 🔴 skill_workshop 加 prompt injection 审查 |
| 2610.10071 | 本地 agent runtime / memory wiki | 🟢 端侧混合图设计参考 |
| 2610.09590 | memory wiki 长期 agent | 🟢 思考策略持久化 |
| 2610.09832 | skill_workshop | 🟢 协同进化模式 |
| 2610.10126 | subagent 调度 | 🟢 拓扑诊断工具 |
| 2610.10507 | memory wiki 检索 | 🟢 adaptive evidence routing |
| 2610.09624 | mcporter | 🟢 tool-call vector 监控 |
| 2610.09159 | agent 任务验证 | 🟢 spec 错配前置 |
| 2610.09348 | memory retrieval | 🟢 evidence gap 评估 |
| 2610.09215 | skill 进化 | 🟢 RL substrate 借鉴 |
| spec PR #3418 | MCP inspector | 🟢 mcpdo 安全模型参考 |
| go-sdk #1350 | mcporter auth | 🟢 token expiry 校验对齐 |
| java-sdk #1164 | MCP Java client | 🟡 Content-Type 兼容性 |

---

## 4. Trends comparison (week trajectory)

| Dimension | 10-05 (Mon) | 10-07 (Wed) | 10-08 (Thu) |
|---|---|---|---|
| Harness/Eval | Recursive Harness | ActiveSaddler/VeriHarness | **78 篇 / 39% 主导** |
| Memory | DyadMem | Heavy-Tailed Traces | HGP / Ledger 3D / evidence gap |
| Multi-Agent | EdgeAgent / MIRROR | Empty Commitments | Topology-Conditioned Diagnosis |
| Tool Use | 配角 | 配角 | Tool-Call Vector 机制可解释性 |
| Safety | Deny Without Disabling | 持续 | **Package Hallucination via AGENTS.md** ⭐ |
| RAG | 配角 | 配角 | RECAST 自适应证据路由 |
| Skill | Knowledge or Calculator | MCRI 4D | SkillForge 协同进化 |
| Code Agent | 配角 | 配角 | 14 篇 — IDE 真实会话分析 |
| RL Post-Train | 配角 | 配角 | 22 篇 — RLVR 标准化 |
| MCP SDK | expectedResource 落地 | rust-sdk v3.5.1 | go-sdk token + java-sdk JSON 校验 |
| MCP spec | maintainers | mcp-server-cards SEP | **PR #3418 mcpdo tutorial** |
| MCP servers | v2.0.0 准备 | 未发布 | 未发布（连续第 4 场）|

---

## 5. Open followups (carry to 10-09 Fri)

1. **🔴 MCP servers v2.0.0 发布** — 连续 4 场未发布（10-05/10-07/10-08）
2. **🔴 web_search 长期方案** — Brave/Tavily 评估（连续 3 天 provider_error）
3. **🟡 GitHub API PAT 配置** — 60 req/h 限制下半场 scout 持续被阻断；建议配 PAT
4. **🟡 HF TLS 状态** — 多场未测试
5. **🟢 arXiv 2610 10539+ 增量** — 继续扫描
6. **🟢 SkillForge / HGP / SpecGuard 全文 + 代码可用性**
7. **🟢 2610.09264 Package Hallucination 防御** — skill_workshop prompt injection 审查
8. **🟢 inspector-2450-security-mcpdo 全文** — mcpdo 教程视频
9. **🟢 spec 仓 PR #2127 mcp-server-cards SEP** — 10-06 合入后细节
10. **🟢 memory wiki "evidence gap" 概念引入** — 2610.09348

---

## 6. Heartbeat priority carry-over

🔴 (continuous 6+ nightly):
- heartbeat delivery route 未配置
- Backup 7+ days stale (10-01 → 10-08)
- memory-lancedb-pro CI failed 2026-05-05 (156 days)
- OpenClaw fork CI cluster 9/22 未复测
- web_search provider 3-day provider_error

🟡 (this run + carry-over):
- GitHub API rate limit IP 23.142.200.185 — **建议配置 PAT**
- 外部网络部分降级
- openclaw update 2026.9.7→2026.9.8 finalize:doctor
- workspace feature/hot-backup +583/-1086 + 83 untracked
- MCP servers v2.0.0 连续 4 场未发布

🔴 **NEW this run**:
- OpenClaw skills/AGENTS.md 体系受 Package Hallucination 攻击（2610.09264）— skill_workshop 发布流程需加 prompt injection 审查

---

*Memory snapshot by NightOps-Scout (cron 0597835a) — Thu 2026-10-08 21:38 CST*
*Next: Fri 2026-10-09 — focus on MCP servers v2.0.0 + web_search 长期方案 + GitHub PAT + Package Hallucination 防御*
