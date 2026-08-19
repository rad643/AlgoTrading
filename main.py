from typing import Any, Generator
from datetime import date
import data_loading.data_loader as dl
import engine.process_1_day as process_1_day
import dataclasses
import metrics.performanceMetrics as performanceMetrics
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



COMPANY_NAMES = {"AAPL": "Apple", "GOOGL": "Google", "MSFT": "Microsoft"}

selected_tickers = "AAPL,GOOGL,MSFT"

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

        symbol:
            Corresponding ticker symbol 

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
            Final net profit/loss for the completed backtest run.
            During the run it accumulates realised P&L from closed trades.
            At the end of the backtest it is overwritten as:
                final equity - starting cash.

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
    symbol: str
    cashValue: float
    ticker_name: str
    verbose_run: bool=False
    fixed_bps: float=0.0005
    flat_fee_per_share: float=0.005
    positionSizing: float=0
    list_dictionaries_event_logs: list = dataclasses.field(default_factory = list)
    list_dictionaries_prices : list = dataclasses.field(default_factory= list)
    list_dictionaries_completed_trades : list = dataclasses.field(default_factory= list)
    listStoreEquityValues: list=dataclasses.field(default_factory=list)
    equity: float =0
    positionTrend: int=0
    entry_day: int=0
    exit_day: int=0
    entryPriceTrend: float =0
    exitPriceTrend: float =0
    profitTrend: float =0
    positionMeanReversion: int =0
    entryPriceMeanReversion: float =0
    exitPriceMeanReversion: float =0
    profitMeanReversion: float =0
    totalProfit: float = 0
    positiveProfitTrend: float=0
    negativeProfitTrend: float=0
    positiveProfitMeanRev: float=0
    negativeProfitMeanRev: float =0
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
        self.list_dictionaries_event_logs = []
        self.list_dictionaries_completed_trades = []
        self.list_dictionaries_prices = []
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
    def build_data_frames(log_events:pd.DataFrame,
                          equity_curve:pd.DataFrame,
                          drawdown_series:pd.DataFrame,
                          trades:pd.DataFrame,
                          prices:pd.DataFrame)->dict[str,pd.DataFrame]:
        """ Wiring function that puts together the final dictionary of data frames computed from the backtest_run() method """
        return{
            "log_events":log_events,
            "equity_curve":equity_curve,
            "drawdown_series":drawdown_series,
            "trades":trades,
            "prices":prices
        }

    @staticmethod
    def build_run_df(run_number:int,
                     ticker:str,
                     strategy:str,
                     starting_cash:float,
                     total_net_profit:float,
                     mdd:float,
                     expectancy:float,
                     payoff_ratio:float,
                     profit_factor:float,
                     sharpe_ratio:float,
                     labels:str)-> dict[str, Any]:
        """ Wiring function that puts together the final summary 'run' data frame
        into a dictionary with values computed from the performance_metrics_data_frame() method"""

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
    def build_drawdown_series(day:int,
                              run_number:int,
                              ticker:str,
                              strategy:str,
                              equity:float,
                              peak_so_far_:float,
                              drawdown: float,
                              drawdown_pct: float)-> dict[str, Any]:
        """ Wiring function that computes a dictionary for each drawdown serie (1 dictionary of drawdowns = 1 single day) 
        with each 1 dictionary of drawdowns corresponding to 1 single row in the later final 'drawdown series' data frame """
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
    def build_one_completed_trade_row(run_number:int,
                                      ticker:str,
                                      strategy:str,
                                      entry_day:int,
                                      entry_price:float,
                                      exit_day:int,
                                      exit_price:float,
                                      profit:float,
                                      return_pct:float,
                                      labels:str)->dict[str,Any]:
        """ Wiring function that, if a completed trade takes place, then it computes and returns a dictionary 
        corresponding to that 1 single completed trade (1 single dictionary = 1 single completed trade), 
        and it represents 1 single row in the latter final 'trades' data frame """
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
    def build_event_log_row(run_number:int, 
                            day:int, 
                            date:date,
                            ticker:str, 
                            strategy:str, 
                            event_type:str, 
                            message:str,
                            cash:float, 
                            equity:float, 
                            position:int,
                            execution_price:float, 
                            pnl:float, 
                            labels: str)->dict[str, Any]:
        """ Wiring function that builds and returns a dictionary in order to 
        log every event that took place (1 single dictionary = 1 single event logged in),
        and it represents 1 single row in the later final 'log_events' data frame """
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
    def build_price_row(day:int, 
                        date: date,
                        ticker: str, 
                        strategy: str, 
                        closing_price:float, 
                        average:float)->dict[str,Any]:
        """ Wiring function that builds and returns a dictionary
        corresponding to each row in the later computed prices data frame
        (1 dictionary of prices = 1 row in the 'prices' data frame)"""
        return {
            "day": day, 
            "date": date, 
            "ticker": ticker, 
            "strategy": strategy,
            "closing_price": closing_price,
            "average": average
        }

    @staticmethod
    def strategy(state:ExecutionState)->str:
        """choooses which strategy to use based on the ExecutionState object's trendMethod boolean
        Args:
            state (ExecutionState): object on which the backtest is being performed 
        Returns:
            str: which strategy method is to be used as a string 
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
            int: number of shares held depending on strategy 
        """
        return state.positionTrend if TradingEngine.strategy(state)=="Trend" else state.positionMeanReversion

    @staticmethod
    def entry_price(state: ExecutionState) -> float:
        """based on the strategy that you're using, it returns either the entry price for trend or the entry price for mean reversion

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy

        Returns:
            float: the corresponding entry price based on the strategy you're using
        """

        return state.entryPriceTrend if TradingEngine.strategy(state) == "Trend" else state.entryPriceMeanReversion

    @staticmethod
    def exit_price(state: ExecutionState) -> float:
        """based on the strategy that you're using, it returns either the exit price for trend or the exit price for mean reversion
        
        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy

        Returns:
            float: the corresponding exit price based on the strategy you're using
        """

        return state.exitPriceTrend if TradingEngine.strategy(state) == "Trend" else state.exitPriceMeanReversion

    @staticmethod
    def profit(state: ExecutionState) -> float:
        """based on the strategy that you're using, it returns either the profit you made by using trend or the profit you made by using mean reversion
                
        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy

        Returns:
            float: the corresponding profit based on the strategy you're using
        """
        return state.profitTrend if TradingEngine.strategy(state) == "Trend" else state.profitMeanReversion

    @staticmethod
    def increment_trade_count( state : ExecutionState ) -> None : 
        """
        Adds 1 to the trade counter for whichever strategy the state is running.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        if TradingEngine.strategy(state) == "Trend" : 

            state.numberTradesTrend += 1

        else:

            state.numberTradesMeanRev += 1 

    @staticmethod
    def increment_positive_profit( state : ExecutionState ):
        """
        Adds 1 to the winning trades counter for whichever strategy the state is running.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        if TradingEngine.strategy(state) == "Trend" : 

            state.positiveProfitTrend += 1

        else:

            state.positiveProfitMeanRev +=1

    @staticmethod
    def increment_total_profit_positive_trades( state : ExecutionState ): 
        """
        Adds the current trade's profit to the running total of profit from winning
        trades, for whichever strategy the state is running.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        if TradingEngine.strategy(state) == "Trend" :

            state.totalProfitPositiveTradesTrend += TradingEngine.profit(state)

        else:

            state.totalProfitPositiveTradesMeanRev += TradingEngine.profit(state)

    @staticmethod
    def increment_negative_profit( state : ExecutionState ):
        """
        Adds 1 to the losing trades counter for whichever strategy the state is running.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        if TradingEngine.strategy(state) == "Trend" :

            state.negativeProfitTrend += 1

        else:

            state.negativeProfitMeanRev += 1         

    @staticmethod
    def increment_total_profit_negative_trades( state : ExecutionState ):
        """
        Adds the current trade's profit to the running total of profit from losing
        trades, for whichever strategy the state is running.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        if TradingEngine.strategy(state) == "Trend" :
           
            state.totalProfitNegativeTradesTrend += TradingEngine.profit(state)

        else:

            state.totalProfitNegativeTradesMeanRev += TradingEngine.profit(state)  

    @staticmethod
    def update_portfolio_state( state : ExecutionState ,
                                day : int ,
                                my_date : date ,
                                closingPrice : float ,
                                average : float ,
                                nextDayOpeningPrice : float ) -> None :
        """
        Runs one trading day through process_one_day() and writes the results back
        onto the state, into whichever set of fields belongs to the strategy the
        state is running.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
            day (int): which day of the backtest this is
            my_date (date): the calendar date for that day
            closingPrice (float): that day's closing price
            average (float): the average of all closing prices up to the current day, current day excluded
            nextDayOpeningPrice (float): the opening price used to execute the trade
        """

        if TradingEngine.strategy(state) == "Trend" :

            (state.positionTrend, 
            state.profitTrend, 
            state.entryPriceTrend, 
            state.exitPriceTrend, 
            state.cashValue, 
            state.equity, 
            state.pending_action, 
            state.entry_day, 
            state.exit_day) = TradingEngine.process_one_day(state, 
                                                            day, 
                                                            my_date, 
                                                            closingPrice, 
                                                            average, 
                                                            nextDayOpeningPrice)

        else:

            (state.positionMeanReversion, 
            state.profitMeanReversion, 
            state.entryPriceMeanReversion, 
            state.exitPriceMeanReversion, 
            state.cashValue, 
            state.equity, 
            state.pending_action, 
            state.entry_day, 
            state.exit_day) = TradingEngine.process_one_day(state, 
                                                            day, 
                                                            my_date, 
                                                            closingPrice, 
                                                            average, 
                                                            nextDayOpeningPrice)

    @staticmethod 
    def backtest_start_logging_event(state:ExecutionState) -> None:
        """ The beginning of the backtest running engine is logged as the starting event in the form of a dictionary,
        and then added to a list of logged events. 

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1, 
                                                        float("nan"), 
                                                        None, 
                                                        state.ticker_name, 
                                                        TradingEngine.strategy(state), 
                                                        "BACKTEST_START",
                                                        "Backtest started",
                                                        state.startingCashValue, 
                                                        state.equity, 
                                                        TradingEngine.position(state),
                                                        None, 
                                                        None,
                                                        None)
        state.list_dictionaries_event_logs.append(event_log_row)

    @staticmethod 
    def buy_executed_log_event(state:ExecutionState , day:int , my_date:date ) -> None:
        """ Whenever a buy happens, it's logged as a buying executed event in the form of a dictionary,
        and then added to a list of logged events. 

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                        day, my_date, state.ticker_name,
                                                        TradingEngine.strategy(state),
                                                        "BUY_EXECUTED",
                                                        "A Buy has been executed",
                                                        state.cashValue,
                                                        state.equity,
                                                        TradingEngine.position(state),
                                                        TradingEngine.entry_price(state) ,
                                                        None ,
                                                        TradingEngine.labels(state) )
        state.list_dictionaries_event_logs.append(event_log_row)

    @staticmethod
    def sell_executed_log_event(state: ExecutionState , day: int , my_date: date) -> None:
        """ Whenever a sell happens, it's logged as a selling executed event in the form of a dictionary,
        and then added to a list of logged events. 

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                        day,my_date,state.ticker_name,
                                                        TradingEngine.strategy(state),
                                                        "SELL_EXECUTED",
                                                        "A Sell has been executed",
                                                        state.cashValue,
                                                        state.equity, 
                                                        TradingEngine.position(state) ,
                                                        TradingEngine.exit_price(state) ,
                                                        TradingEngine.profit(state) ,
                                                        TradingEngine.labels(state) )
        state.list_dictionaries_event_logs.append(event_log_row)

    @staticmethod 
    def trade_closed_log_event(state: ExecutionState, day:int , my_date: date) -> None: 
        """ Whenever a sell has happened, it means that a trade took place, 
        and the trade is now closed; so it's logged as a trading event in the form of a dictionary,
        and then added to a list of logged events. 

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                        day,
                                                        my_date,
                                                        state.ticker_name,
                                                        TradingEngine.strategy(state) ,
                                                        "TRADE_CLOSED",
                                                        "A Trade has been executed",
                                                        state.cashValue,
                                                        state.equity,
                                                        TradingEngine.position(state) ,
                                                        TradingEngine.exit_price(state) ,
                                                        TradingEngine.profit(state) ,
                                                        TradingEngine.labels(state) )
        state.list_dictionaries_event_logs.append(event_log_row)

    @staticmethod
    def backtest_end_logging_event(state: ExecutionState, day:int , my_date:date) -> None :
        """ The end of the backtest running engine is logged as the final event in the form of a dictionary,
        and then added to a list of logged events. 

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """


        event_log_row=TradingEngine.build_event_log_row(ExecutionState.backtest_run_number+1,
                                                                day,
                                                                my_date,
                                                                state.ticker_name,
                                                                TradingEngine.strategy(state),
                                                                "BACKTEST_END",
                                                                "Backtest has ended",
                                                                state.cashValue,
                                                                state.equity,
                                                                TradingEngine.position(state),
                                                                None,
                                                                state.totalProfit,
                                                                None)
        state.list_dictionaries_event_logs.append(event_log_row)

    @staticmethod
    def generator(state:ExecutionState, one_df:pd.DataFrame) -> Generator[ tuple[ int, date, float, float | None, float | None ] , 
                                                                                                  None, 
                                                                                                  None ] :
        """ Stores the yielded tuple ( day, date, closingPrice, average, openingPrice ) for days >= 3 
        from read_ticker_dataframe()'s generator into a variable , and returns it so that it can later be used for unpacking
        in the main for loop. 
        
        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
            one_df (pd.DataFrame): OHLC price data for a single ticker, as consumed by dl.read_ticker_dataframe

        Returns:
            tuple[Any]: ( day,date,closingPrice,average, openingPrice )
        """

        generator = dl.read_ticker_dataframe(one_df, state.cashValue, state.verbose_run)
        return generator

    @staticmethod
    def build_dictionary_prices(state: ExecutionState , 
                                day : int, 
                                my_date : date ,
                                closingPrice : float ,
                                average : float | None ) -> None : 
        """Computes a dictionary which represents a single row in the 'price' data frame 

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
            day (int): the current day 
            my_date (date): current date 
            closingPrice (float): closing price for that day 
            average (float | None): running average ( None on days 1 and 2 )
        """

        price_row=TradingEngine.build_price_row(day, 
                                                my_date, 
                                                state.ticker_name, 
                                                TradingEngine.strategy(state), 
                                                closingPrice, 
                                                average )
        # append to the list of dictionaries/rows for the price data frame 
        state.list_dictionaries_prices.append(price_row)

    @staticmethod 
    def process_one_day(state : ExecutionState , 
                        day , 
                        my_date , 
                        closingPrice , 
                        average , 
                        nextDayOpeningPrice ) -> tuple[Any] :
        """
        Wrapper around process_1_day.process_one_day(). Instead of passing 23 separate
        arguments at the call site, it takes the state object plus the 5 values that
        change each day, and pulls everything else off the state itself.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
            day (int): which day of the backtest this is
            my_date (date): the calendar date for that day
            closingPrice (float): that day's closing price
            average (float): the average of all closing prices up to the current day, current day excluded
            nextDayOpeningPrice (float): the opening price used to execute the trade

        Returns:
            tuple[Any]: ( position, profit, entryPrice, exitPrice, cashValue, equity, pending_action, entry_day, exit_day )
        """

        tuple_results = process_1_day.process_one_day(
                                                        state.verbose_run, 
                                                        day, 
                                                        my_date, 
                                                        closingPrice, 
                                                        average, 
                                                        nextDayOpeningPrice, 
                                                        state.cashValue, 
                                                        state.equity, 
                                                        state.pending_action, 
                                                        state.positionSizing, 
                                                        state.flat_fee_per_share, 
                                                        state.fixed_bps, 
                                                        state.trendMethod, 
                                                        state.positionTrend, 
                                                        state.entry_day, 
                                                        state.exit_day, 
                                                        state.entryPriceTrend, 
                                                        state.exitPriceTrend, 
                                                        state.profitTrend, 
                                                        state.positionMeanReversion, 
                                                        state.entryPriceMeanReversion, 
                                                        state.exitPriceMeanReversion, 
                                                        state.profitMeanReversion
                                                    )
        return tuple_results

    @staticmethod 
    def build_dictionary_trades( state : ExecutionState ) -> None :
        """
        Builds one completed trade as a dictionary and adds it to the list of all
        completed trades. Works for either strategy — the accessors pick the right
        entry price, exit price and profit off the state.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
        """

        one_completed_trade_row=TradingEngine.build_one_completed_trade_row(ExecutionState.backtest_run_number+1,
                                                                            state.ticker_name,
                                                                            TradingEngine.strategy(state),
                                                                            state.entry_day,
                                                                            round( TradingEngine.entry_price(state) , 3 ) ,
                                                                            state.exit_day ,
                                                                            round( TradingEngine.exit_price(state) , 3 ) ,
                                                                            round( TradingEngine.profit(state) , 3 ) ,
                                                                            round((( TradingEngine.exit_price(state) - TradingEngine.entry_price(state) ) / TradingEngine.entry_price(state) ) * 100 , 2 ) ,
                                                                            TradingEngine.labels(state))
        # add it to the list of all dictionaries 
        state.list_dictionaries_completed_trades.append(one_completed_trade_row)

    @staticmethod
    def run_strategy_day( state: ExecutionState ,
                       day:int , 
                       my_date : date ,
                       closingPrice : float , 
                       average : float ,
                       nextDayOpeningPrice : float ) -> None :
        """
        Runs one trading day for whichever strategy the state is running.

        Records the day's price row, remembers the profit and position from before
        the day is processed, then processes the day through update_portfolio_state().

        If the profit changed, a trade took place: it records the completed trade,
        adds the profit to the total, and increments the counters for winning or
        losing trades.

        It then compares the position from before the day against the position after,
        to work out whether shares were bought or sold, and logs the matching events.

        Finally, adds the day's equity to the equity curve.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy
            day (int): which day of the backtest this is
            my_date (date): the calendar date for that day
            closingPrice (float): that day's closing price
            average (float): the average of all closing prices up to the current day, current day excluded
            nextDayOpeningPrice (float): the opening price used to execute the trade
        """

        TradingEngine.build_dictionary_prices(
                                                state, 
                                                day, 
                                                my_date,
                                                closingPrice,
                                                average
                                            )
        
        #we only compute when there's a change in the profit 
        previousProfit = TradingEngine.profit(state)

        # before "process_1_day()" we hold no shares
        previous_position = TradingEngine.position(state)

        # Process one trading day, update portfolio state, and print the day’s execution/output details
        TradingEngine.update_portfolio_state(

            state,
            day,
            my_date,
            closingPrice,
            average,
            nextDayOpeningPrice

        )

        # change in profit => SELL day
        if( ( TradingEngine.profit(state) - previousProfit ) !=0 ):

            TradingEngine.build_dictionary_trades(state)

            state.totalProfit += TradingEngine.profit(state)

            TradingEngine.increment_trade_count(state)

            if( TradingEngine.profit(state) > 0 ):

                TradingEngine.increment_positive_profit(state)

                TradingEngine.increment_total_profit_positive_trades(state)

            #P&L is negative
            else:

                TradingEngine.increment_negative_profit(state)

                TradingEngine.increment_total_profit_negative_trades(state)

        # after "process_1_day()" we might hold shares if we bought any 
        current_position = TradingEngine.position(state)

        # we check if after "process_1_day()" we hold any shares or not compared to before "process_1_day()"
        # if after "process_1_day()" we do hold shares, but before it we didn't =>
        # we bought => we compute BUY_EXECUTED logging event 
        if ( previous_position == 0 and current_position > 0 ):

            TradingEngine.buy_executed_log_event(state, day, my_date)

        # if after "process_1_day()" we don't hold any shares anymore, but before it we did =>
        # we sold => we compute SELL_EXECUTED logging event 
        if ( previous_position > 0 and current_position == 0 ):

            TradingEngine.sell_executed_log_event(state, day, my_date)

            TradingEngine.trade_closed_log_event(state, day, my_date)

        #add trading day's equity to the equity curve 
        state.listStoreEquityValues.append(state.equity)

    @staticmethod 
    def run_days_one_and_two( state: ExecutionState,
                              day : int,
                              my_date : date,
                              closingPrice : float ) -> None :

        state.listStoreEquityValues.append(state.equity)

        TradingEngine.build_dictionary_prices(
                                                state, 
                                                day, 
                                                my_date,
                                                closingPrice,
                                                None
                                            )

    @staticmethod
    def build_prices_data_frame( state : ExecutionState ) -> pd.DataFrame :
        """Turns the list of price dictionaries collected during the backtest into a data frame.

        Args:
            state (ExecutionState): holds list_dictionaries_prices, one dictionary per day.

        Returns:
            pd.DataFrame: one row per day, used for the price markers on the plotting chart.
        """

        # data frame for all the prices of the backtest used for the price markers plotting chart
        price_data_frame = pd.DataFrame(data=state.list_dictionaries_prices)

        return price_data_frame

    @staticmethod
    def build_log_events_data_frame( state : ExecutionState ) -> pd.DataFrame :
        """Turns the list of log event dictionaries collected during the backtest into a data frame.

        Args:
            state (ExecutionState): holds list_dictionaries_event_logs, one dictionary per logged event.

        Returns:
            pd.DataFrame: one row per event, with the day column as a nullable integer so it prints without a decimal.
        """

        # data frame containing all of the 5 logging events (backtest_start,buy_executed,sell_executed,trade_closed,backtest_end) in the list converted into a pandas data frame
        loggingEventsDataFrame=pd.DataFrame(data=state.list_dictionaries_event_logs)
        # converts the day column to pandas nullable integer type — pd.Int64Dtype() — which supports NaN without forcing float promotion => "day" won't be printed with a .0 decimal anymore 
        loggingEventsDataFrame["day"] = loggingEventsDataFrame["day"].astype(pd.Int64Dtype())

        return loggingEventsDataFrame

    @staticmethod
    def build_trades_data_frame( state : ExecutionState ) -> pd.DataFrame :
        """Turns the list of completed trade dictionaries collected during the backtest into a data frame.

        Args:
            state (ExecutionState): holds list_dictionaries_completed_trades, one dictionary per closed trade.

        Returns:
            pd.DataFrame: one row per trade, with a number_trades_took_place column counting the trades within each run. If no trades were made, returns an empty frame with those same columns.
        """

        # final data frame containing all the completed trades in the list converted into a pandas data frame
        tradesDataFrame = pd.DataFrame(data=state.list_dictionaries_completed_trades)
        if tradesDataFrame.empty:
            tradesDataFrame = pd.DataFrame(columns=["run_number", "ticker", "strategy", "entry_day", "entry_price", "exit_day", "exit_price", "profit", "return_pct", "labels", "number_trades_took_place"])
        else:
            tradesDataFrame["number_trades_took_place"] = tradesDataFrame.groupby(by="run_number").cumcount() + 1

        return tradesDataFrame

    @staticmethod
    def build_drawdown_series_data_frame( state : ExecutionState ) -> pd.DataFrame :
        """Builds the drawdown series data frame from the daily equity values collected during the backtest.

        For each day it works out the running peak equity so far, how far below that peak the equity is (the drawdown), and that drop as a percentage.

        Args:
            state (ExecutionState): holds listStoreEquityValues, one equity value per day.

        Returns:
            pd.DataFrame: one row per day, with a labels column that uniquely identifies each line.
        """

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

        return drawdown_series

    @staticmethod
    def build_equity_curve_data_frame( state : ExecutionState ) -> pd.DataFrame :
        """Builds the equity curve data frame by taking only the columns needed for plotting out of the drawdown series.

        Args:
            state (ExecutionState): the state object which represents either Trend or Mean Reversion strategy.

        Returns:
            pd.DataFrame: one row per day, holding just the day, run number, ticker, strategy, equity and labels.
        """

        drawdown_series = TradingEngine.build_drawdown_series_data_frame(state)

        # equity curve final computed data frame from all dictionary rows 
        equity_curve_data_frame = drawdown_series[ ["day", "run_number", "ticker", "strategy", "equity","labels"] ]

        return equity_curve_data_frame

    @staticmethod
    def backtest_run( state: ExecutionState, one_df: pd.DataFrame ) -> dict[ str , pd.DataFrame ] : 

        """ Runs a full backtest for one ticker: iterates day-by-day over one_df, delegating each day's
        buy/sell decision to process_1_day (Trend or Mean Reversion, per state.trendMethod), and logs
        BUY_EXECUTED/SELL_EXECUTED/TRADE_CLOSED events, completed trades, prices, and the equity/drawdown
        series as they occur. Mutates `state` in place; calls state.reset() first so the instance can be reused


        Args:
            state (ExecutionState): mutable run state (cash, position, strategy config); reset() is called at the start
            one_df (pd.DataFrame): OHLC price data for a single ticker, as consumed by dl.read_ticker_dataframe

        Returns:
            dict: {"log_events", "equity_curve", "drawdown_series", "trades", "prices"} — one DataFrame each
        """

        # first, reset all variables back to 0 in case you are reusing the same ExecutionState instance twice 
        state.reset()
        
        TradingEngine.backtest_start_logging_event(state)        
        
        # 1 "for" loop iteration=1 day executed,  entire "for" loop iteration=1 full backtest run 
        for extracted_tuple in dl.read_ticker_dataframe(one_df, state.cashValue, state.verbose_run):

            day , my_date , closingPrice , average , nextDayOpeningPrice = extracted_tuple

            #Days starting from day 3 onwards 
            if(average!=None):

                TradingEngine.run_strategy_day(

                    state,
                    day,
                    my_date,
                    closingPrice,
                    average,
                    nextDayOpeningPrice

                )

            # Days 1 and 2 
            else:

                TradingEngine.run_days_one_and_two(
                                                    state, 
                                                    day,
                                                    my_date,
                                                    closingPrice
                                                )

        state.totalProfit = state.equity - state.startingCashValue
                
        TradingEngine.backtest_end_logging_event(state, day, my_date)

        # count the number of backtest runs at Class level (not per engine instance)
        ExecutionState.backtest_run_number+=1

        price_data_frame = TradingEngine.build_prices_data_frame(state)

        log_events_data_frame = TradingEngine.build_log_events_data_frame(state)
        
        trades_data_frame = TradingEngine.build_trades_data_frame(state)
        
        drawdown_series = TradingEngine.build_drawdown_series_data_frame(state)

        equity_curve_data_frame = TradingEngine.build_equity_curve_data_frame(state)

        # single dictionary containing all structured data outputs's (run data frame, equity curve, trades, drawdown series, log events) final computed data frames 
        dictionary_data_frames=TradingEngine.build_data_frames(log_events_data_frame,
                                                               equity_curve_data_frame,
                                                               drawdown_series,
                                                               trades_data_frame,
                                                               price_data_frame)
        
        return dictionary_data_frames
    
    @staticmethod
    def try_except_performance_metric(fn) -> float : 
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
    def strategy_performance_metrics_stats(state: ExecutionState)-> dict[str,Any] :
        """Selects the correct set of trade statistics from state based on the active strategy.

        Args:
            state (ExecutionState): current backtest state

        Returns:
            dict: trade statistics keyed by positive_count, negative_count, trade_count, positive_total, negative_total
        """
        if TradingEngine.strategy(state) == 'Trend' :

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
                y="total_net_profit",
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
        ticker_strategy_closing_prices=ticker_strategy_data_frame["closing_price"]
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

    def __init__( self , results_data_frames : dict[str, pd.DataFrame] ) -> None :
        """Stores the structured data frames so the summaries can be computed from them.

        Args:
            results_data_frames (dict): the dictionary of final data frames coming out of ExperimentRunner.

        Raises:
            TypeError: if what gets passed in isn't a dictionary.
        """

        if not isinstance(results_data_frames,dict):

            raise TypeError("The resulting data frames need to be stored inside a dictionary")
        
        self.results_data_frames = results_data_frames

    @staticmethod
    def build_average_performance_summary(average_total_net_profit : float ,
                                          average_mdd : float ,
                                          average_expectancy : float ,
                                          average_payoff_ratio : float , 
                                          average_profit_factor : float ,
                                          average_sharpe_ratio : float) -> dict[str, float] :
        """Puts the six averages into one dictionary so they can be printed as a summary.

        Args:
            average_total_net_profit (float): average total net profit across all the runs.
            average_mdd (float): average maximum drawdown across all the runs.
            average_expectancy (float): average expectancy across all the runs.
            average_payoff_ratio (float): average payoff ratio across all the runs.
            average_profit_factor (float): average profit factor across all the runs.
            average_sharpe_ratio (float): average sharpe ratio across all the runs.

        Returns:
            dict[str, float]: the six averages keyed by their names.
        """
        
        return {

            "average total net profit":average_total_net_profit,
            "average mdd":average_mdd,
            "average expectancy":average_expectancy,
            "average payoff ratio":average_payoff_ratio,
            "average profit factor":average_profit_factor,
            "average sharpe ratio": average_sharpe_ratio

        }
    
    @staticmethod
    def build_aggregation_outputs(total_runs : int ,
                                  best_run_summary : dict ,
                                  worst_run_summary : dict ,
                                  average_performance_summary : dict ,
                                  selected_run_summary : dict ,
                                  selected_run_trade_list : pd.DataFrame ) -> dict[ str , Any ] :
        """Puts all the aggregation results into one dictionary so they can be returned together.

        Args:
            total_runs (int): how many backtest runs were made.
            best_run_summary (dict): the summary of the best performing run.
            worst_run_summary (dict): the summary of the worst performing run.
            average_performance_summary (dict): the six averages across all the runs.
            selected_run_summary (dict): the summary of the run that was picked.
            selected_run_trade_list (pd.DataFrame): all the completed trades belonging to the picked run.

        Returns:
            dict[str, Any]: the six aggregation outputs keyed by their names.
        """

        return {

            "total_runs": total_runs,
            "best_run_summary":best_run_summary,
            "worst_run_summary":worst_run_summary,
            "average_performance_summary":average_performance_summary,
            "selected_run_summary":selected_run_summary,
            "selected_run_trade_list":selected_run_trade_list

        }

    def total_runs_summary( self ) -> int : 
        """Counts how many backtest runs were made.

        Returns:
            int: the number of rows in the final run data frame, one row per backtest run
        """

        return len(self.results_data_frames["Final Data Frame Run"])
    
    def run_summary( self , use_max : bool ) -> dict[ str , Any ] :
        """Finds the best or the worst run and returns it as a dictionary.

        Args:
            use_max (bool) : True picks the run with the highest total net profit, False picks the lowest.

        Returns:
            dict[str, Any] : that run's row from the final run data frame, keyed by column name. If more than one run tied on that value, only the first one is taken.
        """

        if use_max:

            total_net_profit = ( self.results_data_frames["Final Data Frame Run"] ["total_net_profit"] ).max()

        else:

            total_net_profit = ( self.results_data_frames["Final Data Frame Run"] ["total_net_profit"] ).min()

        boolean_mask_total_net_profit = ( self.results_data_frames["Final Data Frame Run"] ["total_net_profit"] ) == total_net_profit

        boolean_indexing = self.results_data_frames["Final Data Frame Run"] [ boolean_mask_total_net_profit ] 

        first_row = boolean_indexing.iloc[0] # select only the first row matching that value

        run_summary = first_row.to_dict() # convert the Series into a dictionary

        return run_summary
     
    def best_run_summary(self) -> dict[ str , Any ] :
        """ best run summary from the run data frame, the one with the highest total net profit

        Returns:
            dict[ str , Any ]: best run's row from the final run data frame, keyed by column name
        """

        return self.run_summary( use_max=True )
    
    def worst_run_summary(self)-> dict[ str , Any ] : 
        """ worst run summary from the run data frame, the one with the lowest total net profit

        Returns:
            dict[ str , Any ]: worst run's row from the final run data frame, keyed by column name
        """

        return self.run_summary(use_max=False)
     
    def average_performance_summary(self)-> dict[ str , float ] :
        """Works out the average of each performance metric across all the backtest runs.

        Returns:
            dict[str, float]: the six averages, each rounded to 2 decimals, keyed by their names.
        """

        average_total_net_profit=round(self.results_data_frames["Final Data Frame Run"]["total_net_profit"].mean(),2) 

        average_mdd=round(self.results_data_frames["Final Data Frame Run"]["mdd"].mean(),2)

        average_expectancy=round(self.results_data_frames["Final Data Frame Run"]["expectancy"].mean(),2)

        average_payoff_ratio=round(self.results_data_frames["Final Data Frame Run"]["payoff_ratio"].mean(),2)

        average_profit_factor=round(self.results_data_frames["Final Data Frame Run"]["profit_factor"].mean(),2)

        average_sharpe_ratio=round(self.results_data_frames["Final Data Frame Run"]["sharpe_ratio"].mean(),2)

        average_performance_summary=AggregationLayer.build_average_performance_summary(float(average_total_net_profit),
                                                                                       float(average_mdd),
                                                                                       float(average_expectancy),
                                                                                       float(average_payoff_ratio),
                                                                                       float(average_profit_factor),
                                                                                       float(average_sharpe_ratio))
        
        return average_performance_summary
    
    def selected_run_summary(self , ticker : str , strategy : str ) -> dict[ str , Any ] :
        """Picks out the run matching the ticker and strategy the user selected and returns it as a dictionary.

        Args:
            ticker (str): Apple, Google or Microsoft.
            strategy (str): Trend or Mean Reversion.

        Returns:
            dict[str, Any]: that run's row from the final run data frame, keyed by column name. If more than one run has the same ticker and strategy, only the first one is taken.

        Raises:
            ValueError: if the ticker or the strategy doesn't exist, or if no run matches that pair that the user selected.
        """

        AggregationLayer.ticker_strategy_validation(ticker,strategy)

        selected_label = f"{ticker}-{strategy}"

        labels_column = self.results_data_frames["Final Data Frame Run"] ["labels"]

        boolean_mask = ( labels_column == selected_label )

        boolean_index = ( self.results_data_frames["Final Data Frame Run"] [ boolean_mask ] )

        if boolean_index.empty : 

            raise ValueError("The selected run summary data frame is empty")

        selected_run_summary = boolean_index.iloc[0] # if multiple identical ticker/strategy pairs, pick the first pair only

        selected_run_summary = selected_run_summary.to_dict()

        return selected_run_summary

    def selected_run_trade_list(self, ticker :str , strategy : str )-> pd.DataFrame :
        """Picks out all the completed trades belonging to the ticker and strategy the user selected.

        Args:
            ticker (str): Apple, Google or Microsoft.
            strategy (str): Trend or Mean Reversion.

        Returns:
            pd.DataFrame: every trade row matching that ticker and strategy pair.

        Raises:
            ValueError: if the ticker or the strategy doesn't exist, or if no trades match that pair.
        """

        AggregationLayer.ticker_strategy_validation(ticker,strategy)

        selected_label = f"{ticker}-{strategy}"

        labels_column = self.results_data_frames["Completed Trades"] ["labels"]

        boolean_mask = ( labels_column == selected_label )

        boolean_index = ( self.results_data_frames["Completed Trades"] [ boolean_mask ] )

        if boolean_index.empty:

            raise ValueError("The selected run trade list is empty")
        
        return boolean_index
    
    @staticmethod
    def ticker_strategy_validation(ticker:str , strategy:str) -> None : 
        """Checks that the ticker and the strategy the user selected are ones the backtest actually ran.

        Args:
            ticker (str): Apple, Google or Microsoft.
            strategy (str): Trend or Mean Reversion.

        Raises:
            ValueError: if the ticker isn't one of the three, or if the strategy isn't one of the two.
        """

        if ticker not in ["Apple", "Google", "Microsoft"]:

            raise ValueError("This selected ticker does not exist")
        
        if strategy not in ["Trend", "Mean Reversion"]:

            raise ValueError("This selected strategy does not exist")
        
    def aggregation_outputs(self , ticker:str , strategy:str) -> dict[ str, Any ] :
        """Collects the already-working pieces into one dictionary.

        Calls/reuses: total runs, best run summary, worst run summary, average performance summary,
        selected run summary and selected run trade list.

        Args:
            ticker (str): Apple, Google or Microsoft.
            strategy (str): Trend or Mean Reversion.

        Returns:
            dict[str, Any]: the six aggregation outputs, ready to be handed to the UI.
        """

        aggregation_outputs=AggregationLayer.build_aggregation_outputs(self.total_runs_summary() ,
                                                                       self.best_run_summary(),
                                                                       self.worst_run_summary(),
                                                                       self.average_performance_summary(),
                                                                       self.selected_run_summary(ticker , strategy),
                                                                       self.selected_run_trade_list(ticker , strategy) )
        return aggregation_outputs




class ExperimentRunner:
    """
    Orchestrates multiple backtest runs across different tickers and strategies.
    structured_data_outputs() instantiates one ExecutionState per configuration, runs TradingEngine
    on each, and concatenates all results into five final DataFrames returned in a single dictionary:
    Final Data Frame Run, Equity Curve, Drawdown Series, Completed Trades, Log Events.
    """

    @staticmethod
    def build_results(run_data_frame : pd.DataFrame,
                      equity_curves_df : pd.DataFrame,
                      drawdown_series_df : pd.DataFrame,
                      trades_df : pd.DataFrame,
                      log_events_df : pd.DataFrame,
                      prices_df : pd.DataFrame) -> dict[ str, pd.DataFrame ] :
        """Bundle the six per-run DataFrames into a single labelled dict.

        Args:
            run_data_frame: Per-bar state for the completed run.
            equity_curves_df: Equity value over time.
            drawdown_series_df: Drawdown over time.
            trades_df: One row per completed trade.
            log_events_df: Events emitted during the run.
            prices_df: Price bars used by the run.

        Returns:
            dict[str, pd.DataFrame]: The same frames keyed by display name
            ("Final Data Frame Run", "Equity Curve", "Drawdown Series",
            "Completed Trades", "Log Events", "Prices").
        """

        return{

            "Final Data Frame Run":run_data_frame,
            "Equity Curve":equity_curves_df,
            "Drawdown Series":drawdown_series_df,
            "Completed Trades":trades_df,
            "Log Events":log_events_df,
            "Prices":prices_df

        }

    @staticmethod
    def state( symbol : str , trendMethod : bool , cashValue = 10000 ) -> ExecutionState : 
        """Build one ExecutionState from the passed in arguments.

        Args:
            symbol (str): ticker symbol the state runs on (e.g. "AAPL")
            trendMethod (bool): True = Trend strategy, False = Mean Reversion strategy
            cashValue (float, optional): starting cash for the run. Defaults to 10000.

        Raises:
            KeyError: if the symbol is not in the COMPANY_NAMES dictionary

        Returns:
            ExecutionState: 1 state object corresponding to 1 backtest run,
            with ticker_name looked up from the COMPANY_NAMES dictionary
        """

        if symbol not in COMPANY_NAMES : 
        
            raise ValueError( f"The selected ticker {symbol} is not in the dictionary of selected companies" )
    
        return ExecutionState(
            
                    trendMethod = trendMethod ,
                    symbol = symbol ,
                    cashValue = cashValue ,
                    ticker_name = COMPANY_NAMES[symbol] ,
                    
            )
        
    @staticmethod
    def fetch_bars_by_symbol( selected_tickers : str ) -> dict[ str , pd.DataFrame ] : 
        """Extract the historical bars for all the selected tickers through dl.hist_data().

        Args:
            selected_tickers (str): comma-separated string of all the tickers you wanna request data from (e.g. "AAPL,GOOGL,MSFT")

        Returns:
            dict[str,pd.DataFrame]: dictionary consisting of all the tickers as keys,
            and their corresponding OHLCV bars data frames as the values
            (timeframe, start, end and limit are fixed inside this method)
        """
    
        bars_by_symbol = dl.hist_data( selected_tickers , timeframe='1Day', start="2024-01-16", end="2026-01-13", limit=1000)

        return bars_by_symbol

    @staticmethod
    def structured_data_outputs( selected_tickers : str ) -> dict[ str , pd.DataFrame ] : 
        """Run the full experiment: 1 backtest run per (ticker, strategy) combination, and collect all the outputs.

        Fetches the bars for all the selected tickers, then for each ticker runs
        backtest_run() twice (once Trend, once Mean Reversion). Each run's output
        data frames get appended to their corresponding list, then each list gets
        concatenated into 1 final data frame across all the runs.

        Args:
            selected_tickers (str): comma-separated string of all the tickers you wanna run the experiment on (e.g. "AAPL,GOOGL,MSFT")

        Returns:
            dict[str,pd.DataFrame]: the final results dictionary built by build_results(),
            containing the 6 structured data outputs (final run data frame, equity curve,
            drawdown series, completed trades, log events, prices), each one key-accessible
        """

        equity_curves_logs=[]
        drawdown_series=[]
        trades=[]
        log_events=[]
        prices=[]
        data_frames_run=[]
        
        results={}

        bars_by_symbol = ExperimentRunner.fetch_bars_by_symbol( selected_tickers )

        for symbol in bars_by_symbol : 

            bars_df = bars_by_symbol[symbol]

            for trendMethod in ( True , False ) : 

                state = ExperimentRunner.state( symbol , trendMethod ) 

                dictionary_data_frames = TradingEngine.backtest_run( state , bars_df )

                equity_curves_logs.append(dictionary_data_frames["equity_curve"])
                drawdown_series.append(dictionary_data_frames["drawdown_series"])
                trades.append(dictionary_data_frames["trades"])
                log_events.append(dictionary_data_frames["log_events"])
                prices.append(dictionary_data_frames["prices"])

                data_frames_run.append(TradingEngine.performance_metrics_data_frame(state))

        equity_curves_df = pd.concat(equity_curves_logs)  
        drawdown_series_df = pd.concat(drawdown_series)
        trades_df = pd.concat(trades)
        log_events_df = pd.concat(log_events)
        prices_df = pd.concat(prices)

        final_data_frame_run = pd.concat( data_frames_run )

        results = ExperimentRunner.build_results(

            final_data_frame_run,
            equity_curves_df,
            drawdown_series_df,
            trades_df,
            log_events_df,
            prices_df

        )       

        return results

        
        


if __name__ == "__main__" :

    # selected_tickers = input( "Enter the desired selected tickers: " )

    results = ExperimentRunner.structured_data_outputs( selected_tickers )

    plottedChart=PlottingLayer(results)
    
    aggregationLayerSummary=AggregationLayer(results)

    plottedChart.user_interface_oriented_plotting_equity_curve()
    plottedChart.user_interface_oriented_plotting_drawdown_series()
    plottedChart.user_interface_oriented_plotting_completed_trades()
    plottedChart.user_interface_oriented_plotting_log_events()
    plottedChart.user_interface_oriented_plotting_run_data_frame()
    plottedChart.user_interface_oriented_plotting_price_chart("Apple", "Trend")
    
    print(results["Final Data Frame Run"])
    print(results["Completed Trades"])
    print(results["Drawdown Series"])
    print(results["Equity Curve"])
    print(results["Log Events"])
    print(results["Prices"]) 