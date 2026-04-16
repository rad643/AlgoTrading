import data_loader as dl
import process_1_day
import dataclasses
import performanceMetrics
import pandas as pd

@dataclasses.dataclass
class Engine:
    """
    Current engine behaviour (step 9):

    - The strategy allows multiple shares with position sizing
    - position sizing will be 20% of the initial starting cash value 
    - you can buy as many shares as the posiition sizing allows. (position sizing/closing price)
    - totalProfit represents cumulative realized profit.
    - realized Profit is only computed during the sell signals. 
    - during the sell signals, we sell all of the shares that we currently hold (position=nb of shares), so after a sell day position becomes 0 
    - Unrealized profit while holding a position is included via the equity variable (when we're holding and the current closing price of the day increases/decreases)
    - Profit is not calculated per day — only per completed trade. (selling all shares->position=0)
    
    """
    pending_action: str=''
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
    trendMethod: bool=True

    def execution_per_day(self,cashValue)->float:
        self.positionSizing=cashValue*0.2
        self.equity=cashValue
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
        generatorAverageDayDateClosingPrice=dl.read_ticker_csv("data/aapl_us_d.csv", cashValue)
        for day,date,closingPrice,average,nextDayOpeningPrice in generatorAverageDayDateClosingPrice:

            #Days starting from day 3 onwards 
            if(average!=None):

                #TREND strategy
                if(self.trendMethod):

                    #we only compute when there's a change in the profit 
                    previousProfitTrend=self.profitTrend
                    # Process one trading day, update portfolio state, and print the day’s execution/output details
                    self.positionTrend, self.profitTrend, self.entryPriceTrend, self.exitPriceTrend, cashValue, self.equity, self.pending_action=process_1_day.process_one_day(day, date, closingPrice, average, nextDayOpeningPrice, cashValue, self.equity, self.pending_action, self.positionSizing, self.flat_fee_per_share, self.fixed_bps, self.trendMethod, self.positionTrend, self.entryPriceTrend, self.exitPriceTrend, self.profitTrend, self.positionMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, self.profitMeanReversion)  
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
                    self.positionMeanReversion, self.profitMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, cashValue, self.equity, self.pending_action=process_1_day.process_one_day(day, date, closingPrice, average, nextDayOpeningPrice, cashValue, self.equity, self.pending_action, self.positionSizing, self.flat_fee_per_share, self.fixed_bps, self.trendMethod, self.positionTrend, self.entryPriceTrend, self.exitPriceTrend, self.profitTrend, self.positionMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, self.profitMeanReversion)
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

        #trading finished => evaluate portfolio performance following either Trend or Mean Reversion strategy 
        #MDD metric computation 
        #Expectancy metric computation   
        #Payoff Ratio metric computation
        #Profit Factor metric computation
        #Sharpe Ratio metric computation 
        if self.trendMethod:
            mddMetric=performanceMetrics.mdd(self.listStoreEquityValues)
            expectancy=performanceMetrics.expectancy(positiveProfitTrend, numberTradesTrend, totalProfitPositiveTradesTrend, negativeProfitTrend, totalProfitNegativeTradesTrend)
            payoffRatio=performanceMetrics.payoff_ratio(totalProfitPositiveTradesTrend, totalProfitNegativeTradesTrend, positiveProfitTrend, negativeProfitTrend)
            profitFactor=performanceMetrics.profit_factor(totalProfitPositiveTradesTrend, totalProfitNegativeTradesTrend)
            sharpeRatio=performanceMetrics.sharpe_ratio(self.listStoreEquityValues)
        else:
            mddMetric=performanceMetrics.mdd(self.listStoreEquityValues)
            expectancy=performanceMetrics.expectancy(positiveProfitMeanRev, numberTradesMeanRev, totalProfitPositiveTradesMeanRev, negativeProfitMeanRev, totalProfitNegativeTradesMeanRev)
            payoffRatio=performanceMetrics.payoff_ratio(totalProfitPositiveTradesMeanRev, totalProfitNegativeTradesMeanRev, positiveProfitMeanRev, negativeProfitMeanRev)
            profitFactor=performanceMetrics.profit_factor(totalProfitPositiveTradesMeanRev, totalProfitNegativeTradesMeanRev)
            sharpeRatio=performanceMetrics.sharpe_ratio(self.listStoreEquityValues)

        round(self.totalProfit,3), mddMetric, expectancy, payoffRatio, profitFactor, sharpeRatio
    
        data={ "total net profit": round(self.totalProfit,3), 
               "MDD": mddMetric, 
               "Expectancy": expectancy,
               "Payoff Ratio": payoffRatio,
               "Profit Factor": profitFactor,
               "Sharpe Ratio": sharpeRatio ,
                                             } 
                              
        
        df=pd.DataFrame(data, index=[0])

        return(df)

if __name__=="__main__":
    initial_amount_cash_to_start_with=10000
    engine=Engine()
    print(engine.execution_per_day(initial_amount_cash_to_start_with))