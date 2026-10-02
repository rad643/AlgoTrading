import pytest

from api.database.models import Summary
from api.router.services.summary_service import SummaryService


@pytest.mark.anyio
async def test_read_summary(fake_session):

    summary_1 = Summary(
        id=1,
        ticker="Apple",
        strategy="Trend",
        starting_cash=1000,
        total_net_profit=234.54,
        mdd=5.5,
        expectancy=2.3,
        payoff_ratio=4.67,
        profit_factor=8.23,
        sharpe_ratio=2.345,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(summary_1)
    await async_session.commit()

    summary = SummaryService(async_session)
    result = await summary.read(1)
    assert result == summary_1


@pytest.mark.anyio
async def test_read_bad_summary(fake_session):
    async_session = fake_session
    summary = SummaryService(async_session)
    result = await summary.read(1)
    assert result is None


@pytest.mark.anyio
async def test_delete_summary(fake_session):

    summary_1 = Summary(
        id=1,
        ticker="Apple",
        strategy="Trend",
        starting_cash=1000,
        total_net_profit=234.54,
        mdd=5.5,
        expectancy=2.3,
        payoff_ratio=4.67,
        profit_factor=8.23,
        sharpe_ratio=2.345,
        labels="Apple-Trend",
    )

    async_session = fake_session
    async_session.add(summary_1)
    await async_session.commit()

    summary = SummaryService(async_session)
    result = await summary.delete(1)
    assert result is True


@pytest.mark.anyio
async def test_delete_bad_summary(fake_session):
    async_session = fake_session
    summary = SummaryService(async_session)
    result = await summary.delete(1)
    assert result is False
