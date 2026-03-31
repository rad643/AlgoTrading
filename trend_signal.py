def trend_step(day:int, date:str, closingPrice:float, average:float, nextDayOpeningPrice: float, cashValue:float, equity:float, pending_action: str, positionSizing: float, flat_fee_per_share: float, fixed_bps:float, positionTrend:int, entryPriceTrend:float, exitPriceTrend:float, profitTrend:float)->tuple:
    """
    Description: Executes any pending trading action from the previous day (buy or sell) 
    at the current days market opening price, updates portfolio variables (position, cash, equity, and realized profit),
    and determines the next pending trading signal based on the comparison between the current days closing price and the moving average.

    Args:
        day (int): current day 
        date (str): current date 
        closingPrice (float): closing price of the current day 
        average (float): average of all the closing prices up until the current day (current day's closing price excluded)
        nextDayOpeningPrice (float): execution price at which the trade takes place (sell/buy)
        cashValue (float): current amount of cash 
        equity (float): cash+assets (unrealized profit-value of the shares you currently hold changes based on the latest market price (e.g., the days closing price), without you actually selling them yet)
        pending_action (str): the trading signal determined from the current days prices, whose execution (buy/sell) occurs on the next day at the markets opening price.
        positionSizing (float): maximum amount of money allowed to spend
        flat_fee_per_share (float): the brokers commission charged for each individual share traded (both when buying and when selling).
        fixed_bps (float): a small percentage adjustment applied to the execution price to simulate slippage caused by market frictions and volatility.
        positionTrend (int): number of shares that you currently own (assets)
        entryPriceTrend (float): price at which you buy 
        exitPriceTrend (float): price at which you sell 
        profitTrend (float): realized profit=(exitPriceTrend-entryPriceTrend) * number_of_shares.

    Returns:
        tuple: Updated portfolio state after processing the current day, including the 
        current position (shares held), realized profit, entry and exit prices, remaining cash, current equity (cash + unrealized value of held shares),
        and the pending action signal that will be executed at the next days market opening.
    """

    #pending_action needs to be a string and in {"BUY", "SELL", "HOLD", ""}
    if not isinstance(pending_action, str):
        raise TypeError
    if not pending_action in {"BUY", "SELL", "HOLD", ""}:
        raise ValueError
    
    #cashValue needs to be either integer or float, and it can't be negative or zero 
    if not isinstance( cashValue, (int,float) ): 
        raise TypeError
    if cashValue<=0:
        raise ValueError
    

    #we start by checking for any action signals pending from the day before that need to be executed today based on today's opening price 


    #if we have a pending signal from the day before that told us to BUY today, we buy at the opening price of today's market 
    if(pending_action=="BUY"):

        #and you have no shares => BUY
        if(positionTrend==0): 

            #the price at which you're buying the shares today is the opening price of the market + slippage execution->fixed bias points=0.05% due to market volatility
            entryPriceTrend=round(nextDayOpeningPrice+(fixed_bps*nextDayOpeningPrice),3)
            #this tells you how many shares you can buy depending on your allowed budget
            positionTrend=positionSizing//entryPriceTrend  
            #subtract the number of shares bought and the comission fee for the broker which is applied by share
            cashValue=round(cashValue-(positionTrend*entryPriceTrend)-(positionTrend*flat_fee_per_share), 3)
            #unrealized profit 
            equity=round(cashValue+(positionTrend*closingPrice) ,3)

            #now we need to check what the signal will be regarding tomorrow's required execution action and update it accordingly, and then print it to the screen 

            #TREND says BUY
            if(closingPrice>average): 
                #update pending action for tomorrow accordingly 
                pending_action="BUY"

            #TREND says SELL 
            elif(closingPrice<average): 
                #update pending action for tomorrow accordingly 
                pending_action="SELL"

            #TREND says HOLD
            else: 
                #update pending action for tomorrow accordingly
                pending_action="HOLD"

            #print to the screen what the current day is doing; all variables with the exception of "pending_action" represent today's state
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Execution price: {entryPriceTrend} | Avg: {format(average,".3f")} | Trend: {pending_action} | Position: {positionTrend} | Cash: {cashValue} | Equity: {equity}")

        #but you already own shares=> HOLD => nothing gets updated other than your equity (unrealized profit)
        else: 
            #unrealized profit
            equity=round(cashValue+(positionTrend*closingPrice),3)

            #now we need to check what the signal will be regarding tomorrow's required execution action and update it accordingly, and then print it to the screen 

            #TREND says BUY
            if(closingPrice>average): 
                #update pending action for tomorrow accordingly 
                pending_action="BUY"

            #TREND says SELL 
            elif(closingPrice<average): 
                #update pending action for tomorrow accordingly 
                pending_action="SELL"

            #TREND says HOLD
            else: 
                #update pending action for tomorrow accordingly
                pending_action="HOLD"

            #print to the screen what the current day is doing; all variables with the exception of "pending_action" represent today's state 
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | Trend: {pending_action} | Position: {positionTrend} | Cash: {cashValue} | Equity: {equity}")
        print("\n")



    #if we have a pending signal from the day before that told us to SELL today, we SELL at the opening price of today's market
    elif(pending_action=="SELL"):

        #and you own multiple shares => sell everything you have
        if(positionTrend!=0):  

            #the exit price is the opening price of the market - slippage execution->fixed bias points=0.05% due to market volatility
            exitPriceTrend=round(nextDayOpeningPrice-(fixed_bps*nextDayOpeningPrice) ,3)
            #realized profit is the price at which you sold on the corresponding day - the price at which you bought them initially 
            profitTrend=round(((exitPriceTrend*positionTrend)-(entryPriceTrend*positionTrend)),3)  #profitTrend is always gross
            #cash value is gonna be price at which you sold the shares - the comission fee for the broker which is applied per share
            cashValue=round(cashValue+(positionTrend*exitPriceTrend)-(positionTrend*flat_fee_per_share),3)  #cashValue is net
            #we sold everything so we now own zero shares 
            positionTrend=0
            #unrealized profit 
            equity=round(cashValue+(positionTrend*closingPrice),3)

            #now we need to check what the signal will be regarding tomorrow's required execution action and update it accordingly, and then print it to the screen 

            #TREND says BUY
            if(closingPrice>average): 
                #update pending action for tomorrow accordingly 
                pending_action="BUY"

            #TREND says SELL 
            elif(closingPrice<average): 
                #update pending action for tomorrow accordingly 
                pending_action="SELL"

            #TREND says HOLD
            else: 
                #update pending action for tomorrow accordingly
                pending_action="HOLD"

            #print to the screen what the current day is doing; all variables with the exception of "pending_action" represent today's state
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Execution price: {exitPriceTrend} | Avg: {format(average,".3f")} | Trend: {pending_action} | Position: {positionTrend} | Cash: {cashValue} | Equity: {equity} | P&L: {format(profitTrend,".3f")}")

        #but you don't own any shares so you got nothing to sell => HOLD => nothing gets updated other than your equity (unrealized profit)
        else: 
            #unrealized profit 
            equity=round(cashValue+(positionTrend*closingPrice),3)

            #now we need to check what the signal will be regarding tomorrow's required execution action and update it accordingly, and then print it to the screen 

            #TREND says BUY
            if(closingPrice>average): 
                #update pending action for tomorrow accordingly 
                pending_action="BUY"

            #TREND says SELL 
            elif(closingPrice<average): 
                #update pending action for tomorrow accordingly 
                pending_action="SELL"

            #TREND says HOLD
            else: 
                #update pending action for tomorrow accordingly
                pending_action="HOLD"

            #print to the screen what the current day is doing; all variables with the exception of "pending_action" represent today's state
            print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | Trend: {pending_action} | Position: {positionTrend} | Cash: {cashValue} | Equity: {equity}")
        print("\n")



    #if we have a pending signal from the day before that told us to HOLD today, we HOLD and do nothing => nothing gets updated other than your equity (unrealized profit) 
    elif(pending_action=="HOLD"):

        #unrealized profit
        equity=round(cashValue+(positionTrend*closingPrice) ,3)

        #now we need to check what the signal will be regarding tomorrow's required execution action and update it accordingly, and then print it to the screen 

        #TREND says BUY
        if(closingPrice>average): 
            #update pending action for tomorrow accordingly 
            pending_action="BUY"

        #TREND says SELL 
        elif(closingPrice<average): 
            #update pending action for tomorrow accordingly 
            pending_action="SELL"

        #TREND says HOLD
        else: 
            #update pending action for tomorrow accordingly
            pending_action="HOLD"

        #print to the screen what the current day is doing; all variables with the exception of "pending_action" represent today's state
        print("Day %s | Date: %s | Close: %f | Avg: %.3f | Trend: %s | Position: %d | Cash: %.3f | Equity: %.3f" % (day, date, closingPrice, average, pending_action, positionTrend, cashValue, equity))  
        print("\n")


    
    #this is an edge case where we have no pending signal coming from the previous day => nothing gets updated other than your equity (unrealized profit)  
    elif(pending_action==""):

        #unrealized profit
        equity=round(cashValue+(positionTrend*closingPrice),3)

        #now we need to check what the signal will be regarding tomorrow's required execution action and update it accordingly, and then print it to the screen

        #TREND says BUY
        if(closingPrice>average): 
            #update pending action for tomorrow accordingly 
            pending_action="BUY"

        #TREND says SELL 
        elif(closingPrice<average): 
            #update pending action for tomorrow accordingly 
            pending_action="SELL"

        #TREND says HOLD
        else: 
            #update pending action for tomorrow accordingly
            pending_action="HOLD"  
                
        #print to the screen what the current day is doing; all variables with the exception of "pending_action" represent today's state    
        print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: {format(average,".3f")} | Trend: {pending_action} | Position: {positionTrend} | Cash: {cashValue} | Equity: {equity}")
        print("\n")



    #return the required values for tomorrow's execution day 
    return (positionTrend, profitTrend, entryPriceTrend, exitPriceTrend, cashValue, equity, pending_action)
    
     

