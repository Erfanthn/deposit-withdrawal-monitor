"""MEXC coin config. This endpoint is signed, so it needs a read-only API key.

Set MEXC_API_KEY and MEXC_API_SECRET in your environment (see .env.example).
"""
import hashlib
import hmac
import os
import time

from ..http import get_json
from ..model import NetworkStatus, Snapshot, norm, to_bool

LABEL = "MEXC"
URL = "https://api.mexc.com/api/v3/capital/config/getall"
NEEDS_KEYS = True


def fetch() -> Snapshot:
    key, secret = os.environ["MEXC_API_KEY"], os.environ["MEXC_API_SECRET"]
    query = f"timestamp={int(time.time() * 1000)}"
    sig = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    data = get_json(f"{URL}?{query}&signature={sig}", headers={"X-MEXC-APIKEY": key})
    snap: Snapshot = {}
    for item in data:
        coin = norm(item.get("coin"))
        for net in item.get("networkList") or []:
            snap[(coin, norm(net.get("network")))] = NetworkStatus(
                deposit=to_bool(net.get("depositEnable")),
                withdraw=to_bool(net.get("withdrawEnable")),
            )
    return snap


def has_keys() -> bool:
    return bool(os.environ.get("MEXC_API_KEY") and os.environ.get("MEXC_API_SECRET"))
