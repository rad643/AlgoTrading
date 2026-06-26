from contextlib import asynccontextmanager
import json
from fastapi import FastAPI,HTTPException,status
from typing import Any
from sqlmodel import select
from main import ExecutionState,TradingEngine
from rich import panel,print
from Database import LogEvent, Summary, Trade, BacktestConfig, create_database, SessionDep
from datetime import datetime as dt

@asynccontextmanager
async def lifespan_handler(app:FastAPI):
    # server setup message and database table creation
    print(panel.Panel("Server booting...", border_style='green'))
    create_database()
    # pauses here
    yield 

    # server shutdown message 
    print(panel.Panel("Server shutting down...", border_style='red'))

# server booting starts here 
app=FastAPI(lifespan=lifespan_handler) 
 
@app.post("/run_backtest", description="Backtest Run")
def create_backtest(config: BacktestConfig, session: SessionDep)->dict[str, Any]: 

    # create state object 
    # which will serve as the engine parameter 
    # built from the Pydantic model body configuration
    state=ExecutionState( **config.model_dump() )
    engine=TradingEngine.backtest_run(state) # run the entire backtest once -> this is going to be your engine 

    # compute final run data frame on the state created object 
    run_df=TradingEngine.performance_metrics_data_frame(state)
    run_dict=run_df.to_dict(orient='records') # [] of dictionaries of the form {column: values of that column}
    run_dict=run_dict[0]
    new_summary=Summary(**run_dict) # cast it to a Summary object so that SQL Model can add it to the summary table
    session.add(new_summary)
    session.commit()
    session.refresh(new_summary)

    # compute the log events 
    log_events=engine["log_events"]
    log_events_json_string=log_events.to_json(orient='records')
    log_events_list=json.loads(log_events_json_string)
    log_events_list_with_id=[]
    for event in log_events_list:
        event['date']=dt.strptime(event['date'],"%Y-%m-%d") if event['date'] else None
        new_event=LogEvent(**event) # cast the event dict to a LogEvent object so that sql can add it to the log_events table
        session.add(new_event)
        session.commit()
        session.refresh(new_event)
        log_events_list_with_id.append(new_event.model_dump()) # new list formed of the log events
        # returned from the database after the commit session
        # now also including the 'id' field which will appear in the Swagger response body for the post route

    # compute the trades 
    trades=engine["trades"]
    trades_json_string=trades.to_json(orient='records')
    trades_list=json.loads(trades_json_string)
    trades_list_with_id=[]
    for event in trades_list:
        new_trade=Trade(**event) # cast the event dict to a Trade object so that sql can add it to the trades table
        session.add(new_trade)
        session.commit()
        session.refresh(new_trade)
        trades_list_with_id.append(new_trade.model_dump()) # new list formed of the trades
        # returned from the database after the commit session
        # now also including the 'id' field which will appear in the Swagger response body for the post route
    
    session.refresh(new_summary) # re populates new_summary variable with the fields from the summary table
    # so that 'id' field can also appear in the Swagger response body for the post route

    return { "summary": new_summary ,
             "log_events": log_events_list_with_id,
              "trades": trades_list_with_id }


@app.get("/summary/{backtest_run_number}")
def get_summary(backtest_run_number:int, session:SessionDep):

    summary= session.exec(select(Summary).where(Summary.run_number==backtest_run_number)).first()
    if summary:
        return summary
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given backtest run number doesn't exist")
    

@app.get("/log_event_id/{id}")
def get_log_event_id(id:int, session:SessionDep)->LogEvent | None:

    log_event=session.get(LogEvent, id)

    if log_event: 
        return log_event
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id number doesn't exist")


@app.get("/log_events_backtest_run_number/{backtest_run_number}")
def get_log_events_run_number(backtest_run_number:int, session: SessionDep):

    log_events=session.exec(select(LogEvent).where(LogEvent.run_number == backtest_run_number)).all()

    if log_events:
        return log_events
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given backtest run number doesn't exist")


@app.get("/trade_id/{id}")
def get_trade_id(id:int, session: SessionDep)->Trade | None:

    trade=session.get(Trade, id)

    if trade:
        return trade
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id number doesn't exist")


@app.get("/trades_backtest_run_number/{backtest_run_number}")
def get_trades_backtest_run_number(backtest_run_number:int, session:SessionDep):

    trades=session.exec(select(Trade).where(Trade.run_number==backtest_run_number)).all()

    if trades: 
        return trades
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given backtest run number doesn't exist")      


@app.delete("/summary/{id}")
def delete_summary(id:int, session:SessionDep)->dict[str,str] | None:
    
    summary_deleted=session.get(Summary,id)
    if summary_deleted: 
        session.delete(summary_deleted)
        session.commit()
        return {'detail': f"Summary with id number {id} has been deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The selected id number does not exist")


@app.delete("/trade_id/{id}")
def delete_trade(id:int, session:SessionDep)->dict[str,str] | None:

    trade_deleted=session.get(Trade,id)
    if trade_deleted: 
        session.delete(trade_deleted)
        session.commit()
        return {'detail': f"Trade with id number {id} has been deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The selected id number does not exist")


@app.delete("/trades_backtest_run_number/{backtest_run_number}")
def delete_trades(backtest_run_number:int, session:SessionDep)->dict[str,str] | None:

    trades_deleted=session.exec(select(Trade).where(Trade.run_number==backtest_run_number)).all()
    if trades_deleted: 
        for trade in trades_deleted:
            session.delete(trade)
            session.commit()
        return {'detail': f"Trades with backtest run number {backtest_run_number} have been deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The selected backtest run number does not exist")


@app.delete("/log_event_id/{id}")
def delete_log_event(id:int, session:SessionDep)->dict[str,str] | None:
    
    log_event_deleted=session.get(LogEvent,id)
    if log_event_deleted: 
        session.delete(log_event_deleted)
        session.commit()
        return {'detail': f"Log event with id number {id} has been deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The selected id number does not exist")
    

@app.delete("/log_events_backtest_run_number/{backtest_run_number}")
def delete_log_events(backtest_run_number:int, session:SessionDep)->dict[str,str] | None:
    
    log_events_deleted=session.exec(select(LogEvent).where(LogEvent.run_number==backtest_run_number)).all()
    if log_events_deleted: 
        for event in log_events_deleted:
            session.delete(event)
            session.commit()
        return {'detail': f"Log events with backtest run number {backtest_run_number} have been deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The selected backtest run number does not exist")

