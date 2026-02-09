import trend_signal
import mean_rev_signal

def process_one_day(day,date,closingPrice,average,trendMethod,positionTrend, entryPriceTrend, exitPriceTrend, profitTrend, positionMeanReversion, entryPriceMeanReversion,exitPriceMeanReversion, profitMeanReversion):
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
    if(trendMethod):
        positionTrend, profitTrend, entryPriceTrend, exitPriceTrend=trend_signal.trend_step(day,date,closingPrice,average,positionTrend, entryPriceTrend, exitPriceTrend, profitTrend)
        return (positionTrend, profitTrend, entryPriceTrend, exitPriceTrend)
    else:
        positionMeanReversion, profitMeanReversion, entryPriceMeanReversion, exitPriceMeanReversion=mean_rev_signal.mean_rev_step(day,date,closingPrice,average, positionMeanReversion, entryPriceMeanReversion,exitPriceMeanReversion, profitMeanReversion)
        return (positionMeanReversion, profitMeanReversion, entryPriceMeanReversion, exitPriceMeanReversion)