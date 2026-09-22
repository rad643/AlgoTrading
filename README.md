# Algorithmic Trading Backtesting Platform

A Python algorithmic-trading and backtesting platform for retrieving historical US equity data, running rule-based strategies, modelling execution costs, evaluating performance, visualising results, and persisting backtest outputs through a FastAPI/PostgreSQL API.

The project began as a small CSV-based backtester and has been progressively refactored into a modular application with a reusable trading engine, structured pandas outputs, aggregation and plotting layers, Alpaca market-data integration, asynchronous database persistence, automated tests, static analysis, and continuous integration on both GitHub Actions and CircleCI.

> **Status:** active development. The standalone backtesting pipeline, Alpaca data integration, FastAPI/PostgreSQL persistence layer, and CI quality checks are implemented. The test suite covering every non-API module is complete — **123 tests, all passing** — and both CI pipelines now run it in full. Current work is focused on API testing and further backend cleanup before building the frontend and deployment layers.

## Features

- Historical OHLCV market data from the Alpaca Market Data REST API
- Trend Following and Mean Reversion strategies
- Signal generation at market close with execution at the next bar's open
- Multi-share position sizing
- Slippage and per-share commission modelling
- Daily cash, position, and marked-to-market equity tracking
- Completed-trade and event-log generation
- Performance metrics including Sharpe ratio and maximum drawdown
- Multi-ticker / multi-strategy experiment runner
- Structured pandas DataFrame outputs for downstream API/UI use
- Aggregated summaries for comparing backtest runs
- Interactive Plotly visualisations
- FastAPI backend
- SQLModel models with asynchronous PostgreSQL sessions
- Read/delete API routes for summaries, trades, and log events
- End-to-end `/run_backtest` route that runs a backtest and persists its outputs
- Pytest + `unittest.mock` test coverage of every non-API module, including a golden-master regression test
- Ruff linting and formatting checks
- Mypy static type checking
- Pre-commit quality checks
- GitHub Actions and CircleCI continuous integration

## Strategies

### Trend Following

The Trend strategy:

- generates **BUY** when the closing price is above the cumulative moving average;
- generates **SELL** when the closing price is below the cumulative moving average.

### Mean Reversion

The Mean Reversion strategy:

- generates **BUY** when the closing price is below the cumulative moving average;
- generates **SELL** when the closing price is above the cumulative moving average.

The cumulative moving average is calculated from the closing prices available before the current signal decision.

## Execution Model

The engine models several execution constraints rather than assuming fills occur at the signal price:

- Signals are generated from the current bar's close.
- Orders execute at the following bar's open.
- Buy fills receive positive slippage.
- Sell fills receive negative slippage.
- Default slippage: `0.05%` (`0.0005`).
- Default commission: `$0.005` per share on entry and exit.
- Position sizing defaults to `20%` of available starting capital.
- No pyramiding is used; a sell liquidates the full position.
- Equity is marked to market using the current closing price.

## Architecture

### `ExecutionState`

`ExecutionState` is the dataclass that owns the configuration and mutable state for a single backtest run. It stores information such as:

- ticker and company name;
- strategy selection;
- starting/current cash;
- current position;
- entry and exit information;
- pending action;
- realised P&L;
- trade counters;
- daily equity values;
- execution-cost settings.

Its `reset()` method restores the state for reuse.

### `TradingEngine`

`TradingEngine` contains the core backtesting workflow. The original monolithic backtest logic has been decomposed into smaller helpers so the behaviour can be tested independently.

The main flow includes:

1. iterating through market data;
2. generating strategy decisions;
3. executing pending trades on the next bar;
4. updating portfolio state;
5. recording prices, trades, and lifecycle events;
6. calculating equity and drawdown data; and
7. producing structured DataFrames.

A completed run produces structured outputs for:

- run summary;
- equity curve;
- drawdown series;
- completed trades;
- event logs;
- price / moving-average data.

### `ExperimentRunner`

`ExperimentRunner` coordinates multiple runs across symbols and strategies.

Its main responsibilities are:

- `fetch_bars_by_symbol()` — fetch Alpaca bars once for a comma-separated ticker selection;
- `state()` — build an `ExecutionState` for one symbol/strategy combination;
- `structured_data_outputs()` — execute both strategies for every selected symbol and concatenate their outputs;
- `build_results()` — expose the resulting DataFrames through a labelled dictionary.

The current standalone experiment selection is:

```text
AAPL, GOOGL, MSFT
```

with both Trend Following and Mean Reversion run for each symbol.

### `AggregationLayer`

The aggregation layer converts the raw run outputs into UI-oriented summaries, including:

- total number of runs;
- per-run summaries;
- best-performing run;
- worst-performing run;
- average performance across runs;
- selected ticker/strategy summary;
- selected-run trade list.

### `PlottingLayer`

The Plotly layer creates interactive visualisations from the structured outputs, including equity, drawdown, trade, run-summary, and price/strategy views.

## Performance Metrics

