from fastapi import APIRouter, HTTPException, status

from api.router.dependencies import PricesServiceDep

router_prices = APIRouter(tags=["prices"])


@router_prices.get("/price_id/{id}")
async def get_price_id(id: int, prices_service: PricesServiceDep):

    price = await prices_service.read_id(id)
    if price:
        return price
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_prices.get("/prices_backtest_run_number/{backtest_run_number}")
async def get_prices_backtest_run_number(
    backtest_run_number: int, prices_service: PricesServiceDep
):

    prices = await prices_service.read_run_number(backtest_run_number)
    if prices:
        return prices
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Backtest run number {backtest_run_number} doesn't exist",
    )


@router_prices.delete("/price_id/{id}")
async def delete_price(id: int, prices_service: PricesServiceDep):

    price = await prices_service.delete_id(id)
    if price:
        return {"message": f"Price with id number {id} has been deleted"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_prices.delete("/prices_backtest_run_number/{backtest_run_number}")
async def delete_prices(backtest_run_number: int, prices_service: PricesServiceDep):

    prices = await prices_service.delete_run_number(backtest_run_number)
    if prices:
        return {
            "message": f"Prices with backtest run number {backtest_run_number} have been deleted"
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Backtest run number {backtest_run_number} doesn't exist",
    )
