import trend_signal
import mean_rev_signal

def process_one_day(day, date, closingPrice, average, nextDayOpeningPrice, cashValue, equity, pending_action, positionSizing, flat_fee_per_share, fixed_bps, trendMethod, positionTrend, entryPriceTrend, exitPriceTrend, profitTrend, positionMeanReversion, entryPriceMeanReversion,exitPriceMeanReversion, profitMeanReversion):
    '''
    Decides which signaling method is used on the current day. 
    Redirects towards trend_signal if trendMethod is true, mean_rev_signal otherwise.
    Passes in local variables as arguments.
    Unloads returned tuple into variables. 
    Returns tuple back into the main engine for unloading.
    
    :param day: current day
    :param date: current date
    :param closingPrice: closingPriceOfTheCurrentDay
    :param average: AverageAllClosingPricesUpToCurrentDay
    :param trendMethod: boolean flag deciding which algorithm you wanna use on current day->True for Trend, False for Mean Reversion
    :param positionTrend: 1/0 flag variable; if 1->HOLD/SELL    if 0->BUY/OUT
    :param entryPriceTrend: closingPrice on the current day at which you bought 1 share based on Trend method
    :param exitPriceTrend: closingPrice on the current day at which you sold 1 share based on Trend method
    :param profitTrend: profit=exitPriceTrend-entryPriceTrend
    :param positionMeanReversion: 1/0 flag variable; if 1->SELL/HOLD    if 0->BUY/OUT
    :param entryPriceMeanReversion: closingPrice on the current day at which you bought 1 share based on Mean Rev method 
    :param exitPriceMeanReversion: closingPrice on the current day at which you sold 1 share based on Mean Rev method
    :param profitMeanReversion: profit=exitPriceMeanReversion-entryPriceMeanReversion 
    '''

    #pending_action needs to be a string
    if not type(pending_action) is str:
        raise TypeError
    
    #pending_action is a string but not the correct one 
    if not pending_action in {"BUY", "SELL", "HOLD", ""}:
        raise ValueError

    #trendMethod needs to be a bool
    if not type(trendMethod) is bool:
        raise TypeError
    
    #average needs to be of float or integer data type 
    if not (type(average) is float or type(average) is int): 
        raise TypeError

    #we need to see towards which investment method we branch out 
    if(trendMethod):
        positionTrend, profitTrend, entryPriceTrend, exitPriceTrend, cashValue, equity, pending_action=trend_signal.trend_step(day, date, closingPrice, average, nextDayOpeningPrice, cashValue, equity, pending_action, positionSizing, flat_fee_per_share, fixed_bps, positionTrend, entryPriceTrend, exitPriceTrend, profitTrend)
        return (round(positionTrend,3), round(profitTrend,3), round(entryPriceTrend,3), round(exitPriceTrend,3), round(cashValue,3), round(equity,3), pending_action)
    else:
        positionMeanReversion, profitMeanReversion, entryPriceMeanReversion, exitPriceMeanReversion, cashValue, equity, pending_action=mean_rev_signal.mean_rev_step(day, date, closingPrice, average, nextDayOpeningPrice, cashValue, equity, pending_action, positionSizing, flat_fee_per_share, fixed_bps, positionMeanReversion, entryPriceMeanReversion,exitPriceMeanReversion, profitMeanReversion)
        return (round(positionMeanReversion,3), round(profitMeanReversion,3), round(entryPriceMeanReversion,3), round(exitPriceMeanReversion,3), round(cashValue,3), round(equity,3), pending_action)