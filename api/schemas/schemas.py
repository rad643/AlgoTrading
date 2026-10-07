from pydantic import BaseModel
from sqlmodel import Field


class BacktestConfig(BaseModel):
    trendMethod: bool = Field(default=False)
    symbol: str
    cashValue: float
    ticker_name: str
    timeframe: str = Field(default="1Day")
    start: str = Field(default="2024-01-16")
    end: str = Field(default="2026-01-13")
    limit: int = Field(default=1000)
