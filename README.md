# Algorithmic Trading Backtesting Platform

An ongoing Python project for retrieving historical US equity data, running rule-based backtests, evaluating strategy performance, visualising results, and exposing backtest data through a FastAPI/PostgreSQL backend.

The project started as a small CSV-based backtesting script and has since been refactored into a modular application with a reusable trading engine, structured outputs, an aggregation layer, interactive Plotly charts, live historical data retrieval through the Alpaca Market Data API, and an asynchronous database/API layer.

> **Project status:** active development. The standalone backtesting engine and data pipeline are implemented. The FastAPI/PostgreSQL integration and test-suite refactor are still in progress.

## Main Features

- Historical OHLCV data retrieval from the Alpaca Market Data REST API
- Trend Following and Mean Reversion strategies
- Signal generation at market close with execution at the following bar's open
- Multi-share position sizing using 20% of available starting capital
- Fixed slippage and per-share commission modelling
- Daily cash, position and equity tracking
- Completed-trade and event-log generation
- Performance metrics calculated with pandas
- Multi-ticker and multi-strategy experiment runner
- Structured outputs designed for use by a UI or API
- Interactive Plotly visualisations
- FastAPI backend with asynchronous PostgreSQL persistence
- SQLModel database models and service-based CRUD operations

## Strategies

### Trend Following

- Generates a **BUY** signal when the closing price is above the cumulative moving average.
- Generates a **SELL** signal when the closing price is below the cumulative moving average.

### Mean Reversion

- Generates a **BUY** signal when the closing price is below the cumulative moving average.
- Generates a **SELL** signal when the closing price is above the cumulative moving average.

The cumulative moving average uses all available closing prices before the current signal decision.

## Execution Model

The engine models several practical execution constraints:

- A signal is generated from the current bar's close.
- The order is executed at the next bar's open.
- Buy fills include positive slippage.
- Sell fills include negative slippage.
- Default slippage is `0.05%` of the opening price.
- Default commission is `$0.005` per share on both entry and exit.
- Each position is sized using `20%` of the starting cash allocation.
- A sell closes the full position.
- Equity is marked to market each day using the current closing price.

## Architecture

### `ExecutionState`

`ExecutionState` is a dataclass containing the configuration and mutable state for one backtest run, including:

- ticker symbol and display name
- selected strategy
- starting and current cash
- current position
- entry and exit information
- pending signal
- realised profit
- trade counters
- daily equity values

Its `reset()` method allows the same state object to be reused safely for another run.

### `TradingEngine`

`TradingEngine` operates on an `ExecutionState` and a pandas DataFrame of market data. A completed run produces structured DataFrames for:

- run summary
- equity curve
- drawdown series
- completed trades
- event logs
- price and moving-average data

### `ExperimentRunner`

`ExperimentRunner` retrieves Alpaca data for Apple, Google and Microsoft and runs both strategies for each symbol. It then combines the individual results into consolidated DataFrames.

### `AggregationLayer`

The aggregation layer produces UI-oriented summaries such as:

- total number of runs
- best-performing run
- worst-performing run
- average metrics across all runs
- a selected ticker/strategy summary
- the completed trades for a selected run

### `PlottingLayer`

The Plotly layer creates interactive visualisations for:

- equity curves
- drawdown series
- completed trades
- log events
- run summaries
- price charts with strategy information

## Performance Metrics

The engine currently calculates:

| Metric | Description |
|---|---|
| Total net profit | Sum of realised trade profits after the modelled execution process |
| Maximum drawdown | Largest percentage decline from a previous equity peak |
| Expectancy | Expected profit or loss per completed trade |
| Payoff ratio | Average winning trade divided by average losing trade |
| Profit factor | Gross profit divided by gross loss |
| Sharpe ratio | Mean daily equity return divided by its sample standard deviation, using a zero risk-free rate |

Metrics that cannot be calculated because a run contains no winning trades, no losing trades or no return variation are represented as `NaN`.

## Market Data

Historical bars are downloaded directly from Alpaca using `requests`.

`data_loading/data_loader.py`:

1. sends a request to Alpaca's historical bars endpoint;
2. follows pagination tokens when more data is available;
3. converts the returned bars into pandas DataFrames;
4. renames abbreviated API fields to readable OHLCV column names;
5. converts timestamps to the `America/New_York` timezone; and
6. returns one DataFrame per requested ticker.

The previous Yahoo Finance/CSV workflow has been removed. CSV-dependent tests are being replaced to reflect the current API-based architecture.

## Backend API

The backend uses:

- FastAPI
- SQLModel
- SQLAlchemy asynchronous sessions
- `asyncpg`
- PostgreSQL
- Pydantic Settings

The application creates its database tables during FastAPI startup.

### Database Tables

- `summary` — one performance summary per backtest run
- `trades` — completed trades
- `log_events` — backtest lifecycle, execution and trade events

### Implemented Routes

| Method | Route | Purpose |
|---|---|---|
| POST | `/run_backtest` | Run a backtest and persist its outputs |
| GET | `/summary/{backtest_run_number}` | Retrieve one run summary |
| DELETE | `/summary/{backtest_run_number}` | Delete one run summary |
| GET | `/trade_id/{id}` | Retrieve a trade by database ID |
| GET | `/trades_backtest_run_number/{backtest_run_number}` | Retrieve all trades from one run |
| DELETE | `/trade_id/{id}` | Delete a trade by database ID |
| DELETE | `/trades_backtest_run_number/{backtest_run_number}` | Delete all trades from one run |
| GET | `/log_event_id/{id}` | Retrieve a log event by database ID |
| GET | `/log_events_backtest_run_number/{backtest_run_number}` | Retrieve all log events from one run |
| DELETE | `/log_event_id/{id}` | Delete a log event by database ID |
| DELETE | `/log_events_backtest_run_number/{backtest_run_number}` | Delete all log events from one run |

