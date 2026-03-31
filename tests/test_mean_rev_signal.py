import unittest
#we need StringIO as an in-memory buffer
import io
#we need redirect_stdout() to capture the printed stdout
import contextlib
import mean_rev_signal as mrv

class TestMeanRevSignal(unittest.TestCase):

    #first we test the main logic behaviour (the returned values in the tuple)
    def test_main_logic_behavior(self):

        #no pending action 
        self.assertEqual( mrv.mean_rev_step(1, "2026-05-01", 10, 5.5, 10, 100, 100, '', 20, 0.005, 0.0005, 0, 10, 11, 0), (0, 0, 10, 11, 100, 100, 'SELL') )
        #pending action is BUY when you have no shares 
        self.assertEqual( mrv.mean_rev_step(1, "2026-05-01", 10, 10.5, 10, 100, 100, 'BUY', 20, 0.005, 0.0005, 0, 10, 11, 0), (1.0, 0, 10.005, 11, 89.99, 99.99, 'BUY') )
        #pending action is BUY when you've already got shares 
        self.assertEqual( mrv.mean_rev_step(1, "2026-05-01", 10, 10.5, 10, 100, 100, 'BUY', 20, 0.005, 0.0005, 2, 10, 11, 0), (2, 0, 10, 11, 100, 120, 'BUY') )
        #pending action is SELL and you've got shares 
        self.assertEqual( mrv.mean_rev_step(1, "2026-05-01", 10, 10, 11, 100, 100, 'SELL', 20, 0.005, 0.0005, 2, 10, 11, 0), (0, 1.99, 10, 10.995, 121.98, 121.98, 'HOLD') )
        #pending action is SELL and you don't have any shares 
        self.assertEqual( mrv.mean_rev_step(1, "2026-05-01", 10, 10, 11, 100, 100, 'SELL', 20, 0.005, 0.0005, 0, 10, 11, 0), (0, 0, 10, 11, 100, 100, 'HOLD') )
        #pending action is HOLD
        self.assertEqual( mrv.mean_rev_step(1, "2026-05-01", 10, 5.5, 10, 100, 100, 'HOLD', 20, 0.005, 0.0005, 1, 10, 11, 0), (1, 0, 10, 11, 100, 110, 'SELL') )

    #then we can test for the correct printing to the screen (correct formatted output)
    def test_correct_printed_text(self):

        #capture printed stdout in an in-memory buffer, then compare it to the expected formatted output 
        #no pending action case
        with contextlib.redirect_stdout( io.StringIO() ) as buffer:
            mrv.mean_rev_step(1, "2026-05-01", 10, 5.5, 10, 100, 100, '', 20, 0.005, 0.0005, 0, 10, 11, 0)
        self.assertEqual(buffer.getvalue(), 'Day 1 | Date: 2026-05-01 | Close: 10 | Avg: 5.500 | Mean Reversion: SELL | Position: 0 | Cash: 100 | Equity: 100\n\n\n' )

        #capture printed stdout in an in-memory buffer, then compare it to the expected formatted output 
        #pending action is BUY when you have no shares case
        with contextlib.redirect_stdout( io.StringIO() ) as buffer:
            mrv.mean_rev_step(1, "2026-05-01", 10, 10.5, 10, 100, 100, 'BUY', 20, 0.005, 0.0005, 0, 10, 11, 0)
        self.assertEqual(buffer.getvalue(), 'Day 1 | Date: 2026-05-01 | Close: 10 | Execution price: 10.005 | Avg: 10.500 | Mean Reversion: BUY | Position: 1.0 | Cash: 89.99 | Equity: 99.99\n\n\n' )

        #capture printed stdout in an in-memory buffer, then compare it to the expected formatted output 
        #pending action is BUY when you've already got shares case
        with contextlib.redirect_stdout( io.StringIO() ) as buffer:
            mrv.mean_rev_step(1, "2026-05-01", 10, 10.5, 10, 100, 100, 'BUY', 20, 0.005, 0.0005, 2, 10, 11, 0)
        self.assertEqual(buffer.getvalue(), 'Day 1 | Date: 2026-05-01 | Close: 10 | Avg: 10.500 | Mean Reversion: BUY | Position: 2 | Cash: 100 | Equity: 120\n\n\n' )

        #capture printed stdout in an in-memory buffer, then compare it to the expected formatted output 
        #pending action is SELL and you've got shares case
        with contextlib.redirect_stdout( io.StringIO() ) as buffer:
            mrv.mean_rev_step(1, "2026-05-01", 10, 10, 11, 100, 100, 'SELL', 20, 0.005, 0.0005, 2, 10, 11, 0)
        self.assertEqual(buffer.getvalue(), 'Day 1 | Date: 2026-05-01 | Close: 10 | Execution price: 10.995 | Avg: 10.000 | Mean Reversion: HOLD | Position: 0 | Cash: 121.98 | Equity: 121.98 | P&L: 1.990\n\n\n' )

        #capture printed stdout in an in-memory buffer, then compare it to the expected formatted output 
        #pending action is SELL and you don't have any shares case
        with contextlib.redirect_stdout( io.StringIO() ) as buffer:
            mrv.mean_rev_step(1, "2026-05-01", 10, 10, 11, 100, 100, 'SELL', 20, 0.005, 0.0005, 0, 10, 11, 0)
        self.assertEqual(buffer.getvalue(), 'Day 1 | Date: 2026-05-01 | Close: 10 | Avg: 10.000 | Mean Reversion: HOLD | Position: 0 | Cash: 100 | Equity: 100\n\n\n' )

        #capture printed stdout in an in-memory buffer, then compare it to the expected formatted output 
        #pending action is HOLD case
        with contextlib.redirect_stdout( io.StringIO() ) as buffer:
            mrv.mean_rev_step(1, "2026-05-01", 10, 5.5, 10, 100, 100, 'HOLD', 20, 0.005, 0.0005, 1, 10, 11, 0)
        self.assertEqual(buffer.getvalue(), 'Day 1 | Date: 2026-05-01 | Close: 10.000000 | Avg: 5.500 | Mean Reversion: SELL | Position: 1 | Cash: 100.000 | Equity: 110.000\n\n\n' )

    #and finally add a small set of failures and invalid input tests
    def test_invalid_inputs(self):

        #incorrect nb of arguments passed in 
        with self.assertRaises(TypeError):
            mrv.mean_rev_step( 1, "2026-05-01", 10, 5.5, 10, 100, 100, '', 20, 0.005, 0.0005, 0, 10, 11 )

        #checking if pending_action is a string 
        with self.assertRaises(TypeError):
            mrv.mean_rev_step( 1, "2026-05-01", 10, 5.5, 10, 100, 100, 55, 20, 0.005, 0.0005, 0, 10, 11, 0 )

        #checking that pending_action is in {"BUY", "SELL", "HOLD", ""}
        with self.assertRaises(ValueError):
            mrv.mean_rev_step( 1, "2026-05-01", 10, 5.5, 10, 100, 100, "invalid", 20, 0.005, 0.0005, 0, 10, 11, 0 )

        #checking that cashValue is integer or float 
        with self.assertRaises(TypeError):
            mrv.mean_rev_step( 1, "2026-05-01", 10, 5.5, 10, 'string', 100, "", 20, 0.005, 0.0005, 0, 10, 11, 0 )
        
        #checking that cashValue is not negative
        with self.assertRaises(ValueError):
            mrv.mean_rev_step( 1, "2026-05-01", 10, 5.5, 10, -5, 100, "", 20, 0.005, 0.0005, 0, 10, 11, 0 )

        #checking that cashValue is not zero 
        with self.assertRaises(ValueError):
            mrv.mean_rev_step( 1, "2026-05-01", 10, 5.5, 10, 0, 100, "", 20, 0.005, 0.0005, 0, 10, 11, 0 )

        