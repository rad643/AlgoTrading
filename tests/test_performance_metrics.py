import unittest
import performanceMetrics
import pandas as pd 

class testMDD(unittest.TestCase):
    def test_value_equality(self):
        self.assertEqual(performanceMetrics.mdd([100, 110, 105, 120, 90, 95]), 25)
    def test_float_approximation(self):
        self.assertEqual(performanceMetrics.mdd([100, 112, 109, 121, 103, 108]), 14.88)
    def test_zero_division_error(self):
        with self.assertRaises(ZeroDivisionError):
            performanceMetrics.mdd([0, -1, -3, -2])
    def test_empty_list(self):
        with self.assertRaises(ValueError):
            performanceMetrics.mdd([])
    def test_invalid_data_type(self):
        with self.assertRaises(ValueError):
            performanceMetrics.mdd([100, "abc", 95])
    def test_single_element_list(self):
        self.assertEqual(performanceMetrics.mdd([1]), 0)
    def test_monotonically_increasing_list(self):
        self.assertEqual(performanceMetrics.mdd([100, 110, 120, 130]),0)
    def test_all_equal_values(self):
        self.assertEqual(performanceMetrics.mdd([100,100,100]),0)

class testExpectancy(unittest.TestCase):
    def test_value_equality(self):
        self.assertEqual(performanceMetrics.expectancy(6,10,300.0,4,-200.0), 10.0)
    def test_float_approximation(self):
        self.assertEqual(performanceMetrics.expectancy(2,5,25,3,-22), 0.60)
    def test_zero_negative_profit(self):
        with self.assertRaises(ZeroDivisionError):
            performanceMetrics.expectancy(3,5,90,0,-30)
    def test_zero_positive_profit(self):
        with self.assertRaises(ZeroDivisionError):
            performanceMetrics.expectancy(0,5,90,2,-30)
    def test_zero_number_trades(self):
        with self.assertRaises(ZeroDivisionError):
            performanceMetrics.expectancy(3,0,90,2,-30)
    def test_negative_expectancy(self):
        self.assertEqual(performanceMetrics.expectancy(3, 10, 60.0, 7, -280.0), -22)

class testPayoffRatio(unittest.TestCase):
    def test_value_equality(self):
        self.assertEqual(performanceMetrics.payoff_ratio(300.0,-200.0,6,4), 1)
    def test_float_approximation(self):
        self.assertEqual(performanceMetrics.payoff_ratio(275.0, -120.0, 5,4), 1.83)
    def test_null_positive_profit(self):
        with self.assertRaises(ZeroDivisionError):
            performanceMetrics.payoff_ratio(275.0, -120.0, 0, 4)
    def test_null_negative_profit(self):
        with self.assertRaises(ZeroDivisionError):
            performanceMetrics.payoff_ratio(275.0, -120.0, 5, 0)

class testProfitFactor(unittest.TestCase):
    def test_float_approximation(self):
        self.assertEqual(performanceMetrics.profit_factor(350.0, -210.0), 1.67)
    def test_value_equality(self):
        self.assertEqual(performanceMetrics.profit_factor(300, -150.0), 2)
    def test_null_totalProfitNegativeTrades(self):
        with self.assertRaises(ZeroDivisionError):
            performanceMetrics.profit_factor(300, 0)

class testSharpeRatio(unittest.TestCase):
    def test_value_equality(self):
        self.assertEqual(performanceMetrics.sharpe_ratio([100,110,132,171.6]), 2)
    def test_float_approximation(self):
        self.assertEqual(performanceMetrics.sharpe_ratio([100,110,105,120,90,95]), 0.004)
    def test_null_standardDeviation(self):
        with self.assertRaises(ZeroDivisionError):
            performanceMetrics.sharpe_ratio([100,100,100,100])
    def test_invalid_data_type(self):
        with self.assertRaises(ValueError):
            performanceMetrics.sharpe_ratio([100, 95, 80, "string"])
    def test_empty_list(self):
        with self.assertRaises(ValueError):
            performanceMetrics.sharpe_ratio([])
    def test_single_element_list(self):
        self.assertTrue(pd.isna(performanceMetrics.sharpe_ratio([100])))
    def test_null_sharpe_ratio(self):
        self.assertTrue(performanceMetrics.sharpe_ratio([100,110,99])==0)
    def test_negative_sharpe_ratio(self):
        self.assertTrue(performanceMetrics.sharpe_ratio([100,95,90])== -27.577)