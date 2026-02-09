def averageUpToDay(list_store_closing_prices_up_to_day):
    """

    listStorePreviousClosingPrices: list that stores all the closing prices up to the current day
    list starts at index 0, so the closing price for day 1 will be at index 0; every closing price has an index shifted to the right by 1

    :param list_store_closing_prices_up_to_day: Description
    """
    closingPricesSum = 0
    averageCurrentDay = 0
    for i in range(len(list_store_closing_prices_up_to_day)):
        closingPricesSum += list_store_closing_prices_up_to_day[i]
    averageCurrentDay = closingPricesSum / len(list_store_closing_prices_up_to_day)
    return averageCurrentDay
