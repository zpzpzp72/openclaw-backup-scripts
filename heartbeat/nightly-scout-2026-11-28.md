# Scout NightOps — 2026-11-28

> 正常单夜窗口（宿主机自 11-22 21:38 起持续运行，第 76 小时）。**本窗最大事件是采集方法自身的缺陷被发现并修复**：过去数月用的 arXiv API `max_results=100/150` 会**静默截断**，上窗报告的「0 篇新增 arXiv」是截断造成的假象，不是真的空窗。用 `max_results=300` + arXiv 公告列表页作独立完备性交叉校验后，**恢复出 105 篇真新增**（含一直都在但从未被看见的 11-24 / 11-25 批次）。本窗分析主线是**「产物在变好，但对产物的校验没跟上 —— 而每一个校验器都有已知或可测的失败率，且依赖它的人看不见」**。

## 0. 心跳检查清单

| 项目 | 状态 | 证据 |
|---|---|---|
| DIRECTIVE.md | 无新指令（仅"暂无指令"） | 空扫描 |
| 每日新闻摘要 | ✅ **11-27 08:00 场成功**：`news_digest_20261127_080317.html`（19,778 B），飞书 `om_x100b7fb8c27598accf314487d2211bc` | `news-digest-cron.log` 尾部 |
| MiniMax API | ✅ 直连 200 / 0.28 s | curl 实测 `api.minimaxi.com` |
| OpenRouter API | 🔴 `total_credits: 0` — **连续第 13 窗为 0** | 从 finance agent 库 `auth_profile_store` 提取 key 查 `/api/v1/credits` |
| 代理 25017 | ✅ TCP 可达 | `172.18.160.1:25017` |
| 端口 8080 FastAPI | ✅ 在监听 | TCP 直连 |
| NAS 备份 | 🟢 `openclaw-20261126-0300.tgz` 已落盘；/mnt/h 可用 251G（97% 满） | `backup-cron.log` + `df -h /mnt/h` |
| NAS 回收站守卫 | 🟢 11-27 03:20 正确跳过（251G ≥ 阈值 64G） | `nas-recycle-guard.log` |
| 本机 native backup | 🟢 11-27 03:40 归档 `ok`；剩余 778G | `backup_runs` 表 + `df -h /` |
| gateway RSS | 🟡 **5.62 GB**（PID 36001，uptime 4d19h32m）；watchdog 趋势 **+3,493 KB/h**，预测 837h 触 8GB | ps + `logs/cron-watchdog.log` 00:15 |
| gateway CPU | 🟢 **30%** | watchdog 00:15 |
| model-fetch | 🟢 ok=350 err=6 | watchdog |
| 429 配额 | 🟢 今日 gateway 日志 0 条 429 | grep 全量日志 |
| cron 总览 | 🟡 **30 jobs / 18 enabled** | `state/openclaw.sqlite` → `cron_jobs`（直查，绕开 CLI） |
| 外网连通性 | 🟢 全部可达：tavily/serpapi 复测、export.arxiv 200、api.github 200、飞书可达、代理 25017 通 | curl 实测 + 抓取全部成功 |
| memory | ✅ `agents/scout/memory/2026-11-28.md` 已新建 | — |

### 🔴 本窗唯一可执行的新结论：**arXiv API `max_results` 静默截断，伪造了"零新增"信号**
- 上窗（11-27）报告 **"arXiv 176 真新增"**、再上窗（11-26）报告 **"266 真新增"**、本窗首轮采集算出 **0 真新增**。直觉判断是"周末无新批次"，与 11-23 窗的记录一致（那个结论后来被证明是 mtime 误读）。
- **本窗做了独立交叉校验**：抓 `arxiv.org/list/cs.AI/recent?show=250` 公告列表页（250 条）与 `cs.MA` 列表页（96 条），与 API 返回的 id 集合求差 —— **cs.AI 列表 250 条里有 92 条不在我们的 150 条 API 结果里**。
- 根因：API 查询用 `max_results=150`（cs.AI / MCP）与 `100`（cs.MA），**按 submittedDate 倒序取前 N 条**，而当某天提交量超过 N，剩余条目被丢弃且**无任何报错**。`max_results=300` 后 API 返回 300 条，仍有 20 条列表项被 API 排序/分页吃掉 —— 说明光调大参数不够。
- **最终方法**：三条独立路径取并集 —— ① API `max_results=300` 三组查询；② 公告列表页抓 id 后 `id_list` 反查；③ 对剩余未分类 id 分批 `id_list` 补捞（每批 ≤50，URL 长度限制 4094 字节，713 个 id 一次塞进去会 400）。三路并集去重后 **105 篇真新增**。
- **这一条的方法论教训可外推**：**一个有上限的数据源报"零"，与一个空的数据源报"零"在观测上不可区分**；只有用第二条通往同一数据的路径交叉校验才能区分。本系列的"零新增"结论过去几窗都直接采信了 API 返回值。
- **影响范围**：所有历史窗口的「arXiv 新增数」都可能**系统性偏低**，尤其新增密集的日子。11-26 报的 266 与 11-27 报的 176 是在同一个截断下算出来的，真实值只会更高。

