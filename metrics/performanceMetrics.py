import pandas as pd
import pandas.api.types

def mdd(listEquities:list)->float:
    """
    Calculates maximum draw down based on stored equity values from main.py
    MDD->uses raw equities to evaluate the value of the portfolio levels over time
    MDD=(peak equity value-trough equity followed after that peak)/peak equity value * 100

    Args:
        equities (list): list of stored equtity values from day 1 to day 500

    Returns:
        float: MDD value expressed as a %
    """
    #making sure the list is not empty 
    if len(listEquities)==0:
        raise ValueError
    # 1 dimensional array representing all the raw daily equities 
    equities=pd.Series(listEquities, name="daily_equities")
    #the pandas series can only take numeric values as elements
    if not pandas.api.types.is_numeric_dtype(equities):
        raise ValueError
    #accumulate the current max each time
    running_max=equities.cummax()
    #check for division by 0 error 
    if running_max.max()==0:
        raise ZeroDivisionError
    # find each draw down associated to its current peak 
    draw_down=(equities-running_max) / running_max
    #extract minimum draw down
    mdd=float(draw_down.min())
    return round( (abs(mdd)*100), 2)


def expectancy(positiveProfit, numberTrades, totalProfitPositiveTrades, negativeProfit, totalProfitNegativeTrades):
    """calculates expectancy metric based on trade P&L stats from main.py

    Args:
        positiveProfit (int): total number of wins (total number of positive P&L's)
        numberTrades (int): total number of trades (total number of P&L's)
        totalProfitPositiveTrades (float): total profit obtained from only positive P&L's 
        negativeProfit (int): total number of losses (total number of negative P&L's)
        totalProfitNegativeTrades (float): total profit obtained from only negative P&L's

    Returns:
        float: Expectancy value expressed as a float 
    """

     #make sure denominator is not 0 
    if negativeProfit==0 or positiveProfit==0 or numberTrades==0:
        raise ZeroDivisionError

    
    #Win Rate formula
    winRate=positiveProfit/numberTrades
    #Average Win formula 
    averageWin=totalProfitPositiveTrades/positiveProfit
    #Loss Rate formula 
    lossRate=negativeProfit/numberTrades
    #Average Loss formula
    averageLoss=abs(totalProfitNegativeTrades/negativeProfit)

    #compute the formula for Expectancy 
    expectancy=round( (winRate*averageWin)-(lossRate*averageLoss), 2)
    return expectancy


def payoff_ratio(totalProfitPositiveTrades, totalProfitNegativeTrades, positiveProfit, negativeProfit)-> float:
    """calculates average win divided by average loss 

    Args:
        totalProfitPositiveTrades (float): total profit obtained from only positive P&L's 
        totalProfitNegativeTrades (float): total profit obtained from only negative P&L's
        positiveProfit (int): total number of wins (total number of positive P&L's)
        negativeProfit (int): total number of losses (total number of negative P&L's)

    Returns:
        float: Payoff Ratio expressed as a float 
    """

    #make sure denominator is not 0 
    if positiveProfit==0 or negativeProfit==0:
        raise ZeroDivisionError

    #payoff ratio=average win / average loss 
    payoff_ratio=round( (totalProfitPositiveTrades/positiveProfit) / (abs(totalProfitNegativeTrades/negativeProfit)), 2)
    return payoff_ratio


def profit_factor(totalProfitPositiveTrades, totalProfitNegativeTrades)->float:
    """calculates gross profit divided by absolute value of gross loss 

    Args:
        totalProfitPositiveTrades (float): total profit obtained from only positive P&L's 
        totalProfitNegativeTrades (float): total profit obtained from only negative P&L's

    Returns:
        float: profit factor expressed as a float 
    """

    #make sure denominator is not 0 
    if totalProfitNegativeTrades==0:
        raise ZeroDivisionError

    #profit factor=gross profit / abs(gross loss)
    profit_factor=round(totalProfitPositiveTrades/abs(totalProfitNegativeTrades),2)
    return profit_factor
    

def sharpe_ratio(raw_daily_equities: list):
    """
    Computes sharpe ratio which is (expected portfolio return - risk free rate) / standard deviation 
    raw equity values->describe portfolio state after trading strategy mechanics (entries, exits, position sizing, cash, fees, and slippage) at the end of each day of trading
    daily equity returns=(equity_current_day - equity_previous_day)/equity_previous_day -> period-by-period strategy performance behaviour
    Expected portfolio return (sample mean)->described by the daily equity returns (how the portfolio value changed through time under the strategy)
    Risk free rate=0 because we dont consider trading risk free assets 
    Standard deviation=sqrt( sum( (daily_equity_return_value - sample mean)**2 ) / (nb daily equity return values-1) )

    Args:
        listStoreEquityValues (list): list of stored raw equtity values from day 1 to day 500

    Returns:
        float: sharpe ratio expressed as a float 
    """
    #making sure the list is not empty 
    if len(raw_daily_equities)==0:
        raise ValueError
    #compute the raw daily equity values from the list into a pandas Series and use vectorization 
    equities=pd.Series(raw_daily_equities, name="equities")
    #the pandas series can only take numeric values as elements
    if not pandas.api.types.is_numeric_dtype(equities):
        raise ValueError
    #compute Series of daily equity returned values (change per unit) => fractional change 
    daily_equity_returns=equities.pct_change()
    # expected portfolio return Rp=mean of the daily equity returned values, which represents the sample mean
    expected_portfolio_return=daily_equity_returns.mean()

    #standard deviation
    standardDeviation=daily_equity_returns.std()

    # risk free rate (Rf)=0 ; no modeling of risk free trades 
    riskFreeRate=0

    if standardDeviation==0:
        raise ZeroDivisionError

    #calculate sharpe ratio
    sharpeRatio=float((expected_portfolio_return-riskFreeRate)/standardDeviation)

    return round(sharpeRatio,3)