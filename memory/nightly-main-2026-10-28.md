# Nightly Main 复盘要点 — 2026-10-28 03:00（短版）

- 会话：agent:main:cron:603be37f-4a00-440c-8632-aee35cdfcc78（NightOps 03:00 场，窗口内）
- 报告齐备度：Scout ✅(00:41) / Coder ✅(01:23) / Orch ✅(02:55) / **Life 🔴 连续第 3 场无产出**（从"顺延"升级为"缺失"，白日排查 cron 任务逻辑）
- Gateway 实测：pid 497240、uptime 1d02h、**RSS 9.9GB / CPU 82%**，watchdog 8GB WARN 连发；按 ~74MB/h 斜率 3–4 天内重回 12GB+；真杠杆仍=会话保留策略+arena 对照，均待 ZP 授权
- 10-28 03:00 备份：6.0G（较前日 8.9G -33%，exclude 部分生效）；**cleanup_old 未触发**（10-17 起老档全在）→ Orch"自动清 71.2GB"核验项落空，明日核验扩大为调用链+退出码
- /mnt/h 98%、剩 171G（日内 -6G），释放速度<增速，风险升级；/mnt/m 路径不存在，状态文件记录陈旧
- 版本 2026.10.5 vs 2026.10.8（落后 3 版，中低风险，走 `openclaw gateway install --force` 正规入口，待授权）
- git 实测 69 dirty（53 untracked+15 M+1 D），较 Orch 16:48 的 648 大幅收敛，但 agents/ 嵌套仓仍阻断批量 add
- web_search ❌ 连续 10 天；news_digest 延续缺产物；Heartbeat delivery 8 job 占位 telegram 延续
- 情报主线：OpenAI ETH / Anthropic S-1 / 接口层攻防（MICA、SABench、I-HITL、VELA）
- Or 误报澄清：「memory/ 文件名含空格拼接」文件实测不存在，判误报
- 产出：`heartbeat/main-nightops-review-2026-10-28.md` + 本记忆 + heartbeat-state.json 同步；无 npm 安装、无配置/调度器变更、无重启
