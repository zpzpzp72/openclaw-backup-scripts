# Tomorrow Action Plan — 2026-03-27

**生成时间**: 2026-03-26 04:50 (Asia/Shanghai)  
**Orchestrator**: 📋 Workflows Engine

---

## 📊 综合视图（Agent 报告摘要）

### Scout — 研究简报
- ✅ 完成 AI Agent 框架对比分析（OpenClaw, CrewAI, AutoGPT, Qwen-Agent, LangChain.js, AutoGen）
- 📅 报告周期：2026-02-28 ~ 2026-03-21
- 🔑 发现：MCP 成为标配、工具搜索、HITL、图形化工作流、多模态为共同趋势

### Life — 内容计划
- ✅ 2026-03-27 选题计划（8 个选题，分优先级）
- 🔥 主推方向：军事科技（激光武器）、AI职业冲击（短剧演员）、中日关系（持刀闯馆）
- 📈 政策民生：长护险、短剧回收、健康科普

### Coder — 代码质量报告
- ✅ copilot_proxy 编译通过，AST 分析显示代码质量良好
- ⚠️ 发现 2 个 P1 优先级问题（startup error handling, browser retry）
- ⚠️ audit.test.ts 和 attempt.ts 持续增长需监控

---

## 🎯 明日最重要的 3 项任务（优先级排序）

### [P0] 修复 Coder 的 P1 稳定性问题
- **目标**: 提升 copilot_proxy 生产环境健壮性
- **具体行动**:
  1. 编辑 `copilot_proxy/app.py`：在 `@app.on_event("startup")` 中添加 try/except 包裹 `asyncio.create_task(agent.start())`
  2. 编辑 `copilot_proxy/browser.py`：为 `playwright.launch()` 添加重试机制（最多 3 次）
- **负责 Agent**: Coder
- **预计耗时**: 2-3 小时
- **完成标志**: 重启服务稳定运行，无 silent crash

### [P1] 提交工作区配置文件到版本控制
- **目标**: 确保 orchestration 配置不丢失
- **具体行动**:
  - 在 workspace root 执行：`git add . && git commit -m "feat: add orchestrator configuration files" && git push`
- **负责 Agent**: Orchestrator (直接执行)
- **预计耗时**: 0.5 小时
- **完成标志**: AGENTS.md, SOUL.md, DIRECTIVE.md, HEARTBEAT.md, USER.md, TOOLS.md, IDENTITY.md 已推送

### [P2] 执行 Scout 待处理任务：安装 Playwright MCP
- **目标**: 增强 Scout 浏览器自动化能力
- **具体行动**: `claude mcp add playwright npx @playwright/mcp@latest`
- **负责 Agent**: Scout
- **预计耗时**: 0.5 小时
- **完成标志**: `claude mcp list` 显示 playwright 已添加

---

## 🚧 识别出的阻碍点

### 阻塞项（需立即处理）
- **Coder**: `app.py` startup 无错误处理 → agent.start() 失败导致静默崩溃（生产风险）
- **Coder**: `browser.py` 无重试 → 偶发端口占用导致启动失败
- **Workspace**: 配置文件未 commit → 配置遗失风险

### 潜在风险
- **Coder**: `audit.test.ts` (>3892 行) 和 `attempt.ts` (>3000 行) 持续增长 → 维护负担加重，需定期 review 拆分

---

## 💡 机会点与建议

### 技术升级机会
1. **MCP 集成深化**（呼应 Scout 报告趋势）
   - 将 Playwright MCP 扩展为通用工具搜索能力
   - 评估 CrewAI `toolSearch()` 概念移植到 OpenClaw skill 加载机制的可行性
2. **浏览器自动化增强**
   - 统一错误处理模式，建立重试策略标准
   - 参考 AutoGPT 的 E2B sandbox 优化经验

### 工作流优化
1. **DX 提升**
   - 提供 `openclaw skills search <keyword>` 命令（对标 CrewAI）
   - 将 HITL (Human-in-the-Loop) 模式文档化，作为生产环境最佳实践
2. **可视化工具体验**
   - 借鉴 AutoGPT Builder 的 Graph Editor，评估 Live Canvas 增强方向

### 技术与社区
1. **文档显式化**
   - 在 OpenClaw Docs 首页强调 MCP server 兼容性
2. **社区建设**
   - 建立中文文档镜像站（响应 Qwen-Agent 的中文生态挑战）

---

## 🔄 跨 Agent 协同建议

### 今日依赖链
```
Orchestrator (commit config)
    ↓ 告知完成
Coder (修复 P1 问题)
    ↓ 测试通过
Scout (安装 Playwright MCP)
```

### 协同检查点
- **Coder 完成后**: 重启服务，验证无 crash log
- **Scout 完成后**: 测试 `@playwright/mcp` 工具调用是否正常注入
- **Orchestrator 完成后**: 提醒 Main 审核配置变更

---

## 📈 后续跟踪计划

| Agent | 关注点 | 频率 |
|-------|--------|------|
| Coder | audit.test.ts 增长速率、代码拆分 | 每日 |
| Scout | Playwright MCP 使用反馈、工具搜索需求 | 每周 |
| Life | 热点选题数据源稳定性 | 每日 |
| 所有 | P1 问题复发监控 | 每日 |

---

## ✅ 完成确认

本计划生成后，请各 Agent 在完成对应任务后：
1. Commit 代码或更新配置文件
2. 在 `shared-memory/cross-agent-log.md` 追加完成记录
3. 通过 Heartbeat 或主动告知 Orchestrator 结果

**明日晨间 Heartbeat（05:00）将检查本计划完成度。**
