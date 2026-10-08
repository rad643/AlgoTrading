from unittest.mock import patch

import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from api.database.session import get_session
from api.main import app
from api.router import router_backtest
from api.router.services.log_events_service import LogEventsService
from api.router.services.summary_service import SummaryService
from api.router.services.trades_service import TradesService

ticker_df = {
    "AAPL": pd.DataFrame(
        {
            "open": [
                99.6,
                91.6,
                83.6,
                91.6,
                86.6,
                91.6,
                86.6,
                98.6,
                106.6,
                94.6,
                86.6,
                91.6,
            ],
            "high": [
                101.5,
                93.5,
                85.5,
                93.5,
                88.5,
                93.5,
                88.5,
                100.5,
                108.5,
                96.5,
                88.5,
                93.5,
            ],
            "low": [
                98.5,
                90.5,
                82.5,
                90.5,
                85.5,
                90.5,
                85.5,
                97.5,
                105.5,
                93.5,
                85.5,
                90.5,
            ],
            "close": [
                100.0,
                92.0,
                84.0,
                92.0,
                87.0,
                92.0,
                87.0,
                99.0,
                107.0,
                95.0,
                87.0,
                92.0,
            ],
            "volume": [40000000 + i * 100000 for i in range(12)],
        },
        index=pd.DatetimeIndex(
            pd.to_datetime([f"2025-03-{d:02d}T05:00:00Z" for d in range(3, 15)]),
            name="time",
        ).tz_convert("America/New_York"),
    )
}