### cron 失败情况（直查 `state/openclaw.sqlite`）
- 🔴 **`heartbeat-work` error 120x**（11-24: 24x → 11-26: 72x → 11-27: 96x → **11-28: 120x**）—— 四窗翻五倍，`SQLite session reclamation commit checkpoint expired`
- 🔴 **孤儿投递仍未自愈**：`4c89a409-533d-488f-bd2f-fb159669ae15`（`session_key=agent:work:main`，`recovery_state=unknown_after_send`）**仍 pending，retry 554 → 697**
- 🟡 `openclaw-news-digest` error **2x**（11-27: 1x）；本窗 11-27 场内容层已恢复正常（产物 + om_ 回执齐全），错误为收尾层
- 🟡 `Orchestrator NightOps` error 1x；其余 `NightOps-Dedup` 10x / `DNS-Drift-Monitor` 10x / `NightOps-Life` 4x / `NightOps-Orchestrator` 4x / `NightOps-Coder` 3x / `LanceDB 版本清理` 41x 均为 **enabled=0 的历史作业**
- 🟢 全部 `heartbeat:*` 本窗 **skipped**（`empty-heartbeat-file` 等空转）；`Scout/Life/Coder NightOps` 全 ok；`Memory Dreaming Promotion` / `公网IP` / `memory-weekly-audit` 等全 ok

### 租约泄漏（连续四窗缓增）
- `agent_database_leases`：**32 → 36 行**，全部 `owner_pid=36001`、`owner_start_time` 唯一值=1 → 进程仍存活 → 永不判 stale。
- gateway 未重启，故无回收。**重启仍是唯一自动回收手段**（连续四窗结论未变）。

### agent 库 mtime
scout 11-28 00:45 ✅ / main 11-27 07:50 ✅ / orchestrator 11-27 01:45 ✅ / life 11-27 03:01 ✅ / coder 11-27 03:01 ✅ / finance 11-23 04:35 🟡 / health 11-23 04:42 🟡 / **work 11-23 04:42 🔴（受害方）**

> **方法论延续**：finance/health 的 mtime 停在 11-23，但 11-24 窗已证明「mtime 停 ≠ 库冻结」，故只记为观察项；work 库是唯一有**独立错误证据**（heartbeat-work 120x + 孤儿投递 697 次重试都指向它）的库。

---

## 1. 趋势扫描产出

- 产物：`heartbeat/nightly-scout-2026-11-28.md`（本文件）、`graphify-out/raw/scout-2026-11-28-corpus.md`（377,246 B）、`graphify-out/2026-11-28/{snapshot,manifest}.json`
- 图谱主图：**4,619 节点 / 11,181 边 / 40 社区**（+175 节点 / +472 边；合并前已备份 `graph.json.bak.20261128-0050`；merge 后已重跑聚类）
- LanceDB `nightly-scout`：**662 → 692 行**（+30：news 16 / arxiv 13 / trend 1）

### 数据源与采集量
| 源 | 量 | 备注 |
|---|---|---|
| arXiv | **105 真新增**（三路并集） | API `max_results=300` × 3 组 + 公告列表 id_list 反查 + 713 id 分批补捞；对全部 2510 历史 id 全量比对 |
| arXiv published 直方图 | 11-25=43、11-24=32、11-16=3、11-15=3、11-06=3、11-05=3、11-04=4，其余零散旧批次首次露出 | **旧论文露出是截断造成的，不是新发布** |
| GitHub releases | 11 repo，**4 新 tag** | MCP servers v2.6.0、MCP registry v1.8.17/v1.8.18、MCP inspector 2.17.0/1.0.7（均 11-27） |
| GitHub commits | **91** | claude-code 20、servers 20、vercel/ai 20、openai-python 12、spec 9、anthropic-sdk 10 |
| GHSA | servers 29→**30**、registry 5，**8 条新** | **连续第 5 窗零新增的纪录被打破** |
| HackerNews | top30，**30/30 全换血** | 头条 "AI made self-hosting fun again"（944）、"AI talks behind your back"（532）、AMD llama.cpp fork（415） |
| RSS OpenAI | 1430 items，**+0** | **连续第 2 窗冻结**，末条仍 11-24 13:00 |
| RSS The Decoder | 10 items，**6 全新** | Cloud One 入侵 / Athena / SAP 裁员 / GTA 6 / Aaronson / GPT-6.2 限额 |
| RSS Google AI blog | 20 items，+0 | 末条 11-24 16:00 |
| 正文页 | **19 篇**（6 Decoder + 12 HN 一手源 + 1 Google DevBlog） | md5 全互异；3 篇被上游阻断（Sky 403 / EFF 404 / IACR Cloudflare）已标注 |

