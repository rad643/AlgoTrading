import pytest

from api.database.models import Trade
from api.router.services.trades_service import TradesService


@pytest.mark.anyio
async def test_read_id(fake_session):

    trade_1 = Trade(
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        entry_day=34,
        entry_price=321.45,
        exit_day=56,
        exit_price=365.67,
        profit=96.5,
        return_pct=23.4,
        labels="Google-Mean Reversion",
        number_trades_took_place=12,
    )

    trade_2 = Trade(
        run_number=1,
        ticker="Microsoft",
        strategy="Mean Reversion",
        entry_day=44,
        entry_price=361.45,
        exit_day=66,
        exit_price=395.67,
        profit=46.5,
        return_pct=13.4,
        labels="Microsoft-Mean Reversion",
        number_trades_took_place=9,
    )

    async_session = fake_session
    async_session.add(trade_1)
    async_session.add(trade_2)
    await async_session.commit()

    trades = TradesService(async_session)
    result = await trades.read_id(2)
    assert result == trade_2


@pytest.mark.anyio
async def test_read_bad_id(fake_session):

    trade_1 = Trade(
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        entry_day=34,
        entry_price=321.45,
        exit_day=56,
        exit_price=365.67,
        profit=96.5,
        return_pct=23.4,
        labels="Google-Mean Reversion",
        number_trades_took_place=12,
    )

    async_session = fake_session
    async_session.add(trade_1)
    await async_session.commit()

    trades = TradesService(async_session)
    result = await trades.read_id(2)
    assert result is None


@pytest.mark.anyio
async def test_read_run_number(fake_session):

    trade_1 = Trade(
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        entry_day=34,
        entry_price=321.45,
        exit_day=56,
        exit_price=365.67,
        profit=96.5,
        return_pct=23.4,
        labels="Google-Mean Reversion",
        number_trades_took_place=12,
    )

    trade_2 = Trade(
        run_number=1,
        ticker="Microsoft",
        strategy="Mean Reversion",
        entry_day=44,
        entry_price=361.45,
        exit_day=66,
        exit_price=395.67,
        profit=46.5,
        return_pct=13.4,
        labels="Microsoft-Mean Reversion",
        number_trades_took_place=9,
    )

    async_session = fake_session
    async_session.add(trade_1)
    async_session.add(trade_2)
    await async_session.commit()

    trades = TradesService(async_session)
    result = await trades.read_run_number(1)
    assert result == [trade_1, trade_2]


@pytest.mark.anyio
async def test_read_bad_run_number(fake_session):

    trade_1 = Trade(
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        entry_day=34,
        entry_price=321.45,
        exit_day=56,
        exit_price=365.67,
        profit=96.5,
        return_pct=23.4,
        labels="Google-Mean Reversion",
        number_trades_took_place=12,
    )

    trade_2 = Trade(
        run_number=1,
        ticker="Microsoft",
        strategy="Mean Reversion",
        entry_day=44,
        entry_price=361.45,
        exit_day=66,
        exit_price=395.67,
        profit=46.5,
        return_pct=13.4,
        labels="Microsoft-Mean Reversion",
        number_trades_took_place=9,
    )

    async_session = fake_session
    async_session.add(trade_1)
    async_session.add(trade_2)
    await async_session.commit()

    trades = TradesService(async_session)
    result = await trades.read_run_number(2)
    assert result == []


@pytest.mark.anyio
async def test_delete_id(fake_session):

    trade_1 = Trade(
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        entry_day=34,
        entry_price=321.45,
        exit_day=56,
        exit_price=365.67,
        profit=96.5,
        return_pct=23.4,
        labels="Google-Mean Reversion",
        number_trades_took_place=12,
    )

    async_session = fake_session
    async_session.add(trade_1)
    await async_session.commit()

    trades = TradesService(async_session)
    result = await trades.delete_id(1)
    assert result is True
    assert await trades.read_id(1) is None


@pytest.mark.anyio
async def test_delete_bad_id(fake_session):

    trade_1 = Trade(
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        entry_day=34,
        entry_price=321.45,
        exit_day=56,
        exit_price=365.67,
        profit=96.5,
        return_pct=23.4,
        labels="Google-Mean Reversion",
        number_trades_took_place=12,
    )

    async_session = fake_session
    async_session.add(trade_1)
    await async_session.commit()

    trades = TradesService(async_session)
    result = await trades.delete_id(2)
    assert result is False


@pytest.mark.anyio
async def test_delete_run_number(fake_session):

    trade_1 = Trade(
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        entry_day=34,
        entry_price=321.45,
        exit_day=56,
        exit_price=365.67,
        profit=96.5,
        return_pct=23.4,
        labels="Google-Mean Reversion",
        number_trades_took_place=12,
    )

    trade_2 = Trade(
        run_number=1,
        ticker="Microsoft",
        strategy="Mean Reversion",
        entry_day=44,
        entry_price=361.45,
        exit_day=66,
        exit_price=395.67,
        profit=46.5,
        return_pct=13.4,
        labels="Microsoft-Mean Reversion",
        number_trades_took_place=9,
    )

    async_session = fake_session
    async_session.add(trade_1)
    async_session.add(trade_2)
    await async_session.commit()

    trades = TradesService(async_session)
    result = await trades.delete_run_number(1)
    assert result is True
    assert await trades.read_id(1) is None
    assert await trades.read_id(2) is None


@pytest.mark.anyio
async def test_delete_bad_run_number(fake_session):

    trade_1 = Trade(
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        entry_day=34,
        entry_price=321.45,
        exit_day=56,
        exit_price=365.67,
        profit=96.5,
        return_pct=23.4,
        labels="Google-Mean Reversion",
        number_trades_took_place=12,
    )

    trade_2 = Trade(
        run_number=1,
        ticker="Microsoft",
        strategy="Mean Reversion",
        entry_day=44,
        entry_price=361.45,
        exit_day=66,
        exit_price=395.67,
        profit=46.5,
        return_pct=13.4,
        labels="Microsoft-Mean Reversion",
        number_trades_took_place=9,
    )

    async_session = fake_session
    async_session.add(trade_1)
    async_session.add(trade_2)
    await async_session.commit()

    trades = TradesService(async_session)
    result = await trades.delete_run_number(2)
    assert result is False