@pytest.fixture
async def async_session():
    """Same in-memory database as conftest's fixture, but yields the maker too.
    This file needs a second session later in the test, and a new engine would be a
    different empty database, so the maker has to come out of here alongside the
    session. That's the only reason this file doesn't just use conftest's fixture.
    """
    url = "sqlite+aiosqlite://"
    connect_args = {"check_same_thread": False}
    async_engine = create_async_engine(
        url=url, echo=True, connect_args=connect_args, poolclass=StaticPool
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session, async_session


@pytest.fixture
async def async_client(async_session):
    """Gives each test an async client that talks to the app over the fake database.
    Swaps the app's get_session for one that returns the session from the fixture
    above, so the endpoints hit the fake database instead of the real one. The
    transport wires the client straight to the app, so nothing goes over the
    network, and the base url is just there to make paths like /summary/1 valid.
    The override is cleared once the test is done.
    """
    session, _ = async_session

    def get_fake_session():
        return session

    app.dependency_overrides[get_session] = get_fake_session

    transport = ASGITransport(app=app)
    base_url = "http://test"
    async with AsyncClient(transport=transport, base_url=base_url) as async_client:
        yield async_client

    app.dependency_overrides = {}


@pytest.mark.anyio
async def test_create_backtest_mean_reversion_branch(async_client, async_session):
    """Runs one backtest through the endpoint and checks everything it produced.
    hist_data is mocked so the engine runs on fixed prices instead of calling Alpaca,
    which is what makes the numbers below predictable. First half asserts every field
    of the summary, the last log event and the first trade that came back in the
    response.
    Second half proves the three tables actually persisted. The session the endpoint
    used keeps what it saved in its own cache, so reading through it could answer from
    memory without ever touching the database. That's why a second session is opened on
    the same engine: its cache is empty, so its reads have to go to the fake database,
    and matching values mean the rows are really there.
    """
    client = async_client
    _, session_maker = async_session

    with patch.object(router_backtest, "hist_data", autospec=True) as mock_ticker_df:
        mock_ticker_df.return_value = ticker_df

        config = {"symbol": "AAPL", "cashValue": 10000, "ticker_name": "Apple"}
        response = await client.post("/run_backtest", json=config)
        assert response.status_code == 200

        data = response.json()

        new_summary = data["summary"]
        assert new_summary["ticker"] == "Apple"
        assert new_summary["strategy"] == "Mean Reversion"
        assert new_summary["starting_cash"] == 10000
        assert new_summary["total_net_profit"] == 58.01
        assert new_summary["mdd"] == 1.14
        assert new_summary["expectancy"] == 25.55
        assert new_summary["payoff_ratio"] == 1.48
        assert new_summary["profit_factor"] == 1.48
        assert new_summary["sharpe_ratio"] == 0.072
        assert new_summary["labels"] == "Apple-Mean Reversion"
        assert new_summary["id"] is not None

        log_events_list_with_id = data["log_events"]
        assert len(log_events_list_with_id) == 9
        last_log_event = log_events_list_with_id[8]
        assert last_log_event["run_number"] == new_summary["id"]
        assert last_log_event["day"] == 12
        assert last_log_event["date"] == "2025-03-14"
        assert last_log_event["ticker"] == "Apple"
        assert last_log_event["strategy"] == "Mean Reversion"
        assert last_log_event["event_type"] == "BACKTEST_END"
        assert last_log_event["message"] == "Backtest has ended"
        assert last_log_event["cash"] == 8126.01
        assert last_log_event["equity"] == 10058.01
        assert last_log_event["position"] == 21
        assert last_log_event["execution_price"] is None
        assert last_log_event["pnl"] == 58.01
        assert last_log_event["labels"] == "Apple-Mean Reversion"
        assert last_log_event["id"] is not None
        assert all(log_event["id"] is not None for log_event in log_events_list_with_id)

        trades_list_with_id = data["trades"]
        assert len(trades_list_with_id) == 2
        first_trade = trades_list_with_id[0]
        assert first_trade["run_number"] == new_summary["id"]
        assert first_trade["ticker"] == "Apple"
        assert first_trade["strategy"] == "Mean Reversion"
        assert first_trade["entry_day"] == 4
        assert first_trade["entry_price"] == 91.646
        assert first_trade["exit_day"] == 7
        assert first_trade["exit_price"] == 86.557
        assert first_trade["profit"] == -106.869
        assert first_trade["return_pct"] == -5.55
        assert first_trade["labels"] == "Apple-Mean Reversion"
        assert first_trade["number_trades_took_place"] == 1
        assert all(trade["id"] is not None for trade in trades_list_with_id)

        mock_ticker_df.assert_called_once_with(
            "AAPL", timeframe="1Day", start="2024-01-16", end="2026-01-13", limit=1000
        )

        async with session_maker() as second_session:
            summary_service = SummaryService(second_session)
            result = await summary_service.read(new_summary["id"])
            result_dict = result.model_dump()
            assert result_dict == new_summary

            log_events_service = LogEventsService(second_session)
            result = await log_events_service.read_run_number(new_summary["id"])
            assert len(result) == len(log_events_list_with_id)
            log_event_4 = await log_events_service.read_id(4)
            assert log_event_4.model_dump(mode="json") == log_events_list_with_id[3]

            trades_service = TradesService(second_session)
            result = await trades_service.read_run_number(new_summary["id"])
            assert len(result) == len(trades_list_with_id)
            trade_2 = await trades_service.read_id(2)
            assert trade_2.model_dump(mode="json") == trades_list_with_id[1]

            mock_ticker_df.assert_called_once_with(
                "AAPL",
                timeframe="1Day",
                start="2024-01-16",
                end="2026-01-13",
                limit=1000,
            )


@pytest.mark.anyio
async def test_create_backtest_incomplete(async_client):

    client = async_client

    config = {"symbol": "AAPL", "cashValue": 10000}
    response = await client.post("/run_backtest", json=config)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_backtest_invalid(async_client):

    client = async_client

    config = {"symbol": "AAPL", "cashValue": 10000, "ticker_name": {"name": "Apple"}}
    response = await client.post("/run_backtest", json=config)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_backtest_trend_branch(async_client):

    client = async_client

    with patch.object(router_backtest, "hist_data", autospec=True) as mock_ticker_df:
        mock_ticker_df.return_value = ticker_df

        config = {
            "trendMethod": True,
            "symbol": "AAPL",
            "cashValue": 10000,
            "ticker_name": "Apple",
        }
        response = await client.post("/run_backtest", json=config)
        assert response.status_code == 200

        data = response.json()

        new_summary = data["summary"]
        assert new_summary["ticker"] == "Apple"
        assert new_summary["strategy"] == "Trend"
        assert new_summary["starting_cash"] == 10000
        assert new_summary["total_net_profit"] == 1.692
        assert new_summary["mdd"] == 3.5
        assert new_summary["expectancy"] == 1.05
        assert new_summary["payoff_ratio"] == 1.01
        assert new_summary["profit_factor"] == 1.01
        assert new_summary["sharpe_ratio"] == 0.007
        assert new_summary["labels"] == "Apple-Trend"
        assert new_summary["id"] is not None

        log_events_list_with_id = data["log_events"]
        assert all(
            log_event["run_number"] == new_summary["id"]
            for log_event in log_events_list_with_id
        )

        trades_list_with_id = data["trades"]
        assert all(
            trade["run_number"] == new_summary["id"] for trade in trades_list_with_id
        )

        mock_ticker_df.assert_called_once_with(
            "AAPL", timeframe="1Day", start="2024-01-16", end="2026-01-13", limit=1000
        )


@pytest.mark.anyio
async def test_reversed_window(async_client):

    client = async_client

    config = {
        "symbol": "AAPL",
        "cashValue": 100,
        "ticker_name": "Apple",
        "start": "2026-01-16",
    }
    response = await client.post("/run_backtest", json=config)
    assert response.status_code == 422
    api_error_message_body = response.json()["detail"][0]["msg"]
    assert api_error_message_body == "Value error, Start date must come before end"