---

## 2. 本窗趋势分析

### ① 🔴 方法论事件：**"零新增"是假的** —— 上限截断伪造了空窗
- 详见第 0 节。要点重述：API `max_results` 截断 + 无报错 = "0 新增"看起来和真的没有新东西完全一样。上窗据此写了"arXiv 176 真新增"，本窗据此差点再写一次"0 新增"。
- **横跨本系列的一个坏模式**：11-23 窗的"arXiv 零新增（周末正常）"是 mtime 误读，本窗的"arXiv 零新增（周末正常）"是 API 截断。**两次都是把"我的采集没拿到"当成了"世界上没有"。**
- **可执行**：任何"计数为零"的结论，必须标注**该计数是从哪条路径来的、有没有第二条路径交叉校验**。本窗起，arXiv 采集固定三路并集。

### ② 🔴 本窗主线：**产物在快速变好，而所有校验器的失败率要么已知、要么可测，但依赖它的人看不见**
这一窗几乎所有关键产物都是**校验器**，而每一个都有明确的失败率：

| 校验器 | 失败率 | 依赖方能否看见 |
|---|---|---|
| MCP inspector `--verify` | 空 skills catalog 也报 Verified（本窗已改为失败） | 否 |
| MCP inspector SSRF 守卫 | 按**书写形式**匹配 IPv6 而非解析后的值 → NAT64 绕过（`http://[64:ff9b::a9fe:a9fe]` 可达 169.254.169.254） | 否 |
| `mcp-server-git` | 8 条新 GHSA，含 high 级：Git LFS 跑仓库自带 `.git/config` 里指定的程序、`--repository` 根可经 `.git` 指针改指、`git_remote` 用 TAB 绕过脱敏、`repo_path` 展开 `$NAME` 并在报错里回显 | 否 |
| AI code reviewer | Opus/Sonnet/Haiku 5.5 在 low/medium/high 三档 effort 下**每档都接受 ≥45% 的错补丁**（false success 0.45 / 0.49 / 0.51） | 否 |
| 证明检查器 | Bernstein 维护的 soundness bug 清单，HOL Light 内核仅 400 行但"行数少 ≠ 审得细" | 否 |
| Agent 自身的安全记忆 | 修复漏洞成功率 85.7%，但**新会话重新引入同一漏洞类的概率 26.7%**（从未见过的 agent 是 27.5%）→ 知识存在，不被激活 | 否 |
| Agent 恢复路径 | 失败后自主重规划会**静默丢弃原工作流的安全义务**（864 次运行中 ARGUS 在强制执行下阻止了全部观测到的保护丢失事件） | 否 |

→ **判断**：这与上窗的"证明经济学"是同一根问题的第 4 段，但本窗把它从**单个案例**升级为**系统性模式**：上一窗的教训是"编译通过 ≠ 可用产物"；本窗的教训是**"校验器本身也是产物，而校验器的失败率从未被披露"**。
→ **可执行**：任何把 verifier/checker/reviewer 当作质量保证的流程，都应把**"这个校验器自身的假阳性/假阴性率是多少"**列为必答项，而不是默认它是完美的。没有这个数字，就等于默认接受 45% 的错补丁。

### ③ 🔴 攻击链闭环：**ARTEX 分析发布两周后，美国空军 Cloud One 被从控制平面打穿**
- 上窗 Microsoft 拆解 **ARTEX**：框架**自行分发攻击任务、失败自动换模型、机器速度**运行，驱动 Metasploit 等既有工具；国家背景组织已将其编入 Salt Typhoon / Crystal Typhoon / Onyx Sleet / Storm-0940 行动；防守建议是**欺骗**（诱饵 + 假成功信号诱导攻击 agent 放弃）。
- 本窗 **Reuters**：攻击者打穿 **Cloud One**（空军中央云基础设施），可能暴露战术、人员与后勤数据。发现于上月例行系统升级；据一名信源，攻击者**利用软件漏洞取得控制平面访问权**。Cloud One 自 2017 年起汇聚 Microsoft / Amazon / Oracle / Alphabet 的云资源，运行**防空雷达与弹药管理**应用。空军随即**暂停新增应用迁移、阻断更新、撤销管理员权限**，US Cyber Command 评估损失。攻击者身份与是否外传数据仍不明。报道同时提到**近 6 起针对美国政府机构的其他安全事件**。
- **闭环读法**：上窗给的是"攻击自动化的能力"，本窗给的是"该能力的第一次可见落地"—— 而且落点正是**控制平面**，正是 ARTEX 描述的"快速在大规模云网络中识别漏洞"的目标类型。
- **缺口**：Cloud One 的响应是**传统遏制**（停迁移、阻更新、撤权限），**没有出现上窗建议的欺骗式防御**。响应时间与响应形态本身是结论的一部分。

