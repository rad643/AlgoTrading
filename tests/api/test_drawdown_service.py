import pytest

from api.database.models import Drawdowns
from api.router.services.drawdown_services import DrawdownsService


@pytest.mark.anyio
async def test_read_id(fake_session):

    drawdown_1 = Drawdowns(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        peak_so_far=10000.0,
        drawdown=0.0,
        drawdown_pct=0.0,
        labels="Google-Mean Reversion",
    )

    drawdown_2 = Drawdowns(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=9950.0,
        peak_so_far=10000.0,
        drawdown=-50.0,
        drawdown_pct=-0.5,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(drawdown_1)
    async_session.add(drawdown_2)
    await async_session.commit()

    drawdowns = DrawdownsService(async_session)
    result = await drawdowns.read_id(2)
    assert result == drawdown_2


@pytest.mark.anyio
async def test_read_bad_id(fake_session):

    drawdown_1 = Drawdowns(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        peak_so_far=10000.0,
        drawdown=0.0,
        drawdown_pct=0.0,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(drawdown_1)
    await async_session.commit()

    drawdowns = DrawdownsService(async_session)
    result = await drawdowns.read_id(2)
    assert result is None


@pytest.mark.anyio
async def test_read_run_number(fake_session):

    drawdown_1 = Drawdowns(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        peak_so_far=10000.0,
        drawdown=0.0,
        drawdown_pct=0.0,
        labels="Google-Mean Reversion",
    )

    drawdown_2 = Drawdowns(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=9950.0,
        peak_so_far=10000.0,
        drawdown=-50.0,
        drawdown_pct=-0.5,
        labels="Google-Mean Reversion",
    )

    # day 2 is inserted first, so the result only comes back as [day 1, day 2] because of the order_by
    async_session = fake_session
    async_session.add(drawdown_2)
    await async_session.commit()
    async_session.add(drawdown_1)
    await async_session.commit()

    drawdowns = DrawdownsService(async_session)
    result = await drawdowns.read_run_number(1)
    assert result == [drawdown_1, drawdown_2]


@pytest.mark.anyio
async def test_read_bad_run_number(fake_session):

    drawdown_1 = Drawdowns(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        peak_so_far=10000.0,
        drawdown=0.0,
        drawdown_pct=0.0,
        labels="Google-Mean Reversion",
    )

    drawdown_2 = Drawdowns(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=9950.0,
        peak_so_far=10000.0,
        drawdown=-50.0,
        drawdown_pct=-0.5,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(drawdown_1)
    async_session.add(drawdown_2)
    await async_session.commit()

    drawdowns = DrawdownsService(async_session)
    result = await drawdowns.read_run_number(2)
    assert result == []


@pytest.mark.anyio
async def test_delete_id(fake_session):

    drawdown_1 = Drawdowns(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        peak_so_far=10000.0,
        drawdown=0.0,
        drawdown_pct=0.0,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(drawdown_1)
    await async_session.commit()

    drawdowns = DrawdownsService(async_session)
    result = await drawdowns.delete_id(1)
    assert result is True
    assert await drawdowns.read_id(1) is None


@pytest.mark.anyio
async def test_delete_bad_id(fake_session):

    drawdown_1 = Drawdowns(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        peak_so_far=10000.0,
        drawdown=0.0,
        drawdown_pct=0.0,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(drawdown_1)
    await async_session.commit()

    drawdowns = DrawdownsService(async_session)
    result = await drawdowns.delete_id(2)
    assert result is False


@pytest.mark.anyio
async def test_delete_run_number(fake_session):

    drawdown_1 = Drawdowns(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        peak_so_far=10000.0,
        drawdown=0.0,
        drawdown_pct=0.0,
        labels="Google-Mean Reversion",
    )

    drawdown_2 = Drawdowns(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=9950.0,
        peak_so_far=10000.0,
        drawdown=-50.0,
        drawdown_pct=-0.5,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(drawdown_1)
    async_session.add(drawdown_2)
    await async_session.commit()

    drawdowns = DrawdownsService(async_session)
    result = await drawdowns.delete_run_number(1)
    assert result is True
    assert await drawdowns.read_id(1) is None
    assert await drawdowns.read_id(2) is None


@pytest.mark.anyio
async def test_delete_bad_run_number(fake_session):

    drawdown_1 = Drawdowns(
        day=1,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=10000.0,
        peak_so_far=10000.0,
        drawdown=0.0,
        drawdown_pct=0.0,
        labels="Google-Mean Reversion",
    )

    drawdown_2 = Drawdowns(
        day=2,
        run_number=1,
        ticker="Google",
        strategy="Mean Reversion",
        equity=9950.0,
        peak_so_far=10000.0,
        drawdown=-50.0,
        drawdown_pct=-0.5,
        labels="Google-Mean Reversion",
    )

    async_session = fake_session
    async_session.add(drawdown_1)
    async_session.add(drawdown_2)
    await async_session.commit()

    drawdowns = DrawdownsService(async_session)
    result = await drawdowns.delete_run_number(2)
    assert result is False
