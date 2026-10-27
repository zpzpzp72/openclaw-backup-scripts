# Memory: Nightly Scout — 2026-10-01

## Headline takeaways

- **MCP is stable.** Docs rev `2026-07-28`, ecosystem unchanged (Claude, ChatGPT, VS Code, Cursor, MCPJam). New surface: **MCP Apps** + **MCP Registry**. No breaking changes observed.
- **Agent evaluation is a first-class subfield.** Watchlist: `trajectory-judge` (arXiv 2609.00038), `GUI-CC` (2609.00048), `Auditing Harness Tampering` (2609.00069), `Beneath the Diff` (2609.00077).
- **"Skills" as a reuse unit is now formalised in the literature** — `Scientific Agent Skills` (2609.00065) parallels OpenClaw's `SKILL.md` pattern.
- **Multi-agent scales up.** `ArcticSwarm` (long-horizon consensus), mean-field RL at population scale, LLM-vs-LLM market games.
- **EMNLP 2026** acceptances are still landing as arXiv v2 revisions.

## Operational lessons (durable, for future cron runs)

- `web_search` is **unreliable** from this host — `ECONNRESET` and `DEPTH_ZERO_SELF_SIGNED_CERT` errors. Default to `web_fetch` against arXiv listing pages + `modelcontextprotocol.io` + the MCP spec repo.
- HN (`news.ycombinator.com`) is unreachable from this sandbox; don't include it as a source.
- `graphify` is interactive/expensive — don't invoke it from a cron scout; stage node/edge lists in the heartbeat markdown instead.
- No LanceDB in this workspace yet — scout memory lives in `heartbeat/` + `memory/` markdown until a vector store is wired.

## Watchlist entities

- arXiv: `2609.00038`, `2609.00048`, `2609.00051`, `2609.00057`, `2609.00058`, `2609.00065`, `2609.00066`, `2609.00067`, `2609.00069`, `2609.00077`, `2609.00155`, `2609.00046`, `2609.01870`, `2609.02580`, `2609.02928`.
- Venues: EMNLP 2026, NeurIPS 2026 workshops.
- Protocols: MCP, MCP Apps, MCP Registry.
