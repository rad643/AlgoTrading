from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router.router_backtest import router_backtest
from api.router.router_log_events import router_log_events
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
