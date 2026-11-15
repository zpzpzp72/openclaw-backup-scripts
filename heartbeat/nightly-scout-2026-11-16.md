# 夜间 Scout 报告 · 2026-11-16（执行于 01:30–01:45 CST）

采集窗口：2026-11-15 01:30 → 2026-11-16 01:30 CST ｜ Scopes：AI / Agents / MCP（arXiv cs.AI + cs.MA + MCP 检索集、GitHub releases/commits/advisories、HN top30、RSS、The Decoder 文章页、Anthropic newsroom）

> **本场是"上游全静默、新闻层高信息量"的窗口**：arXiv 三个查询解析 280 条、**真实新增 0**（最新提交仍为 2026-11-12T18:59:06Z，周末 + 周一未放新批次），已用**全量 1452 个历史 id 比对**确认非采集故障；GitHub **新 tag 0 / 新 commit 17**、GHSA **连续第 3 窗零新增**；OpenAI RSS 与 Google AI blog 同样零变化。真正的信号全部来自部署层与地缘层：**美团 LongCat-2.5 全程未用英伟达芯片训练**、**Megaspeed 疑似为中方牵线 120 亿美元英伟达芯片订单**、**Anthropic 披露近 9010 亿美元算力承诺**——三条独立信号指向同一个结论：**模型可得性正在从「基准问题」变成「供应链与地缘政治问题」**。

## 📊 采集与产出总览

| 组件 | 状态 | 说明 |
|---|:---:|---|
| arXiv 抓取（cs.AI 100 / cs.MA 60 / MCP 工具-代理检索集 120） | ✅ | 解析 280 条、去重后**新增 0**（最新提交 2026-11-12；与 1452 个历史 id 全量比对确认） |
| GitHub releases | ✅ | 11 个仓库各取最新 4 条；**新 tag 0**（与 1115 快照 tag 集完全一致） |
| GitHub commits | ✅ | 5 仓库共 48 条；**新 commit 17**（claude-code 15 条 `chore: Update mods/` + vercel/ai 2 条），MCP spec / servers / openai-python 0 新增 |
| 安全通告（servers + registry GHSA） | ✅ | servers 仍 21 条、registry 仍 5 条，**连续第 3 窗零新增** |
| HN top30 | ✅ | 30 条取回；**30/30 与昨夜不同**（换血率 100%）；头条 "SpaceX catches the Starship to end Flight 15" 1495 分，但 AI/agent 主题仅 6 条 |
| RSS（OpenAI news / The Decoder / Google AI blog） | ✅ | OpenAI 1387 items（**与 1115 完全一致，0 新增**，最新条目仍是 11-13 的 ChatGPT Wallet）；Decoder 10 items（**+5**）；Google AI blog 仍返回 299 B 空壳（**连续第 9 窗**） |
| The Decoder 文章页 | ✅ | 本窗新增 5 篇正文抓取成功（120–134 KB），另结转 1114/1115 的 12 篇 |
| Anthropic newsroom | ✅ | 344 KB 页面抓取成功，26 条链接（新增 S-1 上市申请条目） |
| 知识图谱（graphify） | ✅ | 快照 121 节点 / 217 边 → 合并主图 **3,005 节点 / 7,292 边 / 37 社区**（GRAPH_REPORT.md + graph.html 已再生） |
| LanceDB（nightly-scout 表） | ✅ | **+8 行**（news 5 / engineering 2 / trend 1）→ 总 **568 行** |
| 本报告 | ✅ | heartbeat/nightly-scout-2026-11-16.md |

---

## 0️⃣ 本机状态巡检（HEARTBEAT 清单）

