def mean_rev_step(day:int, date:str, closingPrice:float, average:float, positionMeanReversion:int, entryPriceMeanReversion:float, exitPriceMeanReversion:float, profitMeanReversion:float)->tuple:
    """
    if trendMethod flag variable is set to false, we are buying and selling based on the Mean Rev signal method.
    it only handles 1 day at a time.
    prints to the screen the summary of the market on the current day.
    updates positionMeanReversion flag variable accordingly at the end of the day. 

    Args:
        day (int): current day
        date (str):curent date 
        closingPrice (float): price at which We Enter Or Exit The Market -> reference price 
        average (float):  average of all the closing prices up to the current day (excluding the current day's closing price)
        positionMeanReversion (int): 1/0 flag variable; if 1->SELL/HOLD    if 0->OUT/BUY
        entryPriceMeanReversion (float): closingPrice on the current day at which you bought 1 share based on Mean Reversion method
        exitPriceMeanReversion (float): closingPrice on the current day at which you sold 1 share based on Mean Reversion method
        profitMeanReversion (float): profit=exitPriceMeanReversion-entryPriceMeanReversion 

    Returns:
        tuple: if we have sold, bought, held, or just did nothing on the respective day => we know if we're in or out of the market, and if we've made any profit on that day.
    """
    if(closingPrice>average): #TREND says BUY, MEAN REVERSION says SELL

        if(positionMeanReversion==1): #and you bought before so you're already in 
            exitPriceMeanReversion=closingPrice
            profitMeanReversion=exitPriceMeanReversion-entryPriceMeanReversion
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | MeanRev: SELL | Position: {positionMeanReversion} | Exit: {format(exitPriceMeanReversion,".3f")} | P&L: {format(profitMeanReversion,".3f")}")
        if(positionMeanReversion==0): #but you've got nothing
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | MeanRev: OUT | Position: {positionMeanReversion}")
        positionMeanReversion=0
        
        print("\n")

    
    elif(closingPrice==average):  #TREND says do nothing, MEAN REVERSION says do nothing

        if(positionMeanReversion==1): #but you already bought earlier 
            print("Day %s | Date: %s | Close: %f | Avg: %.3f | MeanRev: HOLD | Position: %d | Entry: %.3f" % (day, date, closingPrice,average, positionMeanReversion, entryPriceMeanReversion) )
        if(positionMeanReversion==0): #and you don't have any assets anyway
            print("Day %s | Date: %s | Close: %f | Avg: %.3f | MeanRev: NONE | Position: %d" % (day, date, closingPrice,average, positionMeanReversion) )

        print("\n")

    
    else: #TREND says SELL, MEAN REVERSION says BUY

        if(positionMeanReversion==0):#but you haven't even bought yet, so you're not even in the market yet
            entryPriceMeanReversion=closingPrice #entry price is closing price of the day
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | MeanRev: BUY | Position: {positionMeanReversion} | Entry: {format(entryPriceMeanReversion,".3f")}")
        if(positionMeanReversion==1): #but you already bought before so you're already in the market 
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | MeanRev: HOLD | Position: {positionMeanReversion} | Entry: {format(entryPriceMeanReversion,".3f")}")
        positionMeanReversion=1 #you're in
        
        print("\n")
    
    return (positionMeanReversion, profitMeanReversion, entryPriceMeanReversion, exitPriceMeanReversion)