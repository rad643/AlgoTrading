from unittest import TestCase
from unittest.mock import Mock
import main 
from data_loading import data_loader as dl 
import pandas as pd 
from datetime import date 
from pathlib import Path 
import math 


class TestExecutionState(TestCase):

    def setUp(self):

        self.state = main.ExecutionState(trendMethod=True, symbol='AAPL', cashValue=10000, ticker_name='Apple')

    def test_post_init(self):

        self.assertEqual( self.state.startingCashValue, self.state.cashValue)
        self.assertEqual( self.state.positionSizing, 0.2*self.state.cashValue)
        self.assertEqual( self.state.equity, self.state.cashValue)

    def test_reset(self):

        self.state.reset()

        self.assertEqual( self.state.listStoreEquityValues, [] )
        self.assertEqual( self.state.cashValue, self.state.startingCashValue)
        self.assertEqual( self.state.positionSizing, self.state.cashValue*0.2)
        self.assertEqual( self.state.equity, self.state.cashValue)
        self.assertEqual( self.state.positionTrend, 0)
        self.assertEqual( self.state.entry_day, 0)
        self.assertEqual( self.state.exit_day, 0)
        self.assertEqual( self.state.entryPriceTrend, 0)
        self.assertEqual( self.state.exitPriceTrend, 0)
        self.assertEqual( self.state.profitTrend, 0)
        self.assertEqual( self.state.positionMeanReversion, 0)
        self.assertEqual( self.state.entryPriceMeanReversion, 0)
        self.assertEqual( self.state.exitPriceMeanReversion, 0)
        self.assertEqual( self.state.profitMeanReversion, 0)
        self.assertEqual( self.state.totalProfit, 0)
        self.assertEqual( self.state.positiveProfitTrend, 0)
        self.assertEqual( self.state.negativeProfitTrend, 0)
        self.assertEqual( self.state.positiveProfitMeanRev, 0)
        self.assertEqual( self.state.negativeProfitMeanRev, 0)
        self.assertEqual( self.state.positionSizing, self.state.cashValue*0.2)
        self.assertEqual( self.state.numberTradesTrend, 0)
        self.assertEqual( self.state.numberTradesMeanRev, 0)
        self.assertEqual( self.state.totalProfitPositiveTradesTrend, 0)
        self.assertEqual( self.state.totalProfitNegativeTradesTrend, 0)
        self.assertEqual( self.state.totalProfitPositiveTradesMeanRev, 0)
        self.assertEqual( self.state.totalProfitNegativeTradesMeanRev, 0)
        self.assertEqual( self.state.pending_action, '')


