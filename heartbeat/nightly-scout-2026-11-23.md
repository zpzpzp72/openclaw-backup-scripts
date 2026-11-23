# Scout NightOps — 2026-11-23 01:45 (Asia/Shanghai)

> 正常单夜窗口（宿主机 11-22 21:38 重启后第 4 小时）。上游三个"高产量源"全部零新增，**本窗分析内容全部来自新闻/产品层**。

## 0. 心跳检查清单

| 项目 | 状态 | 证据 |
|---|---|---|
| DIRECTIVE.md | 无新指令（仅"暂无指令"） | 空扫描 |
| 每日新闻摘要 | 🟡 job `fe5fa0ce` 状态 ok，但**今日 08:00 场尚未到点**；最近产物仍是 11-22 21:46 的 `news_digest_20261122_214605.html`（20,559 B） | `workspace/reports/`；crontab `0 8 * * *` 侧日志停在 11-17 |
| MiniMax API | ✅ 直连 200 / 0.27 s | curl 实测 `api.minimaxi.com` |
| OpenRouter API | 🔴 `total_credits: 0` — **连续第 9 窗为 0** | finance agent auth-profiles 备份里的 key 查 `/api/v1/credits` |
| 代理 25017 | ✅ TCP 可达 | `172.18.160.1:25017` TCP_OK |
| 端口 8080 FastAPI | ✅ 在监听 | TCP 探测通过 |
| NAS 备份 | 🟢 `openclaw-20261122-2203.tgz`（6,111,928,153 B）已落盘；/mnt/h 可用 373G | `WSL/` 目录 |
| 本机 native backup | 🟢 21:38 起跑，22:03 verify OK，剩余 779G | `native-backup.log` |
| gateway RSS | 🟢 3.46 GB（PID 695，uptime 3h51m） | ps |
| gateway CPU | 🟡 222%（多核折算 ≈2.2 核） | 较昨夜 165% 继续上行，但 uptime 未满 24h |
| cron 总览 | 🟡 30 jobs | 见下 |
| memory | ✅ 已新建 `agents/scout/memory/2026-11-23.md` | — |

### cron 失败情况
- `heartbeat:orchestrator` **error (6x)** — `agent orchestrator unavailable (SQLite session reclamation commit ...)`
- `heartbeat:finance` **error (7x)** — 同上
- `Orchestrator NightOps` **error** — 同上
- `heartbeat:scout/coder/life/work/health/main` 全部 skipped（正常，"not requested"）
- `Scout NightOps`（本场）running；`Life/Coder NightOps` ok

### agent 库 mtime（写入冻结复核 —— 11-22 结论再次确认）
| agent | mtime | 判定 |
|---|---|---|
| main | 11-23 00:42 | ✅ 正常 |
| scout | 11-23 01:32 | ✅ 正常 |
| coder | 11-22 22:23 | ✅ 正常 |
| life | 11-22 23:11 | ✅ 正常 |
| work | 11-22 21:40 | ✅ 正常 |
| **health** | **11-16 04:13** | 🔴 仍冻结（第 7 天） |
| **finance** | **11-16 04:12** | 🔴 仍冻结（第 7 天） |
| **orchestrator** | **11-17 04:12** | 🔴 仍冻结（第 6 天） |

> **连续两窗确认**：宿主机整体重启后这三个库 mtime 纹丝不动，而其余五个库正常。→ 「重启可解冻」假设**已证伪**，且 heartbeat:health 现在是 skipped 而非 error（它本来就没被调度成功过，不是写坏了）。这三个库需要**单独诊断**：检查它们的 lease 表是否残留未过期租约、以及 heartbeat job 的 `agent unavailable` 判定逻辑。

---

## 1. 趋势扫描产出

