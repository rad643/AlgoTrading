import os
from collections.abc import Generator
from datetime import date
from typing import cast

import pandas as pd
import requests
from dotenv import load_dotenv

import data_loading.compute_average as ca

url_path = "https://data.alpaca.markets/v2/stocks/bars"

load_dotenv()


def get_headers() -> dict[str, str]:
    """Read Alpaca credentials from the environment at call time."""
    return {
        "APCA-API-KEY-ID": os.environ["APCA_API_KEY_ID"],
        "APCA-API-SECRET-KEY": os.environ["APCA_API_SECRET_KEY"],
    }


def hist_data(
    tickers, timeframe="15Min", start="", end="", limit=1000
) -> dict[str, pd.DataFrame]:
    """extract historical data from alpaca's api through direct http request connection

    Args:
        tickers (str): comma-separated string of all the tickers you wanna request data from (mandatory parameter)
        timeframe (str, optional): timeframe between each bar candle . Defaults to "15Min".
        start (str, optional): start of the historical bar candles . Defaults to ''.
        end (str, optional): end of the historical bar candles . Defaults to ''.
        limit (int, optional): maximum number of bars sent back by the API in 1 page ( split across all tickers not per ticker ) . Defaults to 1000.

    Returns:
        dict : dictionary consisting of all the tickers as keys , and their corresponding returned data frames back from the api as the values to the keys
    """

    params = {
        "symbols": tickers,
        "timeframe": timeframe,
        "start": start,
        "end": end,
        "limit": limit,
    }
    bars = {}  # type: ignore [var-annotated]
    headers = get_headers()
    while True:
        r = requests.get(url=url_path, headers=headers, params=params)
        data = r.json()
        for ticker in data["bars"]:
            if ticker not in bars:
                bars[ticker] = []
            bars[ticker] += data["bars"][ticker]
        if data["next_page_token"] == None:
            break
        else:
            params["page_token"] = data["next_page_token"]

    d = {}

    for ticker, data_frame in bars.items():
        ticker_df = pd.DataFrame(data_frame)
        ticker_df.rename(
            columns={
                "c": "close",
                "h": "high",
                "l": "low",
                "o": "open",
                "v": "volume",
                "t": "time",
            },
            inplace=True,
        )
        ticker_df["time"] = pd.to_datetime(ticker_df["time"])
        ticker_df.set_index("time", inplace=True)
        ticker_df.index = pd.DatetimeIndex(ticker_df.index).tz_convert(
            "America/New_York"
        )
        d[ticker] = ticker_df

    return d


def read_ticker_dataframe(
    one_df: pd.DataFrame, cashValue: float, verbose_run: bool
) -> Generator[tuple[int, date, float, float | None, float | None], None, None]:
    """Iterates through each row of a ticker's price DataFrame, yielding one tuple per day for the backtest loop.

    Args:
        one_df (pd.DataFrame): the data frame corresponding to the symbol from the tickers_dfs dictionary
        cashValue (float): Current available cash during the run
        verbose_run (bool): If True, prints daily backtest output

    Yields:
        Generator[tuple[ int, date, float, float | None, float | None ], None, None]: (day, date, closingPrice, average, openingPrice)
        `average` and `openingPrice` are None for days 1-2 (warm-up period, no prior average yet)
        from day 3 onward, `average` is the mean of all closing prices before the current day
    """

    listStorePreviousClosingPrices = []

    for day, row in enumerate(one_df.itertuples(), 1):
        date = cast(pd.Timestamp, row.Index).date()
        closingPrice = cast(float, row.close)
        openingPrice = cast(float, row.open)

        if day == 1:
            listStorePreviousClosingPrices.append(closingPrice)
            if verbose_run:
                print("Position sizing rule: 20% of available cash")
                print("Fixed bias points model: 0.05% of the execution price")
                print("Commission model: $0.005 per share (flat)\n")
                print(
                    f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: N/A | Action: NONE | Position: 0 | Cash: {cashValue} | Equity: {cashValue}"
                )
                print("\n")

            yield (day, date, closingPrice, None, None)

        elif day == 2:
            listStorePreviousClosingPrices.append(closingPrice)
            if verbose_run:
                print(
                    f"Day {day} | Date: {date} | Close: {closingPrice} | Avg: N/A | Action: NONE | Position: 0 | Cash: {cashValue} | Equity: {cashValue}"
                )
                print("\n")

            yield (day, date, closingPrice, None, None)

        else:
            average = cast(float, ca.averageUpToDay(listStorePreviousClosingPrices))
            listStorePreviousClosingPrices.append(closingPrice)
            yield (day, date, closingPrice, average, openingPrice)
