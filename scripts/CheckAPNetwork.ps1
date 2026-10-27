param()
[Console]::OutputEncoding=[Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

$MainProcess    = "ap_network"
$ServiceProcess = "APNetworkService"
$AppPath        = "D:\APNetwork\ap_network.exe"
$LogFile        = "D:\APNetwork\APNetworkMonitor.log"
$StateFile     = "C:\Scripts\logs\apnetwork-failcount.txt"
$CooldownFile  = "C:\Scripts\logs\apnetwork-restart-cooldown.txt"
$TimeoutSeconds = 12
$FailThreshold  = 3
$CooldownHours  = 6

$TestUrls = @(
  "https://www.baidu.com",
  "https://www.aliyun.com",
  "https://cp.cloudflare.com/generate_204",
  "https://www.google.com/generate_204"
)

function Write-Log($msg) {
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  Add-Content -Path $LogFile -Value "$ts  $msg"
}

function Test-Internet {
  foreach ($u in $TestUrls) {
    try {
      Invoke-WebRequest -Uri $u -TimeoutSec $TimeoutSeconds -UseBasicParsing -MaximumRedirection 3 | Out-Null
      return @{ ok = $true; url = $u }
    } catch {
      Write-Log ("  probe failed: " + $u)
    }
  }
  return @{ ok = $false; url = "" }
}

function Read-Int($path, $def) {
  if (Test-Path $path) {
    $v = (Get-Content $path -Raw).Trim()
    if ($v -match "^\d+$") { return [int]$v }
  }
  return $def
}

$null = New-Item -ItemType Directory -Force -Path "C:\Scripts\logs"
$now = Get-Date

# >>> openclaw-net-harden-hook >>>
# 本任务以 RunLevel=Highest 运行, 可执行需要管理员权限的命令.
# NetRepair -OnlyIfBroken: 隧道坏时才修, 好了就跳过 (自愈, 幂等).
try {
  & "C:\Scripts\NetRepair.ps1" -OnlyIfBroken *>&1 | Out-File -FilePath "C:\Scripts\logs\net-repair.log" -Encoding utf8
} catch {
  Add-Content -Path "D:\APNetwork\APNetworkMonitor.log" -Value ("net repair failed: " + $_.Exception.Message)
}
# 一次性加固 (标记文件保证只跑一次; -SkipNicRestart 避免再次打断隧道)
$HardenMarker = "C:\Scripts\logs\net-harden.done"
$HardenLog    = "C:\Scripts\logs\net-harden.log"
if (-not (Test-Path $HardenMarker)) {
    try {
        & "C:\Scripts\NetHarden.ps1" -Apply -SkipNicRestart *>&1 | Out-File -FilePath $HardenLog -Encoding utf8
        New-Item -ItemType File -Path $HardenMarker -Force | Out-Null
    } catch {
        Add-Content -Path "D:\APNetwork\APNetworkMonitor.log" -Value ("network harden hook failed: " + $_.Exception.Message)
    }
}
# <<< openclaw-net-harden-hook <<<

# ---- 快速路径: 客户端进程不存在 -> 直接拉起 ----
$proc = Get-Process -Name $MainProcess -ErrorAction SilentlyContinue
if (-not $proc) {
  Write-Log "客户端进程不存在, 直接启动 APNetwork (快速恢复)。"
  if (Test-Path $AppPath) {
    Start-Process $AppPath
    Write-Log "APNetwork 已启动, 等待 45 秒后复测。"
    Start-Sleep -Seconds 45
    $r = Test-Internet
    if ($r.ok) {
      Write-Log ("启动后外网正常 (" + $r.url + ")。")
      Set-Content -Path $StateFile -Value "0"
    } else { Write-Log "启动后外网仍不可用。" }
  } else { Write-Log ("错误：找不到程序路径：" + $AppPath) }
  exit 0
}

# ---- 进程在跑: 探测 ----
$r = Test-Internet
if ($r.ok) {
  Set-Content -Path $StateFile -Value "0"
  exit 0
}

$fail = Read-Int $StateFile 0
$fail = $fail + 1
Set-Content -Path $StateFile -Value "$fail"
Write-Log ("外网探测失败 (累计 " + $fail + "/" + $FailThreshold + "), 本次目标均不可达")

if ($fail -lt $FailThreshold) {
  Write-Log "未达重启阈值, 保留当前客户端 (避免重启风暴)。"
  exit 0
}

if (Test-Path $CooldownFile) {
  $last = (Get-Content $CooldownFile -Raw).Trim()
  try {
    $lastDt = [datetime]::Parse($last)
    $elapsed = ($now - $lastDt).TotalHours
    if ($elapsed -lt $CooldownHours) {
      Write-Log ("处于重启冷却期 (" + [int]$elapsed + "h < " + $CooldownHours + "h), 跳过重启。")
      exit 0
    }
  } catch { }
}

Set-Content -Path $StateFile -Value "0"
Set-Content -Path $CooldownFile -Value $now.ToString("yyyy-MM-dd HH:mm:ss")
Write-Log ("连续失败达阈值, 准备重启 APNetwork (之后 " + $CooldownHours + "h 内不再重启)。")
foreach ($p in @($MainProcess, $ServiceProcess)) {
  $po = Get-Process -Name $p -ErrorAction SilentlyContinue
  if ($po) {
    Write-Log ("终止进程：" + $p)
    Stop-Process -Name $p -Force -ErrorAction SilentlyContinue
  }
}
Start-Sleep -Seconds 3
if (Test-Path $AppPath) {
  Start-Process $AppPath
  Write-Log "APNetwork 已重新启动。"
}
Start-Sleep -Seconds 45
$r2 = Test-Internet
if ($r2.ok) {
  Write-Log ("重启后外网已恢复正常 (" + $r2.url + ")。")
} else {
  Write-Log "重启后外网仍不可用, 等待下一个检查周期。"
}
exit 0