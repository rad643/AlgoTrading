import os
import pickle
from pathlib import Path
from unittest.mock import patch

import main
from main import selected_tickers


def test_golden_master_backtest_run():
    """
    Runs the whole backtest on recorded bars and checks the output hasn't changed.

    fetch_bars_by_symbol is patched to return the bars saved in
    golden_masters/ohlcv.pkl, so nothing calls Alpaca and the input is
    the same on every run.

    The run counter is set back to 0 first, so run numbers always start
    at 1, whatever tests ran before this one.

    Both file paths are built from this file's own folder, so it works
    no matter which folder I run pytest from.

    Every DataFrame is turned into CSV text. First run: results.txt
    doesn't exist yet, so it gets written and nothing is asserted.
    Every run after that: the new output has to match results.txt exactly.

    If they stop matching, my refactoring changed something.
    Delete results.txt only on purpose, to save a new one.
    """

    with patch.object(
        main.ExperimentRunner, "fetch_bars_by_symbol"
    ) as mock_bars_by_symbol:
        target_dir = os.path.dirname(__file__)

        file_name = "golden_masters/ohlcv.pkl"

        full_path = os.path.join(target_dir, file_name)

        with open(full_path, "rb") as file:
            loaded_ohlcv_data_frames = pickle.load(file)

            mock_bars_by_symbol.return_value = loaded_ohlcv_data_frames

            golden_file_path = Path(f"{target_dir}/golden_masters/results.txt")

            main.ExecutionState.backtest_run_number = 0

            d = main.ExperimentRunner.structured_data_outputs(selected_tickers)

            results = "\n".join(
                f"=== {k} ===\n{v.to_csv(index=False)}" for k, v in d.items()
            )

            if not golden_file_path.exists():
                golden_file_path.parent.mkdir(parents=True, exist_ok=True)

                golden_file_path.write_text(results)
                return

            assert results == golden_file_path.read_text()
