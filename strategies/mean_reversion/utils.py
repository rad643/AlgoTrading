def pending_action_update(closingPrice, average):
    """
    we need to check what the signal will be regarding tomorrow's required execution action
    and update it accordingly, and then print it to the screen
    """
    # MEAN REV says BUY
    if closingPrice < average:
        # update pending action for tomorrow accordingly
        pending_action = "BUY"

    # MEAN REV says SELL
    elif closingPrice > average:
        # update pending action for tomorrow accordingly
        pending_action = "SELL"

    # MEAN REV says HOLD
    else:
        # update pending action for tomorrow accordingly
        pending_action = "HOLD"
    return pending_action


def buy(
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
):
    """
    if we have a pending signal from the day before that told us to BUY today, we buy at the opening price of today's market
    and you have no shares => BUY
    """
    # you enter a position
    entry_day = day
    # the price at which you're buying the shares today is the opening price of the market + slippage execution->fixed bias points=0.05% due to market volatility
    entryPriceMeanReversion = round(
        nextDayOpeningPrice + (fixed_bps * nextDayOpeningPrice), 3
    )
    # this tells you how many shares you can buy depending on your allowed budget
    positionMeanReversion = positionSizing // entryPriceMeanReversion
    # subtract the number of shares bought and the comission fee for the broker which is applied by share
    cashValue = round(
        cashValue
        - (positionMeanReversion * entryPriceMeanReversion)
        - (positionMeanReversion * flat_fee_per_share),
        3,
    )
    # unrealized profit
    equity = round(cashValue + (positionMeanReversion * closingPrice), 3)
    pending_action = pending_action_update(closingPrice, average)
    # print to the screen what the current day is doing; all variables with the exception of "pending_action" represent today's state
    if verbose_run:
        print(
            f"Day {day} | Date: {date} | Close: {closingPrice} | Execution price: {entryPriceMeanReversion} | Avg: {format(average, '.3f')} | Mean Reversion: {pending_action} | Position: {positionMeanReversion} | Cash: {cashValue} | Equity: {equity}"
        )
        print("\n")
    return (
        entryPriceMeanReversion,
        positionMeanReversion,
        cashValue,
        equity,
        entry_day,
        pending_action,
    )


def sell(
    day,
    cashValue,
    nextDayOpeningPrice,
    fixed_bps,
    entryPriceMeanReversion,
    closingPrice,
    flat_fee_per_share,
    verbose_run,
    date,
    average,
    positionMeanReversion,
):
    """
    if we have a pending signal from the day before that told us to SELL today, we SELL at the opening price of today's market
    and you own multiple shares => sell everything you have
    """
    # exit the position
    exit_day = day
    # the exit price is the opening price of the market - slippage execution->fixed bias points=0.05% due to market volatility
    exitPriceMeanReversion = round(
        nextDayOpeningPrice - (fixed_bps * nextDayOpeningPrice), 3
    )
    # realized profit is the price at which you sold on the corresponding day - the price at which you bought them initially
    profitMeanReversion = round(
        (
            (exitPriceMeanReversion * positionMeanReversion)
            - (entryPriceMeanReversion * positionMeanReversion)
        ),
        3,
    )  # profitMeanReversion is always gross
    # cash value is gonna be price at which you sold the shares - the comission fee for the broker which is applied per share
    cashValue = round(
        cashValue
        + (positionMeanReversion * exitPriceMeanReversion)
        - (positionMeanReversion * flat_fee_per_share),
        3,
    )  # cashValue is net
    # we sold everything so we now own zero shares
    positionMeanReversion = 0
    # unrealized profit
    equity = round(cashValue + (positionMeanReversion * closingPrice), 3)
    pending_action = pending_action_update(closingPrice, average)
    # print to the screen what the current day is doing; all variables with the exception of "pending_action" represent today's state
    if verbose_run:
        print(
            f"Day {day} | Date: {date} | Close: {closingPrice} | Execution price: {exitPriceMeanReversion} | Avg: {format(average, '.3f')} | Mean Reversion: {pending_action} | Position: {positionMeanReversion} | Cash: {cashValue} | Equity: {equity} | P&L: {format(profitMeanReversion, '.3f')}"
        )
        print("\n")
    return (
        exitPriceMeanReversion,
        positionMeanReversion,
        cashValue,
        equity,
        profitMeanReversion,
        exit_day,
        pending_action,
    )


def hold(
    cashValue, positionMeanReversion, closingPrice, verbose_run, day, date, average
):
    """
    but you already own shares/or don't own any shares => HOLD either way => nothing gets updated other than your equity (unrealized profit)
    """
    # unrealized profit
    equity = round(cashValue + (positionMeanReversion * closingPrice), 3)
    pending_action = pending_action_update(closingPrice, average)
    if verbose_run:
        print(
            f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average, '.3f')} | Mean Reversion: {pending_action} | Position: {positionMeanReversion} | Cash: {cashValue} | Equity: {equity}"
        )
        print("\n")
    return (positionMeanReversion, cashValue, equity, pending_action)


def validation(pending_action, cashValue):
    # pending_action needs to be a string and in {"BUY", "SELL", "HOLD", ""}
    if not isinstance(pending_action, str):
        raise TypeError
    if not pending_action in {"BUY", "SELL", "HOLD", ""}:
        raise ValueError

    # cashValue needs to be either integer or float, and it can't be negative or zero
    if not isinstance(cashValue, (int, float)):
        raise TypeError
    if cashValue <= 0:
        raise ValueError
