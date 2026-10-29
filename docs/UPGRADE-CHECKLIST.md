# OpenClaw 升级前检查清单

> 当前版本 **2026.10.5** → 可用 **2026.10.9**(npm, channel=stable)
> 执行方式:ZP 在自己终端跑 `openclaw update`(我不代跑 system 级安装)
> 依据:`openclaw update status` + `openclaw update --dry-run`(2026-10-30 00:30 实测,dry-run 明确 "No changes were applied")

## 一、升级前必须已完成(今晚已达成)

- [x] **Git 工作区已收口并推送**:`feature/hot-backup` = 远端,落后 0/领先 0,未提交 0
- [x] **备份链健康**:心跳 `status=ok`,最新 `openclaw-20261029-0300.tgz` (6.0G),`hours_since=0`
- [x] **备份链唯一触发源**:crontab 03:00/03:30/03:40;openclaw cron 的 03:50 重复任务已 disable
- [x] **public 仓库凭据已清零**:远端完整历史 1142 对象扫描,敏感文件 0,凭据命中 0
- [x] **`.backups/` 已剔除**:434MB 数据库备份 + 含 appSecret 的配置备份均不在历史中
- [x] **安全 tag 就位**:`safety/pre-backups-purge-20261030-001127`(可回滚改写前历史)
- [x] **备份 tar 已排除** `.git` + `.backups`(每晚省 634MB)

## 二、升级前建议补做

- [ ] **NAS 回收站清理**(17 份 ≈140G,当前 Avail 仅 165G / 98%)
      → 升级过程会写临时文件,空间紧张增加失败概率。**需 ZP 二次授权**
- [ ] **provider 链定案**(B 方案 vs 现状)→ 升级会重载配置,带着已知断链升级不如先修
- [ ] **Gateway RSS 根因定位**(当前 11.54GB)→ 升级若重启 gateway 会顺带清零,但那是**掩盖**不是修复

## 三、升级前快照(便于回滚)

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak-pre-$(date +%Y%m%d-%H%M%S)
cp ~/.config/systemd/user/openclaw-gateway.service \
   ~/.config/systemd/user/openclaw-gateway.service.bak-pre-$(date +%Y%m%d-%H%M%S)
```

## 四、升级后验证(按序执行)

```bash
openclaw --version                      # 期望 2026.10.9
openclaw gateway status                 # Runtime: running + Connectivity check: ok
openclaw doctor                         # 重点看:
                                         #   - Skipped agent database path repair → openclaw doctor --fix
                                         #   - openclaw-weixin 插件加载错误
                                         #   - memory-lancedb-pro 版本未随更新
openclaw cron list                      # 24 个任务应仍在,Backup Log 应仍为已禁用
cat ~/.openclaw-backup.heartbeat         # status=ok
```

## 五、升级已知风险(来自上次升级记录 2026-10-19)

1. **插件未随更新**:`memory-lancedb-pro` 由 `plugins.load.paths` 托管,更新不覆盖 → 需人工核对版本
2. **agent 数据库路径修复被跳过** → 升级后需手动 `openclaw doctor --fix`
3. **`openclaw-weixin` 插件加载错误**(`ERR_PACKAGE_PATH_NOT_EXPORTED`)→ 升级不保证修好,需单独处理
4. **readiness 未验证**:上次出现「Gateway started but readiness was not verified」→ 升级后必须手动确认端口与连通性
5. **pacman 探测告警**:WSL 无 pacman,`[update] pacman inspection failed` 属**预期噪音**,可忽略
6. **update recovery set 残留**:上次留下 `/home/zhiping/.openclaw.update-captures/<id>/` 且状态 `stale`(内容重复导致),不影响运行

## 六、回滚

- npm 侧:`npm install -g openclaw@2026.10.5`(或 nvm 路径下对应版本)
- 配置侧:用第三节的 `.bak-pre-*` 快照覆盖回去
- Git 侧:`git reset --hard safety/pre-backups-purge-20261030-001127`(**仅在工作区异常时**)
