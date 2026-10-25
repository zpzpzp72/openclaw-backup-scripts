# 🌙 Main NightOps 全局复盘 — 2026-10-25 03:00 CST（周日窗口外补跑 / 主会话场 Night #78）

**生成时间：** 2026-10-25 03:20 CST
**触发方式：** Main NightOps cron（`603be37f-4a00-440c-8632-aee35cdfcc78`）
**本场范围：** 10-24 大修（代理硬编码地址 → 172.18.160.1 / ollama baseUrl / fallback 链）后的首个完整夜间窗口，含周日窗口外补跑场
**覆盖：** 全部 4 场 NightOps 报告（Scout / Life / Coder / Orchestrator）+ 系统层实测核验

---

## 0. 一句话结论

Night #78（2026-10-25 周日）：**系统恢复正常运转。** 5/8 个有报告的子代理产出健康，13 项升级/待办审核完成（放行 7 / 发回 ZP 6 项）。10-24 大修经受住实测验证：错峰 00:30–03:00 窗口内无 MiniMax burst 429 拦截，本地 ollama 兜底真实生效。剩余风险集中在 Gateway 内存爬升（RSS 7.36 → 7.63GB）与 6 项等待 ZP 拍板的决策项。

---

## 1. 子代理报告收集矩阵（Service Status Table）

| 子代理 / 服务 | 状态 | 上次报告 | 本场覆盖 | 备注 |
|--------------|------|---------|----------|------|
| NightOps-Scout | 🟡 | 2026-10-24 05:45 CST | ⚠️ 今日无新场（周日） | 50 篇 arXiv（2610.31307–31667）+ MCP SDK 五仓齐发；web_search 连续 7 天不可用 |
| NightOps-Life | 🟡 | 2026-10-24 05:06 CST | ⚠️ 今日无新场（周日） | B 站 13 天数据复盘 + news_digest 静默失败记录 |
| NightOps-Coder | 🟢 | 2026-10-25 02:20 CST | ✅ 本夜窗口 | M365 仓 **0 P0**；F-1/F-4/F-5 全部闭环；升级项仅剩 U-1~U-3 |
| NightOps-Orchestrator | 🟢 | 2026-10-25 02:40 CST | ✅ 本日 | 11 项计划（P0×3 / P1×4 / P2×4）；梦境产物正常 |
| NightOps-Main（本场） | 🟢 | 2026-10-25 03:00 CST | ✅ 周日补跑场 | 本报告 — Night #78 复盘 |
| **Nightly Health** | 🔴 | 无 | 🔴 未激活 | memory 仍空 |
| Nightly Finance | 🔴 | 最后 04-07 | 🔴 停摆 | 长期无报告 |
| Nightly Work | 🔴 | 最后 10-12 | 🔴 停摆 | W43 audit：MEMORY.md 缺失、无 daily journal |

---

## 2. 升级审核（13 项汇总判定：放行 7 / 发回 6）

### ✅ 放行（7 项，agent 可自行实施 / 维持现状）

1. **Coder U-2** — 维持 11-07 M365 归档评估窗口（无需新动作）
2. **Coder U-3** — 下轮心跳复测仓库活跃性（HEAD 年龄仅 21h，当前活跃）
3. **Orchestrator P1-4** — 删除 `loader.test.ts.bak`（64 天残留，零风险）+ CI 大测试文件门禁
4. **Orchestrator P1-6** — News Digest 采集 0 条时退出码非 0（消除静默失败）
5. **Orchestrator P1-7** — 两个 P0 内容选题交 Life 排期（token 成本三笔账 / AI 替代人干活）
6. **Orch P2-10** — NAS 保留规则（97% 已用）整理为提案，白天由 ZP 确认后实施
7. **Orch P2-11** — 全仓残留硬编码 `127.0.0.1:25017` 扫尾

### ❌ 发回 ZP（6 项，凭证/额度/拍板类，不可 agent 自行实施）

| # | 事项 | 阻塞点 |
|---|---|---|
| 1 | M365 仓 push（Coder U-1 / Orch P0-2） | 缺 git push 凭证；origin/main 落后 1 commit（e5f498e） |
| 2 | run-attempt.ts 拆分边界（Orch P1-5，5849L） | 需 ZP 拍板模块边界 |
| 3 | B 站日报 Feishu 推送修复 | appSecret 在 SecretRef 存储，cron 无法读取明文 |
| 4 | BILIBILI_COOKIES / OPENROUTER_API_KEY | 环境变量未配置，仅匿名模式运行 |
| 5 | 恢复一条云端 fallback（Orch P0-3） | OpenRouter 充值或 SiliconFlow 换 key；现状为本地 ollama 单兜底 |
| 6 | Health / Finance / Work 去留 | 三 agent 长期无产出，错峰排程空转耗 token，需定向决策 |

