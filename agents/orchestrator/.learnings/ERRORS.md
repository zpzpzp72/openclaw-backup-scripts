# Errors

Append structured entries:
- ERR-YYYYMMDD-XXX for command/tool/integration failures
- Include symptom, context, probable cause, and prevention

## ERR-20260724-001: System falsely flags ls metadata as error + premature NightOps check
- **Symptom**: Multiple error signals `[exec] ls: cannot access '[REDACTED]': No such file or directory` — not real errors; also (Command exited with code 2) when checking next-day-brief-07-24
- **Context**: 03:30 AM heartbeat, checking for next-day-brief-07-24 before NightOps scheduled time (04:50)
- **Probable cause**: 
  1. System falsely flags `ls` metadata header lines as errors (same pattern as ERR-20260722-003, ERR-20260723-001/003/005)
  2. next-day-brief-07-24, coder-review-07-24, content_plan don't exist yet because NightOps hasn't run (we're at 03:30 AM, scheduled for 04:50)
- **Prevention**: Only check for next-day outputs after the scheduled NightOps time (04:50); before that, files won't exist yet
- **Resolution**: This is a system false positive + premature check; no action needed. Will recheck at/after 04:50 NightOps

## ERR-20260724-002: System ENOENT false positive - Scout/Life workspace missing
- **Symptom**: Error signal `[read] ENOENT: no such file or directory, access '[REDACTED]'` — not a real error
- **Context**: 06:00 AM heartbeat, system detected ENOENT when reading Scout/Life workspace files
- **Probable cause**: Scout/Life/Health Agent workspace directories genuinely don't exist in `workspace/agents/` — this was already confirmed at 03:01 AM and documented in Phase 1 at 05:30 AM
- **Prevention**: This is a system false positive that matches a real situation (workspace missing); already documented in memory/2026-07-24.md and pushed to Main at 05:30
- **Resolution**: Already handled — P0 pushed to Main at 05:30; no new action needed

## ERR-20260724-003: Recurring system false positive exec metadata error (7th occurrence)
- **Symptom**: Error signal `[exec] -rw-r--r-- 1 zhiping zhiping 850 Jul 24 04:41 [REDACTED]` — not a real error
- **Context**: 07:00 AM heartbeat (system timestamp: 7:00 AM, heartbeat header showed 6:30 AM stale)
- **Probable cause**: System falsely flags `ls -lt` metadata header line as error; path redacted by system; actual data is legitimate file timestamp showing Coder code_report (Jul24 04:41) — unchanged since 05:30 check
- **Prevention**: This is a system false positive; confirmed at 06:30 and 07:00 checks that Coder code_report (Jul24 04:41) is unchanged
- **Resolution**: No action needed; data confirmed unchanged at 06:30

## ERR-20260724-004: System false positive exec metadata error (8th occurrence)
- **Symptom**: Error signal `[exec] -rw-r--r-- 1 zhiping zhiping 850 Jul 24 04:41 [REDACTED]` — not a real error
- **Context**: 19:00 heartbeat check
- **Probable cause**: System falsely flags `ls -lt` metadata header line as error; path redacted by system; actual data is legitimate file timestamp showing Coder code_report (Jul24 04:41) — unchanged since 05:30
- **Prevention**: Pattern matches ERR-20260721-001, ERR-20260722-001/002/003/004, ERR-20260723-001/003/005, ERR-20260724-003 — system-level false positive
- **Resolution**: No action needed; data confirmed unchanged

## ERR-20260725-001: sed delimiter conflict with forward slashes in replacement string
- **Symptom**: `sed: -e expression #1, char 192: unknown option to 's'`
- **Context**: 01:30 heartbeat, updating HEARTBEAT.md Phase 2 trackers with Scout/Life workspace rebuild
- **Root cause**: First sed attempt used `/` as delimiter, but replacement string contained `/` (in URLs/paths like `Scout/Life/Health`), causing sed to misinterpret the command
- **Fix**: Retried with `|` as delimiter instead — succeeded (`Done`)
- **Prevention**: When replacing text containing `/`, use `|` or `#` or `@` as sed delimiter instead of `/`
- **Resolution**: Already handled — retried with `|` delimiter, update succeeded

## ERR-20260725-002: awk command accidentally replaced entire file instead of single line
- **Symptom**: `awk 'NR==50 {print "*Next heartbeat: 2026-07-26 04:50 AM (NightOps)"}' file > tmp && mv tmp file` replaced entire HEARTBEAT.md with only line 50
- **Context**: 05:05 heartbeat, trying to update "Next heartbeat" line in HEARTBEAT.md
- **Root cause**: awk output redirection replaced the file before awk started, resulting in an empty file being moved into place
- **Fix**: Restored HEARTBEAT.md from scratch by rewriting the entire file
- **Prevention**: Use `sed -i` or `head/tail` with proper line selection, or use a temp file with a different name than the target
- **Resolution**: HEARTBEAT.md fully restored with all Phase 2 tracker data intact

## ERR-20260726-001: sed delimiter conflict with newlines in replacement string
- **Symptom**: `sed: -e expression #1, char 130: unknown option to 's'`
- **Context**: 05:03 heartbeat, updating HEARTBEAT.md Next heartbeat and Last updated lines
- **Root cause**: Replacement string contained newline character `\n` and the pattern also contained `/` (in "NightOps 第15夜完成"), causing sed to misinterpret after the first `/` delimiter
- **Fix**: Switched to `#` as delimiter (`sed -i 's#pattern#replacement#'`) — succeeded
- **Prevention**: When replacement contains `/` and newlines, always use alternate delimiter (`#`, `|`, `@`)
- **Resolution**: Update succeeded using `#` delimiter

## ERR-20260726-001: sed "Invalid preceding regular expression" - backslash in replacement
- **Symptom**: `sed: -e expression #1, char 229: Invalid preceding regular expression`
- **Context**: 06:30 heartbeat, updating HEARTBEAT.md Kimi K3 tracker from "2d倒计时" to "1d+" in Phase 2
- **Root cause**: The replacement string contained `\*\*` (escaped asterisks) which confused sed's regex engine — the double asterisk `**` is not a valid regex quantifier without preceding token
- **Fix**: Removed escaped asterisks, used plain `**` in replacement string — succeeded
- **Prevention**: Don't escape asterisks that aren't regex quantifiers; plain text replacements don't need escaping
- **Resolution**: Phase 2 tracker updated to "1d+🔴 P0（07-27凌晨发布窗口）"

## 2026-09-03 sessions_send Agent-to-Agent Blocked
**Error**: `sessions_send` to `agent:main:main` → `forbidden: Agent-to-agent messaging is disabled. Set tools.agentToAgent.enabled=true to allow cross-agent sends.`
**Impact**: 无法主动推送 P0 警报给 Main（NighOps-Orchestrator streak recovery、Main NightOps 3x consecutive error）
**Workaround**: 记录到 memory log，等待 Main 主动联系
**Config**: `tools.agentToAgent.enabled` 需设为 `true` 才能跨 agent 发送
