# 事故:Health-Weekly-IMA-Scan 把 Windows 盘 (/mnt/c) 填到 100%

> 2026-10-30 10:07-10:20 CST · 已止损 · 严重性:高(危及宿主机)

## 发生了什么

`Health-Weekly-IMA-Scan`(每周五 10:00 的 health agent 周任务)派生的子进程执行了:

```bash
cd /mnt/c/Users && cp -r "Zhiping Wu/AppData/Local/ima.copilot/User Data" \
                    "/mnt/c/Users/Zhiping Wu/AppData/Local/ima.copilot/User Data.cdp"
```

**源和目标都在同一块 Windows 盘上** —— 这是在 `/mnt/c`(DrvFs/9p 挂载)上把 Chrome 用户数据
**自我复制成一份副本**。在 9p 挂载上小文件复制极慢,于是表现为「任务卡了 4 小时」。

进程祖先链(证明由 gateway 派生,非人工):
```
systemd --user (pid 530)
└─ node .../openclaw/dist/index.js gateway --port 18789   (pid 648941)
   └─ node .../dist/process/spawn-broker/worker.js         (pid 649053)
      └─ node .../dist/process/supervisor/service-child-group-anchor.js (pid 660462)
         └─ bash -c cd /mnt/c/Users && cp -r ...             (pid 660469)
            └─ cp -r ...                                    (pid 660470)
```

## 影响

```
/mnt/c (C:\):  总 465G
  10:07  Avail 3.1G  已用 100%
  10:12  Avail 2.1G
  10:15  Avail 1.5G   ← 最低点,仍在以 ~0.6GB/min 下降
  10:20  Avail 2.6G   ← 止损后回升并稳住
```
填满 Windows 盘会危及 **ZP 的整个宿主机**(不只是 WSL),所以按「止损优先」处理。

## 止损动作(已执行)

```bash
pkill -9 -f '^cp -r'      # 停止复制
pgrep -x cp                # 确认清空
openclaw cron disable 2bb73c4d-2959-4a14-9ba0-ebbcba9d7131   # 停掉 IMA 周任务,防重发
```
- 磁盘 Avail 回升并稳定在 **2.8G**
- 未删除任何文件;`User Data.cdp` 副本仍在(**删除需 ZP 授权**,它是纯副本非本体,可安全重建)
- 未发任何邮件(该任务第五步「发送邮件」需 ZP 批准,实际未走到)

## 根因分析

1. **payload 与实际行为脱节**:任务 payload 只有 6 步(准备→浏览器发现→读内容→生成建议→发邮件→记状态),
   **没有「复制 IMA 用户数据」这一步**。说明这是 agent 的**自主行为**,不是既定流程。
2. **agent 在环境探测时走了弯路**:发现 9222 不通后,改去复制整个 Chrome 用户数据目录
   想在本地找知识库 → 在 Windows 盘上自我复制 → 慢到看起来像卡死。
3. **缺少边界约束**:没有任何机制阻止 agent 对 `/mnt/c` 做大规模写操作。
   这正是「Chrome 扩展需手动步骤」那条 inherited rule 的同类问题:
   **涉及宿主机资源的操作必须显式授权**。

## 待 ZP 决定

| 事项 | 说明 |
|------|------|
| 删除 `User Data.cdp` 残留 | 纯副本可重建,删除能立刻回收 Windows 盘空间(需二次授权) |
| IMA 周任务是否恢复 | 需先修 payload:① 先自检 9222,不通立即退出 ② 禁止复制 /mnt/c 任何目录 |
| 给 agent 加 `/mnt/c` 写保护 | 建议在 AGENTS.md/SOUL.md 明确:未经 ZP 授权不得对宿主机盘做写/删/批量操作 |
| `/mnt/c` Avail 仅 2.8G | 即使止损后仍只有 2.8G(100% 已用),Windows 盘本身需要清理,与本任务无关 |

## 同源风险(同一根因的其他实例)

今晚已发现同类问题:
- `NightOps` orchestrator 曾整篇覆盖 `.learnings/ERRORS.md`(246 行→16 行)
- `Health-Weekly-IMA-Scan` 曾「write 成功但文件不存在」的伪成功

**共同点**:agent 自主操作共享/宿主机资源时缺少边界与校验。
建议系统性加护栏,而不是逐个修。