class TestTradingEngineWiringFunctions(TestCase):

    def test_build_data_frames(self):
        """ build 5 simple abstract data frames (values can be anything).
        Tests that the method builds the dictionary keys from passed in arguments.
        Checks that the dictionary values are the same data frame objects as the arguments that were passed in
        and not just copies (identical content)  """

        log_events = { 'col1': [1,2], 'col2': [3,4] }
        log_events_df = pd.DataFrame(data=log_events)

        equity_curve = { 'col1': [5,6], 'col2': [7,8] }
        equity_curve_df = pd.DataFrame(data=equity_curve)

        drawdown_series = { 'col1': [9,10], 'col2': [11,12] }
        drawdown_series_df = pd.DataFrame(data=drawdown_series)

        trades = { 'col1': [13,14], 'col2': [15,16] }
        trades_df = pd.DataFrame(data=trades)

        prices = { 'col1': [17,18], 'col2': [19,20] }
        prices_df = pd.DataFrame(data=prices)
        
        dict_df = main.TradingEngine.build_data_frames(log_events_df,
                                                       equity_curve_df,
                                                       drawdown_series_df,
                                                       trades_df,
                                                       prices_df)

        self.assertEqual( len(dict_df), 5 )
        self.assertIs( dict_df['log_events'], log_events_df )
        self.assertIs( dict_df['equity_curve'], equity_curve_df )
        self.assertIs( dict_df['drawdown_series'], drawdown_series_df )
        self.assertIs( dict_df['trades'], trades_df )
        self.assertIs( dict_df['prices'], prices_df )

    def test_build_run_df(self):
        """ build 11 simple abstract variables (values can be anything).
        Tests that the method builds the dictionary keys from passed in arguments.
        Checks that the dictionary values are the same objects as the arguments that were passed in
        and not just copies (identical content)  """
        
        run_number = 1
        ticker='Apple'
        strategy = 'Trend'
        starting_cash = 100
        total_net_profit= 3
        mdd= 4
        expectancy= 5
        payoff_ratio = 6
        profit_factor= 7
        sharpe_ratio= 8
        labels='Apple-Trend'

        d = main.TradingEngine.build_run_df(run_number,
                ticker,
                strategy,
                starting_cash,
                total_net_profit,
                mdd,
                expectancy,
                payoff_ratio,
                profit_factor,
                sharpe_ratio,
                labels)

        self.assertEqual( len(d), 11 )
        self.assertEqual( d['run_number'], run_number )
        self.assertEqual( d['ticker'], ticker )
        self.assertEqual( d['strategy'], strategy )
        self.assertEqual( d['starting_cash'], starting_cash )
        self.assertEqual( d['total_net_profit'], total_net_profit )
        self.assertEqual( d['mdd'], mdd)
        self.assertEqual( d['expectancy'], expectancy)
        self.assertEqual( d['payoff_ratio'], payoff_ratio)
        self.assertEqual( d['profit_factor'], profit_factor)
        self.assertEqual( d['sharpe_ratio'], sharpe_ratio)
        self.assertEqual( d['labels'], labels)

    def test_build_drawdown_series(self):
        """ build 8 simple abstract variables (values can be anything).
        Tests that the method builds the dictionary keys from passed in arguments.
        Checks that the dictionary values are the same objects as the arguments that were passed in
        and not just copies (identical content) """

        day = 1
        run_number = 1
        ticker = "Apple"
        strategy = "Trend"
        equity = 10000.56
        peak_so_far_ = 12000.34
        drawdown = -500.56
        drawdown_pct = -21.45

        dict_drawdown_serie = main.TradingEngine.build_drawdown_series(day,
                                                 run_number,
                                                 ticker,
                                                 strategy,
                                                 equity, 
                                                 peak_so_far_,
                                                 drawdown, 
                                                 drawdown_pct)

        self.assertEqual( len(dict_drawdown_serie), 8)
        self.assertIs( dict_drawdown_serie['day'], day)
        self.assertIs( dict_drawdown_serie['run_number'], run_number )
        self.assertIs( dict_drawdown_serie['ticker'], ticker)
        self.assertIs( dict_drawdown_serie['strategy'], strategy)
        self.assertIs( dict_drawdown_serie['equity'], equity )
        self.assertIs( dict_drawdown_serie['peak_so_far'], peak_so_far_)
        self.assertIs( dict_drawdown_serie['drawdown'], drawdown )
        self.assertIs( dict_drawdown_serie['drawdown_pct'], drawdown_pct )

    def test_build_one_completed_trade_row(self):
        """ build 10 simple abstract variables (values can be anything).
        Tests that the method builds the dictionary keys from passed in arguments.
        Checks that the dictionary values are the same objects as the arguments that were passed in
        and not just copies (identical content)"""

        run_number = 1
        ticker= 'Apple'
        strategy = 'Trend'
        entry_day = 45
        entry_price = 320.56
        exit_day = 120
        exit_price = 315.23
        profit = 100.23
        return_pct = 5.67
        labels = 'Apple-Trend'

        dict_df = main.TradingEngine.build_one_completed_trade_row(
            run_number,
            ticker,
            strategy, 
            entry_day,
            entry_price, 
            exit_day,
            exit_price, 
            profit, 
            return_pct, 
            labels 
        )

        self.assertEqual( len(dict_df), 10 )
        self.assertIs( dict_df['run_number'], run_number)
        self.assertIs( dict_df['ticker'], ticker)
        self.assertIs( dict_df['strategy'], strategy)
        self.assertIs( dict_df['entry_day'], entry_day)
        self.assertIs( dict_df['entry_price'], entry_price)
        self.assertIs( dict_df['exit_day'], exit_day)
        self.assertIs( dict_df['exit_price'], exit_price)
        self.assertIs( dict_df['profit'], profit )
        self.assertIs( dict_df['return_pct'], return_pct )
        self.assertIs( dict_df['labels'], labels )

    def test_build_event_log_row(self):
        """ build 13 simple abstract variables (values can be anything).
        Tests that the method builds the dictionary keys from passed in arguments.
        Checks that the dictionary values are the same objects as the arguments that were passed in
        and not just copies (identical content) """

        run_number = 1
        day = 3
        my_date = date( 2024, 1, 20 )
        ticker = "Apple"
        strategy = "Mean Reversion"
        event_type = 'backtest_start'
        message = 'Backtest has started'
        cash = 10000
        equity = 10320.56
        position = 10
        execution_price = 410.21
        pnl = 540.2
        labels = 'Apple-Mean Reversion'

        dict_df = main.TradingEngine.build_event_log_row(
            run_number,
            day,
            my_date,
            ticker,
            strategy,
            event_type,
            message,
            cash,
            equity,
            position, 
            execution_price, 
            pnl,
            labels
        )

        self.assertEqual( len(dict_df), 13 )
        self.assertIs( dict_df['run_number'], run_number)
        self.assertIs( dict_df['day'], day)
        self.assertIs( dict_df['date'], my_date)
        self.assertIs( dict_df['ticker'], ticker)
        self.assertIs( dict_df['strategy'], strategy)
        self.assertIs( dict_df['event_type'], event_type)
        self.assertIs( dict_df['message'], message)
        self.assertIs( dict_df['cash'], cash)
        self.assertIs( dict_df['equity'], equity)
        self.assertIs( dict_df['position'], position)
        self.assertIs( dict_df['execution_price'], execution_price)
        self.assertIs( dict_df['pnl'], pnl)
        self.assertIs( dict_df['labels'], labels)

    def test_build_price_row(self):
        """ build 6 simple abstract variables (values can be anything).
        Tests that the method builds the dictionary keys from passed in arguments.
        Checks that the dictionary values are the same objects as the arguments that were passed in
        and not just copies (identical content) """

        day = 1
        my_date = date(2026, 1 , 25)
        ticker = 'Google'
        strategy = 'Mean Reversion'
        closing_price = 345.78
        average = 450.1

        dict_df = main.TradingEngine.build_price_row(
            day,
            my_date,
            ticker,
            strategy,
            closing_price,
            average
        )

        self.assertEqual( len(dict_df), 6 )
        self.assertIs( dict_df['day'], day )
        self.assertIs( dict_df['date'], my_date )
        self.assertIs( dict_df['ticker'], ticker )
        self.assertIs( dict_df['strategy'], strategy )
        self.assertIs( dict_df['closing_price'], closing_price )
        self.assertIs( dict_df['average'], average )


