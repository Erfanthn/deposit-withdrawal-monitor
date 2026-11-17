import json
import os

from .model import NetworkStatus, Snapshot


def save(path: str, snap: Snapshot) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = {f"{c}|{n}": {"deposit": s.deposit, "withdraw": s.withdraw} for (c, n), s in snap.items()}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def load(path: str) -> Snapshot:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    snap: Snapshot = {}
    for key, v in data.items():
        coin, _, network = key.partition("|")
        snap[(coin, network)] = NetworkStatus(bool(v.get("deposit")), bool(v.get("withdraw")))
    return snap
