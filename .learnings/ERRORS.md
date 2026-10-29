# ERRORS / 运行备忘

## 2026-10-30 01:06 write 工具“伪成功”问题（首次遇到）

**触发**：`write` 工具对 `heartbeat/nightly-scout-2026-10-30.md` 返回 "Successfully wrote 13317 bytes"，但随后 `ls` 显示 `No such file or directory`，文件实际不存在；同场另一文件 `memory/nightly-scout-2026-10-30.md` 则正常落盘（17096 字节），说明不是全局故障，且与写入内容/长度无关（13KB 不算大）。

**处置**：
1. 对重要产出文件，write 后必须用 `ls -la`/`wc -c` 验证真实存在与字节数，不能只信工具返回的成功消息。
2. 发现伪成功时直接重新 write 同一路径，本场重写即成功（13317 字节落盘）。

**教训**：
- write 的成功返回与磁盘真实状态可能不一致，产出文件一律事后校验（ls/wc），重要文件写入后验证应成为固定收尾步骤。
- 同一目录下并发/相继 write 两个文件时，验证应逐个进行，避免只验了一个就默认另一个也成功。

---
- [2026-10-30 02:45][Orch] NightOps cron 会话收到 <error-detected> 假阳性：引用 exec 标准输出片段(nightly-scout 内容)，当日两次 exec 实际均成功退出；判为调度层误报，仅记录，若同模式再现再深查。