- 产物：`heartbeat/nightly-scout-2026-11-23.md`（本文件）、`graphify-out/raw/scout-2026-11-23-corpus.md`（126,237 B）、`graphify-out/2026-11-23/{snapshot,manifest}.json`
- 图谱主图：**3,613 节点 / 8,756 边 / 39 社区**（+16 节点 / +137 边；合并前已备份 `graph.json.bak.20261123-0200`）
- LanceDB `nightly-scout`：**588 → 599 行**（+11：news 8 / engineering 2 / trend 1）

### 数据源与采集量
| 源 | 量 | 备注 |
|---|---|---|
| arXiv cs.AI / cs.MA / MCP-tool-agent | 400 解析 → **0 新** | 对全部 **1895** 个历史 id 全量比对确认；最新 published 仍为 2026-11-19T18:59:34Z → **周末无新批次，非采集故障** |
| GitHub releases × 11 repo | **1 个新 tag**（MCP registry v1.8.13 @ 11-22 16:29Z） | 走认证 `gh api` |
| GitHub commits × 6 repo | 6 条（claude-code 4× "chore: Update mods/" + MCP spec 2 docs） | — |
| GHSA advisory | servers 29（**+0**）/ registry 5（**+0**） | 回到 11-22 之前的零增长模式 |
| HackerNews top30 | 30 条（**12/30 换血**） | AI 相关：Open Social Web Alliance 108pts、"LLM 的 subagent" 游戏 135pts、Anthropic 87% 燃气 522pts |
| OpenAI RSS | 1421 条（**+0，连续第 3 窗冻结**） | 末条仍是 11-20 10:00 "Combatting adversarial distillation" |
| The Decoder RSS | 10 条（**+2**） | — |
| Google AI blog RSS | 20 条（**+0**） | 末条仍是 11-19 Tool Retrieval（11-17 的 `curl -L` 补丁持续有效） |
| 正文页 | 11 篇（4 篇新 Decoder + OpenAI Perplexity 全文 + OSW + GitHub 项目页 + 4 篇从站点 top-stories 栏重新定位的旧文） | — |

### 本窗关键内容（10 条）
1. **工作场所基准：编码 agent 完成率 < 1/10**（high）— 模拟公司里有同事、项目板、不完整交接；Opus 5.5 与 Astra 完整完成任务不足十分之一。能快速完成独立明确任务，但作为自主开发者会丢失跟踪。
2. **OpenAI 首席科学家 Pachocki 公开内部 perplexity**（high）— log-perplexity 轨迹：GPT-3.5 ≈0.99 / GPT-4 ≈0.91 / <0.8 时网络与数学能力涌现 / ≈0.76 时开始产出突破性数学结果。主张以困惑度作为跨实验室共享节拍指标并设**硬性上限**（下一 transformative 窗口 0.68–0.70），预判 2027 年起可能出现预训练研究的雪崩式进展。
3. **Perplexity Monitor API**（high）— 定时搜索 + webhook 推送 + 决策模型做相关性/可信度/时效性过滤；$1/1000 次；页面监控可返回文本 diff。把"轮询去重"这件事产品化到了 provider 层。
4. **Anthropic：单 agent 优于多 subagent**（high）— 按需加载上下文的单 agent 在质量/成本/延迟上更好，某对比中快约 2 倍；发布迁移工具包。→ 直接限定本系列追踪的 subagent 编排模式为"过渡架构"。
5. **Anthropic：记忆的关键是知道忘什么**（high）— Sonnet 3.7 在 Pokémon Red 一局造 413 文件/225 目录只拿 1 徽章；Fable 5 只留少量策略文件拿 4 徽章；"Dreaming" 事后回溯纠正错误笔记。
6. **Ramp AI Index：token 价格 6 周降 21.2%，用量创纪录 +1.5%**（medium）— Anthropic 占 token 支出近 59%；Ramp/Stripe/OpenRouter 三方同向。
7. **Claude Fable 5.2 用"代码作画"而非像素生成**（medium）— 写 Python 在画布上放约 70 万笔触，模拟笔毛纹理与覆盖错误。
8. **Open Social Web Alliance**（medium）— 以"邮件"为模型的开放社交协议（ActivityPub 系），HN 108pts/95c；与 MCP 同构的"闭源平台 vs 开放协议"格局。
9. **arXiv 零新增**（engineering/medium）— 400 条与上窗完全一致，1895 历史 id 全量比对确认；分布直方图不变（11-19:179 / 11-16:54 / 11-17:53 / 11-18:45）。
10. **GitHub 仅 1 新 tag + 0 新通告**（engineering/medium）— registry v1.8.13；servers 保持 v2.5.0。**11-22 的 8 条 GHSA 爆发应读作发布节奏而非孤立尖峰**。

