from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich import panel, print

from api.database.session import create_database
from api.router.router_backtest import router_backtest
from api.router.router_log_events import router_log_events
from api.router.router_summary import router_summary
from api.router.router_trades import router_trades


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    # server setup message and database table creation
    print(panel.Panel("Server booting...", border_style="green"))
    await create_database()

    # pauses here
    yield

    # server shutdown message
    print(panel.Panel("Server shutting down...", border_style="red"))


# server booting starts here
app = FastAPI(lifespan=lifespan_handler)

origins = ["http://localhost:5173"]

app.add_middleware(CORSMiddleware, allow_origins=origins)

# run it through a separate API Router object
app.include_router(router_backtest)
app.include_router(router_summary)
app.include_router(router_trades)
app.include_router(router_log_events)
