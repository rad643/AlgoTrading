# Algorithmic Trading Backtesting Platform

A Python algorithmic-trading and backtesting platform for retrieving historical US equity data, running rule-based strategies, modelling execution costs, evaluating performance, visualising results, and persisting backtest outputs through a FastAPI/PostgreSQL API.

The project began as a small CSV-based backtester and has been progressively refactored into a modular application with a reusable trading engine, structured pandas outputs, aggregation and plotting layers, Alpaca market-data integration, asynchronous database persistence, automated tests, static analysis, and continuous integration on GitHub Actions.

> **Status:** active development. The standalone backtesting pipeline, Alpaca data integration, FastAPI/PostgreSQL persistence layer with Alembic schema migrations, and CI quality checks are implemented. The test suite is complete across every module, API layer included — **217 tests passing**, plus one opt-in live-data check — and CI runs it in full, offline. React dashboard is live with 3 charts and a performance statistics panel implemented, before proceeding onto deployment.

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
- Interactive Plotly visualisations
- FastAPI backend
- SQLModel models with asynchronous PostgreSQL sessions
- Read/delete API routes for summaries, trades, log events, equities, drawdowns, and prices 
- End-to-end `/run_backtest` route that runs a backtest and persists its outputs
- Pytest + `unittest.mock` test coverage of every module, including the API layer and an offline golden-master regression test
- Request validation: `/run_backtest` rejects a reversed date window with a 422 or when alpaca returns no bars 
- Async API tests against an in-memory SQLite database via FastAPI dependency overrides
- Ruff linting and formatting checks
- Mypy static type checking
- Pre-commit quality checks
- GitHub Actions continuous integration
- Alembic schema migrations
- React dashboard
- Slippage, commission and position sizing are now configurable from the API and dashboard.

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
- No pyramiding: a buy signal while a position is open is ignored; a sell liquidates the full position.
- Equity is marked to market using the current closing price.

## Architecture

### `ExecutionState`

`ExecutionState` is the dataclass that owns the configuration and mutable state for a single backtest run. It stores information such as:

- ticker;
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

The full query-parameter and response-code reference for this endpoint, plus what the
project actually sends, is in `CLAUDE.md` under "Alpaca historical bars reference".

## Backend API

The backend stack currently uses:

- FastAPI
- SQLModel
- SQLAlchemy asynchronous sessions
- `asyncpg`
- PostgreSQL
- Pydantic Settings

The database schema is managed by Alembic (`migrations/`), not created at application startup. See "Database Migrations" below.

### Database Tables

- `summary` — one performance summary per backtest run
- `trades` — completed trades, with commission and slippage cost per trade
- `log_events` — execution and backtest lifecycle events
- `equities` — daily marked-to-market equity per run
- `drawdowns` — daily drawdown from the running equity peak per run
- `prices` — daily closing price and running average per run

A run is identified by `summary.id`, the database-assigned primary key. All five child tables carry a
`run_number` column declared as a foreign key to `summary.id`, so every child row is tied to the
summary of the run that produced it.

### Implemented Routes

