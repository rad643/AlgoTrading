from unittest import TestCase
from unittest.mock import Mock, patch
import pytest
import main 
from data_loading import data_loader as dl 
import pandas as pd 
from datetime import date 
from pathlib import Path 
import math 
import numpy as np

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
    """ class that only tests the 11 accessor methods from main for their branching behavior"""

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

    def test_increment_trade_count(self):

        self.state_trend.numberTradesTrend = 234
        main.TradingEngine.increment_trade_count(self.state_trend)
        self.assertEqual( self.state_trend.numberTradesTrend , 235 )

        self.state_mean_reversion.numberTradesMeanRev =  6
        main.TradingEngine.increment_trade_count(self.state_mean_reversion)
        self.assertEqual( self.state_mean_reversion.numberTradesMeanRev , 7 )

    def test_increment_positive_profit(self):

        self.state_trend.positiveProfitTrend = 58
        main.TradingEngine.increment_positive_profit(self.state_trend)
        self.assertEqual( self.state_trend.positiveProfitTrend , 59 )

        self.state_mean_reversion.positiveProfitMeanRev = 645
        main.TradingEngine.increment_positive_profit(self.state_mean_reversion)
        self.assertEqual( self.state_mean_reversion.positiveProfitMeanRev , 646 )

    def test_increment_total_profit_positive_trades(self):

        self.state_trend.totalProfitPositiveTradesTrend = 9
        self.state_trend.profitTrend = 8
        main.TradingEngine.increment_total_profit_positive_trades(self.state_trend)
        self.assertEqual( self.state_trend.totalProfitPositiveTradesTrend , 17 )

        self.state_mean_reversion.totalProfitPositiveTradesMeanRev = 20
        self.state_mean_reversion.profitMeanReversion = 10
        main.TradingEngine.increment_total_profit_positive_trades(self.state_mean_reversion)
        self.assertEqual( self.state_mean_reversion.totalProfitPositiveTradesMeanRev , 30 )

    def test_increment_negative_profit(self):

        self.state_trend.negativeProfitTrend = -30
        main.TradingEngine.increment_negative_profit(self.state_trend)
        self.assertEqual( self.state_trend.negativeProfitTrend , -29 )

        self.state_mean_reversion.negativeProfitMeanRev = -123
        main.TradingEngine.increment_negative_profit(self.state_mean_reversion)
        self.assertEqual( self.state_mean_reversion.negativeProfitMeanRev , -122 )
    
    def test_increment_total_profit_negative_trades(self):
    
        self.state_trend.totalProfitNegativeTradesTrend = -234
        self.state_trend.profitTrend = -50
        main.TradingEngine.increment_total_profit_negative_trades(self.state_trend)
        self.assertEqual( self.state_trend.totalProfitNegativeTradesTrend , -284 )

        self.state_mean_reversion.totalProfitNegativeTradesMeanRev = -345
        self.state_mean_reversion.profitMeanReversion = -10
        main.TradingEngine.increment_total_profit_negative_trades(self.state_mean_reversion)
        self.assertEqual( self.state_mean_reversion.totalProfitNegativeTradesMeanRev , -355 )


class TestLogEventsTrend(TestCase):

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


