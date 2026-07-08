import numpy as np

def averageUpToDay(list_store_closing_prices_up_to_day):
    """

    listStorePreviousClosingPrices: list that stores all the closing prices up to the current day
    list starts at index 0, so the closing price for day 1 will be at index 0; every closing price has an index shifted to the right by 1

    :param list_store_closing_prices_up_to_day: Description
    """
    #verify that the parameter is a list 
    if not isinstance(list_store_closing_prices_up_to_day, list):
        raise TypeError
    # compute the average with numpy vectorization 
    arr=np.array(list_store_closing_prices_up_to_day)
    return np.mean(arr)

    