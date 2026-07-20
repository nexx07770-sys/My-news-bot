import asyncio
import logging
import feedparser
import re
import os
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import ContextTypes
import sys
sys.path.append('.')
from hinglish import to_hinglish
logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

# ── In-memory cache ──────────────────────────────────────────────────────────
_cache: dict = {"items": [], "fetched_at": None}


def get_greeting() -> str:
    hour = datetime.now(IST).hour
    if hour < 12:   return "Good Morning! ☀️"
    elif hour < 17: return "Good Afternoon! 🌤️"
    elif hour < 21: return "Good Evening! 🌆"
    else:           return "Good Night! 🌙"


def _html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _blocking_fetch_and_translate() -> list[str]:
    """RSS fetch + local Hinglish convert — no API, instant."""
    url = "https://www.thehindu.com/sci-tech/technology/feeder/default.rss"
    feed = feedparser.parse(url)
    entries = feed.entries[:5]
    if not entries:
        return []

    results = []
    for entry in entries:
        raw = getattr(entry, "summary", "")
        summary = re.sub(r"<[^>]+>", "", raw).strip()
        results.append(to_hinglish(entry.title, summary))

    logger.info("Hinglish convert done — %d items", len(results))
    return results


async def refresh_cache() -> None:
    logger.info("Refreshing news cache...")
    items = await asyncio.to_thread(_blocking_fetch_and_translate)
    _cache["items"] = items
    _cache["fetched_at"] = datetime.now(IST)
    logger.info("Cache ready — %d items", len(items))


async def job_refresh_cache(context: ContextTypes.DEFAULT_TYPE) -> None:
    await refresh_cache()


# ── Handlers ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    greeting = get_greeting()
    await update.message.reply_html(
        f"{greeting} {user.mention_html()}! 👋\n\n"
        "Main aapko latest tech ki khabrein <b>Hinglish</b> mein sunati hun 🤖\n"
        "Seedhi baat, no bakwaas! 🚀🔥\n\n"
        "<b>Commands:</b>\n"
        "/latestnews — Aaj ki taaza khabrein 📰"
    )
    logger.info("User %s started", user.id)


async def latestnews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = _cache.get("items", [])
    fetched_at = _cache.get("fetched_at")

    if not items:
        wait_msg = await update.message.reply_text("Ek second... fetch kar rahi hun! ⏳")
        await refresh_cache()
        items = _cache.get("items", [])
        await wait_msg.delete()

    if not items:
        await update.message.reply_text("News nahi mili, thodi der baad try karo 🙏")
        return

    greeting = get_greeting()
    time_str = fetched_at.strftime("%-I:%M %p IST") if fetched_at else ""

    lines = [
        f"🗞 <b>{_html(greeting)} — Aaj Ki Taaza Khabrein</b>",
        f"<i>Hello! Main Aether ki banayi hui news bot hun 🤖</i>",
    ]
    if time_str:
        lines.append(f"<i>🕐 {time_str}</i>")
    lines.append("─────────────────────────")

    for i, item in enumerate(items, 1):
        lines.append(f"<b>{i}.</b> {_html(item)}")
        if i < len(items):
            lines.append("")

    lines += [
        "─────────────────────────",
        "<i>⚡ Har 2 ghante mein auto-refresh</i>",
    ]

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")
    logger.info("latestnews → user %s", update.effective_user.id)
