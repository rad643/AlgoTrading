

---

# AlgoTrading Backtesting Engine

A Python-based algorithmic trading backtesting engine that simulates trading strategies under realistic execution conditions and evaluates performance using industry-standard metrics.

---

## Overview

This project implements a backtesting engine designed to model real trading behavior, including execution delays and market frictions.

It supports:

* Strategy-based signal generation (Trend Following & Mean Reversion)
* Next-bar execution (signal at close → execute at next open)
* Transaction costs (commission per share)
* Slippage modeling (fixed basis points)
* Position sizing based on available capital
* Performance evaluation using pandas

---

## Features

### Strategies

* **Trend Following**

  * Buy when price > average
  * Sell when price < average

* **Mean Reversion**

  * Trade based on deviation from average price

---

### Execution Model

* Signals generated at **closing price**
* Trades executed at **next day’s opening price**
* Includes:

  * Slippage: **0.05% fixed bias**
  * Commission: **$0.005 per share**

---

### Portfolio Mechanics

* Position sizing: **20% of available cash**
* Supports **multiple shares**
* Equity:

  * `equity = cash + position × closingPrice`
* Profit:

  * **Realized only on SELL**

---

### Data Handling

* CSV data loaded via generator
* Moving average computed incrementally
* Daily state processed via execution engine


---

### Performance Metrics (Step 9)

Implemented using **pandas (vectorized)**:

* Maximum Drawdown (MDD)
* Sharpe Ratio
* Expectancy
* Payoff Ratio
* Profit Factor

Metrics operate on:

* Equity curve (daily values)
* Trade P&L statistics

Example:

```python
equities = pd.Series(listStoreEquityValues)
returns = equities.pct_change()
```

Core implementation:


---

## Example Output

The engine prints daily trading state:

* Date
* Closing price
* Moving average
* Signal (BUY / SELL / HOLD)
* Execution price (on trade days)
* Position size
* Cash
* Equity
* Realized P&L

Example:

```
Day 4 | Date: 2024-01-19 | Close: 190.417 | Execution price: 188.295 | Avg: 183.876 | Trend: BUY | Position: 10.0 | Cash: 8117.0 | Equity: 10021.17
```

---

## Project Structure

```
project/
│
├── main.py
├── data_loader.py
├── compute_average.py
├── process_1_day.py
├── trend_signal.py
├── mean_rev_signal.py
├── performanceMetrics.py
│
├── data/
│   └── 5_day_input.csv
│
├── tests/
│   ├── test_data_loader.py
│   ├── test_compute_average.py
│   ├── test_process_1_day.py
│   ├── test_trend_signal.py
│   ├── test_mean_rev_signal.py
│   ├── test_execution_per_day.py
│   └── test_performanceMetrics.py
```

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pandas
```

---

## Running Tests

```bash
PYTHONPATH=. pytest -q tests/
```

---

## Current Status

* Completed up to **Step 9**
* Includes:

  * Realistic execution model
  * Position sizing (>1 share)
  * Full unit test coverage
  * Performance metrics using pandas

---

## Next Steps

* Step 10: Parameter configuration & experiments
* Step 11: NumPy vectorization
* Step 12+: Engine architecture & scaling

---