### ④ 🔴 协议层从静默转向**主动打补丁**：GHSA 连续 5 窗零新增的纪录被打破
- `modelcontextprotocol/servers` **v2.6.0**（11-27）：发行说明写明"修复三个 server 的 8 个漏洞，并补齐 v2.5.0 遗留的 2 个"。升级指引：`mcp-server-git` → 2026.11.27、`@modelcontextprotocol/server-memory` → 2.2.2、`mcp-server-fetch` → 2026.11.27，Windows 上 `@modelcontextprotocol/server-filesystem` → 2.4.1。
- **GHSA feed 侧印证**：servers 29 → 30，8 条新 advisory 全部 11-27 发布。
- 逐条看，这 8 条有一个**统一形状**：MCP server 的信任边界是**本地仓库与本地配置**，而每一条都是 server 依据**用户没写过、也看不见**的内容去执行 / 读取 / 泄露东西。
  - **GHSA-6663-fm5v-gqm5（high）**：装了 Git LFS 时，server 保留了用户配置里的 LFS filter，于是仓库 `.git/config` 里 `lfs.extension.<name>.clean` / `.smudge`、`lfs.customtransfer.<name>.path` / `.args` 这些**指定程序的键**会被 `git_status`、`git_diff_unstaged`、`git_diff`、`git_add`、`git_checkout`、`git_merge` 以 server 权限执行。修法：在仓库作用域清空这些键 + `GIT_LFS_SKIP_SMUDGE=1` 关闭 LFS 下载。
  - **GHSA-3whj-m8jj-x97q**：`.git` 文件或 `commondir` 指向别处的 root 会被接受，于是 `git_show` 读出**另一个仓库**的内容。修法：启动时记录 root 的 Git 目录并要求属于自身（linked worktree / submodule 除外）。
  - **GHSA-wvv2-676g-r57j**：`git_remote` 的脱敏绕过 —— remote 名里一个 **TAB** 把 URL 列错位，或 URL 不以自身值开头就跳过脱敏，于是用户配置里带凭证的 `url.<base>.insteadOf` 被返回。
  - **GHSA-f33v-89w7-f9vc**：`repo_path` 里的 `$NAME` / `${NAME}` 被 GitPython 展开，且路径不存在时**报错里回显展开后的值** → 一次 tool call 就能读出 server 进程的任意环境变量。
  - **GHSA-48j5-hj63-c82c**：memory server `saveGraph` 临时路径竞态 + symlink chmod → 暴露受保护文件。
  - **GHSA-g7v6-hfx3-8rv6**：GHSA-3rxj-6jhw-qfv7 的**不完整修复** —— `mcp-server-fetch` 的 robots.txt 路径规范化仍漏掉反斜杠与 path-parameter 写法。
- **MCP inspector 2.17.0 / 1.0.7**：SSRF 守卫改为**解析地址后按值匹配**，并专门复查 `::ffff:0:0/96`、`64:ff9b::/96`、`64:ff9b:1::/48` 携带的 IPv4（NAT64 绕过）。非安全项里还有一条值得单独记：**`--verify` 遇到空 skills catalog 现在会失败，而不是报 Verified**。
- **MCP registry v1.8.17 / v1.8.18**（同日两次）：18 强制执行 publisher 元数据大小上限，17 准备 staging workload identities。
- **判读**：上一窗「GHSA 连续 5 窗零新增」被当成"协议层静默、注意力转向算力与主权"。本窗证明**那只是 advisory feed 没被填充**，不是没有漏洞 —— 本窗一口气 8 条。真正的变化不是漏洞增多，而是**漏洞开始被批量发现并打包发布**（一次性 release 说明里逐条列 CVE、包名、受影响版本、修复版本）。

