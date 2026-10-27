#!/usr/bin/env python3
"""Send OpenClaw backup log summary to Feishu chat."""
import json
import requests
import sys
from datetime import date
from pathlib import Path
# 凭据统一由 feishu_cred 解析: env -> ~/.openclaw/feishu-cred.env -> openclaw.json
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.expanduser("~/.openclaw/workspace/scripts"))
from feishu_cred import resolve as _resolve_feishu

LOG_FILE = Path.home() / ".openclaw-backup.log"
TODAY_PREFIX = date.today().strftime("%Y-%m-%d")

def get_feishu_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret}, timeout=10)
    if resp.status_code != 200 or resp.json().get("code") != 0:
        return None
    return resp.json()["tenant_access_token"]

def extract_today_logs():
    if not LOG_FILE.exists():
        return None
    lines = LOG_FILE.read_text().splitlines()
    today_lines = []
    in_today = False
    for line in lines:
        if line.startswith(f"[{TODAY_PREFIX}"):
            in_today = True
        if in_today:
            today_lines.append(line)
            # Stop after we see the next day's entry or a big gap
            if len(today_lines) > 50:
                break
    return today_lines

def parse_backup_result(lines):
    """Parse backup log lines to extract result."""
    result = {
        "status": "unknown",
        "file": None,
        "size": None,
        "errors": [],
        "raw_lines": lines
    }
    for line in lines:
        if "备份成功" in line:
            result["status"] = "success"
            # Extract filename and size
            parts = line.split("备份成功: ")
            if len(parts) > 1:
                info = parts[1].split(" (")
                result["file"] = info[0] if len(info) > 0 else None
                result["size"] = info[1].rstrip(")") if len(info) > 1 else None
        elif "备份失败" in line:
            result["status"] = "failed"
        elif "tar 退出码" in line:
            result["errors"].append(line)
        elif "tar:" in line and "file changed" in line:
            result["errors"].append(line.strip())
    return result

def build_summary(result):
    lines = result["raw_lines"]
    # Find key lines
    start = next((l for l in lines if "开始备份" in l), None)
    end = next((l for l in lines if "备份完成" in l or "备份成功" in l or "备份失败" in l), None)
    
    status_emoji = {"success": "✅", "failed": "❌", "unknown": "⚠️"}.get(result["status"], "⚠️")
    
    summary = f"""📦 **OpenClaw 备份日志 — {TODAY_PREFIX}**

{status_emoji} **状态:** {result["status"].upper()}

📁 **备份文件:** {result["file"] or "N/A"}
💾 **大小:** {result["size"] or "N/A"}
"""
    if result["errors"]:
        summary += "\n⚠️ **错误信息:**\n"
        for err in result["errors"]:
            summary += f"- `{err}`\n"
    
    if start:
        summary += f"\n⏰ **开始:** `{start.split(']')[1].strip()}`"
    if end:
        summary += f"\n⏰ **结束:** `{end.split(']')[1].strip()}`"
    
    summary += f"\n📝 **原始日志:** 详见 `~/.openclaw-backup.log`"
    return summary

def send_feishu_message(token, chat_id, content):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    headers = {"Authorization": f"Bearer {token}"}
    message_data = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    resp = requests.post(url, headers=headers, params=params, json=message_data, timeout=30)
    return resp.status_code == 200 and resp.json().get("code") == 0

def main():
    # Load config
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if not config_path.exists():
        print("ERROR: openclaw.json not found")
        sys.exit(1)
    config = json.loads(config_path.read_text())
    
    feishu_cfg = config.get("channels", {}).get("feishu", {})
    app_id, app_secret, cred_err = _resolve_feishu("send-backup-log-feishu", feishu_cfg)
    if cred_err:
        print(f"ERROR: {cred_err}", file=sys.stderr)
        sys.exit(2)
    chat_id = feishu_cfg.get("groupAllowFrom", [None])[0]
    
    if not all([app_id, app_secret, chat_id]):
        print("ERROR: Feishu config incomplete")
        sys.exit(2)
    
    # Get token
    token = get_feishu_token(app_id, app_secret)
    if not token:
        print("ERROR: Failed to get Feishu token")
        sys.exit(3)
    
    # Extract and parse logs
    lines = extract_today_logs()
    if not lines:
        print("No log entries found for today")
        sys.exit(4)
    
    result = parse_backup_result(lines)
    summary = build_summary(result)
    
    print("Summary:")
    print(summary)
    print()
    
    # Send to Feishu
    success = send_feishu_message(token, chat_id, summary)
    if success:
        print("✅ Message sent to Feishu successfully")
        sys.exit(0)
    else:
        print("❌ Failed to send message to Feishu")
        sys.exit(5)

if __name__ == "__main__":
    main()
