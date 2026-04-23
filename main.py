import data_loader as dl
import process_1_day
import dataclasses
import performanceMetrics
import pandas as pd


@dataclasses.dataclass
class Engine:
    """
    Reusable backtesting engine for running Trend Following or Mean Reversion
    experiments on historical price data under realistic execution assumptions.

    The engine models next-bar execution, slippage, commission per share,
    20% position sizing, multiple-share trades, realized profit on full exit,
    and daily equity tracking. It stores the portfolio and strategy state needed
    during a run, including current position, entry/exit prices, realized profit,
    pending action, and the equity curve.

    'backtest_run()' performs one complete backtest run and returns a one-row
    DataFrame containing total net profit and performance metrics.
    'reset()' clears backtest run-specific state field variables so the same Engine instance can be reused
    safely across multiple backtest experiments.
    """
    trendMethod: bool
    csv_ticker: str
    cashValue: float
    ticker_name: str
    verbose_run: bool=False
    fixed_bps: float=0.0005
    flat_fee_per_share: float=0.005
    positionSizing: float=0
    listStoreEquityValues: list=dataclasses.field(default_factory=list)
    equity: int=0
    positionTrend: int=0
    entryPriceTrend: int=0
    exitPriceTrend: int =0
    profitTrend: int =0
    positionMeanReversion: int =0
    entryPriceMeanReversion: int =0
    exitPriceMeanReversion: int =0
    profitMeanReversion: int =0
    backtest_run_number: int=0

    def __post_init__(self):
        self.startingCashValue=self.cashValue

    def backtest_run(self)->float:
        #reset all state fields back to 0 at the end of each backtest run so that the re-used Engine object is clean
        self.reset()
        #initialization of variables for a new backtest run 
        self.positionSizing=self.cashValue*0.2
        self.equity=self.cashValue
        self.totalProfit=0
        previousProfitTrend=0
        previousProfitMeanReversion=0
        positiveProfitTrend=0
        negativeProfitTrend=0
        positiveProfitMeanRev=0
        negativeProfitMeanRev=0
        numberTradesTrend=0
        numberTradesMeanRev=0
        totalProfitPositiveTradesTrend=0
        totalProfitNegativeTradesTrend=0
        totalProfitPositiveTradesMeanRev=0
        totalProfitNegativeTradesMeanRev=0
        pending_action=""
        generatorAverageDayDateClosingPrice=dl.read_ticker_csv(self.csv_ticker, self.cashValue, self.verbose_run)
        # 1 "for" loop iteration=1 day executed,  entire "for" loop iteration=1 full backtest run 
        for day,date,closingPrice,average,nextDayOpeningPrice in generatorAverageDayDateClosingPrice:

            #Days starting from day 3 onwards 
            if(average!=None):

                #TREND strategy
                if(self.trendMethod):

                    #we only compute when there's a change in the profit 
                    previousProfitTrend=self.profitTrend
                    # Process one trading day, update portfolio state, and print the day’s execution/output details
                    self.positionTrend, self.profitTrend, self.entryPriceTrend, self.exitPriceTrend, self.cashValue, self.equity, pending_action=process_1_day.process_one_day(self.verbose_run, day, date, closingPrice, average, nextDayOpeningPrice, self.cashValue, self.equity, pending_action, self.positionSizing, self.flat_fee_per_share, self.fixed_bps, self.trendMethod, self.positionTrend, self.entryPriceTrend, self.exitPriceTrend, self.profitTrend, self.positionMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, self.profitMeanReversion)  
                    # a trade took place
                    if( (self.profitTrend-previousProfitTrend) !=0 ):
                        #add 1 trading day's profit to the total net profit 
                        self.totalProfit+=self.profitTrend
                        #nb of total trades executed during Trend (total nb of P&L's) increases 
                        numberTradesTrend+=1
                        #P&L is positive 
                        if(self.profitTrend>0):
                            #count the nb of positive P&L trades
                            positiveProfitTrend+=1
                            #calculate total profit made out of positive P&L's
                            totalProfitPositiveTradesTrend+=self.profitTrend
                        #P&L is negative
                        else:
                            #count the nb of negative P&L trades 
                            negativeProfitTrend+=1
                            #calculate total profit made out of negative P&L's
                            totalProfitNegativeTradesTrend+=self.profitTrend
                    #add trading day's equity to the equity curve 
                    self.listStoreEquityValues.append(self.equity)
                    

                #MEAN REV strategy 
                else:

                    previousProfitMeanReversion=self.profitMeanReversion
                    self.positionMeanReversion, self.profitMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, self.cashValue, self.equity, pending_action=process_1_day.process_one_day(self.verbose_run, day, date, closingPrice, average, nextDayOpeningPrice, self.cashValue, self.equity, pending_action, self.positionSizing, self.flat_fee_per_share, self.fixed_bps, self.trendMethod, self.positionTrend, self.entryPriceTrend, self.exitPriceTrend, self.profitTrend, self.positionMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, self.profitMeanReversion)
                    if( (self.profitMeanReversion-previousProfitMeanReversion) !=0 ):
                        self.totalProfit+=self.profitMeanReversion
                        #nb of total trades executed during Mean Rev (total nb of P&L's) increases 
                        numberTradesMeanRev+=1
                        #P&L is positive 
                        if(self.profitMeanReversion>0):
                            #count the nb of positive P&L trades 
                            positiveProfitMeanRev+=1
                            #calculate total profit made out of positive P&L's
                            totalProfitPositiveTradesMeanRev+=self.profitMeanReversion
                        #P&L is negative 
                        else:
                            #count the nb of negative P&L trades 
                            negativeProfitMeanRev+=1
                            #calculate total profit made out of negative P&L's
                            totalProfitNegativeTradesMeanRev+=self.profitMeanReversion
                    #add trading day's equity to the equity curve 
                    self.listStoreEquityValues.append(self.equity)
                    

            #Days 1 and 2
            else:
                self.listStoreEquityValues.append(self.equity)

        # count the number of backtest runs at Class level (not per engine instance)
        Engine.backtest_run_number+=1

        #trading finished => evaluate portfolio performance following either Trend or Mean Reversion strategy 
        #MDD metric computation 
        #Expectancy metric computation   
        #Payoff Ratio metric computation
        #Profit Factor metric computation
        #Sharpe Ratio metric computation 

        #TREND method performance metrics computation
        if self.trendMethod:
            strategyUsed="Trend"
            mddMetric=performanceMetrics.mdd(self.listStoreEquityValues)
            try:
                expectancy=performanceMetrics.expectancy(positiveProfitTrend, numberTradesTrend, totalProfitPositiveTradesTrend, negativeProfitTrend, totalProfitNegativeTradesTrend)
            except ZeroDivisionError:
                expectancy=float("nan")
            try:
                payoffRatio=performanceMetrics.payoff_ratio(totalProfitPositiveTradesTrend, totalProfitNegativeTradesTrend, positiveProfitTrend, negativeProfitTrend)
            except ZeroDivisionError:
                payoffRatio=float("nan")
            try:
                profitFactor=performanceMetrics.profit_factor(totalProfitPositiveTradesTrend, totalProfitNegativeTradesTrend)
            except ZeroDivisionError:
                profitFactor=float("nan")
            try: 
                sharpeRatio=performanceMetrics.sharpe_ratio(self.listStoreEquityValues)
            #guard for the mathematically undefined case (std=0 means all returns are identical, so Sharpe is meaningless)
            except ZeroDivisionError:
                sharpeRatio=float("nan")

        #MEAN REVERSION method performance metrics computation 
        else:
            strategyUsed="Mean reversion"
            mddMetric=performanceMetrics.mdd(self.listStoreEquityValues)
            try: 
                expectancy=performanceMetrics.expectancy(positiveProfitMeanRev, numberTradesMeanRev, totalProfitPositiveTradesMeanRev, negativeProfitMeanRev, totalProfitNegativeTradesMeanRev)
            except ZeroDivisionError:
                expectancy=float("nan")
            try:
                payoffRatio=performanceMetrics.payoff_ratio(totalProfitPositiveTradesMeanRev, totalProfitNegativeTradesMeanRev, positiveProfitMeanRev, negativeProfitMeanRev)
            except ZeroDivisionError:
                payoffRatio=float("nan")
            try:
                profitFactor=performanceMetrics.profit_factor(totalProfitPositiveTradesMeanRev, totalProfitNegativeTradesMeanRev)
            except ZeroDivisionError:
                profitFactor=float("nan")
            try: 
                sharpeRatio=performanceMetrics.sharpe_ratio(self.listStoreEquityValues)
            #guard for the mathematically undefined case (std=0 means all returns are identical, so Sharpe is meaningless)
            except ZeroDivisionError:
                sharpeRatio=float("nan")
    
        data={ "Ticker": self.ticker_name,
               "Strategy used": strategyUsed,
               "Starting cash": self.startingCashValue,
               "total net profit": round(self.totalProfit,3), 
               "MDD": mddMetric, 
               "Expectancy": expectancy,
               "Payoff Ratio": payoffRatio,
               "Profit Factor": profitFactor,
               "Sharpe Ratio": sharpeRatio ,
                                             } 
                              
        
        df=pd.DataFrame( data, index=[f"backtest run number {Engine.backtest_run_number}"] )
        
        return df

    def reset(self):
        self.listStoreEquityValues=[]
        self.cashValue=self.startingCashValue
        self.equity=0
        self.positionTrend=0
        self.entryPriceTrend=0
        self.exitPriceTrend=0
        self.profitTrend=0
        self.positionMeanReversion=0
        self.entryPriceMeanReversion=0
        self.exitPriceMeanReversion=0
        self.profitMeanReversion=0



if __name__=="__main__":
    engine_trend_strategy_apple=Engine(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
    engine_mean_rev_strategy_apple=Engine(trendMethod=False, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
    engine_trend_strategy_google=Engine(trendMethod=True, csv_ticker="data/google.csv", cashValue=10000, ticker_name="Google")
    engine_mean_rev_strategy_google=Engine(trendMethod=False, csv_ticker="data/google.csv", cashValue=10000, ticker_name="Google")
    engine_trend_strategy_microsoft=Engine(trendMethod=True, csv_ticker="data/microsoft.csv", cashValue=10000, ticker_name="Microsoft")
    engine_mean_rev_strategy_microsoft=Engine(trendMethod=False, csv_ticker="data/microsoft.csv", cashValue=10000, ticker_name="Microsoft") 
    print( pd.concat( [ engine_trend_strategy_apple.backtest_run(), 
                        engine_mean_rev_strategy_apple.backtest_run(),
                        engine_trend_strategy_google.backtest_run(),
                        engine_mean_rev_strategy_google.backtest_run(),
                        engine_trend_strategy_microsoft.backtest_run(),
                        engine_mean_rev_strategy_microsoft.backtest_run() ] ) ) 