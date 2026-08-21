import json
from typing import Any, cast

import pandas as pd
from fastapi import APIRouter

from api.database.models import LogEvent, Summary, Trade
from api.router.dependencies import SessionDep
from api.schemas.schemas import BacktestConfig
from data_loading.data_loader import hist_data
from main import ExecutionState, TradingEngine

router_backtest = APIRouter(tags=["backtest"])


@router_backtest.post("/run_backtest", description="Backtest Run")
async def create_backtest(
    config: BacktestConfig, session: SessionDep
) -> dict[str, Any]:

    # create state object
    # which will serve as the engine parameter
    # built from the Pydantic model body configuration
    state = ExecutionState(**config.model_dump())
    ticker_df = hist_data(
        state.symbol, timeframe="1Day", start="2024-01-16", end="2026-01-13", limit=1000
    )
    engine = TradingEngine.backtest_run(
        state, ticker_df[state.symbol]
    )  # run the entire backtest once -> this is going to be your engine

    # compute final run data frame on the state created object
    run_df = TradingEngine.performance_metrics_data_frame(state)
    run_dict = run_df.to_dict(
        orient="records"
    )  # [] of dictionaries of the form {column: values of that column}
    summary_dict = cast(dict[str, Any], run_dict[0])
    new_summary = Summary(
        **summary_dict
    )  # cast it to a Summary object so that SQL Model can add it to the summary table
    session.add(new_summary)
    await session.commit()
    await session.refresh(new_summary)

    # compute the log events
    log_events = engine["log_events"]
    log_events_json_string = log_events.to_json(orient="records", date_format="iso")
    log_events_list = json.loads(log_events_json_string)
    log_events_list_with_id = []
    for event in log_events_list:
        event["date"] = pd.to_datetime(event["date"]).date() if event["date"] else None
        new_event = LogEvent(
            **event
        )  # cast the event dict to a LogEvent object so that sql can add it to the log_events table
        session.add(new_event)
        await session.commit()
        await session.refresh(new_event)
        log_events_list_with_id.append(
            new_event.model_dump()
        )  # new list formed of the log events
        # returned from the database after the commit session
        # now also including the 'id' field which will appear in the Swagger response body for the post route

    # compute the trades
    trades = engine["trades"]
    trades_json_string = trades.to_json(orient="records")
    trades_list = json.loads(trades_json_string)
    trades_list_with_id = []
    for event in trades_list:
        new_trade = Trade(
            **event
        )  # cast the event dict to a Trade object so that sql can add it to the trades table
        session.add(new_trade)
        await session.commit()
        await session.refresh(new_trade)
        trades_list_with_id.append(
            new_trade.model_dump()
        )  # new list formed of the trades
        # returned from the database after the commit session
        # now also including the 'id' field which will appear in the Swagger response body for the post route

    await session.refresh(
        new_summary
    )  # re populates new_summary variable with the fields from the summary table
    # so that 'id' field can also appear in the Swagger response body for the post route

    return {
        "summary": new_summary,
        "log_events": log_events_list_with_id,
        "trades": trades_list_with_id,
    }
