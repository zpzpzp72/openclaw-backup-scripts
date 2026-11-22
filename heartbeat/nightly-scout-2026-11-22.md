# Scout NightOps — 2026-11-22 21:45 (Asia/Shanghai)

> **本场覆盖 5.5 天**：宿主机 **2026-11-17 20:06 关机 → 2026-11-22 21:38 重启**（`last -x` 确认），这是本系列最长盲窗。上游 backlog 一次性全部落地。

## 0. 心跳检查清单

| 项目 | 状态 | 证据 |
|---|---|---|
| DIRECTIVE.md | 无新指令（仅"暂无指令"） | 空扫描 |
| 每日新闻摘要 | ✅ 21:46 场已产出 `news_digest_20261122_214605.html`（20,559 B） | `workspace/reports/`；crontab `0 8 * * *` 侧因关机跳过 11-18~11-22 的 08:00 场 |
| MiniMax API | ✅ 直连 200 / 0.32 s | curl 实测 `api.minimaxi.com` |
| OpenRouter API | 🔴 `total_credits: 0` — **连续第 8 窗为 0** | finance agent `auth-profiles.json` 的 key 查 `/api/v1/credits` |
| 代理 25017 | ✅ TCP 可达 | `172.18.160.1:25017` TCP_OK |
| 端口 8080 FastAPI | ✅ 在监听（根路径 404 属正常） | `ss -ltnp` |
| NAS 备份 | 🟢 **重启后自动补跑成功** | `openclaw-20261122-2138.tgz` 6,104,099,260 B；/mnt/h 可用 379G |
| 本机 native backup | 🟢 21:38:44 起跑（`native-backup.log`），keep=7，可用 786G | — |
| gateway RSS | 🟢 3.03 GB（PID 695，uptime 9m32s） | 刚重启，无历史可比 |
| gateway CPU | 🟡 165%（多核折算 ≈1.65 核） | 启动爬升期，待观察 |
| cron 总览 | 🟡 30 jobs | 见下 |
| memory | ✅ 已新建 `agents/scout/memory/2026-11-22.md` | — |

### cron 失败情况
- `heartbeat:orchestrator` **error** — `agent orchestrator unavailable (SQLite session reclamation commit ...)`
- `heartbeat:finance` **error** — 同上
- `Orchestrator NightOps` **error** — 同上
- `【NightOps 记忆体系讨论】` **error**
- `heartbeat:health` ✅ **本场由 error (76x) 转为 skipped** — 健康库已解冻
- `heartbeat:main` running；`NightOps-Scout/Life/Coder` running

### agent 库 mtime（写入冻结复核）
| agent | mtime | 判定 |
|---|---|---|
| main | 11-22 21:43 | ✅ 正常 |
| scout | 11-22 21:48 | ✅ 正常 |
| coder | 11-22 21:48 | ✅ 正常 |
| life | 11-22 21:48 | ✅ 正常 |
| work | 11-22 21:40 | ✅ 正常 |
| **health** | **11-16 04:13** | 🔴 **仍冻结在 11-16**（昨日报告的 5 库冻结问题**未随重启解除**） |
| **finance** | **11-16 04:12** | 🔴 同上 |
| **orchestrator** | **11-17 04:12** | 🔴 同上 |

> **关键结论修正**：11-17 报告假设"重启 gateway 即可解冻 health 库"。本次宿主机**已整体重启**，health/finance/orchestrator 三个库 mtime **依然停在 11-16/11-17**，而 main/work/scout/coder/life 全部正常。→ **假设被证伪**。这三个库是同一类"该 agent 从未被成功调度"的状态（finance/orchestrator 的 heartbeat 报 `agent X unavailable`），health 则报 skipped。需要单独诊断这三个库，**不是全局 SQLite 问题**。

---

## 1. 趋势扫描产出

- 产物：`heartbeat/nightly-scout-2026-11-22.md`（本文件）、`graphify-out/raw/scout-2026-11-22-corpus.md`（732,680 B）、`graphify-out/2026-11-22/{snapshot,manifest}.json`
- 图谱主图：**3,597 节点 / 8,621 边 / 39 社区**（+442 节点 / +951 边；合并前已备份 `graph.json.bak.20261122-2200`）
- LanceDB `nightly-scout`：**575 → 588 行**（+13：news 9 / engineering 3 / trend 1）

