import logging
import os


LOG_DIR = "logs"
LOG_FILE = "trading_bot.log"


def setup_logging():
    """
    Configure application logging.
    Creates a logs directory if it does not exist.
    """

    os.makedirs(LOG_DIR, exist_ok=True)

    log_path = os.path.join(LOG_DIR, LOG_FILE)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )