from typing import List

from .model import Snapshot


def describe(label: str, old: Snapshot, new: Snapshot, listed=frozenset()) -> List[str]:
    """Human-readable changes between two snapshots.

    `listed` is the set of coins we care about most; their lines get a marker.
    """
    lines = []
    for key in sorted(new.keys() | old.keys()):
        coin, network = key
        mark = "*" if coin in listed else " "
        pair = f"{coin}-{network}"
        if key not in old:
            lines.append(f"{mark} {label}: new pair {pair}")
            continue
        if key not in new:
            lines.append(f"{mark} {label}: pair removed {pair}")
            continue
        a, b = old[key], new[key]
        if a.deposit != b.deposit:
            lines.append(f"{mark} {label}: deposit {pair} {_word(a.deposit)} -> {_word(b.deposit)}")
        if a.withdraw != b.withdraw:
            lines.append(f"{mark} {label}: withdraw {pair} {_word(a.withdraw)} -> {_word(b.withdraw)}")
    return lines


def _word(enabled: bool) -> str:
    return "open" if enabled else "closed"