class TestLogEventsMeanReversion(TestCase):

    def setUp(self):

        self.state = main.ExecutionState(
                        
            trendMethod = False, 
            symbol = 'GOOGL', 
            cashValue = 10000 , 
            ticker_name = 'Google'

        )

    def test_backtest_start_logging_event(self):  

        main.TradingEngine.backtest_start_logging_event(self.state)

        row = self.state.list_dictionaries_event_logs[0]

        self.assertEqual( row['run_number'], 1 )
        self.assertTrue( math.isnan(row['day']) )
        self.assertEqual( row['date'], None )
        self.assertEqual( row['ticker'] , 'Google' )
        self.assertEqual( row['strategy'], 'Mean Reversion' )
        self.assertEqual( row['event_type'], "BACKTEST_START" )
        self.assertEqual( row['message'], "Backtest started" )
        self.assertEqual( row['cash'], 10000 )
        self.assertEqual( row['equity'], 10000 )
        self.assertEqual( row['position'], 0 )
        self.assertEqual( row['execution_price'], None)
        self.assertEqual( row['pnl'], None)
        self.assertEqual( row['labels'], None)

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1)

    def test_buy_executed_log_event(self):

        day = 4
        my_date = date(2025, 1, 12)
        self.state.cashValue = 8900.0
        self.state.equity = 8967.0
        self.state.positionMeanReversion = 8
        self.state.entryPriceMeanReversion = 321.0

        main.TradingEngine.buy_executed_log_event(self.state , day , my_date )

        row = self.state.list_dictionaries_event_logs[0]

        
        self.assertEqual( row['run_number'], 1 )
        self.assertEqual( row['day'] , day )
        self.assertEqual( row['date'], my_date )
        self.assertEqual( row['ticker'] , 'Google' )
        self.assertEqual( row['strategy'], 'Mean Reversion' )
        self.assertEqual( row['event_type'], "BUY_EXECUTED" )
        self.assertEqual( row['message'], "A Buy has been executed" )
        self.assertEqual( row['cash'], self.state.cashValue )
        self.assertEqual( row['equity'], self.state.equity )
        self.assertEqual( row['position'], self.state.positionMeanReversion )
        self.assertEqual( row['execution_price'], self.state.entryPriceMeanReversion )
        self.assertEqual( row['pnl'], None )
        self.assertEqual( row['labels'], 'Google-Mean Reversion' )  

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1)

    def test_sell_executed_log_event(self):

        day = 5
        my_date = date ( 2024 , 8 , 25 )
        self.state.cashValue = 8700.0
        self.state.equity = 8957.0
        self.state.positionMeanReversion = 2
        self.state.exitPriceMeanReversion = 345.95
        self.state.profitMeanReversion = 123.654

        main.TradingEngine.sell_executed_log_event(self.state, day , my_date)

        row = self.state.list_dictionaries_event_logs[0]

        self.assertEqual( row['run_number'], 1 )
        self.assertEqual( row['day'] , day )
        self.assertEqual( row['date'], my_date )
        self.assertEqual( row['ticker'] , 'Google' )
        self.assertEqual( row['strategy'], 'Mean Reversion' )
        self.assertEqual( row['event_type'], "SELL_EXECUTED" )
        self.assertEqual( row['message'], "A Sell has been executed" )
        self.assertEqual( row['cash'], self.state.cashValue )
        self.assertEqual( row['equity'], self.state.equity )
        self.assertEqual( row['position'], self.state.positionMeanReversion )
        self.assertEqual( row['execution_price'], self.state.exitPriceMeanReversion )
        self.assertEqual( row['pnl'], self.state.profitMeanReversion )
        self.assertEqual( row['labels'], 'Google-Mean Reversion' )

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1 )

    def test_trade_closed_log_event(self):
    
        day = 21
        my_date = date( 2024 , 9 , 23 )
        self.state.cashValue = 9814.12
        self.state.equity = 9910.645
        self.state.positionMeanReversion = 14
        self.state.exitPriceMeanReversion = 510.54
        self.state.profitMeanReversion = 132.6546

        main.TradingEngine.trade_closed_log_event(self.state, day, my_date)

        row = self.state.list_dictionaries_event_logs[0]

        self.assertEqual( row['run_number'], 1 )
        self.assertEqual( row['day'] , day )
        self.assertEqual( row['date'], my_date )
        self.assertEqual( row['ticker'] , 'Google' )
        self.assertEqual( row['strategy'], 'Mean Reversion' )
        self.assertEqual( row['event_type'], "TRADE_CLOSED" )
        self.assertEqual( row['message'], "A Trade has been executed" )
        self.assertEqual( row['cash'], self.state.cashValue )
        self.assertEqual( row['equity'], self.state.equity )
        self.assertEqual( row['position'], self.state.positionMeanReversion )
        self.assertEqual( row['execution_price'], self.state.exitPriceMeanReversion )
        self.assertEqual( row['pnl'], self.state.profitMeanReversion )
        self.assertEqual( row['labels'], 'Google-Mean Reversion' )

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1 )

    def test_backtest_end_logging_event(self):
    
        day = 14
        my_date = date ( 2028 , 5 , 21 )
        self.state.cashValue = 8694.234
        self.state.equity = 9234.123
        self.state.positionMeanReversion = 21
        self.state.totalProfit = 210.764

        main.TradingEngine.backtest_end_logging_event(self.state, day, my_date)

        row = self.state.list_dictionaries_event_logs[0]

        self.assertEqual( row['run_number'], 1 )
        self.assertEqual( row['day'] , day )
        self.assertEqual( row['date'], my_date )
        self.assertEqual( row['ticker'] , 'Google' )
        self.assertEqual( row['strategy'], 'Mean Reversion' )
        self.assertEqual( row['event_type'], "BACKTEST_END" )
        self.assertEqual( row['message'], "Backtest has ended" )
        self.assertEqual( row['cash'], self.state.cashValue )
        self.assertEqual( row['equity'], self.state.equity )
        self.assertEqual( row['position'], self.state.positionMeanReversion )
        self.assertEqual( row['execution_price'], None )
        self.assertEqual( row['pnl'], self.state.totalProfit )
        self.assertEqual( row['labels'], None )

        self.assertEqual( len(self.state.list_dictionaries_event_logs), 1 )


