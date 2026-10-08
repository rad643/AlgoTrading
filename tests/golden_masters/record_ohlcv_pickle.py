import os
import pickle

from data_loading import data_loader as dl
from main import selected_tickers

"""
Grabs the real Alpaca bars once and saves them to ohlcv.pkl, next to this file.

The golden master test loads ohlcv.pkl instead of calling Alpaca, so it runs
offline and gets the exact same bars every time.

Run it once, from the repo root:
    python -m tests.golden_masters.record_ohlcv_pickle

Running it again overwrites ohlcv.pkl with whatever Alpaca returns that current day,
so only do it on purpose (new tickers or dates), then delete results.txt so
the test saves a new one.
"""


bars_by_symbol = dl.hist_data(
    selected_tickers,
    timeframe="1Day",
    start="2024-01-16",
    end="2026-01-13",
    limit=1000,
)

target_dir = os.path.dirname(__file__)

file_name = "ohlcv.pkl"

full_path = os.path.join(target_dir, file_name)

with open(full_path, "wb") as file:
    pickle.dump(bars_by_symbol, file)
