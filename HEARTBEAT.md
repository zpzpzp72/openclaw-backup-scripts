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
## 2026-11-03 05:40 追加（Life NightOps 失败复盘）
- NightOps 作业的 `sessionKey` 必须与 `agentId` 同域（`agent:<id>:main`），否则失败告警也无法投递（ERR-20261103-006）
- 作业级 model/fallback 覆盖优先于 agent 默认链；litellm 系 402 期间不要放在 fallback 首位（ERR-20261103-007）
- 写 workspace/heartbeat/ 的报告禁用 apply_patch（sandbox root 限制），统一 exec+heredoc / write
- 写完必 grep `arg_key|tool_call|</think>` 与 U+FFFD 校验残留