### ⑤ 🟢 能力的进展是真的，且这一窗它全部落在**系统侧**而非模型侧
- **TransHarness**（arXiv 2611.33757）：从同任务成败对比中演化 harness 干预策略，把执行上下文触发条件与诊断建议配对，经跨任务回放与独立语义选择**只保留能在当前任务证据上落地的策略**。用**仅 300 条来自测试分布之外的源轨迹**，在 DeepSWE v1.1 达 **76.4%**、Terminal-Bench 2.1 达 **95.5%**，超过最强基线 GPT-6 Astra **2.4 与 5.6 个百分点**。→ 这是本系列第一次拿到"harness 演化**可迁移**而非过拟合基准"的证据。
- **Partial Routing**（2611.33402）：让前沿 lead 模型把合适的子任务委派给更便宜的 worker，依据两者历史运行识别 recurring subtask 并测质量与成本，lead 在执行期自行决定委派与否，**不训练任何模型**。δ=0.75 时 ViBench **70.2 → 78.5**（成本低 19%），Terminal-Bench 通过率 **54% → 61%**。**连"只给 lead 子任务分解、不给 worker"都能降本并提通过率。**
- **Confidence scores for gated automation**（2611.33394）：在冻结 2B backbone 的**末层 hidden state** 上拟合线性置信度头（闭源模型则训 text-only 元模型），在高准确率目标下自动化了最大比例的工作量；关键结论是**prompted 置信度可以看起来校准得很好，但没有阈值化所需的分辨率**。
- **Divide, Diagnose, and Compose / DeCAF**（2611.08723）：把 agentic pipeline 的设计空间拆成提示、拓扑、模型选择、工具策略各维度，**独立 coding-agent session 在受限编辑范围内各优化一维**，并生成每个决策的推理轨迹；最终用组件级轨迹评估器定位欠佳组件。
- **Certify What You Plant**（2611.33303）：程序生成的逻辑题通常只"种"了一条证明，但题目可能另有更短或无关的证明，导致标称深度高估实际难度。论文计算**每条证明都必经的步骤、最短证明、极小证明数量、不可或缺的前提**，并导出**独立检查器可验证的证书**；审计 8 个数据集发现 ProofWriter / Blocksworld 深度是强制的，而 **FLDx2 里标称 depth 5 的题其实只需约两条规则应用**，ZebraLogic 的答案则**不需要任何特定步骤**。
- **FlashProve-Next**（2611.33741）：为闭源 LLM API 的单次响应生成**可验证的零知识掩码证明**，在不改原生服务栈（bf16/fp8/mxfp4、random sampling、FlashAttention、CUDA graphs、batching、prefix caching）的前提下，**不泄露权重、隐藏提示、隐藏推理与激活**；28 个 Lean 4 模块（696 声明，**零 sorry**，只用标准公理）机械化了逐轮可靠性、bucket sampling、掩码绑定、因果掩码、六个 IR gadget 与可执行 verifier。
- → **判读**：与上窗 ShellBench（模型差异 1.1pp 在噪声带内、harness 差异几乎不影响性能）合读，本窗给出**方向性反转**：harness 侧出现 76.4 / 95.5 的绝对分数，委派侧给出 +8.3 分与 −19% 成本，置信度头给出可阈值化的门控。**能力竞争的单位从"哪个模型"移到了"什么被委派、谁复核、用什么分数决定放行"。**

### ⑥ 🟢 企业侧：SAP 砍 10,000 岗（9% 员工）押注 AI，而同窗数据显示复核环节正是瓶颈
- **SAP**（Bloomberg / The Decoder）：准备裁减**至少 10,000 个岗位**，约占 110,000+ 全球员工的 **9%**；所有部门被要求找节省空间，产品开发、工程与销售受冲击最大；最终数字未定，需与员工代表谈判。德国约占其员工 1/4，**就业保障到 2028**。CEO Christian Klein 要把 AI 工具嵌入全线产品。公司 2024 年已裁约 10,000 人。同期 **Oracle 12 个月裁 21,000 人**、**Microsoft 向约 60,000 名员工提供买断**。
- **OpenAI Athena**（The Information / The Decoder）：建一个代号 Athena 的数据管理平台，形似**语义层**（为收入、客户数等业务指标提供一致定义）；已有客户认为去年秋天推出的 ChatGPT Work 数据分析 agent **准确度不够**。思路是让 agent 拿到足够上下文以**少猜**。有知情人士称 OpenAI 正用 Athena 构建"收集、记录、更新业务规则"的 agent，好让其他 agent 不必每次从零开始。Snowflake 与 Databricks 已有各自的语义层。**报道点出的战略逻辑是：换语义层供应商比换 AI 模型更难。**
- **同窗的复核瓶颈数据**（两窗前 Anthropic 近 300 个企业部署：55% 有产出提升，但 **19% 完全没产生业务价值**；最大障碍是"AI 产出太多以至于人工复核不过来"，49 次提及）。
- **放在一起读**：SAP 在裁掉复核产能的同时押注 agent 产出，而同窗 arXiv 数据显示 **AI code reviewer 在最优档位仍接受 ≥45% 的错补丁**。**被裁掉的那部分复核容量，正是自动复核漏掉的那部分所对应的容量。** 语义层（Athena）则是同一逻辑的另一面：**正确的上下文是让 agent 少猜的杠杆**，而它同时是一个切换成本护城河。
- **可执行**：agent 落地评估里，**"多少人工复核分钟换一次被采纳的产出"** 必须与"每次委派的成本"并列为两个一等指标（延续上窗的结论）。