### 数据源与采集量
| 源 | 量 | 备注 |
|---|---|---|
| arXiv cs.AI / cs.MA / MCP-tool-agent | 400 解析 → **329 新** | 对全部 1566 个历史 id 全量比对确认，非单窗 diff |
| GitHub releases × 11 repo | **28 个新 tag**（11-16 之后） | 走认证 `gh api`（未认证 api.github.com 撞 60 次/小时限流，已回落） |
| GitHub commits × 6 repo | 60 条 | — |
| GHSA advisory | **servers 29（+8）/ registry 5（+0）** | 打破连续 4 窗零新增 |
| HackerNews top30 | 30 条（**30/30 换血**） | — |
| OpenAI RSS | 1421 条（**+24**） | 本系列单窗最大增量 |
| The Decoder RSS | 10 条 | — |
| Google AI blog RSS | 20 条 | 11-17 修的 `curl -L` 补丁持续有效 |
| 正文页 | 15 篇（8 Decoder / 3 OpenAI / OpenRouter / Better Data Center / Google AI blog） | — |

---

## 2. 上游三大信号

### 2.1 工具层成为最大攻击面（🔴 破 4 窗静默）

**MCP servers 一口气发 8 个新 GHSA，全部在 2026-11-18**（紧接 servers v2.5.0 发布）：

- `GHSA-h2g3-rwxm-xfm3` (high) — git_merge 执行仓库自身 config 的 `gc.recentObjectsHook`
- `GHSA-87qg-cmw8-jc5m` (high) — promisor 配置在 lazy fetch 时执行程序
- `GHSA-9vjp-x34c-xg6v` (high) — 被合并分支创建的 config include 在 git_merge 时执行命令
- `GHSA-pm7p-vphh-2cg7` (high) — 仓库自身 config 仍可执行命令（加固漏了空 driver name）
- `GHSA-r2q8-f657-4r56` (medium) — 构造的 `.git/index` 让只读工具返回 `--repository` 边界外的文件
- `GHSA-8wv7-r664-7594` (high) — submodule 自身 config 在 `git_diff` 上仍跑程序（`diff.submodule=diff`）
- `GHSA-rq2p-q7c4-6g27` (low) — 校验后 symlink 置换，目录列表工具返回 `allowedDirectories` 外条目名
- `GHSA-38j4-j742-j7r3` (low) — server-everything gzip fetch SSRF 守卫仍把 NAT64 `64:ff9b::/96` 当公网

**8 个里 6 个集中在 mcp-server-git，根因是同一个**：git MCP server = 命令执行原语，控制面是仓库里的 config 文件；每一次加固只堵了一条路径，另一条 config 路径仍然可达。**这已经是第 4 次出现"修一条、另一条还在"的模式** —— 建议对 mcp-server-git 做一次配置加载路径的整体收敛，而不是逐条打补丁。

MCP registry 侧 0 新增（仍 5 条）。

### 2.2 推理路由层偷密钥（🔴 首次硬证据）

Dragos 用 **200 万次带假凭据的 AI 请求**（2026-07 ~ 2026-11）测出：
- **至少 3 家 provider 被入侵**，三家都不知道自己被攻破
- 最大一起事件里攻击者捞走**数百个 AWS key**，包括 provider **已拒绝处理**的请求里的 key；几小时内即测试密钥、翻 S3、尝试建立持久访问；一人用了 AI 攻击工具 **ARTEX**
- **模型市场转售商**不用任何漏洞就能读用户请求（只需挂最低价 + 打开日志）；一例法国住宅 IP 用截获密码 SSH 登录
- **ZDR（Zero Data Retention）普遍形同虚设**：某中国 AI lab 在**超过一半**请求里访问了秘密测试 URL（哪怕请求走美国 provider）；某美国 provider 在**两个多月后**仍在爬测试 URL；一个秘密链接在请求 24 天后出现在**内部飞书聊天**里，2 分钟内被北京/上海 3 台电脑 3 台手机打开

