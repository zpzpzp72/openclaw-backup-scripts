#!/usr/bin/env bash
# openclaw-mic-button-deploy.sh
# ---------------------------------------------------------------
# Re-deploys the Mic button JS to dist/control-ui/ after an
# OpenClaw package upgrade wipes the dist files.
#
# This script does NOT restart the Gateway. Per the v3 lesson
# in .learnings/ERRORS.md, Gateway lifecycle (systemctl, /restart)
# MUST come from the user — never from a Gateway-internal agent
# or cron. After this script deploys files, the user issues
# `/restart` in Control UI chat to make the change live.
#
# Detection logic:
#   - If index.html references an openclaw-mic-button-*.js AND
#     the file is present → NO-OP (already deployed)
#   - If index.html references it but the file is missing →
#     RECOVER (re-deploy from template, update reference)
#   - If index.html has no mic reference at all → DEPLOY (inject
#     script tag before </body> and create the file)
#
# Exit codes:
#   0 — OK, already deployed (no action needed)
#   1 — Deployed successfully (user must /restart)
#   2 — Template file missing (cannot deploy)
#   3 — index.html layout changed unexpectedly (manual intervention)
# ---------------------------------------------------------------

set -euo pipefail

PKG="${OPENCLAW_PKG:-/home/zhiping/.nvm/versions/node/v26.10.0/lib/node_modules/openclaw}"
CONTROL_UI="$PKG/dist/control-ui"
INDEX="$CONTROL_UI/index.html"
TEMPLATE="/home/zhiping/.openclaw/workspace/scripts/openclaw-mic-button.template.js"
LOG="${MIC_DEPLOY_LOG:-/home/zhiping/.openclaw/logs/mic-button-deploy.log}"

ts() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[$(ts)] $*" | tee -a "$LOG"; }

mkdir -p "$(dirname "$LOG")" "$CONTROL_UI"

# 1) Template must exist
if [ ! -f "$TEMPLATE" ]; then
  log "FATAL: template not found at $TEMPLATE"
  exit 2
fi

# 2) Find current reference in index.html (if any)
CURRENT_REF=""
if [ -f "$INDEX" ]; then
  # Match timestamp like 20261004-192338 (digits-dash-digits) — \d+ alone misses the dash.
  CURRENT_REF=$(grep -oP 'openclaw-mic-button-\d+-\d+\.js' "$INDEX" 2>/dev/null | head -1 || true)
fi
CURRENT_FILE="$CONTROL_UI/$CURRENT_REF"

# 3) State check: already deployed?
if [ -n "$CURRENT_REF" ] && [ -f "$CURRENT_FILE" ]; then
  log "OK: mic button deployed ($CURRENT_REF, $(wc -c < "$CURRENT_FILE") bytes)"
  exit 0
fi

# 4) Need to act
if [ ! -f "$INDEX" ]; then
  log "FATAL: index.html missing at $INDEX — package layout changed?"
  exit 3
fi

TS="$(date +%Y%m%d-%H%M%S)"
NEW_FILE="$CONTROL_UI/openclaw-mic-button-$TS.js"
cp "$TEMPLATE" "$NEW_FILE"
SHA=$(sha256sum "$NEW_FILE" | cut -d' ' -f1)
log "Deployed: $NEW_FILE ($SHA, $(wc -c < "$NEW_FILE") bytes)"

if [ -n "$CURRENT_REF" ]; then
  # RECOVER: reference exists but file was wiped by upgrade
  sed -i "s|$CURRENT_REF|openclaw-mic-button-$TS.js|g" "$INDEX"
  log "RECOVER: index.html reference $CURRENT_REF → openclaw-mic-button-$TS.js"
else
  # FRESH DEPLOY: no reference at all
  NEEDLE=$'  </body>\n</html>'
  if ! grep -qF "$NEEDLE" "$INDEX"; then
    log "FATAL: expected needle '$NEEDLE' not found in index.html — manual review required"
    rm -f "$NEW_FILE"
    exit 3
  fi
  # Strip any stale duplicate script tags first (defensive — should be no-op in clean state)
  python3 - <<PYEOF
import re
p = "$INDEX"
with open(p) as f: src = f.read()
# Remove any existing openclaw-mic-button script tags before the </body> marker
src = re.sub(r'\n    <script type="module" src="/openclaw-mic-button-\d+-\d+\.js"></script>', '', src)
needle = "  </body>\n</html>"
if needle not in src:
    raise SystemExit("needle missing after dedup")
new = src.replace(needle, f'    <script type="module" src="/openclaw-mic-button-$TS.js"></script>\n  </body>\n</html>', 1)
with open(p, 'w') as f: f.write(new)
PYEOF
  log "DEPLOY: injected script tag in index.html"
fi

log "DONE. Files updated — user must /restart in Control UI chat to make change live."
exit 1