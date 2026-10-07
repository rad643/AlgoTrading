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
    """Runs one backtest and saves everything it produced to the database.
    Builds a state object from the config in the request body, pulls the ticker's
    historical data, and runs the whole backtest once through the engine. Then it
    takes the performance metrics, casts them to a Summary object and adds it to
    the summary table, does the same for every log event and every trade the run
    produced, and returns all three back in the response with their ids filled in
    by the database.
    """
    state = ExecutionState(
        **config.model_dump(exclude={"timeframe", "start", "end", "limit"})
    )
    ticker_df = hist_data(
        state.symbol, config.timeframe, config.start, config.end, config.limit
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
    new_summary = Summary(**summary_dict)
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
        event["run_number"] = new_summary.id
        new_event = LogEvent(**event)
        log_events_list_with_id.append(new_event)

    # compute the trades
    trades = engine["trades"]
    trades_json_string = trades.to_json(orient="records")
    trades_list = json.loads(trades_json_string)
    trades_list_with_id = []
    for trade in trades_list:
        trade["run_number"] = new_summary.id
        new_trade = Trade(**trade)
        trades_list_with_id.append(new_trade)

    session.add_all(log_events_list_with_id + trades_list_with_id)  # type: ignore [operator]
    await session.commit()

    return {
        "summary": new_summary,
        "log_events": log_events_list_with_id,
        "trades": trades_list_with_id,
    }