### ⑦ 🟢 Google 把 MCP 从"可选"变成"强制"，而强制路径上的能力是**故意被阉割的**
- 11-24 Google 让 8 个 Workspace MCP server 正式可用，并在 API 条款里加了一条新约束：**从 2027-02-01，任何"由 AI Agent 驱动"的工具必须通过这些 server 访问 Gmail / Drive / Calendar 等 Workspace**。
- **新增的 Workspace AI Tools Addendum 一句话**："GWS Access Tool 必须使用 Google MCP，且该工具由 AI Agent、AI Harness 或使用 AI 模型的模型/服务驱动。"下一句**禁止伪装 agent 以规避该分类**，违者可被限制/移除访问或停号。
- 技术侧：同日起，直接调 REST API 的 agent **无论付费档位都按 Standard 档配额**——REST 还能用，但慢，且在违约状态。不涉及 AI 的应用（夜间备份、CRM 同步、独立 OAuth 的确定性脚本）不受影响。另有对建 memory 的 agent 重要的数据规则：Workspace 数据只能"为完成活跃的、用户授权的任务"而处理。
- **关键讽刺**：Gmail server 的工具清单里**能搜邮件、读会话、创建草稿、加标签，但发不出邮件、不能回复/转发、不能改已建草稿** —— 这些工具存在，但 Google 配额页写明"需 partner 权限，未普遍开放"。
- → **判读**：两个结构点。**其一，合规面被定义在"调用方是谁"而不是"用不用 MCP"**，且明令禁止伪装 → 合规是**行为性**的，只能靠厂商依据客户端**对自己的描述**来判定，这意味着 agent 必须如实申报自己是什么，而申报本身就是新的攻击面。**其二，被强制的那条路径比 REST 更弱**（不能发邮件），所以迁移不只是合规成本还是能力回退 —— 这与本窗 MCP server 的 8 条 advisory 是同一形状：**能力在，管控是缺陷所在。**

### ⑧ 🟢 推理栈碎片化，且优化方向开始**改变模型的思考方式**而非硬件使用方式
- 11-26 一篇盘点 bespoke 推理引擎的帖子：**llama.cpp / SGLang / vLLM 是"通用引擎"**（不为特定硬件优化、追求广兼容），而新一代 fork **只针对特定模型与硬件子集、用前沿模型 vibe-code 整个工程、追逐越来越高的 token 生成速率**。Strata 能把重度量化的 **Qwen 3.8 Flash Next（180B）** 跑在 **16GB VRAM + 16GB 内存**上。实测的 **AMD 专属 llama.cpp fork** 把 token 生成从 **35 → 55 tok/s**、prefill 从 **700 → 1300 tok/s**。
- **作者点出的不舒服的细节**：Strata 会**优先轮询驻留 VRAM 的 expert，即使按正常策略本应放到系统内存/磁盘的 expert 也会被拉上来** —— 这改变的是**模型怎么算**，不是硬件怎么用。
- **同构现象**：loop transformer（层跑 2~3 遍、共享 KV cache）、OpenAI 自己"超长上下文是死路"的论断、Deepmind 刻意**不奖励 CoT** 以保持意图可读 —— 都是"算什么"而非"算多快"的问题。
- → **判读**：一旦优化目标从质量切到 tok/s，**最省力的杠杆就是改变模型计算什么**。这是**质量风险，而 tok/s 数字不显示它** —— 且按本窗的复核数据，**所有复核档位都接不住这类退化**。

### ⑨ 🟡 本窗的 arXiv 主题分布：评测/编码代理占主导，"记忆"退到 23 篇
- 105 篇新论文的主题计数（关键词口径）：**eval-bench 74 / coding-agent 41 / planning-reasoning 30 / memory 23 / formal 20 / rl-training 16 / agent-safety 13 / security 13 / multi-agent 11 / interpretability 9 / tool-use 8 / MCP 1**。
- 值得注意的是**"记忆"相关论文里出现了两条反向结果**：
  - **Semantic Density Does Not Predict Agent-Memory Collapse**（2611.33184）：在 13 种记忆方法、5 个环境、**805 个快照**上注册了余弦相似度 + 13 项几何/检索/图统计量，**没有任何统计量能可靠预测留出精度的下降**，余弦相似度的中位提前量为 **0**；训练出来的分类器**把 56.9% 的稳定检查点误报为衰退**，且在成功率归零后只检出 **18%**。→ **"记忆会退化"这个担忧没有可靠的预警指标**，监控本身是噪声源。
  - **Peer Memory**（2611.09990）：warm 记忆**降低了 pooled hindsight regret、增加了对其他证据持有者的咨询**，但**最终 token F1 差异不确定**（changed-minus-stable 交互 −1.38 分，95% CI [−3.50, +0.73]）。→ **行为变了，准确率没测到变化。**
- → 这两条与前几窗的"记忆要会忘"、"记忆是预测问题"、"使用期冲突的具体故障率"构成**连续四窗的推进**：保真度 → 效用 → 冲突分类 → **连"会不会退化"都无法预测，且监控会误报**。

