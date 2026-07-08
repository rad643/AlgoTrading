import main 
import unittest
import pandas as pd
import tempfile
import os 

class TestTradingEnginePerformanceMetrics(unittest.TestCase):

    # testing for the correct returned data frame using TREND method on a temporarily created file 
    def test_correct_data_frame_trend_strategy(self: "TestTradingEnginePerformanceMetrics"):

        # Reset the class-level run counter so this test starts from a known run number (since it's not instance-specific)
        main.ExecutionState.backtest_run_number=0

        try: 
            #create temporary 5 row input csv file 
            f=tempfile.NamedTemporaryFile(mode='w', suffix=".csv", delete=False)
            f.write("Date,Open,High,Low,Close,Adj Close,Volume\n")
            f.write("2026-01-01,5,5,5,5,5,1000\n")
            f.write("2026-01-02,6,6,6,6,6,1000\n")
            f.write("2026-01-03,10,10,10,10,10,1000\n")
            f.write("2026-01-04,11,11,11,11,11,1000\n")
            f.write("2026-01-05,6,6,6,6,6,1000\n")
            f.write("2026-01-06,20,20,20,20,20,1000\n")
            f.write("2026-01-07,20,20,20,20,20,1000\n")
            f.close()

            # create ExecutionState instance to test TradingEngine's performance_metrics_data_frame() method on
            state_trend_5_day_file=main.ExecutionState(trendMethod=True, csv_ticker=f.name, cashValue=10000, ticker_name="Test")
            # performance_metrics_data_frame() requires backtest_run() to be called first to populate listStoreEquityValues with raw daily equity values
            main.TradingEngine.backtest_run(state_trend_5_day_file)
            # compute run data frame for state_trend_5_day_file
            run_data_frame_trend_5_day_file=main.TradingEngine.performance_metrics_data_frame(state_trend_5_day_file)
            # ignore the index inside the run data frame 
            run_data_frame_trend_5_day_file=run_data_frame_trend_5_day_file.reset_index(drop=True)

            # create expected returned data frame 
            d={ "run_number": 1, 
                "ticker": "Test",
                "strategy": "Trend", 
                "starting cash": 10000, 
                "total net profit": 1626.285,
                "mdd": 9.07, 
                "expectancy": float("nan"), 
                "payoff ratio": float("nan"), 
                "profit factor": float("nan"), 
                "sharpe ratio": 0.247,
                "labels": "Test-Trend" }                         
            expected_data_frame=pd.DataFrame( data=d , index=[0])
            # ignore index to assert data frame values only 
            expected_data_frame=expected_data_frame.reset_index(drop=True)

            # compare Engine instance from backtest_run() with the expected returned data frame 
            pd.testing.assert_frame_equal( expected_data_frame, run_data_frame_trend_5_day_file )
        
        finally:
            # finally remove the temporarily created file 
            os.remove(f.name)



    # testing for the correct returned data frame using MEAN REVERSION method on a temporarily created file 
    def test_correct_data_frame_mean_rev_strategy(self: "TestTradingEnginePerformanceMetrics"):

        # Reset the class-level run counter so this test starts from a known run number (since it's not instance-specific)
        main.ExecutionState.backtest_run_number=0

        try:
            #create temporary 5 row input csv file 
            f=tempfile.NamedTemporaryFile(mode='w', suffix=".csv", delete=False)
            f.write("Date,Open,High,Low,Close,Adj Close,Volume\n")
            f.write("2026-01-01,5,5,5,5,5,1000\n")
            f.write("2026-01-02,6,6,6,6,6,1000\n")
            f.write("2026-01-03,10,10,10,10,10,1000\n")
            f.write("2026-01-04,11,11,11,11,11,1000\n")
            f.write("2026-01-05,6,6,6,6,6,1000\n")
            f.write("2026-01-06,20,20,20,20,20,1000\n")
            f.write("2026-01-07,20,20,20,20,20,1000\n")
            f.close()

            # create ExecutionState instance to test TradingEngine's performance_metrics_data_frame() method on
            state_mean_reversion_5_day_file=main.ExecutionState(trendMethod=False, csv_ticker=f.name, cashValue=10000, ticker_name="Test")
            # performance_metrics_data_frame() requires backtest_run() to be called first to populate listStoreEquityValues with raw daily equity values
            main.TradingEngine.backtest_run(state_mean_reversion_5_day_file)
            # compute run data frame for state_mean_reversion_5_day_file
            run_data_frame_mean_reversion_5_day_file=main.TradingEngine.performance_metrics_data_frame(state_mean_reversion_5_day_file)
            # ignore the index inside the run data frame 
            run_data_frame_mean_reversion_5_day_file=run_data_frame_mean_reversion_5_day_file.reset_index(drop=True)

            # create expected returned data frame 
            d={ "run_number": 1,
                "ticker": "Test",
                "strategy": "Mean Reversion", 
                "starting cash": 10000, 
                "total net profit": -1.98,
                "mdd": 0.03, 
                "expectancy": float("nan"), 
                "payoff ratio": float("nan"), 
                "profit factor": 0.0, 
                "sharpe ratio": -0.645,
                "labels": "Test-Mean Reversion" }                         
            expected_data_frame_mean_rev=pd.DataFrame( data=d , index=[0])
            # ignore index to assert data frame values only 
            expected_data_frame_mean_rev=expected_data_frame_mean_rev.reset_index(drop=True)

            # compare Engine instance from backtest_run() with the expected returned data frame 
            pd.testing.assert_frame_equal( expected_data_frame_mean_rev, run_data_frame_mean_reversion_5_day_file )
        
        finally:
            # finally remove the temporarily created file 
            os.remove(f.name)

    
    # test for reset correctness on running the same Engine instance multiple times 
    def test_reset_correctness_engine_instance(self:"TestTradingEnginePerformanceMetrics"):

        # Reset the class-level run counter so this test starts from a known run number (since it's not instance-specific)
        main.ExecutionState.backtest_run_number=0

        # create ExecutionState object 
        state=main.ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")

        # run TradingEngine.backtest_run(state) multiple times on the same 'state' ExecutionState object 
        run1=main.TradingEngine.backtest_run(state)
        # backtest_run_number increments with each call, so reset between runs to keep run_number identical across both
        main.ExecutionState.backtest_run_number=0
        run2=main.TradingEngine.backtest_run(state)

        # check for reset correctness 
        pd.testing.assert_frame_equal( run1["log_events"], run2["log_events"] )
        pd.testing.assert_frame_equal(run1["equity_curve"], run2["equity_curve"])
        pd.testing.assert_frame_equal(run1["drawdown_series"], run2["drawdown_series"])
        pd.testing.assert_frame_equal(run1["trades"], run2["trades"])
        pd.testing.assert_frame_equal(run1["prices"], run2["prices"])