OpenRouter 已**下架 3 家 provider + 撤销 125 个 endpoint 的 ZDR 资格**，并称会把该测试方法纳入常态检查。

> **对本工作区的直接含义**：任何把 API key 放进 prompt 的 agent 部署，风险面在**路由层**而不在模型厂商。OpenRouter 恰好是本工作区的备用 API（虽然余额为 0）。

### 2.3 上下文从"预算"变成"可查询索引"（🟢 产业与论文同向）

同窗三个独立信号指向同一结论：
- **Nvidia 研究团队**：超长上下文窗口是死路 —— 很多测试里**周期性摘要 + 定向查找与全量加载效果相当**，而贵得多（GPT-4 8,192 → GPT 5.6 Sol 约 100 万 token，120 倍）
- **Google**：Gemini API 上线 **Tool Retrieval**，工具按需检索而非全量塞进每轮上下文
- **arXiv 329 篇里 memory 类 59 篇**，主干全是同一问题：Forget Freely Grep Later（无索引无损记忆）、MemFolder（结构化记忆折叠）、RAG in a Trenchcoat（何时最小记忆够用）、CompAct-Bench（长任务工作上下文压缩）、HEAMS（agent 记忆系统整体评测）

**arXiv 主题分布**：agent-safety 171 / memory 59 / eval-bench 29 / multi-agent 21 / tool-use 17 / MCP 13 / general 10 / planning 4 / enterprise 3 / science 2。
值得单独标出的：**ToolPulse**（工具型 agent 的侧信道窃听）、**When Tool Names Are Not Identities**（MCP provider 错绑 —— 工具标签 ≠ 工具身份）、**ROGUE-AI**（让 agent 安全事件可复现）、**Weighing the Envelope**（单 agent 包络层防御的组件权重与仲裁）、**Evidence Governance for Tool-Augmented Medical Agents**（并非所有证据都可采信）。

---

## 3. 其它值得记的事件

- **🟢 Riemann 假设机器验证落地**：Anthropic 数学家 Levent Alpöge 称与 Claude 合作给出证明并**用 Lean 写成可机验形式**；11-22 Lean/Mathlib 社区**正式确认正确**。但**几小时后 Stanford 就发布了纯人工的独立竞争稿**（Alessandro Masullo）。→ **验证不再是瓶颈，两条路径同时到达才是**。方法基于 Stepanov 思路（用特殊数学变换链模拟对整数的微分）。
- **🔴 GPT-6.2 Astra/Sol 透明度下降**：Artificial Analysis 实测，答案长度 −34~40%（Astra 352→210 词），标题数 1.99→0.11，但 **Admits Uncertainty 从 96 掉到 24**（Sol 98→51），Organization Index 从 70 掉到 11。→ 更快更直接，但**更少承认不知道** —— 对长程 agent 是反方向。
- **🔴 Nasdaq 100 单周 −10.4%**（疫情以来最差），距 10 月高点 −20%；Nvidia 单日 −14%（SEC 正在审查其会计）；美股半导体指数 −10.7%；Anthropic 上市次日 −9.1%。→ **AI 资本开支第一次被公开市场重新定价**，而非被模型榜单定价。
- **🟢 OpenAI 对抗性蒸馏防御**：GPT-6.2 Astra 下 **protected reasoning 提取攻击成功率 54.0% → 0.2%**。同周 Anthropic 也发《Strengthening our defenses against distillation attacks》。→ 两家同周回应同一威胁。
- **🟡 Anthropic 能源结构**：Better Data Center Project 估算 2028 年 Anthropic 电力 **87% 天然气 / 11% 煤**，2028 年或排放 **3200 万吨 CO₂**；已采购 1.7 GW 重型燃气轮机（34 亿美元）。全行业 177 GW 规划中的 BYOP 燃气产能（够 65% 美国家庭用电），可再生占比到 2032 年不足 20%。→ **agent 经济的真实约束不是 token 价格，是电子与燃气轮机**。
- **🟢 Inkling 2 Mini**（Thinking Machines 开源，Apache 2.0）：**looped transformer**，24 层中 12 层重复跑 3 次，用"内部多算"换"少输出 token"；26.4B 总参 / 5.4B 激活，DeepSWE v1.1 48.2%，32GB Mac 可跑。
- **🟢 GitHub 发版回暖**：28 个新 tag（11-16 以来）—— MCP registry v1.8.10/11/12、servers v2.5.0、inspector 2.16.0、go-sdk v1.9.0-pre.1、anthropic-sdk-python **v2.10.0/v2.11.0/v2.12.0**、claude-code v2.1.326~330、openai-python **v3.53.0~v3.57.0**、vercel/ai ai@5.0.292 / ai@7.0.178/179 / 新增 @ai-sdk/zai、@ai-sdk/xai。
- **⚪ MCP spec 仓库本身仍无新 tag** —— 协议文本没动，服务器与 registry 在它周围疯狂迭代。