class TestTradingEngineAccessors(TestCase):
    """ class that only tests the 3 accessor methods from main for their branching behavior"""

    def setUp(self):
        """ using a fixture that runs before the creation of every new test so that each test 
        can run as a clean fresh state -> isolating behavior.  
        Create 2 ExecutionState objects, 1 using Trend the other using Mean Reversion."""

        self.state_trend = main.ExecutionState(trendMethod=True, 
                                        symbol='GOOGL', 
                                        cashValue=10000, 
                                        ticker_name="Google")

        self.state_mean_reversion = main.ExecutionState(trendMethod=False, 
                                                symbol='GOOGL', 
                                                cashValue=10000, 
                                                ticker_name="Google")

    def test_strategy(self):

        result_trend = main.TradingEngine.strategy(self.state_trend)
        result_mean_reversion = main.TradingEngine.strategy(self.state_mean_reversion)

        self.assertEqual( 'Trend', result_trend )
        self.assertEqual( 'Mean Reversion', result_mean_reversion)

    def test_labels(self):

        result_trend = main.TradingEngine.labels(self.state_trend)
        result_mean_reversion = main.TradingEngine.labels(self.state_mean_reversion)

        self.assertEqual( 'Google-Trend', result_trend)
        self.assertEqual( 'Google-Mean Reversion', result_mean_reversion )
    
    def test_position(self):
        """ Hard-code each ExecutionState object's position (number of shares),
        then call the actual function from main.py to compute the position for both of the Execution State objects,
        and assert the value returned by the function against the hard-coded value"""

        self.state_trend.positionTrend = 11
        position_trend = main.TradingEngine.position(self.state_trend)
        self.assertEqual( position_trend, self.state_trend.positionTrend )

        self.state_mean_reversion.positionMeanReversion = 5
        position_mean_reversion = main.TradingEngine.position(self.state_mean_reversion)
        self.assertEqual( position_mean_reversion, self.state_mean_reversion.positionMeanReversion )

    def test_entry_price(self):

        self.state_trend.entryPriceTrend = 345.19
        entry_price_trend = main.TradingEngine.entry_price(self.state_trend)
        self.assertEqual( entry_price_trend, self.state_trend.entryPriceTrend )

        self.state_mean_reversion.entryPriceMeanReversion = 450.12
        entry_price_mean_reversion = main.TradingEngine.entry_price(self.state_mean_reversion)
        self.assertEqual( entry_price_mean_reversion, self.state_mean_reversion.entryPriceMeanReversion)

    def test_exit_price(self):
    
        self.state_trend.exitPriceTrend = 350.19
        exit_price_trend = main.TradingEngine.exit_price(self.state_trend)
        self.assertEqual( exit_price_trend, self.state_trend.exitPriceTrend )

        self.state_mean_reversion.exitPriceMeanReversion = 419.12
        exit_price_mean_reversion = main.TradingEngine.exit_price(self.state_mean_reversion)
        self.assertEqual( exit_price_mean_reversion, self.state_mean_reversion.exitPriceMeanReversion)

    def test_profit(self):
        
        self.state_trend.profitTrend = 104.54
        profit_trend = main.TradingEngine.profit(self.state_trend)
        self.assertEqual( profit_trend, self.state_trend.profitTrend )

        self.state_mean_reversion.profitMeanReversion = 312.62
        profit_mean_reversion = main.TradingEngine.profit(self.state_mean_reversion)
        self.assertEqual( profit_mean_reversion, self.state_mean_reversion.profitMeanReversion )