| 检查项 | 状态 | 实测 |
|---|:---:|---|
| **NAS 备份** | 🟢 **已恢复并连续** | `/mnt/h` 7.2T 98% 满、**可用 180G**（11-15 清理回收站释放 185 GB 后保持）；**`openclaw-20261115-0300.tgz` 已正常产出**（6.53 GB，11-15 03:15），backup-summary-push 日志显示"已推送并记录: openclaw-20261115-0300.tgz"。**11-15 断档 233 小时的问题已确认闭环** |
| nas-recycle-guard | 🟢 | 11-15 23:23 "NAS 可用 180G >= 阈值 64G，无需清理(跳过)"——守护脚本自动跳过，未误删 |
| 本机 native backup | 🟢 | 11-15 03:40 成功（5.8 G → `/home/zhiping/openclaw-backups/`，verify OK，剩余 796G） |
| 每日新闻摘要 cron | ✅ | 11-15 08:00 场成功（`reports/news_digest_20261115_080310.html` 20,490 B + 080603 重复产物；飞书 message_id `om_x100b60bb22f998a4dc1584209603946`）。今日 08:00 场待观察 |
| MiniMax API | ✅ | 直连 `api.minimaxi.com` **HTTP 200 / 0.24 s**（无鉴权时返回 status_code 1004，说明端点本身通） |
| OpenRouter API | 🔴 | 余额 **total_credits: 0**（用 finance agent 的 `auth-profiles.json` 里的 sk-or-v1 key 实测 `/api/v1/credits`），**连续第 6 窗为 0** |
| 代理 25017 / 端口 8080 | ✅ | 25017 TCP 可达；8080 FastAPI（pid 800）在监听 |
| gateway 795 | 🟡 | RSS **4.19 GB**（watchdog 趋势 **+2.57 MB/h**，预测 1698 小时后才触及 8GB → **10 月式泄漏未复现**）；uptime **1d05h26m**；CPU **100% 满载**（watchdog 每小时 WARN，已连续多窗，属常驻告警而非突发） |
| model-fetch | 🟢 | 今日 01:36 止 **ok=21 err=0**，429 仅 2 次；昨日全天 ok=320 err=4 → **MiniMax 配额压力继续收敛** |
| SQLite session reclamation | 🔴 **仍未解除** | main 库 mtime 停在 **11-15 23:37**（health/life 等库 11-16 01:13 有 shm 活动但主文件不落盘）；**health agent 库 mtime 仍停在 2026-11-05 07:18:49**，heartbeat-health 连续 **error 32 次**（昨日 9x → 今日 32x，累计在涨） |
| cron 总览 | 🟡 | **30 jobs**（比 11-15 的 31 少 1，需确认是否有意合并）、triggersEnabled=true。**Scout NightOps / Life / Coder / Orchestrator NightOps 全部 ok**；heartbeat-* 系列多数 skipped；**唯一 error 是 heartbeat-health (32x)**，根因仍是 "SQLite session reclamation commit checkpoint expired" |

### ⚠️ 唯一未解 P0：heartbeat-health 32x（需要一次 gateway 重启）

- 现象：`modelcontextprotocol` 不相关。`openclaw cron list` 显示 heartbeat-health 连续 32 次 error，最后一次 11-16 00:40。
- 根因（11-15 已定位，本场复核仍成立）：`~/.openclaw/agents/health/agent/openclaw-agent.sqlite` 主文件 mtime 停在 **2026-11-05 07:18:49**，gateway 持有 fd 但从不写入；副本写入与 integrity 检查均正常 → **库本身没坏，是写入冻结**。
- 已验证有效手段：**重启 gateway**（11-14 用同一手段修好了 main 库）。
- 本场**未擅自重启**——gateway 995 已连续运行 29 小时且当前有多个 agent 作业在跑，强行重启会中断在跑作业（含本场自己）。建议 ZP 在空窗期手动 `/restart`，重启后可同时确认 health 库写入恢复与 32x 错误计数归零。

---

## 1️⃣ 要闻 Top（news）

- **Claude Fable 5.2 不是"生成"图像，是"画"图像**（The Decoder，11-15）。Anthropic 的新模型通过**写 1,000–2,000 行 Python 程序驱动一个模拟画笔引擎**，在虚拟画布上放置约 **70 万次模拟笔触**（停车库购物车照片级场景），复现刷毛纹理、颜料上墙方式以及"画错了再覆盖掉"的过程。**不使用外部图像模型，也不使用任何预渲染/描摹源图**。Anthropic 内部 RoboDojo Sim 基准 **64.9% vs GPT-6 Astra 的 29.8%**，但真实机械臂测试中**速度和精细运动控制落后**。为回应 Opus 5.5 被批"只会模仿既有艺术"，Fable 5.2 会**自创画家人设**（虚构背景故事 + 一致风格），开发者用评论在中途改笔画。
  **含义：从像素空间生成转向程序空间生成。**图像合成正在变成 agentic 工具选择问题——与同窗 OpenAI 解散机器人团队、Runway 开源 Praxis-1 机器人控制器是同一条主线。
- **美团开源 1.6 万亿参数 agent 模型，全程未碰英伟达 GPU**（The Decoder，11-15）。LongCat-2.5 **完全用中国硬件训练**，MoE 结构、每 token 仅激活约 **480 亿 / 1.6 万亿**参数，API 上下文最高 **100 万 token**、输出最长 **12.8 万 token**，**把图像转成离散 token 与文本同处理**（而非外挂图像编码器），支持开关 reasoning。编码基准达到**几个月前 Claude Opus 5 的水平**。RL 阶段用**真实 GitHub PR 任务 + 复现的 agent 失败案例**，训练沙箱里**断网、删 Git 历史与缓存文件**，再用语言模型检查解法是否作弊，并从多个专用教师模型蒸馏 agent/推理/对话能力。**权重与激活 4-bit 量化**以匹配国产芯片原生能力，吞吐较 8-bit **提升 43.3%（prompt）/ 42.77%（生成）**，**样例部署跑在 194 颗华为芯片上**。
  **含义：这是对出口管制的直接技术反制，而且效果已经追平前沿闭源。**