| Method | Route | Purpose |
|---|---|---|
| POST | `/run_backtest` | Run a backtest and persist its summary, trades, log events, equities, drawdowns, and prices |
| GET | `/summary/{id}` | Retrieve one run summary |
| DELETE | `/summary/{id}` | Delete one run summary |
| GET | `/trade_id/{id}` | Retrieve a trade by database ID |
| GET | `/trades_backtest_run_number/{backtest_run_number}` | Retrieve all trades for one run |
| DELETE | `/trade_id/{id}` | Delete a trade by database ID |
| DELETE | `/trades_backtest_run_number/{backtest_run_number}` | Delete all trades for one run |
| GET | `/log_event_id/{id}` | Retrieve a log event by database ID |
| GET | `/log_events_backtest_run_number/{backtest_run_number}` | Retrieve all log events for one run |
| DELETE | `/log_event_id/{id}` | Delete a log event by database ID |
| DELETE | `/log_events_backtest_run_number/{backtest_run_number}` | Delete all log events for one run |
| GET | `/equity_id/{id}` | Retrieve a daily equity row by database ID |
| GET | `/equities_backtest_run_number/{backtest_run_number}` | Retrieve the equity curve for one run, ordered by day |
| DELETE | `/equity_id/{id}` | Delete a daily equity row by database ID |
| DELETE | `/equities_backtest_run_number/{backtest_run_number}` | Delete the equity curve for one run |
| GET | `/drawdown_id/{id}` | Retrieve a drawdown row by database ID |
| GET | `/drawdowns_backtest_run_number/{backtest_run_number}` | Retrieve the drawdown series for one run, ordered by day |
| DELETE | `/drawdown_id/{id}` | Delete a drawdown row by database ID |
| DELETE | `/drawdowns_backtest_run_number/{backtest_run_number}` | Delete the drawdown series for one run |
| GET | `/price_id/{id}` | Retrieve a price row by database ID |
| GET | `/prices_backtest_run_number/{backtest_run_number}` | Retrieve the closing prices and running average for one run, ordered by day |
| DELETE | `/price_id/{id}` | Delete a price row by database ID |
| DELETE | `/prices_backtest_run_number/{backtest_run_number}` | Delete the price series for one run |
| GET | `/final_equity/{id}`, `/total_net_profit/{id}`, `/return_pct/{id}`, `/annualized_pct/{id}`, `/sharpe_ratio/{id}`, `/maximum_drawdown/{id}`, `/calmar_ratio/{id}`, `/total_trades/{id}`, `/winning_trades/{id}`, `/losing_trades/{id}`, `/win_rate/{id}`, `/profit_factor/{id}`, `/expectancy/{id}`, `/average_win/{id}`, `/average_loss/{id}`, `/payoff_ratio/{id}`, `/starting_cash/{id}`, `/total_commission/{id}`, `/total_slippage_cost/{id}` | One performance statistic for one run, computed from the database |

The current `/run_backtest` route builds an `ExecutionState` from the request body, fetches Alpaca data for the request's `timeframe`, `start`, `end` and `limit` (defaults `1Day`, `2024-01-16`, `2026-01-13`, `1000`; a `start` after `end` is rejected with a 422), executes the trading engine, calculates the run summary, and persists the summary, trades, log events, equities, drawdowns, and prices to PostgreSQL.

The summary is inserted first so that PostgreSQL assigns its `id`. That id is then written onto every
trade, log event, equity, drawdown, and price row before they are inserted, which is what keeps the foreign keys pointing at the
correct run. The engine's own in-process run counter is a local label for the standalone runner and
is never used as a database key.

## Project Structure