| Metric | Description |
|---|---|
| Total net profit | Final marked-to-market equity minus starting cash, including realised and unrealised P&L after execution costs |
| Maximum drawdown | Largest percentage decline from a previous equity peak |
| Expectancy | Expected profit or loss per completed trade |
| Payoff ratio | Average winning trade divided by average losing trade |
| Profit factor | Gross profit divided by gross loss |
| Sharpe ratio | Mean daily equity return divided by its sample standard deviation, using a zero risk-free rate |

Metrics that cannot be calculated for a particular run are represented as `NaN`.

## Market Data

Historical market data is retrieved from Alpaca with `requests` in `data_loading/data_loader.py`.

The loader:

1. authenticates with Alpaca API credentials from environment variables;
2. requests historical bars for one or more symbols;
3. follows pagination tokens until all requested data is collected;
4. converts the returned bars into pandas DataFrames;
5. renames Alpaca's abbreviated fields to readable OHLCV column names;
6. converts timestamps to the `America/New_York` timezone; and
7. returns a dictionary mapping each symbol to its DataFrame.

## Backend API

The backend stack currently uses:

- FastAPI
- SQLModel
- SQLAlchemy asynchronous sessions
- `asyncpg`
- PostgreSQL
- Pydantic Settings

Database tables are created during the FastAPI lifespan startup handler.

### Database Tables

- `summary` — one performance summary per backtest run
- `trades` — completed trades
- `log_events` — execution and backtest lifecycle events

### Implemented Routes

| Method | Route | Purpose |
|---|---|---|
| POST | `/run_backtest` | Run a backtest and persist its summary, trades, and log events |
| GET | `/summary/{backtest_run_number}` | Retrieve one run summary |
| DELETE | `/summary/{backtest_run_number}` | Delete one run summary |
| GET | `/trade_id/{id}` | Retrieve a trade by database ID |
| GET | `/trades_backtest_run_number/{backtest_run_number}` | Retrieve all trades for one run |
| DELETE | `/trade_id/{id}` | Delete a trade by database ID |
| DELETE | `/trades_backtest_run_number/{backtest_run_number}` | Delete all trades for one run |
| GET | `/log_event_id/{id}` | Retrieve a log event by database ID |
| GET | `/log_events_backtest_run_number/{backtest_run_number}` | Retrieve all log events for one run |
| DELETE | `/log_event_id/{id}` | Delete a log event by database ID |
| DELETE | `/log_events_backtest_run_number/{backtest_run_number}` | Delete all log events for one run |

The current `/run_backtest` route builds an `ExecutionState` from the request body, fetches Alpaca data, executes the trading engine, calculates the run summary, and persists the summary, trades, and log events to PostgreSQL.

## Project Structure

