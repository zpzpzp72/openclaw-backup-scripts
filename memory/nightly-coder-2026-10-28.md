# Coder 夜检要点 — 2026-10-28

- GitHub CI：17 仓库中仅 fork `zpzpzp72/openclaw` 有工作流；CodeQL 质量/安全 ✅ 通过，Install Smoke / Live-E2E / PR Sweeper ❌ 于 09-21~09-22 失败后无新触发（仓库低活跃）。openclaw-backup / openclaw-backup-scripts 无 CI。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- OpenClaw 版本：本地 2026.10.5 < npm latest 2026.10.8，可升级（⚠️ 中低风险，建议维护窗口执行，需 owner 授权）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 依赖：当晚无新 npm 安装 → 未触发安全审计条件；`openclaw-zero-token/` vendored package.json 停在 2026.3.28 陈旧 7 个月，待清理。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 代码变化：952e5a12 记忆纪要 v28（+150）、f169a9ed scout 夜间研究 + graphify 产物（约 1.5 万行）、24b74a5f 备份三根因 learnings。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 系统观察：Gateway PID 497240 与 heartbeat-state 一致 ✅；/mnt/h NAS 98% 满 ⚠️；/mnt/m 路径已消失但状态文件仍记录 97% → heartbeat-state 中 mnt_m 条目陈旧，待修正。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
