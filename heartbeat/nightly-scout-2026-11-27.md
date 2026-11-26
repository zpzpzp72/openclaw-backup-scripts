# Scout NightOps — 2026-11-27

> 正常单夜窗口（宿主机自 11-22 21:38 起持续运行，第 75 小时）。上游三源齐产：arXiv **+176**（11-25 批次）、The Decoder **8/10 全新**、GitHub **7 新 tag + 85 commits**。本窗分析主线是**「能力不再是约束，物理与法律约束同时收紧」** —— 芯片出口管制把中国前沿模型的迭代周期拉长到 12 个月、蒸馏禁令切断训练数据来源，而攻击侧的攻击者边际成本已降到机器速度；评估侧则从"打分"转向"数可数的属性"。

## 0. 心跳检查清单

| 项目 | 状态 | 证据 |
|---|---|---|
| DIRECTIVE.md | 无新指令（仅"暂无指令"） | 空扫描 |
| 每日新闻摘要 | 🔴 **11-26 08:00 场内容层真失败**（非作业 error）—— 当日**未产出** HTML 文件，日报群里没收到，邮件也没有 | `news-digest-cron.log` 11-26 段：`共获取 3 条 → 去重过滤后剩 0 条 → 没有新新闻，跳过推送`；`reports/` 无 `news_digest_20261126_*.html` |
| MiniMax API | ✅ 直连 200 / 0.28 s | curl 实测 `api.minimaxi.com` |
| OpenRouter API | 🔴 `total_credits: 0` — **连续第 12 窗为 0** | 从 finance agent 库 `auth_profile_store` 提取 key 查 `/api/v1/credits` |
| 代理 25017 | ✅ TCP 可达；走代理 `github.com` 200 | `172.18.160.1:25017` |
| 端口 8080 FastAPI | ✅ 在监听（pid 700） | `ss -ltnp` |
| NAS 备份 | 🟢 `openclaw-20261126-0300.tgz`（6,278,527,849 B）已落盘；/mnt/h 可用 257G | `WSL/` 目录 + `nas-recycle-guard.log` |
| 本机 native backup | 🟢 11-26 03:51 verify OK，归档 8→7，剩余 779G | `native-backup.log` |
| NAS 回收站守卫 | 🟢 11-26 03:20 正确跳过（可用 257G ≥ 阈值 64G） | `nas-recycle-guard.log` |
| gateway RSS | 🟢 **4.83 GB**（PID 36001，uptime 3d19h59m）；watchdog 趋势 **+2,731 KB/h**，预测 1,309h 触 8GB | ps + `logs/cron-watchdog.log` 00:15 |
| gateway CPU | 🟢 **23%** | watchdog 00:15 |
| model-fetch | 🟢 今日 ok=350 err=6（err 低位） | watchdog |
| cron 总览 | 🟡 **30 jobs / 18 enabled** | `state/openclaw.sqlite` → `cron_jobs`（直查，绕开 CLI） |
| 外网连通性 | 🟢 本场复测全部恢复：tavily 200 / export.arxiv 200 / api.github 200 / open.feishu.cn 可达 / 代理 github 200 | curl 实测 |
| memory | ✅ `agents/scout/memory/2026-11-27.md` 已更新 | — |

### 🔴 本窗唯一可执行的新结论：**11-26 摘要不是"作业 error"，是内容层真失败**
- 上一窗结论是「作业 error(Nx) ≠ 内容失败，以产物 + om_ 回执为准」。**本窗必须区分第三种情况：作业报 error + 内容也没产出。**
- 11-26 08:04~08:06 日志显示：Tavily / SerpAPI / MiniMax 搜索 / 7 个搜索引擎 / 飞书推送**全部失败**（`Temporary failure in name resolution` + `ProxyError Tunnel 400`），最终 `共获取 3 条 → 去重 0 条 → 跳过推送`。
- 同窗旁证：`dns-drift.log` 在 **11-26 08:17~14:17 连续 7 小时 `ERROR: Could not fetch public IP`** —— 早间外网中断是系统性的，不是单脚本问题。
- 另有独立 bug：兜底推送脚本 `pick_latest_digest()` 按文件名时间戳取最新且**不限日期**，11-26 当日无产物时会选中 11-25 的报告准备重推（仅因当时网络也断才没发出去）。**已修复为「只推当日，无当日产物则跳过」**（`/home/zhiping/.openclaw/scripts/send_digest_feishu.py`）。
- **残留风险**：搜索全失败时静默「0 条跳过」，**没有任何告警** —— 本次只能靠事后翻日志才发现漏发。建议摘要链增加"抓取全失败 → 显式告警 + 保留上一份报告"的分支。

