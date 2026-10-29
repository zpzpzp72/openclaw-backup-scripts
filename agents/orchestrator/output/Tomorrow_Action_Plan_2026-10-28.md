# Tomorrow_Action_Plan — 2026-10-28（生成 2026-10-27 02:40 Asia/Shanghai）

## 数据源（file-grounded）
- Scout 10-27（01:30+02:04）：配额墙已解（01:13-01:20 窗口 429×368，后恢复 200）；gateway PID 497240 RSS 4.29→4.57GB、CPU 212-347%；proxy 25017 ✅
- 系统 02:26 实测：RSS 6.99GB、CPU 278% → 按 0.1-0.2GB/15min 斜率，预计 03:30-04:30 触 8GB 预警线
- Life 10-26：fallback 写入中断待重写（备份 bak.scoutfb/bak.fallback-20261026-0348 已就绪）；10-26 digest 推送成功但来源收缩（webserp 0 / Tavily 兜底 / openclaw.cc RemoteDisconnected / 知乎 403）
- Coder 10-27：copilot_proxy py_compile 4 文件 OK；git 停留 2026-04-06（约 6.5 个月）；无 CI；audit.test.ts 3892 行

## P0（Main 决策）
1. 【Gateway 内存二次爬升】今晚 8GB 预警窗口前决定是否再重启；若重启后仍复现爬升 → 转 Coder 做根因改造
2. 【fallback 链重写】fallbacks=['litellm/deepseek-flash','litellm/LongCat-2.0','litellm/GLM-5.3-Flash','ollama/qwen3:4b-instruct']（主模型不动）；先 validate 后写入；Owner=Coder+Main 确认
3. 【MiniMax Token Plan】昨触顶 2056 一次、今晨又现启动窗集中 429；白天决策：升级套餐 / 夜间主模型切换 deepseek

## P1（今日推进）
4. 【Digest 源修复】webserp 0 条 + openclaw.cc RemoteDisconnected + 知乎 403 → 仅 Tavily 单点存活；Owner=Coder
5. 【M365 push 凭证】距 10-29 截止剩 2 天，配置 PAT 或 SSH remote 推 e5f498e；Owner=Main
6. 【copilot_proxy】拆分 audit.test.ts（3892 行）、清 loader.test.ts.bak；Main 决策仓库归档 or 维护模式
7. 【Cron 治理】清理 0597835a/2bb73c4d/04ebf3a5/f0214b7e(37x)；补 cron-watchdog.log；Owner=Coder

## P2（观察/例行）
8. 【Life 指令源】life/DIRECTIVE.md 注入内容运营指令 + 统一口径"cron 注入语境 ≠ 用户指令"（昨日计划已列，今日落实）
9. 【08:00 digest 监控】验证 settlement-closed 是否复发；Owner=Orch 心跳
10. 【硬编码扫描】全仓 grep `127.0.0.1:25017` 残留；Owner=Coder

## 附注
- Health 无产出、Finance 最后报告 04-07 → 维持"代理空转"观察
- 按 Token 预算跳过 IMA 三轮讨论；IMA 检索待 Scout 日间触发后按 Phase 1-5 执行
