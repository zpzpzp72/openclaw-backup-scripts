# WSL core dumps 元数据留证(实际文件已清理)
# 采集时间: 2026-10-31 18:08:39 CST
# 目录: /mnt/c/Users/Zhiping Wu/AppData/Local/Temp/wsl-crashes

  drwxrwxrwx 1 zhiping zhiping        4096 2026-10-30 04:13 .
  drwxrwxrwx 1 zhiping zhiping        4096 2026-10-31 18:08 ..
  -rwxrwxrwx 1 zhiping zhiping 22030974976 2026-10-27 01:13 wsl-crash-1793034642-319857-_home_zhiping_.nvm_versions_node_v26.10.0_bin_node-6.dmp
  -rwxrwxrwx 1 zhiping zhiping 13201776632 2026-10-30 04:16 wsl-crash-1793304806-497240-_usr_local_lib_nodejs_node-v26.10.0_bin_node-6.dmp

## 解读
- 两个均为 ELF 64-bit core file(node 进程崩溃转储),非用户数据
- 1793034642 → pid 319857 = 10-27 之前的 gateway(记录 RSS 1.29GB 时代)
- 1793304806 → pid 497240 = 2026-10-30 白天那个 gateway(RSS 峰值 13.7GB 时代)
- core dump 大小与进程 RSS 同量级,侧面印证了 RSS 膨胀的严重程度
- 两个 pid 均已退出,当前 gateway pid 648941 存活,dump 对当前问题无调试价值
