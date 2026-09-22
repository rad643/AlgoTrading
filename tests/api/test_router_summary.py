from fastapi.testclient import TestClient

from api.database.models import Summary
from api.main import app
from api.router.dependencies import get_summary_service

client = TestClient(app)


class FakeSummaryService:
    async def read(self, backtest_run_number: int):
        if backtest_run_number == 1:
            return Summary(
                id=1,
                run_number=1,
                ticker="Apple",
                strategy="Trend",
                starting_cash=1000,
                total_net_profit=200,
                mdd=10.5,
                expectancy=3.1,
                payoff_ratio=5.56,
                profit_factor=30.34,
                sharpe_ratio=32.234,
                labels="Apple-Trend",
            )
        return None

    async def delete(self, backtest_run_number: int):
        return backtest_run_number == 1


def get_fake_summary_service():
    return FakeSummaryService()


def test_read_summary():
    app.dependency_overrides[get_summary_service] = get_fake_summary_service
    response = client.get("/summary/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "run_number": 1,
        "ticker": "Apple",
        "strategy": "Trend",
        "starting_cash": 1000.0,
        "total_net_profit": 200.0,
        "mdd": 10.5,
        "expectancy": 3.1,
        "payoff_ratio": 5.56,
        "profit_factor": 30.34,
        "sharpe_ratio": 32.234,
        "labels": "Apple-Trend",
    }
    app.dependency_overrides = {}


def test_read_summary_bad_id():
    app.dependency_overrides[get_summary_service] = get_fake_summary_service
    response = client.get("/summary/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}
    app.dependency_overrides = {}


def test_delete_summary():
    app.dependency_overrides[get_summary_service] = get_fake_summary_service
    response = client.delete("/summary/1")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Summary with backtest run number 1 has been deleted"
    }
    app.dependency_overrides = {}


def test_delete_summary_bad_id():
    app.dependency_overrides[get_summary_service] = get_fake_summary_service
    response = client.delete("/summary/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Backtest run number 2 doesn't exist"}
    app.dependency_overrides = {}
