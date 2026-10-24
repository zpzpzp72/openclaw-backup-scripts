# ERRORS / 运行备忘 — 2026-10-25 NightOps

## 本轮遇到的错误与处置

1. **exec: external sqlite3 被拒开活 DB（state 目录沙箱）**
   - 触发：`sqlite3 state/openclaw.sqlite ...` 直接查活跃 state DB
   - 处置：属工具沙箱保护，符合预期；改走 `openclaw models status` 等 CLI，或把 DB 复制到非 state 目录再读。

2. **bash: `2>/summary` → Permission denied**
   - 触发：想写 `2>/dev/null` 误写成 `2>/summary`
   - 处置：更正拼写重跑即可；报错像权限问题，实为拼写问题。

3. **read 路径手误（含一次把文件路径误拼成 URL 形状）**
   - 触发：路径拼写错误 / 不存在的文件
   - 处置：利用 read 报错自带的 "Did you mean:" 候选列表定位真实文件；candidate list 常比 find 还快。

4. **`openclaw agent exec` 参数错误**
   - 触发：`--thinking adaptive` 对 MiniMax-M2.7 不支持；`--agent` flag 不存在（agent 名是位置参数）
   - 处置：按报错提示的 `off/minimal/low/medium/high/ultra` 重试；agent 通路验证以**实际产物落地**为准更可靠。

## 通用注意
- 读文件一律走 read 工具（bash cat 会把长行连在一起，且 read 的报错有候选提示）。
- 探测 provider 状态必须用 `openclaw models status` 看 effective/cooldown，不能用配置里的占位符字面量当 key 实测。