class TestBuildingDictionaries(TestCase):

    def test_build_dictionary_prices(self):

        state = main.ExecutionState(
                        
            trendMethod = False, 
            symbol = 'GOOGL', 
            cashValue = 10000 , 
            ticker_name = 'Google'

        )

        day = 5
        my_date = date(2024 ,12, 1)
        closingPrice = 345.12
        average = 432.1

        main.TradingEngine.build_dictionary_prices(
                                                        state, 
                                                        day, 
                                                        my_date, 
                                                        closingPrice, 
                                                        average 
                                                    )

        row = state.list_dictionaries_prices[0]

        self.assertEqual( row['day'], day )
        self.assertEqual( row['date'], my_date )
        self.assertEqual( row['ticker'], 'Google' )
        self.assertEqual( row['strategy'], 'Mean Reversion' )
        self.assertEqual( row['closing_price'], closingPrice )
        self.assertEqual( row['average'], average )

        self.assertEqual( len(state.list_dictionaries_prices), 1 )

    def test_build_dictionary_trades(self):

        state_trend = main.ExecutionState(
                                
                    trendMethod = True, 
                    symbol = 'GOOGL', 
                    cashValue = 10000 , 
                    ticker_name = 'Google'
        
                )

        state_mean_reversion = main.ExecutionState(
                                        
                    trendMethod = False, 
                    symbol = 'GOOGL', 
                    cashValue = 10000 , 
                    ticker_name = 'Google'
                
                )
        
        state_trend.entry_day = 54
        state_trend.entryPriceTrend = round (345.6 , 3)
        state_trend.exit_day = 65
        state_trend.exitPriceTrend = round( 543.0 , 3)
        state_trend.profitTrend = round( 123.6 , 3)
        state_trend.return_pct = round( ( (state_trend.exitPriceTrend-state_trend.entryPriceTrend) / state_trend.entryPriceTrend ) * 100 , 2 )

        state_mean_reversion.entry_day = 34
        state_mean_reversion.exit_day = 354
        state_mean_reversion.entryPriceMeanReversion = 534.6
        state_mean_reversion.exitPriceMeanReversion = 432.6
        state_mean_reversion.profitMeanReversion = -432.4
        state_mean_reversion.return_pct = round( ( (state_mean_reversion.exitPriceMeanReversion - state_mean_reversion.entryPriceMeanReversion ) / state_mean_reversion.entryPriceMeanReversion ) * 100 , 2 )
        
        
        main.TradingEngine.build_dictionary_trades( state_trend )     

        row = state_trend.list_dictionaries_completed_trades[0]

        self.assertEqual( row['run_number'], 1 )
        self.assertEqual( row['ticker'], 'Google' )
        self.assertEqual( row['strategy'], 'Trend' )
        self.assertEqual( row['entry_day'], state_trend.entry_day )
        self.assertEqual( row['entry_price'], state_trend.entryPriceTrend )
        self.assertEqual( row['exit_day'], state_trend.exit_day )
        self.assertEqual( row['exit_price'], state_trend.exitPriceTrend )
        self.assertEqual( row['profit'], state_trend.profitTrend )
        self.assertEqual( row['return_pct'], state_trend.return_pct )
        self.assertEqual( row['labels'], 'Google-Trend' )

        self.assertEqual( len(state_trend.list_dictionaries_completed_trades) , 1 )

        main.TradingEngine.build_dictionary_trades( state_mean_reversion )     
        
        row = state_mean_reversion.list_dictionaries_completed_trades[0]

        self.assertEqual( row['run_number'], 1 )
        self.assertEqual( row['ticker'], 'Google' )
        self.assertEqual( row['strategy'], 'Mean Reversion' )
        self.assertEqual( row['entry_day'], state_mean_reversion.entry_day )
        self.assertEqual( row['entry_price'], state_mean_reversion.entryPriceMeanReversion )
        self.assertEqual( row['exit_day'], state_mean_reversion.exit_day )
        self.assertEqual( row['exit_price'], state_mean_reversion.exitPriceMeanReversion )
        self.assertEqual( row['profit'], state_mean_reversion.profitMeanReversion )
        self.assertEqual( row['return_pct'], state_mean_reversion.return_pct )
        self.assertEqual( row['labels'], 'Google-Mean Reversion' )

        self.assertEqual( len(state_mean_reversion.list_dictionaries_completed_trades) , 1 )



