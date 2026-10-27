# 🌙 Nightly Scout Report — 2026-10-26 (Sunday)

**Generated:** 2026-10-26 00:45 CST (Asia/Shanghai) / 2026-10-25 16:45 UTC
**Window:** NightOps Scout — ✅ 在 Mon–Fri 00:30–03:00 窗口内（本场 00:30 触发，周日；沿用 2026-10-24 起的新窗口，避开 MiniMax Token Plan burst 耗尽区间 02:00–05:00）
**Runtime:** OpenClaw NightOps-Scout (cron `0597835a-31e0-4604-b064-f75491d65cb5`)
**Coverage:** ✅ arXiv API (cs.AI 50 / cs.MA 25 / MCP-exact 25 / tool-agent 40 = 140 条目) ✅; GitHub API (24 端点全 200：spec/servers/inspector/registry/ext-auth/ext-apps/8 个 SDK/claude-code/governance-wg/access + 9 个 SDK 提交流 + 安全公告) ✅; HackerNews top 30 ✅; RSS (OpenAI 1318 / Vercel 1704 / Google AI) ✅; web_fetch (3 篇原文) ✅; ❌ web_search provider (**连续 8 天失败**，10-06 → 10-26)

---

## 0. 🔴 本场头号发现：MCP servers v2.1.0 — 一次发布修掉 8 个安全漏洞

**这是本场最重要的信号，远超任何单篇论文。**

`modelcontextprotocol/servers` 于 **2026-10-25 00:03Z** 发布 **v2.1.0**，一次性修复 **3 个 server 中的 8 个漏洞**，并同步发布 8 条 GitHub Security Advisory（全部于 2026-10-25 00:15–00:19Z 公开）。这与 10-24 场刚记录的 "servers v2.0.0 发布" 是同一仓的下一个版本——**从 v2.0.0（功能发布）到 v2.1.0（安全加固），只隔 6 天**。

### 0.1 八条漏洞全表

| GHSA | 严重度 | 组件 | 漏洞 |
|---|---|---|---|
| **GHSA-53mr-w429-c597** | low | server-filesystem | 父目录 fallback TOCTOU：检查目录与写入之间父目录被换成 symlink，`write_file`/`edit_file`/`create_directory`/`move_file` 可写到允许目录之外（**Windows 仅部分修复**）|
| **GHSA-7rgq-gccq-qphx** | medium | server-filesystem | 路径校验与使用不一致（Check/Use Mismatch）：校验时不剥尾部引号/空白，同名兄弟目录可被访问 |
| **GHSA-4gxg-m5jx-9j57** | medium | server-filesystem | 大小写变体绕过 symlink 检查（macOS 大小写不敏感卷），可越界创建文件；2026.8.31 引入的回归 |
| **GHSA-hhwq-wxfx-cj7g** | low | server-filesystem | `list_directory_with_sizes` 跟随 symlink，泄露目录外文件的大小与修改时间 |
| **GHSA-mvf5-2qqv-rg3c** | medium | server-everything | 跨源环境变量外泄：HTTP/SSE transport 不校验 `Origin`，且下发 `Access-Control-Allow-Origin: *`，任意网页可调用 server 工具（如 `get-env`）并读取结果 |
| **GHSA-v38p-wf49-hx2j** | medium | mcp-server-fetch | IDNA 主机名 SSRF 绕过：校验的域名与实际连接的域名不一致，可达内网地址 |
| **GHSA-66qx-2266-pmj6** | low | mcp-server-fetch | NAT64 前缀 `64:ff9b::/96` 被当作公网地址，元数据地址在 NAT64/DNS64 出口可达 |
| **GHSA-3jqg-r5pp-rmp2** | low | mcp-server-fetch | robots.txt 约束在 HTTP 重定向后不再检查 |

### 0.2 修复版本与一个坑

| 包 | 受影响 | 修复于 |
|---|---|---|
| `@modelcontextprotocol/server-filesystem` | 1.0.0 – 2.0.0，及 2026.8.31 之前的日期版本 | **2.0.1** |
| `@modelcontextprotocol/server-everything` | 1.0.0 – 2.0.0，及 2025.9.24 – 2026.8.31 日期版本 | **2.0.1** |
| `mcp-server-fetch` | 至 2026.10.19 | **2026.10.24** |

> ⚠️ **升级陷阱（官方明确警告）**：TypeScript servers 已从日期版本（2025.x / 2026.x）转向语义版本（1.0.0+），包管理器把 **2.0.1 排在所有 2025.x/2026.x 之后**，因此**不会自动提示升级**。必须显式安装：
> `npm install @modelcontextprotocol/server-filesystem@2.0.1`
> `pip install mcp-server-fetch==2026.10.24`

