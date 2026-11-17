"""Poll platforms, compare with the last snapshot, alert on changes.

    python -m monitor.main                 # all sources, every 60 s
    python -m monitor.main --once kucoin   # one round, one source
"""
import argparse
import logging
import os
import time

from . import notify, store
from .diff import describe
from .sources import SOURCES, bitpin

log = logging.getLogger("monitor")


def load_env(path=".env"):
    """Small .env reader, so the project needs nothing beyond requests."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if v.strip():
                    os.environ.setdefault(k.strip(), v.strip())


def run_round(names, state_dir, listed):
    for name in names:
        src = SOURCES[name]
        path = os.path.join(state_dir, f"{name}.json")
        try:
            new = src.fetch()
        except Exception as e:  # one platform being down should not stop the others
            log.warning("%s: %s", src.LABEL, e)
            continue
        if not new:
            log.warning("%s returned nothing, keeping the old snapshot", src.LABEL)
            continue
        old = store.load(path)
        if old:
            notify.send(describe(src.LABEL, old, new, listed))
        else:
            log.info("%s: first snapshot, %d pairs saved", src.LABEL, len(new))
        store.save(path, new)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sources", nargs="*", default=list(SOURCES))
    p.add_argument("--interval", type=int, default=60, help="seconds between rounds")
    p.add_argument("--once", action="store_true", help="run one round and exit")
    p.add_argument("--state", default="state", help="folder for snapshots")
    a = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_env()
    names = []
    for n in a.sources:
        if n not in SOURCES:
            p.error(f"unknown source {n}; choose from {', '.join(SOURCES)}")
        src = SOURCES[n]
        if src.NEEDS_KEYS and not src.has_keys():
            log.warning("%s skipped: no API key in the environment", src.LABEL)
            continue
        names.append(n)

    try:
        listed = bitpin.listed_coins()
    except Exception as e:
        log.warning("could not load the Bitpin listing, alerts will not be marked: %s", e)
        listed = set()

    while True:
        run_round(names, a.state, listed)
        if a.once:
            break
        time.sleep(a.interval)


if __name__ == "__main__":
    main()