### cron 失败情况（直查 `state/openclaw.sqlite`）
- 🔴 **`heartbeat-work` error 96x**（11-24: 24x → 11-26: 72x → **11-27: 96x**）—— `SQLite session reclamation commit checkpoint expired`
- 🔴 **孤儿投递仍未自愈**：`4c89a409-533d-488f-bd2f-fb159669ae15`（`session_key=agent:work:main`，`recovery_state=unknown_after_send`，目标=本飞书群）**仍 pending，retry 410 → 554**
- 🟡 `openclaw-news-digest` error 1x —— 错误文本本窗变为 **`Context overflow: prompt too large for the model`**（此前是 `SESSION_PLACEMENT_TURN_SETTLEMENT_CLOSED`）→ 又是投递/收尾层失败，与内容层失败**叠加**在同一场
- ⚪ `LanceDB 版本清理` 41x / `DNS-Drift-Monitor` 10x / `NightOps-Dedup` 10x / `NightOps-Life` 4x / `NightOps-Orchestrator` 4x / `NightOps-Coder` 3x 均为 **enabled=0 的历史作业**，不再产生新失败
- 🟢 全部 `heartbeat:*`（coder/finance/health/life/main/orchestrator/scout）本窗状态 **skipped**（`empty-heartbeat-file` / `no-route` / `cron-in-progress`），属正常空转
- 🟢 `Scout/Life/Coder/Orchestrator NightOps` 全 ok；`Memory Dreaming Promotion` / `公网IP` / `memory-weekly-audit` / `NightOps 记忆体系讨论` / `a-stock-pr-review-reminder` 全 ok

### 租约泄漏（连续三窗缓增）
- `agent_database_leases`：**25 → 32 行**，全部 `owner_pid=36001`、`owner_start_time` 唯一值=1 → 进程仍存活 → 永不判 stale。
- gateway 未重启，故无回收。**重启仍是唯一自动回收手段**（连续三窗结论未变）。

### agent 库 mtime
scout 11-27 00:41 ✅ / main 11-26 23:30 ✅ / orchestrator 11-26 03:10 ✅ / life 11-26 03:01 ✅ / coder 11-26 03:01 ✅ / finance 11-23 04:35 🟡 / health 11-23 04:42 🟡 / **work 11-23 04:42 🔴（受害方）**

> **方法论延续**：finance/health 的 mtime 停在 11-23 但 11-24 窗已证明「mtime 停 ≠ 库冻结」，故只记为观察项；work 库是唯一有**独立错误证据**（heartbeat-work 96x + 孤儿投递 554 次重试都指向它）的库。

---

## 1. 趋势扫描产出

- 产物：`heartbeat/nightly-scout-2026-11-27.md`（本文件）、`graphify-out/raw/scout-2026-11-27-corpus.md`（471,682 B）、`graphify-out/2026-11-27/{snapshot,manifest}.json`
- 图谱主图：**4,444 节点 / 10,710 边 / 40 社区**（+236 节点 / +584 边；合并前已备份 `graph.json.bak.20261127-0050`；merge 后已重跑聚类，0 个 `community=None`）
- LanceDB `nightly-scout`：**638 → 662 行**（+24：news 12 / arxiv 11 / trend 1）

