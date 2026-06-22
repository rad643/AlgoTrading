from fastapi import FastAPI,HTTPException,status
from typing import Any
from pydantic import BaseModel,Field
from main import ExecutionState,TradingEngine
from sqlite_summary_db import SummaryDatabase
from sqlite_log_events_db import LogEventsDatabase
from sqlite_trades_db import TradesDatabase

app=FastAPI()

#create summary.db database 
summary_db=SummaryDatabase("summary") # `summary.db` is the database and `summary` is the table inside it
log_events_db=LogEventsDatabase("log_events") # `log_events.db` is the database and `log_events` is the table inside it
trades_db=TradesDatabase("trades") 

class BacktestConfig(BaseModel):
    trendMethod: bool=Field(default=False)
    csv_ticker: str
    cashValue: float
    ticker_name: str


@app.post("/run_backtest", description="Backtest Run")
def create_backtest(config: BacktestConfig)->dict[str, Any]: 

    # create state object 
    # which will serve as the engine parameter 
    # built from the Pydantic model body configuration
    state=ExecutionState( **config.model_dump() )
    engine=TradingEngine.backtest_run(state) # run the entire backtest once -> this is going to be your engine 

    # compute final run data frame 
    run_df=TradingEngine.performance_metrics_data_frame(state)
    run_df=run_df.where(cond=run_df.notna(), other=None) # replaces all Nan values from the data frame with None
    run_df=run_df.to_dict(orient='records') # [] of dictionaries of the form {column: values of that column}
    run_df=run_df[0] 
    summary_with_id=summary_db.create_summary(run_df) # creating the database table after computing the run data frame from the engine 

    # compute the log events 
    log_events=engine["log_events"]
    log_events=log_events.where(cond=log_events.notna(), other=None)
    log_events=log_events.to_dict(orient='records')
    log_events_with_id=log_events_db.create_event(log_events)

    # compute the trades 
    trades=engine["trades"]
    trades=trades.where(cond=trades.notna(), other=None)
    trades=trades.to_dict(orient='records')
    trades_with_id=trades_db.create_trade(trades)
    
    return { "summary": summary_with_id ,
             "log_events": log_events_with_id, 
             "trades": trades_with_id} 
    
    
@app.get("/summary/{backtest_run_number}")
def get_summary(backtest_run_number:int):

    row=summary_db.read_summary(backtest_run_number,"summary")

    if row: 
        return row 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist")
    

@app.get("/log_events/{backtest_run_number}")
def get_log_events_run_number(backtest_run_number:int):

    row=log_events_db.read_event(backtest_run_number,"log_events")

    if row: 
        return row 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist")


@app.get("/log_events/{backtest_run_number}/{id}")
def get_log_events_id(backtest_run_number:int, id:int):

    row=log_events_db.read_event_id(backtest_run_number, "log_events", id)
    
    if row:
        return row
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist")


@app.get("/trades/{backtest_run_number}")
def get_trades(backtest_run_number:int):

    row=trades_db.read_trade(backtest_run_number,"trades")

    if row: 
        return row 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist")


@app.get("/trades/{backtest_run_number}/{id}")
def get_trades_id(backtest_run_number:int, id:int):

    row=trades_db.read_trade_id(backtest_run_number, "trades", id)
    
    if row:
        return row
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist")       

    
@app.delete("/summary/{backtest_run_number}")
def delete_summary(backtest_run_number:int):
    
    deleted_row=summary_db.delete_summary_run_number(backtest_run_number,"summary")
    #return deleted_row
     
    if deleted_row: 
        return f"You have chosen to delete row from run_number {deleted_row["run_number"]}: {deleted_row}" 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist") 
    

@app.delete("/trades/{backtest_run_number}")
def delete_trade(backtest_run_number:int):

    deleted_rows=trades_db.delete_trade_run_number(backtest_run_number,"trades")

    if deleted_rows: 
        return f"You have chosen to delete row from run_number {deleted_rows["run_number"]} :{deleted_rows}" 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist")
    

@app.delete("/log_events/{backtest_run_number}")
def delete_log_event(backtest_run_number:int):
    
    deleted_rows=log_events_db.delete_log_event_run_number(backtest_run_number,"log_events")

    if deleted_rows: 
        return f"You have chosen to delete row from run_number {deleted_rows["run_number"]} :{deleted_rows}" 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist")
