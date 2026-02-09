import data_loader as dl
import process_1_day as pd

trendMethod=True #choose which signaling method you wanna use based on the flag

positionTrend=0
entryPriceTrend=0
exitPriceTrend=0
profitTrend=0
totalProfit=0

positionMeanReversion=0
entryPriceMeanReversion=0
exitPriceMeanReversion=0
profitMeanReversion=0

generatorAverageDayDateClosingPrice=dl.read_ticker_csv("aapl_us_d.csv") #referencing the generator object that we're gonna yield values from 

#first let's use TREND FOLLOWING method for BUY and SELL signals: 
#second we're gonna use MEAN REVERSION method for BUY and SELL signals: 

for day,date,closingPrice,average in generatorAverageDayDateClosingPrice: #unloading the tuple yielded by the generator object into variables
#and iterating through every line of the file until reaching the eof 

    if(average!=None): #average=none inside the tuple for days 1 and 2
#so we need to start from day 3 

        if(trendMethod):
            positionTrend, profitTrend, entryPriceTrend, exitPriceTrend=pd.process_one_day(day,date,closingPrice,average,trendMethod,positionTrend, entryPriceTrend, exitPriceTrend, profitTrend, positionMeanReversion, entryPriceMeanReversion,exitPriceMeanReversion, profitMeanReversion)
            totalProfit+=profitTrend
        else:
            positionMeanReversion, profitMeanReversion, entryPriceMeanReversion, exitPriceMeanReversion=pd.process_one_day(day,date,closingPrice,average,trendMethod,positionTrend, entryPriceTrend, exitPriceTrend, profitTrend, positionMeanReversion, entryPriceMeanReversion,exitPriceMeanReversion, profitMeanReversion)
            totalProfit+=profitMeanReversion

    
    else:#average=none so we skip days 1 and 2 
        continue 


print(" {:.3f} ".format(totalProfit))
    

#if __name__ == "__main__":
#run_backtest()
