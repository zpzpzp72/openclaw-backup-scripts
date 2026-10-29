# Tomorrow Action Plan — 2026-10-29（周三）

> 生成：2026-10-28 02:40 Orchestrator NightOps（cron d7773686）。报告源：Coder 10-28 02:33 ✅、Scout 10-28 01:41 ✅、Life 顺延（10-26 最新）；Main 10-27 复盘已并入。

## P0（今日 10-28 白天优先）
1. **Gateway 497240 RSS 9.31GB 破 8GB 阈值**（第 4 次劣化，增速 6.7→9.31GB/<17h）→ ZP 择机重启；Coder 在重启后 3–4h 复查 RSS/CPU（目标 <200MB/h、CPU 不持续 >80%）
2. **会话保留策略授权**（清 1956 json + 605 zst）→ 真杠杆，须 ZP 亲自/授权，防 RSS 回升
3. **M365 push 凭证（PAT/SSH）** → 10-29 截止，剩余约 1 天，ZP 白日队列最高位

## P1
4. **copilot_proxy 分叉收敛**：origin/main 独有 1 (d2af52a)、本地领先 5（U-1 push 凭证，含 e5f498e bare except 修复）；无凭证期间批准 Coder「NightOps 零 commit」模式（U-4）防孤儿堆积
5. **备份 4.1GB 体积骤减核对**：tar 内容清单 vs exclude 规则（疑未含 LanceDB 9.5G）；并入 backup.sh `--exclude .memory-write.lock.lock`
6. **/mnt/h 98% 水位**：RETAIN_DAYS=30 名存实亡（39 份未清）→ ZP 清旧档
7. **监控 10-28 08:00 news digest** 是否成功（10-27 08:00 场已恢复 ✅，需连续性验证）

## P2
8. **Life 补 10-27/10-28 缺席报告**；Health / Finance 长期停摆去留 → ZP 决策
9. **U-5**：安装 ruff/pyflakes 纳入 NightOps；修复 app.py startup `asyncio.create_task(agent.start())` 无 try/except（P1-1）
10. **Orch NightOps 错峰**：本场 02:40 仍在 MiniMax burst 窗口（02:00–05:00）内 → 建议前移至 00:30 前；残留 `127.0.0.1:25017` 全仓 grep 收尾

## 阻塞（需 ZP 拍板项）
- MiniMax Token Plan 三选一（配额管理 / 升级 / 换源，凌晨 429 83% 峰值）
- OpenRouter 402 余额 0、LiteLLM@NAS DB 挂、web_search 连续 9 天失败、Heartbeat 8 job 占位 telegram:123456789 改飞书
- BILIBILI_COOKIES / OPENROUTER_API_KEY 补齐

## 亮点
- 本场无新增 429；10-27 08:00 新闻摘要恢复推飞书成功；Coder 已回归并遵守 rule #5 零 commit