### 数据源与采集量
| 源 | 量 | 备注 |
|---|---|---|
| arXiv | 400 parsed / **176 真新增** | 对全部 2334 历史 id 全量比对；published 直方图 11-25=196、11-24=37、11-23=47、11-22=30 |
| GitHub releases | 11 repo，**7 新 tag** | openai-python v3.60.0 + vercel/ai 6 包（全部依赖 bump） |
| GitHub commits | **85** | vercel/ai 20、anthropic-sdk 20、claude-code 20、openai-python 18、MCP spec 7、**servers 0** |
| GHSA | servers 29 / registry 5，**0 新增** | **连续第 5 窗零新增** |
| HackerNews | top30，**30/30 全换血** | 头条 Aaronson "HOLY SHIT ×4"（1823 分）、1Password 安全事件（1581 分） |
| RSS OpenAI | 1430 items，**+0** | 冻结（末条仍 11-24 13:00）→ 上窗的 +8 是**积压补投**而非活跃流 |
| RSS The Decoder | 10 items，**8 全新** | 主题整体转向算力/主权 |
| RSS Google AI blog | 20 items，+0 | 末条 11-24 16:00 |
| 正文页 | **16 篇** | 8 Decoder + 1Password + nfs2root + Aaronson + code-golf + bare-metal Qwen + NYT/Photoshop + GRH Lean + Cogentic |

---

## 2. 本窗趋势分析

### ① 🔴 算力与数据两侧的约束**同时**收紧，且第一次在同一周内被量化
- **算力侧**：FT 报道 Nvidia 要求 Dell / Supermicro **停止向马来西亚、新加坡、泰国、印尼发货**（商务部 BIS 新规针对的是"通过境外云厂商租用"这一漏洞）。副作用更大：GPU Mart 老板向 CNBC 确认，**数千颗 B300 涌入二级市场**；东南亚云商有 90 天申请许可的窗口，业者称"一片混乱"；新加坡 Aolani 的字节跳动订单已有约 **5 亿美元贷款被银行叫停**。
- **数据侧**：Reuters 称 Z.AI 的约 3 万亿参数 **GLM-5.5 原定 11 月发布，大概率滑到 2027 Q1**（过渡措施是提前放出 750B 的 GLM-5.4）；Moonshot AI 失去境外算力后**迭代周期从 6 个月翻倍到 12 个月**，Kimi K4 大概率推迟到 2027 年中；因 OpenAI 与 Anthropic 封堵蒸馏抓取，Moonshot **转用 Google 与 Meta 的最新模型做训练**，并到欧洲找算力。
- **The Information 补第三块拼图**：Deepseek 内部估算，若蒸馏彻底消失，其与顶级美模型的差距会**从 3~6 个月扩大到 9 个月**；Moonshot 已取消在印尼的 **1.5 亿美元 Blackwell 订单**；MiniMax、miHoYo、阿里转向国产芯片 + 自建 RL 数据。
→ **判断**：本系列前几窗追踪的是"前沿算力可得性是第一约束"。本窗的推进是 —— **该约束现在有了对称的一侧**：不是单次调用价格，而是**可获得的数据 + 可获得芯片的交集**。模型侧能力差距（3~6 → 9 个月）与部署侧可得性差距（6 → 12 个月周期）第一次同时出现在同一周的报道里。
→ **可执行**：任何依赖"训练前沿模型"或"依赖美系算力"的路线规划，应把**芯片与数据的双约束**作为一等输入，而不是只算 token 成本。

### ② 🔴 攻击侧：攻击任务的边际成本已降到机器速度，且可**自动换模型**
- Microsoft Threat Intelligence 拆解 **ARTEX**（2026-07 发布，源码由 GitHub 用户 Autumn-27 发布后删除、仍有分发，威胁通（ThreatBook）还卖商业 Pro 版）：**框架自行分发攻击任务，失败时在不同语言模型之间切换**，直接驱动 Metasploit 等既有工具，**以机器速度运行**，防守方只有几分钟响应窗口。Microsoft 称中国与朝鲜国家背景组织已把 ARTEX 编入 Salt Typhoon / Crystal Typhoon / Onyx Sleet / Storm-0940 行动 financially motivated 的团伙也用于供应链攻击。
- 防守建议反而是**欺骗**而非封堵：诱饵系统 + **假成功信号（"fake wins"）诱导攻击 agent 自行放弃**。
→ **与上窗同源但更进一步**：上窗是"危害边际成本 2.5 美分"，本窗是**攻击本身成为一个可自适应调度模型的自动化流水线**。约束不再是"模型会不会被骗"，而是"防守方能否用同样便宜的方式制造假目标"。
→ **可执行**：agent 防御的对抗预算表必须包含**"对方可以自己换模型"**这一假设。