### 0.3 为什么这条比论文更值得记

- 这 8 条漏洞**全部是「agent 特有」的攻击面**：TOCTOU 路径逃逸、跨源工具调用、凭据/环境变量外泄、SSRF 到内网——**传统应用里不存在的面**。
- 与 10-24 场的论文主线**精确对上**：*filesystem capability laundering*（2610.22301，客户端批准授予过宽文件系统权限）→ 官方 server 现在自己把这条面补上了；*Approve What, Exactly?*（2610.21063，step-up 授权的效果绑定）→ `get-env` 跨源外泄正是「批准了但效果没绑定」的实例。
- 与产业侧收敛同向：Vercel 的 plan/scope 授权模型（10-23）说的就是「批准要绑定到具体效果」——**官方 server 用 8 个 CVE 把这条主张落到了代码上**。

---

## 1. 本场研究主题

**AI / Agent / MCP 当日最新动态 — 10 月最后一周 · 周末安全场**

> 上场 (10-24) 关键回顾：
> (a) `mcp/servers` **v2.0.0** 发布（10-19）；
> (b) arXiv cs.AI 落在 2610.31307–26860（10-22 提交）；
> (c) MCP SDK 全线爆发；`anthropic-sdk-python` 三天跳 v2；Decisions API GA；Kimi K3.1 Pro（1M 上下文）；Vercel plan/scope 授权 + OIDC；ext-auth OAuth Client Credentials 转 stable。

**本场新增 / 延续观察：**
> (a) **【头号】`mcp/servers` v2.1.0（10-25）— 8 个漏洞、3 个 server、8 条 GHSA 同期公开**；
> (b) **MCP org 安全面全面收紧**：registry 仓 10-24 单日 9 个提交全是安全向（ECDSA P-384 签名填充、验证器拒绝非法参数、GitLab 嵌套子组、仓库元数据完整性、mcp-publisher 安装器 pin & verify）；
> (c) **新语言 SDK 同步补安全修复**：Go SDK 限制 HTTP client 跨源重定向（#1440）、`insufficient_scope` 错误进 `WWW-Authenticate`（#1421）；Swift SDK 转义 `WWW-Authenticate` quoted-pair（#305）；C# SDK 补 **SEP-2640 Skills 扩展支持**（#1856）；Ruby SDK 连续修 stdio/HTTP 帧编码；
> (d) **CVE-2026-111497（"Node2Shell" → "HTTP2Shell"）**：Brotli 解码器越界写，CVSS 9.2，**OpenAI 2 月发现、10-23 披露**，影响 Node.js / Python / C++ / bun / Envoy 等所有解 Brotli 的服务（HN 365 分）；
> (e) **Cerebras 万亿参数模型部署工程**（HN 282 分 / 95 评论）；
> (f) **arXiv 周末无新提交**（cs.AI 最新仍为 2610.31667，10-22 提交），本场 arXiv 增量实际为 **0 篇新论文**——已完整核验 API 200 条目全部落在 10-21/10-22；
> (g) **MCP spec 仍无新 release**（连续 10 场，已 90 天），但 **governance-wg 仓 10-19 建立工作组结构**，Tasks & Events WG 仍在推进；
> (h) **Anthropic 官网 news 页可解析了**（本场通过 `__next_f` 内嵌 JSON 提取到标题+日期），但 RSS 四个候选 URL 仍全部 404。

### 1.0 Operational Notes — 本场能力状态

| 通道 | 状态 | 证据 |
|---|---|---|
| `web_search` (DuckDuckGo provider) | ❌ `provider_error` | **连续 8 天失败**（10-06 → 10-26）。本场用 web_fetch + curl 直连 + RSS 全量替代 |
| `web_fetch` (cf-markdown) | ✅ 200 OK | 3 篇原文（Vercel ×2 + Aikido/CVE ×1）；OpenAI 域被 SSRF 防护拦截（`resolves to private/internal IP`）|
| `curl` arXiv API | ✅ 200 OK | cs.AI 50 + cs.MA 25 + MCP-exact 25 + tool-agent 40 = 140 条目；另拉 200 条核验批次边界 |
| `curl` GitHub API | ✅ 200 OK | 24 个端点全 200（release/commits/advisories/org repos）|
| HackerNews API (firebaseio) | ✅ 200 OK | topstories 500 + 前 30 条 item 并发抓取 |
| RSS — OpenAI | ✅ 200 OK | 1318 items（最新 10-23）|
| RSS — Vercel | ✅ 200 OK | 1704 items（最新 10-23 21:44Z）|
| RSS — Google AI | ✅ 200 OK | 30 items（最新 10-21；旧 URL 需 301 跟随后可用）|
| RSS — Anthropic | ❌ 404 ×4 | `/rss.xml`、`/news/rss.xml`、`/feed.xml`、`/news/feed.xml` 全 404；改用官网 HTML 内嵌 JSON |
| RSS — LangChain | ⚠️ 返回 HTML | `/rss/` 现返回 Webflow 页面（216KB），非 RSS |
| `graphify` CLI | ✅ 200 OK | `cluster-only` 重聚类成功：**504 节点 / 1207 边 / 48 社区**，HTML 刷新至 499KB |

