# Tomorrow Action Plan — 2026-10-30（周四）

> 生成：2026-10-29 02:40 Orchestrator NightOps（cron d7773686）。报告源：Scout 10-29 01:47 ✅（heartbeat/nightly-scout-2026-10-29.md）；Coder 顺延 10-28 code_report；Life 顺延 10-26；Health/Finance 无产出。

## P0（今日 10-29 白天最高优先）
1. **M365 push 凭证（PAT/SSH）今日 10-29 截止** → ZP 白日队列最高位；凭证到位后 Coder 立即验证推送
2. **Gateway 497240 内存需重启**：RSS 10.6GB（第 5 次劣化，~73MB/h 增速；不处理预计 10-30 达 ~12.8GB）→ ZP 择机执行；Coder 在重启后 3–4h 复查 RSS/CPU
3. **会话保留清理授权**（1956 json + 605 zst）→ 连续两日未获批，ZP 拍板后由 Coder 执行，防 RSS 回升

## P1
4. **验证 10-29 08:00 news digest 推送成功**（10-28 08:00 ✅ 21,382B；再成功一次方可确认连续恢复）
5. **fallback 单点风险**：目前仅本地 ollama 可用（LiteLLM@NAS DB 挂 / OpenRouter 402 / SiliconFlow key 失效）→ ZP 决定充值或补 key，否则 NightOps 实质单点运行
6. **MiniMax 429 缓解跟踪**：84 次（昨日 259）；观察 10-29/10-30 08:00 早峰，若持续无恶化可下调「错峰迁移」优先级
7. **备份 4.1GB 体积骤减核对**（tar 清单 vs exclude 规则，疑漏 LanceDB 9.5G）+ **/mnt/h 98% 水位清理**

## P2
8. **长期停摆 Agent 处置**：Health memory 为空、Finance 最后产出 04-07、Life 缺 10-27/10-28 报告 → ZP 决策：复活 / 合并 / 关闭
9. **代码质量（Coder 10-28 报告顺延）**：删除 loader.test.ts.bak；新增 CI 测试文件行数门禁（3000L）；拆分 run-attempt.ts（5849L）
10. **copilot_proxy 分叉收敛**（本地领先 5 / origin 独有 1）→ 待 push 凭证（见 P0-1）修复后统一 push

## 阻塞（ZP 拍板项，自昨日顺延）
- MiniMax Token Plan 三选一（配额管理 / 升级 / 换源）；OpenRouter 充值；LiteLLM@NAS 恢复
- Heartbeat 8 个占位 telegram:123456789 任务改飞书；BILIBILI_COOKIES / OPENROUTER_API_KEY 补齐
- 残留 `127.0.0.1:25017` 硬编码全仓 grep 收尾

## 亮点
- 本场 NightOps 全部完成（Scout 01:47 ✅、Orch 02:40 ✅）；429 为近期最低；10-28 08:00 digest 成功推飞书
