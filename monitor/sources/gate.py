"""Gate.io public currency list. No key needed. One row per coin and chain."""
from ..http import get_json
from ..model import NetworkStatus, Snapshot, norm

LABEL = "Gate"
URL = "https://api.gateio.ws/api/v4/spot/currencies"
NEEDS_KEYS = False


def fetch() -> Snapshot:
    snap: Snapshot = {}
    for item in get_json(URL):
        chain = item.get("chain")
        if not chain:
            continue
        snap[(norm(item.get("currency")), norm(chain))] = NetworkStatus(
            deposit=not item.get("deposit_disabled", False),
            withdraw=not item.get("withdraw_disabled", False),
        )
    return snap
