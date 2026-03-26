"""Telegram alerts when errors occur. Configure via TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ALERTS_ENABLED in .env."""

import json
import ssl
import urllib.error
import urllib.request

from app_logger import get_logger
from config import config

log = get_logger(__name__)

# Telegram message max length
MAX_MESSAGE_LENGTH = 4096


def send_alert(message: str, prefix: str = "CoFounder Bot") -> bool:
    """Send a Telegram message. Safe to call from anywhere; no-op if alerts disabled or not configured.

    Args:
        message: Alert text (will be truncated if over Telegram limit).
        prefix: Short prefix for the alert (e.g. "CoFounder Bot").

    Returns:
        True if sent successfully, False otherwise (or if disabled).
    """
    if not config.telegram_alerts_enabled or not config.telegram_bot_token or not config.telegram_chat_id:
        return False
    text = f"[{prefix}]\n{message}"
    if len(text) > MAX_MESSAGE_LENGTH:
        text = text[: MAX_MESSAGE_LENGTH - 3] + "..."
    url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
    data = json.dumps({"chat_id": config.telegram_chat_id, "text": text, "disable_web_page_preview": True}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})

    ssl_ctx = ssl.create_default_context()
    if not config.telegram_ssl_verify:
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_ctx))

    try:
        with opener.open(req, timeout=10) as resp:
            if resp.status == 200:
                return True
    except (urllib.error.URLError, OSError) as e:
        log.warning("Telegram alert send failed: %s", e)
    except Exception as e:
        # Keep alert path fully safe: never propagate notification failures.
        log.warning("Unexpected error while sending Telegram alert: %s", e)
    return False