```text
AlgoTrading/
├── .github/
│   └── workflows/
│       └── ci.yaml                # GitHub Actions pipeline
├── api/
│   ├── main.py                    # FastAPI application and CORS
│   ├── config.py                  # PostgreSQL settings
│   ├── database/
│   │   ├── models.py              # SQLModel tables
│   │   └── session.py             # Async engine/session dependency
│   ├── router/
│   │   ├── dependencies.py        # FastAPI dependencies
│   │   ├── router_backtest.py
│   │   ├── router_drawdowns.py
│   │   ├── router_equities.py
│   │   ├── router_log_events.py
│   │   ├── router_prices.py
│   │   ├── router_statistics.py
│   │   ├── router_summary.py
│   │   ├── router_trades.py
│   │   └── services/              # Async database service classes
│   └── schemas/
│       └── schemas.py             # Pydantic request models
├── dashboard/                     # Vite + React frontend
│   └── src/
│       ├── Dashboard.jsx          # Page layout, state, API fetches
│       ├── BacktestParameters.jsx # Parameter panel, POSTs /run_backtest
│       ├── Summary.jsx            # Runs table with ticker filter
│       ├── LogEvents.jsx          # Log events of the selected run
│       ├── Trades.jsx             # Trades of the selected run
│       ├── PriceChart.jsx         # Close, running average and buy/sell markers
│       ├── EquityCurve.jsx        # Equity curve of the selected run
│       ├── DrawdownSeriesChart.jsx # Drawdown % of the selected run
│       ├── PerformanceStatistics.jsx # Statistics panel of the selected run
│       └── index.css              # Dark theme, table and chart layout
├── data_loading/
│   ├── compute_average.py         # Cumulative-average calculation
│   └── data_loader.py             # Alpaca data retrieval/preparation
├── engine/
│   └── process_1_day.py           # Routes one day through the chosen strategy
├── legacy/                        # Earlier implementation retained for reference
├── metrics/
│   └── performance_metrics.py     # Performance-metric functions
├── migrations/
│   ├── env.py                     # Alembic environment, reads the URL from api.config
│   └── versions/                  # Migration scripts
├── strategies/
│   ├── mean_reversion/
│   └── trend/
├── tests/
│   ├── api/
│   │   ├── conftest.py            # In-memory SQLite session fixture
│   │   └── test_*.py              # 94 tests across 13 files
│   ├── golden_masters/
│   │   ├── ohlcv.pkl              # Recorded Alpaca bars, the golden master's input
│   │   ├── record_ohlcv_pickle.py # Re-records ohlcv.pkl (one live call)
│   │   └── results.txt            # Golden-master expected output
│   ├── conftest.py
│   └── test_*.py                  # 123 tests across 10 files, plus 1 opt-in live test
├── .pre-commit-config.yaml        # Local quality hooks
├── alembic.ini                    # Alembic config (URL is set in migrations/env.py)
├── conftest.py                    # Empty; marks the rootdir for pytest
├── main.py                        # Engine, aggregation, plotting, experiment runner
├── mypy.ini
├── pytest.ini                     # Registers heavy_test and deselects it by default
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

The GitHub Actions pipeline uses Python `3.13`.

## Configuration

### Alpaca credentials

Create a root-level `.env` file:

```env
APCA_API_KEY_ID=YOUR_KEY_ID
APCA_API_SECRET_KEY=YOUR_SECRET_KEY
```

`data_loader.py` reads these environment variables and maps them to Alpaca's required HTTP header names internally.

The `.env` file is excluded by `.gitignore`. Never commit API credentials.

No test in the default run calls Alpaca, so the credentials are only needed for the standalone
runner, the API, and the opt-in `pytest -m heavy_test` check. CI still has them, stored as GitHub repository secrets and injected as job-level `env` in `.github/workflows/ci.yaml`
under these names:

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

`api/config.py` instantiates its `Settings` object at import time, so these five values must be
resolvable before anything under `api/` can be imported — including by the test suite. Pydantic
Settings accepts plain environment variables as well as the file, which is how CI supplies dummy
values without an `api/.env`.

### Database Migrations

Schema changes are applied with Alembic, so a model change no longer means dropping tables and
losing their rows. `SQLModel.metadata.create_all` only creates missing tables and never alters an
existing one, which is why it was replaced.

- `migrations/env.py` reads the database URL from `api.config.settings`, so no credentials are
  stored in `alembic.ini`.
- `env.py` imports `api.database.models` only to register the tables on `SQLModel.metadata`, which
  autogenerate compares against the live database. The import is marked `# noqa: F401` so Ruff
  does not remove it.
- `migrations/script.py.mako` imports `sqlmodel`, because autogenerate writes `str` columns as
  `sqlmodel.sql.sqltypes.AutoString()`.
- The initial revision, `74bc25b2f973`, creates `summary`, `log_events`, `trades`, `equities`, `drawdowns` and `prices` from
  `models.py`, so `alembic upgrade head` builds the full schema on an empty database.

```bash
alembic revision --autogenerate -m "describe the change"   # generate a migration from models.py
alembic upgrade head                                       # apply pending migrations
alembic current                                            # revision the database is at
alembic check                                              # fails if models.py and the database differ
```

