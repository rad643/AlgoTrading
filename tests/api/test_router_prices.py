import datetime

import pytest
from fastapi.testclient import TestClient

from api.database.models import Prices
from api.main import app
from api.router.dependencies import get_prices_service

client = TestClient(app)

price_1 = Prices(
    id=1,
    day=1,
    date=datetime.date(2025, 3, 3),
    run_number=1,
    ticker="Apple",
    strategy="Mean Reversion",
    closing_price=100.0,
    average=None,
)

price_2 = Prices(
    id=2,
    day=3,
    date=datetime.date(2025, 3, 5),
    run_number=1,
    ticker="Apple",
    strategy="Mean Reversion",
    closing_price=84.0,
    average=96.0,
)


class FakePricesService:
    async def read_id(self, id: int):
        if id == 1:
            return price_1
        return None

    async def read_run_number(self, backtest_run_number: int):
        if backtest_run_number == 1:
            return [price_1, price_2]
        return []

    async def delete_id(self, id: int):
        return id == 1

    async def delete_run_number(self, backtest_run_number: int):
        return backtest_run_number == 1


def get_fake_prices_service():
    return FakePricesService()


@pytest.fixture()
def dependency_overrides():
    app.dependency_overrides[get_prices_service] = get_fake_prices_service
    yield
    app.dependency_overrides = {}


def test_read_price_id(dependency_overrides):
    response = client.get("/price_id/1")
    assert response.status_code == 200
    assert response.json() == price_1.model_dump(mode="json")


def test_read_price_bad_id(dependency_overrides):
    response = client.get("/price_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_read_prices_backtest_run_number(dependency_overrides):
    response = client.get("/prices_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == [
        price_1.model_dump(mode="json"),
        price_2.model_dump(mode="json"),
    ]


def test_read_prices_bad_backtest_run_number(dependency_overrides):
    response = client.get("/prices_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}


def test_delete_price_id(dependency_overrides):
    response = client.delete("/price_id/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Price with id number 1 has been deleted"}


def test_delete_price_bad_id(dependency_overrides):
    response = client.delete("/price_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_delete_prices_backtest_run_number(dependency_overrides):
    response = client.delete("/prices_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Prices with backtest run number 1 have been deleted"
    }


def test_delete_prices_bad_backtest_run_number(dependency_overrides):
    response = client.delete("/prices_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}