class TestTradingEngineBacktestRun(unittest.TestCase):

    def setUp(self):
        # Reset the class-level run counter so this test starts from a known run number (since it's not instance-specific)
        main.ExecutionState.backtest_run_number=0

    def test_returned_dictionary(self: "TestTradingEngineBacktestRun"):
        """Test that TradingEngine.backtest_run() returns a dictionary.

        Args:
            self (TestTradingEngineBacktestRun):  Current unittest test case instance.
        """
        # create the object and then run backtest_run on it to generate the returned dictionary
        state=main.ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
        output=main.TradingEngine.backtest_run(state)

        self.assertIsInstance(output,dict)

    def test_expected_keys(self: "TestTradingEngineBacktestRun"):
        """Test that backtest_run() returns all expected output dictionary keys.

        Args:
            self (TestTradingEngineBacktestRun):  Current unittest test case instance.
        """
        # create the object and then run backtest_run on it to generate the returned dictionary
        state=main.ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
        output=main.TradingEngine.backtest_run(state)

        expected_keys=["log_events", "equity_curve", "drawdown_series", "trades","prices"]

        self.assertEqual( expected_keys, list(output.keys()) )

    def test_dictionary_values_types(self: "TestTradingEngineBacktestRun"):
        """Check each returned dictionary value is a pd.DataFrame type

        Args:
            self (TestTradingEngineBacktestRun): Current unittest test case instance.
        """
        # create the object and then run backtest_run on it to generate the returned dictionary
        state=main.ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
        output=main.TradingEngine.backtest_run(state)

        self.assertIsInstance( output["log_events"], pd.DataFrame ) 
        self.assertIsInstance( output["equity_curve"], pd.DataFrame )
        self.assertIsInstance( output["drawdown_series"], pd.DataFrame )
        self.assertIsInstance( output["trades"], pd.DataFrame )
        self.assertIsInstance( output["prices"], pd.DataFrame )

    def test_expected_columns_per_data_frame(self: "TestTradingEngineBacktestRun"):
        """Tests that the column labels for each of the 5 returned data frames correspond to the output  

        Args:
            self (TestTradingEngineBacktestRun): Current unittest test case instance.
        """
        # create the object and then run backtest_run on it to generate the returned dictionary
        state=main.ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
        output=main.TradingEngine.backtest_run(state)

        # put all of the expected column labels of each of the 5 data frames from the returned dictionary object into a list 
        expected_columns_log_events_df=["run_number", "day", "date", "ticker", "strategy", "event_type", "message", 
                          "cash", "equity", "position", "execution_price", "pnl", "labels"]
        expected_columns_equity_curve_df=["day", "run_number", "ticker", "strategy", "equity","labels"]
        expected_columns_drawdown_series_df=["day","run_number", "ticker", "strategy", "equity", 
                                             "peak_so_far", "drawdown", "drawdown_pct", "labels"]
        expected_columns_trades_df=["run_number", "ticker", "strategy", "entry_day", "entry_price",
                                    "exit_day", "exit_price", "profit", "return_pct",
                                    "labels", "number_trades_took_place"]                     
        expected_columns_prices_df=["day", "date", "ticker", "strategy", "closing price", "average"]

        self.assertEqual( list(output["log_events"].columns), expected_columns_log_events_df )
        self.assertEqual( list(output["equity_curve"].columns), expected_columns_equity_curve_df )
        self.assertEqual( list(output["drawdown_series"].columns), expected_columns_drawdown_series_df)
        self.assertEqual( list(output["trades"].columns), expected_columns_trades_df)
        self.assertEqual( list(output["prices"].columns), expected_columns_prices_df)

    def test_empty_data_frames(self: "TestTradingEngineBacktestRun"):
        """ tests if any of the 5 data frames is empty (any of the axes are of length 0)

        Args:
            self (TestTradingEngineBacktestRun): Current unittest test case instance.
        """
        # create the object and then run backtest_run on it to generate the returned dictionary
        state=main.ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
        output=main.TradingEngine.backtest_run(state)

        self.assertTrue(output["log_events"].empty==False)
        self.assertTrue(output["equity_curve"].empty==False)
        self.assertTrue(output["drawdown_series"].empty==False)
        self.assertTrue(output["trades"].empty==False)
        self.assertTrue(output["prices"].empty==False)