Always read the generated file in `migrations/versions/` before running `alembic upgrade head`.

To wipe all backtest rows and reset `summary.id` back to 1 (tables and schema are kept):

```bash
psql -U postgres -d algo_trading_dev -c "TRUNCATE TABLE log_events, summary, trades RESTART IDENTITY CASCADE;"
```

This is destructive and irreversible. Replace `algo_trading_dev` with your `POSTGRES_DB`.

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

## React Dashboard

`dashboard/` is a Vite + React app that runs backtests through the API and displays the stored
results. It calls the API at `http://localhost:8000`; the API's CORS settings allow
`http://localhost:5173`, Vite's default dev address.

- Parameter panel: ticker, strategy, starting cash, slippage, commission and position size, posted
  to `/run_backtest`
- Summary table of runs, filterable by ticker, with green/red net profit
- Clicking a run loads its log events, trades, equity curve, drawdown series and prices
- Price chart: closing price, running average, and buy/sell markers at each trade's entry and exit
- Equity-curve chart of the selected run
- Drawdown chart (% below the running peak) of the selected run
- Performance statistics panel of the selected run
- Dark theme, right-aligned tabular numbers, profit/loss colouring

With the API running:

```bash
cd dashboard
npm install
npm run dev
```

## Testing

Run the full local test directory with:

```bash
pytest -v tests/
```

The suite currently gives **217 passed, 1 deselected**, and covers every module in the project. The
deselected test is the opt-in live Alpaca check described below.

Engine, strategy, and data layers — 123 tests:

| File | Tests | Area under test |
|---|---|---|
| `tests/test_main.py` | 61 | `ExecutionState`, `TradingEngine` helpers, DataFrame builders, aggregation layer, experiment runner |
| `tests/test_performance_metrics.py` | 29 | Performance-metric functions |
| `tests/test_data_loader.py` | 8 | Alpaca retrieval, pagination, and DataFrame preparation |
| `tests/test_compute_average.py` | 5 | Cumulative moving average |
| `tests/test_trend_utils.py` | 5 | Trend buy/sell/hold execution and validation |
| `tests/test_mean_reversion_utils.py` | 5 | Mean Reversion buy/sell/hold execution and validation |
| `tests/test_process_1_day.py` | 3 | Per-day strategy routing and input validation |
| `tests/test_trend_signal.py` | 3 | Trend signal step |
| `tests/test_mean_reversion_signal.py` | 3 | Mean Reversion signal step |
| `tests/test_golden_master.py` | 1 | Full pipeline output against `results.txt` |

API layer — 94 tests, all offline:

| File | Tests | Area under test |
|---|---|---|
| `tests/api/test_log_events_service.py` | 8 | `LogEventsService` against a real session |
| `tests/api/test_router_log_events.py` | 8 | Log-event routes with a faked service |
| `tests/api/test_trades_service.py` | 8 | `TradesService` against a real session |
| `tests/api/test_router_trades.py` | 8 | Trade routes with a faked service |
| `tests/api/test_equities_service.py` | 8 | `EquitiesService` against a real session |
| `tests/api/test_router_equities.py` | 8 | Equity routes with a faked service |
| `tests/api/test_drawdown_service.py` | 8 | `DrawdownsService` against a real session |
| `tests/api/test_router_drawdown.py` | 8 | Drawdown routes with a faked service |
| `tests/api/test_prices_service.py` | 8 | `PricesService` against a real session |
| `tests/api/test_router_prices.py` | 8 | Price routes with a faked service |
| `tests/api/test_router_backtest.py` | 6 | `/run_backtest` end to end, run-identity wiring, reversed-window and empty-bars 422 |
| `tests/api/test_summary_service.py` | 4 | `SummaryService` primary-key lookups |
| `tests/api/test_router_summary.py` | 4 | Summary routes with a faked service |

