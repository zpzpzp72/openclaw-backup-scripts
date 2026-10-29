# Tomorrow Action Plan — 2026-10-31（周六）

> 生成：2026-10-30 02:45 Orchestrator NightOps（cron d7773686）。报告源：Scout 10-30 ✅、Coder 10-30 ✅、Life 10-29 ✅、Main 10-29 ✅；Health/Finance 仍无产出。

## P0
1. **Gateway 重启**：RSS 12.25GB（第 6 次劣化，2h 内 +0.46GB，根因=trajectory 事件 256KB 展开副本，已定位）→ ZP 择机执行；重启后 Coder 3–4h 复测 RSS/增速（目标 <200MB/h）
2. **/mnt/h 98%**：回收站滞留 17 份被删备份 ≈140G 未真正释放 → ZP 授权清理（不可逆，唯一需拍板的删除项）；配套：会话保留策略授权（清 1956 json + 605 zst）防 RSS 回升
3. **OpenClaw 升级拍板**：本地 2026.10.5 → npm 10.9（0 天新鲜度，风险高）或浸泡 2 天选 10.8；检查清单已备（822f46fd），需 owner + 维护窗口

## P1
4. **模型单点加固**：本地 ollama 为唯一兜底 → OpenRouter 402 充值 / LiteLLM@NAS DB 恢复 / MiniMax 429 持续跟踪（10-29 早峰未观测到新增 429，观察再现）
5. **web_search 连续 11 场失败** → 将知乎直采（api.zhihu.com/topstory/hot-list 已验证 200）接入 news digest，替代中文源中位龄 231 天的搜索通道
6. **git 收口**：push 凭证（U-1）→ backup 2 commits + copilot_proxy 5 orphan commits（含 e5f498e bare except 修复）；凭证未到位则执行 U-4「NightOps 零 commit」防孤儿继续堆积
7. **采集修复**：微博 hot_band 403（补 cookie 或固化 tophub 镜像）；微信数据 Windows 侧重导出（停自 08-28）

## P2
8. **停摆 Agent 处置**：Health memory 空、Finance 最后 04-07 → ZP 决策：复活 / 合并 / 关闭
9. **小修收尾**：watchdog line50 语法错；/mnt/m 心跳 stale 条目修正；ruff/pyflakes 安装（U-5）；copilot_proxy P1-1（startup create_task 无保护）
10. **NightOps 错峰**：5 路集中于 04:50–05:20 撞 MiniMax burst → 移至 00:30–03:30

## 亮点
- **安全**：.backups（434MB 备份+含凭据配置）已被 Coder 移除——本周期最重要安全修复
- 备份推送链幂等化端到端实测通过；NightOps 报告链恢复连续性（Scout/Coder 连续两晚准点落盘）

## 观察点（Scout 10-31 场）
MCP SEP-3392 首个 SDK 实现 / Mistral Large 4 评测与许可 / Gemini 4 Carbon 是否公开 / 429 是否缓解 / RSS 若不重启预计 ~12.9GB
