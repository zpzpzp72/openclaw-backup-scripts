- [2026-10-24] [Orchestrator] 根因定位：NightOps 连败5次系代理地址硬编码 127.0.0.1:25017（WSL2内不通），非服务宕机；已改 172.18.160.1，News Digest+Feishu 恢复
- [2026-10-24] [Orchestrator] ollama provider baseUrl 同样指向 localhost 致 fallback 失效，已改 172.18.160.1:11434；litellm NAS 端 no_db_connection 已移出 fallback 链
- [2026-10-24] [Orchestrator] M365 repo 终止220天冻结：browser.py bare except 已修 + .gitignore + commit e5f498e
- [2026-10-24] [Orchestrator] 第二根因：MiniMax Token Plan burst 额度耗尽（02-05点 429×382）；已加固 fallback 链首选项为本地 ollama/qwen3:4b-instruct；建议 NightOps 5 路错峰至 00:30-03:30
- [2026-10-24] [Main] 裁决：Scout 与 Orchestrator 的 fallback 修改互相覆盖（Scout 01:28 把已挂的 litellm@NAS 提为 8 agent 首位，Orchestrator 04:50 又从 defaults 移除）。已实测 litellm=400 no_db_connection，统一收敛为 ollama/qwen3:4b-instruct → ollama/qwen3.6:27b → minimax/MiniMax-M2.7
- [2026-10-24] [Main] 裁决：health primary 原为 longcat/LongCat-2.0（401 无 key），已改为 minimax/MiniMax-M2.7；config validate 通过 + hot reload revision 4
- [2026-10-24] [Main] 执行：9 个 NightOps job 错峰至 00:30-03:00，避开 MiniMax Token Plan burst 耗尽窗口 02:00-05:00（今日 402 次 429，峰值 04:53-05:01）；Main NightOps 与 NightOps-Orchestrator 同撞 03:00 已拆开
- [2026-10-24] [Main] 观测：Gateway RSS 二次劣化 3.75GB(重启后) → 5.9GB(3.7h)，CPU 278%；model-fetch 近 30min 成功 184 次；本地 ollama 是当前唯一可用兜底
- [2026-10-25] [Orchestrator] NightOps 汇总完成：生成 output/Tomorrow_Action_Plan.md，基于 coder 10-25、scout 10-24 夜报与 cross-agent-log 裁决；关键项 = 错峰后 NightOps 验证 / M365 push 凭证缺失 / 云端 fallback 恢复

- [2026-10-26] [Orchestrator] NightOps汇总完成：RSS二次劣化确认(重启→10.9GB/2d)，重启+根因复查列P0-1/2；429凌晨再达83%列P0-3；deepseek新可用列入建议P1-5b；计划见 output/Tomorrow_Action_Plan_2026-10-27.md
- [2026-10-26] [Main] Coder 状态记录口径澄清：code_report/coder-review 2026-10-26 已 02:30 落盘，coder cron 存活、nightly 报告路径断点缺席；本次以 10-25 复盘与 code_report 补位，非产出缺位
- [2026-10-26] [Main] Coder状态口径澄清：code_report/coder-review-2026-10-26已02:30落盘→coder cron存活、nightly路径断点缺席，以10-25复盘补位，非产出缺位
- [2026-10-26] [Main] 03:00复盘落盘main-nightops-review-2026-10-26.md：Gateway RSS 10.29→10.94GB爬升+CPU86.9%不回落(uptime1d16h)，根因=会话量线性增长非泄漏，重启仅买时间，真杠杆=会话转录保留策略；MiniMax 429=配额管理非故障；ZP白日队列：重启/套餐三选一/M365 push凭证/deepseek临时链拍板/BILIBILI_COOKIES与OPENROUTER_API_KEY补齐/health+finance去留

- [2026-10-27] [Orchestrator] NightOps 10-28 计划已生成 output/Tomorrow_Action_Plan_2026-10-28.md；P0=gateway 内存二次爬升+fallback 重写+MiniMax 套餐决策
- [2026-10-27] [Main] 03:00复盘落盘main-nightops-review-2026-10-27.md：确认用户01:13重启Gateway，pid 497240 RSS 5.95GB/2h回升至5.95GB（+0.4GB/2h），会话保留策略仍待ZP授权；03:00备份完成9.5GB落盘正常（心跳status时序滞后）；磁盘98%水位持续，P0关注；Scout 10-27缺位，Orch/Life/Coder三源齐备
- [2026-10-28] [Orchestrator] NightOps 10-29 计划已生成 output/Tomorrow_Action_Plan_2026-10-29.md；P0 = Gateway RSS 9.31GB 重启+保留策略、M365 push 凭证(10-29 截止)；Scout 10-28 齐备，Life 顺延 10-26
