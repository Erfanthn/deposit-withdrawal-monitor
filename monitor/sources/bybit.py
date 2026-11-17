"""Bybit coin info (v5). Signed endpoint, needs a read-only API key.

Set BYBIT_API_KEY and BYBIT_API_SECRET in your environment (see .env.example).
"""
import hashlib
import hmac
import os
import time

from ..http import get_json
from ..model import NetworkStatus, Snapshot, norm, to_bool

LABEL = "Bybit"
URL = "https://api.bybit.com/v5/asset/coin/query-info"
NEEDS_KEYS = True
RECV_WINDOW = "10000"


def fetch() -> Snapshot:
    key, secret = os.environ["BYBIT_API_KEY"], os.environ["BYBIT_API_SECRET"]
    ts = str(int(time.time() * 1000))
    sig = hmac.new(secret.encode(), (ts + key + RECV_WINDOW).encode(), hashlib.sha256).hexdigest()
    headers = {
        "X-BAPI-API-KEY": key,
        "X-BAPI-TIMESTAMP": ts,
        "X-BAPI-RECV-WINDOW": RECV_WINDOW,
        "X-BAPI-SIGN": sig,
    }
    data = get_json(URL, headers=headers)
    if data.get("retCode") != 0:
        raise RuntimeError(f"Bybit error {data.get('retCode')}: {data.get('retMsg')}")
    snap: Snapshot = {}
    for row in data.get("result", {}).get("rows", []):
        coin = norm(row.get("coin"))
        for chain in row.get("chains") or []:
            snap[(coin, norm(chain.get("chain")))] = NetworkStatus(
                deposit=to_bool(chain.get("chainDeposit")),
                withdraw=to_bool(chain.get("chainWithdraw")),
            )
    return snap


def has_keys() -> bool:
    return bool(os.environ.get("BYBIT_API_KEY") and os.environ.get("BYBIT_API_SECRET"))
