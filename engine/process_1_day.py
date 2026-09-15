import strategies.mean_reversion.signal as mean_reversion_signal
import strategies.trend.signal as trend_signal


def process_one_day(
    verbose_run,
    day,
    date,
    closingPrice,
    average,
    nextDayOpeningPrice,
    cashValue,
    equity,
    pending_action,
    positionSizing,
    flat_fee_per_share,
    fixed_bps,
    trendMethod,
    positionTrend,
    entry_day,
    exit_day,
    entryPriceTrend,
    exitPriceTrend,
    profitTrend,
    positionMeanReversion,
    entryPriceMeanReversion,
    exitPriceMeanReversion,
    profitMeanReversion,
):
    """
    Description: Routes the current day to one of the two signalling strategies and
    normalises its output. Calls trend_signal.trend_step when trendMethod is True and
    mean_reversion_signal.mean_rev_step otherwise, passing that strategy's own position,
    entry/exit price and profit variables, then rounds the numeric fields of the returned
    tuple to 3 decimals before handing it back to the engine.

    Args:
        verbose_run (bool): flag variable deciding whether or not to print the 500 daily lines to the console
        day (int): current day
        date (str): current date
        closingPrice (float): closing price of the current day
        average (float): average of all the closing prices up until the current day (current day's closing price excluded)
        nextDayOpeningPrice (float): execution price at which the trade takes place (sell/buy)
        cashValue (float): current amount of cash
        equity (float): cash + assets (unrealized value of the shares currently held, marked at the day's closing price)
        pending_action (str): trading signal produced on the previous day, executed today at the market's opening price; one of "BUY", "SELL", "HOLD" or ""
        positionSizing (float): maximum amount of money allowed to spend
        flat_fee_per_share (float): the broker's commission charged for each individual share traded (both when buying and when selling)
        fixed_bps (float): a small percentage adjustment applied to the execution price to simulate slippage caused by market frictions and volatility
        trendMethod (bool): boolean flag deciding which algorithm is used on the current day -> True for Trend, False for Mean Reversion
        positionTrend (int): number of shares currently owned under the Trend method
        entry_day (int): day on which the currently open position was bought
        exit_day (int): day on which the last position was sold
        entryPriceTrend (float): price at which you buy under the Trend method
        exitPriceTrend (float): price at which you sell under the Tre
        profitTrend (float): realized profit = (exitPriceTrend - entryPriceTrend) * number_of_shares
        positionMeanReversion (int): number of shares currently owned under the Mean Reversion method
        entryPriceMeanReversion (float): price at which you buy under
        exitPriceMeanReversion (float): price at which you sell under the Mean Reversion method
        profitMeanReversion (float): realized profit = (exitPriceMeanReversion - entryPriceMeanReversion) * number_of_shares

    Raises:
        TypeError: if pending_action is not a str, or trendMethod is not a bool.
        ValueError: if pending_action is a str outside {"BUY", "SELL", "HOLD", ""}.

    Returns:
        tuple: the selected strategy's 9-tuple - (position, profit, e
        cash, equity, pending_action, entry_day, exit_day) - with the seven numeric fields
        rounded to 3 decimals.
    """

    # pending_action needs to be a string
    if not isinstance(pending_action, str):
        raise TypeError

    # pending_action is a string but not the correct one
    if not pending_action in {"BUY", "SELL", "HOLD", ""}:
        raise ValueError

    # trendMethod needs to be a bool
    if not isinstance(trendMethod, bool):
        raise TypeError

    # we need to see towards which investment method we branch out
    if trendMethod:
        (
            positionTrend,
            profitTrend,
            entryPriceTrend,
            exitPriceTrend,
            cashValue,
            equity,
            pending_action,
            entry_day,
            exit_day,
        ) = trend_signal.trend_step(
            verbose_run,
            day,
            date,
            closingPrice,
            average,
            nextDayOpeningPrice,
            cashValue,
            equity,
            pending_action,
            positionSizing,
            flat_fee_per_share,
            fixed_bps,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
        )
        return (
            positionTrend,
            round(profitTrend, 3),
            round(entryPriceTrend, 3),
            round(exitPriceTrend, 3),
            round(cashValue, 3),
            round(equity, 3),
            pending_action,
            entry_day,
            exit_day,
        )
    else:
        (
            positionMeanReversion,
            profitMeanReversion,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            cashValue,
            equity,
            pending_action,
            entry_day,
            exit_day,
        ) = mean_reversion_signal.mean_rev_step(
            verbose_run,
            day,
            date,
            closingPrice,
            average,
            nextDayOpeningPrice,
            cashValue,
            equity,
            pending_action,
            positionSizing,
            flat_fee_per_share,
            fixed_bps,
            positionMeanReversion,
            entry_day,
            exit_day,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )
        return (
            positionMeanReversion,
            round(profitMeanReversion, 3),
            round(entryPriceMeanReversion, 3),
            round(exitPriceMeanReversion, 3),
            round(cashValue, 3),
            round(equity, 3),
            pending_action,
            entry_day,
            exit_day,
        )