**结论：arXiv / GitHub / GitHub Advisory / HN / web_fetch / graphify 全部通道绿；web_search 连续 8 天空档（唯一红灯）；Anthropic + LangChain RSS 本场降级。**

---

## 2. 上场 (10-24) 待跟进事项今日清单

| 上场关注点 | 今日判定 | 证据 |
|---|---|---|
| `mcp/servers` v2.0.0 | ⬆️ **已升级 v2.1.0（安全加固版）** | 2026-10-25T00:03:20Z，修复 8 个漏洞 / 3 个 server / 8 条 GHSA |
| MCP spec release | ❌ **仍未发布（连续 10 场）** | 最新 tag 仍 `2026-07-28`（sha 5f5440b），已 **90 天** |
| Tasks & Events WG 首个产出 | ➡️ 仍无独立产出 | ext-tasks 最近提交仍停在 10-20（`-32021` 错误码）|
| ext-auth 下一步 | ➡️ 无新 tag / 无新提交 | 最后提交仍为 10-23 `15ca394`；仓内无 release/tag |
| Go SDK 何时跟上 | 🟡 **发版停滞但代码在修安全** | release 仍 v1.8.0（09-14，41 天），但 10-23 提交跨源重定向限制 + insufficient_scope |
| `anthropic-sdk-python` v2.x 稳定性 | ✅ **再发一版 v2.3.0** | v2.3.0（2026-10-23T23:18Z），v2.2.0 之后 10 小时 |
| Kimi K3.1 Pro 权重（11-04 前） | ➡️ 未发 | Vercel AI Gateway 已上架，权重未放 |
| OpenAI Decisions API 实测可用性 | ➡️ 未实测 | OpenAI 域被 web_fetch SSRF 防护拦截，需换路径 |
| arXiv 下一批次 | ❌ **周末无新提交** | cs.AI 最新仍 2610.31667；200 条核验最新提交日 = 10-22 |
| `web_search` provider | ❌ **仍不可用（8 天）** | provider_error |
| **MCP SDK 跨语言** | ⬆️ **扩展到 Swift / Ruby** | Swift SDK 10-25 两提交（WWW-Authenticate 转义）；Ruby SDK 10-24 修帧编码 |

---

## 3. 🔒 MCP 生态安全主线（本场核心章节）

### 3.1 MCP org 全仓安全收紧

| 仓 | 时间 (UTC) | 内容 |
|---|---|---|
| **servers** | 10-25 00:03 | **v2.1.0 发布，8 个漏洞修复**（详见第 0 节）|
| **servers** | 10-24 23:40 | `ef9808f` Merge PR #5249 — release v2.1.0；`fefc558` Python CalVer 版本戳记 2026.10.24 |
| **registry** | 10-24 22:00 | `edd9fa7` docs: DNS/HTTP 认证排障 |
| **registry** | 10-24 21:51 | `c34626b` docs: HTTP 验证要求文档化 + 测试 pin 住 |
| **registry** | 10-24 21:44 | `cd511f4` **docs(security): pin & verify mcp-publisher 安装器**（#1523）|
| **registry** | 10-24 21:32 | `63d22fa` fix: init 时记录 `repository.id`，仓改名后仍可解析（#1570）|
| **registry** | 10-24 21:22 | `020fed3` fix(validators): 拒绝非法参数类型与空位置参数（#1583）|
| **registry** | 10-24 21:14 | `8a2efd0` fix(validators): 允许 GitLab 带嵌套子组的仓库 URL（#1361）|
| **registry** | 10-24 21:07 | `efee8f0` fix(validators): 拒绝不完整的仓库元数据（#1555）|
| **registry** | 10-24 20:52 | `097bdc4` fix(publisher): **ECDSA P-384 签名填充至固定宽度**（#1457）|