```text
AlgoTrading/
├── .circleci/
│   └── config.yml                 # CircleCI pipeline
├── .github/
│   └── workflows/
│       └── ci.yaml                # GitHub Actions pipeline
├── api/
│   ├── main.py                    # FastAPI application and lifespan handler
│   ├── config.py                  # PostgreSQL settings
│   ├── database/
│   │   ├── models.py              # SQLModel tables
│   │   └── session.py             # Async engine/session dependency
│   ├── router/
│   │   ├── dependencies.py        # FastAPI dependencies
│   │   ├── router_backtest.py
│   │   ├── router_log_events.py
│   │   ├── router_summary.py
│   │   ├── router_trades.py
│   │   └── services/              # Async database service classes
│   └── schemas/
│       └── schemas.py             # Pydantic request models
├── data_loading/
│   ├── compute_average.py         # Cumulative-average calculation
│   └── data_loader.py             # Alpaca data retrieval/preparation
├── engine/
│   └── process_1_day.py           # Routes one day through the chosen strategy
├── legacy/                        # Earlier implementation retained for reference
├── metrics/
│   └── performance_metrics.py     # Performance-metric functions
├── strategies/
│   ├── mean_reversion/
│   └── trend/
├── tests/
│   ├── golden_masters/
│   ├── conftest.py
│   └── test_*.py                  # 123 tests across 9 files
├── .pre-commit-config.yaml        # Local quality hooks
├── main.py                        # Engine, aggregation, plotting, experiment runner
├── mypy.ini
├── requirements.txt               # Pinned Python dependencies
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rad643/AlgoTrading.git
cd AlgoTrading
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

The GitHub Actions pipeline uses Python `3.13`; the CircleCI pipeline uses Python `3.12.7`.

## Configuration

### Alpaca credentials

Create a root-level `.env` file:

```env
APCA_API_KEY_ID=YOUR_KEY_ID
APCA_API_SECRET_KEY=YOUR_SECRET_KEY
```

`data_loader.py` reads these environment variables and maps them to Alpaca's required HTTP header names internally.

The `.env` file is excluded by `.gitignore`. Never commit API credentials.

Both CI pipelines need the same two credentials, because the golden-master test performs a live Alpaca fetch:

- **GitHub Actions** — repository secrets, injected as job-level `env` in `.github/workflows/ci.yaml`;
- **CircleCI** — project environment variables.

Use the same names in both:

```text
APCA_API_KEY_ID
APCA_API_SECRET_KEY
```

### PostgreSQL

Create `api/.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=algotrading
```

Create the matching PostgreSQL database before starting the API.

## Running the Standalone Backtest

From the repository root:

```bash
python main.py
```

The current standalone runner downloads Alpaca data for `AAPL,GOOGL,MSFT`, executes both strategies for each symbol, aggregates the results, and builds Plotly outputs.

## Running the API

Ensure PostgreSQL is running and both sets of environment variables are configured, then run:

```bash
uvicorn api.main:app --reload
```

FastAPI's interactive Swagger documentation is then available at:

```text
http://127.0.0.1:8000/docs
```

## Testing

Run the full local test directory with:

```bash
pytest -v tests/
```

The suite currently contains **123 tests, all passing**, and covers every module outside `api/`:

| File | Tests | Area under test |
|---|---|---|
| `tests/test_main.py` | 62 | `ExecutionState`, `TradingEngine` helpers, DataFrame builders, aggregation layer, experiment runner, golden master |
| `tests/test_performance_metrics.py` | 29 | Performance-metric functions |
| `tests/test_data_loader.py` | 8 | Alpaca retrieval, pagination, and DataFrame preparation |
| `tests/test_compute_average.py` | 5 | Cumulative moving average |
| `tests/test_trend_utils.py` | 5 | Trend buy/sell/hold execution and validation |
| `tests/test_mean_reversion_utils.py` | 5 | Mean Reversion buy/sell/hold execution and validation |
| `tests/test_process_1_day.py` | 3 | Per-day strategy routing and input validation |
| `tests/test_trend_signal.py` | 3 | Trend signal step |
| `tests/test_mean_reversion_signal.py` | 3 | Mean Reversion signal step |

The two strategy layers are tested in different styles. The signal tests patch `buy`, `sell` and `hold` with `unittest.mock` autospecs and assert branch routing, the exact argument mapping, and the returned tuple. The utils tests mock nothing and assert the real execution arithmetic — slippage-adjusted fill price, share count, cash after commission, marked-to-market equity, realised profit — plus the verbose console output through pytest's `capsys` fixture.

Both CI pipelines run the whole directory with per-package coverage:

```bash
pytest -v --cov=main --cov=engine --cov=strategies --cov=data_loading --cov=metrics tests/
```

### Golden-master regression test

The full backtest pipeline also has a golden-master test. It stores a known-good serialized output and compares future runs against it so structural refactoring can be checked for unintended behavioural changes.

The golden-master path is:

```text
tests/golden_masters/results.txt
```

Because this test currently performs live Alpaca data retrieval, Alpaca environment variables must also be available in CI. The remaining tests run offline.

## Code Quality and Continuous Integration

### Pre-commit

The repository includes local pre-commit hooks for:

- Ruff linting
- Ruff formatting checks
- Mypy type checking

Run them manually with:

```bash
pre-commit run --all-files
```

### Pipelines

Two pipelines are active, and both run the same stages:

1. checkout;
2. create a virtual environment and install `requirements.txt`;
3. `ruff check`;
4. `ruff format --check`;
5. `mypy`;
6. `pytest` over the full `tests/` directory with per-package coverage.

| Pipeline | File | Python | Trigger |
|---|---|---|---|
| GitHub Actions | `.github/workflows/ci.yaml` | `3.13` | push to `main` |
| CircleCI | `.circleci/config.yml` | `3.12.7` | project-configured builds |

Coverage is requested one package at a time (`main`, `engine`, `strategies`, `data_loading`, `metrics`) so that the not-yet-tested `api/` package and the retained `legacy/` directory stay out of the report.

Both pipelines are passing all of these stages.

## Current Development State

### Implemented

- Core backtesting loop
- Trend Following and Mean Reversion strategy execution
- Cash/equity accounting
- Multi-share position sizing
- Slippage and commissions
- Next-bar execution
- Trade/event logging
- Performance metrics
- Structured DataFrame outputs
- Multi-ticker experiment runner
- Aggregation layer
- Plotly visualisation layer
- Alpaca historical-market-data integration
- FastAPI routers and dependency injection
- SQLModel/PostgreSQL persistence with async sessions
- End-to-end `/run_backtest` persistence flow
- Read/delete services for summaries, trades, and log events
- Refactored `TradingEngine` helpers with unit tests
- Complete unit coverage of both strategy packages — signal routing and execution arithmetic
- Golden-master regression coverage
- Pinned dependency file
- Ruff linting/formatting
- Mypy type checking
- Pre-commit hooks
- GitHub Actions and CircleCI pipelines, both running the full test suite

### Current work

- API testing with FastAPI `TestClient`
- Test database/session dependency overrides
- Further API/database cleanup, including reducing per-row commit overhead
- Moving hard-coded backtest date configuration into the request/configuration layer

### Planned

- React frontend/dashboard
- Dockerised application/deployment
- Broader CI/CD workflow
- Live Alpaca websocket market-data integration
- Paper-trading support
- Additional strategies and broader ticker support

## Disclaimer

This project is for educational and software-development purposes only. It does not provide financial advice, and simulated backtest results should not be interpreted as evidence of future trading performance.
