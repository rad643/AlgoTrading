import datetime

import pytest
from fastapi.testclient import TestClient

from api.database.models import LogEvent
from api.main import app
from api.router.dependencies import get_log_events_service

client = TestClient(app)

log_event_1 = LogEvent(
    id=1,
    run_number=1,
    day=12,
    date=datetime.date(2025, 1, 15),
    ticker="Apple",
    strategy="Trend",
    event_type="backtest_start",
    message="Backtest has started",
    cash=1000.0,
    equity=1100.0,
    position=4,
    execution_price=434.56,
    pnl=212.5,
    labels="Apple-Trend",
)

log_event_2 = LogEvent(
    id=2,
    run_number=1,
    day=13,
    date=datetime.date(2025, 2, 15),
    ticker="Apple",
    strategy="Trend",
    event_type="BUY_EXECUTED",
    message="A Buy has been executed",
    cash=1005.0,
    equity=1200.0,
    position=5,
    execution_price=436.56,
    pnl=211.5,
    labels="Apple-Trend",
)


class FakeLogEventsService:
    async def read_id(self, id: int):
        if id == 1:
            return log_event_1
        return None

    async def read_run_number(self, backtest_run_number: int):
        if backtest_run_number == 1:
            return [log_event_1, log_event_2]
        return []

    async def delete_id(self, id: int):
        return id == 1

    async def delete_run_number(self, backtest_run_number: int):
        return backtest_run_number == 1


def get_fake_log_events_service():
    return FakeLogEventsService()


@pytest.fixture()
def dependency_overrides():
    app.dependency_overrides[get_log_events_service] = get_fake_log_events_service
    yield
    app.dependency_overrides = {}


def test_read_log_event_id(dependency_overrides):
    response = client.get("/log_event_id/1")
    assert response.status_code == 200
    assert response.json() == log_event_1.model_dump(mode="json")


def test_read_log_event_bad_id(dependency_overrides):
    response = client.get("/log_event_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_read_log_event_backtest_run_number(dependency_overrides):
    response = client.get("/log_events_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == [
        log_event_1.model_dump(mode="json"),
        log_event_2.model_dump(mode="json"),
    ]


def test_read_log_event_bad_backtest_run_number(dependency_overrides):
    response = client.get("/log_events_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}


def test_delete_log_event_id(dependency_overrides):
    response = client.delete("/log_event_id/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Log event with id number 1 has been deleted"}


def test_delete_bad_log_event_id(dependency_overrides):
    response = client.delete("/log_event_id/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Given id number 2 doesn't exist"}


def test_delete_log_event_backtest_run_number(dependency_overrides):
    response = client.delete("/log_events_backtest_run_number/1")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Log events with backtest run number 1 have been deleted"
    }


def test_delete_log_event_bad_backtest_run_number(dependency_overrides):
    response = client.delete("/log_events_backtest_run_number/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}