### ③ 🟢 1Password 事件是一次**边界的精确校准**
- 攻击者对后端执行恶意代码，下载了：客户姓名与邮箱、账号与用户标识、账号创建与最后登录时间、公钥、SRP 参数、**部分邮件邀请/配置/找回链接中的 token**、以及内部架构元数据。**保险库内容与其保护密钥均未被触及**。
- 同时攻击者复制了私有仓库源码并进入 CI/CD（含基础设施密钥）→ 1Password 已触发全部相关凭证轮换，声称服务可用性与产品安全不受影响。找回/邀请 token 需配合 SSO 或邮箱 6 位码使用，公司已把该码从 6 位数字改为 10 位字母数字。
→ **判断**：这是本系列少见的"架构赌注部分成立"的案例 —— **边界恰好落在设计处**（vault 未破），但**紧邻系统（源码、CI/CD）完全可达**。可作为 agent 威胁模型的标定样本：不要问"agent 能不能被攻破"，要问"**边界画在哪、相邻系统是否在边界外**"。

### ④ 🟢 评测侧从"打分"转向"数可数的属性"（连续第 5 窗，但本窗换了三个轴）
- **arXiv 2611.34875（Delta Residue Attribution）**：回放 **7,660 条**已解决的 GitHub Copilot CLI 轨迹（18 个前沿模型，SWE-bench Verified 6,728 + DeepSWE 932），把补丁的每个单元回退后重跑测试来判断"是否必要"。结论：**agent 补丁确实改得更多行，但大部分额外改动是加测试（61%）与加文档（13%）**；DeepSWE 上则以代码为主（58%）；agent 的代码**平均至少和人类的一样必要**（SWE-bench Verified 0.887 vs 0.864，18 个模型中 11 个更少冗余）。**SWE-bench Verified 上 11% 的代码单元仍不必要，其中 89% 会改变行为**；模型间差异大，且与 resolve rate **不相关**（SWE-bench Verified 无相关，DeepSWE 上 **负相关 −0.59**）。用 agent 可见的测试做 DRA 剪枝：recall 67% / precision 46%，**89% 剪枝后补丁仍能解决任务**。
- **arXiv 2611.34852（DRBench Pro）**：把**结构化知识覆盖率**（breadth × depth 的几何均值）作为深度研究 agent 的主指标，取代报告质量打分。
- **go/codegolf benchmark（bjin）**：把 Google 2015 年内部 code golf 的 32 题 × 8 语言搬出来，**按字节数计分**、对照真实人类纪录（GPT-6.2 Astra 首个刷新纪录）；评分是**规则化字节比较**，几乎无法被"改评分过程"作弊 —— 正好是上窗 BenchJack（10 个基准 9 个拿接近满分却没解题）所要求的形态。
→ **判断**：三件事共同指向同一方向 —— **"给 agent 一个可被 hack 的总分"这条路线正在被放弃**，改用**可核对的属性**：改了哪几行（必要/不必要）、覆盖了哪些知识分支、写了几字节。
→ **可执行**：选型与验收时，把"分数"拆成**可回滚验证的属性清单**（必要性、覆盖率、字节/行数代价）。

### ⑤ 🟢 记忆从"保真度"换到"使用期冲突"（连续第 3 窗，本窗给出了具体故障率）
- **arXiv 2611.34762（TASK Memory）**：提出**"use-time memory hallucination"** —— 记忆检索对了、放进 prompt 了，答案仍然与记忆冲突或被用到错误问题上。五个开源模型上分三类：**memory-ignoring（参数知识覆盖外部记忆）最高 46% 的查询**、memory-misapplying（把记忆安到无关实体）最高 24%，**检索 + 权重编辑叠加时升到 49%**、version confusion（版本混乱）**53%**。方案是 TASK memory = 文本笔记 + **activation steering** + 知识编辑。
- **arXiv 2611.34624（HoMe）**：把**记忆系统的 harness**（构造/维护/检索/生成所用的代码、prompt、配置）本身当作可优化对象，用会话级记忆版本 + 执行轨迹定位跨案例的共性失败机制。
- 与上窗 Leto（记忆是预测问题）、上上窗 Anthropic（记忆要会忘）构成**三窗连续推进**：保真度 → 效用 → **使用期冲突的具体分类与故障率**。

