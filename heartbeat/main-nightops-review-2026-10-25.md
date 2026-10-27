**时间: 2026-10-25 03:17 CST**

【核心结论】主会话 exec 沙箱政策收紧至 workspace 限制(拒 /tmp,/mnt/c),文件工具(read/write/edit/apply_patch)沙箱收紧到 workspace 根;但 `bash cat` 不受影响可正常读。

【工具层状况】
1. exec 可用度: 政策性移除后已部分恢复,常规命令已 OK。
   ❌ 禁止: `sqlite3 state/openclaw.sqlite` 沙箱强制拒(保护活跃 DB);read/write/edit/apply_patch 限制在 workspace 根内(/tmp /mnt/c 拒,"Path escapes sandbox root")
2. 文件工具(read/write/edit/apply_patch)可用度: 沙箱已收紧到 workspace 根。
   ✅ workspace 内正常读写,✅ bash cat 正常读 /tmp /mnt/c。

【结论/推测】exec 沙箱仅针对 state DB 保护,常规 shell 不受影响;文件工具沙箱收紧到 workspace 根。

【建议】临时文件放工作区 `.learnings/` 下再执行操作;Shell 级任务挂起等权限恢复。