> The API layer is still being aligned with the newer Alpaca DataFrame-based engine interface. The read/delete service routes and asynchronous database architecture are implemented, while the end-to-end `/run_backtest` flow is currently being refactored.

## Project Structure

```text
AlgoTrading/
├── api/
│   ├── api.py                     # FastAPI application and lifespan handler
│   ├── config.py                  # PostgreSQL settings
│   ├── database/
│   │   ├── models.py              # SQLModel table models
│   │   └── session.py             # Async engine and session dependency
│   ├── router/
│   │   ├── dependencies.py        # FastAPI dependencies
│   │   ├── router_backtest.py
│   │   ├── router_log_events.py
│   │   ├── router_summary.py
│   │   ├── router_trades.py
│   │   └── services/              # Async database service classes
│   └── schemas/
│       └── schemas.py             # Request schemas
├── data_loading/
│   ├── compute_average.py         # NumPy cumulative-average calculation
│   └── data_loader.py             # Alpaca REST data retrieval and DataFrame preparation
├── engine/
│   └── process_1_day.py           # Routes one day to the selected strategy
├── metrics/
│   └── performanceMetrics.py      # Backtest performance metrics
├── strategies/
│   ├── trend/                     # Trend strategy logic
│   └── mean_reversion/            # Mean-reversion strategy logic
├── tests/                         # Unit tests; currently being updated
├── legacy/                        # Earlier SQLite/API implementation retained for reference
├── main.py                        # Engine, experiment runner, aggregation and plotting layers
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

### 3. Install the current dependencies

The repository does not yet include a final pinned requirements file. Install the packages currently used by the project:

```bash
pip install pandas numpy requests plotly fastapi uvicorn sqlmodel sqlalchemy asyncpg pydantic-settings rich pytest
```

## Configuration

### Alpaca credentials

Create a root-level `.env` file containing valid Alpaca Market Data credentials in JSON format:

```json
{
  "APCA-API-KEY-ID": "YOUR_KEY_ID",
  "APCA-API-SECRET-KEY": "YOUR_SECRET_KEY"
}
```

The file is excluded by `.gitignore`. Never commit real credentials.

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

Run commands from the repository root so the configuration files can be found correctly:

```bash
python main.py
```

The current experiment runner:

- downloads daily Alpaca bars for `AAPL`, `GOOGL` and `MSFT`;
- runs Trend and Mean Reversion configurations for each ticker;
- builds six backtest summaries; and
- generates structured outputs and Plotly charts.

## Running the API

Ensure PostgreSQL is running and `api/.env` is configured, then start FastAPI:

```bash
uvicorn api.api:app --reload
```

Interactive API documentation is available through FastAPI's `/docs` route while the development server is running.

## Tests

Run the suite with:

```bash
python -m pytest tests/ -v
```

Refactored `main.TradingEngine.backtest_run()` into small helper functions to make it unit-testable; used a golden master test to make sure the output after the refactoring stayed identical to the output before it.

Ran the pre-refactor version from the last GitHub commit to generate results_old.txt, then used a diff command to compare it against the results.txt produced by the refactored code. Both files came back identical, which confirmed the refactoring hadn't changed any output; After that, every time I refactor something in main.py I just run the characterization test again. If it comes out green, the changes I made haven't changed the output. 

Once the refactoring is complete and the new unit tests for the helper functions are green, the characterization test can be deleted — the unit tests now cover the individual pieces, so the golden master isn't needed as a safety net anymore.

`test_main.py` currently covers the extracted wiring and accessor helpers, plus the golden master (characterization) test over the full backtest pipeline. Remaining work:

- mock Alpaca HTTP responses so tests run without network access;
- extend unit coverage to the log-event helpers and the remaining `backtest_run()` logic; and
- add API/database integration tests.

The existing suite passes; coverage of the remaining engine logic and the API layer is still to come.

## Development Roadmap

### Completed or substantially implemented

- Core single-position backtesting loop
- Trade logging and state refactoring
- Cash and equity tracking
- Multi-share position sizing
- Slippage, commissions and next-bar execution
- Performance metrics
- Parameter experiments
- Partial NumPy/pandas vectorisation
- Modular engine architecture
- Structured DataFrame outputs
- Plotly visualisation layer
- UI-oriented aggregation layer
- Alpaca historical market-data integration
- FastAPI application structure
- SQLModel database models
- Asynchronous PostgreSQL sessions
- Summary, trade and log-event service routes

### Current work

- Complete the API wrapper around the updated engine
- Align the request schema with symbol-based Alpaca data retrieval
- Refactor and extend the test suite
- Improve error handling and configuration loading
- Add a pinned dependency file

### Planned work

- Final frontend/UI integration
- End-to-end API tests
- Deployment
- Additional strategies and configurable parameters
- Broader ticker and portfolio support

## Disclaimer

This project is for educational and software-development purposes. It does not provide financial advice, and its simulated results should not be interpreted as evidence of future trading performance.
