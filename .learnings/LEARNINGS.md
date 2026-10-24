# Learnings

Append structured entries:
- LRN-YYYYMMDD-XXX for corrections / best practices / knowledge gaps
- Include summary, details, suggested action, metadata, and status

## 2026-08-26 — Inherited from memory-lancedb-pro

### NightOps Protocol
1. Check NightOps window (Mon-Fri 21:30-23:30) before action on heartbeat polls
2. Report system inspection with service status table
3. Run security audit after installing npm packages
4. Never install Chrome extension without informing user of manual steps
5. Report health as table with ✅/❌/⚠️


## 2026-10-03 — OpenClaw 2026.9.5 → 2026.9.7 升级

### 摘要
| 项 | 详情 |
|---|---|
| 升级类型 | patch 级（2 个 patch：9.5 → 9.7） |
| 安装点 | NVM (`/home/zhiping/.nvm/versions/node/v26.10.0/lib/node_modules/openclaw`) |
| 用时 | ~10 分钟（含 dry-start）|
| 结果 | ✅ 成功，零 schema 问题 |
| 内存上限 | 4096 MiB（保留下调，便于观察泄漏）|

### 关键经验教训

**1. 必须先 `grep ExecStart` 看准安装点**
- CLI (`openclaw --version`) 跟 gateway 实际跑的可能不是同一个安装点
- 这台机器：CLI 在 npm-global，gateway 在 NVM
- 升级前不查就会装错位置

**2. 4 个必加的保护（核心）**
- `Restart=no` override（drop-in 文件）—— 避免 drain 超时后无限重启循环
- `OOMScoreAdjust=-1000` override —— 保护升级期间执行的所有 exec 命令不被 OOM killer 杀
- `--max-old-space-size=4096`（从 8192 降下来）—— 让 V8 GC 更早触发，泄漏提前暴露
- **手动 dry-start（Step 5）** —— 不接 systemd，先确认能起来，避免新版本启动失败 → 系统失联

**3. `systemctl --user`（不带 sudo）才能用**
- WSL2 下 `sudo systemctl --user` → "Failed to connect to bus: No medium found"
- sudo 不传 DBus session

**4. `openclaw backup create` 在不稳定 gateway 下会 hang**
- 用 `cp -a` 快照代替（更完整，能抓到所有状态文件）
- 或者等 gateway 完全稳定再做

**5. `cp -a` 大目录（>10G）必须在后台跑**
- `exec` 默认 timeout 5 分钟不够用
- 必须用 `setsid cp -a ... </dev/null >log 2>&1 & disown` 完全脱离
- 否则 exec 超时会 SIGKILL cp，留下半截快照

**6. doctor 输出的关键判断点**
- ✅ 没有 `schema version mismatch` / `Cannot find package` / `upgrade.*fail` = 升级成功
- ✅ `agent database integrity gate` 通过 = state SQLite 没坏
- ⚠️ 其他 warning（github plugin、device-pair、command owner 等）都是预存的，跟升级无关

**7. 升级后必须做的事（按顺序）**
1. `systemctl --user start openclaw-watchdog`（常被忘记！）
2. `openclaw doctor` 验证
3. 留一个 post-upgrade 快照作为新安全网
4. 更新 MEMORY.md（版本号 + 时间戳）
5. 删掉升级前的快照（确认稳定后）

### 元数据
- 日期：2026-10-03
- 升级路径：2026.9.5 (ec9c1a1) → 2026.9.7 (c074824)
- 负责人：main session + 用户手动执行
- 状态：✅ 完成，无后续问题

## 2026-10-04 18:07 — OpenClaw Control UI 注入的 SW 缓存陷阱

**现象**: 把新 `<script src="...">` 注入 `dist/control-ui/index.html`、Gateway `/restart` 后，浏览器**仍看不到**新脚本——磁盘和 `curl` 都验证了 served HTML 含 loader。根因是 `dist/control-ui/sw.js` 把 `'./'` 写进 `PRECACHE_URLS`，cache key 是「完整 URL（含 query）」，它会一直命中旧 `index.html`，根本不重新走网络。

**修复**: 给新加的 `<script src>` 加 `?v=<version>` 后缀，让 SW 视为新 key、走网络回源。同一技巧也适用于用户报告"我刷新了还是老版本"——优先确认是 SW cache（用 `chrome://serviceworker-internals` / DevTools Application 看 active worker 的 cache 名）。

**经验**:
- OpenClaw Control UI 的 `sw.js` cache 名 = `openclaw-control-<EMBEDDED_CACHE_VERSION>`，改 `sw.js` 里的版本字符串也能强制清缓存（更彻底但侵入更大）
- 改 query string 是更小侵入的"镜像绕过"，适合补丁级（mic 按钮、CSS 调整、图标替换）
- 升级时 OpenClaw 自己也会发 cache bust，bundles 插件升级的 `?v=...` 戳就是这套机制

