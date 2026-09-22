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

# Tests
pytest -v tests/                                            # full suite (123 tests, all passing)
pytest tests/test_main.py                                   # one file (62 tests)
pytest tests/test_main.py::TestExecutionState::test_reset   # one test

# With coverage, exactly as both CI pipelines run it
pytest -v --cov=main --cov=engine --cov=strategies --cov=data_loading --cov=metrics tests/

# Quality gate — same checks both CI pipelines run
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

There are **two CI pipelines, both live**, running the same four stages — `ruff check`,
`ruff format --check`, `mypy`, then `pytest` over the whole `tests/` directory:

| Pipeline | File | Python | Trigger | Alpaca credentials |
|---|---|---|---|---|
| GitHub Actions | `.github/workflows/ci.yaml` | 3.13 | push to `main` only — not PRs, not other branches | repository secrets (added in f00a707) |
| CircleCI | `.circleci/config.yml` | 3.12.7 | project-configured builds | project environment variables |

Both run the full suite, so a failure anywhere in `tests/` breaks CI. `--cov` is passed once per
package (`main`, `engine`, `strategies`, `data_loading`, `metrics`) to keep `api/` and `legacy/`
out of the coverage report — a bare `--cov` would measure everything under the rootdir.

`ruff format` also formats Python code blocks inside Markdown, so `README.md` and this file are
subject to it — a misaligned `# comment` in a ```python block will fail the format check and block commits.

Ruff and mypy have no config beyond `mypy.ini` (`explicit_package_bases = True`); there is no
`pyproject.toml`.

They disagree about `legacy/`. Ruff's `respect-gitignore` defaults to true and its gitignore matcher
never consults the git index, so the `legacy/` entry in `.gitignore` takes that directory out of
`ruff check .` entirely (47 files seen, 0 of them in `legacy/`; `--no-respect-gitignore` pulls in
that directory's 5 modules plus other gitignored scratch files). Mypy has no such behaviour and
still type-checks all of it — `mypy . --exclude=.venv` reports 50 source files. So `legacy/` must
keep passing **mypy** but is no longer linted or format-checked.

## Environment

Two separate `.env` files, both gitignored:

- root `.env` — `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY` (Alpaca market data)
- `api/.env` — `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_DB`

`api/config.py` calls `Settings()` at module import, so **importing anything under `api/` fails
without `api/.env`**. Keep that in mind when adding API tests — the import blows up before any
fixture runs.

Tests that touch `ExperimentRunner.structured_data_outputs` or `hist_data` hit the live Alpaca
API and need the root `.env` plus network access.

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
incremented once per `backtest_run()`. It becomes the `run_number` column and the API's lookup key.
Tests must zero it before and after (see the `state_backtest_run` fixture in `tests/conftest.py`),
or run ordering leaks into the golden master.

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
not catch it and no unit test covers it. Keep those builders in sync with `api/database/models.py`.

The same applies to `ExecutionState(**config.model_dump())`: field names in
`api/schemas/schemas.py::BacktestConfig` must match `ExecutionState`'s constructor.

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

`pytest tests/` gives **123 passed, 0 failed**. The suite is complete: every module outside `api/`
has coverage, and both CI pipelines run all of it.

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

## Golden-master test

`tests/test_main.py::TestTradingEngineBacktestRun` serializes every output DataFrame to CSV and
compares it against `tests/golden_masters/results.txt` (~587 KB).

It runs a **live Alpaca fetch**, so it needs credentials and network. To regenerate after an
intentional behaviour change, delete `results.txt` and run the test once — it writes the file and
asserts nothing on that run. Never regenerate to make an unexplained diff go away; that is the only
thing guarding the refactors against silent behavioural drift.

## Known rough edges

Do not "fix" these incidentally — they are tracked work:

- The backtest date window `start="2024-01-16", end="2026-01-13"` is hard-coded in **two** places:
  `ExperimentRunner.fetch_bars_by_symbol()` and `router_backtest.py`. Moving it into config is planned.
- `/run_backtest` commits and refreshes **once per row** inside its loops. Batching is planned.
- Tradeable tickers are whitelisted in `COMPANY_NAMES` (`main.py`); `ExperimentRunner.state()`
  raises `ValueError` for anything else. Adding a ticker means adding it there.
- `legacy/` holds the earlier SQLite implementation, kept on disk for reference only. It is untracked
  and gitignored, and not imported by live code. Mypy still type-checks it, so it must keep passing
  `mypy .`; ruff skips it (see "Commands" above).
- `.venv/` was built at an older path and its scripts were repaired in place. If the project directory
  is ever renamed again, every console script in `.venv/bin/`, `.venv/pyvenv.cfg`, and
  `.git/hooks/pre-commit` will break with `bad interpreter`. Rebuild the venv, or rewrite those paths.
