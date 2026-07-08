from fastapi import APIRouter, HTTPException,status
from api.router.dependencies import LogEventsServiceDep
from api.schemas.schemas import BacktestConfig

router_log_events=APIRouter(tags=["log_events"])

@router_log_events.get("/log_event_id/{id}")
def get_log_event_id(id:int, log_events_service: LogEventsServiceDep): 

    log_event = log_events_service.read_id(id)
    if log_event: 
        return log_event
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Given id number {id} doesn't exist")

@router_log_events.get("/log_events_backtest_run_number/{backtest_run_number}")
def get_log_events_run_number(backtest_run_number:int, log_events_service: LogEventsServiceDep):

    log_events = log_events_service.read_run_number(backtest_run_number)
    if log_events: 
        return log_events
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Backtest run number {backtest_run_number} doesn't exist")  

@router_log_events.delete("/log_event_id/{id}")
def delete_log_event(id:int, log_events_service: LogEventsServiceDep):
    
    log_event = log_events_service.delete_id(id)
    if log_event:
        return {'message': f"Log event with id number {id} has been deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Given id number {id} doesn't exist")

@router_log_events.delete("/log_events_backtest_run_number/{backtest_run_number}")
def delete_log_events(backtest_run_number:int, log_events_service: LogEventsServiceDep):
    
    log_events = log_events_service.delete_run_number(backtest_run_number)
    if log_events:
        return {'message': f"Log events with backtest run number {backtest_run_number} have been deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Backtest run number {backtest_run_number} doesn't exist")