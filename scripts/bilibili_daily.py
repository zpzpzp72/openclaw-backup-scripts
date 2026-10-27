#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站热门视频日报 - cron 包装脚本

由 ~/.openclaw/skills/bilibili-hot-monitor 提供底层 API，
本脚本负责：
  1. 优雅降级（无 cookies → 匿名热门；无 OpenRouter → 无 AI 总结；
     无 SMTP 凭据 → 仅生成报告文件，不发邮件）
  2. 统一日志、退出码、错误处理
  3. 让 cron 在任何凭据状态下都能产出有用的结果

环境变量（全部可选）：
  BILIBILI_COOKIES    完整 B 站 Cookie 字符串
  OPENROUTER_API_KEY  OpenRouter Key
  SMTP_EMAIL          发件邮箱
  SMTP_PASSWORD       发件邮箱应用密码
  BILIBILI_RECIPIENTS 收件人，逗号分隔
  BILIBILI_NUM_VIDEOS 视频数量（默认 10）
"""

import datetime
import io
import json
import os
import sys
import time
from pathlib import Path
# 凭据统一由 feishu_cred 解析: env -> ~/.openclaw/feishu-cred.env -> openclaw.json
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.expanduser("~/.openclaw/workspace/scripts"))
from feishu_cred import resolve as _resolve_feishu

# 修复 Windows 控制台编码（脚本也可能在 Windows 跑）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SKILL_DIR = Path.home() / ".openclaw" / "skills" / "bilibili-hot-monitor"
sys.path.insert(0, str(SKILL_DIR))

from bilibili_api import BilibiliAPI, format_number, format_duration, format_timestamp  # noqa: E402

REPORT_DIR = Path.home() / ".openclaw" / "workspace" / "reports" / "bilibili-hot-daily"
FINANCE_SEND_EMAIL = Path.home() / ".openclaw" / "workspace" / "agents" / "finance" / "send_email.py"
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"
TODAY = datetime.date.today().strftime("%Y-%m-%d")
NOW_STR = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
REPORT_FILE = REPORT_DIR / f"bilibili_hot_{TODAY}.md"


def log(msg: str) -> None:
    """带时间戳的日志输出"""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def parse_cookies(s: str) -> dict:
    out = {}
    for item in s.split(";"):
        item = item.strip()
        if "=" in item:
            k, v = item.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def build_client() -> tuple[BilibiliAPI, str, bool]:
    """构造 BilibiliAPI client + 模式描述"""
    cookies_str = os.environ.get("BILIBILI_COOKIES", "").strip()
    if cookies_str:
        cookies = parse_cookies(cookies_str)
        sessdata = cookies.get("SESSDATA", "")
        log(f"🔐 使用登录 cookies 模式 (SESSDATA len={len(sessdata)})")
        api = BilibiliAPI(
            sessdata=sessdata,
            bili_jct=cookies.get("bili_jct", ""),
            buvid3=cookies.get("buvid3", ""),
            dedeuserid=cookies.get("DedeUserID", ""),
            all_cookies=cookies,
        )
        return api, "登录模式", True
    else:
        log("ℹ️  未提供 BILIBILI_COOKIES，使用匿名模式（仅热门列表，无字幕/AI）")
        return BilibiliAPI(), "匿名模式", False


def fetch_subtitle(api: BilibiliAPI, bvid: str, aid: int, cid: int) -> str | None:
    """获取视频字幕纯文本（需要登录 cookies）"""
    try:
        return api.get_video_subtitle_text(bvid, aid=aid, cid=cid, prefer_lang="zh")
    except Exception as e:
        log(f"  ⚠️  字幕获取失败 {bvid}: {e}")
        return None


def fetch_videos(api: BilibiliAPI, n: int) -> list:
    """获取热门视频列表"""
    log(f"📡 获取 B 站热门 Top {n}...")
    videos = api.get_popular_videos(page_size=n)
    log(f"✅ 获取到 {len(videos)} 个视频")
    return videos


def enrich_video(api: BilibiliAPI, video: dict, idx: int, total: int,
                 openrouter_key: str, model: str) -> dict:
    """补充视频信息：UP主 cid、字幕、AI 总结、点评"""
    bvid = video["bvid"]
    short_title = video["title"][:18] + "..." if len(video["title"]) > 18 else video["title"]

    # 仅登录模式才尝试拿 cid + 字幕（匿名模式不缓存）
    if openrouter_key:
        pct = int(idx / total * 100)
        if pct in (25, 50, 75) or idx == total:
            log(f"  [{idx}/{total}] 字幕+AI总结: {short_title}")

    video_data = {
        "idx": idx,
        "bvid": bvid,
        "title": video["title"],
        "owner": video.get("owner", {}),
        "stat": video.get("stat", {}),
        "desc": video.get("desc", ""),
        "duration": video.get("duration", 0),
        "pubdate": video.get("pubdate", 0),
        "ai_summary": "",
        "ai_outline": [],
        "ai_comment": "",
        "viral_analysis": "",
        "subtitle_text": "",
    }

    if not openrouter_key:
        return video_data

    # 有 OpenRouter Key 时才尝试拿字幕 + 总结
    try:
        info = api.get_video_info(bvid)
        cid = info.get("cid")
        aid = info.get("aid")
        subtitle = fetch_subtitle(api, bvid, aid, cid)
        if subtitle:
            video_data["subtitle_text"] = subtitle
            # 调用 skill 自带的 generate_report.py 中的两个 LLM 函数
            from generate_report import generate_video_summary_from_subtitle, generate_ai_comment
            summary = generate_video_summary_from_subtitle(
                api_key=openrouter_key, model=model,
                title=video["title"], subtitle_text=subtitle,
            )
            video_data["ai_summary"] = summary.get("summary", "")
            video_data["ai_outline"] = summary.get("outline", [])
            time.sleep(0.5)

            ai_comment, viral = generate_ai_comment(
                api_key=openrouter_key, model=model, video_info=video_data,
            )
            video_data["ai_comment"] = ai_comment
            video_data["viral_analysis"] = viral
            time.sleep(0.5)
    except Exception as e:
        log(f"  ⚠️  AI 处理失败 {bvid}: {e}")

    return video_data


def render_report(videos: list, mode: str) -> str:
    """渲染 Markdown 报告"""
    lines = [
        "# B站热门视频日报",
        "",
        f"**生成时间**：{NOW_STR}",
        f"**模式**：{mode}",
        "",
        "---",
        "",
        f"## 📋 本期热门视频（{TODAY}）",
        "",
        "| 排名 | 视频标题 | 播放量 | 链接 |",
        "|------|----------|--------|------|",
    ]
    for v in videos:
        link = f"https://www.bilibili.com/video/{v['bvid']}"
        safe_title = v["title"].replace("|", "｜")
        lines.append(
            f"| {v['idx']} | {safe_title} | {format_number(v['stat'].get('view', 0))} "
            f"| [打开视频]({link}) |"
        )
    lines += ["", "---", "", "## 📹 详细报告", ""]

    for v in videos:
        lines.append(f"### {v['idx']}. {v['title']}")
        lines.append("")
        lines.append(f"- **UP主**：{v['owner'].get('name', 'N/A')}")
        lines.append(
            f"- **时长**：{format_duration(v.get('duration', 0))} | "
            f"**发布时间**：{format_timestamp(v.get('pubdate', 0))}"
        )
        lines.append("")
        stat = v.get("stat", {})
        lines.append(
            f"**📊 数据统计**：\n"
            f"> 播放 {format_number(stat.get('view', 0))} | "
            f"点赞 {format_number(stat.get('like', 0))} | "
            f"收藏 {format_number(stat.get('favorite', 0))} | "
            f"硬币 {format_number(stat.get('coin', 0))} | "
            f"弹幕 {stat.get('danmaku', 0):,} | "
            f"评论 {stat.get('reply', 0):,} | "
            f"分享 {stat.get('share', 0):,}"
        )
        lines.append("")

        if v.get("desc"):
            desc = v["desc"][:300].replace("\n", " ").replace("\r", " ")
            lines.append(f"**📝 视频简介**：\n> {desc}{'...' if len(v['desc']) > 300 else ''}")
            lines.append("")

        if v.get("ai_summary"):
            lines.append(f"**🤖 AI视频总结**：\n> {v['ai_summary']}")
            if v.get("ai_outline"):
                lines.append(">")
                lines.append("> **内容大纲**：")
                for item in v["ai_outline"][:4]:
                    t = item.get("title", "")
                    parts = item.get("part_outline", [])
                    if t:
                        lines.append(f"> • **{t}**")
                        for p in parts[:3]:
                            c = p.get("content", "")
                            if c:
                                lines.append(f">   - {c}")
            lines.append("")
        elif not v.get("ai_summary") and mode == "登录模式":
            lines.append("**🤖 AI视频总结**：\n> （该视频无字幕，无法生成总结）")
            lines.append("")

        if v.get("ai_comment"):
            lines.append(f"**💡 AI点评**：\n> {v['ai_comment']}")
            lines.append("")
        if v.get("viral_analysis"):
            lines.append(f"**🚀 运营爆款分析**：\n> {v['viral_analysis']}")
            lines.append("")

        lines.append(f"🔗 [点击观看视频](https://www.bilibili.com/video/{v['bvid']})")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("*报告由 B 站 API 自动生成（cron: bilibili-hot-cron.sh）*")
    return "\n".join(lines)


def send_email_via_qq(report_path: Path, videos: list) -> bool:
    """
    使用 AMAT 模式的多 provider SMTP 发送邮件（默认 QQ，参考 finance/send_email.py）
    凭据读取：~/.secrets/qq_smtp_password（AMAT 已配置）
    收件人：环境变量 BILIBILI_RECIPIENTS（逗号分隔），未设则跳过
    """
    recipients = os.environ.get("BILIBILI_RECIPIENTS", "").strip()
    if not recipients:
        log("ℹ️  BILIBILI_RECIPIENTS 未设置，跳过邮件推送")
        return True
    if not FINANCE_SEND_EMAIL.exists():
        log(f"❌ 找不到 {FINANCE_SEND_EMAIL}")
        return False

    # 读全文后传给 --body（QQ SMTP 派发器目前只接受 --body，不支持 --body-file）
    body_md = report_path.read_text(encoding="utf-8")
    subject = f"B站热门视频日报 - {TODAY}"

    rc_list = [r.strip() for r in recipients.split(",") if r.strip()]
    log(f"📧 发送邮件给 {len(rc_list)} 个收件人 (provider=qq)...")

    import subprocess
    all_ok = True
    for rcpt in rc_list:
        try:
            result = subprocess.run(
                [
                    "python3", str(FINANCE_SEND_EMAIL),
                    "--provider", "qq",
                    "--to", rcpt,
                    "--subject", subject,
                    "--body", body_md,
                    "--html",
                ],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                log(f"   ✅ → {rcpt}")
            else:
                log(f"   ❌ → {rcpt}: {result.stderr.strip() or '未知错误'}")
                all_ok = False
        except Exception as e:
            log(f"   ❌ → {rcpt}: {e}")
            all_ok = False
    return all_ok


def get_feishu_token(app_id: str, app_secret: str) -> str | None:
    """获取飞书 tenant_access_token"""
    import requests
    try:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": app_id, "app_secret": app_secret}, timeout=10,
        )
        data = resp.json()
        return data.get("tenant_access_token") if data.get("code") == 0 else None
    except Exception as e:
        log(f"⚠️  获取飞书 token 失败: {e}")
        return None


def send_feishu_summary(videos: list) -> bool:
    """
    推送 B 站热门摘要到飞书群（参考 cron-scripts/send-backup-log-feishu.py）
    凭据来源：~/.openclaw/openclaw.json → channels.feishu
    推送内容：Top 10 标题 + 播放量 + 报告路径（避免超出飞书 30KB 限制）
    """
    if not OPENCLAW_CONFIG.exists():
        log("ℹ️  ~/.openclaw/openclaw.json 不存在，跳过飞书推送")
        return True
    try:
        cfg = json.loads(OPENCLAW_CONFIG.read_text())
    except Exception as e:
        log(f"❌ 解析 openclaw.json 失败: {e}")
        return False

    fs = cfg.get("channels", {}).get("feishu", {})
    if not fs.get("enabled", False):
        log("ℹ️  飞书频道未启用 (channels.feishu.enabled=false)")
        return True

    app_id, app_secret, cred_err = _resolve_feishu("bilibili", fs)
    if cred_err:
        log(f"⚠️  {cred_err}")
        return False
    chat_id = (fs.get("groupAllowFrom") or [None])[0]
    if not all([app_id, app_secret, chat_id]):
        log("ℹ️  飞书配置不完整 (appId/appSecret/groupAllowFrom)，跳过")
        return True

    # 构造摘要消息（控制长度）
    lines = [f"📺 B站热门视频日报 — {TODAY}", ""]
    total_views = 0
    for i, v in enumerate(videos, 1):
        views = v.get("stat", {}).get("view", 0)
        total_views += views
        title = v.get("title", "")[:36]
        link = f"https://www.bilibili.com/video/{v.get('bvid', '')}"
        lines.append(f"{i}. [{title}]({link}) — {format_number(views)}")
    lines.append("")
    lines.append(f"📊 总播放量：{format_number(total_views)}")
    lines.append(f"📂 完整报告：`{REPORT_FILE}`")
    summary = "\n".join(lines)

    log(f"💬 推送飞书摘要到 {chat_id}...")
    token = get_feishu_token(app_id, app_secret)
    if not token:
        log("❌ 获取飞书 token 失败，跳过推送")
        return False

    import requests
    try:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            params={"receive_id_type": "chat_id"},
            headers={"Authorization": f"Bearer {token}"},
            json={
                "receive_id": chat_id,
                "msg_type": "text",
                "content": json.dumps({"text": summary}),
            },
            timeout=30,
        )
        data = resp.json()
        if resp.status_code == 200 and data.get("code") == 0:
            log("✅ 飞书推送成功")
            return True
        else:
            log(f"❌ 飞书推送失败: {data}")
            return False
    except Exception as e:
        log(f"❌ 飞书推送异常: {e}")
        return False


def main() -> int:
    log(f"📺 B站热门视频日报 - {NOW_STR}")
    log(f"📂 报告目录: {REPORT_DIR}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    num_videos = int(os.environ.get("BILIBILI_NUM_VIDEOS", "10"))

    api, mode, _has_cookies = build_client()

    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    # 模型选择：env > 配置 > 默认 gemini flash
    model = os.environ.get("OPENROUTER_MODEL", "google/gemini-3-flash-preview")
    if openrouter_key:
        log(f"🤖 AI 功能已启用 (model={model})")
    else:
        log("ℹ️  未提供 OPENROUTER_API_KEY，跳过 AI 总结/点评")

    # 1. 获取视频
    try:
        videos = fetch_videos(api, num_videos)
    except Exception as e:
        log(f"❌ 获取热门视频失败: {e}")
        return 1

    # 2. AI 增强（可选）
    enriched = []
    total = len(videos)
    for i, video in enumerate(videos, 1):
        try:
            data = enrich_video(api, video, i, total, openrouter_key, model)
        except Exception as e:
            log(f"  ⚠️  enrich 失败 {video.get('bvid', '?')}: {e}")
            data = {
                "idx": i, "bvid": video.get("bvid", ""),
                "title": video.get("title", ""),
                "owner": video.get("owner", {}),
                "stat": video.get("stat", {}),
                "desc": video.get("desc", ""),
                "duration": video.get("duration", 0),
                "pubdate": video.get("pubdate", 0),
                "ai_summary": "", "ai_outline": [],
                "ai_comment": "", "viral_analysis": "",
            }
        enriched.append(data)

    # 3. 渲染 + 保存
    report = render_report(enriched, mode)
    REPORT_FILE.write_text(report, encoding="utf-8")
    log(f"✅ 报告已保存: {REPORT_FILE} ({len(report)} chars)")

    # 4. 推送：QQ 邮件 + 飞书摘要（独立通道，都跳过则视为成功）
    email_ok = send_email_via_qq(REPORT_FILE, enriched)
    feishu_ok = send_feishu_summary(enriched)

    if not email_ok or not feishu_ok:
        log(f"⚠️  推送部分失败 (email={email_ok}, feishu={feishu_ok})")
        return 2

    log("🎉 全部完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())