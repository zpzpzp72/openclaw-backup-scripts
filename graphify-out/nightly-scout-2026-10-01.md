# Knowledge Graph — Nightly Scout 2026-10-01

> Staged input for the `graphify` skill. Run `graphify` against `heartbeat/nightly-scout-2026-10-01.md` to produce HTML/JSON/audit report. This file is the human-readable node/edge spec.

## Nodes

### Protocols & surfaces
- `MCP` (Model Context Protocol) — open standard, docs rev 2026-07-28.
- `MCP Apps` — interactive apps running inside AI clients.
- `MCP Registry` — discovery layer for MCP servers.
- `USB-C analogy` — mental model used on the MCP homepage.

### Implementations / clients
- `Claude` (Anthropic Connectors)
- `ChatGPT` (OpenAI MCP support)
- `VS Code` (Copilot Chat MCP)
- `Cursor` (context MCP)
- `MCPJam`

### OpenClaw skills (this workspace)
- `mcporter` — MCP server list/config/auth/call/inspect.
- `skill_workshop` — author reusable skills.
- `SKILL.md` pattern — unit of procedural knowledge for agents.

### arXiv papers (September 2026)
- `trajectory-judge` — 2609.00038, NeurIPS 2026 workshop.
- `GUI-CC` — 2609.00048, EMNLP 26 Findings.
- `From Detection to Refusal` — 2609.00051, EMNLP 26 Findings.
- `ValueGraph` — 2609.00057.
- `CUDA-Harness` — 2609.00058.
- `Scientific Agent Skills` — 2609.00065.
- `OCGQuant` — 2609.00066, EMNLP 26 Main.
- `Multimodal Sycophancy` — 2609.00067.
- `Auditing Harness Tampering` — 2609.00069.
- `Beneath the Diff` — 2609.00077, EMNLP 26.
- `Lingua Franca or Probing Artifact` — 2609.00155, EMNLP 26.
- `RAPIDMap` — 2609.00046, CaGIS 2026.
- `ArcticSwarm` — 2609.01870.
- `Competitive Market Behavior of LLMs` — 2609.02580.
- `Scaling RL to Massive Populations` — 2609.02928.

### Subfields
- `agent-evaluation`
- `multi-agent-systems`
- `agent-skills` (literature niche parallel to OpenClaw skill workshop)
- `quantization-NVFP4`

### Venues
- `EMNLP 2026`
- `NeurIPS 2026`

## Edges

| source | relation | target |
|---|---|---|
| MCP Apps | part_of | MCP |
| MCP Registry | part_of | MCP |
| MCP | enables | tool-use |
| MCP | compared_to | USB-C analogy |
| Claude | implements | MCP |
| ChatGPT | implements | MCP |
| VS Code | implements | MCP |
| Cursor | implements | MCP |
| MCPJam | implements | MCP |
| mcporter | implements | MCP |
| Scientific Agent Skills | parallel_to | SKILL.md pattern |
| Scientific Agent Skills | parallel_to | skill_workshop |
| trajectory-judge | subfield_of | agent-evaluation |
| GUI-CC | subfield_of | agent-evaluation |
| Auditing Harness Tampering | subfield_of | agent-evaluation |
| Beneath the Diff | subfield_of | agent-evaluation |
| ArcticSwarm | subfield_of | multi-agent-systems |
| Scaling RL to Massive Populations | subfield_of | multi-agent-systems |
| Competitive Market Behavior of LLMs | subfield_of | multi-agent-systems |
| RAPIDMap | subfield_of | multi-agent-systems |
| ValueGraph | uses | graphify |
| OCGQuant | subfield_of | quantization-NVFP4 |
| EMNLP 2026 | venue_of | trajectory-judge |
| NeurIPS 2026 | venue_of | trajectory-judge (workshop) |
| EMNLP 2026 | venue_of | GUI-CC |
| EMNLP 2026 | venue_of | From Detection to Refusal |
| EMNLP 2026 | venue_of | OCGQuant |
| EMNLP 2026 | venue_of | Beneath the Diff |
| EMNLP 2026 | venue_of | Lingua Franca or Probing Artifact |

## Communities (anticipated after clustering)

1. **MCP ecosystem** — {MCP, MCP Apps, MCP Registry, Claude, ChatGPT, VS Code, Cursor, MCPJam, mcporter}.
2. **Agent evaluation** — {trajectory-judge, GUI-CC, Auditing Harness Tampering, Beneath the Diff, agent-evaluation}.
3. **Multi-agent research** — {ArcticSwarm, Scaling RL to Massive Populations, Competitive Market Behavior of LLMs, RAPIDMap, multi-agent-systems}.
4. **Agent skills literature** — {Scientific Agent Skills, SKILL.md pattern, skill_workshop, agent-skills}.
5. **Efficiency / quantisation** — {OCGQuant, quantization-NVFP4}.
6. **Multilingual / alignment** — {Multimodal Sycophancy, Lingua Franca or Probing Artifact, From Detection to Refusal}.
7. **GPU / code agents** — {CUDA-Harness, ValueGraph}.

## Sources

- https://arxiv.org/list/cs.CL/2026-09
- https://arxiv.org/list/cs.MA/2026-09
- https://modelcontextprotocol.io/
- https://github.com/modelcontextprotocol/modelcontextprotocol
