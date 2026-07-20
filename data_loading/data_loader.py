import json
import pandas as pd
import requests
import time  
import data_loading.compute_average as ca 

url_path="https://data.alpaca.markets/v2/stocks/bars"

credentials= open(".env", 'r').read()  

headers=json.loads(credentials) 

def hist_data(tickers, timeframe= "15Min", start= '', end='' , limit= 1000):
    """_summary_

    Args:
        tickers (_type_): _description_
        timeframe (str, optional): _description_. Defaults to "15Min".
        start (str, optional): _description_. Defaults to ''.
        end (str, optional): _description_. Defaults to ''.
        limit (int, optional): _description_. Defaults to 1000.
    """

    params = {"symbols": tickers,
              "timeframe": timeframe, 
              "start": start, 
              "end": end, 
              "limit": limit}
    bars={}
    while True: 
        r = requests.get(url=url_path, headers= headers, params= params)
        data= r.json()
        for ticker in data['bars']:
            if ticker not in bars:
                bars[ticker] = []
            bars[ticker] += data['bars'][ticker]
        if data['next_page_token'] == None: 
            break
        else:
            params['page_token']= data['next_page_token']
    d={}
    for ticker in bars:
        ticker_df= pd.DataFrame(bars[ticker])
        ticker_df.rename(columns= {"c": "close", "h": "high", "l": "low", "o": "open", "v": "volume", 't': 'time'} , inplace=True)
        ticker_df['time']= pd.to_datetime(ticker_df['time'])
        ticker_df.set_index('time', inplace=True)
        ticker_df.index = ticker_df.index.tz_convert("America/New_York")
        d[ticker] = ticker_df

    return d 
        

def read_ticker_csv(one_df, cashValue, verbose_run):

    listStorePreviousClosingPrices=[]
    
    for day, row in enumerate(one_df.itertuples(), 1):
        date = row.Index.date()
        closingPrice = row.close
        openingPrice = row.open
        if(day==1):
            listStorePreviousClosingPrices.append(closingPrice)
            if verbose_run:
                print("Position sizing rule: 20% of available cash")
                print("Fixed bias points model: 0.05% of the execution price")
                print("Commission model: $0.005 per share (flat)\n")
                print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: N/A | Action: NONE | Position: 0 | Cash: {cashValue} | Equity: {cashValue}")
                print("\n")
            yield(day,date,closingPrice,None,None)
        elif(day==2):
            listStorePreviousClosingPrices.append(closingPrice)
            if verbose_run:
                print(f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: N/A | Action: NONE | Position: 0 | Cash: {cashValue} | Equity: {cashValue}")
                print("\n")
            yield(day,date,closingPrice,None,None)
        else:
            average=ca.averageUpToDay(listStorePreviousClosingPrices)
            listStorePreviousClosingPrices.append(closingPrice)
            yield(day,date,closingPrice,average, openingPrice)