- **Anthropic CEO Amodei：算力采购是"公司面临的最深层的商业困境"**（The Decoder，11-14）。在 JPMorgan 纽约投资者活动上、与 Jamie Dimon 对谈时，Amodei 称算力必须**提前一到两年采购**，而没人知道收入能否覆盖：买少了影响服务与营收，买多了"会在财务上过度扩张"。已承诺**近 9010 亿美元**（多数是算力与芯片，据 Bloomberg），**其中约 710 亿在 2027 年 9 月前到期**——这个数字**超过标普 500 中约三分之二公司的市值**。IPO（11-19 上市，11-18 定价）正是为了建现金缓冲以承受支出与收入的错配。今年 2 月 Amodei 已警告过 2027 年底起可能买 1 万亿美元算力。
  **含义：这是同窗"每个验证通过答案的成本"讨论的成本侧硬数字。**
- **澳大利亚央行：AI 首先冲击的是年轻从业者**（The Decoder，11-15）。RBA 的 Mike Major 建了一套监测系统，聚焦入门级工人与高 AI 暴露职业（编程、文书、客服）。自 2022 年底 ChatGPT 上线以来**各群体招聘岗位数普遍下滑，最高暴露组降幅最大**；该组 **15–24 岁**青年与应届大学毕业生**就业率更弱、失业率更高**，而**同龄段年长者就业反升**。作者明确警告**不构成因果**，且只度量"理论暴露"而非企业实际使用。旁证：Stanford 2025-08 研究（美国数百万薪资记录）显示 AI 高暴露职业中 22–25 岁就业相对下降 **13%**，年轻软件开发者近 **20%**；Anthropic 2026-03 研究同群体求职成功率降约 **14%**；**Anthropic 内部数据显示技术岗初级招聘占比从 27% 降到 9%**，2026 年 8 月 AI agent 记录的工时已是人类的 6 倍。
- **Megaspeed 疑似为中方牵线近 120 亿美元英伟达芯片订单**（The Decoder，11-15，更新）。据 WSJ 审阅的文件，Megaspeed 在 **2024-03 至 2025-06** 间为多家中国企业安排了近 **120 亿美元**的英伟达高性能芯片订单，**几十万颗**本应被出口管制拦下的芯片；该公司归**黄仁勋前女友 Alice Huang**所有，因把**阿里巴巴**算作大客户而作为英伟达云合作伙伴获得稀缺芯片优先获取权。英伟达官方口径是六个月中国收入 **124 亿美元（占 7%）**，而做空机构 Culper Research 估算**上财年超 20% 收入来自中国客户**——即真实敞口约为官方口径的 3 倍。更新称 Megaspeed 对 Reuters 声明 Alice Huang 已于 2025-08-30 正式离开公司、目前无职务，公司称业务"合法"并已聘外部律师做内部调查；"她可能是中国间谍"属未证实猜测。
  **含义：与前两窗的 Blackwell 指纹取证、以及本窗美团自研，构成连续三窗的硬件获取信号。**

---

## 2️⃣ 上游工程观察

**上游本窗同样近乎静默**，但静默的"形状"变了：

- **GitHub 新 tag = 0**（11 个仓库，全部 tag 集与 1115 快照逐条一致）。连续两窗零发版。
- **新 commit = 17**：claude-code **15 条全部是自动化的 `chore: Update mods/`**（11-15 00:26Z → 16:52Z），vercel/ai **2 条**（`test(mcp): increase timeout for Windows npx spawn tests` #25062、`fix(ai): validate JSON values in UI message metadata in a single pass` #25046）。MCP spec / MCP servers / openai-python **0 新增**。
- **GHSA 零新增**（servers 21 / registry 5），**连续第 3 窗**。1114 窗 servers 曾新增 4 条并伴随 v2.4.0 发版。
- **OpenAI news RSS 1387 条逐条一致（0 新增）**，最新仍是 11-13 的 "Introducing ChatGPT Wallet"。**Google AI blog RSS 连续第 9 窗只返回 299 B 空壳**——建议正式从采集清单降级。
- **Anthropic newsroom** 列表新增两条：S-1 上市申请（10-26）与公共利益基金（10-18），并确认 **Claude Fable 5.2 / Mythos 5.2 于 11-09 发布**（对应本窗头条新闻）。

---

## 3️⃣ 趋势判定

**窗口特征：零新增 + 三重硬件/算力信号收敛。**

