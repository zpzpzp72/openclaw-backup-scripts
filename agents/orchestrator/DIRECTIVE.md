# DIRECTIVE.md — Orchestrator

## 夜间任务
1. 收集所有子 Agent 的报告
2. 建立综合视图（trends + code + content）
3. 生成《Tomorrow Action Plan》

## ⚡ 执行效率铁律
- 能用一次 exec 完成的命令绝不分成多次；多个命令用 `&&` 合并
