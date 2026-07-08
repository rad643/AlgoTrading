from fastapi import APIRouter,HTTPException,status
from api.router.dependencies import SummaryServiceDep
from api.schemas.schemas import BacktestConfig

router_summary=APIRouter(tags=["summary"])

@router_summary.get("/summary/{backtest_run_number}")
def get_summary(backtest_run_number:int, summary_service: SummaryServiceDep ):

    summary = summary_service.read(backtest_run_number)
    if summary:
        return summary
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Backtest run number {backtest_run_number} doesn't exist")

@router_summary.delete("/summary/{backtest_run_number}")
def delete_summary(backtest_run_number:int, summary_service: SummaryServiceDep):
    
    summary = summary_service.delete(backtest_run_number)
    if summary:
        return {'message': f"Summary with backtest run number {backtest_run_number} has been deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Backtest run number {backtest_run_number} doesn't exist")