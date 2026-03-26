"""Central logging setup for CoFoundersLab scraper bot.

Call setup_logging() once at application start (e.g. in main()).
Use get_logger(__name__) in each module for a named logger.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Applied once by setup_logging
_configured = False

# Default format: timestamp | level | logger | message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    logger_name: str = "cofunder",
) -> None:
    """Configure application logging. Idempotent; safe to call once at startup.

    Args:
        log_level: One of DEBUG, INFO, WARNING, ERROR (case-insensitive).
        log_file: Optional path to log file. If set, uses RotatingFileHandler (2 MB, 5 backups).
        logger_name: Root logger name for the app (default 'cofunder').
    """
    global _configured
    if _configured:
        return
    _configured = True

    level = getattr(logging, (log_level or "INFO").upper(), logging.INFO)
    if not isinstance(level, int):
        level = logging.INFO

    root = logging.getLogger(logger_name)
    root.setLevel(level)
    root.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)
    root.addHandler(console)

    # Optional file (rotating)
    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                path,
                maxBytes=2 * 1024 * 1024,  # 2 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
        except OSError:
            root.warning("Could not create log file %s", log_file)

    # Reduce noise from third-party loggers
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given name (e.g. __name__). All loggers are under 'cofunder.*'."""
    if name == "__main__":
        name = "main"
    if name.startswith("cofunder."):
        return logging.getLogger(name)
    return logging.getLogger(f"cofunder.{name}")
