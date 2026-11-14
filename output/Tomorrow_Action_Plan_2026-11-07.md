# Tomorrow Action Plan — 2026-11-07 (周六)

> 生成：2026-11-06 02:40 Orchestrator NightOps（cron d7773686）
> 数据源：Scout 11-06 01:30 / Life 11-06 01:50(+05:55) / Coder 11-06 02:20 / watchdog 02:15 / automations registry
> 报告齐备度：Scout ✅ Life ✅ Coder ✅ | Finance 🔴 停摆(自 04-07) | Health 🔴 空目录(无报告)

---

## P0 — 必须今天处理（阻塞面最大）

### P0-1 [多源确认] SQLite session reclamation commit checkpoint expired
- **Signal**：11-05 全天 70 次 + 11-06 至今 8 次报错同源。受害全为 target=main 的作业（Heartbeat main 22x、main 宿主 NightOps 3~6x）；target=isolated 正常。根因：主线程与回收 Worker 用 SharedArrayBuffer 做提交授权握手，超时上限 COMMIT_DECISION_TIMEOUT_MS=5s；多 lane 并发写同一 SQLite 会话库即触发。
- **Impact**：本作业自身 lastRunStatus=error，lastDeliveryError 即为该签名 —— Main 侧收不到 NightOps 结论。Health/Finance/Heartbeat 同相位作业全部受累。
- **Blocker**：需停 Gateway + `openclaw doctor --fix` + 重启（需 owner 在场）。
- **Next Step**：ZP 白日授权一次停机修复；修复后立刻错峰 7 个 agent 的 heartbeat（当前几乎同相位）；长期方案为升级 openclaw 或收敛会话库写入并发。

### P0-2 NAS /mnt/h 100% 满，凌晨备份必失败
- **Signal**：/mnt/h 可用 3.8G / 7.2T（100%）。单份备份 5.7G（openclaw-20261105-0300.tgz = 6.1GB）。WSL 目录 22 份 tgz ≈ 157G；回收站另有 27 份 ≈ 123G 未释放。
- **Impact**：今晚 03:00 备份将因空间不足失败 → 恢复点断裂，等于失去最近一次可用备份。
- **Blocker**：清回收站需人工确认；删 tgz 需授权。
- **Next Step**：①清空 /mnt/h/#recycle/AI/openclaw.zone/WSL 释放 123G（收益最大、风险最低）；②保留最近 3 份 tgz，其余移入回收站；③把备份阈值/保留策略写进脚本。

### P0-3 Coder 新 P0：stdlib 遮蔽导致服务不可启动
- **Signal**：`/home/zhiping/M365_Copilot_Playwright_Proxy/selectors.py` 遮蔽 Python 标准库 `selectors`；`python3 -c "import app"` → AttributeError: module 'selectors' has no attribute 'SelectSelector'。跨 cwd / PYTHONPATH 注入同样复现。
- **Impact**：asyncio/subprocess/aiohttp 全链受影响 → 服务当前不可启动。此 P0 前 5 轮均未检出（历史扫描只 grep bare-except，未做 import 链验证）。
- **Blocker**：修复为纯重命名（git mv selectors.py → copilot_selectors.py + 改 app.py import），需 Main 授权。
- **Next Step**：ZP 授权后由 Coder 执行重命名并 py_compile + `import app` 回归验证，验证通过再谈 push。

---

## P1 — 今日推进

- **P1-1 M365 仓库停滞 D13 + push 通道阻塞**：HEAD e5f498e 停于 10-24 05:00（~213h），ahead 1 / behind 0，非分叉。`gh api` 正常（private, push 权限在），但 `git ls-remote` = gnutls_handshake() failed、`fetch --dry-run` rc=1 → 阻塞在 git HTTPS 传输层/TLS，不是凭证。上轮"push 可行"结论系 `ls-remote | head` 取到 head 的退出码造成的假阳性（rule #8 反转，教训需固化）。建议：换 SSH 或改用 `gh` API 提交，或先确认出站 TLS 代理策略。
- **P1-2 云端 fallback 全断 + MiniMax 429**：OpenRouter 402×82（余额 0）；LiteLLM@NAS no_db_connection；SiliconFlow key 失效；LongCat 无 key → 本地 ollama（172.18.160.1:11434，实测可达）是唯一兜底。本地 ollama/qwen3:4b-instruct 实测 3.5s 可用。
- **P1-3 Life 报告连续断 2 场（11-04/11-05）**，本场 11-06 恢复（status=ok, delivered=true, 204.8s）。真因：fallback 链耗尽 → 429/402 → 仅剩 ollama 4B → stuck session recovery age=465s 主动 abort，abort 阈值 = max(300s, 120s×3)=360s → 报告型 cron 单次必须 < 6 分钟。Life 已把四兄弟作业统一为 model=minimax/MiniMax-M2.7、fallbacks M3.1-Flash → M3 → ollama/qwen3.6:27b（Coder 原跑 4B 导致连续 4 场 context overflow）。
- **P1-4 web_search（duckduckgo）连续第 16 次 provider_error**；alignment.openai.com 不可达（直连 SSL_ERROR_SYSCALL，走 25017 代理 CONNECT tunnel 400）→ OpenAI misalignment 报告改由 The Decoder 转述。
- **P1-5 cron registry 计数矛盾**：Life 场 automations list 显示 total=1，Scout 场显示 30 jobs；本作业 automations list 亦只返回自身 1 条 → registry 可见性异常，需 owner 在 Control UI 核对真实 job 数与触发器状态。

---

## P2 — 观察与清账

- **P2-1** news digest 11-05 产物 20,555B + 飞书推送成功（om_x100b6188359c24a0c30bcc9fd91954f），但作业状态仍 error(7x) → 另一签名 SESSION_PLACEMENT_TURN_SETTLEMENT_CLOSED 发生在 turn 收尾，产物与推送均成功。**判定作业失败前必须先核对产物与飞书回执**。
- **P2-2** BILIBILI_COOKIES / OPENROUTER_API_KEY 仍未配置。
- **P2-3** 备份完成邮件发送失败（已忽略，不影响清理与心跳）。
- **P2-4** B站采样口径统一为 ps=20×3（本场 60 条 vs 11-03 的 100 条），下场均按新口径。

---

## 🟢 已闭环（不再占用注意力）

- **Gateway 内存**：2.78GB / uptime 18.9h，watchdog 趋势 −586 ~ −859 KB/h（负增长），CPU 24%。与 10-28~10-30 的 12GB 级连续劣化不同 → **无需重启**。
- **根分区磁盘**：/ 155G/1007G，17%，健康（此前 98% 告警已缓解）。
- **M365 bare-except**：全仓 grep = 0 hits，历史 P0 维持闭环；.gitignore 在位，tracked .pyc = 0。
- **代理 25017 / ollama 11434**：172.18.160.1 双端口 TCP 可达。
- **Scout 抓取管线**：arXiv 新 124 条、GitHub 新 tag 9、LanceDB 464 行 assert 通过、知识图谱 2,375 节点/5,593 边/37 社区。
- **Coder workspace 卫生**：38 个 >7d review + 15 个 >90d daily 已归档（git mv，可回滚）。

---

## 📌 明日（11-07）需 Main 拍板的三件事

1. **停机修复 SQLite 会话库**（P0-1）—— 停 Gateway → `openclaw doctor --fix` → 重启，顺带做 7 路 heartbeat 错峰。
2. **NAS 回收站清理授权**（P0-2）—— 释放 123G，保住明晚 03:00 备份。
3. **M365 selectors.py 重命名授权**（P0-3）—— 先修 P0 再 push。

## 💡 明日内容侧机会（Life 新增选题 4 条）

① AI 短剧"没有呼吸" × 投币收藏率（知乎+公众号 ★★★，原创度最高）
② OpenAI 自曝 GPT-6 Astra 偷懒 40% / 监控盲区（知乎+公众号 ★★★）
③ 辛顿切尔诺贝利 × 赛义德暂停 AI 研发（知乎+公众号 ★★★）
④ SemiAnalysis GDPx：206 任务无一超 12%，最强模型也仅 12%，中文侧零覆盖（公众号+X ★★☆）
