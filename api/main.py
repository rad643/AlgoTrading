from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router.router_backtest import router_backtest
from api.router.router_drawdowns import router_drawdowns
from api.router.router_equities import router_equities
from api.router.router_log_events import router_log_events
from api.router.router_prices import router_prices
from api.router.router_statistics import router_statistics
from api.router.router_summary import router_summary
from api.router.router_trades import router_trades

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
)

# run it through a separate API Router object
app.include_router(router_backtest)
app.include_router(router_summary)
app.include_router(router_trades)
app.include_router(router_log_events)
app.include_router(router_equities)
app.include_router(router_drawdowns)
app.include_router(router_prices)
app.include_router(router_statistics)
