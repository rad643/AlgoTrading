import pytest
from fastapi.testclient import TestClient

from api.database.models import Equities
from api.main import app
from api.router.dependencies import get_equities_service

client = TestClient(app)

equity_1 = Equities(
    id=1,
    day=1,
    run_number=1,
    ticker="Apple",
    strategy="Mean Reversion",
    equity=10000.0,
    labels="Apple-Mean Reversion",
)

equity_2 = Equities(
    id=2,
    day=2,
    run_number=1,
    ticker="Apple",
    strategy="Mean Reversion",
    equity=10012.217,
    labels="Apple-Mean Reversion",
)


class FakeEquitiesService:
    async def read_id(self, id: int):
        if id == 1:
            return equity_1
        return None

    async def read_run_number(self, backtest_run_number: int):
        if backtest_run_number == 1:
            return [equity_1, equity_2]
        return []

    async def delete_id(self, id: int):
        return id == 1

    async def delete_run_number(self, backtest_run_number: int):
        return backtest_run_number == 1


def get_fake_equities_service():
    return FakeEquitiesService()


@pytest.fixture()
def dependency_overrides():
    app.dependency_overrides[get_equities_service] = get_fake_equities_service
    yield
    app.dependency_overrides = {}


def test_read_equity_id(dependency_overrides):
    response = client.get("/equity_id/1")
    assert response.status_code == 200
    assert response.json() == equity_1.model_dump()


def test_read_equity_bad_id(dependency_overrides):
    response = client.get("/equity_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_read_equities_backtest_run_number(dependency_overrides):
    response = client.get("/equities_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == [equity_1.model_dump(), equity_2.model_dump()]


def test_read_equities_bad_backtest_run_number(dependency_overrides):
    response = client.get("/equities_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}


def test_delete_equity_id(dependency_overrides):
    response = client.delete("/equity_id/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Equity with id number 1 has been deleted"}


def test_delete_equity_bad_id(dependency_overrides):
    response = client.delete("/equity_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_delete_equities_backtest_run_number(dependency_overrides):
    response = client.delete("/equities_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Equities with backtest run number 1 have been deleted"
    }


def test_delete_equities_bad_backtest_run_number(dependency_overrides):
    response = client.delete("/equities_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}
