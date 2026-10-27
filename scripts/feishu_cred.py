#!/usr/bin/env python3
"""
共享飞书凭据解析。

来源优先级：
  1. 环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET
  2. ~/.openclaw/feishu-cred.env (自动加载, 0600)
  3. openclaw.json channels.feishu.appSecret 为明文字符串时直接使用

openclaw.json 的 appSecret 已迁移为密钥库 SecretRef，shell 脚本读不到明文，
因此 cron 场景统一走 (1)/(2) 通道。
"""
import json
import os
import re
from pathlib import Path

CRED_FILE = Path.home() / ".openclaw" / "feishu-cred.env"
CONFIG = Path.home() / ".openclaw" / "openclaw.json"


def load_env_file(path=CRED_FILE):
    """把 cred.env 里的 export 行解析进 os.environ（已存在则不覆盖）。"""
    if not path.exists():
        return False
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line)
            if not m:
                continue
            key = m.group(1)
            val = m.group(2).strip().strip('"').strip("'")
            os.environ.setdefault(key, val)
        return True
    except Exception:
        return False


def resolve(tag="feishu", fs=None):
    """返回 (app_id, app_secret, err)。err 非空表示不可用。"""
    load_env_file()
    if fs is None:
        try:
            fs = json.loads(CONFIG.read_text()).get("channels", {}).get("feishu", {})
        except Exception:
            fs = {}

    app_id = os.environ.get("FEISHU_APP_ID", "") or fs.get("appId", "")
    raw = os.environ.get("FEISHU_APP_SECRET", "") or fs.get("appSecret", "")

    if isinstance(raw, dict):
        return app_id, "", (
            tag + ": appSecret 是 SecretRef(secret store: "
            + str(raw.get("id", "?"))
            + ")，cron 脚本读不到明文。请确认 "
            + str(CRED_FILE)
            + " 存在且含明文，或 export FEISHU_APP_SECRET=<明文>。"
        )
    if not isinstance(raw, str):
        raw = ""
    return app_id, raw, ""


if __name__ == "__main__":
    a, s, e = resolve("selfcheck")
    print("cred_file_exists:", CRED_FILE.exists())
    print("appId:", a or "(none)")
    print("secret_len:", len(s))
    print("err:", e or "(none)")