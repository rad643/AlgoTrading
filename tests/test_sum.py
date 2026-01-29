from helpers.indicators import calculate_sum

def test_sum_calc():
    a = 5
    b = 10

    return_sum = calculate_sum(a, b)
    assert return_sum == 15