import helpers.indicators as ind

#initiliaze var
new_list=[]
currentPrice=0
currentDay=0
average=0
positionTrend=0
entryPriceTrend=0
exitPriceTrend=0
profitTrend=0
positionMeanReversion=0
entryPriceMeanReversion=0
exitPriceMeanReversion=0
profitMeanReversion=0
totalProfit=0

# def read_ticker_csv(csv_path):
#     with open(csv_path, 'r') as f:
        

#open file and print the BUY/SELL signals to the screen based on the respective trading method out of the 2  
with open("aapl_us_d.csv", 'r') as f:
    header=f.readline() #skips header 
    #go through every line of the file 
    for line in f: #line="2024-01-16,181.074,183.161,179.853,182.534,65996913" 
        line=line.split(',') #line=["2024-01-16","181.074","183.161","179.853","182.534","65996913"]
        closingPriceIndex = 4
        line[4]=float(line[closingPriceIndex])
        currentPrice=line[4]
        if(line[0]=="2024-01-16"):
            currentDay=1
            if(currentDay==1):
                print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: N/A | Action: NONE")
        else:
            currentDay+=1                
        new_list.append( (line[0],line[4]) ) #new_list=[    ("2024-01-16", 182.534)  ,  ("2024-01-17", 181.59) , ("2024-01-18", 187.50) , ("2024-01-19", 190.45) ]
        if(currentDay==2):
                print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: N/A | Action: NONE")
        elif(currentDay==1):
              continue
        else:
            average=ind.aaverage_up_to_n_day(currentDay,new_list)



            #first let's use TREND FOLLOWING method for BUY and SELL signals: 
            #second we're gonna use MEAN REVERSION method for BUY and SELL signals: 


            if(currentPrice>average): #TREND says BUY, MEAN REVERSION says SELL


                if(positionTrend==0): #but you havent yet bought
                    entryPriceTrend=line[4] #the entry price is the closing price 
                    print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: {format(average,".3f")} | Trend: BUY | Position: {positionTrend} | Entry: {format(entryPriceTrend,".3f")}")
                if(positionTrend==1): #but you already bought before so you're already in the market 
                    print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: {format(average,".3f")} | Trend: HOLD | Position: {positionTrend} | Entry: {format(entryPriceTrend,".3f")}")
                positionTrend=1 #you're in 

                if(positionMeanReversion==1): #and you bought before so you're already in 
                    exitPriceMeanReversion=line[4]
                    profitMeanReversion=exitPriceMeanReversion-entryPriceMeanReversion
                    totalProfit+=profitMeanReversion
                    print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: {format(average,".3f")} | MeanRev: SELL | Position: {positionMeanReversion} | Exit: {format(exitPriceMeanReversion,".3f")} | P&L: {format(profitMeanReversion,".3f")}")
                if(positionMeanReversion==0): #but you've got nothing
                    print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: {format(average,".3f")} | MeanRev: OUT | Position: {positionMeanReversion}")
                positionMeanReversion=0
                print("\n")


            elif(currentPrice==average):  #TREND says do nothing, MEAN REVERSION says do nothing


                if(positionTrend==1): #you already bought so you're already in 
                    print("Day %s | Date: %s | Close: %f | Avg: %.3f | Trend: HOLD | Position: %d | Entry: %.3f" % (currentDay,line[0],line[4],average, positionTrend, entryPriceTrend) ) 
                if(positionTrend==0): #you haven't yet bought so you're not even in the market yet
                    print("Day %s | Date: %s | Close: %f | Avg: %.3f | Trend: NONE | Position: %d" % (currentDay,line[0],line[4],average, positionTrend) ) 
            
                if(positionMeanReversion==1): #but you already bought earlier 
                    print("Day %s | Date: %s | Close: %f | Avg: %.3f | MeanRev: HOLD | Position: %d | Entry: %.3f" % (currentDay,line[0],line[4],average, positionMeanReversion, entryPriceMeanReversion) )
                if(positionMeanReversion==0): #and you don't have any assets anyway
                    print("Day %s | Date: %s | Close: %f | Avg: %.3f | MeanRev: NONE | Position: %d" % (currentDay,line[0],line[4],average, positionMeanReversion) )

                print("\n")


            else: #TREND says SELL, MEAN REVERSION says BUY


                if(positionTrend==1): #and you've bought before, so you're already in the market 
                    exitPriceTrend=line[4]
                    profitTrend=exitPriceTrend-entryPriceTrend
                    totalProfit+=profitTrend
                    print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: {format(average,".3f")} | Trend: SELL | Position: {positionTrend} | Exit: {format(exitPriceTrend,".3f")} | P&L: {format(profitTrend,".3f")}")
                if(positionTrend==0): #but you haven't even bought, so you're not even in the market yet 
                    print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: {format(average,".3f")} | Trend: OUT | Position: {positionTrend}") 
                positionTrend=0

                if(positionMeanReversion==0):#but you haven't even bought yet, so you're not even in the market yet
                    entryPriceMeanReversion=line[4] #entry price is closing price of the day
                    print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: {format(average,".3f")} | MeanRev: BUY | Position: {positionMeanReversion} | Entry: {format(entryPriceMeanReversion,".3f")}")
                if(positionMeanReversion==1): #but you already bought before so you're already in the market 
                    print(f"Day {currentDay} | Date: {line[0]} | Close: {line[4]} | Avg: {format(average,".3f")} | MeanRev: HOLD | Position: {positionMeanReversion} | Entry: {format(entryPriceMeanReversion,".3f")}")
                positionMeanReversion=1 #you're in
                print("\n")

    print(" {:.3f} ".format(totalProfit))
    



