import data_loader as dl
import process_1_day
import dataclasses
import performanceMetrics
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@dataclasses.dataclass
class ExecutionState:
    """
    Mutable state for one backtest run.

    One ExecutionState object represents:
    - one ticker
    - one strategy choice
    - one starting cash value
    - one full backtest run state

    Core config:
        trendMethod:
            True = Trend strategy.
            False = Mean Reversion strategy.

        csv_ticker:
            Path to the CSV file used for this run.

        cashValue:
            Current available cash during the run.

        ticker_name:
            Human-readable ticker name used in output DataFrames.

        verbose_run:
            If True, prints daily backtest output.

    Execution costs:
        fixed_bps:
            Slippage percentage applied to entry/exit execution price.

        flat_fee_per_share:
            Commission charged per share.

    Portfolio state:
        positionSizing:
            Maximum cash allocated per trade. Set to 20% of starting cash.

        listStoreEquityValues:
            Stores daily equity values for equity curve, drawdown, and Sharpe ratio.

        equity:
            Current portfolio value = cash + market value of held shares.

    Trade state:
        positionTrend / positionMeanReversion:
            Number of shares currently held for each strategy.

        entry_day / exit_day:
            Day number of the latest trade entry and exit.

        entryPriceTrend / exitPriceTrend:
            Entry and exit prices for Trend trades.

        entryPriceMeanReversion / exitPriceMeanReversion:
            Entry and exit prices for Mean Reversion trades.

        profitTrend / profitMeanReversion:
            Latest realized profit for the active strategy.

    Performance counters:
        totalProfit:
            Total realized profit accumulated during the run.

        positiveProfitTrend / negativeProfitTrend:
            Number of winning/losing Trend trades.

        positiveProfitMeanRev / negativeProfitMeanRev:
            Number of winning/losing Mean Reversion trades.

        numberTradesTrend / numberTradesMeanRev:
            Total completed trades per strategy.

        totalProfitPositiveTradesTrend / totalProfitNegativeTradesTrend:
            Sum of winning/losing Trend trade profits.

        totalProfitPositiveTradesMeanRev / totalProfitNegativeTradesMeanRev:
            Sum of winning/losing Mean Reversion trade profits.

    Signal state:
        pending_action:
            Signal from the previous day to execute today.
            Expected values: "BUY", "SELL", "HOLD", or "".

    Class-level state:
        backtest_run_number:
            Shared counter across all ExecutionState instances.
    """
 

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
    """
    Stateless engine that operates on ExecutionState objects.
    backtest_run() iterates through all trading days, executes signals, and returns a dictionary
    of structured DataFrames (equity curve, drawdown series, trades, log events).
    performance_metrics_data_frame() computes summary statistics for a completed run.
    All methods are static — no instance of TradingEngine is ever created.
    """

    @staticmethod
    def build_data_frames(log_events,equity_curve,drawdown_series,trades,prices):
        return{
            "log_events":log_events,
            "equity_curve":equity_curve,
            "drawdown_series":drawdown_series,
            "trades":trades,
            "prices":prices
        }

    @staticmethod
    def build_run_df(run_number, ticker, strategy,starting_cash,total_net_profit,mdd,expectancy,payoff_ratio,profit_factor,sharpe_ratio,labels):
        return{
            "run_number":run_number,
            "ticker":ticker,
            "strategy":strategy,
            "starting_cash":starting_cash,
            "total_net_profit": total_net_profit,
            "mdd": mdd,
            "expectancy": expectancy,
            "payoff_ratio": payoff_ratio,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio, 
            "labels": labels
        }

    @staticmethod 
    def build_drawdown_series(day,run_number,ticker,strategy,equity,peak_so_far_,drawdown,drawdown_pct):
        return{
            "day":day,
            "run_number": run_number,
            "ticker":ticker,
            "strategy":strategy,
            "equity": equity,
            "peak_so_far":peak_so_far_,
            "drawdown":drawdown,
            "drawdown_pct":drawdown_pct
        }

    @staticmethod
    def build_one_completed_trade_row(run_number,ticker,strategy,entry_day,entry_price,exit_day,exit_price,profit,return_pct,labels):
        return {
            "run_number":run_number,
            "ticker":ticker,
            "strategy": strategy,
            "entry_day":entry_day,
            "entry_price":entry_price,
            "exit_day":exit_day,
            "exit_price":exit_price,
            "profit":profit,
            "return_pct":return_pct,
            "labels":labels
        }

    @staticmethod
    def build_event_log_row(run_number, day, date, ticker, strategy, event_type, message, cash, equity, position, execution_price, pnl, labels):
        return {
            "run_number":  run_number,
            "day": day,
            "date": date,
            "ticker": ticker, 
            "strategy": strategy, 
            "event_type": event_type, 
            "message": message, 
            "cash": cash, 
            "equity": equity, 
            "position": position, 
            "execution_price": execution_price, 
            "pnl": pnl, 
            "labels": labels
        }

    @staticmethod
    def build_price_row(day, date, ticker, strategy, closing_price, average):
        return {
            "day": day, 
            "date": date, 
            "ticker": ticker, 
            "strategy": strategy,
            "closing price": closing_price,
            "average": average
        }

    @staticmethod
    def strategy(state:ExecutionState)->str:
        """choooses which strategy to use based on the ExecutionState object's trendMethod boolean
        Args:
            state (ExecutionState): object on which the backtest is being performed 
        Returns:
            str: wihch strategy method is to be used as a string 
        """
        return "Trend" if state.trendMethod else "Mean Reversion"
    
    @staticmethod
    def labels(state:ExecutionState)->str:
        """computes the corresponding name for the "labels" column in the "trades" df based on the ticker's name and the strategy used
        Args:
            state (ExecutionState): current object on which the backtest is being performed 
        Returns:
            str: the correct name formatting inside the "labels" column for the "trades" df 
        """
        return state.ticker_name+"-"+TradingEngine.strategy(state) 
    
    @staticmethod
    def position(state:ExecutionState)->int:
        """ returns the number of shares held (as an integer) depending on the strategy used 
        Args:
            state (ExecutionState): current object on which the backtest is being performed 
        Returns:
            int: 
        """
        return state.positionTrend if TradingEngine.strategy(state)=="Trend" else state.positionMeanReversion

    @staticmethod
    def backtest_run(state: ExecutionState)->dict: # state is an ExecutionState object 

        # first, reset all variables back to 0 in case you are reusing the same ExecutionState instance twice 
        state.reset()
        # list of dictionaries holding all the logged events 
        list_dictionaries_event_logs=[]
        list_dictionaries_prices=[]
        list_dictionaries_completed_trades=[]
        # compute the dictionary for the BACKTEST_START logging event 
        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1, float("nan"), 
                                                        None, state.ticker_name, 
                                                        TradingEngine.strategy(state), 
                                                        "BACKTEST_START",
                                                        "Backtest started",
                                                        state.startingCashValue, 
                                                        state.equity, 
                                                        TradingEngine.position(state),
                                                        None, 
                                                        None,
                                                        None)
        list_dictionaries_event_logs.append(event_log_row)
        # extract data from the csv file 
        generatorAverageDayDateClosingPrice=dl.read_ticker_csv(state.csv_ticker, state.cashValue, state.verbose_run)
        # 1 "for" loop iteration=1 day executed,  entire "for" loop iteration=1 full backtest run 
        for extracted_tuple in generatorAverageDayDateClosingPrice:

            day=extracted_tuple[0]
            date=extracted_tuple[1]
            closingPrice=extracted_tuple[2]
            average=extracted_tuple[3]
            nextDayOpeningPrice=extracted_tuple[4]

            #Days starting from day 3 onwards 
            if(average!=None):

                #TREND method
                if state.trendMethod:
                    
                    # compute the dictionary row for the price data frame 
                    price_row=TradingEngine.build_price_row(day, date, state.ticker_name, TradingEngine.strategy(state), closingPrice, average)
                    # append to the list of dictionaries/rows for the price data frame 
                    list_dictionaries_prices.append(price_row)
                    #we only compute when there's a change in the profit 
                    previousProfitTrend=state.profitTrend
                    # before "process_1_day()" we hold no shares
                    previous_position=state.positionTrend 
                    # Process one trading day, update portfolio state, and print the day’s execution/output details
                    state.positionTrend, state.profitTrend, state.entryPriceTrend, state.exitPriceTrend, state.cashValue, state.equity, state.pending_action, state.entry_day, state.exit_day=process_1_day.process_one_day(state.verbose_run, day, date, closingPrice, average, nextDayOpeningPrice, state.cashValue, state.equity, state.pending_action, state.positionSizing, state.flat_fee_per_share, state.fixed_bps, state.trendMethod, state.positionTrend, state.entry_day, state.exit_day, state.entryPriceTrend, state.exitPriceTrend, state.profitTrend, state.positionMeanReversion, state.entryPriceMeanReversion, state.exitPriceMeanReversion, state.profitMeanReversion)
                    # a trade took place
                    if( (state.profitTrend-previousProfitTrend) !=0 ):
                        one_completed_trade_row=TradingEngine.build_one_completed_trade_row(ExecutionState.backtest_run_number+1,
                                                                                            state.ticker_name,
                                                                                            TradingEngine.strategy(state),
                                                                                            state.entry_day,
                                                                                            round(state.entryPriceTrend,3),
                                                                                            state.exit_day,
                                                                                            round(state.exitPriceTrend,3),
                                                                                            round(state.profitTrend,3),
                                                                                            round(((state.exitPriceTrend-state.entryPriceTrend)/state.entryPriceTrend)*100,2),
                                                                                            TradingEngine.labels(state))
                        # add it to the list of all dictionaries 
                        list_dictionaries_completed_trades.append(one_completed_trade_row)
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
                        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                                        day, date, state.ticker_name, 
                                                                        TradingEngine.strategy(state), "BUY_EXECUTED",
                                                                        "A Buy has been executed",
                                                                        state.cashValue,
                                                                        state.equity, 
                                                                        state.positionTrend,
                                                                        state.entryPriceTrend,
                                                                        None, 
                                                                        TradingEngine.labels(state) )
                        list_dictionaries_event_logs.append(event_log_row)

                    # if after "process_1_day()" we don't hold any shares anymore, but before it we did =>
                    # we sold => we compute SELL_EXECUTED logging event 
                    if ( previous_position>0 and current_position==0 ):
                        # we compute the dictionary row for the BUY_EXECUTED logging event 
                        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                                        day, date, state.ticker_name,
                                                                        TradingEngine.strategy(state),
                                                                        "SELL_EXECUTED",
                                                                        "A Sell has been executed",
                                                                        state.cashValue,
                                                                        state.equity,
                                                                        state.positionTrend,
                                                                        state.exitPriceTrend,
                                                                        state.profitTrend,
                                                                        TradingEngine.labels(state) )
                        list_dictionaries_event_logs.append(event_log_row)

                        # if a sell has been executed, then a fully completed trade took place => TRADE_CLOSED log event happens immediately after SELL_EXECUTED log event
                        # create the dictionary row for the TRADE_CLOSED logging event 
                        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                                        day,date,state.ticker_name,
                                                                        TradingEngine.strategy(state) , "TRADE_CLOSED",
                                                                        "A Trade has been executed",
                                                                        state.cashValue,
                                                                        state.equity,
                                                                        state.positionTrend,
                                                                        state.exitPriceTrend,
                                                                        state.profitTrend,
                                                                        TradingEngine.labels(state) )
                        list_dictionaries_event_logs.append(event_log_row)

                    #add trading day's equity to the equity curve 
                    state.listStoreEquityValues.append(state.equity) 

                #MEAN REVERSION method 
                else:
                    
                    price_row=TradingEngine.build_price_row(day, date, state.ticker_name, TradingEngine.strategy(state), closingPrice, average)
                    # append to the list of dictionaries/rows for the price data frame 
                    list_dictionaries_prices.append(price_row)
                    #we only compute when there's a change in the profit 
                    previousProfitMeanReversion=state.profitMeanReversion
                    # before "process_1_day()" we hold no shares
                    previous_position=state.positionMeanReversion 
                    # Process one trading day, update portfolio state, and print the day’s execution/output details
                    state.positionMeanReversion, state.profitMeanReversion, state.entryPriceMeanReversion, state.exitPriceMeanReversion, state.cashValue, state.equity, state.pending_action,state.entry_day,state.exit_day=process_1_day.process_one_day(state.verbose_run, day, date, closingPrice, average, nextDayOpeningPrice, state.cashValue, state.equity, state.pending_action, state.positionSizing, state.flat_fee_per_share, state.fixed_bps, state.trendMethod, state.positionTrend, state.entry_day, state.exit_day, state.entryPriceTrend, state.exitPriceTrend, state.profitTrend, state.positionMeanReversion, state.entryPriceMeanReversion, state.exitPriceMeanReversion, state.profitMeanReversion)
                    # a trade took place 
                    if( (state.profitMeanReversion-previousProfitMeanReversion) !=0 ):
                        one_completed_trade_row=TradingEngine.build_one_completed_trade_row(ExecutionState.backtest_run_number+1,
                                                                                            state.ticker_name,
                                                                                            TradingEngine.strategy(state),
                                                                                            state.entry_day,
                                                                                            round(state.entryPriceMeanReversion,3),
                                                                                            state.exit_day,
                                                                                            round(state.exitPriceMeanReversion,3),
                                                                                            round(state.profitMeanReversion,3),
                                                                                            round(((state.exitPriceMeanReversion-state.entryPriceMeanReversion)/state.entryPriceMeanReversion)*100,2),
                                                                                            TradingEngine.labels(state))
                        # add it to the list of all dictionaries 
                        list_dictionaries_completed_trades.append(one_completed_trade_row)
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
                        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                                        day,date,state.ticker_name,
                                                                        TradingEngine.strategy(state) ,
                                                                        "BUY_EXECUTED",
                                                                        "A Buy has been executed",
                                                                        state.cashValue,
                                                                        state.equity,
                                                                        state.positionMeanReversion,
                                                                        state.entryPriceMeanReversion,
                                                                        None,
                                                                        TradingEngine.labels(state) )
                        list_dictionaries_event_logs.append(event_log_row)

                    # if after "process_1_day()" we don't hold any shares anymore, but before it we did =>
                    # we sold => we compute SELL_EXECUTED logging event 
                    if ( previous_position>0 and current_position==0 ):
                        # we compute the dictionary row for the SELL_EXECUTED logging event 
                        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                                        day,date,state.ticker_name,
                                                                        TradingEngine.strategy(state),
                                                                        "SELL_EXECUTED",
                                                                        "A Sell has been executed",
                                                                        state.cashValue,
                                                                        state.equity, 
                                                                        state.positionMeanReversion,
                                                                        state.exitPriceMeanReversion,
                                                                        state.profitMeanReversion,
                                                                        TradingEngine.labels(state) )
                        list_dictionaries_event_logs.append(event_log_row)

                        # if a sell has been executed, then a fully completed trade took place => TRADE_CLOSED log event happens immediately after SELL_EXECUTED log event
                        # create the dictionary row for the TRADE_CLOSED logging event
                
                        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                                        day,date,state.ticker_name,
                                                                        TradingEngine.strategy(state) ,
                                                                        "TRADE_CLOSED",
                                                                        "A Trade has been executed",
                                                                        state.cashValue,
                                                                        state.equity,
                                                                        state.positionMeanReversion,
                                                                        state.exitPriceMeanReversion,
                                                                        state.profitMeanReversion,
                                                                        TradingEngine.labels(state) )
                        list_dictionaries_event_logs.append(event_log_row)

                    #add trading day's equity to the equity curve 
                    state.listStoreEquityValues.append(state.equity) 

            # Days 1 and 2 
            else:
                state.listStoreEquityValues.append(state.equity)
                price_row=TradingEngine.build_price_row(day, date, state.ticker_name, TradingEngine.strategy(state), closingPrice, None)
                # append to the list of dictionaries/rows for the price data frame 
                list_dictionaries_prices.append(price_row)
                
        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                        day,date,state.ticker_name,
                                                        TradingEngine.strategy(state),
                                                        "BACKTEST_END",
                                                        "Backtest has ended",
                                                        state.cashValue,
                                                        state.equity,
                                                        TradingEngine.position(state),
                                                        None,
                                                        state.totalProfit,
                                                        None)
        list_dictionaries_event_logs.append(event_log_row)

        # data frame for all the prices of the backtest used for the price markers plotting chart
        price_data_frame=pd.DataFrame(data=list_dictionaries_prices)
        # data frame containing all of the 5 logging events (backtest_start,buy_executed,sell_executed,trade_closed,backtest_end) in the list converted into a pandas data frame
        loggingEventsDataFrame=pd.DataFrame(data=list_dictionaries_event_logs)
        # converts the day column to pandas nullable integer type — pd.Int64Dtype() — which supports NaN without forcing float promotion => "day" won't be printed with a .0 decimal anymore 
        loggingEventsDataFrame["day"] = loggingEventsDataFrame["day"].astype(pd.Int64Dtype())
        # final data frame containing all the completed trades in the list converted into a pandas data frame
        tradesDataFrame=pd.DataFrame(data=list_dictionaries_completed_trades)
        # adding an extra column that counts the number of completed trades that took place starting from 1 per individual backtest run
        tradesDataFrame["number_trades_took_place"]=tradesDataFrame.groupby(by="run_number").cumcount()+1
        # count the number of backtest runs at Class level (not per engine instance)
        ExecutionState.backtest_run_number+=1
        # 1 dimensional array representing all the raw daily equities 
        daily_equities=pd.Series(state.listStoreEquityValues)
        # equity peak so far for drawdown series computation 
        running_max=daily_equities.cummax()
        # compute drawdown values 
        drawdown=round(daily_equities-running_max,3)
        # compute drawdown values expressed as percentages 
        drawdown_pct=round( (drawdown/running_max)*100 , 2)
        # list of dictionaries holding all the drawdown series 
        list_dictionaries_rows_per_equity_drawdown_series=[]
        # create list of dictionaries for drawdown series (1 dictionary= 1 day)
        for i in range(len(state.listStoreEquityValues)): 
            row_drawdown_series=TradingEngine.build_drawdown_series(i+1,
                                                                    ExecutionState.backtest_run_number,
                                                                    state.ticker_name,
                                                                    TradingEngine.strategy(state),
                                                                    state.listStoreEquityValues[i],
                                                                    running_max.iloc[i],
                                                                    drawdown.iloc[i],
                                                                    drawdown_pct.iloc[i])
            list_dictionaries_rows_per_equity_drawdown_series.append(row_drawdown_series)
        # drawdown series final computed data frame from all dictionary rows 
        drawdown_series=pd.DataFrame(data=list_dictionaries_rows_per_equity_drawdown_series)
        # add another extra column in the drawdown series data frame called 'labels' that uniquely identifies each line
        drawdown_series["labels"]=drawdown_series["ticker"]+"-"+drawdown_series["strategy"]
        # equity curve final computed data frame from all dictionary rows 
        equityCurveDataFrame=drawdown_series[ ["day", "run_number", "ticker", "strategy", "equity","labels"] ]
        # single dictionary containing all structured data outputs's (run data frame, equity curve, trades, drawdown series, log events) final computed data frames 
        dictionary_data_frames=TradingEngine.build_data_frames(loggingEventsDataFrame,
                                                               equityCurveDataFrame,
                                                               drawdown_series,
                                                               tradesDataFrame,
                                                               price_data_frame)

        return dictionary_data_frames
    
    @staticmethod
    def try_except_performance_metric(fn):
        """Calls a performance metric function and returns nan if it raises ZeroDivisionError.
        Used to guard metrics that require at least one winning and one losing trade to be defined.

        Args:
            fn: a zero-argument callable (lambda) wrapping the metric function call

        Returns:
            float: the metric result, or float("nan") if ZeroDivisionError is raised
        """
        try:
            return fn()
        except ZeroDivisionError:
            return float("nan")

    @staticmethod
    def strategy_performance_metrics_stats(state: ExecutionState)->dict:
        """Selects the correct set of trade statistics from state based on the active strategy.

        Args:
            state (ExecutionState): current backtest state

        Returns:
            dict: trade statistics keyed by positive_count, negative_count, trade_count, positive_total, negative_total
        """
        if state.trendMethod:
            return {
                    "positive_count": state.positiveProfitTrend,
                    "negative_count": state.negativeProfitTrend,
                    "trade_count": state.numberTradesTrend,
                    "positive_total": state.totalProfitPositiveTradesTrend,
                    "negative_total": state.totalProfitNegativeTradesTrend }
        else:
             return {
                    "positive_count": state.positiveProfitMeanRev,
                    "negative_count": state.negativeProfitMeanRev,
                    "trade_count": state.numberTradesMeanRev,
                    "positive_total": state.totalProfitPositiveTradesMeanRev,
                    "negative_total": state.totalProfitNegativeTradesMeanRev }   


    @staticmethod
    def performance_metrics_data_frame(state: ExecutionState)->pd.DataFrame:
        """Computes all performance metrics for a completed backtest run and returns them as a one-row DataFrame.
        Must be called after backtest_run() — depends on state.listStoreEquityValues being populated.

        Args:
            state (ExecutionState): completed backtest state

        Returns:
            pd.DataFrame: one-row DataFrame containing run_number, ticker, strategy, starting cash, 
                        total net profit, mdd, expectancy, payoff ratio, profit factor, sharpe ratio, labels
        """
        stats_dictionary=TradingEngine.strategy_performance_metrics_stats(state)
        mddMetric=performanceMetrics.mdd(state.listStoreEquityValues)
        expectancy=TradingEngine.try_except_performance_metric(lambda: performanceMetrics.expectancy(stats_dictionary["positive_count"],
                                                                                                     stats_dictionary["trade_count"],
                                                                                                     stats_dictionary["positive_total"],
                                                                                                     stats_dictionary["negative_count"],
                                                                                                     stats_dictionary["negative_total"]))
        payoffRatio=TradingEngine.try_except_performance_metric(lambda: performanceMetrics.payoff_ratio(stats_dictionary["positive_total"],
                                                                                                        stats_dictionary["negative_total"],
                                                                                                        stats_dictionary["positive_count"],
                                                                                                        stats_dictionary["negative_count"]))
        profitFactor=TradingEngine.try_except_performance_metric(lambda: performanceMetrics.profit_factor(stats_dictionary["positive_total"],
                                                                                                          stats_dictionary["negative_total"]))
        sharpeRatio=TradingEngine.try_except_performance_metric(lambda: performanceMetrics.sharpe_ratio(state.listStoreEquityValues))

        run_data_frame=TradingEngine.build_run_df(ExecutionState.backtest_run_number,
                                                  state.ticker_name,
                                                  TradingEngine.strategy(state),
                                                  state.startingCashValue,
                                                  round(state.totalProfit,3),
                                                  mddMetric,
                                                  expectancy,
                                                  payoffRatio,
                                                  profitFactor,
                                                  sharpeRatio,
                                                  TradingEngine.labels(state))

        return pd.DataFrame( data=run_data_frame , index=[0])


        

