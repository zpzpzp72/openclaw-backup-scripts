# 🌃 Main NightOps 复盘 — 2026-10-26 (周一) 03:00

**Runtime:** agent=main | session=agent:main:cron:603be37f
**窗口：** ✅ Mon–Fri 00:30–03:00（03:00 场）
**收集方式：** 落盘报告 + cross-agent-log + sessions_list 全景（无挂靠 subagent）

---

## 1. 子 Agent 报告收集

| Agent | 报告 | 状态 | 摘要 |
|---|:---:|---|---|
| Scout | `nightly-scout-2026-10-26.md` (00:45) | ✅ 满覆盖 | **MCP servers v2.1.0 单日修 8 CVE**（GHSA×8；semver 排序陷阱→需显式版本安装）；CVE-2026-111497 Brotli RCE CVSS 9.2；spec 90 天未发版；web_search 连续 8 天 ❌；arXiv 周末 0 增量（已核验批次边界）；LanceDB 118→135 行 |
| Life | `nightly-life-2026-10-26.md` (00:50) | ✅ 滬覆盖 | B站 14 天 140 条全量重算：播放↔传播效率**负相关**；推翻"AI 投币反超"与"中文热榜主题拐点"两旧结论（中文 digest 源码级污染，中位龄 234 天）→ 修复路线：改走 `parse_bilibili_popular` / `parse_zhihu_hot` 直抓；痛点第一 = token 成本 10.0%；P0 选题①中美同题/②B站复盘 就绪；微博/X/B站分区榜三通道 🆕首通 |
| Coder | `code_report-2026-10-26.md` / `coder-review-2026-10-26.md` (02:30) 已落盘，`nightly-coder-2026-10-26.md` 缺位 | ⚠️ | **cron 存活、nightly 落盘路径断点**，非产出缺位；以 10-25 复盘补位：M365 仓 0 P0；提案 nightops_scan.sh (P1) / copilot_proxy lint (P2) / 归档脚本 (P3) |
| Orchestrator | `nightly-orchestrator-2026-10-26.md`（02:45） | ✅ | 三源整合 + Tomorrow_Action_Plan（P0×4 / P1×7 / P2×8）；IMA 三轮讨论按预算跳过 |
| main(自身) | 本文件 | ✅ | 全局复盘落盘 ✓ |

## 2. 系统服务状态总表

| 服务/组件 | 状态 | 说明 |
|---|:---:|---|
| Gateway 进程 | 🔴 | pid 319857：RSS **10.29→10.94GB**（01:02→03:12 实测），CPU 86.9% 不回落，uptime 1d16h。根因：**非泄漏，是会话量线性增长**（15194 anon 映射 / 2571 会话 ≈5.91 映射·会话，10/24 ≈7.2 同量级）；heap 仅 496MB，9.88GB 堆外 → `--max-old-space-size` 无效；**真杠杆 = 会话转录保留策略**（1956 json + 605 zst，删除/归档须 ZP 授权）。重启仅买时间 |
| 备份归档 | 🟢 | `openclaw-20261026-0300.tgz`（03:13 落盘 9.2GB），近 5 日连续无断档 |
| 备份大盘 | 🟡 | /mnt/m 7.0T/7.2T **97%**（剩 271G）→ 备份盘接近满，建议 ZP 关注容量 |
| 飞书出站 | 🟢 | 200。⚠️ 主群会话 `status=failed`，contextTokens 191k/204.8k（>80%）→ 需核查 |
| MiniMax 429 | 🟡 | 凌晨最高 83%（M2.7 报 2056 用量上限）= 配额管理非认证故障；查余量 `mmx quota`（CN key → api.minimaxi.com） |
| fallback 链 | 🟡 | 统一口径 4b→27b→M2.7；27b ECONNREFUSED 待修；建议 P1-5b 临时链 4b→deepseek-flash/pro(200)→M2.7，待 ZP 拍板 |
| 版本 | 🟡 | 运行 2026.10.5 vs latest v2026.10.7；node 分裂（shell v24.15.0 / gateway v26.10.0）；a74727b2 声称"仅改了些行、未重启"，但 gateway 仍为 10-24 11:01 起的 pid 319857 → "归一 node v26"修复未落地，白昼复核 |
| web_search | 🔴 | 连续 8 天 provider_error |
| news_digest | 🔴 | 中文源被搜索历史页污染（中位龄 234 天，line 1422 以搜索代直抓）；摘要 OpenRouter 402 余额 0；BILIBILI_COOKIES / OPENROUTER_API_KEY 仍缺 |
| B站日报+飞书推送 | 🟢 | 连续 2 天成功（此前 11 天连败）；SecretRef 经 feishu-cred.env 解决 |
| 微博/X/B站分区榜 | 🟢 🆕 | 10-26 首通（50/1215/97 条）；知乎 401、Reddit 反爬 ❌ |
| wechat-cli | 🟢 | 依赖修复可读 500 条群历史；数据时效停 8/28 |
| graphify / LanceDB | 🟢 | 504 节点 / 1207 边 / 48 社区；LanceDB 118→135 行 |
| M365 仓 | 🟢 | 0 P0，近 20 commit 无运行代码变更 |

## 3. 升级审核（Orch 计划逐项裁决）

