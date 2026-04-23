import main 
import unittest
import pandas as pd
import tempfile
import os 

class backTestRun(unittest.TestCase):
    # testing for the correct returned data frame using TREND method on a temporarily created file 
    def test_correct_data_frame_trend_strategy(self):

        #create temporary 5 row input csv file 
        f=tempfile.NamedTemporaryFile(mode='w', suffix=".csv", delete=False)
        f.write("Date,Open,High,Low,Close,Adj Close,Volume\n")
        f.write("2026-01-01,5,5,5,5,5,1000\n")
        f.write("2026-01-02,6,6,6,6,6,1000\n")
        f.write("2026-01-03,10,10,10,10,10,1000\n")
        f.write("2026-01-04,11,11,11,11,11,1000\n")
        f.write("2026-01-05,6,6,6,6,6,1000\n")
        f.close()

        # create Engine instance based on the temporary file with defined parameters 
        engine_trend_strategy_5_day_input=main.Engine(trendMethod=True, csv_ticker=f.name, cashValue=10000, ticker_name="Test")
        # run the instance so you can obtain the returned data frame 
        engine_trend_strategy_5_day_input_data_frame=engine_trend_strategy_5_day_input.backtest_run()
        # ignore the index inside the data frame 
        engine_trend_strategy_5_day_input_data_frame=engine_trend_strategy_5_day_input_data_frame.reset_index(drop=True)

        # create expected returned data frame 
        d={ "Ticker": "Test",
               "Strategy used": "Trend", 
               "Starting cash": 10000, 
               "total net profit": 0,
               "MDD": 9.07, 
               "Expectancy": float("nan"), 
               "Payoff Ratio": float("nan"), 
               "Profit Factor": float("nan"), 
               "Sharpe Ratio": -0.501 }                         
        expected_data_frame_trend=pd.DataFrame( data=d , index=[0])
        # ignore index to assert data frame values only 
        expected_data_frame_trend=expected_data_frame_trend.reset_index(drop=True)

        # compare Engine instance from backtest_run() with the expected returned data frame 
        pd.testing.assert_frame_equal( expected_data_frame_trend, engine_trend_strategy_5_day_input_data_frame )
        # finally remove the temporarily created file 
        os.remove(f.name)



    # testing for the correct returned data frame using MEAN REVERSION method on a temporarily created file 
    def test_correct_data_frame_mean_rev_strategy(self):

        #create temporary 5 row input csv file 
        f=tempfile.NamedTemporaryFile(mode='w', suffix=".csv", delete=False)
        f.write("Date,Open,High,Low,Close,Adj Close,Volume\n")
        f.write("2026-01-01,5,5,5,5,5,1000\n")
        f.write("2026-01-02,6,6,6,6,6,1000\n")
        f.write("2026-01-03,10,10,10,10,10,1000\n")
        f.write("2026-01-04,11,11,11,11,11,1000\n")
        f.write("2026-01-05,6,6,6,6,6,1000\n")
        f.close()

        # create Engine instance based on the temporary file with defined parameters 
        engine_mean_rev_strategy_5_day_input=main.Engine(trendMethod=False, csv_ticker=f.name, cashValue=10000, ticker_name="Test")
        # run the instance so you can obtain the returned data frame 
        engine_mean_rev_strategy_5_day_input_data_frame=engine_mean_rev_strategy_5_day_input.backtest_run()
        # ignore the index inside the data frame 
        engine_mean_rev_strategy_5_day_input_data_frame=engine_mean_rev_strategy_5_day_input_data_frame.reset_index(drop=True)

        # create expected returned data frame 
        d={    "Ticker": "Test",
               "Strategy used": "Mean reversion", 
               "Starting cash": 10000, 
               "total net profit": 0,
               "MDD": 0.0, 
               "Expectancy": float("nan"), 
               "Payoff Ratio": float("nan"), 
               "Profit Factor": float("nan"), 
               "Sharpe Ratio": float("nan") }                         
        expected_data_frame_mean_rev=pd.DataFrame( data=d , index=[0])
        # ignore index to assert data frame values only 
        expected_data_frame_mean_rev=expected_data_frame_mean_rev.reset_index(drop=True)

        # compare Engine instance from backtest_run() with the expected returned data frame 
        pd.testing.assert_frame_equal( expected_data_frame_mean_rev, engine_mean_rev_strategy_5_day_input_data_frame )
        # finally remove the temporarily created file 
        os.remove(f.name)

        
    # test for reset correctness on running the same Engine instance multiple times 
    def test_reset_correctness_engine_instance(self):
        # create any Engine instance 
        engine=main.Engine(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
        # run the backtest multiple times to check if the values are correctly reset 
        engine_data_frame_run1=engine.backtest_run()
        engine_data_frame_run2=engine.backtest_run()
        # drop index 
        engine_data_frame_run1=engine_data_frame_run1.reset_index(drop=True)
        engine_data_frame_run2=engine_data_frame_run2.reset_index(drop=True)
        # check for reset correctness 
        pd.testing.assert_frame_equal( engine_data_frame_run1, engine_data_frame_run2 )