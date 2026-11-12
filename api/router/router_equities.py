from fastapi import APIRouter, HTTPException, status

from api.router.dependencies import EquitiesServiceDep

router_equities = APIRouter(tags=["equities"])


@router_equities.get("/equity_id/{id}")
async def get_equity_id(id: int, equities_service: EquitiesServiceDep):

    equity = await equities_service.read_id(id)
    if equity:
        return equity
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_equities.get("/equities_backtest_run_number/{backtest_run_number}")
async def get_equities_backtest_run_number(
    backtest_run_number: int, equities_service: EquitiesServiceDep
):

    equities = await equities_service.read_run_number(backtest_run_number)
    if equities:
        return equities
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Backtest run number {backtest_run_number} doesn't exist",
    )


@router_equities.delete("/equity_id/{id}")
async def delete_equity(id: int, equities_service: EquitiesServiceDep):

    equity = await equities_service.delete_id(id)
    if equity:
        return {"message": f"Equity with id number {id} has been deleted"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_equities.delete("/equities_backtest_run_number/{backtest_run_number}")
async def delete_equities(
    backtest_run_number: int, equities_service: EquitiesServiceDep
):

    equities = await equities_service.delete_run_number(backtest_run_number)
    if equities:
        return {
            "message": f"Equities with backtest run number {backtest_run_number} have been deleted"
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Backtest run number {backtest_run_number} doesn't exist",
    )
