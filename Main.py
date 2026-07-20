import logging
import sys
import os

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Import build_application from Commands.py
from Commands import build_application

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