class PlottingLayer:
    """

    Visualization layer that generates interactive Plotly charts from structured backtest results.
    Accepts the results dictionary from ExperimentRunner.structured_data_outputs() and exposes one
    method per chart type. user_interface_oriented_plotting_price_chart() is parameterized by ticker
    and strategy — all other methods plot all 6 runs at once.

    """

    def __init__(self,results_data_frames):
        self.results_data_frames=results_data_frames
    
    def user_interface_oriented_plotting_equity_curve(self):

        equity_curve_line_chart=px.line( data_frame=self.results_data_frames["Equity Curve"],
                 x="day",
                 y="equity",
                 color="labels",
                 title="Equity Curve Chart", 
                 labels={"day": "Trading Day", "equity": "Equity ($)", "labels": "run_label"} )
        equity_curve_line_chart.show()

    def user_interface_oriented_plotting_drawdown_series(self):

        drawdown_series_chart=px.line(data_frame=self.results_data_frames["Drawdown Series"],
                x="day",
                y="drawdown_pct",
                color="labels",
                title="Drawdown Series Chart",
                labels={"day":"Trading Day", "drawdown_pct":"Drawdown (%)", "labels":"run_label"})
        drawdown_series_chart.show()

    def user_interface_oriented_plotting_completed_trades(self):

        drawdown_series_chart=px.bar(data_frame=self.results_data_frames["Completed Trades"],
                x="number_trades_took_place",
                y="profit",
                color="labels",
                title="Completed Trades Chart",
                labels={"number_trades_took_place": "Trade number", "profit":"Profit ($)", "labels":"run_label"},
                barmode="group")
        drawdown_series_chart.show()

    def user_interface_oriented_plotting_log_events(self):

        log_events_chart=px.scatter(data_frame=self.results_data_frames["Log Events"],
                x="day",
                y="event_type",
                color="labels",
                hover_data=["cash", "equity", "position", "execution_price", "pnl"],
                title="Log Events Chart")
        log_events_chart.show()

    def user_interface_oriented_plotting_run_data_frame(self):

        run_data_frame_chart=px.bar(data_frame=self.results_data_frames["Final Data Frame Run"],
                x="run_number",
                y="total net profit",
                color= "labels",
                title="Run Chart",
                barmode="group",
                labels={"run_number": "Backtest run number"} )
        run_data_frame_chart.show()
                    
    def user_interface_oriented_plotting_price_chart(self, ticker, strategy):

        # Price BUY/SELL Marker Chart 

        # markers (buy/sell markers) -> log events data frame 
        ticker_strategy_data_frame_log_events=self.results_data_frames["Log Events"] [self.results_data_frames["Log Events"]["labels"]==f"{ticker}-{strategy}"]
        ticker_strategy_data_frame_buy_executed=ticker_strategy_data_frame_log_events[ticker_strategy_data_frame_log_events["event_type"]=="BUY_EXECUTED"]
        ticker_strategy_data_frame_buy_executed_price=ticker_strategy_data_frame_buy_executed["execution_price"]
        ticker_strategy_data_frame_sell_executed=ticker_strategy_data_frame_log_events [ticker_strategy_data_frame_log_events["event_type"]=="SELL_EXECUTED"]
        ticker_strategy_data_frame_sell_executed_price=ticker_strategy_data_frame_sell_executed["execution_price"]
        strategy_chart=go.Figure()

        # closing price + average (lines) -> prices data frame 
        ticker_strategy_data_frame=self.results_data_frames["Prices"] [ (self.results_data_frames["Prices"] ["ticker"]==f"{ticker}") & (self.results_data_frames["Prices"] ["strategy"]==f"{strategy}") ]
        ticker_strategy_closing_prices=ticker_strategy_data_frame["closing price"]
        ticker_strategy_averages=ticker_strategy_data_frame["average"]
        
        # add the closing prices line and averages line to the y-axis of the price chart 
        strategy_chart.add_trace(go.Scatter(x=ticker_strategy_data_frame["day"], y=ticker_strategy_closing_prices, mode="lines", name="Closing Prices"))
        strategy_chart.add_trace(go.Scatter(x=ticker_strategy_data_frame["day"], y=ticker_strategy_averages, mode="lines", name="Averages"))

        # add the buy/sell markers to the price chart
        strategy_chart.add_trace(go.Scatter(x=ticker_strategy_data_frame_buy_executed["day"], y=ticker_strategy_data_frame_buy_executed_price, mode="markers", name="BUY_EXECUTED", marker_size=15))
        strategy_chart.add_trace(go.Scatter(x=ticker_strategy_data_frame_sell_executed["day"], y=ticker_strategy_data_frame_sell_executed_price, mode="markers", name="SELL_EXECUTED",marker_size=15))
        strategy_chart.update_layout(xaxis_title="Trading Day", yaxis_title="Price", title=f"Price chart BUY/SELL markers: {ticker}-{strategy}")
        strategy_chart.show()        



    
    

