from datetime import date

import pytest

from api.database.models import LogEvent
from api.router.services.log_events_service import LogEventsService


@pytest.mark.anyio
async def test_read_id(fake_session):

    log_event_1 = LogEvent(
        run_number=1,
        day=34,
        date=date(2025, 1, 12),
        ticker="Apple",
        strategy="Trend",
        event_type="BUY",
        message="A Buy has been executed",
        cash=1000,
        equity=1100,
        position=10,
        execution_price=321.56,
        pnl=45.7,
        labels="Apple-Trend",
    )

    log_event_2 = LogEvent(
        run_number=1,
        day=36,
        date=date(2025, 1, 13),
        ticker="Apple",
        strategy="Trend",
        event_type="SELL",
        message="A Sell has been executed",
        cash=1000,
        equity=1100,
        position=11,
        execution_price=341.56,
        pnl=40.7,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(log_event_1)
    async_session.add(log_event_2)
    await async_session.commit()

    events = LogEventsService(async_session)
    result = await events.read_id(1)
    assert result == log_event_1


@pytest.mark.anyio
async def test_read_bad_id(fake_session):

    log_event_1 = LogEvent(
        run_number=1,
        day=34,
        date=date(2025, 1, 12),
        ticker="Apple",
        strategy="Trend",
        event_type="BUY",
        message="A Buy has been executed",
        cash=1000,
        equity=1100,
        position=10,
        execution_price=321.56,
        pnl=45.7,
        labels="Apple-Trend",
    )

    log_event_2 = LogEvent(
        run_number=1,
        day=36,
        date=date(2025, 1, 13),
        ticker="Apple",
        strategy="Trend",
        event_type="SELL",
        message="A Sell has been executed",
        cash=1000,
        equity=1100,
        position=11,
        execution_price=341.56,
        pnl=40.7,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(log_event_1)
    async_session.add(log_event_2)
    await async_session.commit()

    events = LogEventsService(async_session)
    result = await events.read_id(3)
    assert result is None


@pytest.mark.anyio
async def test_read_run_number(fake_session):

    log_event_1 = LogEvent(
        run_number=1,
        day=34,
        date=date(2025, 1, 12),
        ticker="Apple",
        strategy="Trend",
        event_type="BUY",
        message="A Buy has been executed",
        cash=1000,
        equity=1100,
        position=10,
        execution_price=321.56,
        pnl=45.7,
        labels="Apple-Trend",
    )

    log_event_2 = LogEvent(
        run_number=1,
        day=36,
        date=date(2025, 1, 13),
        ticker="Apple",
        strategy="Trend",
        event_type="SELL",
        message="A Sell has been executed",
        cash=1000,
        equity=1100,
        position=11,
        execution_price=341.56,
        pnl=40.7,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(log_event_1)
    async_session.add(log_event_2)
    await async_session.commit()

    events = LogEventsService(async_session)
    result = await events.read_run_number(1)
    assert result == [log_event_1, log_event_2]


@pytest.mark.anyio
async def test_read_bad_run_number(fake_session):

    log_event_1 = LogEvent(
        run_number=1,
        day=34,
        date=date(2025, 1, 12),
        ticker="Apple",
        strategy="Trend",
        event_type="BUY",
        message="A Buy has been executed",
        cash=1000,
        equity=1100,
        position=10,
        execution_price=321.56,
        pnl=45.7,
        labels="Apple-Trend",
    )

    log_event_2 = LogEvent(
        run_number=1,
        day=36,
        date=date(2025, 1, 13),
        ticker="Apple",
        strategy="Trend",
        event_type="SELL",
        message="A Sell has been executed",
        cash=1000,
        equity=1100,
        position=11,
        execution_price=341.56,
        pnl=40.7,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(log_event_1)
    async_session.add(log_event_2)
    await async_session.commit()

    events = LogEventsService(async_session)
    result = await events.read_run_number(2)
    assert result == []


@pytest.mark.anyio
async def test_delete_id(fake_session):

    log_event_1 = LogEvent(
        run_number=1,
        day=34,
        date=date(2025, 1, 12),
        ticker="Apple",
        strategy="Trend",
        event_type="BUY",
        message="A Buy has been executed",
        cash=1000,
        equity=1100,
        position=10,
        execution_price=321.56,
        pnl=45.7,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(log_event_1)
    await async_session.commit()

    events = LogEventsService(async_session)
    result = await events.delete_id(1)
    assert result is True
    assert await events.read_id(1) is None


@pytest.mark.anyio
async def test_delete_bad_id(fake_session):

    log_event_1 = LogEvent(
        run_number=1,
        day=34,
        date=date(2025, 1, 12),
        ticker="Apple",
        strategy="Trend",
        event_type="BUY",
        message="A Buy has been executed",
        cash=1000,
        equity=1100,
        position=10,
        execution_price=321.56,
        pnl=45.7,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(log_event_1)
    await async_session.commit()

    events = LogEventsService(async_session)
    result = await events.delete_id(2)
    assert result is False


@pytest.mark.anyio
async def test_delete_run_number(fake_session):

    log_event_1 = LogEvent(
        run_number=1,
        day=34,
        date=date(2025, 1, 12),
        ticker="Apple",
        strategy="Trend",
        event_type="BUY",
        message="A Buy has been executed",
        cash=1000,
        equity=1100,
        position=10,
        execution_price=321.56,
        pnl=45.7,
        labels="Apple-Trend",
    )

    log_event_2 = LogEvent(
        run_number=1,
        day=36,
        date=date(2025, 1, 13),
        ticker="Apple",
        strategy="Trend",
        event_type="SELL",
        message="A Sell has been executed",
        cash=1000,
        equity=1100,
        position=11,
        execution_price=341.56,
        pnl=40.7,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(log_event_1)
    async_session.add(log_event_2)
    await async_session.commit()

    events = LogEventsService(async_session)
    result = await events.delete_run_number(1)
    assert result is True
    assert await events.read_run_number(1) == []


@pytest.mark.anyio
async def test_delete_bad_run_number(fake_session):

    log_event_1 = LogEvent(
        run_number=1,
        day=34,
        date=date(2025, 1, 12),
        ticker="Apple",
        strategy="Trend",
        event_type="BUY",
        message="A Buy has been executed",
        cash=1000,
        equity=1100,
        position=10,
        execution_price=321.56,
        pnl=45.7,
        labels="Apple-Trend",
    )

    log_event_2 = LogEvent(
        run_number=1,
        day=36,
        date=date(2025, 1, 13),
        ticker="Apple",
        strategy="Trend",
        event_type="SELL",
        message="A Sell has been executed",
        cash=1000,
        equity=1100,
        position=11,
        execution_price=341.56,
        pnl=40.7,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(log_event_1)
    async_session.add(log_event_2)
    await async_session.commit()

    events = LogEventsService(async_session)
    result = await events.delete_run_number(2)
    assert result is False
