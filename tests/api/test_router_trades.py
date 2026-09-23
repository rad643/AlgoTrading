import pytest
from fastapi.testclient import TestClient

from api.database.models import Trade
from api.main import app
from api.router.dependencies import get_trades_service

client = TestClient(app)

trade_1 = Trade(
    id=1,
    run_number=1,
    ticker="Apple",
    strategy="Mean Reversion",
    entry_day=12,
    entry_price=123.56,
    exit_day=45,
    exit_price=143.65,
    profit=67.56,
    return_pct=9.45,
    labels="Apple-Mean Reversion",
    number_trades_took_place=6,
)

trade_2 = Trade(
    id=2,
    run_number=1,
    ticker="Apple",
    strategy="Mean Reversion",
    entry_day=56,
    entry_price=235.56,
    exit_day=89,
    exit_price=265.76,
    profit=-45.6,
    return_pct=-0.56,
    labels="Apple-Mean Reversion",
    number_trades_took_place=12,
)


class FakeTradesService:
    async def read_id(self, id: int):
        if id == 1:
            return trade_1
        return None

    async def read_run_number(self, backtest_run_number: int):
        if backtest_run_number == 1:
            return [trade_1, trade_2]
        return []

    async def delete_id(self, id: int):
        return id == 1

    async def delete_run_number(self, backtest_run_number: int):
        return backtest_run_number == 1


def get_fake_trades_service():
    return FakeTradesService()


@pytest.fixture()
def dependency_overrides():
    app.dependency_overrides[get_trades_service] = get_fake_trades_service
    yield
    app.dependency_overrides = {}


def test_read_trade_id(dependency_overrides):
    response = client.get("/trade_id/1")
    assert response.status_code == 200
    assert response.json() == trade_1.model_dump()


def test_read_trade_bad_id(dependency_overrides):
    response = client.get("/trade_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_read_trades_backtest_run_number(dependency_overrides):
    response = client.get("/trades_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == [trade_1.model_dump(), trade_2.model_dump()]


def test_read_trades_bad_backtest_run_number(dependency_overrides):
    response = client.get("/trades_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}


def test_delete_trade_id(dependency_overrides):
    response = client.delete("/trade_id/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Trade with id number 1 has been deleted"}


def test_delete_trade_bad_id(dependency_overrides):
    response = client.delete("/trade_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_delete_trades_backtest_run_number(dependency_overrides):
    response = client.delete("/trades_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Trades with backtest run number 1 have been deleted"
    }


def test_delete_trades_bad_backtest_run_number(dependency_overrides):
    response = client.delete("/trades_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}