class AggregationLayer:

    def __init__(self,results_data_frames: dict):
        if not isinstance(results_data_frames,dict):
            raise TypeError("The resulting data frames need to be stored inside a dictionary")
        self.results_data_frames=results_data_frames

    @staticmethod
    def build_average_performance_summary(average_total_net_profit,average_mdd,average_expectancy,average_payoff_ratio,average_profit_factor,average_sharpe_ratio):
        return{
            "average total net profit":average_total_net_profit,
            "average mdd":average_mdd,
            "average expectancy":average_expectancy,
            "average payoff ratio":average_payoff_ratio,
            "average profit factor":average_profit_factor,
            "average sharpe ratio": average_sharpe_ratio
        }
    
    @staticmethod
    def build_aggregation_outputs(total_runs,best_run_summary,worst_run_summary,average_performance_summary,selected_run_summary,selected_run_trade_list):
        return{
            "total_runs":total_runs,
            "best_run_summary":best_run_summary,
            "worst_run_summary":worst_run_summary,
            "average_performance_summary":average_performance_summary,
            "selected_run_summary":selected_run_summary,
            "selected_run_trade_list":selected_run_trade_list
        }

    # total backtest runs by the Trading Engine
    def total_runs_summary(self)->int:

        return len(self.results_data_frames["Final Data Frame Run"])
    
    def run_summary(self,max):

        if max:
            total_net_profit=self.results_data_frames["Final Data Frame Run"]["total net profit"].max()
        else:
            total_net_profit=self.results_data_frames["Final Data Frame Run"]["total net profit"].min()
        run_summary=self.results_data_frames["Final Data Frame Run"] [self.results_data_frames["Final Data Frame Run"]["total net profit"]==total_net_profit] # select the row/rows from the data frame matching the value for 'total net profit'
        run_summary=run_summary.iloc[0] # select only the first row matching that value
        run_summary=run_summary.to_dict() # convert the Series into a dictionary
        return run_summary
    
    # best run summary from the run data frame based on the total net profit 
    def best_run_summary(self)->dict:

        return self.run_summary(max=True)
    
    # worst run summary from the run data frame based on the total net profit 
    def worst_run_summary(self)->dict:

        return self.run_summary(max=False)
    
    # average performance summary of each metric from all the backtest runs 
    def average_performance_summary(self)->dict:

        average_total_net_profit=round(self.results_data_frames["Final Data Frame Run"]["total net profit"].mean(),2) 
        average_mdd=round(self.results_data_frames["Final Data Frame Run"]["mdd"].mean(),2)
        average_expectancy=round(self.results_data_frames["Final Data Frame Run"]["expectancy"].mean(),2)
        average_payoff_ratio=round(self.results_data_frames["Final Data Frame Run"]["payoff ratio"].mean(),2)
        average_profit_factor=round(self.results_data_frames["Final Data Frame Run"]["profit factor"].mean(),2)
        average_sharpe_ratio=round(self.results_data_frames["Final Data Frame Run"]["sharpe ratio"].mean(),2)
        average_performance_summary=AggregationLayer.build_average_performance_summary(float(average_total_net_profit),
                                                                                       float(average_mdd),
                                                                                       float(average_expectancy),
                                                                                       float(average_payoff_ratio),
                                                                                       float(average_profit_factor),
                                                                                       float(average_sharpe_ratio))
        return average_performance_summary
    
    # user input selected run summary (ticker-strategy) from the run data frame 
    def selected_run_summary(self,ticker,strategy)->dict:

        AggregationLayer.ticker_strategy_validation(ticker,strategy)
        selected_run_summary=(self.results_data_frames["Final Data Frame Run"] [self.results_data_frames["Final Data Frame Run"]["labels"]==f"{ticker}-{strategy}"])
        selected_run_summary=selected_run_summary.iloc[0] # if multiple identical ticker/strategy pairs, pick the first pair only
        if selected_run_summary.empty:
            raise ValueError("The selected run summary data frame is empty")
        selected_run_summary=selected_run_summary.to_dict()
        return selected_run_summary

    # user input selection for a complete trade run based on ticker and strategy from the Completed Trades data frame 
    def selected_run_trade_list(self,ticker,strategy)->pd.DataFrame:

        AggregationLayer.ticker_strategy_validation(ticker,strategy)
        selected_run_trade=(self.results_data_frames["Completed Trades"] [self.results_data_frames["Completed Trades"]["labels"]==f"{ticker}-{strategy}"])
        if selected_run_trade.empty:
            raise ValueError("The selected run trade list is empty")
        return selected_run_trade
    
    @staticmethod
    def ticker_strategy_validation(ticker,strategy):
        if ticker not in ["Apple", "Google", "Microsoft"]:
            raise ValueError("This selected ticker does not exist")
        if strategy not in ["Trend", "Mean Reversion"]:
            raise ValueError("This selected strategy does not exist")
        
    def aggregation_outputs(self,ticker:str,strategy:str)->dict:

        """collect the already-working pieces into one dictionary.
           calls/reuses: total runs, best run summary, worst run summary, average performance summary, 
           selected run summary and selected run trade list   


        Args:
            ticker (str): Apple, Google, Microsoft
            strategy (str): strategy method

        Returns:
            dict: final dictionary ready for Step 15 "UI-ready package"
        """
        aggregation_outputs=AggregationLayer.build_aggregation_outputs(self.total_runs_summary(),
                                                                       self.best_run_summary(),
                                                                       self.worst_run_summary(),
                                                                       self.average_performance_summary(),
                                                                       self.selected_run_summary(ticker,strategy),
                                                                       self.selected_run_trade_list(ticker,strategy))
        return aggregation_outputs