## 2026-10-04 18:16 — OpenClaw chat-input 用了 closed shadow root，v1 的 textarea 查找策略失败

**现象**: 把 `<script type="module" src="…mic-button.js?v=…">` 注入 `dist/control-ui/index.html`、Gateway `/restart` 后，curl 看到 served HTML 含 loader，HTTP 200；浏览器硬刷新后**仍然看不到按钮**。调试路径：用户在 Control UI 内嵌视图里，没有 DevTools，无法直接确认 DOM 状态。

**根因**: v1 脚本在 init() 之后调 `updatePosition()`，**找不到 textarea 就 `display: none` 按钮**。它只查 `Array.from(document.querySelectorAll("*"))` 里 `el.shadowRoot` 开放的元素。但 OpenClaw 的 `<chat-input>` Lit 组件用 `attachShadow({ mode: "closed" })`，对 closed root `el.shadowRoot === null`，`textarea` 在里面、`document.querySelector("textarea")` 也拿不到。结果：DOM 里有按钮，但 `display: none` 一辈子，视觉上看不见。

**修复 (v2)**:
1. 按钮默认 `display: block`，**永远可见**；不被 textarea 查找结果影响
3. textarea 查找 4 级 fallback：open shadow root → plain `<textarea>` → `[contenteditable]` → 同源 iframe contentDocument
4. 加 console banner：`[openclaw-mic] ready lang=zh sr=…` 方便无 DevTools 用户自查脚本是否跑

**经验**:
- 给第三方 SPA 注入 UI 组件，**永远不要把可见性绑到"我找到了某个子组件"上**——closed shadow root、iframe、延迟挂载、CSP 沙箱都让查找失败；先让按钮"看起来对"，再让行为"连得上"
- `display:none` 是诊断杀手：DOM 在但视觉不在，没有 DevTools 时无法验证其"布局了什么"
- 注入的脚本必须自带 console banner，让用户能"在没 DevTools 的情况下"确认它运行了
- Position `bottom: 88px` 比 `bottom: 56px` 更安全——避开常见的 send/attachment toolbar

## 2026-10-04 18:30 — OpenClaw chat-input 元素定位策略（v3）

**v2 设计教训**: 把按钮位置写死成 `bottom: 88px` 是错的——OpenClaw Control UI 的底部 toolbar 实际位置在 viewport 底部 0–40px 之间，88px 让按钮"飘"在 toolbar 上方、与输入框之间留出明显空隙，视觉上不属于输入框。

**v3 修复策略**:
- 优先找 `<chat-input>` host 元素（`document.querySelector('chat-input')`），用 `getBoundingClientRect()` 拿到真实位置，按钮放在 host 矩形**右下角内侧 14px**——视觉上明显属于输入框
- 找不到 host 时退化到 viewport 右下角 14px / 80px（send 按钮的左侧）
- 始终 `display: block`，不被任何查找结果影响（v2 lesson 已记）

**Edit surface 5-step ladder**:
1. `<chat-input>.shadowRoot.querySelector('textarea, [contenteditable]')` — Lit 默认 open shadow
2. 遍历所有 open shadow root 找 textarea / contenteditable
3. document light DOM 的 textarea / contenteditable
4. activeElement 链上溯 8 层（含 shadow host）
5. 同源 iframe contentDocument
**完全失败** 时，文本进 clipboard + 弹 toast"已复制，请粘贴"——保证语音结果不丢

**Click feedback**: mousedown 时 `scale(0.95)`，click 后 `scale(1.08)` 闪 200ms，无 SR 环境下也能确认点击已注册。

**经验**:
- 注入 UI 元素的位置**永远不要写死 px**，优先锚到主机元素真实 rect，再退化
- `getBoundingClientRect()` 在 closed shadow root 也返回宿主元素位置（host 元素本身不在 shadow 里）
- 5-step fallback 对 void→closed 没用，但 clipboard + toast 兜底让用户至少能拿回语音文本

## 2026-10-04 18:48 — 不要修改 dist/control-ui/，用 Userscript

**现象**: 2026-10-04 14:15-18:33 这段时间尝试给 OpenClaw Control UI 加麦克风按钮，方法是把脚本 + loader tag 直接写到 `dist/control-ui/index.html` 和新建 `dist/control-ui/openclaw-mic-button.js`。结果：
- 改了 5 次（v1/v2/v3/r1/r2/r3），每次都要 Gateway `/restart`
- 用户的反馈："这只是改 UI，不需要重启 gateway 啊"
- Gateway 重启在 OpenClaw 2026.9.8 是有 drain + retention 开销的（`createControlUiRootLifecycle` 在 boot 时把 `index.html` 读进 `state.cached`）
- 任何 1 像素 CSS 调整、1 个 query 参数变化都要重启