### ⑩ 🟡 协议生态侧的其余信号：登记处在"打包发布"，spec 在写发布周期
- **MCP registry v1.8.17 / v1.8.18 同日两次**（11-27）：18 强制执行 publisher 元数据大小上限，17 准备 staging 的 workload identities、预览生产配置、把 v1.8.16 提升到生产。→ 登记处正在**连续多次小版本推进自身运维**，与上窗"registry 24h 三连发是本系列最快节奏"相比节奏持平。
- **MCP spec**：新增 **release cycle 页面**（#3550），并修了 2026-07-28 与 draft 规格文档的小错误；这是本窗 spec 仓库唯一有实质内容的提交，其余是依赖 bump。
- **openai-python v3.60.0**（11-26）：新增 spend alerts 与 response compaction 字段、支持更新 session vaults、澄清 message retries 与 Batch 端点、文档化 inline skill 上传限制。
- **anthropic-sdk-python 2.14.0**：新增 compliance review cases / notices / items 的 API 支持、Google 托管数据控制、修复 `trust_env` 与代理处理。
- **vercel/ai** 20 commits 里有实质的一条：**支持 WebMCP source-based tool ownership**、对齐 MCP Events 与 SEP-3415、限制单条 server-sent event 大小、修复 harness 的 `stopPreviousBridge` 进程列举与树遍历、在受限权限模式下**约束仓库 `AGENTS.md` 符号链接**。

### ⑪ 🟡 HN 侧：本窗的"头条"不是模型，是工具与自托管
- top30 **30/30 全换血**。分数最高的几条：
  - **"AI made self-hosting fun again"（944 分 / 452 评论）** —— 基础设施配置都在 Git 仓库里（Docker Compose、脚本、配置文件），于是 AI coding agent 可以像对待普通软件项目一样动手；过去因为要读 changelog、排障而搁置的改动，现在"临时起意的想法也能成真"。
  - **"The group chat where your AI talks behind your back"（532 分）** —— 一行 prompt 就能让模型.commit 到"用户群聊里 AI 们背后议论你"这个框架，用它学到的关于用户的全部信息；文中有真人授权输出（ChatGPT / Claude / Gemini / Codex / DeepSeek 各设人设）。→ 技术含量低但信号不小：**这是一次无需攻击者技能的隐私提取演示** —— payload 是用户自己的提问，模型天然配合。**模型本身就是保险库边界**，而泄漏的是"用户的私有模型"—— 没有保险库在保护它，因为从没被当成保险库。
  - **"Claude sabotaging ML research tasks?"（231 分）**、**AMD 专属 llama.cpp fork（415 分）**、**Google Workspace MCP 强制（388 分）**、**Kimi for Science（125 分）**。
- **Kimi for Science**（Moonshot）：开放第一批 cohort 申请（12-08 截止）。→ **当模型能力成为给定的，剩下的差异化就是"科学工作实际发生的管道"**；一个带人类研究者、迭代数月的 cohort 就是那个管道的制度化形式 —— 与本窗量子引力那篇（**斯坦福物理学家用 GPT-6 Astra 迭代数月、约 4 亿 token** 完成引力子对计算）同构。
- **"False Computer-Checked Proofs"（D.J. Bernstein，17 分但内容密度最高）**：本窗最值得记的一条，见 ②。

---

## 3. 趋势变化（相对 11-27 窗）

- 🔴 **采集方法自身的缺陷被发现：arXiv API `max_results` 静默截断，"零新增"是假信号** → 恢复 105 篇真新增；**所有历史窗口的 arXiv 新增数都可能系统性偏低**
- 🔴 **主线确立：产物在变好，校验器没跟上，且每个校验器的失败率都已知/可测而依赖方看不见**（inspector NAT64 + 空 catalog 报 Verified / git server 8 条 GHSA / reviewer ≥45% 错补丁接受率 / proof checker soundness bug / agent 安全记忆 26.7% 不跨会话 / 恢复路径丢安全义务）
- 🔴 **攻击链闭环**：ARTEX 分析发布两周后，美国空军 Cloud One 控制平面被打穿（防空雷达与弹药管理应用所在平台），而响应是传统遏制而非上窗建议的欺骗式防御
- 🔴 **协议层从静默转向主动打补丁**：GHSA 连续 5 窗零新增被打破（servers 29→30，8 条新，含 1 条 high）；v2.6.0 一次性修复三包 8 漏洞
- 🔴 **企业侧把复核当成成本项砍掉**：SAP 至少裁 10,000 岗（9%），同窗数据显示最优 AI reviewer 仍接受 ≥45% 错补丁
- 🔴 **heartbeat-work 96x → 120x**（四窗翻五倍），孤儿投递 retry 554 → **697** 仍 pending
- 🔴 **OpenRouter 连续第 13 窗为 0**
- 🟢 **能力进展整体落在系统侧**：harness 演化可迁移（DeepSWE 76.4 / Terminal-Bench 95.5，300 条分布外轨迹）、partial routing（ViBench 70.2→78.5，−19% 成本）、置信度头（2B 末层 hidden state，可阈值化）、DeCAF 分解式 pipeline 优化、证明深度证书、FlashProve-Next（闭源 API 响应的零知识证明，28 个 Lean 模块零 sorry）
- 🟢 **Google 把 MCP 变成强制路径**，但强制路径上的 Gmail 发信能力被故意不开通用 —— 合规面在"调用方身份"而非"能力"，且明令禁止伪装
- 🟢 **推理栈碎片化，优化的杠杆从"硬件怎么用"滑向"模型怎么算"**
- 🟢 **记忆退化无法预警**：805 快照上无任何统计量可靠预测，监控误报 56.9%，真衰退检出仅 18%
- 🟡 **两个 RSS 源同时冻结在 11-24**（OpenAI 连续第 2 窗，Google AI blog 同日）→ 更像共同的上游发布空档，而非两个独立故障
- 🟡 Gateway RSS 4.83 → **5.62 GB**（+3,493 KB/h，预测 837h 触 8GB，10 月式泄漏仍未复现，但已越过 5GB）