> **解读**：registry 在 10-23 三次生产 promote（1.8.2→1.8.4）之后，10-24 转入**纯安全加固模式**——签名编码、参数校验、元数据完整性、安装器供应链 pin 住。**MCP 注册中心已从「能注册」进入「防伪造」阶段**。

### 3.2 多语言 SDK 安全同步

| SDK | 时间 (UTC) | 提交 |
|---|---|---|
| **Go** | 10-23 15:48 | `2e00768` **限制 HTTP client 跨源重定向**（#1440）——防凭据被跨域重定向带走 |
| **Go** | 10-23 08:57 | `7899792` 403 时 `WWW-Authenticate` 头带 `insufficient_scope`（#1421）——**把授权粒度写进协议层** |
| **Go** | 10-23 08:43 | `f77a5d7` SSEClientTransport 跳过非 message 事件（#1439）|
| **Go** | 10-22 08:53 | `12e768b` oauthex: `jwks` client metadata 按 JSON 对象编解码（#1435）|
| **Go** | 10-21 15:09 | `b874fad` conformance: 运行 client credentials 场景（#1433）|
| **Swift** | 10-25 12:29 | `68300d7` 转义 `WWW-Authenticate` 参数中所有 quoted-pair 序列（#305）|
| **Swift** | 10-24 23:10 | `2a44bfd` / `05a54fe` data URL base64 检测从 header 而非 payload 读取（#310/#309）|
| **C#** | 10-23 18:42 | `8b00f20` **新增 SEP-2640 Skills 扩展支持**（#1856）|
| **C#** | 10-22 21:05 | `4f97244` 修复请求取消时通知丢失/误报取消（#1917）|
| **Ruby** | 10-24 17:34 | `ec6501b` 丢弃无法生成的 buffered notification |
| **Ruby** | 10-23 21:48 | `37270d6` HTTP 回复无法编码时返回 Internal error |
| **Python** | 10-24 20:19 | `a525a3d` 结构化输出支持裸 `dict`/`set`/`frozenset` 返回注解（#3758）|
| **Python** | 10-24 17:39 | `72ff38c` **从工具 input/output schema 中移除生成的 title**（#3757）——减少 token 浪费 |
| **Python** | 10-24 16:46 | `86ca12b` 解决 open code 扫描告警（#3755）|
| **TypeScript** | 10-23 17:58 | `895007f` stateless legacy 405 响应设置 `Allow: POST`（#3002）|
| **TypeScript** | 10-23 17:29 | `a633756` **feat: token 刷新时可选携带 scope**（#3085）|

> **解读**：Go / Swift 两处 `WWW-Authenticate` + `insufficient_scope` 改动是**本场被低估的信号**——「授权不足」被正式写进 HTTP 认证挑战协议，与 Vercel 的 scope 模型、arXiv 的 effect-binding 论文形成三方一致。TypeScript 的 "token 刷新携带 scope" 则是 OAuth scope 语义的客户端落地。

### 3.3 MCP org 结构面

- **governance-wg**（2026-10-19 建立）最近提交：`3bf2af8` 初始工作组结构 → **治理 WG 已就位，spec 发版仍待其收敛**；
- **access**（IaC 管理 MCP 访问）10-24 有推送：新增 **Financial Services Interest Group** 成员（`7bd36fe`，2026-10-21）；用 Pulumi 同步 GitHub Team / Google Workspace / Discord / Cloudflare Access / npm & PyPI 发布权限；
- **ext-tasks** 最后提交仍是 10-20（`-32021` 错误码说明），**Tasks & Events WG 尚未产出可发布内容**；
- **ext-skills** 10-16 提交（Skills Over MCP WG，749 star）——与 C# SDK 刚加的 SEP-2640 Skills 支持呼应；
- **ext-apps** 自 10-23 `get-screenshot` 后无新提交；
- **org 45 仓中 10 月新建 3 个**：`governance-wg`(10-19)、`experimental-ext-file-uploads`(10-14)、`experimental-ext-filesystems`(10-07)。

### 3.4 MCP spec 状态（连续 10 场未发版）

- 最新 tag 仍为 `2026-07-28`（sha `5f5440b`），**距今 90 天**；
- 仓内最后提交 10-23 `dae694f`（更新维护者 GitHub handle）；
- 10-20 `80041ab` 合并 PR #3440（Tasks & Events WG + Agents IG 措辞与名单）后无进展；
- **判断**：spec 走「工作组化 → 收敛 → 发版」路线，governance-wg 已建立工作组结构，**发版大概率在治理 WG 与 Tasks WG 各自收敛之后**。

---

## 4. 🔐 产业安全：Node2Shell → HTTP2Shell

