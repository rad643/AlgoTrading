import datetime

from sqlmodel import Field, Relationship, SQLModel


class LogEvent(SQLModel, table=True):
    __tablename__ = "log_events"
    id: int | None = Field(default=None, primary_key=True)
    run_number: int = Field(foreign_key="summary.id")
    summary: "Summary" = Relationship()
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


class Summary(SQLModel, table=True):
    __tablename__ = "summary"
    id: int | None = Field(default=None, primary_key=True)
    ticker: str
    strategy: str
    starting_cash: float
    total_net_profit: float
    mdd: float
    expectancy: float | None
    payoff_ratio: float | None
    profit_factor: float | None
    sharpe_ratio: float | None
    labels: str


class Trade(SQLModel, table=True):
    __tablename__ = "trades"
    id: int | None = Field(default=None, primary_key=True)
    run_number: int = Field(foreign_key="summary.id")
    summary: "Summary" = Relationship()
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


class Equities(SQLModel, table=True):
    __tablename__ = "equities"
    id: int | None = Field(default=None, primary_key=True)
    day: int
    run_number: int = Field(foreign_key="summary.id")
    summary: "Summary" = Relationship()
    ticker: str
    strategy: str
    equity: float
    labels: str


class Drawdowns(SQLModel, table=True):
    __tablename__ = "drawdowns"
    id: int | None = Field(default=None, primary_key=True)
    day: int
    run_number: int = Field(foreign_key="summary.id")
    summary: "Summary" = Relationship()
    ticker: str
    strategy: str
    equity: float
    peak_so_far: float
    drawdown: float
    drawdown_pct: float
    labels: str


class Prices(SQLModel, table=True):
    __tablename__ = "prices"
    id: int | None = Field(default=None, primary_key=True)
    day: int
    date: datetime.date
    run_number: int = Field(foreign_key="summary.id")
    summary: "Summary" = Relationship()
    ticker: str
    strategy: str
    closing_price: float
    average: float | None