class TestLogEvents(TestCase):

    def setUp(self):

        self.state = main.ExecutionState(
                                        
            trendMethod = True , 
            symbol = 'AAPL' , 
            cashValue = 10000, 
            ticker_name = 'Apple'
    
        )

        self.state.entryPriceTrend = 187.5
        self.state.exitPriceTrend  = 193.2
        self.state.profitTrend     = 57.0
        self.state.positionTrend   = 10
        self.state.totalProfit     = 431.9
        self.state.cashValue       = 9500.0
        self.state.equity          = 10057.0

    def test_backtest_start_logging_event(self):

        main.TradingEngine.backtest_start_logging_event(self.state)

        row = self.state.list_dictionaries_event_logs[0]

        self.assertEqual( row['run_number'], main.ExecutionState.backtest_run_number+1 )
        self.assertTrue( math.isnan(row['day']) )
        self.assertEqual( row['date'], None )
        self.assertEqual( row['ticker'] , self.state.ticker_name )
        self.assertEqual( row['strategy'], main.TradingEngine.strategy(self.state) )
        self.assertEqual( row['event_type'], "BACKTEST_START" )
        self.assertEqual( row['message'], "Backtest started" )
        self.assertEqual( row['cash'], self.state.startingCashValue)
        self.assertEqual( row['equity'], self.state.equity)
        self.assertEqual( row['position'], main.TradingEngine.position(self.state))
        self.assertEqual( row['execution_price'], None)
        self.assertEqual( row['pnl'], None)
        self.assertEqual( row['labels'], None)

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1 )

    def test_buy_executed_log_event(self):

        day = 4
        my_date = date ( 2026 , 1 , 12 )

        main.TradingEngine.buy_executed_log_event(self.state, day, my_date)

        row = self.state.list_dictionaries_event_logs[0]

        self.assertEqual( row['run_number'], main.ExecutionState.backtest_run_number+1 )
        self.assertEqual( row['day'] , day )
        self.assertEqual( row['date'], my_date )
        self.assertEqual( row['ticker'] , self.state.ticker_name )
        self.assertEqual( row['strategy'], main.TradingEngine.strategy(self.state) )
        self.assertEqual( row['event_type'], "BUY_EXECUTED" )
        self.assertEqual( row['message'], "A Buy has been executed" )
        self.assertEqual( row['cash'], 9500.0 )
        self.assertEqual( row['equity'], 10057.0 )
        self.assertEqual( row['position'], 10 )
        self.assertEqual( row['execution_price'], 187.5 )
        self.assertEqual( row['pnl'], None )
        self.assertEqual( row['labels'], main.TradingEngine.labels(self.state))

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1 )

    def test_sell_executed_log_event(self):

        day = 5
        my_date = date ( 2024 , 8 , 25 )

        main.TradingEngine.sell_executed_log_event(self.state, day, my_date)

        row = self.state.list_dictionaries_event_logs[0]

        self.assertEqual( row['run_number'], main.ExecutionState.backtest_run_number+1 )
        self.assertEqual( row['day'] , day )
        self.assertEqual( row['date'], my_date )
        self.assertEqual( row['ticker'] , self.state.ticker_name )
        self.assertEqual( row['strategy'], main.TradingEngine.strategy(self.state) )
        self.assertEqual( row['event_type'], "SELL_EXECUTED" )
        self.assertEqual( row['message'], "A Sell has been executed" )
        self.assertEqual( row['cash'], 9500.0 )
        self.assertEqual( row['equity'], 10057.0 )
        self.assertEqual( row['position'], 10 )
        self.assertEqual( row['execution_price'], 193.2 )
        self.assertEqual( row['pnl'], 57.0 )
        self.assertEqual( row['labels'], main.TradingEngine.labels(self.state))

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1 )

    def test_trade_closed_log_event(self):

        day = 30
        my_date = date ( 2025 , 3 , 18 )

        main.TradingEngine.trade_closed_log_event(self.state, day, my_date)

        row = self.state.list_dictionaries_event_logs[0]

        self.assertEqual( row['run_number'], main.ExecutionState.backtest_run_number+1 )
        self.assertEqual( row['day'] , day )
        self.assertEqual( row['date'], my_date )
        self.assertEqual( row['ticker'] , self.state.ticker_name )
        self.assertEqual( row['strategy'], main.TradingEngine.strategy(self.state) )
        self.assertEqual( row['event_type'], "TRADE_CLOSED" )
        self.assertEqual( row['message'], "A Trade has been executed" )
        self.assertEqual( row['cash'], 9500.0 )
        self.assertEqual( row['equity'], 10057.0)
        self.assertEqual( row['position'], 10 )
        self.assertEqual( row['execution_price'], 193.2 )
        self.assertEqual( row['pnl'], 57.0 )
        self.assertEqual( row['labels'], main.TradingEngine.labels(self.state))

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1 )

    def test_backtest_end_logging_event(self):

        day = 21
        my_date = date ( 2027 , 7 , 4 )

        main.TradingEngine.backtest_end_logging_event(self.state, day, my_date)

        row = self.state.list_dictionaries_event_logs[0]

        self.assertEqual( row['run_number'], main.ExecutionState.backtest_run_number+1 )
        self.assertEqual( row['day'] , day )
        self.assertEqual( row['date'], my_date )
        self.assertEqual( row['ticker'] , self.state.ticker_name )
        self.assertEqual( row['strategy'], main.TradingEngine.strategy(self.state) )
        self.assertEqual( row['event_type'], "BACKTEST_END" )
        self.assertEqual( row['message'], "Backtest has ended" )
        self.assertEqual( row['cash'], 9500.0 )
        self.assertEqual( row['equity'], 10057.0 )
        self.assertEqual( row['position'], 10)
        self.assertEqual( row['execution_price'], None )
        self.assertEqual( row['pnl'], 431.9 )
        self.assertEqual( row['labels'], None )

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1 )

    def test_log_events_mean_reversion(self):

        state = main.ExecutionState(

            trendMethod = False ,
            symbol = 'AAPL' ,
            cashValue = 10000,
            ticker_name = 'Apple'

        )

        state.entryPriceMeanReversion = 71.1
        state.exitPriceMeanReversion  = 74.4
        state.profitMeanReversion     = 33.0
        state.positionMeanReversion   = 7

        main.TradingEngine.buy_executed_log_event(state, 4, date(2026, 1, 12))
        main.TradingEngine.sell_executed_log_event(state, 5, date(2026, 1, 13))
        main.TradingEngine.trade_closed_log_event(state, 5, date(2026, 1, 13))

        buy = state.list_dictionaries_event_logs[0]
        sell = state.list_dictionaries_event_logs[1]
        closed = state.list_dictionaries_event_logs[2]

        self.assertEqual( buy['strategy'], 'Mean Reversion' )
        self.assertEqual( buy['labels'], 'Apple-Mean Reversion' )
        self.assertEqual( buy['position'], 7 )
        self.assertEqual( buy['execution_price'], 71.1 )
        self.assertEqual( buy['pnl'], None )

        self.assertEqual( sell['execution_price'], 74.4 )
        self.assertEqual( sell['pnl'], 33.0 )
        self.assertEqual( sell['position'], 7 )

        self.assertEqual( closed['execution_price'], 74.4 )
        self.assertEqual( closed['pnl'], 33.0 )

        self.assertEqual( len(state.list_dictionaries_event_logs), 3 )








        

        




class TestTradingEngineBacktestRun(TestCase):

    def test_characterization_run(self):
        """
        Builds the path to results.txt so it lives next to test_main.py,
        no matter which folder I run pytest from.

        Runs the whole backtest and turns every DataFrame into CSV text.

        First run: write_text() creates results.txt file on disk and the test
        asserts nothing. Every run after that: compares the new output
        against that file.

        If they stop matching, my refactoring changed something.
        Delete results.txt to save a new one.
        """
        
        golden = Path(__file__).parent / 'results.txt'

        experimentRunner = main.ExperimentRunner()
        d = experimentRunner.structured_data_outputs()
        results = "\n".join(f"=== {k} ===\n{v.to_csv(index=False)}" for k, v in d.items())

        if not golden.exists():
            golden.write_text(results)
            return

        self.assertEqual(results, golden.read_text())
        
        