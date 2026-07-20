"""
Entry point for the Telegram bot.
Run with: python main.py
"""

import logging
import sys
import os

# Configure logging BEFORE any imports so all startup errors are visible.
# Write to stderr (default) so both normal logs and crash tracebacks appear.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Add the bot directory to the Python path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from bot import build_application


def main() -> None:
    """Start the bot using long-polling."""
    logger.info("Starting bot...")
    try:
        app = build_application()
        app.run_polling(drop_pending_updates=True)
    except Exception:
        logger.exception("Bot crashed with an unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
  
