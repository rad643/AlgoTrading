import os
import pickle

import pandas as pd
import pytest

import data_loading.data_loader as dl
import main
from main import selected_tickers


@pytest.mark.heavy_test(
    reason="only run voluntarily when wanting to check for changes in alpaca's live bars"
)
def test_alpaca_live_bars():
    """
    Checks that Alpaca still returns the same bars I saved in ohlcv.pkl.

    Only runs when I ask for it with `pytest -m heavy_test`. pytest.ini
    leaves it out of normal runs, so the suite stays offline.

    Calls Alpaca live for the exact same window as the recording (1Day,
    2024-01-16 to 2026-01-13, limit 1000). First checks both have the
    same tickers, then compares each ticker's DataFrame with the saved one.

    This is separate from the golden master: the golden master checks my
    code, this checks Alpaca's data.

    If it fails, Alpaca changed something, not my code. Re-run
    record_ohlcv_pickle.py, then delete results.txt so the golden master
    saves a new one.
    """

    dictionary_data_frames = dl.hist_data(
        selected_tickers,
        timeframe="1Day",
        start="2024-01-16",
        end="2026-01-13",
        limit=1000,
    )

    target_dir = os.path.dirname(__file__)

    file_name = "golden_masters/ohlcv.pkl"

    full_path = os.path.join(target_dir, file_name)

    with open(full_path, "rb") as file:
        loaded_ohlcv_data_frames = pickle.load(file)

        main.ExecutionState.backtest_run_number = 0

        assert dictionary_data_frames.keys() == loaded_ohlcv_data_frames.keys()

        for ticker in dictionary_data_frames:
            pd.testing.assert_frame_equal(
                dictionary_data_frames[ticker], loaded_ohlcv_data_frames[ticker]
            )