class TestExternalFunctions(TestCase):

    def test_generator(self):
        """ 
        After creating an ExecutionState object, it patches main's dl with a MagicMock object, 
        and manually hard codes read_ticker_dataframe's return value.
        It then calls the real TradingEngine.generator() and asserts its result 
        against the magic mock's return value.
        It also asserts that the magic mock has been called exactly once with the specified parameters.
        The autospec parameter checks that the mock respects the original function's signature, 
        so that the mock would reject calls that the real function would also reject.
        """

        state = main.ExecutionState(

            trendMethod=True,
            symbol='AAPL',
            cashValue= 10000,
            ticker_name = 'Apple'

        )

        with patch.object( main , 'dl' , autospec = True) as mock_dl:

            mock_dl.read_ticker_dataframe.return_value = [ 

                                                        (1, date(2024, 1, 16), 185.92, None, None) , 
                                                        (2, date(2024, 1, 17), 185.64, None, None) , 
                                                        (3, date(2024, 1, 18), 188.63, np.float64(185.77999999999997), 185.59), 
                                                        (4, date(2024, 1, 19), 187.68, np.float64(186.73), 189.33), 
                                                        (5, date(2024, 1, 22), 191.56, np.float64(186.96749999999997), 188.04) 

                                                            ]

            one_df = pd.DataFrame(
                {
                "open":  [186.06, 187.15, 185.59, 189.33, 188.04],
                "close": [185.92, 185.64, 188.63, 187.68, 191.56],
                } ,
                index=pd.to_datetime(
                    ["2024-01-16", "2024-01-17", "2024-01-18", "2024-01-19", "2024-01-22"]
                ) ,
            )

            generator = main.TradingEngine.generator(state , one_df )
            generator_list = [
                tupl for tupl in generator
            ]

            self.assertEqual( 

                mock_dl.read_ticker_dataframe.return_value, generator_list

            )

            mock_dl.read_ticker_dataframe.assert_called_once_with(one_df, state.cashValue, state.verbose_run)

    def test_process_one_day(self):

        state = main.ExecutionState(
        
                trendMethod=False,
                symbol='MSFT',
                cashValue= 10000,
                ticker_name = 'Microsoft'
        
                )

        day = 20
        my_date = date(2025 , 5 , 8)
        closingPrice = 435.143
        average = 444.4
        nextDayOpeningPrice = 473.76

        with patch.object( main , 'process_1_day' , autospec = True ) as mock_one_day:

            mock_one_day.process_one_day.return_value = (

                5,
                341.5,
                450.1,
                420.7,
                8930.0,
                9100.5,
                'BUY',
                341,
                400

            )

            tuple_results = main.TradingEngine.process_one_day(

                state,
                day,
                my_date,
                closingPrice, 
                average,
                nextDayOpeningPrice

            )

            self.assertEqual( 

                mock_one_day.process_one_day.return_value , tuple_results

            )

            mock_one_day.process_one_day.assert_called_once_with(

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

    def test_update_portfolio_state(self):

        state = main.ExecutionState(
        
            trendMethod=True,
            symbol='MSFT',
            cashValue= 10000,
            ticker_name = 'Microsoft'

        )

        day = 214
        my_date = date( 2026 , 4 , 29 )
        closingPrice = 543.123
        average = 567.1
        nextDayOpeningPrice = 532.6

        with patch( 'main.TradingEngine.process_one_day' , autospec = True ) as mock : 

            mock.return_value = (

                20,
                235.6,
                396.78,
                399.65,
                9817.432,
                9999.11,
                'SELL',
                235,
                299

            )

            ( mock_positionTrend, 
            mock_profitTrend, 
            mock_entryPriceTrend, 
            mock_exitPriceTrend, 
            mock_cashValue, 
            mock_equity, 
            mock_pending_action, 
            mock_entry_day, 
            mock_exit_day ) = mock.return_value

            main.TradingEngine.update_portfolio_state(

                state,
                day,
                my_date,
                closingPrice,
                average,
                nextDayOpeningPrice

            )

            self.assertEqual( mock_positionTrend , state.positionTrend )
            self.assertEqual( mock_profitTrend , state.profitTrend )
            self.assertEqual( mock_entryPriceTrend , state.entryPriceTrend )
            self.assertEqual( mock_exitPriceTrend , state.exitPriceTrend )
            self.assertEqual( mock_cashValue , state.cashValue )
            self.assertEqual( mock_equity , state.equity ) 
            self.assertEqual( mock_pending_action , state.pending_action )
            self.assertEqual( mock_entry_day , state.entry_day )
            self.assertEqual( mock_exit_day , state.exit_day )

            mock.assert_called_once_with(

                state, 
                day, 
                my_date, 
                closingPrice, 
                average, 
                nextDayOpeningPrice

            )

        state = main.ExecutionState(
                
                    trendMethod=False,
                    symbol='MSFT',
                    cashValue= 10000,
                    ticker_name = 'Microsoft'
        
                )
        
        day = 215
        my_date = date( 2025 , 5 , 19 )
        closingPrice = 523.123
        average = 587.1
        nextDayOpeningPrice = 592.6 

        with patch( 'main.TradingEngine.process_one_day' , autospec = True ) as mock : 
        
            mock.return_value = (

                25,
                215.6,
                496.78,
                499.65,
                7817.432,
                5999.11,
                'BUY',
                335,
                199

            )

            ( mock_positionMeanReversion, 
            mock_profitMeanReversion, 
            mock_entryPriceMeanReversion, 
            mock_exitPriceMeanReversion, 
            mock_cashValue, 
            mock_equity, 
            mock_pending_action, 
            mock_entry_day, 
            mock_exit_day ) = mock.return_value

            main.TradingEngine.update_portfolio_state(

                state,
                day,
                my_date,
                closingPrice,
                average,
                nextDayOpeningPrice

            )

            self.assertEqual( mock_positionMeanReversion , state.positionMeanReversion )
            self.assertEqual( mock_profitMeanReversion , state.profitMeanReversion )
            self.assertEqual( mock_entryPriceMeanReversion , state.entryPriceMeanReversion )
            self.assertEqual( mock_exitPriceMeanReversion , state.exitPriceMeanReversion )
            self.assertEqual( mock_cashValue , state.cashValue )
            self.assertEqual( mock_equity , state.equity ) 
            self.assertEqual( mock_pending_action , state.pending_action )
            self.assertEqual( mock_entry_day , state.entry_day )
            self.assertEqual( mock_exit_day , state.exit_day )

            mock.assert_called_once_with(

                state, 
                day, 
                my_date, 
                closingPrice, 
                average, 
                nextDayOpeningPrice

            )   


class TestRunStrategy(TestCase):

    def test_run_strategy_day(self):
        """
        Tests the 4 possible cases that can happen inside run_strategy_day():

            1. BUY only          — position went from 0 to something, no profit change yet
            2. SELL with +P&L    — position went back to 0, profit went up
            3. SELL with -P&L     — position went back to 0, profit went down
            4. Nothing happened  — no position change, no profit change

        Testing run_strategy_day() means testing its logic — what it decides to do
        and which branch it goes down — not what values it returns, because it
        doesn't return anything, it just calls other helpers I've already tested
        separately.

        So for each case I patch process_one_day() and hard code the position and
        profit it hands back, which is what decides the branch. Then I patch the
        helpers that each branch calls, and assert which ones fired and which ones
        didn't.

        Realised P&L only exists once the position closes, which is why BUY and
        SELL can never happen on the same day.
        """

        # BUY Only Case 
        
        state = main.ExecutionState(
                
                trendMethod=True,
                symbol='GOOGL',
                cashValue= 10000,
                ticker_name = 'Google'
        
                )

        day = 10
        my_date =date(2024,5,12)
        closingPrice = 423.6
        average = 543.6
        nextDayOpeningPrice = 541.312

        with (

            patch.object(main.TradingEngine, 'process_one_day') as mock_1_day ,
            patch.object(main.TradingEngine, 'buy_executed_log_event' , autospec = True) as mock_buy ,
            patch.object(main.TradingEngine, 'sell_executed_log_event' ) as mock_sell 

        ) :
                    
            mock_1_day.return_value = (
                10, #state.positionTrend
                0, #state.profitTrend
                232.65, 
                222.5, 
                9235.6, 
                9666.2, 
                '', 
                234, 
                464
            )

            main.TradingEngine.run_strategy_day(state,
                                day, 
                                my_date ,
                                closingPrice, 
                                average ,
                                nextDayOpeningPrice)

            mock_buy.assert_called_once_with(state, day, my_date)
            mock_sell.assert_not_called()
            assert len(state.listStoreEquityValues) == 1

        # SELL With Positive Profit Case

        state = main.ExecutionState(
                        
                        trendMethod=True,
                        symbol='GOOGL',
                        cashValue= 10000,
                        ticker_name = 'Google'
                
                        )

        day = 10
        my_date =date(2024,5,12)
        closingPrice = 423.6
        average = 543.6
        nextDayOpeningPrice = 541.312

        state.positionTrend = 35 # previous position

        with (

            patch.object( main.TradingEngine , 'process_one_day') as mock_1_day ,
            patch.object( main.TradingEngine , 'sell_executed_log_event' ) as mock_sell ,
            patch.object( main.TradingEngine , 'trade_closed_log_event' ) as mock_trade ,
            patch.object( main.TradingEngine , 'buy_executed_log_event') as mock_buy ,
            patch.object( main.TradingEngine , 'increment_positive_profit' ) as mock_increment_positive_profit ,
            patch.object(main.TradingEngine , 'increment_total_profit_positive_trades') as mock_increment_total_profit_positive_trades ,
            patch.object(main.TradingEngine , 'increment_negative_profit') as mock_increment_negative_profit ,
            patch.object(main.TradingEngine , 'increment_total_profit_negative_trades') as mock_increment_total_profit_negative_trades 

        ) :

            mock_1_day.return_value = (

                0, #state.positionTrend
                234.564, #state.profitTrend
                354.8, 
                254.7, 
                10234.6, 
                12445.7, 
                'BUY', 
                65, 
                67

            )

            main.TradingEngine.run_strategy_day(

                state,
                day,
                my_date,
                closingPrice,
                average,
                nextDayOpeningPrice

            )

            # this asserts that SELL case with a positive P&L was invoked
            mock_increment_positive_profit.assert_called_once_with(state)
            mock_increment_total_profit_positive_trades.assert_called_once_with(state)
            mock_increment_negative_profit.assert_not_called()
            mock_increment_total_profit_negative_trades.assert_not_called()

            # this asserts that SELL case was invoked 
            mock_sell.assert_called_once_with(state, day, my_date)
            mock_trade.assert_called_once_with(state, day, my_date)
            mock_buy.assert_not_called()
            self.assertTrue ( len(state.listStoreEquityValues) == 1 )

        # SELL With Negative Profit Case
        
        state = main.ExecutionState(
                        
                        trendMethod=True,
                        symbol='GOOGL',
                        cashValue= 10000,
                        ticker_name = 'Google'
                
                        )

        day = 10
        my_date =date(2024,5,12)
        closingPrice = 423.6
        average = 543.6
        nextDayOpeningPrice = 541.312

        state.positionTrend = 38 # previous position

        with (

            patch.object( main.TradingEngine , 'process_one_day') as mock_1_day ,
            patch.object( main.TradingEngine , 'sell_executed_log_event' ) as mock_sell ,
            patch.object( main.TradingEngine , 'trade_closed_log_event' ) as mock_trade ,
            patch.object( main.TradingEngine , 'buy_executed_log_event') as mock_buy ,
            patch.object( main.TradingEngine , 'increment_negative_profit' ) as mock_increment_negative_profit ,
            patch.object(main.TradingEngine , 'increment_total_profit_negative_trades') as mock_increment_total_profit_negative_trades ,
            patch.object(main.TradingEngine , 'increment_positive_profit') as mock_increment_positive_profit ,
            patch.object(main.TradingEngine , 'increment_total_profit_positive_trades') as mock_increment_total_profit_positive_trades 

        ) :

            mock_1_day.return_value = (

                0, #state.positionTrend
                -412.564, #state.profitTrend
                354.8, 
                254.7, 
                10234.6, 
                12445.7, 
                'BUY', 
                65, 
                67

            )

            main.TradingEngine.run_strategy_day(

                state,
                day,
                my_date,
                closingPrice,
                average,
                nextDayOpeningPrice

            )

            # this asserts that SELL case with a negative P&L was invoked
            mock_increment_negative_profit.assert_called_once_with(state)
            mock_increment_total_profit_negative_trades.assert_called_once_with(state)
            mock_increment_positive_profit.assert_not_called()
            mock_increment_total_profit_positive_trades.assert_not_called()

            # this asserts that SELL case was invoked 
            mock_sell.assert_called_once_with(state, day, my_date)
            mock_trade.assert_called_once_with(state, day, my_date)
            mock_buy.assert_not_called()
            self.assertTrue ( len(state.listStoreEquityValues) == 1 )

        # Nothing has happened case 

        state = main.ExecutionState(
                        
                        trendMethod=True,
                        symbol='GOOGL',
                        cashValue= 10000,
                        ticker_name = 'Google'
                
                        )

        day = 10
        my_date =date(2024,5,12)
        closingPrice = 423.6
        average = 543.6
        nextDayOpeningPrice = 541.312

        with ( 

            patch.object(main.TradingEngine , 'process_one_day') as mock_1_day,
            patch.object(main.TradingEngine , 'buy_executed_log_event') as mock_buy , 
            patch.object(main.TradingEngine , 'sell_executed_log_event') as mock_sell , 
            patch.object(main.TradingEngine , 'trade_closed_log_event') as mock_trade

        ) :

            mock_1_day.return_value = ( 0, #state.positionTrend 
                                        0, #state.profitTrend
                                        state.entryPriceTrend, 
                                        state.exitPriceTrend, 
                                        state.cashValue, 
                                        state.equity, 
                                        state.pending_action, 
                                        state.entry_day, 
                                        state.exit_day )

            main.TradingEngine.run_strategy_day(

                state,
                day,
                my_date,
                closingPrice,
                average ,
                nextDayOpeningPrice

            )

            mock_buy.assert_not_called()
            mock_sell.assert_not_called()
            mock_trade.assert_not_called()
            self.assertTrue( len(state.listStoreEquityValues) == 1 )


    def test_run_days_one_and_two(self):

        state = main.ExecutionState(
                        
            trendMethod=True,
            symbol='GOOGL',
            cashValue= 10000,
            ticker_name = 'Google'

        )
        
        day = 10
        my_date =date(2024,5,12)
        closingPrice = 423.6

        with patch('main.TradingEngine.build_dictionary_prices') as mock_dict :

            main.TradingEngine.run_days_one_and_two(

                state,
                day,
                my_date,
                closingPrice

            )

            self.assertTrue( len(state.listStoreEquityValues) ==1 )
            mock_dict.assert_called_once_with(  state, 
                                                day, 
                                                my_date,
                                                closingPrice,
                                                None )






# The rest of the tests following up are written with Pytest , and not Unittest anymore.
# This is solely for educational and learning purposes 



class TestBuildDataFrames:

    def test_build_prices_data_frame(self , state):

        expected = pd.DataFrame({
                'day': [1, 2, 3],
                'date': [date(2024,1,1), date(2024,1,2), date(2024,1,3)],
                'ticker': ['Google', 'Google', 'Google'],
                'strategy': ['Trend', 'Trend', 'Trend'],
                'closing_price': [101.18, 106.40, 101.43],
                'average': [float('nan'), float('nan'), 103.0],
            })

        pd.testing.assert_frame_equal( main.TradingEngine.build_prices_data_frame(state) , expected )

    def test_build_log_events_data_frame(self , state ) :

        expected = pd.DataFrame( {

            'day' : [56,57,58] , 
            'date' : [ date(2025,3,25) , date(2025,3,26) , date(2025,3,27) ] ,
            'ticker' : [ 'Google' , 'Google' , 'Google' ] , 
            'strategy' : ['Trend' , 'Trend' , 'Trend'] ,
            'closing_price' : [234.18 , 267.40 , 262.65] , 
            'average' : [254.65 , 236.12 , 298.00]

        })

        expected['day'] = expected['day'].astype(pd.Int64Dtype())

        pd.testing.assert_frame_equal( main.TradingEngine.build_log_events_data_frame(state) , expected )

    def test_build_trades_data_frame( self , state):

        expected = pd.DataFrame({
            'run_number': [1, 1],
            'ticker': ['Google', 'Google'],
            'strategy': ['Trend', 'Trend'],
            'entry_day': [12, 31],
            'entry_price': [98.400, 110.050],
            'exit_day': [19, 38],
            'exit_price': [105.720, 103.900],
            'profit': [73.200, -61.500],
            'return_pct': [7.44, -5.59],
            'labels': ['Google-Trend', 'Google-Trend'],
            'number_trades_took_place': [1, 2],
        })

        pd.testing.assert_frame_equal( main.TradingEngine.build_trades_data_frame(state) , expected )

        state.list_dictionaries_completed_trades = []

        expected = pd.DataFrame(columns=[
            'run_number', 'ticker', 'strategy', 'entry_day', 'entry_price',
            'exit_day', 'exit_price', 'profit', 'return_pct', 'labels',
            'number_trades_took_place',
        ])

        pd.testing.assert_frame_equal( main.TradingEngine.build_trades_data_frame(state) , expected )
        
    def test_build_drawdown_series_data_frame(self, state):

        expected = pd.DataFrame({
            'day': [1, 2, 3, 4, 5, 6, 7, 8],
            'run_number': [0, 0, 0, 0, 0, 0, 0, 0],
            'ticker': ['Google'] * 8,
            'strategy': ['Trend'] * 8,
            'equity': [10000.0, 10240.5, 10105.2, 9870.8, 10310.4, 10520.9, 10180.3, 9950.6],
            'peak_so_far': [10000.0, 10240.5, 10240.5, 10240.5, 10310.4, 10520.9, 10520.9, 10520.9],
            'drawdown': [0.0, 0.0, -135.3, -369.7, 0.0, 0.0, -340.6, -570.3],
            'drawdown_pct': [0.00, 0.00, -1.32, -3.61, 0.00, 0.00, -3.24, -5.42],
            'labels': ['Google-Trend'] * 8,
        })

        pd.testing.assert_frame_equal( main.TradingEngine.build_drawdown_series_data_frame(state) , expected )

    def test_build_equity_curve_data_frame(self , state ) :

        expected = pd.DataFrame({
            'day': [1, 2, 3, 4, 5, 6, 7, 8],
            'run_number': [0, 0, 0, 0, 0, 0, 0, 0],
            'ticker': ['Google'] * 8,
            'strategy': ['Trend'] * 8,
            'equity': [10000.0, 10240.5, 10105.2, 9870.8, 10310.4, 10520.9, 10180.3, 9950.6],
            'labels': ['Google-Trend'] * 8,
        }) 

        pd.testing.assert_frame_equal( main.TradingEngine.build_equity_curve_data_frame(state) , expected )        



class TestBacktestRun:

    def test_backtest_run(self, state_backtest_run ):

        one_df = pd.DataFrame({

            'close':  [101.20, 103.10, 102.40, 103.90, 105.60, 107.00],
            'high':   [102.40, 103.80, 104.90, 104.00, 106.10, 107.50],
            'low':    [ 99.10, 100.70, 101.80, 100.90, 103.40, 105.20],
            'open':   [100.00, 101.50, 103.20, 102.10, 104.80, 106.30],
            'volume': [  2100,   2450,   1980,   2600,   3010,   2780],
        }, index=pd.to_datetime([
            '2024-01-16 09:30:00', '2024-01-17 09:30:00', '2024-01-18 09:30:00',
            '2024-01-19 09:30:00', '2024-01-22 09:30:00', '2024-01-23 09:30:00',
        ], utc=True).tz_convert('America/New_York'))
        
        one_df.index.name = 'time'

        expected_log_events_df = pd.DataFrame({

            'run_number': [1, 1, 1],
            'day': pd.array([None, 4, 6], dtype=pd.Int64Dtype()),
            'date': [None, date(2024,1,19), date(2024,1,23)],
            'ticker': ['Google', 'Google', 'Google'],
            'strategy': ['Trend', 'Trend', 'Trend'],
            'event_type': ['BACKTEST_START', 'BUY_EXECUTED', 'BACKTEST_END'],
            'message': ['Backtest started', 'A Buy has been executed', 'Backtest has ended'],
            'cash': [10000.000, 8059.036, 8059.036],
            'equity': [10000.000, 10033.136, 10092.036],
            'position': [0.0, 19.0, 19.0],
            'execution_price': [float('nan'), 102.151, float('nan')],
            'pnl': [float('nan'), float('nan'), 0.0],
            'labels': [None, 'Google-Trend', None],
            
        }) 

        expected_equity_curve_df = pd.DataFrame({

            'day': [1, 2, 3, 4, 5, 6],
            'run_number': [1, 1, 1, 1, 1, 1],
            'ticker': ['Google'] * 6,
            'strategy': ['Trend'] * 6,
            'equity': [10000.000, 10000.000, 10000.000, 10033.136, 10065.436, 10092.036],
            'labels': ['Google-Trend'] * 6,
            
        })

        expected_drawdown_series_df = pd.DataFrame({

            'day': [1, 2, 3, 4, 5, 6],
            'run_number': [1, 1, 1, 1, 1, 1],
            'ticker': ['Google'] * 6,
            'strategy': ['Trend'] * 6,
            'equity': [10000.000, 10000.000, 10000.000, 10033.136, 10065.436, 10092.036],
            'peak_so_far': [10000.000, 10000.000, 10000.000, 10033.136, 10065.436, 10092.036],
            'drawdown': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'drawdown_pct': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'labels': ['Google-Trend'] * 6,
            
        })

        expected_trades_df = pd.DataFrame(

            columns = [ 'run_number' , 'ticker' , 'strategy' , 'entry_day' ,
                       'entry_price' , 'exit_day' , 'exit_price' , 'profit' ,
                        'return_pct' , 'labels' , 'number_trades_took_place' ]

        )

        expected_prices_df = pd.DataFrame({

            'day': [1, 2, 3, 4, 5, 6],
            'date': [date(2024,1,16), date(2024,1,17), date(2024,1,18),
                    date(2024,1,19), date(2024,1,22), date(2024,1,23)],
            'ticker': ['Google'] * 6,
            'strategy': ['Trend'] * 6,
            'closing_price': [101.2, 103.1, 102.4, 103.9, 105.6, 107.0],
            'average': [float('nan'), float('nan'), 102.150000, 102.233333, 102.650000, 103.240000],
            
        })

        dict_dfs = main.TradingEngine.backtest_run( state_backtest_run , one_df )

        pd.testing.assert_frame_equal( 

            dict_dfs['log_events'] , expected_log_events_df

        )

        pd.testing.assert_frame_equal( 
        
            dict_dfs['equity_curve'] , expected_equity_curve_df

        )

        pd.testing.assert_frame_equal( 
        
            dict_dfs['drawdown_series'] , expected_drawdown_series_df

        )

        pd.testing.assert_frame_equal( 
        
            dict_dfs['trades'] , expected_trades_df

        )

        pd.testing.assert_frame_equal( 
        
            dict_dfs['prices'] , expected_prices_df

        )



class TestPerformanceMetricsHelpers:

    def test_try_except_performance_metric(self):

        function = lambda *args , **kwargs : 5/0

        assert math.isnan( 

            main.TradingEngine.try_except_performance_metric( function )

        ) == True

        function = lambda *args , **kwargs : 5/5

        assert main.TradingEngine.try_except_performance_metric( function ) == 1

    def test_strategy_performance_metrics_stats(self, state_backtest_run ):

        state_backtest_run.positiveProfitTrend = 523.35
        state_backtest_run.negativeProfitTrend = -234.65
        state_backtest_run.numberTradesTrend = 56
        state_backtest_run.totalProfitPositiveTradesTrend = 600.234
        state_backtest_run.totalProfitNegativeTradesTrend = -534.6

        d = main.TradingEngine.strategy_performance_metrics_stats(state_backtest_run)

        assert d['positive_count'] == state_backtest_run.positiveProfitTrend
        assert d['negative_count'] == state_backtest_run.negativeProfitTrend 
        assert d['trade_count'] == state_backtest_run.numberTradesTrend
        assert d["positive_total"] == state_backtest_run.totalProfitPositiveTradesTrend
        assert d['negative_total'] == state_backtest_run.totalProfitNegativeTradesTrend

        state = main.ExecutionState(
                                
            trendMethod=False,
            symbol='GOOGL',
            cashValue= 10000,
            ticker_name = 'Google'
            
        )

        state.positiveProfitMeanRev = 543.35
        state.negativeProfitMeanRev = -274.65
        state.numberTradesMeanRev = 59
        state.totalProfitPositiveTradesMeanRev = 700.234
        state.totalProfitNegativeTradesMeanRev = -234.6

        d = main.TradingEngine.strategy_performance_metrics_stats(state)
        
        assert d['positive_count'] == state.positiveProfitMeanRev
        assert d['negative_count'] == state.negativeProfitMeanRev
        assert d['trade_count'] == state.numberTradesMeanRev
        assert d["positive_total"] == state.totalProfitPositiveTradesMeanRev
        assert d['negative_total'] == state.totalProfitNegativeTradesMeanRev
        

        
        












class TestTradingEngineBacktestRun(TestCase):

    def test_golden_master_backtest_run(self):
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

        golden_file_path = Path( 'tests/golden_masters/backtest_run_old_results.txt' )

        experimentRunner = main.ExperimentRunner()
        d = experimentRunner.structured_data_outputs()
        results = "\n".join(f"=== {k} ===\n{v.to_csv(index=False)}" for k, v in d.items())
        
        if not golden_file_path.exists():

            golden_file_path.parent.mkdir( parents = True ,
                                        exist_ok = True )

            golden_file_path.write_text(results)
            return 

        self.assertEqual( results , golden_file_path.read_text() )
        
        