**CVE-2026-111497**：Google Brotli 解码器越界写（1.0.3 – 1.2.0，全平台），CVSS v4.0 **9.2 Critical**。

| 时间 | 事件 |
|---|---|
| **2 月** | **OpenAI 发现该漏洞**，按未认证远程代码执行上报（双向可利用：恶意客户端可接管未打补丁服务器，恶意服务器可接管接受压缩响应的客户端）|
| 10-21 (三) | Node.js 披露，命名 "node2shell" |
| 10-22 (四) | Python 披露，Python 包同样受影响 |
| 10-23 (五) | 确认影响更多语言与服务；**OpenAI 公开披露**（此时根因虽早已在 Brotli 源码修复，但漏洞性质当时未知）|
| 10-23 16:12 PT | 补丁发布：libbrotli / Python / C++ / Node.js / bun / Envoy 等；Apache 与 Nginx 默认不解 Brotli |

> **HN 365 分 / 182 评论**，Aikido 专文《Node2Shell evolves to HTTP2Shell》。
> **与本场主线的关系**：这是「**AI 发现漏洞 → 协调披露 → 生态打补丁**」全链条的第二例（上一例是 10-21 的 Patch the Planet / PHP）。**OpenAI 已成为漏洞发现的常规上游**，而这条链路的成本正在由「协调」压到「天数级」（2 月发现 → 10-23 披露，跨语言扩散仅 2 天）。

---

## 5. 📰 产业快讯

### 5.1 🧠 Cerebras — 万亿参数模型部署（HN 282 分 / 95 评论）

- Cerebras 官方工程博客发布万亿参数级 frontier 模型部署实践；
- 与 Kimi K3.1 Pro（3T 级开源权重、1M 上下文）同期，说明**超大模型的推理基础设施**是当前热点；
- 原文页在 HN 有链接但 web_fetch 404（站点改版），本场以 HN 标题+分数+评论数作为证据。

### 5.2 🌙 Kimi K3.1 Pro（延续观察）

- 已上 **Vercel AI Gateway**（10-23 00:00Z）；**完整权重承诺 11-04 前发布**——本场未见发布。

### 5.3 🛡️ OpenAI（延续观察，10-21 → 10-23）

| 日期 | 事件 |
|---|---|
| 10-21 | **Patch the Planet**：GPT-5.6 Sol 发现 PHP 关键漏洞，协调 Defender's Window，10 亿美元补贴 Daybreak |
| 10-21 | **Cloudflare links vulnerability discovery to defense with OpenAI** |
| 10-21 | **Democratic governance of frontier AI, part II: Empowering cyber defenders** |
| 10-21 | **Broad access through consistent standards**（一致性标准 → 广泛接入）|
| 10-22 | **Decisions API GA**（GPT-6 Luna，有界答案快至 10×，单请求 400 问）|
| 10-23 | **Securing our frontier model training environment**（沙箱隔离加固 + 自家模型红队）|
| 10-23 | **OpenAI × 波兰 NASK** AI 安全合作 |
| 10-23 | 在线存储扩容 Part II（Habitat + Cosmos DB，12× 读加速）|

### 5.4 🛠 Vercel（延续观察，10-22 → 10-23）

- **Death to long-lived static credentials**（10-22，Malte Ubl）：HTTPS 2010 类比；推出 **OIDC UI**（shadcn/ui registry，给 provider 信任策略表单 + token 验证代码）；对 Marketplace provider 设新认证要求；文中明确点名 **prompt injection 导致 agent 泄露凭据**；
- **How Vercel Agent accesses production safely**（10-23，Tom Dale）：**plan 决定权限**。模型 Intent → Work → Access → Enforcement；scopes 为具名能力（`read:deployment` / `read-write:deployment`）；超出只读基线的 plan **整体**等待批准（含其中的只读任务）；每个 plan 记录任务与进度，并把请求的 scope 附在任务上；
- 工程侧同周：`Vercel CLI adds Spend Management`、`Send feedback from the Vercel MCP`、`Deployments now show build cache size`、`Vercel Connect adds managed Stripe API keys`、`Routing Middleware supports Python`、`WebSocket GA`。

### 5.5 📊 其他

