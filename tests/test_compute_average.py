import unittest
import compute_average as ca 

class TestComputeAverage(unittest.TestCase):
    #assert correct output for valid list 
    def test_valid_list(self):
        self.assertEqual( ca.averageUpToDay([1,2,3,4,5,6,7,8,9]), 5 ) 
        self.assertEqual( ca.averageUpToDay([53,234,1321,312131]), 78434.75 ) 

    #empty list input raises division by zero error 
    def test_empty_list(self):
        with self.assertRaises(ZeroDivisionError):
            ca.averageUpToDay([])

    #invalid data type inside list 
    def test_invalid_list_data_type(self):
        with self.assertRaises(TypeError):
            ca.averageUpToDay([1,2,3,4,'string', 5,6,])

    #incorrect input type 
    def test_incorrect_input(self):
        with self.assertRaises(TypeError):
            ca.averageUpToDay({3,57.5235,123,42})

    #single element list 
    def test_single_element(self):
        self.assertEqual( ca.averageUpToDay([5]), 5 )

    #float inputs are accepted as valid input ]
    def test_float_inputs(self):
        self.assertEqual( ca.averageUpToDay([1.5,3.23,5.1874,8.2]), 4.52935 )

    #list of only zero values 
    def test_list_zeros(self):
        self.assertEqual( ca.averageUpToDay([0,0,0,0,0]), 0 )
    