class ExperimentRunner:
    """
    Orchestrates multiple backtest runs across different tickers and strategies.
    structured_data_outputs() instantiates one ExecutionState per configuration, runs TradingEngine
    on each, and concatenates all results into five final DataFrames returned in a single dictionary:
    Final Data Frame Run, Equity Curve, Drawdown Series, Completed Trades, Log Events.
    """

    @staticmethod
    def build_results(run_data_frame,equity_curves_df,drawdown_series_df,trades_df,log_events_df,prices_df):

        return{
            "Final Data Frame Run":run_data_frame,
            "Equity Curve":equity_curves_df,
            "Drawdown Series":drawdown_series_df,
            "Completed Trades":trades_df,
            "Log Events":log_events_df,
            "Prices":prices_df
        }

    # method running 5 different outputs: run data frame, trades data frame, equity curves, drawdown series, logs
    def structured_data_outputs(self):
        
        # multiple ExecutionState objects representing multiple experiments with different configurated parameters 
        states=[    ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple"), 
                    ExecutionState(trendMethod=False, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple"),
                    ExecutionState(trendMethod=True, csv_ticker="data/google.csv", cashValue=10000, ticker_name="Google"),
                    ExecutionState(trendMethod=False, csv_ticker="data/google.csv", cashValue=10000, ticker_name="Google"),
                    ExecutionState(trendMethod=True, csv_ticker="data/microsoft.csv", cashValue=10000, ticker_name="Microsoft"),
                    ExecutionState(trendMethod=False, csv_ticker="data/microsoft.csv", cashValue=10000, ticker_name="Microsoft") ]

        # list of all the prices data frames , 1 prices data frame corresponding to 1 ExecutionState object 
        prices=[]
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
            prices.append(dictionary_data_frames["prices"])
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
        # prices data frame made out of all the different Execution State objects's log events data frames concatenated together
        prices_df=pd.concat(prices)

        # add all the final structured outputs to a single final returned dictionary, and make each structured output key-accessible
        results=ExperimentRunner.build_results(final_data_frame_run,
                                               equity_curves_df,
                                               drawdown_series_df,
                                               trades_df,
                                               log_events_df,
                                               prices_df)       
        return results


if __name__=="__main__":
    experimentRunner=ExperimentRunner()
    results=experimentRunner.structured_data_outputs()
    plottedChart=PlottingLayer(results)
    aggregationLayerSummary=AggregationLayer(results)

    print(results["Log Events"])

    #plottedChart.user_interface_oriented_plotting_equity_curve()
    #plottedChart.user_interface_oriented_plotting_drawdown_series()
    #plottedChart.user_interface_oriented_plotting_completed_trades()
    #plottedChart.user_interface_oriented_plotting_log_events()
    #plottedChart.user_interface_oriented_plotting_run_data_frame()
    #plottedChart.user_interface_oriented_plotting_price_chart("Apple", "Trend")
    
    #print(results["Final Data Frame Run"])
    #print(results["Completed Trades"])
    #print(results["Drawdown Series"])
    #print(results["Equity Curve"])
    #print(results["Log Events"])
    #print(results["Prices"]) 