### ⑥ 🟢 产物可机器验证 ≠ 产物可被人复核（黎曼线的第 3 段，且这次有了对照）
- Scott Aaronson 长文（HN 1823 分）：在 OpenAI 与 Anthropic 的 **VP ≠ VNP** 证明、以及 Alpöge/Anthropic 的黎曼假设证明之后，OpenAI 声称**矩阵乘指数 ω 恰为 9/4**（下界匹配其 10-06 "Mathocalypse" 给出的上界）。他的震惊点有两个：这是 1960s Strassen 以来的中心谜题，**答案竟是一个有理数**；而 **AI 能证明 ω>2 形式的下界**，他原以为这不会比 P≠NP 容易多少。随后 OpenAI 又放出傅里叶变换所需线性门数的**精确下界** N(log N)^{1/2+o(1)}，改进 FFT 与其 10 月的上界。
- 配套：**lsernau/grh-lean**（808 stars / 85 forks）发布 **GRH 的精简 Lean 4 证明**（HN 509 分）—— 与 Anthropic 的 1700 万行版本对照，**"证明经济学"从"谁能复核"落到了"有人已经在做压缩版"**。
→ **判断**：上窗的教训是"编译通过 ≠ 可用产物"。本窗出现了**社区自发的应对**：既然 1700 万行不可读，就自己写一份短的。这说明**复核成本不是恒定门槛，而是一个会被社区用工程量换掉的变量** —— 谁来承担复核成本的问题，正在部分被绕过。

### ⑦ 🟢 "用代码解视觉"反超视频模型
- **arXiv 2611.34813**：把**同一批视觉推理任务**（VBVR-Pro-Bench，500 实例、5 类认知、带符号 ground truth）同时交给视频生成模型与**写程序渲染答案视频的 coding agent**，评测器统一且未经修改（规则化）→ **coding agent 是更强的视觉推理者**。
→ 与上上窗 "loop transformer 两端同时出现"、上窗 "Solve Vision with Code" 同族，但结论反直觉且可复用：**符号路径可能比原生媒介路径更可靠**。

### ⑧ 🟢 治理边界被明确切分：任务自动化 ≠ 治理委托
- Amodei 长文回应 Axios 报道（"部分 Anthropic 员工认为人类应安全地把权力交给超级智能系统"）：AI 必须由**合法民主程序**治理，政治决定应留在人类手中，**把治理交给 AI 是坏主意** —— 与他反对威权的论证"逐字相同"。但他同时认可**任务级自动化**（驾驶、癌症药物、写软件）能救很多命，只是端到端自动化有失业与"模型无监督地造新模型"的风险，且"人类宁愿自己做一些事，以保持对重要事物的参与"。
- 同期 OpenAI **Private Inference 开始试点**：查询在**可独立验证的隔离硬件**上处理；**Private Safety Processing** 让 OpenAI 在不存客户数据的前提下扫描滥用，被标记内容加密后存到**客户自己的云**里，只有受控审核系统可读。Google 的 Private AI Compute 同路。
→ **判断**：这两条一起读很清楚 —— **"自动化任务"与"委托治理"被明确切成了两件事**，而企业侧的技术方案（可验证隔离硬件 + 客户自持数据）正是为了让前者可被接受。协议侧同步有 1Password 事件作为反向标定（边界画在哪）。

