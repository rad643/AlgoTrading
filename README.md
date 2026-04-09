# AlgoTrading Backtesting Engine

A Python-based algorithmic trading backtesting engine that simulates trading strategies on historical market data with realistic execution assumptions.

---

## Overview

This project implements a backtesting engine designed to model how trading strategies behave under more realistic market conditions.

It supports:

* Strategy-based signal generation (Trend Following & Mean Reversion)
* Next-bar execution (signals generated at close, executed at next open)
* Transaction costs (commission per share)
* Slippage modeling (fixed basis points)
* Position sizing based on available capital

The goal is to move beyond naive backtesting and incorporate key market frictions that affect real-world performance.

---

## Features

* **Trend Strategy**

  * Generates buy/sell signals based on price vs moving average

* **Mean Reversion Strategy**

  * Trades based on deviations from average price

* **Position Sizing**

  * Allocates 20% of available cash per trade

* **Execution Model**

  * Signals generated at closing price
  * Trades executed at next day’s opening price

* **Slippage Model**

  * Fixed bias (0.05%) applied to execution price

* **Commission Model**

  * Flat fee per share traded

* **Equity Tracking**

  * Tracks daily equity (cash + unrealized position value)

* **Realized Profit Tracking**

  * Profit is realized only on full position exit (SELL)

* **Unit Tested**

  * Core modules fully tested (data loading, signals, execution logic, engine)

---

## Example Output

The engine prints daily state transitions including:

* Date
* Closing price
* Moving average
* Signal (BUY / SELL / HOLD)
* Position size
* Cash balance
* Equity value
* Execution price (on trade days)
* Realized P&L (on SELL)

---

## Project Structure

project/
│
├── main.py
├── data_loader.py
├── compute_average.py
├── process_1_day.py
├── trend_signal.py
├── mean_rev_signal.py
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
│   └── test_execution_per_day.py

---

## Setup

### 1. Create virtual environment

```bash
python3 -m venv .venv
```

### 2. Activate environment

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install pytest
```

---

## Running Tests

From project root:

```bash
PYTHONPATH=. pytest tests/
```

or (quiet mode):

```bash
PYTHONPATH=. pytest -q tests/
```

---

## Current Status

* Completed up to **Step 8**
* Includes realistic execution model (next-bar execution, slippage, commissions)
* Full unit test coverage for core logic

---

## Next Step

Step 9: Performance Metrics (using pandas)
