from pydantic import BaseModel
from sqlmodel import Field

class BacktestConfig(BaseModel):
    trendMethod: bool = Field(default=False)
    csv_ticker: str
    cashValue: float
    ticker_name: str