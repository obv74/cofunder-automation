"""Configuration settings for the CoFoundersLab scraper bot.

All settings can be overridden via environment variables or a .env file
in the project directory. See .env.example for available variables.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project directory (same as this file)
_SRC_DIR = Path(__file__).resolve().parent
load_dotenv(_SRC_DIR / ".env")

# Session file next to this config (same dir as main.py) so login and scrape use the same file
SESSION_PATH = _SRC_DIR / "session" / "state.json"


def _env_bool(key: str, default: bool) -> bool:
    """Parse env var as boolean. Accepts 1/0, true/false, yes/no (case-insensitive)."""
    v = os.getenv(key)
    if v is None or v == "":
        return default
    return v.strip().lower() in ("1", "true", "yes")


def _env_int(key: str, default: int) -> int:
    """Parse env var as int."""
    v = os.getenv(key)
    if v is None or v == "":
        return default
    try:
        return int(v.strip())
    except ValueError:
        return default


@dataclass
class ScraperConfig:
    """Configuration for the scraper bot (env overrides)."""

    session_path: str = str(SESSION_PATH)
    login_url: str = "https://cofounderslab.com/login"
    login_timeout: int = 300000  # 5 minutes in milliseconds
    headless: bool = True  # Default headless for scrape (CLI --headless overrides)
    retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    # Selector/page timeouts (ms) – increase on slow machines or flaky network
    selector_timeout_ms: int = 20000
    page_load_timeout_ms: int = 45000
    # Monitoring: interval between checks (seconds)
    monitor_interval_sec: int = 60
    # Max monitoring cycles (0 = unlimited). Use 1 for "run once and exit" (e.g. scheduled task).
    max_monitor_checks: int = 0
    # Extra wait after feed reload for content to render (seconds)
    feed_render_wait_sec: int = 5
    # Retries when creating a new post fails (e.g. timeout) before next cycle
    create_post_retries: int = 3
    retry_delay_create_post_sec: int = 5
    # Telegram alerts when errors occur (env: TELEGRAM_ALERTS_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    telegram_alerts_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    # Set false only if behind a proxy/firewall that causes SSL CERTIFICATE_VERIFY_FAILED (e.g. corporate SSL inspection)
    telegram_ssl_verify: bool = True
    # Logging: level (DEBUG, INFO, WARNING, ERROR), optional file path for rotating file handler
    debug: bool = False
    log_level: str = "INFO"
    log_file: str = ""


def _load_config() -> ScraperConfig:
    """Build config from env with defaults."""
    return ScraperConfig(
        session_path=str(SESSION_PATH),
        login_url=os.getenv("LOGIN_URL", "https://cofounderslab.com/login"),
        login_timeout=_env_int("LOGIN_TIMEOUT_MS", 300000),
        headless=_env_bool("HEADLESS", True),
        retry_attempts=_env_int("RETRY_ATTEMPTS", 3),
        retry_delay=_env_int("RETRY_DELAY", 5),
        selector_timeout_ms=_env_int("SELECTOR_TIMEOUT_MS", 20000),
        page_load_timeout_ms=_env_int("PAGE_LOAD_TIMEOUT_MS", 45000),
        monitor_interval_sec=_env_int("MONITOR_INTERVAL_SEC", 60),
        max_monitor_checks=_env_int("MAX_MONITOR_CHECKS", 0),
        feed_render_wait_sec=_env_int("FEED_RENDER_WAIT_SEC", 5),
        create_post_retries=_env_int("CREATE_POST_RETRIES", 3),
        retry_delay_create_post_sec=_env_int("RETRY_DELAY_CREATE_POST_SEC", 5),
        debug=_env_bool("DEBUG", False),
        telegram_alerts_enabled=_env_bool("TELEGRAM_ALERTS_ENABLED", False),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        telegram_ssl_verify=_env_bool("TELEGRAM_SSL_VERIFY", True),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO",
        log_file=os.getenv("LOG_FILE", "").strip(),
    )


# Global configuration instance (reads from .env)
config = _load_config()
