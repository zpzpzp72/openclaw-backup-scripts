# Knowledge Graph — Nightly Scout 2026-10-03

> Staged input for the `graphify` skill. Run `graphify` against `heartbeat/nightly-scout-2026-10-03.md` to produce HTML/JSON/audit report.

## Nodes

### arXiv papers (October 2026, first batch — 2610.xxxxx)

#### Agent evaluation & methodology
- `Agents-Are-Systems` — 2610.01618, "Agents Are Systems, Not Models: Rethinking Agentic Evaluation"
- `MCRI` — 2610.01506, "MCRI: A Four-Dimensional Framework for Analyzing and Evaluating Agent Skills"
- `Continuous-Skill-Eval` — 2610.01833, "Continuous Process-Level Evaluation for Evolving Enterprise AI Agent Skills"
- `Argo-Bench` — 2610.02122, "Argo-Bench: Evaluating Data Agents on Enterprise-Scale Workflows"
- `KaliBench` — 2610.02206, cybersecurity tool-use benchmark, runtime-free verifiable rewards
- `WebArena-Audit` — 2610.01491, "Auditing Web Agent Evaluation on WebArena-Lite"
- `ScholarCatalyst` — 2610.02202, paper-inspiration retrieval benchmark

#### Harness design
- `VeriHarness` — 2610.00972, scaling agentic verification
- `ActiveSaddler` — 2610.00906, automated curriculum for harness optimization
- `Mid-Harness` — 2609.39982, model↔harness intermediate layer
- `Harness-Annealing` — 2610.01235, learning to act with less external control
- `Keyword-Harnesses-Fail-Open` — 2610.02142, SLM tool-use safety diagnostic
- `Mingbird` — 2610.02001, local-first agent harness for small open models
- `AutoCompact` — 2610.02163, learning when to compact context in coding agents
- `VISTA` — 2610.02200, visual harness for interactive world reasoning

#### Memory & RAG
- `MemPP` — 2610.02002, "Mem++" non-destructive memory for long-term organizational agents
- `Causal-Memory-Policy` — 2610.02070, identifiable memory utility via causal intervention
- `Matryoshka-RAG` — 2610.01767, hierarchical RAG for multi-hop QA
- `RAG-Taxonomy` — 2610.01936, four-axis RAG taxonomy
- `Alignment-Memory-Asymptotics` — 2610.01828, asymptotics of LM alignment with memory
- `RefCon` — 2609.39143, iterative refinement + contrastive memory

#### Multi-agent failure diagnosis
- `Where-MAS-Fail` — 2609.38761, evidence-grounded diagnosis of collective mechanisms
- `CollabFlow` — 2609.38662, recursive self-improvement of agent collaboration
- `Solo-To-Social` — 2609.38516, recursive social improvement in LLMs
- `Delegation-Danger-Band` — 2610.00041, mid-cap sub-agents over-trust inherited stale state
- `Hidden-Info-Failures` — 2610.01244, right answers wrong states in multi-agent
- `Verifier-Leak` — 2610.00126, verifier leaks answer in closed-loop debugging
- `Bayesian-Council` — 2610.02005, Bayesian dialectical argumentation for multi-LLM councils
- `Global-Coherence` — 2610.02036, local-to-global semantic foundation for MAS
- `Heterogeneity-Team-Selection` — 2609.38274, measuring heterogeneity for LLM team selection
- `Deny-Without-Disabling` — 2610.00371, authorization-paired evaluation & control

#### Skill marketplace & self-improvement
- `SkillSeek` — 2609.38822, agent skill retrieval at marketplace scale
- `GUI-Component-Routing` — 2610.01787, component routing for self-improving GUI agents
- `My-FAULT` — 2610.01161, self-diagnosis as credit assignment

#### Long-horizon / belief
- `Beyond-Memory-Belief` — 2610.01415, explicit belief states for long-horizon agents
- `Decision-Titan` — 2610.01513, test-time training for long-term memory in offline RL
- `Epistemic-Action` — 2610.00511, epistemic action before agent decisions

#### Applications
- `Mimir-Irrigation` — 2610.02038, physics-grounded LLM agents for irrigation
- `Health-Checkup-MAS` — 2610.01451, multi-agent LLM health checkup framework
- `SoK-Agent-Econ` — 2610.01756, decentralized agent economic infrastructure SoK
- `Safety-Latent-Comm` — 2609.39788, safety of latent comm in MAS
- `AI-Security-ATLAS` — 2610.01436, deterministic auditable AI security framework with ATLAS

### MCP ecosystem — repositories & assets
- `MCP-Spec` — modelcontextprotocol/modelcontextprotocol
- `MCP-TypeScript-SDK` — modelcontextprotocol/typescript-sdk
- `MCP-Servers` — modelcontextprotocol/servers (includes `everything`, `memory` servers)
- `MCP-Registry` — modelcontextprotocol/registry
- `MCP-Conformance` — Conformance maintainers subteam (added 2026-10-01)
- `MCP-SEP` — Spec Enhancement Proposal governance
- `SEP-3336` — Require WG/IG discussion before SEP submission
- `mcpscore` — first independent MCP server quality scoring tool (added to community list 2026-09-22)
- `MCP-Memory-Server` — knowledge graph memory reference server (9-03 8-commit robustness sweep)
- `MCP-Docs-2026-07-28` — current docs revision (unchanged for 2+ months)

### Specific commits / PRs
- `PR-3411` — dependabot npm_and_yarn (brace-expansion + markdown-it) 2026-10-03
- `PR-3409` — dependabot undici bump 2026-10-02
- `PR-3408` — maintainers-tnorimat-nbarbettini merge 2026-10-01
- `PR-2938` — typescript-sdk CLAUDE.md principles 2026-10-02
- `PR-2934` — typescript-sdk SSE retry fix 2026-10-02
- `PR-4712` — servers/everything session cleanup 2026-09-22
- `PR-4555` — servers/memory graph mutation race fix 2026-09-03

### OpenClaw skills (this workspace)
- `mcporter` — MCP server list/config/auth/call/inspect
- `skill_workshop` — author reusable skills
- `SKILL.md` pattern — unit of procedural knowledge

### Subfields
- `agent-evaluation` — methodology niche (4-D frameworks, systems-not-models stance)
- `harness-engineering` — harness-as-research-object
- `agent-skill-marketplace` — skill retrieval, library, marketplace
- `multi-agent-failure-diagnosis` — evidence-grounded failure localization
- `memory-for-agents` — non-destructive, causal, hierarchical
- `agent-security` — fail-open diagnostics, authorization-paired control

### Venues
- `arXiv 2610` — October 2026 first batch
- `arXiv 2609.39xxx` — September end stragglers

## Edges

### Agent evaluation subfield
| source | relation | target |
|---|---|---|
| Agents-Are-Systems | subfield_of | agent-evaluation |
| Agents-Are-Systems | stance | "agents are systems not models" |
| MCRI | subfield_of | agent-evaluation |
| MCRI | uses | four-dimensional framework |
| Continuous-Skill-Eval | subfield_of | agent-evaluation |
| Continuous-Skill-Eval | target | enterprise AI agent skills |
| Argo-Bench | subfield_of | agent-evaluation |
| Argo-Bench | target | enterprise-scale workflows |
| KaliBench | subfield_of | agent-evaluation |
| KaliBench | uses | runtime-free verifiable rewards |
| ScholarCatalyst | subfield_of | agent-evaluation |
| ScholarCatalyst | parallel_to | scout-agent (this cron) |

### Harness engineering
| source | relation | target |
|---|---|---|
| VeriHarness | subfield_of | harness-engineering |
| ActiveSaddler | subfield_of | harness-engineering |
| Mid-Harness | subfield_of | harness-engineering |
| Harness-Annealing | subfield_of | harness-engineering |
| Keyword-Harnesses-Fail-Open | subfield_of | harness-engineering |
| Keyword-Harnesses-Fail-Open | subfield_of | agent-security |
| Mingbird | subfield_of | harness-engineering |
| Mingbird | parallels | OpenClaw (local runtime) |
| AutoCompact | subfield_of | harness-engineering |
| VISTA | subfield_of | harness-engineering |

