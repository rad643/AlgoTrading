import pytest
from fastapi.testclient import TestClient

from api.database.models import Drawdowns
from api.main import app
from api.router.dependencies import get_drawdowns_service

client = TestClient(app)

drawdown_1 = Drawdowns(
    id=1,
    day=1,
    run_number=1,
    ticker="Apple",
    strategy="Mean Reversion",
    equity=10000.0,
    peak_so_far=10000.0,
    drawdown=0.0,
    drawdown_pct=0.0,
    labels="Apple-Mean Reversion",
)

drawdown_2 = Drawdowns(
    id=2,
    day=2,
    run_number=1,
    ticker="Apple",
    strategy="Mean Reversion",
    equity=9950.0,
    peak_so_far=10000.0,
    drawdown=-50.0,
    drawdown_pct=-0.5,
    labels="Apple-Mean Reversion",
)


class FakeDrawdownsService:
    async def read_id(self, id: int):
        if id == 1:
            return drawdown_1
        return None

    async def read_run_number(self, backtest_run_number: int):
        if backtest_run_number == 1:
            return [drawdown_1, drawdown_2]
        return []

    async def delete_id(self, id: int):
        return id == 1

    async def delete_run_number(self, backtest_run_number: int):
        return backtest_run_number == 1


def get_fake_drawdowns_service():
    return FakeDrawdownsService()


@pytest.fixture()
def dependency_overrides():
    app.dependency_overrides[get_drawdowns_service] = get_fake_drawdowns_service
    yield
    app.dependency_overrides = {}


def test_read_drawdown_id(dependency_overrides):
    response = client.get("/drawdown_id/1")
    assert response.status_code == 200
    assert response.json() == drawdown_1.model_dump()


def test_read_drawdown_bad_id(dependency_overrides):
    response = client.get("/drawdown_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_read_drawdowns_backtest_run_number(dependency_overrides):
    response = client.get("/drawdowns_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == [drawdown_1.model_dump(), drawdown_2.model_dump()]


def test_read_drawdowns_bad_backtest_run_number(dependency_overrides):
    response = client.get("/drawdowns_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}


def test_delete_drawdown_id(dependency_overrides):
    response = client.delete("/drawdown_id/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Drawdown with id number 1 has been deleted"}


def test_delete_drawdown_bad_id(dependency_overrides):
    response = client.delete("/drawdown_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_delete_drawdowns_backtest_run_number(dependency_overrides):
    response = client.delete("/drawdowns_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Drawdowns with backtest run number 1 have been deleted"
    }


def test_delete_drawdowns_bad_backtest_run_number(dependency_overrides):
    response = client.delete("/drawdowns_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}
