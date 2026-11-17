"""KuCoin public currency list. No key needed."""
from ..http import get_json
from ..model import NetworkStatus, Snapshot, norm

LABEL = "KuCoin"
URL = "https://api.kucoin.com/api/v3/currencies"
NEEDS_KEYS = False


def fetch() -> Snapshot:
    snap: Snapshot = {}
    for item in get_json(URL).get("data") or []:
        coin = norm(item.get("currency"))
        for chain in item.get("chains") or []:
            snap[(coin, norm(chain.get("chainName")))] = NetworkStatus(
                deposit=bool(chain.get("isDepositEnabled")),
                withdraw=bool(chain.get("isWithdrawEnabled")),
            )
    return snap
