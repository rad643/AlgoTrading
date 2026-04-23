import compute_average as ca 

def read_ticker_csv(csv_path, cashValue, verbose_run):
    '''
    opens the csv file and goes through it line by line 
    splits it so it can extract the day and the closing price corresponding to that day 
    days 1 and 2 averages are being neglected as they don't have a computed average yet
    we start printing the average once we reach day 3 
    
    :param csv_path: imported csv file
    '''
    with open(csv_path, 'r') as f:
        listStorePreviousClosingPrices=[]
        header=f.readline() #reads and discards header
        for day,line in enumerate(f, start=1): #we enumerate through every line of the file starting at index=1 so that we can extract the day (starting from day 1)
            line=line.split(',') #columns: date, open, high, low, close, volume”
            closingPriceIndex=4 #index of close column 
            openingPriceIndex=1 #index opening price column 
            dateIndex=0 #index of date column 
            date=line[dateIndex] 
            closingPrice=float(line[closingPriceIndex]) #use close as trade price 
            nextDayOpeningPrice=float(line[openingPriceIndex]) #next bar execution: buy/sell at next day's opening price 
            if(day==1): #no average yet on day 1
                listStorePreviousClosingPrices.append(closingPrice) #store the closing price in the list
                if verbose_run:
                    print("Position sizing rule: 20% of available cash")
                    print("Fixed bias points model: 0.05% of the execution price")
                    print("Commission model: $0.005 per share (flat)\n")
                    print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: N/A | Action: NONE | Position: 0 | Cash: {cashValue} | Equity: {cashValue}")
                    print("\n")
                yield(day,date,closingPrice,None,None)
            elif(day==2): #no average yet on day 2
                listStorePreviousClosingPrices.append(closingPrice) #store the closing price in the list
                if verbose_run:
                    print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: N/A | Action: NONE | Position: 0 | Cash: {cashValue} | Equity: {cashValue}")
                    print("\n")
                yield(day,date,closingPrice,None,None)
            else: #i need to compute average 
                average=ca.averageUpToDay(listStorePreviousClosingPrices)#first compute the average of all days up until that day
                listStorePreviousClosingPrices.append(closingPrice)#and then store the closing price of the day
                yield(day,date,closingPrice,average, nextDayOpeningPrice) #and yield the result
        