### ⑨ 🟡 协议层继续长，但本窗 GitHub 侧信号极弱
- **7 个新 tag 全部是依赖 bump**：openai-python v3.60.0（内容仍有价值：spend alerts 与 response compaction 字段、**支持更新 session vaults**、明确 message retries 与 Batch 端点、Realtime 音频降噪说明、inline skill 上传限制），以及 vercel/ai 的 `ai@5.0.294 / 6.0.338 / 7.0.183` 与 `@ai-sdk/zai@1.0.14 / 2.0.24 / 3.0.59`，**全部由单个上游 commit 80d778a 驱动**（provider-utils 5.0.85、gateway 4.0.156）。
- **MCP servers 本窗 0 commit** —— 跟踪集里第一次出现完全静默的仓库。**GHSA 连续第 5 窗零新增**（servers 29 / registry 5）。
- 另：Amazon 与 Meta 就 **Muse** 谈判（Forter 数据：Muse 占全部 agentic 订单 **51%**、Grok 24%、ChatGPT 22%；Amazon 68.6 亿美元广告业务是核心分歧）；FCC 批准 SpaceX 部署**最多 100 万颗** Starmind 轨道 AI 数据中心卫星（并批准光链路失效时的无线电回传）。
→ **判断**：本窗协议/生态层缺少新的能力性发布（连续 5 窗 GHSA 零新增 + 本窗 tag 全为依赖 bump），**注意力已完全转移到算力与主权**。100 万颗卫星的授权是本窗最大胆的一条 —— 它是对"地面算力供给受限"的一条**绕开路径**，但瓶颈会转移到发射节奏与轨道碎片。

---

## 3. 趋势变化（相对 11-26 窗）

- 🔴 **供给侧双约束同时收紧且首次同日量化**：Nvidia 停发四国 + B300 涌入二级市场 + 5 亿美元贷款被叫停；GLM-5.5 滑到 2027 Q1、Moonshot 周期 6→12 个月、Deepseek 差距 3~6→9 个月
- 🔴 **攻击侧从"低边际成本"升级为"自适应流水线"**：ARTEX 自行分发任务 + 失败自动换模型 + 机器速度，防守方转向"假成功信号"欺骗
- 🔴 **heartbeat-work 72x → 96x**（三窗翻四倍），孤儿投递 retry 410 → **554** 仍 pending
- 🔴 **OpenRouter 连续第 12 窗为 0**
- 🔴 **11-26 摘要内容层真失败**（当日无产物、群内无推送）—— 修正上一窗「作业 error ≠ 内容失败」的二分法，实为三态
- 🟢 **评测从"打分"转向"可核对属性"**：补丁必要性（DRA，7,660 轨迹）、知识覆盖率（DRBench Pro）、字节数（code golf）
- 🟢 **记忆换到"使用期冲突"具体化**：memory-ignoring 46% / misapplying 24%（+编辑 49%）/ 版本混乱 53%
- 🟢 **复核成本被社区用工程量部分绕开**：grh-lean 把 GRH 证明压成短版 Lean（808 stars）
- 🟢 **治理边界被切分**：任务自动化 ≠ 治理委托（Amodei）；企业侧可验证隔离硬件 + 客户自持数据（OpenAI Private Inference）
- 🟢 **符号路径可能优于原生媒介**：coding agent 在视觉推理上反超视频模型
- 🟡 **协议/生态层静默**：GHSA 连续第 5 窗零新增、7 个新 tag 全为依赖 bump、MCP servers 0 commit
- 🟡 Gateway RSS 4.62 → 4.83 GB（+2,731 KB/h，预测 1,309h 触 8GB，10 月式泄漏仍未复现）

---

## 4. 工具/流程修复

- [x] **夜班脚本按日期模板化**：`fetch_1127.sh` / `fetch_gh_1127.sh` / `fetch_pages_1127.sh` / `prep_arxiv_1127.py` / `build_corpus_1127.py` / `build_graph_1127.py` / `merge_graph_1127.py` / `build_rows`（本窗直接生成 rows_1127.json）/ `update_lancedb_1127.py` / `regen_report_1127.py`
- [x] **修 bash 抓取函数的语法坑**：`fetch_pages_1126.sh` 里 `grab()` 用了 `[ ... ]; then` 的畸形写法（应为 `if ... ; then`），直接模板化会带崩新脚本 → 本窗重写为合法 `if` 形式并验证 16/16 页抓取成功
- [x] **修 build_corpus 的撇号语法坑**：单引号字符串里的英文撇号（`Googlers'` / `attacker'` / `patch's` / `Google's`）会破坏 Python 字符串 → 本窗统一改为无撇号措辞，并加 `tokenize` 预检
- [x] **修 build_graph 的 newids 口径 bug**：`new_ids` 用 `x['id']`（含版本号 `v1`）与去版本后的 `id_base` 比较 → 本窗改为 `x.get('id_base') or x['id'].split('v')[0]`，修正后 arXiv 节点数从 300 降到正确的 176
- [x] **正文页 md5 去重断言**：16 篇抓取页面 md5 全部互异（`md5sum | uniq -d` 为空）—— 沿用 11-26 的教训（"抓到了 ≠ 抓对了"）
- [x] **Graphify merge 后重跑聚类**（沿用 11-24 教训）：主图 40 社区、0 个 `community=None`
- [x] **cron 状态直查 state 库**（沿用 11-26）：CLI 侧 `openclaw cron list` 在部分 secret 引用下不可用 → 直查 `~/.openclaw/state/openclaw.sqlite` 的 `cron_jobs`（含 `state_json.consecutiveErrors`），本窗据此拿到 96x / 554 次重试的精确计数
- [x] **摘要兜底推送守卫**（本场另一并行巡检已完成）：`send_digest_feishu.py` 的 `pick_latest_digest()` 改为**只接受当日**文件，当日无摘要则抛 `FileNotFoundError` 跳过，避免把昨天的报告重复推到群里

