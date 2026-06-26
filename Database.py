import datetime
from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session
from sqlalchemy import create_engine

class BacktestConfig(BaseModel):
    trendMethod: bool = Field(default=False)
    csv_ticker: str
    cashValue: float
    ticker_name: str

class LogEvent(SQLModel,table=True):
    __tablename__='log_events'
    id: int | None = Field(default=None, primary_key=True)
    run_number: int
    day: int | None 
    date: datetime.date | None
    ticker: str
    strategy: str
    event_type: str 
    message: str
    cash: float
    equity: float
    position: int
    execution_price: float | None
    pnl: float | None
    labels: str | None

class Summary(SQLModel,table=True):
    __tablename__='summary'
    id: int | None = Field(default=None, primary_key=True)
    run_number: int
    ticker: str
    strategy: str
    starting_cash: float
    total_net_profit: float
    mdd: float
    expectancy: float
    payoff_ratio: float
    profit_factor: float
    sharpe_ratio: float
    labels: str

class Trade(SQLModel, table=True):
    __tablename__='trades'
    id: int | None = Field(default=None, primary_key=True)
    run_number: int
    ticker: str
    strategy: str
    entry_day: int
    entry_price: float
    exit_day: int 
    exit_price: float
    profit: float
    return_pct: float
    labels: str
    number_trades_took_place: int

engine=create_engine(url="sqlite:///data/Database.db", echo=True, connect_args={'check_same_thread':False})

def create_database():
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    with Session(bind=engine) as session:
        yield session

SessionDep=Annotated [Session, Depends(get_session)]