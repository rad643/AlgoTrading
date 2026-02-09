def trend_step(day:int,date:str,closingPrice:float,average:float, positionTrend:int, entryPriceTrend:float, exitPriceTrend:float, profitTrend:float)->tuple:
    """
    if trendMethod flag variable is set to true, we are buying and selling based on the Trend signal method.
    it only handles 1 day at a time.
    prints to the screen the summary of the market on the current day.
    updates positionTrend flag variable accordingly at the end of the day. 

    Args:
        day (int): current day 
        date (str): current date 
        closingPrice (float): price at which We Enter Or Exit The Market -> reference price 
        average (float): average of all the closing prices up to the current day (excluding the current day's closing price)
        positionTrend (int): 1/0 flag variable; if 1->HOLD/SELL    if 0->BUY/OUT
        entryPriceTrend (float): closingPrice on the current day at which you bought 1 share based on Trend method
        exitPriceTrend (float): closingPrice on the current day at which you sold 1 share based on Trend method
        profitTrend (float): profit=exitPriceTrend-entryPriceTrend

    Returns:
        tuple: if we have sold, bought, held, or just did nothing on the respective day => we know if we're in or out of the market, and if we've made any profit on that day. 
    """
    if(closingPrice>average): #TREND says BUY
            
        if(positionTrend==0): #but you havent yet bought
            entryPriceTrend=closingPrice #the entry price is the closing price 
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | Trend: BUY | Position: {positionTrend} | Entry: {format(entryPriceTrend,".3f")}")
        if(positionTrend==1): #but you already bought before so you're already in the market 
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | Trend: HOLD | Position: {positionTrend} | Entry: {format(entryPriceTrend,".3f")}")
        positionTrend=1 #you're in 

        print("\n")

    elif(closingPrice==average):  #TREND says do nothing
            
        if(positionTrend==1): #you already bought so you're already in 
            print("Day %s | Date: %s | Close: %f | Avg: %.3f | Trend: HOLD | Position: %d | Entry: %.3f" % (day, date, closingPrice, average, positionTrend, entryPriceTrend) ) 
        if(positionTrend==0): #you haven't yet bought so you're not even in the market yet
            print("Day %s | Date: %s | Close: %f | Avg: %.3f | Trend: NONE | Position: %d" % (day, date, closingPrice, average, positionTrend) ) 

        print("\n")
            
    else: #TREND says SELL
        
        if(positionTrend==1): #and you've bought before, so you're already in the market 
            exitPriceTrend=closingPrice
            profitTrend=exitPriceTrend-entryPriceTrend
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | Trend: SELL | Position: {positionTrend} | Exit: {format(exitPriceTrend,".3f")} | P&L: {format(profitTrend,".3f")}")
        if(positionTrend==0): #but you haven't even bought, so you're not even in the market yet 
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | Trend: OUT | Position: {positionTrend}") 
        positionTrend=0

        print("\n")
    
    return (positionTrend, profitTrend, entryPriceTrend, exitPriceTrend)
    
     