| 维度 | 11-15 窗 | 11-16 窗 | 判定 |
|---|:---:|:---:|---|
| arXiv 新增 | 0 | 0 | 连续两窗零——周末效应已过，**周一未放新批次**，非采集故障 |
| GitHub 新 tag | 0 | 0 | 连续两窗零发版 |
| GitHub 新 commit | 2 | 17 | 回升但全是自动化 chore + 2 条真实修复 |
| GHSA 新增 | 0 | 0 | 连续第 3 窗零 |
| OpenAI RSS 新增 | 0 | 0 | 自 11-13 起冻结 |
| Google AI blog RSS | 299 B 空 | 299 B 空 | **连续第 9 窗结构性失效** |
| HN top30 换血 | 19/30 | **30/30** | 全换血，但 AI 主题仅 6 条 |
| 知识图谱 | 2,975 节点 | **3,005 节点**（+30） | 增量全部来自 release/advisory/news 侧 |
| LanceDB 行数 | 560 | **568**（+8） | — |

**本窗的核心趋势句**：*上游版本流已经停摆（零发版、零论文、零通告），但产业与地缘信号在加密——三条独立新闻分别从训练硬件（美团）、分销渠道（Megaspeed）、资本开支（Anthropic 9010 亿）指向同一件事：**前沿算力的可得性正在成为 agent 产品可行性的第一约束，而不是单次调用价格。***

**推论**：如果 11-17 窗上游仍零新增，Scout 的信号价值将从"版本追踪"整体转向"部署层叙事追踪"，采集清单应该做减法（Google AI blog 源下线、GitHub tag 轮询降频到每周），把省下的预算投到**中国模型/硬件侧的英文与中文双源监控**（本窗唯一有实质信息量的三条恰好全在这一侧）。

---

## 4️⃣ 产物清单

| 产物 | 路径 |
|---|---|
| 本报告 | `heartbeat/nightly-scout-2026-11-16.md` |
| 原始语料 | `graphify-out/raw/scout-2026-11-16-corpus.md`（582,003 B） |
| 图谱快照 | `graphify-out/2026-11-16/snapshot.json`（121 节点 / 217 边）+ `manifest.json` |
| 主图谱 | `graphify-out/graph.json`（**3,005 节点 / 7,292 边 / 37 社区**，合并前已备份 `graph.json.bak.20261116-0136`） |
| 图谱报告 / HTML | `graphify-out/GRAPH_REPORT.md`（前版备份 `.bak.20261116`）+ `graphify-out/graph.html`（3.0 MB） |
| LanceDB 行 | `rows_1116.json`（8 行）→ `~/.openclaw/memory/lancedb-pro` 表 `nightly-scout`（560 → **568 行**） |
| 采集脚本 | `fetch_1116.sh` / `fetch_gh_1116.sh` / `fetch_pages_1116.sh` |
| 构建脚本 | `prep_arxiv_1116.py` / `build_corpus_1116.py` / `build_graph_1116.py` / `merge_graph_1116.py` / `build_rows_1116.py` / `update_lancedb_1116.py` |
| 每日笔记 | `agents/scout/memory/2026-11-16.md` |

---

## 5️⃣ P0 / P1 清单

**P0**
1. 🔴 **重启 gateway 一次** —— 修 `heartbeat-health` 连续 **32x** error（health 库写入冻结，mtime 停在 11-05 07:18:49）。11-14 同样手段已验证有效。**ZP 空窗手动 `/restart`**。
2. 🔴 **OpenRouter 余额 0**（连续第 6 窗）—— 充值可把新闻摘要从全 MiniMax 兜底的 ~6 分钟压下来，属 ZP 决策。

**P1**
3. 🟡 **Google AI blog RSS 降级**（连续第 9 窗 299 B 空壳）—— 从采集清单移除或换入口。
4. 🟡 **合并重复 NightOps 作业**（0597835a 工作日版 vs c46eeb63 每日版）；本窗 cron 总数从 31 → 30，需确认是有意合并还是配置丢失。
5. 🟡 **跟踪 Claude Fable 5.2 的 RoboDojo 64.9% 与真实机械臂落后的背离** —— 程序空间生成 vs 扩散空间生成的取舍，值得下一窗找一手材料（Anthropic 官方模型卡 / Jake Eaton 的 X 原帖）。
6. 🟢 **WSL/ 中 11-05 之前现存归档**（10-27 ~ 11-05 共 10 份 ≈ 63 GB）仍在 NAS 上，NAS 已回到 180G 可用，暂不急。

**已闭环**
- ✅ NAS 备份断档（233 小时）—— 11-15 03:00 已正常产出 `openclaw-20261115-0300.tgz`（6.53 GB）并推送成功。
- ✅ MiniMax 429 配额压力持续收敛（今日 2 次，vs 10-27 峰值 1256 次/日）。
- ✅ Gateway 10 月式内存泄漏未复现（4.19 GB，+2.57 MB/h，预测 1698 小时后触阈）。
