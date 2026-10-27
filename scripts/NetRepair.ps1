param([switch]$OnlyIfBroken)
[Console]::OutputEncoding=[Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"
function Say($m){ Write-Host $m }

# ---- 自愈判断: 隧道健康就什么都不做 ----
if ($OnlyIfBroken) {
  $adapter = Get-NetAdapter -Name "APNetwork" -ErrorAction SilentlyContinue
  $adapterUp = ($adapter -ne $null -and $adapter.Status -eq "Up")
  $probeOK = $false
  try {
    Invoke-WebRequest -Uri "https://www.google.com/generate_204" -TimeoutSec 10 -UseBasicParsing | Out-Null
    $probeOK = $true
  } catch { }
  if ($adapterUp -and $probeOK) {
    Say "  tunnel healthy (adapter Up + google 204 OK), skip repair"
    exit 0
  }
  Say ("  tunnel broken (adapterUp=" + $adapterUp + ", probeOK=" + $probeOK + "), repairing...")
}

Say "===== NetRepair ====="

Say "1) remove BlockInbound-* firewall rules"
foreach ($n in @("BlockInbound-APNetwork","BlockInbound-vEthernet (WSL (Hyper-V firewall))","BlockInbound-vEthernet (Default Switch)")) {
  $r = Get-NetFirewallRule -DisplayName $n -ErrorAction SilentlyContinue
  if ($r) { Remove-NetFirewallRule -DisplayName $n -ErrorAction SilentlyContinue; Say ("  removed: " + $n) }
}

Say "2) kill stale ap_network"
$p = Get-Process -Name "ap_network" -ErrorAction SilentlyContinue
if ($p) {
  foreach ($x in $p) { Say ("  kill pid " + $x.Id + " (started " + $x.StartTime + ")") }
  Stop-Process -Name "ap_network" -Force -ErrorAction SilentlyContinue
} else { Say "  (not running)" }
Start-Sleep -Seconds 5

Say "3) start ap_network (recreates TUN adapter)"
if (Test-Path "D:\APNetwork\ap_network.exe") {
  Start-Process "D:\APNetwork\ap_network.exe"
  Say "  started"
} else { Say "  ERROR: ap_network.exe not found" }
Start-Sleep -Seconds 50

Say "4) status"
Get-Process -Name "ap_network" -ErrorAction SilentlyContinue | Select-Object Id,StartTime | Format-Table -AutoSize | Out-String -Width 100
Get-NetAdapter -Name "APNetwork" -ErrorAction SilentlyContinue | Select-Object Name,Status,LinkSpeed | Format-Table -AutoSize | Out-String -Width 100
foreach ($u in @("https://www.baidu.com","https://www.google.com/generate_204")) {
  try {
    $r = Invoke-WebRequest -Uri $u -TimeoutSec 12 -UseBasicParsing
    Say ("  probe OK: " + $u + " -> " + $r.StatusCode)
  } catch {
    Say ("  probe FAIL: " + $u)
  }
}
Say "===== NetRepair DONE ====="