#we need to automatically create temporary files, assign them unique names and manage their paths in order to prevent filename collisions
import tempfile
#we're only importing os to delete the csv files we created manually inside the test
import os 
import data_loader as dl
import unittest

#unittest framework: multiple tests/methods=multiple edge cases 
class TestDataLoaderMethods(unittest.TestCase):
    #generator produces the correct output for a normal CSV input with 5 days of data
    def test_normal_csv(self):
        #holds tuples representing each day's values 
        generator=dl.read_ticker_csv("data/5_day_input.csv", 100)
        #expected yielded tuples corresponding to each day's values 
        #days 1 and 2 have no computed average and no nextDayOpeningPrice => None,None
        self.assertEqual( (1, "2026-01-01", 5, None, None), next(generator) )
        self.assertEqual( (2, "2026-01-02", 6, None, None), next(generator) )
        self.assertEqual( (3, "2026-01-03", 10, 5.5, 10), next(generator) )
        self.assertEqual( (4, "2026-01-04", 11, 7, 11), next(generator) )
        self.assertEqual( (5, "2026-01-05", 6, 8, 6), next(generator) )

        #verify that the generator stops exactly after the 5 rows
        with self.assertRaises(StopIteration):
            next(generator)

    #edge case test that the generator produces the correct output for an empty CSV input
    def test_empty_csv(self):
        #create a temporary file that is empty 
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            #nothing to write inside it other than the header (that is skipped)
            f.write("Date, Open, High, Low, Close, Adj Close, Volume\n")
            #store the full path of this temporary file so we can reopen/read it later after leaving the with block
            temp_path_created_file=f.name
        #the file is now closed, but the generator can open it because we've stored its path as a string inside temp_path_created_file
        #we need to make sure that the temp file gets deleted no matter what the outcome
        try:
            #empty csv file => generator can't yield any tuples 
            generator=dl.read_ticker_csv(temp_path_created_file, 100)
            #Expect StopIteration when calling next() on an empty generator 
            with self.assertRaises(StopIteration):
                next(generator)
        #'finally' block runs no matter what => we need to completely remove the temporary file we created once we're done
        finally: 
            #remove temp file 
            os.remove(temp_path_created_file)

    #edge case test that the generator produces the correct output for a 2 row CSV input 
    def test_2_row_csv(self):
        #create a temporary file that only contains 2 rows => average and nextDayOpeningPrice are both None during first 2 days 
        with tempfile.NamedTemporaryFile(mode='w', suffix=".csv", delete=False) as f:
            f.write("Date, Open, High, Low, Close, Adj Close, Volume\n")
            f.write("2026-01-01, 5, 5, 5, 5, 5, 1000\n")
            f.write("2026-01-02, 6, 6, 6, 6, 6, 1000")
            #store the full path of this temporary file so we can reopen/read it later after leaving the with block
            temp_path_created_file=f.name
        #the file is now closed, but the generator can open it because we've stored its path as a string inside temp_path_created_file
        #we need to make sure that the temp file gets deleted no matter what the outcome
        try:
            #check that generator asserts correct tuples for days 1 and 2 
            generator=dl.read_ticker_csv(temp_path_created_file, 100)
            #no averages and nextDayOpeningPrices produced => all None's 
            self.assertEqual( (1, "2026-01-01", 5, None, None), next(generator) )
            self.assertEqual( (2, "2026-01-02", 6, None, None), next(generator) )
            #verify that the generator stops yielding values after the 2 rows
            with self.assertRaises(StopIteration):
                next(generator)
        #'finally' block runs no matter what => we need to completely remove the temporary file we created once we're done
        finally:
            #remove temp file 
            os.remove(temp_path_created_file)

    #edge case test that the generator produces the correct output for a malformed csv (extra column)
    def test_malformed_csv(self):
        #create a temporary file with malformed structure (too many fields) that you can test on for the edge case 
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date, Open, High, Low, Close, Adj Close, Volume\n")
            f.write("2026-01-01, 6, 6, 6, 6, 6, 1000\n")
            #closing price index missing => float(line[4]) will raise an error 
            f.write("2026-01-01, 6, 6, 6\n")
            #store the full path of this temporary file so we can reopen/read it later after leaving the with block
            temp_path_created_file=f.name
        #the file is now closed, but the generator can open it because we've stored its path as a string inside temp_path_created_file
        #we need to make sure that the temp file gets deleted no matter what the outcome 
        try:
            #generator yields values from the temporary file 
            generator=dl.read_ticker_csv(temp_path_created_file, 100)
            #first row yielded is valid so no error raised there
            next(generator)
            #if ValueError raised for malformed csv on the first error it encounters, test passes, generator ends 
            with self.assertRaises(IndexError):
                next(generator)
        #'finally' block runs no matter what => we need to completely remove the temporary file we created once we're done
        finally:
            #remove temp file
            os.remove(temp_path_created_file)

    #edge case test that the generator produces the correct output for inconsistent data types (text in a numeric column)
    def test_inconsistent_data_type(self):
        #create a temporary file with incorrect structure that you can test on for the edge case 
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date, Open, High, Low, Close, Adj Close, Volume\n")
            f.write("2026-01-01, 6, 6, 6, 6, 6, 1000\n")
            f.write("2026-01-01, 10, 10, 10, 10, 10, 1000\n")
            #string type in place of numeric closing price 
            f.write("2026-01-01, 6, 6, 6, 'error', 6, 1000\n")
            #store the full path of this temporary file so we can reopen/read it later after leaving the with block
            temp_path_created_file=f.name
        #the file is now closed, but the generator can open it because we've stored its path as a string inside temp_path_created_file
        #we need to make sure that the temp file gets deleted no matter what the outcome 
        try:
            #generator yields values from the temporarily created tmp.csv file  
            generator=dl.read_ticker_csv(temp_path_created_file, 100)
            #first 2 rows are correct so generator yields them with no errors raised 
            next(generator)
            next(generator)
            #if ValueError raised for inconsistent data type on the first error it encounters, test passes, generator ends
            with self.assertRaises(ValueError):
                next(generator)
        #'finally' block runs no matter what => we need to completely remove the temporary file we created once we're done
        finally:
            #remove temp file 
            os.remove(temp_path_created_file)