---

## 4. 本窗口收敛出的三条结论

1. **可信度问题已经下沉到工具层和路由层。** 模型厂商把 protected reasoning 提取攻击压到 0.2%，但同一周里 MCP git server 有 6 个 high 级命令执行漏洞，推理路由层有三家 provider 偷密钥、125 个 endpoint 的 ZDR 承诺失效。**agent 的攻击面不在模型里。**
2. **成本问题已经从"每 token"转到"每上下文"。** Nvidia 说长上下文是死路，Google 上线 Tool Retrieval，论文侧 59 篇在做记忆选择与压缩 —— 而 Qwen4-Max 那种"每任务成本降 62%"的叙事在上一窗已定型。**下一个可比指标是"每任务上下文 token 数"，不是"每任务美元数"。**
3. **验证正在贬值，路径多样性在升值。** Riemann 证明已被 Lean 社区确认，但 Stanford 几小时后给出纯人工竞争稿；METR 说任务长度每 3.6 个月翻倍、200 小时任务 2027 年 7 月可达 50% 成功率。**当机器验证足够便宜，"谁能给出另一条路径"就比"谁先做出来"更有信息量。**

---

## 5. P0 待处理

1. 🔴 **health / finance / orchestrator 三个 agent 库写入仍冻结**（mtime 停在 11-16 04:1x / 11-17 04:12），**宿主机整体重启并未解除** → 修正 11-17 的"重启即可解冻"结论。这三个库对应的 heartbeat 报 `agent X unavailable`。需单独诊断，不可再寄望于重启。
2. 🔴 **OpenRouter 余额 0（连续第 8 窗）** —— 且本窗正是 OpenRouter 下架 3 家 provider、撤销 125 个 endpoint ZDR 的时候。作为备用 API 它既没钱也不安全。
3. 🔴 **mcp-server-git 配置加载路径需整体收敛** —— 6 个 high 级 GHSA 同根因，逐条打补丁已证明无效（4 次"修一条另一条还在"）。本场未擅自升级/改代码。
4. 🟡 **agent 密钥不应进 prompt** —— Dragos 证据表明路由层会读取并转售请求；建议核对本工作区所有把 key 放进上下文的调用路径。
5. 🟡 **MCP spec 仓库长期无 tag**（自 2025-06）而 registry/servers 每天发版 —— 协议与实现脱节，建议评估影响。
6. 🟡 **NAS 归档仍在累积**（WSL/ 下 11-16、11-17、11-22 三份新包，/mnt/h 可用 379G）→ 需安排 RETAIN_DAYS 清理（已知坑：NAS 删除只进 `#recycle/`，不释放空间）。
7. 🟡 **合并重复 NightOps 作业**（0597835a vs c46eeb63）仍未做。
8. 🟡 **Gateway RSS 需重新建立基线**（刚重启 3.03GB），10 月式泄漏是否复现要等 24h 后再判。

---

## 6. 本场工具修复

- **GitHub 采集改走认证 `gh api`**：未认证 `api.github.com` 在本场直接撞上 60 次/小时限流（`fetch_gh_1122.sh` 全部返回 279 字节限流壳）。已新增 `fetch_gh_1122b.sh` 用已登录的 `gh` CLI token（scopes: gist/read:org/repo/workflow），并加了"响应体含 `rate limit exceeded` 则重试"的判定。**教训：GitHub 采集必须默认走 `gh api`，不要用裸 curl。**