class TestExperimentRunner(unittest.TestCase):

    def setUp(self):
        # Reset the class-level run counter so this test starts from a known run number (since it's not instance-specific)
        main.ExecutionState.backtest_run_number=0
    
    def test_returned_dictionary(self: "TestExperimentRunner"):
        """Test that ExperimentRunner.structured_data_outputs() returns a dictionary.

        Args:
            self (TestExperimentRunner):  Current unittest test case instance.
        """
        # construct the ExperimentRunner instance and call structured_data_outputs() on it to compute the dictionary containing the data frames 
        experimentRunner=main.ExperimentRunner()
        results=experimentRunner.structured_data_outputs()

        self.assertIsInstance(results,dict)
        
    def test_expected_keys(self: "TestExperimentRunner"):
        """Test that structured_data_outputs() returns all expected dictionary keys.

        Args:
            self (TestExperimentRunner):  Current unittest test case instance.
        """
        # construct the ExperimentRunner instance and call structured_data_outputs() on it to compute the dictionary containing the data frames
        experimentRunner=main.ExperimentRunner()
        results=experimentRunner.structured_data_outputs()

        expected_keys=["Final Data Frame Run", "Equity Curve", "Drawdown Series", "Completed Trades",
                       "Log Events", "Prices"]
        
        self.assertEqual( list(results.keys()), expected_keys )

    def test_dictionary_values_type(self: "TestExperimentRunner"):
        """Check each returned dictionary value is a pd.DataFrame dtype

        Args:
            self (TestExperimentRunner): Current unittest test case instance.
        """
        # construct the ExperimentRunner instance and call structured_data_outputs() on it to compute the dictionary containing the data frames
        experimentRunner=main.ExperimentRunner()
        results=experimentRunner.structured_data_outputs()

        self.assertIsInstance( results["Final Data Frame Run"], pd.DataFrame )
        self.assertIsInstance( results["Equity Curve"], pd.DataFrame )
        self.assertIsInstance( results["Drawdown Series"], pd.DataFrame )
        self.assertIsInstance( results["Completed Trades"], pd.DataFrame )
        self.assertIsInstance( results["Log Events"], pd.DataFrame )
        self.assertIsInstance( results["Prices"], pd.DataFrame )

    def test_length_and_labels_column_run_data_frame(self:"TestExperimentRunner"):
        """tests that Final Data Frame Run contains exactly 6 rows (1 row per TradingEngine run), and that the run data frame's "labels" column exists

        Args:
            self (TestExperimentRunner): Current unittest test case instance.
        """
        # construct the ExperimentRunner instance and call structured_data_outputs() on it to compute the dictionary containing the data frames
        experimentRunner=main.ExperimentRunner()
        results=experimentRunner.structured_data_outputs()

        expected_values_labels_run_data_frame=["Apple-Trend", "Apple-Mean Reversion", 
                                               "Google-Trend", "Google-Mean Reversion",
                                               "Microsoft-Trend", "Microsoft-Mean Reversion"]

        self.assertTrue( len(results["Final Data Frame Run"])==6 )
        self.assertEqual( list(results["Final Data Frame Run"]["labels"]), expected_values_labels_run_data_frame )

    def test_non_empty_data_frames(self:"TestExperimentRunner"):
        """tests that the data frames are not empty (no axes of length 0)
        Args:
            self (TestExperimentRunner): Current unittest test case instance.
        """
        # construct the ExperimentRunner instance and call structured_data_outputs() on it to compute the dictionary containing the data frames
        experimentRunner=main.ExperimentRunner()
        results=experimentRunner.structured_data_outputs()

        self.assertFalse(results["Equity Curve"].empty)
        self.assertFalse(results["Drawdown Series"].empty)
        self.assertFalse(results["Completed Trades"].empty)
        self.assertFalse(results["Log Events"].empty)
        self.assertFalse(results["Prices"].empty)

    def test_labels_columns_data_frames(self:"TestExperimentRunner"):
        """tests that the "labels" columns exist for each data frame

        Args:
            self (TestExperimentRunner): Current unittest test case instance.
        """
        # construct the ExperimentRunner instance and call structured_data_outputs() on it to compute the dictionary containing the data frames
        experimentRunner=main.ExperimentRunner()
        results=experimentRunner.structured_data_outputs()

        expected_values_labels=["Apple-Trend", "Apple-Mean Reversion", 
                                "Google-Trend", "Google-Mean Reversion",
                                "Microsoft-Trend", "Microsoft-Mean Reversion"]

        self.assertEqual( list(results["Equity Curve"]["labels"].unique()), expected_values_labels )
        self.assertEqual( list(results["Drawdown Series"]["labels"].unique()), expected_values_labels )
        self.assertEqual( list(results["Completed Trades"]["labels"].unique()), expected_values_labels )
        self.assertEqual( list(results["Log Events"]["labels"].dropna().unique()), expected_values_labels )
        self.assertEqual( list((results["Prices"]["ticker"]+"-"+results["Prices"]["strategy"]).unique()), expected_values_labels )



        
        
