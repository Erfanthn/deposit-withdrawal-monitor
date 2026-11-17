from monitor import store
from monitor.diff import describe
from monitor.model import NetworkStatus as S
from monitor.notify import _chunks


def test_changes_are_reported():
    old = {("USDT", "TRC20"): S(True, True), ("BTC", "BTC"): S(True, True)}
    new = {("USDT", "TRC20"): S(False, True), ("ETH", "ERC20"): S(True, True)}
    out = describe("X", old, new, listed={"USDT"})
    assert "* X: deposit USDT-TRC20 open -> closed" in out
    assert "  X: pair removed BTC-BTC" in out
    assert "  X: new pair ETH-ERC20" in out
    assert len(out) == 3


def test_no_change_no_lines():
    snap = {("USDT", "TRC20"): S(True, False)}
    assert describe("X", snap, dict(snap)) == []


def test_store_roundtrip(tmp_path):
    snap = {("USDT", "BEP20"): S(True, False)}
    p = str(tmp_path / "s.json")
    store.save(p, snap)
    assert store.load(p) == snap


def test_long_alerts_are_split():
    text = "\n".join(f"line {i}" for i in range(2000))
    parts = list(_chunks(text))
    assert all(len(p) <= 3500 for p in parts)
    assert "\n".join(parts) == text
