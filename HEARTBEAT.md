# OpenClaw Main Session Heartbeat
- last_check: 2026-10-24T05:10:00+08:00
- last_run_epoch: 1792789800000
- status: ok (with escalations)
- NightOps_window: Mon-Fri 00:30-03:00  ← 2026-10-24 改（原 21:30-23:30 + 04:00-05:00，避开 MiniMax burst 耗尽窗口）
- last_nightly_run: 2026-10-24T05:00:00+08:00
- main_session_id: agent:main:main
- nightly_reschedule: 9 个 NightOps job 已错峰至 00:30-03:00
- fallback_chain: 8 agent 统一为 ollama/qwen3:4b-instruct → ollama/qwen3.6:27b → minimax/MiniMax-M2.7（已剔除死链 litellm/longcat）
- optimization_rule: NightOps 讨论中发现更优的网络/系统优化方式 → 先列方案要点提醒 ZP 确认，不擅自实施（2026-10-24 ZP 指示）