Three testing styles are used, one per layer. The **signal** tests patch `buy`, `sell` and `hold` with `unittest.mock` autospecs and assert branch routing, the exact argument mapping, and the returned tuple. The **utils** tests mock nothing and assert the real execution arithmetic — slippage-adjusted fill price, share count, cash after commission, marked-to-market equity, realised profit — plus the verbose console output through pytest's `capsys` fixture. The **API** tests run against an in-memory SQLite database: route tests swap the service dependency for a fake, while service and end-to-end tests use a real async session created through `app.dependency_overrides`. Async tests run on the `anyio` plugin and are marked with `@pytest.mark.anyio`; `pytest-asyncio` is not used.

CI runs the whole directory with per-package coverage:

```bash
pytest -v --cov=main --cov=engine --cov=strategies --cov=data_loading --cov=metrics --cov=api tests/
```

### Golden-master regression test

The full backtest pipeline also has a golden-master test. It stores a known-good serialized output and compares future runs against it so structural refactoring can be checked for unintended behavioural changes.

The golden-master path is:

```text
tests/golden_masters/results.txt
```

The test runs offline: Alpaca is patched out and the bars come from `tests/golden_masters/ohlcv.pkl`, recorded once with:

```bash
python -m tests.golden_masters.record_ohlcv_pickle
```

A separate opt-in test checks that Alpaca still returns those same bars. It is marked `heavy_test`, which `pytest.ini` deselects by default:

```bash
pytest -m heavy_test
```

If it fails, Alpaca's data changed, not the code: re-record `ohlcv.pkl`, then delete `results.txt` and run the golden master once to save a new one.

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

One pipeline is active, running these stages:

1. checkout;
2. create a virtual environment and install `requirements.txt`;
3. `ruff check`;
4. `ruff format --check`;
5. `mypy`;
6. `pytest` over the full `tests/` directory with per-package coverage.

| Pipeline | File | Python | Trigger |
|---|---|---|---|
| GitHub Actions | `.github/workflows/ci.yaml` | `3.13` | push to `main` |

A CircleCI pipeline previously ran the same stages on Python `3.12.7`; it was removed and
`.circleci/config.yml` no longer exists.

Alongside the Alpaca secrets, the workflow sets dummy `POSTGRES_*` environment variables so that
`api/` can be imported in CI without an `api/.env` file.

Coverage is requested one package at a time (`main`, `engine`, `strategies`, `data_loading`, `metrics`, `api`) so that the retained `legacy/` directory stays out of the report.

The pipeline is passing all of these stages.

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
- Read/delete services for summaries, trades, log events, equities, drawdowns and prices
- Refactored `TradingEngine` helpers with unit tests
- Complete unit coverage of both strategy packages — signal routing and execution arithmetic
- Offline golden-master regression coverage, plus an opt-in live check of the recorded bars
- Backtest date window and bar limit configurable per request through `BacktestConfig`, with start/end validation
- Batched persistence in `/run_backtest` — two commits per run instead of one per row
- Database-assigned run identity, with `summary.id` as the foreign key on trades and log events
- Full API test suite — routes with faked services, services against a real async session, and an end-to-end `/run_backtest` test
- Test database/session dependency overrides against in-memory SQLite
- Pinned dependency file
- Ruff linting/formatting
- Mypy type checking
- Pre-commit hooks
- GitHub Actions pipeline running the full test suite
- Alembic schema migrations
- React dashboard — parameter panel, run summaries, log events and trades per run, prices, equities and drawdowns charts, performance statistics panel

### Current work

- Further API/database cleanup
- Removing the date window still hard-coded in the standalone runner (`ExperimentRunner.fetch_bars_by_symbol`)

### Planned

- Dockerised application/deployment
- Broader CI/CD workflow
- Live Alpaca websocket market-data integration
- Paper-trading support
- Additional strategies and broader ticker support

## Disclaimer

This project is for educational and software-development purposes only. It does not provide financial advice, and simulated backtest results should not be interpreted as evidence of future trading performance.
