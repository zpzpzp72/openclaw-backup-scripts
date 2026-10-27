#!/bin/bash
# dns-drift-monitor.sh — Alert when public IP changes
# Cron: DNS-Drift-Monitor (c3f2d27a-8cbf-4150-9802-a54397e18c01)
# If IP changes, output starts with DNS_DRIFT_ALERT

STATE_FILE="${STATE_FILE:-/tmp/dns-drift-state.txt}"
LOG_FILE="${LOG_FILE:-/tmp/dns-drift.log}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

get_public_ip() {
    curl -s --max-time 8 https://api.ipify.org \
        || curl -s --max-time 8 https://ifconfig.me \
        || curl -s --max-time 8 https://checkip.amazonaws.com \
        || echo "ERROR"
}

current_ip=$(get_public_ip)

if [ "$current_ip" = "ERROR" ] || [ -z "$current_ip" ]; then
    log "ERROR: Could not fetch public IP"
    exit 0
fi

log "Current IP: $current_ip"

if [ ! -f "$STATE_FILE" ]; then
    echo "$current_ip" > "$STATE_FILE"
    log "First run, stored IP: $current_ip"
    exit 0
fi

previous_ip=$(cat "$STATE_FILE")

if [ "$current_ip" != "$previous_ip" ]; then
    echo "$current_ip" > "$STATE_FILE"
    log "IP CHANGE: $previous_ip -> $current_ip"
    echo "DNS_DRIFT_ALERT Public IP changed from $previous_ip to $current_ip at $(date '+%Y-%m-%d %H:%M:%S %Z')"
    exit 0
fi

log "No change: $current_ip"
exit 0
