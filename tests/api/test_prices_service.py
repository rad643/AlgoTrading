import datetime

import pytest

from api.database.models import Prices
from api.router.services.prices_service import PricesService


@pytest.mark.anyio
async def test_read_id(fake_session):

    price_1 = Prices(
        day=1,
        date=datetime.date(2025, 3, 3),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=100.0,
        average=None,
    )

    price_2 = Prices(
        day=2,
        date=datetime.date(2025, 3, 4),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=92.0,
        average=None,
    )

    async_session = fake_session
    async_session.add(price_1)
    async_session.add(price_2)
    await async_session.commit()

    prices = PricesService(async_session)
    result = await prices.read_id(2)
    assert result == price_2


@pytest.mark.anyio
async def test_read_bad_id(fake_session):

    price_1 = Prices(
        day=1,
        date=datetime.date(2025, 3, 3),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=100.0,
        average=None,
    )

    async_session = fake_session
    async_session.add(price_1)
    await async_session.commit()

    prices = PricesService(async_session)
    result = await prices.read_id(2)
    assert result is None


@pytest.mark.anyio
async def test_read_run_number(fake_session):

    price_1 = Prices(
        day=1,
        date=datetime.date(2025, 3, 3),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=100.0,
        average=None,
    )

    price_2 = Prices(
        day=2,
        date=datetime.date(2025, 3, 4),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=92.0,
        average=None,
    )

    # day 2 is inserted first, so the result only comes back as [day 1, day 2] because of the order_by
    async_session = fake_session
    async_session.add(price_2)
    await async_session.commit()
    async_session.add(price_1)
    await async_session.commit()

    prices = PricesService(async_session)
    result = await prices.read_run_number(1)
    assert result == [price_1, price_2]


@pytest.mark.anyio
async def test_read_bad_run_number(fake_session):

    price_1 = Prices(
        day=1,
        date=datetime.date(2025, 3, 3),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=100.0,
        average=None,
    )

    price_2 = Prices(
        day=2,
        date=datetime.date(2025, 3, 4),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=92.0,
        average=None,
    )

    async_session = fake_session
    async_session.add(price_1)
    async_session.add(price_2)
    await async_session.commit()

    prices = PricesService(async_session)
    result = await prices.read_run_number(2)
    assert result == []


@pytest.mark.anyio
async def test_delete_id(fake_session):

    price_1 = Prices(
        day=1,
        date=datetime.date(2025, 3, 3),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=100.0,
        average=None,
    )

    async_session = fake_session
    async_session.add(price_1)
    await async_session.commit()

    prices = PricesService(async_session)
    result = await prices.delete_id(1)
    assert result is True
    assert await prices.read_id(1) is None


@pytest.mark.anyio
async def test_delete_bad_id(fake_session):

    price_1 = Prices(
        day=1,
        date=datetime.date(2025, 3, 3),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=100.0,
        average=None,
    )

    async_session = fake_session
    async_session.add(price_1)
    await async_session.commit()

    prices = PricesService(async_session)
    result = await prices.delete_id(2)
    assert result is False


@pytest.mark.anyio
async def test_delete_run_number(fake_session):

    price_1 = Prices(
        day=1,
        date=datetime.date(2025, 3, 3),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=100.0,
        average=None,
    )

    price_2 = Prices(
        day=2,
        date=datetime.date(2025, 3, 4),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=92.0,
        average=None,
    )

    async_session = fake_session
    async_session.add(price_1)
    async_session.add(price_2)
    await async_session.commit()

    prices = PricesService(async_session)
    result = await prices.delete_run_number(1)
    assert result is True
    assert await prices.read_id(1) is None
    assert await prices.read_id(2) is None


@pytest.mark.anyio
async def test_delete_bad_run_number(fake_session):

    price_1 = Prices(
        day=1,
        date=datetime.date(2025, 3, 3),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=100.0,
        average=None,
    )

    price_2 = Prices(
        day=2,
        date=datetime.date(2025, 3, 4),
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        closing_price=92.0,
        average=None,
    )

    async_session = fake_session
    async_session.add(price_1)
    async_session.add(price_2)
    await async_session.commit()

    prices = PricesService(async_session)
    result = await prices.delete_run_number(2)
    assert result is False
