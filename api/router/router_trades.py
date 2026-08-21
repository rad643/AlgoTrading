from fastapi import APIRouter, HTTPException, status

from api.router.dependencies import TradesServiceDep

router_trades = APIRouter(tags=["trades"])


@router_trades.get("/trade_id/{id}")
async def get_trade_id(id: int, trades_service: TradesServiceDep):

    trade = await trades_service.read_id(id)
    if trade:
        return trade
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_trades.get("/trades_backtest_run_number/{backtest_run_number}")
async def get_trades_backtest_run_number(
    backtest_run_number: int, trades_service: TradesServiceDep
):

    trades = await trades_service.read_run_number(backtest_run_number)
    if trades:
        return trades
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Backtest run number {backtest_run_number} doesn't exist",
    )


@router_trades.delete("/trade_id/{id}")
async def delete_trade(id: int, trades_service: TradesServiceDep):

    trade = await trades_service.delete_id(id)
    if trade:
        return {"message": f"Trade with id number {id} has been deleted"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_trades.delete("/trades_backtest_run_number/{backtest_run_number}")
async def delete_trades(backtest_run_number: int, trades_service: TradesServiceDep):

    trades = await trades_service.delete_run_number(backtest_run_number)
    if trades:
        return {
            "message": f"Trades with backtest run number {backtest_run_number} have been deleted"
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Backtest run number {backtest_run_number} doesn't exist",
    )
