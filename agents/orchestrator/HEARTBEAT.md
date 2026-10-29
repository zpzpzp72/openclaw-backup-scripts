# HEARTBEAT.md — Orchestrator Agent

## Step 1. 收集报告
- scout: research_brief.md
- life: content_plan.md
- coder: code_report.md

## Step 2. 综合分析
- 识别明日最重要的 3 项任务
- 识别阻碍点
- 识别机会点

## Step 3. 输出明日计划
生成：
- output/Tomorrow_Action_Plan.md

## Step 4. 提交给 Main 审核

---

## 关键指标追踪（更新于 2026-10-24）

- [x] **代理 25017** — 🟢 **已修复 2026-10-24**：并非服务宕机，而是脚本硬编码 `127.0.0.1:25017`（WSL2 内不通）。实际代理在 `172.18.160.1:25017`。已修 `openclaw_news_digest.py`(3处) + `run_news_digest.sh`(2处)
- [x] **ollama provider baseUrl** — 🟢 **已修复 2026-10-24**：`127.0.0.1:11434` → `172.18.160.1:11434`
- [x] **fallback 链** — 🟢 移除死链 `litellm/MiniMax-M2.7`（NAS `no_db_connection`）→ 现为 `['ollama/qwen3.6:27b','longcat/LongCat-2.0']`
- [x] **News Digest** — 🟢 恢复：2026-10-24 01:11 生成 20123 bytes 报告，Feishu 推送成功
- [x] **M365 Repo 冻结** — 🟢 **已解冻**：commit `e5f498e`，browser.py bare except 修复 + .gitignore，终止 220 天冻结
- [ ] **NightOps 全线验证** — 🔴 04:50 仍 error，但原因已变为 **MiniMax Token Plan burst 额度耗尽 429**（今日 02-05点 382 次），与 proxy 故障是**两个独立问题**
- [x] **fallback 加固** — 🟢 链首改为本地 `ollama/qwen3:4b-instruct`（实测 3.5s）；已加该模型到 ollama provider；hot reload 生效
- [ ] **云端 fallback 全断** — 🔴 LiteLLM@NAS(no_db_connection) / SiliconFlow(key 失效) / LongCat(无 key) / OpenRouter(402) → **本地 ollama 是唯一兜底**
- [ ] **NightOps 错峰** — 🔴 5 路 NightOps 集中在 04:50-05:20，正撞 MiniMax 额度耗尽区间，建议移到 00:30-03:30
- [ ] **OpenRouter** — 🔴 402 余额耗尽，news digest 仅靠 MiniMax 单点
- [ ] **LiteLLM@NAS (192.168.31.231:4000)** — 🔴 后端 DB 挂，11 个模型全不可用
- [ ] **Life** — 🔴 最后报告 09-08（46 天）
- [ ] **Health** — 🔴 memory 目录空
- [ ] **Finance** — 🔴 最后报告 04-07
- [ ] **残留硬编码扫描** — 🟡 全仓 grep `127.0.0.1:25017`

### ⚠️ 教训（避免重复误判）
> 「代理 25017 DOWN 12+ 天」被当作**服务宕机**跟踪了 12 天，实际是**地址写错**——代理一直在跑。
> **任何 "DOWN" 结论，必须先对比「实际监听地址 vs 代码里硬编码的地址」，再上报宕机。**
