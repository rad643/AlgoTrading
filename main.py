import data_loader as dl
import process_1_day
import dataclasses
import performanceMetrics
import pandas as pd


@dataclasses.dataclass
class ExecutionState:

    # instance field variables 
    trendMethod: bool
    csv_ticker: str
    cashValue: float
    ticker_name: str
    verbose_run: bool=False
    fixed_bps: float=0.0005
    flat_fee_per_share: float=0.005
    positionSizing: float=0
    listStoreEquityValues: list=dataclasses.field(default_factory=list)
    equity: int=0
    positionTrend: int=0
    entry_day: int=0
    exit_day: int=0
    entryPriceTrend: int=0
    exitPriceTrend: int =0
    profitTrend: int =0
    positionMeanReversion: int =0
    entryPriceMeanReversion: int =0
    exitPriceMeanReversion: int =0
    profitMeanReversion: int =0
    totalProfit: float=0
    positiveProfitTrend: int=0
    negativeProfitTrend: int=0
    positiveProfitMeanRev: int=0
    negativeProfitMeanRev: int=0
    numberTradesTrend: int=0
    numberTradesMeanRev: int=0
    totalProfitPositiveTradesTrend: float=0
    totalProfitNegativeTradesTrend: float=0
    totalProfitPositiveTradesMeanRev: float=0
    totalProfitNegativeTradesMeanRev: float=0
    pending_action: str=""

    backtest_run_number=0 # class variable (no type annotation)-> shared accross all ExecutionState instances 
    
    def __post_init__(self):
        self.startingCashValue=self.cashValue
        self.positionSizing=self.cashValue*0.2
        self.equity=self.cashValue


    def reset(self):
        self.listStoreEquityValues=[]
        self.cashValue=self.startingCashValue
        self.positionSizing=self.cashValue*0.2
        self.equity=self.cashValue
        self.positionTrend=0
        self.entry_day=0
        self.exit_day=0
        self.entryPriceTrend=0
        self.exitPriceTrend=0
        self.profitTrend=0
        self.positionMeanReversion=0
        self.entryPriceMeanReversion=0
        self.exitPriceMeanReversion=0
        self.profitMeanReversion=0
        self.totalProfit=0
        self.positiveProfitTrend=0
        self.negativeProfitTrend=0
        self.positiveProfitMeanRev=0
        self.negativeProfitMeanRev=0
        self.numberTradesTrend=0
        self.numberTradesMeanRev=0
        self.totalProfitPositiveTradesTrend=0
        self.totalProfitNegativeTradesTrend=0
        self.totalProfitPositiveTradesMeanRev=0
        self.totalProfitNegativeTradesMeanRev=0
        self.pending_action=""



