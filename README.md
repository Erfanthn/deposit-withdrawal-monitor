# deposit-withdrawal-monitor

Trading platforms suspend deposits or withdrawals for a coin all the time: a
network upgrade, a hack somewhere, a wallet under maintenance. If you list the
same coin and you find out late, your users find out first.

At work we used to check this by hand, coin by coin and network by network.
I wrote small bots to do it instead. This repo is a cleaned-up public
rewrite of those bots: same idea, one shared core, no company code and no keys.

## What it does

Every minute it reads the deposit and withdrawal settings of every coin on
every network (USDT on TRC20 and on ERC20 are different things), compares them
with the last snapshot, and sends one message with what changed:

```
* KuCoin: withdraw USDT-TRC20 open -> closed
  MEXC: new pair XYZ-BEP20
```

The `*` marks coins that are listed on Bitpin, the ones we care about first.
If no Telegram bot is set up, the same lines are printed to the console.

| Source | Key needed? |
|---|---|
| Bitpin | no |
| KuCoin | no |
| MEXC | read-only API key |
| Bybit | read-only API key |

A platform that is down or returns nothing is skipped for that round; the old
snapshot is kept, so a temporary outage does not show up as hundreds of
"pair removed" alerts.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env        # optional: add keys and a Telegram bot
python -m monitor.main --once kucoin bitpin   # one round
python -m monitor.main                        # all sources, every 60 s
python -m pytest -q
```

The first round only saves a snapshot. Alerts start from the second round.

## Notes

* Keys are read from the environment or `.env`, never from the code.
  `.env` and the `state/` folder are in `.gitignore`.
* The original bots were one script per platform and repeated a lot of code.
  Here each platform is one small file in `monitor/sources/` that returns
  `{(coin, network): status}`, and everything else is shared.
* I wrote this with a lot of help from AI tools, and I tested it against the
  live Bitpin and KuCoin endpoints. The MEXC and Bybit parts follow their API
  docs but need your own keys to run.

## License

MIT
