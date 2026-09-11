import numpy as np


def averageUpToDay(list_store_closing_prices_up_to_day):
    """Arithmetic mean of every closing price recorded before the current day.

    The list is append-only and 0-indexed, so day N's closing price sits at
    index N-1. Callers append today's close *after* calling this, which is
    what makes the returned average exclude the current day.

    Args:
        list_store_closing_prices_up_to_day (list[float]): closing prices for
            all days preceding the current one, in chronological order.

    Returns:
        np.float64: the mean of the list. Returns ``nan`` (with a
        RuntimeWarning) for an empty list rather than raising.

    Raises:
        TypeError: if the argument is not a ``list``.
    """
    # verify that the parameter is a list
    if not isinstance(list_store_closing_prices_up_to_day, list):
        raise TypeError("Prices need to be stored inside a list")
    # compute the average with numpy vectorization
    arr = np.array(list_store_closing_prices_up_to_day)
    return np.mean(arr)
