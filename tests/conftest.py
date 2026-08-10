from datetime import date

import pytest
import main

@pytest.fixture()
def state():

    state = main.ExecutionState(
                    
            trendMethod=True,
            symbol='GOOGL',
            cashValue= 10000,
            ticker_name = 'Google'
    
    )

    state.list_dictionaries_prices = [
        {'day': 1, 'date': date(2024,1,1), 'ticker': 'Google', 'strategy': 'Trend', 'closing_price': 101.18, 'average': None},
        {'day': 2, 'date': date(2024,1,2), 'ticker': 'Google', 'strategy': 'Trend', 'closing_price': 106.40, 'average': None},
        {'day': 3, 'date': date(2024,1,3), 'ticker': 'Google', 'strategy': 'Trend', 'closing_price': 101.43, 'average': 103.00},
    ]

    state.list_dictionaries_event_logs = [
        {'day': 56, 'date': date(2025,3,25), 'ticker': 'Google', 'strategy': 'Trend', 'closing_price': 234.18, 'average': 254.65},
        {'day': 57, 'date': date(2025,3,26), 'ticker': 'Google', 'strategy': 'Trend', 'closing_price': 267.40, 'average': 236.12},
        {'day': 58, 'date': date(2025,3,27), 'ticker': 'Google', 'strategy': 'Trend', 'closing_price': 262.65, 'average': 298.00},
    ]

    state.list_dictionaries_completed_trades = [
        {'run_number': 1, 'ticker': 'Google', 'strategy': 'Trend', 'entry_day': 12, 'entry_price': 98.400, 'exit_day': 19, 'exit_price': 105.720, 'profit': 73.200, 'return_pct': 7.44, 'labels': 'Google-Trend'},
        {'run_number': 1, 'ticker': 'Google', 'strategy': 'Trend', 'entry_day': 31, 'entry_price': 110.050, 'exit_day': 38, 'exit_price': 103.900, 'profit': -61.500, 'return_pct': -5.59, 'labels': 'Google-Trend'},
    ]

    state.listStoreEquityValues = [10000.0, 10240.5, 10105.2, 9870.8, 10310.4, 10520.9, 10180.3, 9950.6]

    return state


@pytest.fixture()
def state_backtest_run():

    state = main.ExecutionState(
                        
                trendMethod=True,
                symbol='GOOGL',
                cashValue= 10000,
                ticker_name = 'Google'
        
    )

    main.ExecutionState.backtest_run_number = 0

    yield state

    main.ExecutionState.backtest_run_number = 0