class TestAggregationLayer(unittest.TestCase):

    def test_total_runs_summary(self):
        """tests that total_runs_summary returns the correct number of rows
        of the 'Final Data Frame Run' (length of the data frame) 
        """

        # new 'fake' run data frame to test the method on 
        d={ "run_number": [1,2,3], 
            "ticker": ["Apple", "Apple", "Google"],
            "strategy": ["Trend","Trend","Trend"],
            "starting cash": [1000,1000,1000],
            "total net profit": [50.6, 46.12, -12.56],
            "mdd": [8.53, 5.12, 2.64],
            "expectancy": [-2.54, None, 13.4],
            "payoff ratio": [2.4, 1.44, 7.2],
            "profit factor": [5.23, 1.02, 1.23],
            "sharpe ratio": [0.045, -0.13, 1.5],
            "labels": ["Apple-Trend", "Apple-Trend", "Google-Trend"] }
        new_final_run_df=pd.DataFrame(data=d)
        results={ "Final Data Frame Run": new_final_run_df }

        self.assertTrue(main.AggregationLayer(results).total_runs_summary()==3)

    def test_best_run_summary(self):
        """tests that best_run_summary returns the entire row from "Final Data Frame Run"
        which corresponds to the maximum 'total net profit' cell value
        """

        # new 'fake' run data frame to test the method on 
        d={ "run_number": [1,2,3], 
            "ticker": ["Apple", "Apple", "Google"],
            "strategy": ["Trend","Trend","Trend"],
            "starting cash": [1000,1000,1000],
            "total net profit": [50.6, 46.12, -12.56],
            "mdd": [8.53, 5.12, 2.64],
            "expectancy": [-2.54, None, 13.4],
            "payoff ratio": [2.4, 1.44, 7.2],
            "profit factor": [5.23, 1.02, 1.23],
            "sharpe ratio": [0.045, -0.13, 1.5],
            "labels": ["Apple-Trend", "Apple-Trend", "Google-Trend"] }
        new_final_run_df=pd.DataFrame(data=d)
        results={ "Final Data Frame Run": new_final_run_df }

        self.assertTrue(main.AggregationLayer(results).best_run_summary()=={"run_number": 1, 
                                                                            "ticker": "Apple",
                                                                            "strategy": "Trend",
                                                                            "starting cash": 1000,
                                                                            "total net profit": 50.6,
                                                                            "mdd": 8.53,
                                                                            "expectancy": -2.54,
                                                                            "payoff ratio": 2.4,
                                                                            "profit factor": 5.23,
                                                                            "sharpe ratio": 0.045,
                                                                            "labels": "Apple-Trend"})
        
    def test_worst_run_summary(self):
        """tests that worst_run_summary returns the entire row from "Final Data Frame Run"
        which corresponds to the minimum 'total net profit' cell value
        """
        # new 'fake' run data frame to test the method on 
        d={ "run_number": [1,2,3], 
            "ticker": ["Apple", "Apple", "Google"],
            "strategy": ["Trend","Trend","Trend"],
            "starting cash": [1000,1000,1000],
            "total net profit": [50.6, 46.12, -12.56],
            "mdd": [8.53, 5.12, 2.64],
            "expectancy": [-2.54, None, 13.4],
            "payoff ratio": [2.4, 1.44, 7.2],
            "profit factor": [5.23, 1.02, 1.23],
            "sharpe ratio": [0.045, -0.13, 1.5],
            "labels": ["Apple-Trend", "Apple-Trend", "Google-Trend"] }
        new_final_run_df=pd.DataFrame(data=d)
        results={ "Final Data Frame Run": new_final_run_df }

        self.assertTrue(main.AggregationLayer(results).worst_run_summary()=={"run_number": 3, 
                                                                            "ticker": "Google",
                                                                            "strategy": "Trend",
                                                                            "starting cash": 1000,
                                                                            "total net profit": -12.56,
                                                                            "mdd": 2.64,
                                                                            "expectancy": 13.4, 
                                                                            "payoff ratio": 7.2,
                                                                            "profit factor": 1.23,
                                                                            "sharpe ratio": 1.5,
                                                                            "labels": "Google-Trend"})

    def test_average_performance_summary(self):
        """tests that the expected averages are calculated 
        for each individual performance metric per total backtest runs
        """
        # new 'fake' run data frame to test the method on 
        d={ "run_number": [1,2,3], 
            "ticker": ["Apple", "Apple", "Google"],
            "strategy": ["Trend","Trend","Trend"],
            "starting cash": [1000,1000,1000],
            "total net profit": [50.6, 46.12, -12.56],
            "mdd": [8.53, 5.12, 2.64],
            "expectancy": [-2.54, None, 13.4],
            "payoff ratio": [2.4, 1.44, 7.2],
            "profit factor": [5.23, 1.02, 1.23],
            "sharpe ratio": [0.045, -0.13, 1.5],
            "labels": ["Apple-Trend", "Apple-Trend", "Google-Trend"] }
        new_final_run_df=pd.DataFrame(data=d)
        results={ "Final Data Frame Run": new_final_run_df }

        self.assertTrue( main.AggregationLayer(results).average_performance_summary()=={"average total net profit": 28.05, 
                                                                               "average mdd": 5.43,
                                                                               'average expectancy': 5.43,
                                                                               'average payoff ratio': 3.68,
                                                                               'average profit factor': 2.49,
                                                                               'average sharpe ratio': 0.47} )
        
    def test_selected_run_summary(self):
        """Test that selected_run_summary() returns the correct row as a dict 
        for a given ticker and strategy."""

        # new 'fake' run data frame to test the method on 
        d={ "run_number": [1,2,3], 
            "ticker": ["Apple", "Apple", "Google"],
            "strategy": ["Trend","Trend","Trend"],
            "starting cash": [1000,1000,1000],
            "total net profit": [50.6, 50.6, -12.56],
            "mdd": [8.53, 8.53, 2.64],
            "expectancy": [13.4, 13.4, None],
            "payoff ratio": [1.44, 1.44, 7.2],
            "profit factor": [5.23, 5.23, 1.23],
            "sharpe ratio": [-0.13, -0.13, 1.5],
            "labels": ["Apple-Trend", "Apple-Trend", "Google-Trend"] }
        new_final_run_df=pd.DataFrame(data=d)
        results={ "Final Data Frame Run": new_final_run_df }

        self.assertTrue( main.AggregationLayer(results).selected_run_summary("Apple", "Trend")=={"run_number": 1, 
                                                                                                "ticker": "Apple",
                                                                                                "strategy": "Trend",
                                                                                                "starting cash": 1000,
                                                                                                "total net profit": 50.6,
                                                                                                "mdd": 8.53,
                                                                                                "expectancy": 13.4, 
                                                                                                "payoff ratio": 1.44,
                                                                                                "profit factor": 5.23,
                                                                                                "sharpe ratio": -0.13,
                                                                                                "labels": "Apple-Trend"})
        
    def test_selected_run_trade_list(self):
        """Test that selected_run_trade_list() returns the correct 
        filtered trades DataFrame for a given ticker and strategy."""

        # new 'fake' run data frame to test the method on 
        d_trades = {
                    "run_number": [1,2,3],
                    "ticker":["Apple","Apple","Google" ],
                    "strategy":["Trend","Trend","Mean Reversion"],
                    "entry_day":[3,7,4 ],
                    "entry_price":[100.0,110.0,200.0],
                    "exit_day":[5,9,6 ],
                    "exit_price":[105.0,108.0,195.0],
                    "profit":[50.0,-20.0,-50.0],
                    "return_pct":[5.0, -1.82,-2.5],
                    "labels":["Apple-Trend", "Apple-Trend", "Google-Mean Reversion"],
                    "number_trades_took_place":[1,1,1] }
        new_final_run_df=pd.DataFrame(data=d_trades)
        results={ "Completed Trades": new_final_run_df }

        # dictionary for the selected trade run 
        selected_run={ "run_number": 3, 
         "ticker": "Google",
         "strategy": "Mean Reversion",
         "entry_day": 4,
         "entry_price": 200.0,
         "exit_day": 6,
         "exit_price": 195.0, 
         "profit": -50.0,
         "return_pct": -2.5,
         "labels": "Google-Mean Reversion", 
         "number_trades_took_place": 1}
        selected_run_df=pd.DataFrame(data=selected_run,index=[0])
        selected_run_df=selected_run_df.reset_index(drop=True)

        pd.testing.assert_frame_equal( (main.AggregationLayer(results).selected_run_trade_list("Google", "Mean Reversion")).reset_index(drop=True) , selected_run_df )

    def test_selected_run_trade_list_empty(self):
        """Test that selected_run_trade_list() raises ValueError 
        when no trades exist for the given ticker and strategy."""

        # new 'fake' run data frame to test the method on 
        d_trades = { "run_number": [],
                    "ticker":[],
                    "strategy":[],
                    "entry_day":[],
                    "entry_price":[],
                    "exit_day":[],
                    "exit_price":[],
                    "profit":[],
                    "return_pct":[],
                    "labels":[],
                    "number_trades_took_place":[] }
        new_trades_df=pd.DataFrame(data=d_trades)
        results={ "Completed Trades": new_trades_df }

        with self.assertRaises(ValueError):
            main.AggregationLayer(results).selected_run_trade_list("Google", "Mean Reversion")

    def test_aggregation_outputs_returned_dictionary(self):
        """test that it returns the correct dictionary instance"""
        main.ExecutionState.backtest_run_number=0

        state=main.ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
        dictionary_data_frames=main.TradingEngine.backtest_run(state)
        run_data_frame=main.TradingEngine.performance_metrics_data_frame(state)
        results_data_frames={ "Final Data Frame Run": run_data_frame,
                              "Equity Curve": dictionary_data_frames["equity_curve"],
                                "Drawdown Series": dictionary_data_frames["drawdown_series"],
                                  "Completed Trades": dictionary_data_frames["trades"],
                                    "Log Events": dictionary_data_frames["log_events"],
                                      "Prices": dictionary_data_frames["prices"]  }

        self.assertIsInstance( main.AggregationLayer(results_data_frames).aggregation_outputs("Apple", "Trend") , dict)
        
    def test_aggregation_outputs_expected_keys(self):
        """test that it contains the 6 expected keys"""
        main.ExecutionState.backtest_run_number=0

        state=main.ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
        dictionary_data_frames=main.TradingEngine.backtest_run(state)
        run_data_frame=main.TradingEngine.performance_metrics_data_frame(state)
        results_data_frames={ "Final Data Frame Run": run_data_frame,
                              "Equity Curve": dictionary_data_frames["equity_curve"],
                                "Drawdown Series": dictionary_data_frames["drawdown_series"],
                                  "Completed Trades": dictionary_data_frames["trades"],
                                    "Log Events": dictionary_data_frames["log_events"],
                                      "Prices": dictionary_data_frames["prices"]  }
        
        expected_keys=["total_runs", "best_run_summary", "worst_run_summary", "average_performance_summary",
                       "selected_run_summary", "selected_run_trade_list"]

        self.assertEqual( list((main.AggregationLayer(results_data_frames).aggregation_outputs("Apple","Trend")).keys()) , expected_keys)

    def test_aggregation_outputs_dictionary_dtype(self):
        """Check each returned dictionary value belongs to its corresponding expected data type"""
        main.ExecutionState.backtest_run_number=0

        state=main.ExecutionState(trendMethod=True, csv_ticker="data/aapl_us_d.csv", cashValue=10000, ticker_name="Apple")
        dictionary_data_frames=main.TradingEngine.backtest_run(state)
        run_data_frame=main.TradingEngine.performance_metrics_data_frame(state)
        results_data_frames={ "Final Data Frame Run": run_data_frame,
                              "Equity Curve": dictionary_data_frames["equity_curve"],
                                "Drawdown Series": dictionary_data_frames["drawdown_series"],
                                  "Completed Trades": dictionary_data_frames["trades"],
                                    "Log Events": dictionary_data_frames["log_events"],
                                      "Prices": dictionary_data_frames["prices"]  }
        
        self.assertIsInstance( (main.AggregationLayer(results_data_frames).aggregation_outputs("Apple", "Trend"))["total_runs"], int )
        self.assertIsInstance( (main.AggregationLayer(results_data_frames).aggregation_outputs("Apple", "Trend"))["best_run_summary"], dict )
        self.assertIsInstance( (main.AggregationLayer(results_data_frames).aggregation_outputs("Apple", "Trend"))["worst_run_summary"], dict )
        self.assertIsInstance( (main.AggregationLayer(results_data_frames).aggregation_outputs("Apple", "Trend"))["average_performance_summary"], dict )
        self.assertIsInstance( (main.AggregationLayer(results_data_frames).aggregation_outputs("Apple", "Trend"))["selected_run_summary"], dict )
        self.assertIsInstance( (main.AggregationLayer(results_data_frames).aggregation_outputs("Apple", "Trend"))["selected_run_trade_list"], pd.DataFrame )
        