- **Google**（10-21）：东南亚数字经济 3,680 亿美元；Gemini 4 Argon（10-13）为最新模型发布；
- **OpenAI**：Uber 全员部署 ChatGPT Work（10-22）；OpenAI 模型上架 Google Cloud（10-21）；ChatGPT Ads 扩至 26 国（超 10 万广告主）；AT&T 法务场景（10-21）；
- **Anthropic**（官网 HTML 提取）：`Open call for guest investigators in the life sciences`（10-22）、`Investing in the public benefit`（10-18）；
- **GitHub 新仓库热度**（10-15 起新建）：`Leonxlnx/earshot`（2,754★，让编码 agent 听音审音）、`aicodeking/leanrea`（2,480★，8KB skill 替代 REA）、`reason-machines/reason-network`（1,221★，让团队编码 agent 互相通信）、**麦当劳 MCP 生态集群**（`mcd-party-planner` 1,589★、`mcd-money-saver` 356★、`mai-suanpan` 220★、`mcd-saver-checkup` 206★ 等 6+ 仓）——**「垂直行业 MCP 应用」已出现规模化自发生成**。

---

## 6. 📚 arXiv（周末无新提交，本节为已释放批次的补充挖掘）

> **核验说明**：arXiv API 拉取 cs.AI 200 条 + cs.MA 25 条 + MCP 25 条 + tool-agent 40 条，**publishedDate 分布确认最新提交日为 2026-10-22**（cs.AI 200 条中 169 条为 10-22、31 条为 10-21）。**周末（10-25/10-26）arXiv 不发布新批次**，本场 arXiv 增量为 0。以下是上一批（10-22）中此前未被单独提炼的 cs.MA 论文——本场**首次系统性覆盖 cs.MA 25 篇**。

### 6.1 🔒 安全 / 治理 / 授权（本场 cs.MA 最大增量）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.31446** | **When Is a Memory Safe Enough to Act On? Action-Conditioned Verification for Long-Lived Agents** | 记忆是否需复核**不是记忆条目自身的属性，而是动作的属性**——同一地址用于普通发货可直接用，用于贵重发货必须重新确认。形式化为**序贯停止问题**；在验证器可靠性与成本条件下，**动作后果增大可使同一记忆依次穿过 proceed / verify / direct-abstention 三个区间**。给出实践门控 **AMV-Guard** |
| **2610.29669** | **Conflicted Records: Typed Adversarial Contracts for Auditable LLM Output Quality Enforcement** | 经典数据清洗无法处理「同一段文本同时满足与违反质量规则」（事实邻接幻觉、答案邻接刻板印象）；单一 LLM judge 也不行（共享产生该冲突的偏差）。**BiasGuard-D**：两个不同模型家族的对抗角色交换 typed claim 文档，**三模型多数表决**，referential + semantic 双检查 |
| **2610.30221** | **Agentic Architecture of Information Systems. The AAM/5C Model** | 提出 AAM/5C 参考模型：五能力（Capture/Comprehend/Choose/Coordinate/Control）× 七逻辑层 L1–L7。**单条授权规则 R-AUT 分离「谁提议 / 谁决定 / 谁执行」**：概率规划器(L4) 提议 → 治理层(L6) 在**签名策略**下裁决并写入**签名评估证明** → 安全层(L5) 签发绑定该证明的**短时效 act token** → 策略执行点双重校验 |
| **2610.30557** | **Governed Self-Evolution for Autonomous Investing (Steward)** | 自我进化边界画在**类型系统**里：9 个角色特化 agent 联合决策（4 分析师出 typed report → Portfolio Manager → 受保护的 Risk Manager 审计）；**七层共享记忆**；改进靠**复盘**——代码每晚给每笔交易/预测打分写入记忆，每季度 reflector 提出 prompt 学习，由**确定性门控可逆应用**并用记录输入重放校验。**面向不可逆动作 + 不可信 Web 内容** |

### 6.2 🧠 记忆 / 状态 / 上下文

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.31314** | **When LLMs Forget What They Believe: State Integrity Collapse** | 定义 **State Integrity Collapse**：模型在记忆里保留了约束，却不再在后续轮次应用它。StateTrack-Bench 覆盖数值/格式/角色/事实记忆/逻辑规则五类约束，7 个 provider 快照 × 5 个深度探针，**严格联合保持率 62.4%–100.0%**；**分叉回溯审计显示 88.6% 的失败是「行为漂移」而非普通遗忘**（剔除脆弱离群模型后仍为 84.4%）；深度至 50 轮仍成立 |
| **2610.31446** | （同上）动作条件化记忆验证 | 见 6.1 |

