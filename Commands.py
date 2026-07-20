import asyncio
import logging
import feedparser
import re
import os
import sys
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import ContextTypes

# Path fix
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from hinglish import to_hinglish

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

# In-memory cache
_cache = {"items": [], "fetched_at": None}

def get_greeting() -> str:
    hour = datetime.now(IST).hour
    if hour < 12:
        return "Good Morning! ☀️"
    elif hour < 17:
        return "Good Afternoon! 🌤️"
    elif hour < 21:
        return "Good Evening! 🌆"
    else:
        return "Good Night! 🌙"
