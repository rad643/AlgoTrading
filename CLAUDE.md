# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Verify before asserting

Never assert an old result. Re-run all the checks before writing a claim about current state —
re-verify anything time-sensitive at the moment of assertion, and always confirm by running the tools
first.

## Commands

Run everything from the repository root. The virtualenv is `.venv/`.

```bash
source .venv/bin/activate

# Standalone backtest (AAPL, GOOGL, MSFT x both strategies) + Plotly output
python main.py

# API
uvicorn api.main:app --reload         # docs at http://127.0.0.1:8000/docs

# Reset the dev database: wipes all rows, restarts summary.id at 1. Destructive — only when the user asks.
psql -U postgres -d algo_trading_dev -c "TRUNCATE TABLE log_events, summary, trades RESTART IDENTITY CASCADE;"

# Tests
pytest -v tests/                                            # full suite (167 tests, all passing)
pytest tests/api/                                           # API layer only (44 tests)
pytest tests/test_main.py                                   # one file (62 tests)
pytest tests/test_main.py::TestExecutionState::test_reset   # one test

# With coverage, exactly as CI runs it
pytest -v --cov=main --cov=engine --cov=strategies --cov=data_loading --cov=metrics --cov=api tests/

# Quality gate — same checks CI runs
ruff check . --exclude=.venv
ruff format --check . --exclude=.venv
mypy . --exclude=.venv
pre-commit run --all-files            # runs all three
```

Bare `pytest` is correct. The repo root used to contain an empty `__init__.py`, which made pytest treat
the root as a package and put its *parent* directory on `sys.path` instead of the root itself, so
`import main` in `tests/conftest.py` failed with `ModuleNotFoundError` and everything had to go through
`python -m pytest`. That file was deleted in 270ea64, so rootdir lands on `sys.path` normally and CI
runs bare `pytest` too. If you ever re-add an `__init__.py` at the root, this breaks again.

There *is* a tracked, deliberately **empty** `conftest.py` at the repo root. It holds no fixtures —
its only job is to mark the rootdir so pytest puts it on `sys.path`. Do not delete it, and do not
confuse it with the `__init__.py` above.

Async tests run on the **anyio** plugin bundled with `anyio==4.13.0`; `pytest-asyncio` is *not*
installed. There is no `anyio_backend` fixture anywhere, so the asyncio backend comes from anyio's
default — which is why test ids read `[asyncio]`. Every async test needs `@pytest.mark.anyio`.

There is **one CI pipeline**, running four stages — `ruff check`, `ruff format --check`, `mypy`,
then `pytest` over the whole `tests/` directory:

| Pipeline | File | Python | Trigger | Alpaca credentials |
|---|---|---|---|---|
| GitHub Actions | `.github/workflows/ci.yaml` | 3.13 | push to `main` only — not PRs, not other branches | repository secrets (added in f00a707) |

CircleCI used to be a second live pipeline; `.circleci/config.yml` was **deleted in d608322** and the
directory no longer exists. Ignore any older reference to it.

It runs the full suite, so a failure anywhere in `tests/` breaks CI. `--cov` is passed once per
package (`main`, `engine`, `strategies`, `data_loading`, `metrics`, `api`) to keep `legacy/` out of
the coverage report — a bare `--cov` would measure everything under the rootdir.

