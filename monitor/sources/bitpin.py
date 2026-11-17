"""Bitpin public network settings. No key needed. The endpoint is paginated."""
from ..http import get_json
from ..model import NetworkStatus, Snapshot, norm

LABEL = "Bitpin"
URL = "https://api.bitpin.org/v1/mkt/network_settings/"
LISTING_URL = "https://api.bitpin.ir/api/v1/mkt/currencies/"
NEEDS_KEYS = False


def fetch() -> Snapshot:
    snap: Snapshot = {}
    page = 1
    while True:
        data = get_json(URL, params={"page": page, "page_size": 60})
        for item in data.get("results", []):
            coin = norm(item["currency"]["code"])
            net = item["network"]
            network = norm(net["code"])
            snap[(coin, network)] = NetworkStatus(
                deposit=not item.get("deposit_under_maintenance", False) and bool(net.get("can_deposit")),
                withdraw=not item.get("withdraw_under_maintenance", False) and bool(net.get("can_withdraw")),
            )
        if not data.get("next"):
            return snap
        page += 1


def listed_coins() -> set:
    """Coins listed on Bitpin, used to mark alerts that matter for us."""
    data = get_json(LISTING_URL)
    return {norm(item["currency"]) for item in data if "currency" in item}
