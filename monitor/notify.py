"""Send alerts to Telegram if configured, otherwise print them."""
import hashlib
import logging
import os
import time

import requests

log = logging.getLogger(__name__)
_recent = {}
DEDUP_SECONDS = 600
MAX_LEN = 3500  # Telegram's limit is 4096 characters


def send(lines):
    if not lines:
        return
    text = "\n".join(lines)
    digest = hashlib.sha256(text.encode()).hexdigest()
    now = time.time()
    if now - _recent.get(digest, 0) < DEDUP_SECONDS:
        log.info("same alert sent recently, skipped")
        return
    _recent[digest] = now

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chats = [c.strip() for c in os.environ.get("TELEGRAM_CHAT_IDS", "").split(",") if c.strip()]
    if not token or not chats:
        print(text, flush=True)
        return
    for chunk in _chunks(text):
        for chat in chats:
            try:
                r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                  json={"chat_id": chat, "text": chunk}, timeout=15)
                if r.status_code == 429:
                    time.sleep(r.json().get("parameters", {}).get("retry_after", 30))
                elif r.status_code != 200:
                    log.warning("Telegram returned %s", r.status_code)
            except requests.RequestException as e:
                # never log the URL here: it contains the bot token
                log.warning("Telegram send failed: %s", type(e).__name__)


def _chunks(text):
    while text:
        if len(text) <= MAX_LEN:
            yield text
            return
        cut = text.rfind("\n", 0, MAX_LEN)
        cut = cut if cut > 0 else MAX_LEN
        yield text[:cut]
        text = text[cut:].lstrip("\n")
