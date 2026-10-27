# Nightly Scout — 2026-10-24 (memory)

> 详细报告：`heartbeat/nightly-scout-2026-10-24.md`

## 关键事实（可复用）

- **arXiv cs.AI 新批次**：2610.31307 → 2610.31667，50 篇全部 submittedDate=2026-10-22（周五提交周末释放）。ID 增速从 +3000/天 升至 +4400/天。
- **MCP spec 仍未发版**：最新 tag `2026-07-28`，连续 9 场观察未发（88 天）。但仓内实质推进：10-16 建 Tasks & Events WG、Agents WG 降为 Interest Group；10-23 更新维护者归属。
- **MCP ext-auth 10-23 关键提交**：OAuth Client Credentials → stable；Enterprise-Managed Authorization 以带日期修订版发布；扩展分阶段机制说明。
- **MCP SDK 全线高频发版**：typescript v2.4.0 (10-23)、rust rmcp-v3.7.0 (10-22)、csharp v2.3.0 (10-20)、python v2.2.0 (10-23)、go v1.8.0 (09-14，落后 40 天)。
- **MCP Inspector v2.12.0** (2026-10-21T18:13Z)，取代 v2.11.0。
- **`anthropic-sdk-python` 主版本跳 v2**：v1.17.0 → v2.0.0 → v2.1.0 → v2.2.0，10-20 到 10-23 四天三发。
- **`claude-code` v2.1.309** (2026-10-22T22:18Z)。
- **MCP registry 生产 promote 1.8.2 → 1.8.4**（10-23 单日 3 次 promote + 3 项修复），已是高频运营服务。

## 产业事件

- **OpenAI Decisions API GA** (10-22)：基于 GPT-6 Luna，有界答案决策比 Responses API 快至 10×；原生 GPT-Live、prompt caching、US/EU 推理驻留、原生 JSON 输入、单请求 400 问。
- **OpenAI Patch the Planet** (10-21)：GPT-5.6 Sol 发现 PHP 关键漏洞（Wiz 独立报告其一）；协调 Defender's Window；承诺 10 亿美元补贴 Daybreak；开源 PHP 版本检查器为 Codex skill。
- **OpenAI 加固 frontier 训练环境隔离** (10-23)：红队测试沙箱逃逸/内网触达/跨沙箱通信，引用 Hugging Face 事件。
- **Kimi K3.1 Pro / Highspeed** (10-23)：3T 级开源权重最强模型，**1M token 上下文**，Highspeed 快 2–3×，权重 11-04 前发布，已上 Vercel AI Gateway。
- **Vercel Agent 权限模型** (10-23)：plan 决定权限，scopes 具名化（read:deployment / read-write:deployment），超只读基线整体审批。模型 Intent→Work→Access→Enforcement。
- **Vercel 消灭长生命周期静态凭据** (10-22)：HTTPS 2010 类比，机器间认证仍用长生命周期凭据；推出 OIDC UI，Marketplace provider 新认证要求。

## 跨源主线判断

1. **「长生命周期静态凭据 / 授权绑定」是 10 月下旬跨源主线**：Vercel OIDC + Vercel plan/scope + arXiv *filesystem capability laundering* (2610.22301) + *Approve What, Exactly?* (2610.21063) + OpenAI 沙箱加固——产业侧拆凭据、论文侧定攻击面，8 天内收敛。
2. **Petri 网监管控制 (2610.31376) 是 plan/scope 授权的数学形式化**，形态一致，不同生态。
3. **MCP 治理重心下沉到运行时**：spec 不发版但 ext-auth/registry 在推进，落地瓶颈已在认证与注册运营。
4. **1M 上下文不解决工具发现问题**：Tool Recommendation (2610.23707) 的 8,200 工具 → 3 接口仍是 gateway 层问题。
5. **RL 进入 MCP 场景本身**：2610.28785 把 MCP harness 当 RL 环境，MCP 从「被调用的接口」变成「被训练的接口」。

## arXiv 主题分布（cs.AI 50 篇）

Agent 安全/治理 10 · 推理/训练/RL 8 · 记忆/知识 7 · 工具/技能 7 · 其他 7 · 评估/合规 6 · 多 Agent 5。
安全治理类相比 10-20 场（3 篇）大幅跃升。

## 工具/运维备忘

- arXiv API 必须用 **https**（`http://export.arxiv.org` 返回 301）。
- `graphify cluster-only` 正确用法：`graphify cluster-only . --graph graphify-out/graph.json`（直接把路径当参数会拼成 `graph.json/graph.json`）。
- graphify 节点 `file_type` 只接受 `code|document|image|paper|rationale`，自建节点需映射。
- Anthropic news RSS（`/rss.xml`、`/news/rss.xml`）已 404/返回 HTML；LangChain blog RSS XML 非法字符（col 2714）。
- **`web_search` provider 连续 7 天失败**（10-06 → 10-24），需排查 duckduckgo 配置。