### 趋势判断（trend 行）
**本窗从"能力"转向"度量"：三条独立数字都在说"基准题 ≠ 工作题"。**
-  workplace 基准 <1/10 完成率（度量设计问题）
-  单 agent > 多 subagent（架构简化问题）
-  记忆要会忘（状态跟踪问题）
- 而 OpenAI 侧同步给出**可比的节拍指标**（perplexity + 跨实验室上限），并承认对齐审计会继续退化
- 成本侧继续下行（token −21.2%/6 周，量创新高）
→ **对 agent 工程而言，当前约束已不是价格或能力，而是状态跟踪与评测设计**。建议把采样口径从"孤立基准分数"切到"多步 messy 任务的端到端完成率"，并加采样"跨实验室可比的原始指标"。

---

## 2. 工具/流程修复

- [x] **中断恢复**：首次后台 fetch 被上一轮 turn 中断打断（`fetch_1123.sh` 只落 1 个文件即消失）→ 改用 `setsid nohup ... < /dev/null & disown` 脱离会话重跑，恢复正常。**教训：cron 夜班里的长抓取必须 setsid 脱离，否则会话中断会连坐被杀。**
- [x] 采集脚本按日期模板化：`fetch_1123.sh` / `fetch_gh_1123.sh`（`SINCE` 改为 2026-11-22）/ `prep_arxiv_1123.py` / `build_corpus_1123.py` / `build_graph_1123.py` / `merge_graph_1123.py` / `build_rows_1123.py` / `update_lancedb_1123.py` / `regen_report_1123.py`
- [x] **GHSA "零新增"判定加固**：与上窗逐条 ghsa_id 比对（而非只比数量），确认为真零新增，避免把"抓取失败"误判成"零通告"
- [x] 补充采集：GN 之外，额外从 The Decoder 站点 top-stories 栏定位到 4 篇此前未入库的旧文（single-agent / memory-forget / Ramp 增长 / Fable 5.2 绘画），补齐了本窗的证据链

---

## 3. P0 待处理

1. 🔴 **health / finance / orchestrator 三库写入冻结**（第 6–7 天）— 重启已证伪无效，需单独诊断（stale lease？job 侧的 `agent unavailable` 判定？）
2. 🔴 **OpenRouter 余额 0**（连续第 9 窗）— ZP 决策充值；且其路由层已被证明不安全（11-22 窗 Dragos 事件）
3. 🟡 **OpenAI RSS 连续第 3 窗冻结**（末条 11-20）— 源可能改为分页/改版，需换抓取入口或换源
4. 🟡 **arXiv 零新增**：周末正常，但需在 11-24 场确认新批次恢复（若仍 0 则判为采集故障）
5. 🟡 **NAS 归档累积**：`WSL/` 已有 3 份新包（含 2 份 11-22）；清理前必须先清 NAS 回收站（历史已验证）
6. 🟡 **合并重复 NightOps 作业**（0597835a vs c46eeb63）
7. 🟡 **Gateway RSS 基线重建**：24h 后（11-23 21:38 之后）再判 10 月式泄漏是否复现；当前 3.46 GB / uptime 3h51m
8. 🟡 **新增采样口**：本窗建议加"跨实验室可比的原始训练指标（perplexity）"与"多步工作任务的端到端完成率"两条线

---

**Last check: 2026-11-23 01:45 (Asia/Shanghai) — Scout NightOps**
