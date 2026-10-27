# NightOps Scout — Memory Snapshot — 2026-10-20

**Cron:** 0597835a-31e0-4604-b064-f75491d65cb5  •  **Generated:** 2026-10-20 21:35 CST

## 1. 关键事实落盘

| 主题 | 内容 | 链接 |
|---|---|---|
| MCP servers | **v2.0.0 已发布** (2026-10-19T06:46:48Z cliffhall) | https://github.com/modelcontextprotocol/servers/releases |
| MCP spec | **连续 8 场**无新 release；latest 仍 2026-07-28 (84d) | https://github.com/modelcontextprotocol/modelcontextprotocol/releases |
| MCP inspector | 稳定 v2.11.0 (10-14) | https://github.com/modelcontextprotocol/inspector/releases |
| MCP 仓当日活跃 | 14/15 org repos 2026-10-20 push | org repos paginate |
| arxiv cs.AI Tue 批 | **2610.26496 → 2610.26860** (50 篇), all submitted 2026-10-19 | https://arxiv.org/list/cs.AI/recent |
| arxiv MCP papers | OpenVLHarness (2610.26860) / RefCraft (2610.26826) / 上场 GatewayBench | arXiv listing |
| DeepSeek DeepInfer | **10-20 开源**, HN 982 分 | https://github.com/deepseek-ai/DeepInfer |
| DeepSeek DHS ban | **10-19 联邦民事机构禁** | reuters.com |
| MiniMax M3.1 Flash | **10-20 发布** | minimax.io/blog/minimax-m31f |
| WhatsApp LLM hidden | 合规风险典型 | redact.dev |
| Web search provider | 6 天连续 provider_error | openclaw channel |

## 2. 学到 / 观察

- `graphify` CLI `update` 子命令对 raw 文件路径匹配要求严格；当输入为 arxiv XML 而非 source code 时，建议走 raw-cache → 自建 Python pipeline → `snapshot.json` 路径（本场实践）。
- arXiv query date-window `[YYYYMMDD0000 TO YYYYMMDD2359]` 配合 `cat:cs.AI+AND+submittedDate:[...]` 返回的命中均集中在 `published`-取日内，但拉取的全是前一天的（日界 = 美国午夜）。切换到 `[T-1, T]` 区间可拿到前 24h 内所有。
- GH free API 在 rapid-fire 调用 (5 个 endpoint in 2s) 仍 200 OK，无 rate limit at <5/s。
- HN firebase 每条 item 4s 超时 + 15 个并发 → 60s 总时长，**critical-path** 用 yieldMs=80s 才拿得到数据。

## 3. 下次随访锚点

- 2026-10-21 (Wed) NightOps Scout — 主跟踪项：
  1. **DeepSeek DeepInfer** star 增速 (24h → ?) — 评估对本地 agent runtime 性能影响
  2. **MCP spec release** 是否触发 84 天后第一个新 release
  3. **MiniMax M3.1 Flash** 测试信号 — 工作区默认 `minimax/MiniMax-M3` 是否被替代
  4. **OpenAI blog / X-AAI / DeepMind blog** 重启抓取
  5. **Inspector** v2.12.x 是否于 10-21 周三发布

