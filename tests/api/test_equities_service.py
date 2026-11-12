import pytest

from api.database.models import Equities
from api.router.services.equities_service import EquitiesService


@pytest.mark.anyio
async def test_read_id(fake_session):

    equity_1 = Equities(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        labels="Google-Mean Reversion",
    )

    equity_2 = Equities(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10012.217,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(equity_1)
    async_session.add(equity_2)
    await async_session.commit()

    equities = EquitiesService(async_session)
    result = await equities.read_id(2)
    assert result == equity_2


@pytest.mark.anyio
async def test_read_bad_id(fake_session):

    equity_1 = Equities(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(equity_1)
    await async_session.commit()

    equities = EquitiesService(async_session)
    result = await equities.read_id(2)
    assert result is None


@pytest.mark.anyio
async def test_read_run_number(fake_session):

    equity_1 = Equities(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        labels="Google-Mean Reversion",
    )

    equity_2 = Equities(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10012.217,
        labels="Google-Mean Reversion",
    )

    # day 2 is inserted first, so the result only comes back as [day 1, day 2] because of the order_by
    async_session = fake_session
    async_session.add(equity_2)
    await async_session.commit()
    async_session.add(equity_1)
    await async_session.commit()

    equities = EquitiesService(async_session)
    result = await equities.read_run_number(1)
    assert result == [equity_1, equity_2]


@pytest.mark.anyio
async def test_read_bad_run_number(fake_session):

    equity_1 = Equities(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        labels="Google-Mean Reversion",
    )

    equity_2 = Equities(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10012.217,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(equity_1)
    async_session.add(equity_2)
    await async_session.commit()

    equities = EquitiesService(async_session)
    result = await equities.read_run_number(2)
    assert result == []


@pytest.mark.anyio
async def test_delete_id(fake_session):

    equity_1 = Equities(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(equity_1)
    await async_session.commit()

    equities = EquitiesService(async_session)
    result = await equities.delete_id(1)
    assert result is True
    assert await equities.read_id(1) is None


@pytest.mark.anyio
async def test_delete_bad_id(fake_session):

    equity_1 = Equities(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(equity_1)
    await async_session.commit()

    equities = EquitiesService(async_session)
    result = await equities.delete_id(2)
    assert result is False


@pytest.mark.anyio
async def test_delete_run_number(fake_session):

    equity_1 = Equities(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        labels="Google-Mean Reversion",
    )

    equity_2 = Equities(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10012.217,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(equity_1)
    async_session.add(equity_2)
    await async_session.commit()

    equities = EquitiesService(async_session)
    result = await equities.delete_run_number(1)
    assert result is True
    assert await equities.read_id(1) is None
    assert await equities.read_id(2) is None


@pytest.mark.anyio
async def test_delete_bad_run_number(fake_session):

    equity_1 = Equities(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        labels="Google-Mean Reversion",
    )

    equity_2 = Equities(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10012.217,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(equity_1)
    async_session.add(equity_2)
    await async_session.commit()

    equities = EquitiesService(async_session)
    result = await equities.delete_run_number(2)
    assert result is False
