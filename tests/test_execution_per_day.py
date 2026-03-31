import main 
import unittest

class TestExecutionPerDay(unittest.TestCase):

    #create instance/object of the Engine class that is now an attribute of this class's instances/objects (like self), but for the Trend strategy
    #testing for returned total profit 
    engineTrendStrategy=main.Engine()
    #checking the main core logic by asserting if returned total profit equals expected output (based on 5_day_input csv file) based on Trend method 
    def test_final_total_profit_trend_strategy(self):
        #by default trendMethod=true => total profit is computed via Trend strategy 
        self.assertEqual( self.engineTrendStrategy.execution_per_day(100), 0 )

    #create instance/object of the Engine class that is now an attribute of this class's instances/objects (like self), but for the Trend strategy
    #testing for list of stored equities 
    engineTrendStrategyListEquities=main.Engine()
    def test_final_list_equity_values_trend_strategy(self):
        #by default trendMethod=true => list of stored equity values is computed via Trend strategy
        #first we call execution_per_day to compute the list of equities based on Trend strategy 
        self.engineTrendStrategyListEquities.execution_per_day(100)
        #then we assert on self.engine.listStoreEquityValues against expected output 
        self.assertEqual( self.engineTrendStrategyListEquities.listStoreEquityValues, [100, 100, 100.0, 99.99, 94.99] )

    #create instance/object of the Engine class that is now an attribute of this class's instances/objects (like self), but for the Mean Rev strategy
    #testing for returned total profit 
    engineMeanRevStrategy=main.Engine()
    #checking the main core logic by asserting if returned total profit equals expected output (based on 5_day_input csv file) based on Mean Rev method
    def test_final_total_profit_mean_rev_strategy(self):
        #override trendMethod to false => total profit is computed via Mean Rev strategy
        self.engineMeanRevStrategy.trendMethod=False
        self.assertEqual( self.engineMeanRevStrategy.execution_per_day(100), 0 )

    #create instance/object of the Engine class that is now an attribute of this class's instances/objects (like self), but for the Mean Rev strategy
    #testing for list of stored equities 
    engineMeanRevStrategyListEquities=main.Engine()
    def test_final_list_equity_values_mean_rev_strategy(self):
        #override trendMethod to false => list of equities is computed via Mean Rev strategy
        self.engineMeanRevStrategyListEquities.trendMethod=False
        #first we call execution_per_day to compute the list of equities based on Mean Rev strategy 
        self.engineMeanRevStrategyListEquities.execution_per_day(100)
        #then we assert on self.engine.listStoreEquityValues against expected output 
        self.assertEqual( self.engineMeanRevStrategyListEquities.listStoreEquityValues, [100, 100, 100, 100, 100] )