import data_loader as dl
import process_1_day as pd

class Engine:
    def __init__(self, positionTrend=0, entryPriceTrend=0, exitPriceTrend=0, profitTrend=0, positionMeanReversion=0, entryPriceMeanReversion=0, exitPriceMeanReversion=0, profitMeanReversion=0,trendMethod=False)->None:
        self.positionTrend=positionTrend
        self.entryPriceTrend=entryPriceTrend
        self.exitPriceTrend=exitPriceTrend
        self.profitTrend=profitTrend
        self.positionMeanReversion=positionMeanReversion
        self.entryPriceMeanReversion=entryPriceMeanReversion
        self.exitPriceMeanReversion=exitPriceMeanReversion
        self.profitMeanReversion=profitMeanReversion
        self.trendMethod=trendMethod

    def execution_per_day(self)->float:
        self.totalProfit=0
        generatorAverageDayDateClosingPrice=dl.read_ticker_csv("aapl_us_d.csv")
        for day,date,closingPrice,average in generatorAverageDayDateClosingPrice:
            if(average!=None):
                if(self.trendMethod):
                    self.positionTrend, self.profitTrend, self.entryPriceTrend, self.exitPriceTrend=pd.process_one_day(day,date,closingPrice,average,self.trendMethod,self.positionTrend, self.entryPriceTrend, self.exitPriceTrend, self.profitTrend, self.positionMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, self.profitMeanReversion)
                    self.totalProfit+=self.profitTrend
                else:
                    self.positionMeanReversion, self.profitMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion=pd.process_one_day(day,date,closingPrice,average,self.trendMethod,self.positionTrend, self.entryPriceTrend, self.exitPriceTrend, self.profitTrend, self.positionMeanReversion, self.entryPriceMeanReversion, self.exitPriceMeanReversion, self.profitMeanReversion)
                    self.totalProfit+=self.profitMeanReversion
            else:#average=none so we skip days 1 and 2 
                continue 
            
        return self.totalProfit

engine1=Engine()
print(" {:.3f} ".format(engine1.execution_per_day()))


#if __name__=="__main__":
    #main.py()