param(
  [switch]$Apply,
  [switch]$JumboFrame,
  [switch]$BlockVirtual,
  [switch]$BlockTunnel,
  [switch]$EnableDoH,
  [switch]$SkipNicRestart
)
[Console]::OutputEncoding=[Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"
function Say($m){ Write-Host $m }
function Rule($t){ Say ""; Say "########## $t ##########" }

if (-not $Apply) {
  Say "===== PREVIEW (add -Apply to execute) ====="
  Say "1) disable NIC power-saving props (Gigabit Lite / Power Saving Mode)"
  Say "2) report EEE / JumboFrame current values"
  Say "3) disable SMB / NetBIOS firewall rules (invariant group @FirewallAPI.dll,-28502)"
  Say "4) block INBOUND on virtual NICs: OFF by default"
  Say "   reason: blocking inbound on the APNetwork TUN interface can break the tunnel;"
  Say "   inbound on vEthernet(WSL) breaks WSL->Windows calls (incl. this tooling)."
  Say "   enable with -BlockTunnel / -BlockVirtual only if you accept the risk."
  if ($EnableDoH) { Say "5) DoH for 223.5.5.5 (opt-in)" } else { Say "5) DoH: skipped" }
  if ($JumboFrame) { Say "6) JumboFrame -> 9014 (explicit)" } else { Say "6) JumboFrame: skipped" }
  Say "NOTE: NIC restart drops the APNetwork TUN adapter; NetRepair.ps1 rebuilds it."
  exit 0
}

Say "===== APPLY ====="
$nic = "以太网"
$targets = @("环保节能","Gigabit Lite","Power Saving Mode","节能以太网路","节能乙太网路")

Rule "1 disable NIC power saving"
$n = 0
foreach ($p in Get-NetAdapterAdvancedProperty -Name $nic -ErrorAction SilentlyContinue) {
  if ($targets -contains $p.DisplayName -and $p.RegistryValue -ne "0") {
    try {
      Set-NetAdapterAdvancedProperty -Name $nic -DisplayName $p.DisplayName -RegistryValue 0 -NoRestart -ErrorAction Stop
      Say ("  {0}: {1} -> 0" -f $p.DisplayName, $p.DisplayValue); $n++
    } catch { Say ("  {0}: FAILED" -f $p.DisplayName) }
  }
}
if ($n -eq 0) { Say "  nothing to change (already off / absent)" }

Rule "2 key props"
Get-NetAdapterAdvancedProperty -Name $nic -ErrorAction SilentlyContinue |
  Where-Object {$_.DisplayName -match "EEE|Jumbo|Gigabit|Power|Eco|Green|Energy"} |
  Select-Object DisplayName,DisplayValue,RegistryValue | Format-Table -AutoSize | Out-String -Width 140

if ($JumboFrame) {
  Rule "3 jumbo frame"
  try {
    Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "巨型帧" -DisplayValue "9014 字节" -NoRestart -ErrorAction Stop
    Say "  JumboFrame -> 9014"
  } catch { Say ("  FAILED: " + $_.Exception.Message.Split([char]10)[0]) }
}

Rule "4 disable SMB / NetBIOS rules"
$c = 0
$smbRules = @()
try { $smbRules = @(Get-NetFirewallRule -Group "@FirewallAPI.dll,-28502" -ErrorAction Stop) } catch { }
if ($smbRules.Count -eq 0) {
  $smbRules = @(Get-NetFirewallRule -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match "SMB|NetBIOS|文件和打印机共享|网络发现" })
}
foreach ($r in $smbRules) {
  if ($r.Enabled -eq "True") { Disable-NetFirewallRule -DisplayName $r.DisplayName -ErrorAction SilentlyContinue; $c++ }
}
Say ("  disabled {0} of {1} SMB/NetBIOS rules" -f $c, $smbRules.Count)

Rule "5 block inbound (opt-in)"
if ($BlockTunnel) {
  $null = New-NetFirewallRule -DisplayName "BlockInbound-APNetwork" -Direction Inbound -InterfaceAlias "APNetwork" -Action Block -Profile Any -ErrorAction SilentlyContinue
  Say "  blocked inbound on APNetwork"
} else {
  Say "  skipped (default OFF: blocking the TUN interface inbound can break the tunnel)"
}
if ($BlockVirtual) {
  foreach ($v in @("vEthernet (WSL (Hyper-V firewall))","vEthernet (Default Switch)")) {
    $null = New-NetFirewallRule -DisplayName "BlockInbound-$v" -Direction Inbound -InterfaceAlias $v -Action Block -Profile Any -ErrorAction SilentlyContinue
    Say ("  blocked inbound: " + $v)
  }
} else { Say "  skipped vEthernet(WSL)/DefaultSwitch (need -BlockVirtual)" }

if ($EnableDoH) {
  Rule "6 DoH"
  try {
    Set-DnsClientGlobalSetting -DnsOverHttpsEnabled -ErrorAction Stop
    Add-DnsClientDohServerAddress -ServerAddress "223.5.5.5" -DohTemplate "https://dns.alidns.com/dns-query" -AllowFallbackToUdp $true -AutoUpgrade $true -ErrorAction Stop
    Say "  DoH enabled for 223.5.5.5"
  } catch { Say ("  DoH failed: " + $_.Exception.Message.Split([char]10)[0]) }
}

if (-not $SkipNicRestart) {
  Rule "7 restart NIC"
  Say "  重启以太网会移除 APNetwork TUN 适配器, 之后必须跑 NetRepair.ps1 重建隧道。"
  Restart-NetAdapter -Name $nic -Confirm:$false -ErrorAction SilentlyContinue
  Say "  restarted"
} else {
  Say ""
  Say "(NIC restart skipped via -SkipNicRestart)"
}

Rule "final state"
Get-NetAdapter -Name $nic | Select-Object Name,Status,LinkSpeed | Format-Table -AutoSize | Out-String -Width 120
Say "DONE."