### 6.3 🌐 多 Agent / 人机协作

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.31325** | **Consistent but Biased: Chair Personas Trade Noise for Bias in Multi-Agent Clinical Decisions** | 7 个 agent 模拟科室，20 例已发表病例**原样重放**，只改主席/副手 persona（无/协商式/专断式/回避式，写成规则或仅写性格特质）。写成规则时，主席**当场手术率 93%（专断）vs 2%（回避）vs 57%（无人格）**，但手术决策本身几乎不变——**persona 主要改「是否现在做」而非「做什么」**；多轮一致性不等于正确性 |
| **2610.30780** | **ABRA: Agent-Bound UI for Human-Agent Communication beyond Chat with Reusable Views** | 把**可复用交互结构**与**任务特定语义**分离：agent 把任务语义绑定到可复用视图的交互上，并把绑定作为共享状态发布，人与 agent 在共享画布上协作。评测 4 个 LLM agent 的画布创作、owner 侧后果消解、跨 agent 调用 |
| **2610.30769** | **LLM Multi-Agent Systems Are Vulnerable to Herding and Runaway Cascades** | 复刻经典 Music Lab：暴露于累计推荐计数导致**失控级联**，集体推荐偏离真实偏好且不可预测 |
| **2610.30851** | **ADAPT for Science** | 科学优化当作两个耦合决策：**在哪搜（where）+ 怎么搜（how）**；用历史设计初始化、逐步集中算力、从执行反馈演化优化过程。在**引力波探测器设计**上用可微物理模拟器 + 8 个未见拓扑评测，匹配预算下**平均损失 0.204** |
| **2610.31003** | **Agri-SCHOLAR** | 滚动式田间建议（每几天/每周一次），LLM agent 提议农艺参数边界 + 优化器在边界内搜索 + **作物模拟器（APSIM）充当评估 oracle** 的闭环 |
| **2610.31351** | **DoorDash feature flag 清理**（延续） | 56,000+ flag / 623 repo / 1,659 stale，规则工具不足，端到端多 agent LLM 清理 |

### 6.4 🔬 其他（推理 / 隐写 / 表达）

| 论文 ID | 标题 | 一句话摘要 |
|---|---|---|
| **2610.30516** | **Beyond End-to-End Recovery: LLM Steganography via Rolewise Decomposition** | 端到端恢复率**无法区分编码失败与解码失败**。在 7,200 条编码器回复中识别出 **168 条解码器漏掉的可验证编码**，以及 **706 条通过词长/词首模式重建出私密消息**的回复——**编码器指令未显式指定的模式**。E2E 恢复会掩盖重要区分 |
| **2610.29934** | **ToM2Vec** | 连续化的「theory-of-mind token」用于多 agent 协调 |
| **2610.30108** | **Multimodal Embodied Agents: 统一能力视角** | 从 computer-use 到 robot-use 的统一能力分类学 |
| **2610.30074** | **Parallel AI Agent Collaboration as Graph-Structured Distributed Block Optimization** | 并行 agent 协作映射为图结构分布式块优化 |

---

## 7. 🔗 本场关键关联（跨源知识图谱）

1. **「批准必须绑定到具体效果」在本场从论文变成 CVE**：2610.31446（动作条件化验证）、2610.29669（对抗契约 + 多数表决）、2610.30221（R-AUT：提议/决定/执行分离 + 签名证明 + 短时效 token）、Vercel plan/scope 模型、Go/Swift SDK 把 `insufficient_scope` 写进 `WWW-Authenticate`、以及 servers v2.1.0 的 8 个漏洞——**五个独立来源在 24 小时内指向同一句话：授权不是一个布尔值，是一个带作用域、带时效、带效果的证明对象**。
2. **MCP 的安全重心已完全下沉到「实现」层**：spec 90 天未发版，但 servers 一天修 8 个 CVE、registry 一天 9 个安全提交、5 个语言 SDK 各自修跨源重定向与认证头——**协议层停滞，运行时层狂奔**。
3. **Brotli CVE-2026-111497 是「AI 参与攻防」的第一个可量化样本**：OpenAI 2 月发现、10-23 披露，跨语言扩散仅 2 天，7 个运行时同日拿到补丁。这与 10-21 的 Patch the Planet（PHP）构成**同一模式第二次出现**——**AI 发现漏洞已从个案变成流水线**。
4. **记忆安全的三层分工已经清晰**：*State Integrity Collapse*（模型是否还守约束）→ *action-conditioned verification*（这条记忆在此动作下是否需复核）→ *AMV-Guard*（门控实现）。三篇论文分别对应「状态」「决策」「执行」，是**可组合的完整链条**，而不是三个孤立问题。
5. **Claude Code 与 MCP SDK 的下一个战场是「context 与 scope 经济学」**：Python SDK 移除 schema 中的生成 title（省 token）、TS SDK 让 token 刷新携带 scope、Go SDK 把 scope 写进 401 挑战——**授权语义正在下沉到 wire format**，而上下文预算正在被 SDK 主动优化。
6. **GitHub 新仓生态出现「场景化 MCP 集群」**：麦当劳 MCP 衍生出 6+ 个独立仓（合计 >2,800★），另有 earshot（让 agent 听音）、reason-network（agent 互聊）、leanrea（8KB skill 替代 REA）——**MCP 正从「协议玩具」变成「应用脚手架」**。