### Memory & RAG
| source | relation | target |
|---|---|---|
| MemPP | subfield_of | memory-for-agents |
| MemPP | parallels | Mem++ open-source framework |
| Causal-Memory-Policy | subfield_of | memory-for-agents |
| Causal-Memory-Policy | uses | causal intervention |
| Matryoshka-RAG | subfield_of | memory-for-agents |
| RAG-Taxonomy | subfield_of | memory-for-agents |
| Alignment-Memory-Asymptotics | subfield_of | memory-for-agents |
| RefCon | subfield_of | memory-for-agents |

### Multi-agent failure diagnosis
| source | relation | target |
|---|---|---|
| Where-MAS-Fail | subfield_of | multi-agent-failure-diagnosis |
| Where-MAS-Fail | methodology | evidence-grounded diagnosis |
| CollabFlow | subfield_of | multi-agent-failure-diagnosis |
| Solo-To-Social | subfield_of | multi-agent-failure-diagnosis |
| Delegation-Danger-Band | subfield_of | multi-agent-failure-diagnosis |
| Delegation-Danger-Band | warns | OpenClaw subagent delegation |
| Hidden-Info-Failures | subfield_of | multi-agent-failure-diagnosis |
| Verifier-Leak | subfield_of | multi-agent-failure-diagnosis |
| Bayesian-Council | subfield_of | multi-agent-failure-diagnosis |
| Global-Coherence | subfield_of | multi-agent-failure-diagnosis |
| Heterogeneity-Team-Selection | subfield_of | multi-agent-failure-diagnosis |
| Deny-Without-Disabling | subfield_of | multi-agent-failure-diagnosis |
| Deny-Without-Disabling | subfield_of | agent-security |

### Skill marketplace
| source | relation | target |
|---|---|---|
| SkillSeek | subfield_of | agent-skill-marketplace |
| SkillSeek | parallels | SKILL.md pattern |
| SkillSeek | parallels | skill_workshop |
| MCRI | subfield_of | agent-skill-marketplace |
| Continuous-Skill-Eval | subfield_of | agent-skill-marketplace |
| GUI-Component-Routing | subfield_of | agent-skill-marketplace |
| My-FAULT | subfield_of | agent-skill-marketplace |

### MCP ecosystem
| source | relation | target |
|---|---|---|
| MCP-Conformance | part_of | MCP-Spec |
| MCP-SEP | part_of | MCP-Spec |
| SEP-3336 | tightens | MCP-SEP |
| mcpscore | part_of | MCP-Registry community list |
| mcpscore | measures_quality_of | MCP-Servers |
| MCP-Memory-Server | part_of | MCP-Servers |
| PR-4555 | fixes | MCP-Memory-Server (graph mutation race) |
| PR-4712 | fixes | MCP-Servers/everything |
| PR-3408 | merges | MCP-Conformance maintainers PR |
| PR-3411 | bumps_dep_of | MCP-Spec |
| PR-3409 | bumps_dep_of | MCP-Spec |
| PR-2938 | adds | CLAUDE.md principles to MCP-TypeScript-SDK |
| PR-2934 | fixes | MCP-TypeScript-SDK SSE retry |
| MCP-Docs-2026-07-28 | current_docs_rev | MCP-Spec |
| mcporter | implements | MCP-Servers |

### Long-horizon / belief
| source | relation | target |
|---|---|---|
| Beyond-Memory-Belief | uses | explicit belief states |
| Decision-Titan | subfield_of | memory-for-agents |
| Epistemic-Action | precedes | agent decisions |

### Venues
| source | relation | target |
|---|---|---|
| arXiv 2610 | venue_of | Agents-Are-Systems |
| arXiv 2610 | venue_of | MCRI |
| arXiv 2610 | venue_of | Delegation-Danger-Band |
| arXiv 2610 | venue_of | MemPP |
| arXiv 2610 | venue_of | KaliBench |
| arXiv 2610 | venue_of | ScholarCatalyst |
| arXiv 2609.39xxx | venue_of | Where-MAS-Fail |
| arXiv 2609.39xxx | venue_of | SkillSeek |
| arXiv 2609.39xxx | venue_of | Mid-Harness |
