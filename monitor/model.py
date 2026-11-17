from dataclasses import dataclass
from typing import Dict, Tuple

Key = Tuple[str, str]  # (coin, network)


@dataclass(frozen=True)
class NetworkStatus:
    deposit: bool
    withdraw: bool


Snapshot = Dict[Key, NetworkStatus]


def norm(text) -> str:
    return str(text or "").strip().upper()


def to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().lower() in {"1", "true", "yes", "enabled"}