class TradingEngine:

    @staticmethod
    def backtest_run(state): # state is an ExecutionState object 

        # first, reset all variables back to 0 in case you are reusing the same ExecutionState instance twice 
        state.reset()
        # list of dictionaries holding all the completed trades (1 full dictionary=1 fully completed trade)
        list_dictionaries_completed_trades=[]
        # list of dictionaries holding all the logged events 
        list_dictionaries_event_logs=[]
        # compute dictionary containing each single log-worthy event (1 dictionary= 1 event row)
        event_log={}
        # compute the dictionary for the BACKTEST_START logging event 
        event_log["run_number"]=ExecutionState.backtest_run_number+1
        event_log["day"]=None
        event_log["date"]=None
        event_log["ticker"]=state.ticker_name
        event_log["strategy"]="Trend" if state.trendMethod else "Mean Reversion"
        event_log["event_type"]="BACKTEST_START"
        event_log["message"]="Backtest started"
        event_log["cash"]=state.startingCashValue
        event_log["equity"]=state.equity
        event_log["position"]=state.positionTrend if state.trendMethod else state.positionMeanReversion
        event_log["execution_price"]=None
        event_log["pnl"]=None
        list_dictionaries_event_logs.append(event_log)


        # extract data from the csv file 
        generatorAverageDayDateClosingPrice=dl.read_ticker_csv(state.csv_ticker, state.cashValue, state.verbose_run)
        # 1 "for" loop iteration=1 day executed,  entire "for" loop iteration=1 full backtest run 
        for day,date,closingPrice,average,nextDayOpeningPrice in generatorAverageDayDateClosingPrice:
            #Days starting from day 3 onwards 
            if(average!=None):

                #TREND method
                if state.trendMethod:
                    #we only compute when there's a change in the profit 
                    previousProfitTrend=state.profitTrend
                    # before "process_1_day()" we hold no shares
                    previous_position=state.positionTrend 
                    # Process one trading day, update portfolio state, and print the day’s execution/output details
                    state.positionTrend, state.profitTrend, state.entryPriceTrend, state.exitPriceTrend, state.cashValue, state.equity, state.pending_action, state.entry_day, state.exit_day=process_1_day.process_one_day(state.verbose_run, day, date, closingPrice, average, nextDayOpeningPrice, state.cashValue, state.equity, state.pending_action, state.positionSizing, state.flat_fee_per_share, state.fixed_bps, state.trendMethod, state.positionTrend, state.entry_day, state.exit_day, state.entryPriceTrend, state.exitPriceTrend, state.profitTrend, state.positionMeanReversion, state.entryPriceMeanReversion, state.exitPriceMeanReversion, state.profitMeanReversion)
                    # a trade took place
                    if( (state.profitTrend-previousProfitTrend) !=0 ):
                        # create the dictionary containing 1 completed trade
                        one_completed_trade={}
                        one_completed_trade["run_number"]=ExecutionState.backtest_run_number+1
                        one_completed_trade["ticker"]=state.ticker_name
                        one_completed_trade["strategy"]="Trend" if state.trendMethod else "Mean Reversion"
                        one_completed_trade["entry_day"]=state.entry_day
                        one_completed_trade["entry_price"]=round(state.entryPriceTrend,3)
                        one_completed_trade["exit_day"]=state.exit_day
                        one_completed_trade["exit_price"]=round(state.exitPriceTrend,3)
                        one_completed_trade["profit"]=round(state.profitTrend,3)
                        one_completed_trade["return_pct"]=round(((state.exitPriceTrend-state.entryPriceTrend)/state.entryPriceTrend)*100,2)
                        # add it to the list of all dictionaries 
                        list_dictionaries_completed_trades.append(one_completed_trade)
                        #add 1 trading day's profit to the total net profit 
                        state.totalProfit+=state.profitTrend
                        #nb of total trades executed during Trend (total nb of P&L's) increases 
                        state.numberTradesTrend+=1
                        #P&L is positive 
                        if(state.profitTrend>0):
                            #count the nb of positive P&L trades
                            state.positiveProfitTrend+=1
                            #calculate total profit made out of positive P&L's
                            state.totalProfitPositiveTradesTrend+=state.profitTrend
                        #P&L is negative
                        else:
                            #count the nb of negative P&L trades 
                            state.negativeProfitTrend+=1
                            #calculate total profit made out of negative P&L's
                            state.totalProfitNegativeTradesTrend+=state.profitTrend

                    # after "process_1_day()" we might hold shares if we bought any 
                    current_position=state.positionTrend 
                    # we check if after "process_1_day()" we hold any shares or not compared to before "process_1_day()"
                    # if after "process_1_day()" we do hold shares, but before it we didn't =>
                    # we bought => we compute BUY_EXECUTED logging event 
                    if ( previous_position==0 and current_position>0 ):
                        # we compute the dictionary row for the BUY_EXECUTED logging event 
                        # reset event_log dict back to 0 so we can use it cleanly
                        event_log={}
                        event_log["run_number"]=ExecutionState.backtest_run_number+1
                        event_log["day"]=day
                        event_log["date"]=date
                        event_log["ticker"]=state.ticker_name
                        event_log["strategy"]="Trend" 
                        event_log["event_type"]="BUY_EXECUTED"
                        event_log["message"]="A Buy has been executed"
                        event_log["cash"]=state.cashValue 
                        event_log["equity"]=state.equity
                        event_log["position"]=state.positionTrend
                        event_log["execution_price"]=state.entryPriceTrend 
                        event_log["pnl"]=None
                        list_dictionaries_event_logs.append(event_log)
                    # if after "process_1_day()" we don't hold any shares anymore, but before it we did =>
                    # we sold => we compute SELL_EXECUTED logging event 
                    if ( previous_position>0 and current_position==0 ):
                        # we compute the dictionary row for the BUY_EXECUTED logging event 
                        # reset event_log dict back to 0 so we can use it cleanly
                        event_log={}
                        event_log["run_number"]=ExecutionState.backtest_run_number+1
                        event_log["day"]=day
                        event_log["date"]=date
                        event_log["ticker"]=state.ticker_name
                        event_log["strategy"]="Trend" 
                        event_log["event_type"]="SELL_EXECUTED"
                        event_log["message"]="A Sell has been executed"
                        event_log["cash"]=state.cashValue 
                        event_log["equity"]=state.equity
                        event_log["position"]=state.positionTrend
                        event_log["execution_price"]=state.exitPriceTrend
                        event_log["pnl"]=state.profitTrend
                        list_dictionaries_event_logs.append(event_log)

                        # if a sell has been executed, then a fully completed trade took place => TRADE_CLOSED log event happens immediately after SELL_EXECUTED log event
                        # create the dictionary row for the TRADE_CLOSED logging event 
                        event_log={}
                        event_log["run_number"]=ExecutionState.backtest_run_number+1
                        event_log["day"]=day
                        event_log["date"]=date
                        event_log["ticker"]=state.ticker_name
                        event_log["strategy"]="Trend" 
                        event_log["event_type"]="TRADE_CLOSED"
                        event_log["message"]="A Trade has been executed"
                        event_log["cash"]=state.cashValue 
                        event_log["equity"]=state.equity
                        event_log["position"]=state.positionTrend
                        event_log["execution_price"]=state.exitPriceTrend 
                        event_log["pnl"]=state.profitTrend
                        list_dictionaries_event_logs.append(event_log)

                    #add trading day's equity to the equity curve 
                    state.listStoreEquityValues.append(state.equity)

                #MEAN REVERSION method 
                else:
                    #we only compute when there's a change in the profit 
                    previousProfitMeanReversion=state.profitMeanReversion
                    # before "process_1_day()" we hold no shares
                    previous_position=state.positionMeanReversion 
                    # Process one trading day, update portfolio state, and print the day’s execution/output details
                    state.positionMeanReversion, state.profitMeanReversion, state.entryPriceMeanReversion, state.exitPriceMeanReversion, state.cashValue, state.equity, state.pending_action,state.entry_day,state.exit_day=process_1_day.process_one_day(state.verbose_run, day, date, closingPrice, average, nextDayOpeningPrice, state.cashValue, state.equity, state.pending_action, state.positionSizing, state.flat_fee_per_share, state.fixed_bps, state.trendMethod, state.positionTrend, state.entry_day, state.exit_day, state.entryPriceTrend, state.exitPriceTrend, state.profitTrend, state.positionMeanReversion, state.entryPriceMeanReversion, state.exitPriceMeanReversion, state.profitMeanReversion)
                    # a trade took place 
                    if( (state.profitMeanReversion-previousProfitMeanReversion) !=0 ):
                        # create the dictionary containing 1 completed trade
                        one_completed_trade={}
                        one_completed_trade["run_number"]=ExecutionState.backtest_run_number+1
                        one_completed_trade["ticker"]=state.ticker_name
                        one_completed_trade["strategy"]="Trend" if state.trendMethod else "Mean Reversion"
                        one_completed_trade["entry_day"]=state.entry_day
                        one_completed_trade["entry_price"]=round(state.entryPriceMeanReversion,3)
                        one_completed_trade["exit_day"]=state.exit_day
                        one_completed_trade["exit_price"]=round(state.exitPriceMeanReversion,3)
                        one_completed_trade["profit"]=round(state.profitMeanReversion,3)
                        one_completed_trade["return_pct"]=round(((state.exitPriceMeanReversion-state.entryPriceMeanReversion)/state.entryPriceMeanReversion)*100,2)
                        # add it to the list of all dictionaries 
                        list_dictionaries_completed_trades.append(one_completed_trade)
                        #add 1 trading day's profit to the total net profit 
                        state.totalProfit+=state.profitMeanReversion
                        #nb of total trades executed during Mean Rev (total nb of P&L's) increases 
                        state.numberTradesMeanRev+=1
                        #P&L is positive 
                        if(state.profitMeanReversion>0):
                            #count the nb of positive P&L trades 
                            state.positiveProfitMeanRev+=1
                            #calculate total profit made out of positive P&L's
                            state.totalProfitPositiveTradesMeanRev+=state.profitMeanReversion
                        #P&L is negative 
                        else:
                            #count the nb of negative P&L trades 
                            state.negativeProfitMeanRev+=1
                            #calculate total profit made out of negative P&L's
                            state.totalProfitNegativeTradesMeanRev+=state.profitMeanReversion

                    # after "process_1_day()" we might hold shares if we bought any 
                    current_position=state.positionMeanReversion 
                    # we check if after "process_1_day()" we hold any shares or not compared to before "process_1_day()"
                    # if after "process_1_day()" we do hold shares, but before it we didn't =>
                    # we bought => we compute BUY_EXECUTED logging event 
                    if ( previous_position==0 and current_position>0 ):
                        # we compute the dictionary row for the BUY_EXECUTED logging event 
                        # reset event_log dict back to 0 so we can use it cleanly
                        event_log={}
                        event_log["run_number"]=ExecutionState.backtest_run_number+1
                        event_log["day"]=day
                        event_log["date"]=date
                        event_log["ticker"]=state.ticker_name
                        event_log["strategy"]="Mean Reversion" 
                        event_log["event_type"]="BUY_EXECUTED"
                        event_log["message"]="A Buy has been executed"
                        event_log["cash"]=state.cashValue 
                        event_log["equity"]=state.equity
                        event_log["position"]=state.positionMeanReversion
                        event_log["execution_price"]=state.entryPriceMeanReversion 
                        event_log["pnl"]=None
                        list_dictionaries_event_logs.append(event_log)

                    # if after "process_1_day()" we don't hold any shares anymore, but before it we did =>
                    # we sold => we compute SELL_EXECUTED logging event 
                    if ( previous_position>0 and current_position==0 ):
                        # we compute the dictionary row for the SELL_EXECUTED logging event 
                        # reset event_log dict back to 0 so we can use it cleanly
                        event_log={}
                        event_log["run_number"]=ExecutionState.backtest_run_number+1
                        event_log["day"]=day
                        event_log["date"]=date
                        event_log["ticker"]=state.ticker_name
                        event_log["strategy"]="Mean Reversion" 
                        event_log["event_type"]="SELL_EXECUTED"
                        event_log["message"]="A Sell has been executed"
                        event_log["cash"]=state.cashValue 
                        event_log["equity"]=state.equity
                        event_log["position"]=state.positionMeanReversion
                        event_log["execution_price"]=state.exitPriceMeanReversion 
                        event_log["pnl"]=state.profitMeanReversion 
                        list_dictionaries_event_logs.append(event_log)

                        # if a sell has been executed, then a fully completed trade took place => TRADE_CLOSED log event happens immediately after SELL_EXECUTED log event
                        # create the dictionary row for the TRADE_CLOSED logging event
                        event_log={}
                        event_log["run_number"]=ExecutionState.backtest_run_number+1
                        event_log["day"]=day
                        event_log["date"]=date
                        event_log["ticker"]=state.ticker_name
                        event_log["strategy"]="Mean Reversion" 
                        event_log["event_type"]="TRADE_CLOSED"
                        event_log["message"]="A Trade has been executed"
                        event_log["cash"]=state.cashValue 
                        event_log["equity"]=state.equity
                        event_log["position"]=state.positionMeanReversion
                        event_log["execution_price"]=state.exitPriceMeanReversion 
                        event_log["pnl"]=state.profitMeanReversion 
                        list_dictionaries_event_logs.append(event_log)

                    #add trading day's equity to the equity curve 
                    state.listStoreEquityValues.append(state.equity) 

            # Days 1 and 2 
            else:
                state.listStoreEquityValues.append(state.equity)

        # compute the dictionary for the BACKTEST_END logging event 
        event_log={}
        event_log["run_number"]=ExecutionState.backtest_run_number+1
        event_log["day"]=day
        event_log["date"]=date
        event_log["ticker"]=state.ticker_name
        event_log["strategy"]="Trend" if state.trendMethod else "Mean Reversion"
        event_log["event_type"]="BACKTEST_END"
        event_log["message"]="Backtest has ended"
        event_log["cash"]=state.cashValue
        event_log["equity"]=state.equity
        event_log["position"]=state.positionTrend if state.trendMethod else state.positionMeanReversion
        event_log["execution_price"]=None
        event_log["pnl"]=state.totalProfit
        list_dictionaries_event_logs.append(event_log)

        # data frame containing all of the 5 logging events (backtest_start,buy_executed,sell_executed,trade_closed,backtest_end) in the list converted into a pandas data frame
        loggingEventsDataFrame=pd.DataFrame(data=list_dictionaries_event_logs)
        # final data frame containing all the completed trades in the list converted into a pandas data frame
        tradesDataFrame=pd.DataFrame(data=list_dictionaries_completed_trades)
        # count the number of backtest runs at Class level (not per engine instance)
        ExecutionState.backtest_run_number+=1
        # 1 dimensional array representing all the raw daily equities 
        daily_equities=pd.Series(state.listStoreEquityValues)
        # equity peak so far for drawdown series computation 
        running_max=daily_equities.cummax()
        # compute drawdown values 
        drawdown=round(daily_equities-running_max,3)
        # compute drawdown values expressed as percentages 
        drawdown_pct=round(drawdown/running_max,2)
        # list of dictionaries holding all the drawdown series 
        list_dictionaries_rows_per_equity_drawdown_series=[]
        # create list of dictionaries for drawdown series (1 dictionary= 1 day)
        for i in range(len(state.listStoreEquityValues)): 
            dictionary_per_equity_row_drawdown_series={}
            dictionary_per_equity_row_drawdown_series["run_number"]=ExecutionState.backtest_run_number
            dictionary_per_equity_row_drawdown_series["ticker"]=state.ticker_name
            dictionary_per_equity_row_drawdown_series["strategy"]="Trend" if state.trendMethod else "Mean Reversion"
            dictionary_per_equity_row_drawdown_series["equity"]=state.listStoreEquityValues[i]
            dictionary_per_equity_row_drawdown_series["peak_so_far"]=running_max.iloc[i]
            dictionary_per_equity_row_drawdown_series["drawdown"]=drawdown.iloc[i]
            dictionary_per_equity_row_drawdown_series["drawdown_pct"]=drawdown_pct.iloc[i]
            list_dictionaries_rows_per_equity_drawdown_series.append(dictionary_per_equity_row_drawdown_series)
        # drawdown series final computed data frame from all dictionary rows 
        drawdown_series=pd.DataFrame(data=list_dictionaries_rows_per_equity_drawdown_series, index= [ f"day {i}" for i in range( 1,len(state.listStoreEquityValues)+1) ] )
        # equity curve final computed data frame from all dictionary rows 
        equityCurveDataFrame=drawdown_series[ ["run_number", "ticker", "strategy", "equity"] ]
        # single dictionary containing all structured data outputs's (run data frame, equity curve, trades, drawdown series, log events) final computed data frames 
        dictionary_data_frames={}
        dictionary_data_frames["log_events"]=loggingEventsDataFrame
        dictionary_data_frames["equity_curve"]=equityCurveDataFrame
        dictionary_data_frames["drawdown_series"]=drawdown_series
        dictionary_data_frames["trades"]=tradesDataFrame
        return dictionary_data_frames
    
    @staticmethod
    def performance_metrics_data_frame(state):

        #TREND method performance metrics computation 
        if state.trendMethod: 
            strategyUsed="Trend"
            mddMetric=performanceMetrics.mdd(state.listStoreEquityValues)
            try:
                expectancy=performanceMetrics.expectancy(state.positiveProfitTrend, state.numberTradesTrend, state.totalProfitPositiveTradesTrend, state.negativeProfitTrend, state.totalProfitNegativeTradesTrend)
            except ZeroDivisionError:
                expectancy=float("nan")
            try:
                payoffRatio=performanceMetrics.payoff_ratio(state.totalProfitPositiveTradesTrend, state.totalProfitNegativeTradesTrend, state.positiveProfitTrend, state.negativeProfitTrend)
            except ZeroDivisionError:
                payoffRatio=float("nan")
            try:
                profitFactor=performanceMetrics.profit_factor(state.totalProfitPositiveTradesTrend, state.totalProfitNegativeTradesTrend)
            except ZeroDivisionError:
                profitFactor=float("nan")
            try: 
                sharpeRatio=performanceMetrics.sharpe_ratio(state.listStoreEquityValues)
            #guard for the mathematically undefined case (std=0 means all returns are identical, so Sharpe is meaningless)
            except ZeroDivisionError:
                sharpeRatio=float("nan")
        # MEAN REVERSION method performance metrics computation 
        else:
            strategyUsed="Mean Reversion"
            mddMetric=performanceMetrics.mdd(state.listStoreEquityValues)
            try: 
                expectancy=performanceMetrics.expectancy(state.positiveProfitMeanRev, state.numberTradesMeanRev, state.totalProfitPositiveTradesMeanRev, state.negativeProfitMeanRev, state.totalProfitNegativeTradesMeanRev)
            except ZeroDivisionError:
                expectancy=float("nan")
            try:
                payoffRatio=performanceMetrics.payoff_ratio(state.totalProfitPositiveTradesMeanRev, state.totalProfitNegativeTradesMeanRev, state.positiveProfitMeanRev, state.negativeProfitMeanRev)
            except ZeroDivisionError:
                payoffRatio=float("nan")
            try:
                profitFactor=performanceMetrics.profit_factor(state.totalProfitPositiveTradesMeanRev, state.totalProfitNegativeTradesMeanRev)
            except ZeroDivisionError:
                profitFactor=float("nan")
            try: 
                sharpeRatio=performanceMetrics.sharpe_ratio(state.listStoreEquityValues)
            #guard for the mathematically undefined case (std=0 means all returns are identical, so Sharpe is meaningless)
            except ZeroDivisionError:
                sharpeRatio=float("nan")

        data={ "Ticker": state.ticker_name,
                "Strategy used": strategyUsed,
                "Starting cash": state.startingCashValue,
                "total net profit": round(state.totalProfit,3), 
                "MDD": mddMetric, 
                "Expectancy": expectancy,
                "Payoff Ratio": payoffRatio,
                "Profit Factor": profitFactor,
                "Sharpe Ratio": sharpeRatio ,
                                                } 
                              
        return pd.DataFrame( data, index=[f"backtest run number {ExecutionState.backtest_run_number}"] )

        
                    

