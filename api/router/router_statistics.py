from fastapi import APIRouter, HTTPException, status

from api.router.dependencies import StatisticsServiceDep

router_statistics = APIRouter(tags=["statistics"])


@router_statistics.get("/final_equity/{id}")
async def get_final_equity_id(id: int, statistics_service: StatisticsServiceDep):

    final_equity = await statistics_service.final_equity(id)
    if final_equity:
        return final_equity
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/total_net_profit/{id}")
async def get_total_net_profit_id(id: int, statistics_service: StatisticsServiceDep):

    total_net_profit = await statistics_service.total_net_profit(id)
    if total_net_profit:
        return total_net_profit
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/return_pct/{id}")
async def get_return_pct_id(id: int, statistics_service: StatisticsServiceDep):

    return_pct = await statistics_service.return_pct(id)
    if return_pct:
        return return_pct
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/sharpe_ratio/{id}")
async def get_sharpe_ratio_id(id: int, statistics_service: StatisticsServiceDep):

    sharpe_ratio = await statistics_service.sharpe_ratio(id)
    if sharpe_ratio:
        return sharpe_ratio
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/annualized_pct/{id}")
async def get_annualized_pct_id(id: int, statistics_service: StatisticsServiceDep):

    annualized_pct = await statistics_service.annualized_pct(id)
    if annualized_pct:
        return annualized_pct
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/maximum_drawdown/{id}")
async def get_mdd_id(id: int, statistics_service: StatisticsServiceDep):

    mdd = await statistics_service.mdd(id)
    if mdd:
        return mdd
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/calmar_ratio/{id}")
async def get_calmar_ratio_id(id: int, statistics_service: StatisticsServiceDep):

    calmar_ratio = await statistics_service.calmar_ratio(id)
    if calmar_ratio:
        return calmar_ratio
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/total_trades/{id}")
async def get_total_trades_id(id: int, statistics_service: StatisticsServiceDep):

    total_trades = await statistics_service.total_trades(id)
    if total_trades:
        return total_trades
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/winning_trades/{id}")
async def get_winning_trades_id(id: int, statistics_service: StatisticsServiceDep):

    winning_trades = await statistics_service.winning_trades(id)
    if winning_trades:
        return winning_trades
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/losing_trades/{id}")
async def get_losing_trades_id(id: int, statistics_service: StatisticsServiceDep):

    losing_trades = await statistics_service.losing_trades(id)
    if losing_trades:
        return losing_trades
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/win_rate/{id}")
async def get_win_rate_id(id: int, statistics_service: StatisticsServiceDep):

    win_rate = await statistics_service.win_rate(id)
    if win_rate is not None:
        return win_rate
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/profit_factor/{id}")
async def get_profit_factor_id(id: int, statistics_service: StatisticsServiceDep):

    profit_factor = await statistics_service.profit_factor(id)
    if profit_factor:
        return profit_factor
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/expectancy/{id}")
async def get_expectancy_id(id: int, statistics_service: StatisticsServiceDep):

    expectancy = await statistics_service.expectancy(id)
    if expectancy:
        return expectancy
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/average_win/{id}")
async def get_average_win_id(id: int, statistics_service: StatisticsServiceDep):

    average_win = await statistics_service.average_win(id)
    if average_win is not None:
        return average_win
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/average_loss/{id}")
async def get_average_loss_id(id: int, statistics_service: StatisticsServiceDep):

    average_loss = await statistics_service.average_loss(id)
    if average_loss is not None:
        return average_loss
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/payoff_ratio/{id}")
async def get_payoff_ratio_id(id: int, statistics_service: StatisticsServiceDep):

    payoff_ratio = await statistics_service.payoff_ratio(id)
    if payoff_ratio:
        return payoff_ratio
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/starting_cash/{id}")
async def get_starting_cash_id(id: int, statistics_service: StatisticsServiceDep):

    starting_cash = await statistics_service.starting_cash(id)
    if starting_cash is not None:
        return starting_cash
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/total_commission/{id}")
async def get_total_commission_id(id: int, statistics_service: StatisticsServiceDep):

    total_commission = await statistics_service.total_commission(id)
    if total_commission is not None:
        return total_commission
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )


@router_statistics.get("/total_slippage_cost/{id}")
async def get_total_slippage_cost_id(id: int, statistics_service: StatisticsServiceDep):

    total_slippage_cost = await statistics_service.total_slippage_cost(id)
    if total_slippage_cost is not None:
        return total_slippage_cost
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Given id number {id} doesn't exist",
    )