`ruff format` also formats Python code blocks inside Markdown, so `README.md` and this file are
subject to it — a misaligned `# comment` in a ```python block will fail the format check and block commits.

Ruff and mypy have no config beyond `mypy.ini` (`explicit_package_bases = True`); there is no
`pyproject.toml`.

They disagree about `legacy/`. Ruff's `respect-gitignore` defaults to true and its gitignore matcher
never consults the git index, so the `legacy/` entry in `.gitignore` takes that directory out of
`ruff check .` entirely (54 files seen, 0 of them in `legacy/`; `--no-respect-gitignore` pulls in
that directory's 5 modules plus other gitignored scratch files). Mypy has no such behaviour and
still type-checks all of it — `mypy . --exclude=.venv` reports 59 source files. So `legacy/` must
keep passing **mypy** but is no longer linted or format-checked.

## Environment

Two separate `.env` files, both gitignored:

- root `.env` — `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY` (Alpaca market data)
- `api/.env` — `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_DB`

`api/config.py` calls `Settings()` at module import, so **importing anything under `api/` fails
unless those five values are present**. Pydantic Settings reads real environment variables too, not
just the file — CI relies on exactly that, injecting dummy `POSTGRES_*` values as job-level `env` in
`ci.yaml` so `tests/api/` can import the app without an `api/.env`. Locally the file is the easy
route. Either way the import blows up before any fixture runs.

Tests that touch `ExperimentRunner.structured_data_outputs` or `hist_data` hit the live Alpaca
API and need the root `.env` plus network access.

## Alpaca historical bars reference

`data_loading/data_loader.py::hist_data()` calls one endpoint:

```
GET https://data.alpaca.markets/v2/stocks/bars
```

Auth: headers `APCA-API-KEY-ID` and `APCA-API-SECRET-KEY`, built by `get_headers()` from the
`APCA_API_KEY_ID` / `APCA_API_SECRET_KEY` env vars (root `.env`).

Results are sorted by symbol first, then by bar timestamp. With several symbols and a `limit`,
the first page may contain only one symbol; keep requesting with `next_page_token` until it is
`null`. `hist_data()` does this loop.

### Query params

| Param | Type | Required | Default | Notes |
|---|---|---|---|---|
| `symbols` | string | yes | — | Comma-separated, e.g. `AAPL,TSLA` |
| `timeframe` | string | yes | — | `[1-59]Min`/`T`, `[1-23]Hour`/`H`, `1Day`/`1D`, `1Week`/`1W`, `[1,2,3,4,6,12]Month`/`M` |
| `start` | date-time | no | start of current day (≥15 min ago without real-time access) | Inclusive. RFC-3339 or `YYYY-MM-DD` |
| `end` | date-time | no | now (or 15 min ago without real-time access) | Inclusive. RFC-3339 or `YYYY-MM-DD` |
| `limit` | int 1–10000 | no | `1000` | Max data points **per page**, counted across **all symbols**, not per symbol. May return fewer |
| `adjustment` | string | no | `raw` | `raw`, `split`, `dividend`, `spin-off`, `all`; combine with commas, e.g. `split,spin-off` |
| `asof` | `YYYY-MM-DD` | no | today | Resolves symbol name changes (FB → META on 2022-06-09). `-` skips mapping |
| `feed` | enum | no | `sip` | `sip` all US exchanges, `iex` Investors Exchange, `boats` Blue Ocean overnight, `otc` |
| `currency` | ISO 4217 | no | `USD` | |
| `page_token` | string | no | — | From the previous response's `next_page_token` |
| `sort` | enum | no | `asc` | `asc` or `desc` |

### Responses

| Code | Meaning |
|---|---|
| 200 | OK |
| 400 | A parameter is invalid; the body says which. **`start` after `end` is a 400** |
| 401 | Auth headers missing or invalid |
| 403 | Forbidden |
| 429 | Rate limit; check the `X-RateLimit-*` headers |
| 500 | Alpaca-side error; retry later |

### What this project sends

- `hist_data()` sends `symbols`, `timeframe`, `start`, `end`, `limit`, plus `page_token` when
  paging. Nothing else, so `adjustment`, `feed`, `asof`, `currency`, `sort` are all Alpaca defaults.
- `hist_data()`'s own defaults are `timeframe="15Min"`, `start=""`, `end=""`, `limit=1000`.
  `/run_backtest` overrides them from `BacktestConfig`: `1Day`, `2024-01-16`, `2026-01-13`, `1000`.
  The golden master and the API tests assume those four values.
- `raise_for_status()` turns any non-2xx into `requests.exceptions.HTTPError`, which is what the
  route currently surfaces as a 500.

Docs: https://docs.alpaca.markets/reference/stockbars

## Architecture

### One engine, two entry points

`main.py` (standalone `ExperimentRunner`) and `api/router/router_backtest.py` (`POST /run_backtest`)
both funnel into the same call: `TradingEngine.backtest_run(state, ticker_df)`. Any change to the
engine affects both paths.

### `ExecutionState` is the whole world

`ExecutionState` (dataclass, `main.py`) holds config *and* all mutable run state — cash, position,
entry/exit prices, trade counters, and the accumulating lists of dicts that later become DataFrames.

Every `TradingEngine` method is a `@staticmethod` taking `state` and **mutating it in place**;
nothing returns a new state. `backtest_run()` calls `state.reset()` first so one instance can be reused.

`backtest_run_number` is a **class variable**, not a field — a counter shared by every instance,
incremented once per `backtest_run()`. It becomes the `run_number` column in the log-event, trade,
equity-curve and drawdown frames. Tests must zero it before and after (see the `state_backtest_run`
fixture in `tests/conftest.py`), or run ordering leaks into the golden master.

It is **not** the API's lookup key. The counter is a process-local run *label* only: it resets to 0
on every restart, and the database issues its own identities. See "Run identity" below.

### The per-day loop

`dl.read_ticker_dataframe()` (`data_loading/data_loader.py`) is a generator yielding
`(day, date, closingPrice, average, nextDayOpeningPrice)`:

- **Days 1–2**: warm-up, `average` is `None` → `TradingEngine.run_days_one_and_two()`
- **Day 3+**: → `run_strategy_day()` → `engine/process_1_day.process_one_day()` → `trend_step` or
  `mean_rev_step`, chosen by `state.trendMethod`

Signals are computed from today's close; execution happens at the **next** bar's open. That one-day
offset is the core of the execution model — preserve it in any engine change.

### DataFrame columns are a runtime contract with the database

`router_backtest.py` constructs ORM rows by splatting DataFrame records:

```python
Summary(**summary_dict)  # from TradingEngine.performance_metrics_data_frame
LogEvent(**event)  # from build_log_events_data_frame
Trade(**event)  # from build_trades_data_frame
```

**Renaming or adding a column in `main.py` silently breaks `/run_backtest` at runtime** — mypy will
not catch it. `tests/api/test_router_backtest.py` now covers the happy path end to end, so a renamed
column will fail there, but keep those builders in sync with `api/database/models.py` regardless.

One column is no longer a pass-through: `router_backtest.py` overwrites `run_number` on every child
record with `new_summary.id` before the splat. See "Run identity" below.

The same applies to `ExecutionState(**config.model_dump())`: field names in
`api/schemas/schemas.py::BacktestConfig` must match `ExecutionState`'s constructor.

Note that `Summary(**summary_dict)` is *not* protected by this — SQLModel silently discards unknown
kwargs on `table=True` models. `Summary(run_number=1, ...)` raises nothing and sets nothing, so a
misspelled or removed field passes construction and only shows up as missing data later.

### Run identity

`summary.id` is the identity of a backtest run. `Summary` has **no** `run_number` column;
`LogEvent.run_number` and `Trade.run_number` are `Field(foreign_key="summary.id")`.

Two different things therefore produce run numbers, and they must not be confused:

| | Source | Lifetime |
|---|---|---|
| `ExecutionState.backtest_run_number` | Python class variable | resets to 0 each process |
| `summary.id` | Postgres sequence | persistent, never reused |

`main.py` stamps the counter into its frames, which is correct for the standalone runner and the
golden master. The API must **translate**: `router_backtest.py` inserts the `Summary`, commits and
refreshes so the database assigns `id`, then sets `event["run_number"] = new_summary.id` on each
child before constructing it. Writing the counter straight into the FK column is the bug this design
exists to prevent — it only looks correct on an empty database in a fresh process, and breaks on a
restart, after any `DELETE /summary/{id}`, or with more than one worker.

### Strategies are deliberate near-duplicates

`strategies/trend/` and `strategies/mean_reversion/` are copies of each other. The **only** logical
difference is the comparison direction in `pending_action_update()` (trend buys above the average,
mean reversion below); the rest differs just in variable naming (`positionTrend` vs
`positionMeanReversion`). A bug fixed in one almost certainly exists in the other — check both.

The tests mirror the packages the same way: `tests/test_trend_signal.py` ↔
`tests/test_mean_reversion_signal.py` and `tests/test_trend_utils.py` ↔
`tests/test_mean_reversion_utils.py` are the same tests with different mock values, and the only
inverted assertion is the `pending_action_update` direction. Fixing one strategy means updating its
mirrored test too.

Adding a strategy touches: a new `strategies/<name>/` package, a branch in
`engine/process_1_day.py`, new fields in `ExecutionState` **and** its `reset()`, and new branches in
the `TradingEngine` accessors (`strategy`, `labels`, `position`, `entry_price`, `exit_price`,
`profit`, and the `increment_*` counters).

The `*_step` signal functions take 18 positional arguments and return a 9-tuple. That tuple shape
is a contract spanning `process_1_day`, `main.py`, the signal tests, and the golden master — changing
it is a wide refactor, not a local edit.

### Naming convention is split

Engine and strategy code uses camelCase (`cashValue`, `entryPriceTrend`, `positionSizing`);
DataFrame columns and DB models use snake_case (`entry_price`, `run_number`, `total_net_profit`).
This is intentional at the boundary — match whichever convention the file you are editing already uses.

## Test suite

`pytest tests/` gives **167 passed, 0 failed** — 123 outside `api/` plus 44 in `tests/api/`. Every
module in the project now has coverage, and CI runs all of it.

| File | Tests | Covers |
|---|---|---|
| `tests/test_main.py` | 62 | `ExecutionState`, `TradingEngine` helpers, DataFrame builders, aggregation, `ExperimentRunner`, golden master |
| `tests/test_performance_metrics.py` | 29 | every function in `metrics/performance_metrics.py` |
| `tests/test_data_loader.py` | 8 | `read_ticker_dataframe` and the Alpaca request/pagination helpers |
| `tests/test_compute_average.py` | 5 | `averageUpToDay` |
| `tests/test_trend_utils.py` | 5 | `strategies/trend/utils.py` |
| `tests/test_mean_reversion_utils.py` | 5 | `strategies/mean_reversion/utils.py` |
| `tests/test_process_1_day.py` | 3 | `process_one_day` branch routing and its two type/value guards |
| `tests/test_trend_signal.py` | 3 | `trend_step` |
| `tests/test_mean_reversion_signal.py` | 3 | `mean_rev_step` |

API layer — `tests/api/`, all offline against in-memory SQLite:

| File | Tests | Covers |
|---|---|---|
| `tests/api/test_log_events_service.py` | 8 | `LogEventsService` against a real session |
| `tests/api/test_router_log_events.py` | 8 | log-event routes with a faked service |
| `tests/api/test_trades_service.py` | 8 | `TradesService` against a real session |
| `tests/api/test_router_trades.py` | 8 | trade routes with a faked service |
| `tests/api/test_router_backtest.py` | 4 | `/run_backtest` end to end, including run-identity wiring |
| `tests/api/test_summary_service.py` | 4 | `SummaryService` (`session.get(Summary, id)`) |
| `tests/api/test_router_summary.py` | 4 | summary routes with a faked service |

Two deliberately different testing styles, one per layer:

- **`test_*_signal.py` mock everything.** `buy`, `sell` and `hold` are patched with
  `patch.object(..., autospec=True)`, so these tests assert *routing*, not arithmetic: which helper
  a `(pending_action, position)` combination reaches, that the other two are never called, the exact
  positional mapping via `assert_called_once_with`, and the returned 9-tuple — including the
  pass-through slots the chosen branch never touches. All four routes into `hold` are covered
  (`"BUY"` with a position, `"SELL"` with none, `"HOLD"`, `""`), the last two tracked through
  `mock_hold.call_args_list`.
- **`test_*_utils.py` mock nothing.** They assert the real numbers — execution price with slippage,
  share count, cash after commission, marked-to-market equity, realized profit — then re-call with
  `verbose_run=True` and compare the printed line through `capsys`. Note the print ends with
  `\n\n\n`: the f-string's own newline plus `print("\n")`.

When writing an `expected` tuple for a signal test, remember the mocked helper's return **rebinds**
the caller's variables: `hold` returns `(position, cash, equity, pending_action)`, so slot 0 of the
mock return is what lands in the 9-tuple, not the `positionTrend` you passed in.

The golden master and the `ExperimentRunner` tests in `test_main.py` perform a live Alpaca fetch, so
a clean run needs the root `.env` and network access. Everything else runs offline.

### Two traps in `tests/api/`

Neither is visible from the code; both matter if you change these tests.

**SQLite does not enforce the foreign keys.** `tests/api/conftest.py` never issues
`PRAGMA foreign_keys=ON`, and SQLite defaults it off per connection. A `LogEvent` whose `run_number`
points at no summary row inserts without error. Postgres does enforce it. So a broken FK will pass
`tests/api/` and fail in production — the suite guards run identity through explicit assertions
(`run_number == new_summary["id"]`), not through the constraint.

**The run counter is not reset between these tests, only the database is.** Fixtures are
function-scoped, so every test builds a fresh in-memory database and its first summary gets `id=1`.
`ExecutionState.backtest_run_number` is a class variable and keeps climbing across the module:

```text
test_create_backtest_mean_reversion_branch: counter 0 -> 1   (stamps 1, summary.id 1 — they match)
test_create_backtest_trend_branch:          counter 1 -> 2   (stamps 2, summary.id 1 — they diverge)
```

That divergence is the whole reason the Trend branch carries the `run_number == summary["id"]`
assertions: it is the only test where the counter and the database id disagree, so it is the only one
that can actually catch a regression in the translation. Run that test **alone** and the counter
starts at 0, stamps 1, matches by coincidence, and passes even with the bug reintroduced.

## Golden-master test

`tests/test_main.py::TestTradingEngineBacktestRun` serializes every output DataFrame to CSV and
compares it against `tests/golden_masters/results.txt` (~573 KB).

It runs a **live Alpaca fetch**, so it needs credentials and network. To regenerate after an
intentional behaviour change, delete `results.txt` and run the test once — it writes the file and
asserts nothing on that run. Never regenerate to make an unexplained diff go away; that is the only
thing guarding the refactors against silent behavioural drift.

## Known rough edges

Do not "fix" these incidentally — they are tracked work:

- The backtest date window `start="2024-01-16", end="2026-01-13"` is hard-coded in **two** places:
  `ExperimentRunner.fetch_bars_by_symbol()` and `router_backtest.py`. Moving it into config is planned.
- `/run_backtest` commits and refreshes **once per row** inside its loops. Batching is planned. The
  summary's own commit must stay ahead of the loops, though — that is what assigns `summary.id`.
- **There is no migration tooling.** `api/database/session.py` only calls `SQLModel.metadata.create_all`,
  which creates missing tables and never `ALTER`s an existing one. Any model change therefore has no
  effect on a live database until those tables are dropped and recreated, which destroys their rows.
  Adding Alembic is the real fix.
- Tradeable tickers are whitelisted in `COMPANY_NAMES` (`main.py`); `ExperimentRunner.state()`
  raises `ValueError` for anything else. Adding a ticker means adding it there.
- **Route naming is now inconsistent.** The summary router moved to `/summary/{id}`, but the trades
  and log-events routers still read `/trades_backtest_run_number/{backtest_run_number}` and
  `/log_events_backtest_run_number/{backtest_run_number}`, with matching
  `read_run_number`/`delete_run_number` service methods. Those children do still have a `run_number`
  column, so the names are not *wrong* — but the same number is called `id` on one route and
  `backtest_run_number` on another, which is confusing in `/docs`.
- `legacy/` holds the earlier SQLite implementation, kept on disk for reference only. It is untracked
  and gitignored, and not imported by live code. Mypy still type-checks it, so it must keep passing
  `mypy .`; ruff skips it (see "Commands" above).
- `.venv/` was built at an older path and its scripts were repaired in place. If the project directory
  is ever renamed again, every console script in `.venv/bin/`, `.venv/pyvenv.cfg`, and
  `.git/hooks/pre-commit` will break with `bad interpreter`. Rebuild the venv, or rewrite those paths.