class ExperimentRunner:

    # method running 5 different outputs: run data frame, trades data frame, equity curves, drawdown series, logs 
    def structured_data_outputs(self):
        
        # multiple ExecutionState objects representing multiple experiments with different configurated parameters 
        states=[    ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple"),
                    ExecutionState(trendMethod=False, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple"),
                    ExecutionState(trendMethod=True, csv_ticker="data/google.csv", cashValue=10000, ticker_name="Google"),
                    ExecutionState(trendMethod=False, csv_ticker="data/google.csv", cashValue=10000, ticker_name="Google"),
                    ExecutionState(trendMethod=True, csv_ticker="data/microsoft.csv", cashValue=10000, ticker_name="Microsoft"),
                    ExecutionState(trendMethod=False, csv_ticker="data/microsoft.csv", cashValue=10000, ticker_name="Microsoft") ]

        # list containing each 1 run data frame per ExecutionState object with corresponding parameters 
        data_frames_run=[]
        # list of all the equity curve data frames , 1 equity curve data frame corresponding to 1 ExecutionState object 
        equity_curves_logs=[]
        # list of all the drawdown series data frames , 1 drawdown serie data frame corresponding to 1 ExecutionState object 
        drawdown_series=[]
        # list of all the completed trades data frames , 1 trade data frame corresponding to 1 ExecutionState object
        trades=[]
        # list of all the log events data frames , 1 log event data frame corresponding to 1 ExecutionState object
        log_events=[]
        # 1 single final dictionary containing all 5 structured data outputs
        results={}

        # add each ExecutionState object to its corresponding structured data output 
        for state in states: 
            # call Trading Engine's backtest_run() method once per ExecutionState object, and store its returned dictionary
            dictionary_data_frames=TradingEngine.backtest_run(state)
            # extract all 4 outputs from that same "backtest_run(state)" result 
            equity_curves_logs.append(dictionary_data_frames["equity_curve"])
            drawdown_series.append(dictionary_data_frames["drawdown_series"])
            trades.append(dictionary_data_frames["trades"])
            log_events.append(dictionary_data_frames["log_events"])
            # run data frame computed using the performance metrics method 
            data_frames_run.append(TradingEngine.performance_metrics_data_frame(state))

        # run data frame made out of all the different Execution State objects's run data frames concatenated together
        final_data_frame_run=pd.concat( data_frames_run )
        # trades data frame made out of all the different Execution State objects's trade data frames concatenated together
        trades_df=pd.concat(trades)
        # equity curve data frame made out of all the different Execution State objects's equity curve data frames concatenated together
        equity_curves_df=pd.concat(equity_curves_logs)
        # drawdown series data frame made out of all the different Execution State objects's drawdown data frames concatenated together
        drawdown_series_df=pd.concat(drawdown_series)
        # log events data frame made out of all the different Execution State objects's log events data frames concatenated together
        log_events_df=pd.concat(log_events)

        # add all the final structured outputs to a single final returned dictionary, and make each structured output key-accessible
        results["Final Data Frame Run"]=final_data_frame_run
        results["Equity Curve"]=equity_curves_df
        results["Drawdown Series"]=drawdown_series_df
        results["Completed Trades"]=trades_df
        results["Log Events"]=log_events_df

        return results
    
    
if __name__=="__main__":
    experimentRunner=ExperimentRunner()
    results=experimentRunner.structured_data_outputs()
    print(results["Final Data Frame Run"])
    print(results["Completed Trades"])
    print(results["Drawdown Series"])
    print(results["Equity Curve"])
    print(results["Log Events"])
    