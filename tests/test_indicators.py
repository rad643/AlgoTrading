from helpers import indicators as ind   

def test_avg_expected_resp():
    """
    Function to test the average calculation
    from the indicators file
    """

    # arange 
    test_list = [ ("2023-01-16", 100), ("2023-01-17",200)  ]
    N = 5
    # act
    avg = ind.avg(N=N, listInsert=test_list)
    # assert 
    expected_output = 150
    assert avg == expected_output   
    print(avg)


def test_avg_N_longer_than_list():
    test_list = [ ("2023-01-16", 100), ("2023-01-17",200)  ]
    N = 5
    result = ind.avg(N=N, listInsert=test_list)
    assert result == None