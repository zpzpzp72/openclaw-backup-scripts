# Tomorrow Action Plan — 2026-11-16（周一）

> 生成：2026-11-15 02:40 Orchestrator NightOps｜来源：Scout/Life/Coder 11-15 场 + 自测

## P0（Owner 决策，我无权执行）
1. **Gateway 重启 + `doctor --fix`（health 库）** — health 库 mtime 仍冻结 11-05 07:18，`Cron maintenance failed` 每 60s 一条（实测 60 条/h）。11-14 重启**未**解决 health 库（仅 main 库解冻）。本次已定位：PID 795 持 health 库两个 fd，read-only recover 被拒 → 必须**先停 gateway**再 `openclaw doctor --fix --session-sqlite-agent health`，再启动。
2. **NAS 备份链验证** — Scout 场已清 35 份回收站（释放 185GB → 186G 可用）；`~/.openclaw-backup.heartbeat` 仍 `status=error / hours_since_last_backup=233`（最后归档 11-05）。**11-15 03:00 是端到端验证点**，需确认 `openclaw-20261115-0300.tgz` 落盘 + heartbeat 转 ok。
3. **QQ SMTP 授权码重生成** — 备份邮件自 11-08 起 535 Login fail，`backup-cron.log` 连续 8 次「Connection unexpectedly closed」，断链 7 天仍静默。
4. **`git push origin HEAD`（M365_Copilot_Playwright_Proxy）** — HEAD `219f199`，ahead 5 / behind 0，dry-run rc=0、ls-remote 5/5 全绿、非分叉；含 2 个 P0 + 8 个 P1 修复。远端 pushed_at 仍 2026-03-18（停滞 8 个月），Recreate 废弃风险继续累积。

## P1（agent 可自动推进，需授权项已单列）
5. Gateway heap 4096 → 8192MB 后择机重启（当前 RSS 4.6–4.9GB，已顶满 4096 堆上限；systemd Memory 7.0G / peak 11.1G）。
6. OpenRouter 余额连续第 5 窗为 0 → 充值或换 key（B站日报 AI 总结、知乎字幕因此关闭）。
7. 补 `BILIBILI_COOKIES` + 知乎 cookie（官方热榜 API 401 已 7 场）、ddg 搜索返回 000 → 换搜索入口。
8. **B站日报 10:00 / news_digest 08:00 连续 6 天未执行** — 根因是 WSL 休眠导致系统 crontab 未触发（非脚本故障）；建议加「开机补跑」或迁到 gateway 内置调度。
9. 给 `run_news_digest.sh` 飞书推送段加**独立日志**（当前推送是否送达长期不可证实）。
10. 合并重复 NightOps 作业：工作日版 `0597835a` vs 每日版 `c46eeb63`（Scout 场报）。
11. heartbeat-coder 孤儿 receipt lease → 重启后应自愈，若仍 error 则改跑独立会话（消除与 poll 会话自指阻塞）。

## P2（观察项）
12. Life NightOps 11-14 场 `OPENCLAW_DIRECT_ABORT`（1201s 后中止）；11-15 场已正常完成 → 观察下一场是否复现（疑 MiniMax 配额/长任务超时）。
13. cron registry 视图矛盾：`automations list` total=1 vs DB 30 jobs，已持续 8 场 → 需 owner 确认视图范围。
14. `heartbeat-orchestrator` 状态 `no-route` → 需设 `commands.ownerAllowFrom`（投递路由未设，heartbeat 全在等路由）。
15. Google AI blog RSS 连续第 8 窗空壳 → 从采集清单降级。
16. 清理 WSL 目录 11-05 前 7 份旧归档（可再腾约 40GB，本场保守未动）。

## 🟢 本场已闭环（无需再决策）
- NAS 空间：100% 满 / Avail 4.7MB → **186G 可用**（Scout 场执行回收站清理）
- main 会话库写入冻结：**已解**（11-14 20:06 重启后 mtime 实时更新）
- SQLite reclaim 错误：180 次/h → **60 次/h（全部归因 health）**，租约 19 行全属 PID 795，无 stale、无泄漏式重复
- heartbeat:main consecutiveErrors 72 → **0**（现为空心跳文件 → skipped，属正常）
- NightOps 双轨：per-agent 4 路全 ok；legacy `NightOps-*` 4 路仍 disable（正确）
- 本地原生备份：11-14 20:06 一轮 **ok / 7.1GB**（`backup_runs` 表确认），仅存 11-07 两份 + 11-14 一份
- Coder：11-15 新增 commit `219f199`（SSE 未落盘 / on_cleanup TypeError / history 错形 JSON 崩溃 / 活动会话按插入序误选）+ HTTP 层集成门禁；4/4 门禁首次真实执行全 PASS
- Scout：`build_corpus_1115.py` STAMP/PREV 分离修正（`sed s/1114/1115/g` 会覆盖 11-14 产物，已 git checkout 恢复）

## 需 Owner 回答的一句话
**明天上午是否有空窗停 Gateway？** health 库必须停机才能 doctor --fix，且建议同窗把 heap 提到 8192，一次重启解决两件事。