**原则：** 安全/数据风险优先；ZP 白日队列不自动代做；配置/调度器改动先报后做；**不替 ZP 动 systemd（v3 规则）**。

| # | 事项 | 裁决 | 路由 |
|---|---|---|---|
| P0-1 | 重启 Gateway + 会话保留策略 | ✅ 分析成立，但不替 ZP 动 systemd——重启请 ZP 亲自操作或明确授权；真杠杆 = 会话保留策略，删除需授权 | **ZP 白日** |
| P0-2 | 重启后 3–4h 复查 RSS/CPU | ✅ 待 P0-1 落地后执行 | Orch→Coder |
| P0-3 | MiniMax Token Plan 三选一 | ✅ 配额机制已录入 MEMORY；凌晨 429 83% 印证 | **ZP 拍板** |
| P0-4 | M365 push 凭证 PAT/SSH | ✅ 凭证类必须 ZP 亲自配置（截止 10-29） | **ZP 白日** |
| P1-5 | qwen3.6:27b ECONNREFUSED 修复 | ✅ Coder 白天场自可执行（探活+换地址） | Coder 白天 |
| P1-5b | 临时链 4b→deepseek-flash/pro→M2.7 | ✅ deepseek 实测 200；写入属 ZP 拍板后 Main 白天执行 | ZP 拍板 → Main |
| P1-6 | 10-24 四件建议核验 | SecretRef ✅ 已解决；其余 3 项（news_digest 0条退出码 / BILIBILI_COOKIES / OPENROUTER_API_KEY）未核验 | ZP + Coder/Life |
| P1-7 | life DIRECTIVE 注入 + 口径统一 | ✅ 批准，跨 agent 写入由 Main 白天主会话执行 | Main 白天 |
| P1-8 | 监控 08:00 news digest | ✅ Orch 心跳照办 | Orch |
| P2-9 | B站 10-26 增量日报 | Life 白天场 | Life |
| P2-10 | health/finance 去留 | 判定维持（跑但产出缺位），去留 ZP 决策 | **ZP 决策** |
| P2-11 | Gateway 膨胀改造 | 并入 P0-1 保留策略 | Coder + ZP |
| P2 | untracked 收口 / PR 评估 / 插件加固 / 三件复验 | 例行 | Coder / Orch |

## 4. 全局复盘

**本场特征：报告收集层 100% 落地，执行层 0% 主动执行**——受 v3 规则与授权边界约束，所有需变更项均列为 ZP 白日队列。

**A. 质量亮点**
- 错峰改制后首次「两绿一橙」：Scout/Life 准点落盘，Coder cron 存活但 nightly 落盘断点；口径已沉淀至 cross-agent-log。
- Orch 报告整合质量高；但 a74727b2「已归一 node v26」标注与 gateway 未重启的实况矛盾，白昼复核。
- 主群会话 status=failed（191k/204.8k >80%）→ 已列入观察。

**B. 系统层三根轴**
1. **Gateway 内存——定位已定，处置待 ZP**：RSS 10.29→10.94GB 爬升 + CPU 86.9%；回归分析确认非泄漏、会话量线性增长；heap 堆外 9.88GB；真杠杆=会话保留策略。重启买时间，删除资产须 ZP 授权。
2. **MiniMax 429=配额管理**：凌晨 429 最高 83%，错峰后仍撞窗口耗尽。三选一 → ZP。
3. **版本/配置漂移**：2026.10.5 vs 10.7；node 分裂与「已修复」标注矛盾 → 白昼复核。

**C. 内容/情报主线**
- 「批准必须绑定到具体效果」从论文到 CVE（servers v2.1.0 八漏洞）：授权是带作用域、时效、效果的证明对象。
- MCP 协议层停滞 vs 实现层狂奔：注意力应转向工具与安全面。
- 内容 P0 双选题就绪：①「20 万媒体岗位中美同题」②「B站 14 天复盘」可同日双发。
- 数据卫生规则固化建议：趋势结论先核日期；单日小样本不作趋势依据。

**D. 本场无变更说明**
- 无 npm 安装、无配置/调度器变更；产出：本报告 + nightly-main 记忆 + heartbeat-state 同步。写入层面唯一瑕疵（cross-agent-log 短暂出现重复条目，已当场去重并核验）。

## 5. 下一场关注点（10-27 周二 00:30 起）

| 关注点 | 判定 |
|---|---|
| Coder nightly 恢复 | `nightly-coder-2026-10-27.md` |
| 主群会话 failed 恢复 | sessions_list 快照 |
| 08:00 news digest（settlement closed 复发） | cron 是否成功 |
| 重启后 RSS 回落 | 增长 <200MB/h |
| MiniMax 429 / deepseek 临时链 | `mmx quota` + log |
| arXiv 周一批次 | 突破 2610.31667 |
| MCP spec 打破 90 天 | tags/releases |
| openclaw 本体增速 | +148 锚点验证 |
| web_search 恢复 | duckduckgo/webserp |

---
**产出：** `heartbeat/main-nightops-review-2026-10-26.md` · `memory/nightly-main-2026-10-26.md` · heartbeat-state.json 同步
**无 npm 安装 / 无配置变更 / 无 subagent 挂靠。下一场：2026-10-27 周二 00:30 起。**
