---

# AlgoTrading Backtesting Engine

A Python-based algorithmic trading backtesting engine that simulates trading strategies under realistic execution conditions and evaluates performance using industry-standard metrics.

---

## Overview

This project implements a reusable backtesting engine built around a `dataclass`-based `Engine` class. It models real trading behavior including execution delays, market frictions, and position sizing, and runs experiments across multiple tickers and strategies in a single execution.

It supports:

* Strategy-based signal generation (Trend Following & Mean Reversion)
* Next-bar execution (signal at close → execute at next open)
* Transaction costs (commission per share)
* Slippage modeling (fixed basis points)
* Position sizing based on available capital
* Performance evaluation using pandas
* Multi-ticker, multi-strategy experiment runs
* Automated market data download via Yahoo Finance

---

## Features

### Strategies

* **Trend Following**
  * Buy when closing price > moving average
  * Sell when closing price < moving average

* **Mean Reversion**
  * Buy when closing price < moving average
  * Sell when closing price > moving average

---

### Execution Model

* Signals generated at **closing price**
* Trades executed at **next day's opening price**
* Slippage: **0.05% fixed bias** applied to execution price
* Commission: **$0.005 per share** (flat fee, charged on both buy and sell)

---

### Portfolio Mechanics

* Position sizing: **20% of available cash**
* Supports **multiple shares per trade**
* Equity tracked daily: `equity = cash + position × closingPrice`
* Profit realized only on full SELL

---

### Engine Architecture

The `Engine` dataclass in `main.py` encapsulates all backtest state and logic:

* `backtest_run()` — runs one complete backtest and returns a one-row DataFrame of results
* `reset()` — clears run-specific state so the same instance can be safely reused
* `Engine.backtest_run_number` — class-level counter tracking total runs across all instances

Each engine instance is configured at construction time with a ticker, strategy, and starting capital. Multiple instances can be run and their results combined with `pd.concat()`.

---

### Data Handling

* Historical OHLCV data loaded from CSV via a generator (`data_loader.py`)
* Moving average computed incrementally using all closing prices up to each day
* Daily state (position, cash, equity, profit, pending action) updated and yielded per day
* Yahoo Finance data downloaded and saved to CSV via `yahoo.py` (run separately before backtesting)

---

### Performance Metrics

Implemented using **pandas (vectorized)** in `performanceMetrics.py`:

| Metric | Description |
|---|---|
| Maximum Drawdown (MDD) | Largest peak-to-trough decline in equity, expressed as % |
| Sharpe Ratio | Risk-adjusted return: mean daily return / standard deviation |
| Expectancy | Average profit per trade across wins and losses |
| Payoff Ratio | Average win / average loss |
| Profit Factor | Gross profit / gross loss |

Metrics operate on the equity curve and trade P&L statistics collected during the backtest loop. If a strategy produces no losing trades (or no winning trades), trade-dependent metrics (Expectancy, Payoff Ratio, Profit Factor) are reported as `NaN`.

---

## Example Output

```
                        Ticker Strategy used  Starting cash  total net profit   MDD  Expectancy  Payoff Ratio  Profit Factor  Sharpe Ratio
backtest run number 1    Apple         Trend          10000           -51.491  8.04       -5.72          6.91           0.86         0.023
backtest run number 2    Apple Mean reversion         10000           361.240  2.64       40.14          0.82           6.60         0.035
backtest run number 3   Google         Trend          10000          -103.482  6.97       -8.62          1.44           0.72         0.086
backtest run number 4   Google Mean reversion         10000           386.496  2.34       32.21          1.59           7.95         0.043
backtest run number 5   Microsoft         Trend          10000          -410.960  5.30      -24.17          0.62           0.13        -0.021
backtest run number 6   Microsoft Mean reversion         10000           546.022  2.41         NaN           NaN            NaN         0.075
```

Daily verbose output (when `verbose_run=True`):

```
Day 4 | Date: 2024-01-19 | Close: 190.417 | Execution price: 188.295 | Avg: 183.876 | Trend: BUY | Position: 10.0 | Cash: 8117.0 | Equity: 10021.17
```

---

## Project Structure

```
project/
│
├── main.py                   # Engine dataclass + experiment runner
├── yahoo.py                  # Yahoo Finance data downloader (run separately)
├── data_loader.py            # CSV generator
├── compute_average.py        # Incremental moving average
├── process_1_day.py          # Strategy router (Trend vs Mean Reversion)
├── trend_signal.py           # Trend Following signal logic
├── mean_rev_signal.py        # Mean Reversion signal logic
├── performanceMetrics.py     # MDD, Sharpe, Expectancy, Payoff Ratio, Profit Factor
│
├── data/
│   ├── aapl_us_d.csv         # Apple historical OHLCV
│   ├── google.csv            # Google historical OHLCV (generated by yahoo.py)
│   ├── microsoft.csv         # Microsoft historical OHLCV (generated by yahoo.py)
│   └── 5_day_input.csv       # Minimal CSV used in unit tests
│
└── tests/
    ├── test_data_loader.py
    ├── test_compute_average.py
    ├── test_process_1_day.py
    ├── test_trend_signal.py
    ├── test_mean_rev_signal.py
    ├── test_execution_per_day.py
    └── test_performance_metrics.py
```

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pandas yfinance
```

---

## Downloading Market Data

Run this once before backtesting to fetch and save the latest CSV data:

```bash
python yahoo.py
```

This downloads GOOGL and MSFT data from Yahoo Finance and saves them to `data/google.csv` and `data/microsoft.csv`.

---

## Running the Backtest

```bash
python main.py
```

---

## Running Tests

```bash
PYTHONPATH=. pytest -q tests/
```

---

## Current Status

Completed up to **Step 10 — Parameter configuration & experiments**

* Reusable `Engine` dataclass with configurable ticker, strategy, and starting capital
* `reset()` method for clean reuse across multiple runs
* Class-level backtest run counter
* Multi-ticker experiments: Apple, Google, Microsoft
* Both strategies per ticker in a single run
* Results combined into a single DataFrame via `pd.concat()`
* Graceful `NaN` handling for metrics that cannot be computed (e.g. no losing trades)
* Full unit test coverage across all modules
* Automated Yahoo Finance data download

---

## Next Steps

* Step 11: NumPy vectorization
* Step 12: Full engine architecture & scaling
* Step 13: Plotting & visuals
* Step 14: Multiple tickers / portfolio support
* Step 15: Live data / API integration

---