**修复**: 把脚本从 `dist/control-ui/` 全部撤回（已经在 2026-10-04 18:48 完成，disk == orig sha `7422b6b1...`），改成 **Tampermonkey userscript** 放在 `~/.openclaw/workspace/userscripts/openclaw-mic.user.js`。

**优点**:
1. **零重启**: 以后任何 UI 调整都改 userscript 文件，Tampermonkey 自动检测 `// @version` 变化并热更新（< 24h 或手动 Update）
2. **不污染 NVM 安装**: `dist/control-ui/` 保持原样，`npm update` 不会覆盖
3. **可移植**: userscript 文件独立，跟 OpenClaw 版本解耦
4. **可审查**: 100% 客户端 JS

**安装**:
1. Tampermonkey 扩展 (Chrome / Edge / Firefox / Safari 都支持)
2. 安装 `~/.openclaw/workspace/userscripts/openclaw-mic.user.js`
3. 重载 Control UI 标签页

**经验**:
- 给 OpenClaw Control UI 加自定义 UI，**优先用 userscript**，不要碰 `dist/control-ui/`
- Gateway 重启的成本不只是用户操作时间，还有 drain/retention 期间的 worker loop 重启（最近一次看到 5 个 supervisor 子进程在 5 秒内重启）
- 只有在以下情况才考虑直接修改 `dist/control-ui/`：
  - 用户明确要求永久打包进 OpenClaw
  - 没有浏览器扩展权限（嵌入式 webview 等）
  - 改的是 `sw.js` 缓存策略本身

## LRN-20261024-001 — 「飞书通道报错」实为模型层 thinking 载荷不兼容（2026-10-24 21:54-22:10）

### 摘要
| 项 | 详情 |
|---|---|
| 类型 | 误判纠正 + 工具坑 |
| 触发 | 飞书群会话每轮 400 (2013) `requires adaptive thinking` |
| 真因 | `agents.defaults.thinkingDefault="off"` + MiniMax M3 系列强制 `thinking.type=adaptive` |
| 修复 | `agents.defaults.models` 给 M3/M3.1-Flash 加 `params.thinking="adaptive"` |
| 状态 | ✅ 已修复并热载（网关 revision 8）|

### 详情

**1. 报错归属要看 rawError，不要看 provider 名字。**
日志里 `LLM request rejected: invalid params, model "MiniMax-M3.1-Flash" requires adaptive thinking` 出现在飞书会话下，一度被当成飞书侧故障。实际链路：OpenClaw 运行时 `createMinimaxThinkingDisabledWrapper`（dist/proxy-*.mjs）在 `thinkingLevel === "off"` 分支**不覆盖** `thinking`，把 `thinking:{type:"disabled"}` 原样发给服务端；MiniMax M3/M3.1-Flash 服务端强制 adaptive → 400。

**2. `configured fallbacks disabled by user model override` 是关键线索。**
会话级 `modelOverride`（session_nodes.entry_json）会屏蔽配置里的 fallback 链 → 一旦 primary 坏掉就没有兜底，看起来像「全盘皆黑」。排查 fallback 相关故障先查 modelOverride。

**3. 改 primary/fallback 链时必须连带验证 thinking 兼容性。**
当天把 6 个 agent 的 primary 和 9 处 fallback 首位都换成 M3.1-Flash，与既存的 `thinkingDefault=off` 组合直接踩雷。模型可用性 = 路由可达 × 载荷兼容 × 配额未耗尽，三者要一起验。

**4. 工具坑**
- `openclaw agent exec` 的 message 是**位置参数**；`--message` 属于 `openclaw agent`。
- `openclaw agent --session-key ...` 会报 `Gateway agent from agent exec would lose inter-session attribution` — 这是 CLI 归因保护，**不是模型错误**，别误判成修复失败。
- `openclaw agent exec` 单次 30-90s；放后台会被 exec 会话回收，必须前台串行跑。
- 长探测脚本写成 `/tmp/x.py` 再执行，别用长 heredoc（引号/中文混排易炸）。
- `openclaw models status --json` 的 `missingProvidersInUse:["minimax"]` 是**冷却标记**不是缺 key，别去改凭据。

### 建议动作
1. 新增或升级模型后，跑一遍 `openclaw agent exec --json --model <model> "..."` 做真实载荷验证（不靠 `models list` 的显示状态）。
2. 若某 provider 模型强制 thinking，与全局 `thinkingDefault` 冲突时，优先用 per-model `params.thinking` 覆盖，不动全局。
3. 会话级 modelOverride 是「隐形开关」，每次改 fallback 链后检查目标会话有没有 override。

### 元数据
- 状态: ✅ 已应用
- 关联: `memory/2026-10-24.md` (MINIMAX-THINKING-FIX-20261024), MEMORY.md P0 条目
<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