---

## 8. ⚠️ 本场失败 / 降级通道

| 通道 | 现象 | 影响 | 处置 |
|---|---|---|---|
| `web_search` (duckduckgo) | `provider_error` | 无法做开放域检索 | 用 web_fetch + RSS + curl API 全量替代；**连续 8 天** |
| `web_fetch` → openai.com | `Blocked: resolves to private/internal/special-use IP address` | OpenAI 原文无法抓取 | 改用 RSS 描述字段 + 已知背景；本场 OpenAI 事件均为延续观察，未新增未证事实 |
| `web_fetch` → cerebras.ai | 404（两版 URL 均失败） | Cerebras 原文缺失 | 仅以 HN 标题/分数/评论数作证，未展开技术细节 |
| Anthropic RSS | 4 个候选 URL 全 404 | 官方公告缺位 | 改用官网 HTML 的 `__next_f` 内嵌 JSON（可拿到 title/date/category），本场仅提取到 2 条新闻级条目 |
| LangChain blog RSS | `/rss/` 现返回 Webflow HTML（216KB），非 XML | 解析失败 | 本场未采信 LangChain 内容 |
| Google AI RSS | 旧 URL 301 | 需跟随后解析 | 已用 `curl -L` 跟随，RSS 正常（30 items）|
| arXiv 周末无新批次 | cs.AI 最新仍 10-22 | 本场 arXiv 增量为 0 | 已用 200 条拉取核验批次边界，并转而系统挖掘 cs.MA 25 篇 |

---

## 9. 🎯 下场 (10-27 周一) 关注清单

| # | 关注点 | 判定方式 |
|---|---|---|
| 1 | **arXiv 周一批次释放**（10-26 提交，10-27 可见） | cs.AI / cs.MA `submittedDate` 分布，ID 是否突破 2610.31667 |
| 2 | **MCP spec release**（连续 10 场 90 天） | `modelcontextprotocol/modelcontextprotocol` tags + releases |
| 3 | **servers v2.1.0 之后是否有 v2.1.1 / 2.0.2 补漏**（Windows TOCTOU 仅部分修复） | GitHub releases + security-advisories |
| 4 | **是否还有其他仓发布 GHSA**（ext-auth / registry / SDK 层） | `orgs/modelcontextprotocol/repos` + 各仓 advisories |
| 5 | **governance-wg 首个产出**（10-19 已建工作组结构） | spec 仓 SEP/PR + governance-wg commits |
| 6 | **Go SDK 是否发 v1.9.0**（release 停滞 41 天，代码在修安全） | `modelcontextprotocol/go-sdk` releases |
| 7 | **CVE-2026-111497 后续影响面**（Apache/Nginx 之外的服务；AI agent 常驻 HTTP 客户端） | HN / advisories / 各语言公告 |
| 8 | **Kimi K3.1 Pro 权重（11-04 前）** | HuggingFace / GitHub release |
| 9 | **`web_search` provider 是否恢复**（已连续 8 天空档） | 需排查 duckduckgo 配置 |
| 10 | **SDK schema/title 优化是否扩散**（Python 移除生成 title 后，TS/Rust 是否跟进） | 各 SDK commits |

---

## 10. 🔧 产出物清单

| 文件 | 内容 |
|---|---|
| `heartbeat/nightly-scout-2026-10-26.md` | 本报告 |
| `memory/nightly-scout-2026-10-26.md` | 记忆版摘要 |
| `graphify-out/2026-10-26/snapshot.json` | 本场快照图（303 节点 / 561 边）|
| `graphify-out/2026-10-26/manifest.json` | 本场 manifest |
| `graphify-out/raw/scout-2026-10-26-corpus.md` | 语料（273,409 字符 / 140 arXiv 条目）|
| `graphify-out/graph.json` | **主图已更新**：504 节点 / 1207 边 / 48 社区（+147 节点 / +468 边）|
| `graphify-out/GRAPH_REPORT.md` | 图报告已重新生成 |
| `graphify-out/graph.html` | 交互图已刷新（499,739 字节）|
| `scout-raw/*.json`, `*.xml`, `*.html` | 全部原始证据（arXiv / GitHub / GHSA / HN / RSS / 文章）|

---

_🤖 NightOps-Scout · 2026-10-26 00:45 CST · 数据截止 2026-10-25 16:45 UTC_
