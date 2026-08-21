from strategies.trend.utils import buy, hold, sell, validation


def trend_step(
    verbose_run: bool,
    day: int,
    date: str,
    closingPrice: float,
    average: float,
    nextDayOpeningPrice: float,
    cashValue: float,
    equity: float,
    pending_action: str,
    positionSizing: float,
    flat_fee_per_share: float,
    fixed_bps: float,
    positionTrend: int,
    entry_day: int,
    exit_day: int,
    entryPriceTrend: float,
    exitPriceTrend: float,
    profitTrend: float,
) -> tuple:
    """
    Description: Executes any pending trading action from the previous day (buy or sell)
    at the current days market opening price, updates portfolio variables (position, cash, equity, and realized profit),
    and determines the next pending trading signal based on the comparison between the current days closing price and the moving average.

    Args:
        verbose_run (bool): flag variable deciding whether or not to print the 500 daily lines to the console
        day (int): current day
        date (str): current date
        closingPrice (float): closing price of the current day
        average (float): average of all the closing prices up until the current day (current day's closing price excluded)
        nextDayOpeningPrice (float): execution price at which the trade takes place (sell/buy)
        cashValue (float): current amount of cash
        equity (float): cash+assets (unrealized profit-value of the shares you currently hold changes based on the latest market price (e.g., the days closing price), without you actually selling them yet)
        pending_action (str): the trading signal determined from the current days prices, whose execution (buy/sell) occurs on the next day at the markets opening price.
        positionSizing (float): maximum amount of money allowed to spend
        flat_fee_per_share (float): the brokers commission charged for each individual share traded (both when buying and when selling).
        fixed_bps (float): a small percentage adjustment applied to the execution price to simulate slippage caused by market frictions and volatility.
        positionTrend (int): number of shares that you currently own (assets)
        entryPriceTrend (float): price at which you buy
        exitPriceTrend (float): price at which you sell
        profitTrend (float): realized profit=(exitPriceTrend-entryPriceTrend) * number_of_shares.

    Returns:
        tuple: Updated portfolio state after processing the current day, including the
        current position (shares held), realized profit, entry and exit prices, remaining cash, current equity (cash + unrealized value of held shares),
        and the pending action signal that will be executed at the next days market opening.
    """

    validation(pending_action, cashValue)

    if pending_action == "BUY":
        if positionTrend == 0:
            (
                entryPriceTrend,
                positionTrend,
                cashValue,
                equity,
                entry_day,
                pending_action,
            ) = buy(
                day,
                cashValue,
                nextDayOpeningPrice,
                fixed_bps,
                positionSizing,
                flat_fee_per_share,
                closingPrice,
                verbose_run,
                date,
                average,
            )
        else:
            positionTrend, cashValue, equity, pending_action = hold(
                cashValue, positionTrend, closingPrice, verbose_run, day, date, average
            )

    elif pending_action == "SELL":
        if positionTrend != 0:
            (
                exitPriceTrend,
                positionTrend,
                cashValue,
                equity,
                profitTrend,
                exit_day,
                pending_action,
            ) = sell(
                day,
                cashValue,
                nextDayOpeningPrice,
                fixed_bps,
                entryPriceTrend,
                closingPrice,
                flat_fee_per_share,
                verbose_run,
                date,
                average,
                positionTrend,
            )
        else:
            positionTrend, cashValue, equity, pending_action = hold(
                cashValue, positionTrend, closingPrice, verbose_run, day, date, average
            )

    elif (pending_action == "HOLD") or (pending_action == ""):
        positionTrend, cashValue, equity, pending_action = hold(
            cashValue, positionTrend, closingPrice, verbose_run, day, date, average
        )

    return (
        positionTrend,
        profitTrend,
        entryPriceTrend,
        exitPriceTrend,
        cashValue,
        equity,
        pending_action,
        entry_day,
        exit_day,
    )
