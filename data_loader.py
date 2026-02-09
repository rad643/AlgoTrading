import compute_average as ca

def read_ticker_csv(csv_path):
    '''
    opens the csv file and goes through it line by line 
    splits it so it can extract the day and the closing price corresponding to that day 
    days 1 and 2 averages are being neglected as they don't have a computed average yet
    we start printing the average once we reach day 3 
    
    :param csv_path: imported csv file
    '''
    with open(csv_path, 'r') as f:
        listStorePreviousClosingPrices=[]
        average=0
        header=f.readline() #reads and discards header
        for day,line in enumerate(f, start=1): #we enumerate through every line of the file starting at index=1 so that we can extract the day (starting from day 1)
            line=line.split(',') #columns: date, open, high, low, close, volume”
            closingPriceIndex=4 #index of close column 
            dateIndex=0 #index of date column 
            date=line[dateIndex] 
            closingPrice=float(line[closingPriceIndex]) #use close as trade price 
            if(day==1): #no average yet on day 1
                listStorePreviousClosingPrices.append(closingPrice) #store the closing price in the list
                print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: N/A | Action: NONE")
                yield(day,date,closingPrice,None)
                print("\n")
            elif(day==2): #no average yet on day 2
                listStorePreviousClosingPrices.append(closingPrice) #store the closing price in the list
                print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: N/A | Action: NONE")
                yield(day,date,closingPrice,None)
                print("\n")
            else: #i need to compute average 
                average=ca.averageUpToDay(listStorePreviousClosingPrices)#first compute the average of all days up until that day
                listStorePreviousClosingPrices.append(closingPrice)#and then store the closing price of the day
                yield(day,date,closingPrice,average) #and yield the result
        