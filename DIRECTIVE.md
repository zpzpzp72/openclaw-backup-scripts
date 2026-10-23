# OpenClaw Main Session Directive
- Owner: gateway-owner (human, verified)
- Runtime: Asia/Shanghai
- NightOps window: Mon-Fri 00:30-03:00 CST  ← 2026-10-24 改（避开 MiniMax Token Plan burst 耗尽窗口 02:00-05:00）
- Backup cron: 03:00 daily, target /mnt/h/AI/openclaw.zone/WSL/
- Heartbeat delivery: 飞书 (chat_id oc_f54afb4bc6f317bdae35af63d2a48926)
- 8 Agent: main / orchestrator / scout / coder / life / finance / health / work
- Inherited rules (from lancedb-pro): #1 服务状态表, #3 可视指示符, #5 NightOps 窗口
- Fallback chain (2026-10-24 收敛): ollama/qwen3:4b-instruct → ollama/qwen3.6:27b → minimax/MiniMax-M2.7
- 已知死链 provider (勿放 fallback): litellm@NAS(no_db_connection) / longcat(无key) / siliconflow(key失效) / openrouter(余额0)