---

## 4. 工具/流程修复

- [x] **夜班脚本按日期模板化**：`fetch_1128.sh` / `fetch_gh_1128.sh` / `fetch_pages_1128.sh` / `prep_arxiv_1128.py` / `build_corpus_1128.py` / `build_graph_1128.py` / `merge_graph_1128.py` / `build_rows_1128.py` / `update_lancedb_1128.py` / `regen_report_1128.py`
- [x] **修复 arXiv 采集的截断缺陷（本窗最重要的工具修复）**：新增三路并集采集 —— ① API `max_results=300` × 3 组；② 公告列表页 `arxiv.org/list/<cat>/recent?show=250` 抓 id 后 `id_list` 反查；③ 剩余未分类 id 分批（≤50/批）补捞。写入 `scout-raw/arxiv-1128-newids-final.json`
- [x] **修 `id_list` URL 超长 400**：`https://...id_list=<713 ids>` 触发 `Request Line is too large (7890 > 4094)` → 改为每批 ≤50 并对每批做 3 次重试
- [x] **修 `build_graph` 的 arXiv 节点重复计数**：5 个解析文件并存时同一 id 被重复 `add_link` → 加 `_arxiv_seen` 去重，节点数从 178 修正为 **105**
- [x] **`build_corpus` 的 arXiv 数据源切换**到全量解析文件 + 最终 newids 并集
- [x] **正文页 md5 去重断言**：19 篇抓取页面 md5 全部互异
- [x] **3 处上游阻断已标注而非静默丢弃**：Sky News 403 Access Denied、EFF 404（URL 变更）、IACR ePrint Cloudflare challenge —— 均在 corpus 中标注为"仅标题/仅元数据"
- [x] **`fetch_pages_1128.sh` 补漏**：`generativehistory.substack.com` SSL 失败导致脚本提前退出，后续 8 个 URL 未抓 → 单独补跑脚本全部补齐（`/tmp/fp2.sh`）

---

## 5. P0 待处理

1. 🔴 **孤儿投递 + work 库 + 重启回收 36 条租约**（`openclaw doctor --state-sqlite compact` → `doctor --session-sqlite recover --session-sqlite-agent work` → 停 Gateway → `doctor --fix` → 重启；CLI 需 ≥300s）
2. 🔴 **OpenRouter 余额 0**（第 13 窗，ZP 决策充值）
3. 🔴 **所有历史窗口的 arXiv 新增数需重算**（截断已修，但历史 baseline 偏低，会让新窗口的"新增"被低估）
4. 🟡 **摘要链仍缺告警**（抓取全失败 → 显式告警 + 保留上一份报告）；本窗 11-27 场正常，问题仍未修
5. 🟡 **任何以 verifier/reviewer 为质量保证的流程，需补"校验器自身失败率"这一必答项**（本窗给出的基线：AI code reviewer ≥45% 错补丁接受率）
6. 🟡 **NAS 归档累积**（WSL/ 8 份，/mnt/h 可用 251G，97% 满）→ 清理前先清回收站
7. 🟡 **合并重复 NightOps 作业**（0597835a vs c46eeb63）
8. 🟡 **Gateway RSS 5.62 GB**（预测 837h 触 8GB）
9. 🟡 **RSS 双源同时冻结在 11-24** → 需换抓取入口或确认上游发布空档
10. 🟢 **新增四条采样口**：校验器自身的假阳性/假阴性率 / 上限数据源的"零"是否有第二路径佐证 / 委派子任务的复核分钟数 / 语义层资产（业务定义）的版本化与迁移成本

---

*产物核对：corpus 377,246 B；图谱 4,619 节点 / 11,181 边 / 40 社区；LanceDB 662 → 692 行；本窗新增 30 行（news 16 / arxiv 13 / trend 1）。*
