import logging
import time

import requests

log = logging.getLogger(__name__)


def get_json(url, *, params=None, headers=None, retries=3, delay=5, timeout=20):
    """GET with a few retries. Raises on the last failure."""
    last = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}: {r.text[:200]}"
        except requests.RequestException as e:
            last = str(e)
        log.warning("%s failed (attempt %d/%d): %s", url, attempt, retries, last)
        time.sleep(delay)
    raise RuntimeError(f"{url} failed after {retries} attempts: {last}")