---

## 5. P0 待处理

1. 🔴 **处置孤儿投递 + work 库 + 重启回收租约**（需 ZP 授权，CLI 给足 ≥300s 不要 timeout 强杀）：
   1. `openclaw doctor --state-sqlite compact` —— 清掉孤儿投递 `4c89a409-533d-488f-bd2f-fb159669ae15`（**关键动作**，retry 已 554 次）
   2. `openclaw doctor --session-sqlite recover --session-sqlite-agent work`
   3. 停 Gateway → `doctor --fix` → 重启 —— 同时回收 **32 条**泄漏租约
2. 🔴 **OpenRouter 余额 0**（连续第 12 窗）— ZP 决策充值
3. 🔴 **摘要链缺告警**：11-26 全网中断时静默「0 条跳过」，用户侧零感知。建议：抓取全失败 → 显式告警 + 保留上一份报告并标注"本场为旧内容"
4. 🟡 **评测验收改为可核对属性清单**：DRA 的"补丁必要性"、DRBench Pro 的"知识覆盖率"、code golf 的"字节数" → 替代单一总分
5. 🟡 **记忆系统验收换轴**：从保真度 → 效用（Leto）→ **使用期冲突分类**（TASK Memory 的 46% / 24% / 53%）→ 建议直接以"使用期冲突率"作为记忆系统的回归指标
6. 🟡 **自建 agent 威胁模型时按"边界 + 相邻系统"建模**：1Password 事件显示 vault 未破但源码与 CI/CD 全可达 → 不要只问"能不能被攻破"
7. 🟡 **把"算力可得性"扩成"算力 + 数据双约束"**：任何依赖训练或依赖美系算力的路线，把 GLM-5.5 延期、Moonshot 周期翻倍、Deepseek 差距 9 个月、蒸馏禁令一起算进去
8. 🟡 **防守预算按"对方会自己换模型"设计**：ARTEX 已在自动切换模型；假成功信号/诱饵是当前低成本手段
9. 🟡 **跟踪 code golf 榜单的后续**：GPT-6.2 Astra 首个刷新 2015 人类纪录，后续若多模型逼近，"字节数计分"可能成为最抗作弊的 agent 能力基准
10. 🟡 **NAS 归档累积**：`WSL/` 已 8 份（11-15~11-26），可用 257G；清理前必须先清 NAS 回收站（历史已验证：NAS 删除只进回收站不释放空间）
11. 🟡 **合并重复 NightOps 作业**（0597835a vs c46eeb63）
12. 🟡 **Gateway RSS**：4.83 GB / +2,731 KB/h / 预测 1,309h 触 8GB → 10 月式泄漏仍未复现，但已过 4.8 GB，继续观察
13. 🟡 **新增采样口**：① **补丁必要率**（DRA：11% 冗余 / 89% 改行为）② **知识覆盖率**（DRBench Pro 口径）③ **记忆使用期冲突率**（46% / 24% / 53%）④ **攻击任务单位成本与自动换模型次数**

---

**Last check: 2026-11-27 00:55 (Asia/Shanghai) — Scout NightOps**
