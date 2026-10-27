#!/usr/bin/env python3
"""
Generic Feishu push helper for OpenClaw cron jobs.

Usage:
    # Text (short summary)
    python3 feishu_push.py --text "Daily A股 close — 上证 3300 (+1.2%)"

    # File (HTML report upload as attachment)
    python3 feishu_push.py --file /path/to/report.html --title "A股票日报"

Credentials: read from ~/.openclaw/openclaw.json → channels.feishu.*
Design:
    - Graceful: channel disabled / creds missing → exit 0
    - Never raises: prints error and exits non-zero on Feishu failure,
      but callers should treat all non-zero as soft failure
    - Bypasses HTTP_PROXY env vars (proxy may be DOWN)
"""

import argparse
import json
import os
import sys
from pathlib import Path
import requests
# 凭据统一由 feishu_cred 解析: env -> ~/.openclaw/feishu-cred.env -> openclaw.json
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.expanduser("~/.openclaw/workspace/scripts"))
from feishu_cred import resolve as _resolve_feishu

CONFIG = Path.home() / ".openclaw" / "openclaw.json"


def get_token(app_id: str, app_secret_value: str) -> str | None:
    try:
        r = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": app_id, "app_secret": app_secret_value},
            timeout=10,
        ).json()
        return r.get("tenant_access_token") if r.get("code") == 0 else None
    except Exception as e:
        print(f"[feishu_push] token error: {e}", file=sys.stderr)
        return None


def upload_file(token: str, file_path: Path) -> str | None:
    try:
        with open(file_path, "rb") as f:
            r = requests.post(
                "https://open.feishu.cn/open-apis/im/v1/files",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": (file_path.name, f, "text/html")},
                data={"file_type": "stream"},
                timeout=60,
            ).json()
        if r.get("code") != 0:
            print(f"[feishu_push] upload error: {r}", file=sys.stderr)
            return None
        return r["data"]["file_key"]
    except Exception as e:
        print(f"[feishu_push] upload exception: {e}", file=sys.stderr)
        return None


def send_text_message(token: str, chat_id: str, text: str) -> dict:
    return requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages",
        params={"receive_id_type": "chat_id"},
        headers={"Authorization": f"Bearer {token}"},
        json={
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False),
        },
        timeout=30,
    ).json()


def send_file_message(token: str, chat_id: str, file_key: str) -> dict:
    return requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages",
        params={"receive_id_type": "chat_id"},
        headers={"Authorization": f"Bearer {token}"},
        json={
            "receive_id": chat_id,
            "msg_type": "file",
            "content": json.dumps({"file_key": file_key}),
        },
        timeout=30,
    ).json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Push content to OpenClaw Feishu chat")
    parser.add_argument("--file", help="HTML/text file to upload as attachment")
    parser.add_argument("--text", help="Plain text content (≤30KB)")
    parser.add_argument("--title", default="📊 Report", help="Title prefix (text mode only)")
    parser.add_argument("--chat-id", help="Override chat_id (default from openclaw.json)")
    args = parser.parse_args()

    if not args.file and not args.text:
        print("[feishu_push] ERROR: --file or --text required", file=sys.stderr)
        return 2

    if not CONFIG.exists():
        print(f"[feishu_push] {CONFIG} 不存在，跳过")
        return 0

    cfg = json.loads(CONFIG.read_text())
    fs = cfg.get("channels", {}).get("feishu", {})
    if not fs.get("enabled", False):
        print("[feishu_push] 频道未启用 (enabled=false)")
        return 0

    chat_id = args.chat_id or (fs.get("groupAllowFrom") or [None])[0]
    if not chat_id:
        print("[feishu_push] 无 groupAllowFrom 配置")
        return 0

    app_id, app_secret_value, cred_err = _resolve_feishu("feishu_push", fs)
    if cred_err:
        print(f"[feishu_push] {cred_err}")
        return 7
    if not (app_id and app_secret_value):
        print("[feishu_push] appId/appSecret 缺失")
        return 0

    # Bypass proxy (proxy may be DOWN, Feishu API doesn't need it)
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "NO_PROXY", "no_proxy"):
        os.environ.pop(k, None)

    token = get_token(app_id, app_secret_value)
    if not token:
        print("[feishu_push] 获取 token 失败")
        return 3

    try:
        if args.file:
            fpath = Path(args.file)
            if not fpath.is_file():
                print(f"[feishu_push] 文件不存在 {fpath}")
                return 2
            fk = upload_file(token, fpath)
            if not fk:
                return 4
            r = send_file_message(token, chat_id, fk)
            if r.get("code") == 0:
                msg_id = r.get("data", {}).get("message_id")
                print(f"[feishu_push] file={fpath.name} sent, message_id={msg_id}")
                return 0
            print(f"[feishu_push] send file error: {r}", file=sys.stderr)
            return 5
        else:
            text = (args.title + "\n\n" + args.text)[:30000]
            r = send_text_message(token, chat_id, text)
            if r.get("code") == 0:
                msg_id = r.get("data", {}).get("message_id")
                print(f"[feishu_push] text sent ({len(text)} chars), message_id={msg_id}")
                return 0
            print(f"[feishu_push] send text error: {r}", file=sys.stderr)
            return 5
    except Exception as e:
        print(f"[feishu_push] 推送异常: {e}", file=sys.stderr)
        return 6


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[feishu_push] fatal: {e}", file=sys.stderr)
        sys.exit(7)