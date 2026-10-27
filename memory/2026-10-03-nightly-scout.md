# Memory: Nightly Scout — 2026-10-03

## Headline takeaways

- **10 月 arXiv 2610 序列首批已上线**：~110 篇 10 月新号 + ~40 篇 9 月尾延续；Agent/Harness/Skill/Tool 主题占比 ~70%（vs 9 月末 ~65%），延续"agent 工程化"主题。
- **Agent 评估方法学立场形成**：`Agents Are Systems, Not Models` (2610.01618) 明确反对"评估 LLM = 评估 Agent"的混淆——可能成为该子领域的方法学立场论文。
- **Harness 自身成研究对象**：`VeriHarness` / `ActiveSaddler` / `Mid-Harness` / `Harness-Annealing` / `Keyword-Harnesses-Fail-Open` / `Mingbird` / `AutoCompact` / `VISTA` 8 篇同期 harness 论文 → harness design 已是独立 subfield。
- **Skill marketplace 路径实证**：`SkillSeek` (2609.38822) + `MCRI` (2610.01506) + `Continuous-Skill-Eval` (2610.01833) → SKILL.md 模式从单仓库走向 marketplace 已具备文献基础。
- **Memory / RAG 升为主角**：`Mem++` (2610.02002) + `Causal-Memory-Policy` (2610.02070) + `Matryoshka-RAG` (2610.01767) + `RAG-Taxonomy` (2610.01936) → 10 月首个新热点。
- **多 agent 失败诊断细化**：`Where-MAS-Fail` (2609.38761) + `Delegation-Danger-Band` (2610.00041) + `Hidden-Info-Failures` (2610.01244) + `Verifier-Leak` (2610.00126) → evidence-grounded 方法学已成形。
- **MCP 生态本周围绕"工具外延"展开**：spec 仓只有 Dependabot；typescript-sdk 引入 `CLAUDE.md` principles (PR-2938)；servers/memory 9-03 一波 8 commit 健壮性大扫除；registry 把 **mcpscore**（首个独立 MCP server 评分工具）纳入 community list。
- **MCP 官方 docs 仍未刷新**：仍 `2026-07-28`，2+ 个月没动。

## Direct connections to OpenClaw workspace

| 论文 | OpenClaw 连接 |
|---|---|
| `Delegation-Danger-Band` (2610.00041) | **中能力 subagent 过度信任继承过期状态** — 与 OpenClaw `sessions_spawn` 委派模式直接相关，**待评估**是否要在 AGENTS.md 加委派规约 |
| `Mingbird` (2610.02001) | local-first + 小开源模型 → 与 OpenClaw 本地 runtime 哲学一致 |
| `Keyword-Harnesses-Fail-Open` (2610.02142) | SLM 工具使用 fail-open 诊断 → 影响 `mcporter` 后续小模型适配 |
| `MCRI` (2610.01506) + `SkillSeek` (2609.38822) | SKILL.md / `skill_workshop` 方法学补强 → 评估是否要把 skill 检索/分类维度纳入 Workshop 流程 |
| `ScholarCatalyst` (2610.02202) | "启发性论文检索 benchmark" → 直映射 Scout 类 agent 评估 |
| `Mem++` (2610.02002) + `Causal-Memory-Policy` (2610.02070) | 非破坏性记忆 + 因果可识别 → 与 `graphify` / memory/ 当前实现对照 |
| `MCP-Memory-Server` 9-03 8-PR 大扫除 | memory server 加了 `serialize graph mutations` 防并发写 → 借鉴改造 graphify 工作流？ |

## Operational lessons (durable, for future cron runs)

- `web_search` 仍不可靠；继续用 `web_fetch` + `api.github.com` REST API（无 auth 限速可达）
- arXiv listing 用 `/list/cs.{AI,CL,MA}/recent` + `/list/cs.{AI,CL}/2610` 双路覆盖新号段 + 跨列表去重
- HN（news.ycombinator.com）仍不可达
- `graphify` 是交互式/高成本——继续 stage node/edge 列表在 `graphify-out/nightly-scout-YYYY-MM-DD.md`
- LanceDB 仍无写入路径（scout memory 落在 `heartbeat/` + `memory/` markdown）
- 周六 cron 触发 scout 不受 NightOps (Mon-Fri 21:30-23:30) 窗口限制

## Watchlist entities (carried forward + new)

**High-priority new (this run):**
- arXiv: `2610.01618`, `2610.01506`, `2610.01833`, `2610.00041`, `2610.02002`, `2610.02070`, `2610.01767`, `2610.01936`, `2610.02122`, `2610.02206`, `2609.38761`, `2609.38822`, `2610.01244`, `2610.00126`, `2609.39982`, `2610.00972`, `2610.00906`, `2610.01235`, `2610.02142`, `2610.00371`, `2610.01415`, `2610.02202`, `2610.02001`

**Continued:**
- MCP ecosystem: Conformance maintainers, mcpscore, typescript-sdk CLAUDE.md principles, MCP-Docs-2026-07-28 (still unchanged)
- Subfields: agent-evaluation, harness-engineering, agent-skill-marketplace, multi-agent-failure-diagnosis, memory-for-agents, agent-security

## Cron scheduling note

- This run was triggered by Saturday-evening cron (17:23 CST 2026-10-03) — outside the documented NightOps window (Mon-Fri 21:30-23:30).
- The cron expression should be reviewed: either the cron is misconfigured (running outside intended window), or the Mon-Fri NightOps window documentation is too narrow for actual scout cadence.
- Recommended action: update NightOps-Scout cron to align with scout's actual coverage intent (daily 21:30-23:30 including weekends), or update MEMORY.md documentation to reflect weekend exclusion.
