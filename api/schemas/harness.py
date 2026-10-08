from pydantic import BaseModel, model_validator
from sqlmodel import Field
from typing_extensions import Self


class BacktestConfig(BaseModel):
    trendMethod: bool = Field(default=False)
    symbol: str
    cashValue: float
    ticker_name: str
    timeframe: str = Field(default="1Day")
    start: str = Field(default="2024-01-16")
    end: str = Field(default="2026-01-13")
    limit: int = Field(default=1000)

    @model_validator(mode="after")
    def check_time_window(self) -> Self:
        if self.start > self.end:
            raise ValueError("Start date must come before end")
        return self
