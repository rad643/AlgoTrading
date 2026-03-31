import process_1_day
import unittest

class TestProcessDay(unittest.TestCase):
    #main behavior logic
    def test_valid_redirection(self):
        self.assertEqual( process_1_day.process_one_day(1, "2026-05-01", 10, 5.5, 10, 100, 100, '', 20, 0.005, 0.0005, True, 0, 10, 11, 0, 0, 10, 10, 0), (0, 0, 10, 11, 100, 100, 'BUY') )
        self.assertEqual( process_1_day.process_one_day(1,"2026-05-01", 10, 5.5, 10, 100, 100, '', 20, 0.005, 0.0005, False, 0, 10, 11, 0, 0, 10, 11, 0), (0, 0, 10, 11, 100, 100, 'SELL') )
        self.assertEqual( process_1_day.process_one_day(1, "2026-05-01", 10, 5.5, 10, 100, 100, 'BUY', 20, 0.005, 0.0005, True, 0, 10, 11, 0, 0, 10, 11, 0), (1.0, 0, 10.005, 11, 89.99, 99.99, 'BUY') )
        self.assertEqual( process_1_day.process_one_day(1, "2026-05-01", 10, 5.5, 10, 100, 100, 'SELL', 20, 0.005, 0.0005, False, 0, 10, 11, 0, 2, 10, 11, 0), (0, -0.01, 10, 9.995, 119.98, 119.98, 'SELL') )

    #small set of failure and invalid input tests
    def test_invalid_data_type(self):
        #checking that trendMethod is a boolean 
        with self.assertRaises(TypeError):
            process_1_day.process_one_day(1, "2026-05-01", 10, 5.5, 10, 100, 100, 'SELL', 20, 0.005, 0.0005, 'False', 0, 10, 11, 0, 2, 10, 11, 0)
        #checking that pending_action is a string data type
        with self.assertRaises(TypeError):
            process_1_day.process_one_day(1, "2026-05-01", 10, 5.5, 10, 100, 100, True, 20, 0.005, 0.0005, False, 0, 10, 11, 0, 2, 10, 11, 0)
        #pending_action is a string data type but is not inside {BUY, SELL, HOLD, ''}
        with self.assertRaises(ValueError):
            process_1_day.process_one_day(1, "2026-05-01", 10, 5.5, 10, 100, 100, 'incorrect string', 20, 0.005, 0.0005, False, 0, 10, 11, 0, 2, 10, 11, 0)
        #checking that average is a float or integer 
        with self.assertRaises(TypeError):
            process_1_day.process_one_day(1, "2026-05-01", 10, 'hello', 10, 100, 100, 'BUY', 20, 0.005, 0.0005, False, 0, 10, 11, 0, 2, 10, 11, 0)
        