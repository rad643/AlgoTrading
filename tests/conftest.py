from datetime import date

import pandas as pd
import pytest

import main


@pytest.fixture()
def results_data_frames() -> dict[str, pd.DataFrame]:
    """hand-built results_data_frames to pass in as an argument to AggregationLayer's object instantiation

    Returns:
        dict : the dictionary of final data frames coming out of ExperimentRunner
    """

    log_events_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

    equity_curve_df = pd.DataFrame({"col1": [5, 6], "col2": [7, 8]})

    drawdown_series_df = pd.DataFrame({"col1": [9, 10], "col2": [11, 12]})

    trades_df = pd.DataFrame({"col1": [13, 14], "col2": [15, 16]})

    prices_df = pd.DataFrame({"col1": [17, 18], "col2": [19, 20]})

    final_run_df = pd.DataFrame({"col1": [21, 22], "col2": [23, 24]})

    results_data_frames = {
        "Final Data Frame Run": final_run_df,
        "Equity Curve": equity_curve_df,
        "Drawdown Series": drawdown_series_df,
        "Completed Trades": trades_df,
        "Log Events": log_events_df,
        "Prices": prices_df,
    }

    return results_data_frames


@pytest.fixture()
def state_backtest_run():
    """hand-built ExecutionState with all of its lists filled in, so the tests don't run against empty ones.

    Sets the class level backtest_run_number to 0 before the test and puts it back to 0 after, so it doesn't leak into the golden master test.

    Yields:
        main.ExecutionState : the state object to pass into the functions under test
    """

    state = main.ExecutionState(
        trendMethod=True, symbol="GOOGL", cashValue=10000, ticker_name="Google"
    )

    main.ExecutionState.backtest_run_number = 0

    state.list_dictionaries_prices = [
        {
            "day": 1,
            "date": date(2024, 1, 1),
            "ticker": "Google",
            "strategy": "Trend",
            "closing_price": 101.18,
            "average": None,
        },
        {
            "day": 2,
            "date": date(2024, 1, 2),
            "ticker": "Google",
            "strategy": "Trend",
            "closing_price": 106.40,
            "average": None,
        },
        {
            "day": 3,
            "date": date(2024, 1, 3),
            "ticker": "Google",
            "strategy": "Trend",
            "closing_price": 101.43,
            "average": 103.00,
        },
    ]

    state.list_dictionaries_event_logs = [
        {
            "day": 56,
            "date": date(2025, 3, 25),
            "ticker": "Google",
            "strategy": "Trend",
            "closing_price": 234.18,
            "average": 254.65,
        },
        {
            "day": 57,
            "date": date(2025, 3, 26),
            "ticker": "Google",
            "strategy": "Trend",
            "closing_price": 267.40,
            "average": 236.12,
        },
        {
            "day": 58,
            "date": date(2025, 3, 27),
            "ticker": "Google",
            "strategy": "Trend",
            "closing_price": 262.65,
            "average": 298.00,
        },
    ]

    state.list_dictionaries_completed_trades = [
        {
            "run_number": 1,
            "ticker": "Google",
            "strategy": "Trend",
            "entry_day": 12,
            "entry_price": 98.400,
            "exit_day": 19,
            "exit_price": 105.720,
            "profit": 73.200,
            "return_pct": 7.44,
            "labels": "Google-Trend",
        },
        {
            "run_number": 1,
            "ticker": "Google",
            "strategy": "Trend",
            "entry_day": 31,
            "entry_price": 110.050,
            "exit_day": 38,
            "exit_price": 103.900,
            "profit": -61.500,
            "return_pct": -5.59,
            "labels": "Google-Trend",
        },
    ]

    state.listStoreEquityValues = [
        10000.0,
        10240.5,
        10105.2,
        9870.8,
        10310.4,
        10520.9,
        10180.3,
        9950.6,
    ]

    yield state

    main.ExecutionState.backtest_run_number = 0
