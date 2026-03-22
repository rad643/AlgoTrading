import data_loader as dl
import process_1_day as pd
import dataclasses

@dataclasses.dataclass
class Engine:
    """
    Current engine behaviour (step 8):

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
        generatorAverageDayDateClosingPrice=dl.read_ticker_csv("position_sizing.csv", cashValue)
        for day,date,closingPrice,average,nextDayOpeningPrice in generatorAverageDayDateClosingPrice:
            if(average!=None):
                if(self.trendMethod):
                    previousProfitTrend=self.profitTrend
                    self.positionTrend, self.profitTrend, self.entryPriceTrend, self.exitPriceTrend, cashValue, self.equity, self.pending_action=pd.process_one_day(day, date, closingPrice, average, nextDayOpeningPrice, cashValue, self.equity, self.pending_action, self.positionSizing, self.flat_fee_per_share, self.fixed_bps, self.trendMethod, self.positionTrend, self.entryPriceTrend, self.exitPriceTrend, self.profitTrend, self.positionMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, self.profitMeanReversion)
                    # We track only NEW realized profit per iteration.
                    # process_one_day returns cumulative realized profit.
                    # To avoid double-counting, we compute the delta between:
                    #   - profit before this day
                    #   - profit after this day
                    # If a SELL occurred, delta != 0.
                    # If no trade occurred (HOLD/OUT), delta == 0.
                    # We add only the delta to totalProfit.
                    if( (self.profitTrend-previousProfitTrend) !=0 ):
                        self.totalProfit+=(self.profitTrend-previousProfitTrend)
                    self.listStoreEquityValues.append(self.equity)
                else:
                    previousProfitMeanReversion=self.profitMeanReversion
                    self.positionMeanReversion, self.profitMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, cashValue, self.equity, self.pending_action=pd.process_one_day(day, date, closingPrice, average, nextDayOpeningPrice, cashValue, self.equity, self.pending_action, self.positionSizing, self.flat_fee_per_share, self.fixed_bps, self.trendMethod, self.positionTrend, self.entryPriceTrend, self.exitPriceTrend, self.profitTrend, self.positionMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, self.profitMeanReversion)
                    if( (self.profitMeanReversion-previousProfitMeanReversion) !=0 ):
                        self.totalProfit+=(self.profitMeanReversion-previousProfitMeanReversion)
            else:#average=none so we skip days 1 and 2 and just append the corresponding equities to the list 
                self.listStoreEquityValues.append(self.equity)
            
        return self.totalProfit

if __name__=="__main__":
    initial_amount_cash_to_start_with=100
    engine1=Engine()
    print(engine1.execution_per_day(initial_amount_cash_to_start_with))