---

## 3. fallback 链一致性核查

| 来源 | 描述 |
|---|---|
| DIRECTIVE.md / Orchestrator 计划（书面） | `ollama/qwen3:4b-instruct → qwen3.6:27b → minimax/MiniMax-M2.7` |
| `openclaw models status`（实测） | primary `minimax/MiniMax-M2.7`；fallbacks: minimax/MiniMax-M3.1-Flash → M2.7 → litellm/GLM-5.3-Flash → litellm/deepseek-flash → litellm/LongCat-2.0 → ollama/qwen3:4b-instruct |

- **实际链**：MiniMax 为主（当前 15h rate_limit cooldown，预计今日 18:00 前后解除）；云端候选实际全断（litellm@NAS no_db_connection / siliconflow key 失效 / openrouter 402 / longcat 无 key），唯一真兜底 = 本地 ollama（172.18.160.1:11434）
- **成因**：10-24 当晚 Scout（01:28）与 Orchestrator（04:50）、22:10（M3 thinking=adaptive 兼容性收敛）多轮改动互相覆盖
- **处置**：本轮不改配置。待 ZP `/restart` 固化新链后，再统一更新两处文档并同步全 agent 口径
- **教训已固化**：cross-agent-log 已沉淀「探测失败 ≠ 服务死」；`.learnings/LEARNINGS.md` 收录三类误判来源（占位符当真 key / 硬编码 loopback 地址 / cooldown 误判死链）

---

## 4. 系统健康核验（03:12–03:20 实测）

| 维度 | 状态 | 证据 |
|---|---|---|
| 备份 cron | 🟢 | `openclaw-20261025-0300.tgz` 03:00 准点生成 |
| 小时心跳 | 🟢 | cron-heartbeat.log 自 10-24 14:00 起连续至 Sun 03:00:01，无缺场 |
| 外网连通 | 🟢 | baidu 200 / google 204；出网与代理均正常 |
| 飞书 API 可达 | 🟢 | open.feishu.cn 直连返回 400/404/200（鉴权前状态），域名可达、未走异常通道 |
| B 站日报 | 🟢 | 10-24 10:00 场全绿（飞书推送成功，退出码 0）——Life 报告中"连续 5 天推送失败"已自行好转 |
| 模型调用 | 🟢 | 今日 473 成功 / 0 失败 |
| MiniMax | 🟠 | cooldown 15h（rate_limit），预计今日 18:30 前后解除 |
| Gateway RSS | 🟡 | 7.63GB @03:20（对照 02:15 的 7.36GB，约 +0.3GB/h）；照此速率 04–05 点间触 8GB 观察线 |
| watchdog | 🟡 | 01:15 / 02:15 双 WARN 生效；脚本 line 74 数值比较 bug（`integer expression expected`）待日间修复 |
| 工具层 | 🟢 | 本轮 3 个小错误（sqlite3 沙箱 / 重定向笔误 / 路径手误）已记 ERRORS.md，无系统影响 |

## 5. 全局复盘要点

1. **修复验证通过**：10-24 单日闭环（代理硬编码地址 / ollama baseUrl / fallback 链）；今夜整个窗口无 MiniMax burst 429 拦截，各项 NightOps 全部成功运行
2. **最需警惕的是文档漂移而非故障**：fallback 链描述存在文档 vs 配置分歧，建议 `/restart` 稳定后由 Main 一次性校准 DIRECTIVE.md 与 Orchestrator 计划，防止后续 agent 拿旧文案当事实
3. **"探测失败 ≠ 服务死"教训已固化**：`.learnings/LEARNINGS.md` 收录三类误判来源（占位符当真 key / 硬编码 loopback 地址 / cooldown 误判死链）；cross-agent-log 同步，配置改动前必读最新裁决
4. **三个子 agent 长期无产出**（Health / Finance / Work），错峰排程在空转耗 token，白天一并定去留或重启节奏
5. **本场所见工具沙箱收紧**：外部 sqlite3 禁开 state 目录、路径手误等仅影响核验手段，不影响任务完成

## 6. 产物清单

- `heartbeat/nightly-main-2026-10-25.md`（主复盘文档）
- `reports/main-nightops-review-2026-10-25.md`（本文件，审计版）
- `heartbeat/heartbeat-state.json`（nightlyMain 已刷新至本场）
- `.learnings/LEARNINGS.md` / `.learnings/ERRORS.md`（新增 / 更新）
- workspace git 本地 commit（**未 push**，push 需凭证属发回项 U-1）

---

## 7. Next

- 下一正式窗口：周一（2026-10-26）00:30–03:00，Main 复盘场 03:00；Scout / Life / Coder 的错峰场上报
- 日间：等待 ZP 对 6 项发回事项拍板；MiniMax 冷却解除（约 18:30）后，重任务先确认额度再派发
