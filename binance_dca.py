#!/usr/bin/env python3
"""
binance_dca.py  –  simple dollar-cost-averaging bot for Binance Spot

•   Configure the section “USER SETTINGS” below.
•   Add the script to crontab (examples at bottom).
•   The bot keeps a tiny JSON state-file so it never buys more
    than your target amount inside the current week.

Tested with python-binance ≥ 1.0.28.                       (pip install python-binance pytz) 
Docs: https://python-binance.readthedocs.io               :contentReference[oaicite:0]{index=0}
"""

import json
import math
import os
from datetime import datetime, timedelta, timezone

import pytz
from binance.client import Client
from binance.enums import *

# ────────────────────────────────
# USER  SETTINGS
# ────────────────────────────────
API_KEY      = os.getenv("BINANCE_API_KEY")        # or paste the key here
API_SECRET   = os.getenv("BINANCE_API_SECRET")     # or paste the secret here

TRADING_PAIR = "BTCEUR"        # e.g. BTCEUR, ETHEUR … must exist on Binance Spot

INVEST_TOTAL_EUR  = 25.0       # how much to invest per period (EUR)
PERIOD            = "week"     # only "week" is implemented
SMART_INTERVAL    = True       # spread purchases across the week?
MIN_TX_EUR        = 5.0        # minimum EUR per single order when SMART_INTERVAL

TIMEZONE          = "Europe/Stockholm"
STATE_FILE        = os.path.expanduser("~/.binance_dca_state.json")
TEST_MODE         = True        # True  ➜ use create_test_order()  (no real money)
                                # False ➜ place real market orders – BE CAREFUL!

# ────────────────────────────────
# DO NOT TOUCH  BELOW THIS LINE
# ────────────────────────────────
tz     = pytz.timezone(TIMEZONE)
now    = datetime.now(tz)

if PERIOD != "week":
    raise NotImplementedError("Only weekly periods are implemented")

period_start = (now - timedelta(days=now.weekday()))       # Monday 00:00 local
period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)

# load or init state
state = {"executed": {}}          # { "2025-W17": [ts1, ts2 …] }
if os.path.isfile(STATE_FILE):
    with open(STATE_FILE, "r") as fh:
        state.update(json.load(fh))

period_key   = period_start.strftime("%G-W%V")             # e.g. 2025-W17
executed_now = state["executed"].get(period_key, [])

# 1️⃣ decide if we *should* invest on this run
if SMART_INTERVAL:
    # number of chunks = ceil(total / min_tx)   ➜ max 7 chunks
    chunks          = min(7, math.ceil(INVEST_TOTAL_EUR / MIN_TX_EUR))
    spacing_days    = 7 / chunks
    next_due_time   = period_start + timedelta(days=len(executed_now) * spacing_days)

    should_invest   = now >= next_due_time and len(executed_now) < chunks
    tranche_eur     = round(INVEST_TOTAL_EUR / chunks, 2)  # simple equal split
else:
    # non-smart: one purchase per period
    should_invest   = len(executed_now) == 0
    tranche_eur     = INVEST_TOTAL_EUR

if not should_invest:
    print(f"[{now}]  Nothing to do – already on track.")
    raise SystemExit(0)

# 2️⃣ place market buy order against quote amount (EUR)
#client = Client(API_KEY, API_SECRET, tld="com", timeout=15)
client = Client(
    API_KEY,
    API_SECRET,
    tld="com",
    requests_params={"timeout": 15}   # ← timeout lives here
)

order_kwargs = dict(
    symbol=TRADING_PAIR,
    side=SIDE_BUY,
    type=ORDER_TYPE_MARKET,
    quoteOrderQty=tranche_eur,     # spend EXACTLY this many EUR
)

try:
    if TEST_MODE:
        resp = client.create_test_order(**order_kwargs)
        print(f"[TEST-MODE] simulated order: {order_kwargs}")
    else:
        resp = client.create_order(**order_kwargs)
        print(f"Order executed: id={resp['orderId']} spent={tranche_eur} EUR")
except Exception as e:
    print(f"⚠️  Binance API error: {e}")
    raise SystemExit(2)

# 3️⃣ persist state
executed_now.append(now.isoformat())
state["executed"][period_key] = executed_now

with open(STATE_FILE, "w") as fh:
    json.dump(state, fh, indent=2)

print(f"✓ Recorded purchase #{len(executed_now)} for {period_key}")

# ────────────────────────────────
# CRON  EXAMPLES
# ────────────────────────────────
# Run once per day at 09:07 Stockholm time (adjust path & python):
#   7 9 * * * /usr/bin/python3 /home/you/bin/binance_dca.py >>/home/you/dca.log 2>&1
#
# Run every 4 hours (good for smart-interval):
#   7 */4 * * * /usr/bin/python3 /home/you/bin/binance_dca.py >>/home/you/dca.log 2>&1
#
# IMPORTANT:
# • Leave TEST_MODE=True while you experiment ➜ Binance never touches real funds.
# • Remove it *only* when you are 100 % happy with the behaviour.
