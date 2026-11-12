from fastapi import APIRouter, HTTPException, status

from api.router.dependencies import DrawdownsServiceDep

router_drawdowns = APIRouter(tags=["drawdowns"])


@router_drawdowns.get("/drawdown_id/{id}")
async def get_drawdown_id(id: int, drawdowns_service: DrawdownsServiceDep):

    drawdown = await drawdowns_service.read_id(id)
    if drawdown:
        return drawdown
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_drawdowns.get("/drawdowns_backtest_run_number/{backtest_run_number}")
async def get_drawdowns_backtest_run_number(
    backtest_run_number: int, drawdowns_service: DrawdownsServiceDep
):

    drawdowns = await drawdowns_service.read_run_number(backtest_run_number)
    if drawdowns:
        return drawdowns
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Backtest run number {backtest_run_number} doesn't exist",
    )


@router_drawdowns.delete("/drawdown_id/{id}")
async def delete_drawdown(id: int, drawdowns_service: DrawdownsServiceDep):

    drawdown = await drawdowns_service.delete_id(id)
    if drawdown:
        return {"message": f"Drawdown with id number {id} has been deleted"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_drawdowns.delete("/drawdowns_backtest_run_number/{backtest_run_number}")
async def delete_drawdowns(
    backtest_run_number: int, drawdowns_service: DrawdownsServiceDep
):

    drawdowns = await drawdowns_service.delete_run_number(backtest_run_number)
    if drawdowns:
        return {
            "message": f"Drawdowns with backtest run number {backtest_run_number} have been deleted"
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Backtest run number {backtest_run_number} doesn't exist",
    )
