from unittest.mock import Mock, call, patch

import numpy as np
import pandas as pd
import pytest
import requests

from data_loading import data_loader as dl
from main import selected_tickers


def test_get_headers(monkeypatch):
    """Pins the three behaviours of data_loader.get_headers().

    get_headers() reads two environment variables at call time and maps them
    onto Alpaca's HTTP header names. Note the two naming conventions:

        env var                 ->  header name
        APCA_API_KEY_ID         ->  APCA-API-KEY-ID
        APCA_API_SECRET_KEY     ->  APCA-API-SECRET-KEY

    It uses os.environ[] (rather than using os.get() ), a
    missing variable raises KeyError instead of returning None.

    monkeypatch is a built-in pytest fixture: setenv/delenv change the real
    environment and are undone automatically when the test ends. The changes
    accumulate during the test, so a var deleted earlier stays deleted until
    it is explicitly set again.
    """

    # --- happy path: both credentials present ---
    monkeypatch.setenv("APCA_API_KEY_ID", "1234")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "string")

    assert dl.get_headers()["APCA-API-KEY-ID"] == "1234"
    assert dl.get_headers()["APCA-API-SECRET-KEY"] == "string"
    # whole-dict comparison also pins the key set: no extra or missing headers
    assert dl.get_headers() == {
        "APCA-API-KEY-ID": "1234",
        "APCA-API-SECRET-KEY": "string",
    }

    # --- failure path 1: key id missing ---
    monkeypatch.delenv("APCA_API_KEY_ID")

    with pytest.raises(KeyError) as excinfo:
        # the subscript never runs; get_headers() itself raises while building
        # the dict, on the first missing env var it reaches
        dl.get_headers()["APCA-API-KEY-ID"]
    # excinfo proves *which* var was missing, not merely that something raised
    assert str(excinfo.value) == "'APCA_API_KEY_ID'"

    # --- failure path 2: secret key missing ---
    # the key id must be restored first, otherwise get_headers() raises on it
    # again and this branch is never reached
    monkeypatch.setenv("APCA_API_KEY_ID", "1234")
    monkeypatch.delenv("APCA_API_SECRET_KEY")

    with pytest.raises(KeyError) as excinfo:
        dl.get_headers()["APCA-API-SECRET-KEY"]
    # excinfo proves *which* var was missing, not merely that something raised
    assert str(excinfo.value) == "'APCA_API_SECRET_KEY'"


def test_hist_data_single_page():

    PAGE_1 = {
        "bars": {
            "AAPL": [
                {
                    "c": 318.92,
                    "h": 319.58,
                    "l": 318.25,
                    "o": 319.0,
                    "v": 103520,
                    "t": "2026-09-08T08:00:00Z",
                }
            ],
            "GOOGL": [
                {
                    "c": 336.71,
                    "h": 338.80,
                    "l": 336.53,
                    "o": 337.39,
                    "v": 129489,
                    "t": "2026-09-08T08:00:00Z",
                }
            ],
            "MSFT": [
                {
                    "c": 496.84,
                    "h": 498.10,
                    "l": 495.37,
                    "o": 497.59,
                    "v": 60638,
                    "t": "2026-09-08T08:00:00Z",
                }
            ],
        },
        "next_page_token": None,
    }

    with patch.object(dl, "requests", autospec=True) as mock_requests:
        mock_requests.get.return_value.json.return_value = PAGE_1

        expected = {
            "AAPL": pd.DataFrame(
                {
                    "close": [318.92],
                    "high": [319.58],
                    "low": [318.25],
                    "open": [319.00],
                    "volume": [103520],
                },
                index=pd.DatetimeIndex(
                    ["2026-09-08T08:00:00Z"], name="time"
                ).tz_convert("America/New_York"),
            ),
            "GOOGL": pd.DataFrame(
                {
                    "close": [336.71],
                    "high": [338.80],
                    "low": [336.53],
                    "open": [337.39],
                    "volume": [129489],
                },
                index=pd.DatetimeIndex(
                    ["2026-09-08T08:00:00Z"], name="time"
                ).tz_convert("America/New_York"),
            ),
            "MSFT": pd.DataFrame(
                {
                    "close": [496.84],
                    "high": [498.10],
                    "low": [495.37],
                    "open": [497.59],
                    "volume": [60638],
                },
                index=pd.DatetimeIndex(
                    ["2026-09-08T08:00:00Z"], name="time"
                ).tz_convert("America/New_York"),
            ),
        }

        timeframe = "15Min"
        start = ""
        end = ""
        limit = 1000

        actual = dl.hist_data(selected_tickers, timeframe, start, end, limit)

        for ticker in actual:
            pd.testing.assert_frame_equal(actual[ticker], expected[ticker])

        params = {
            "symbols": selected_tickers,
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": limit,
        }

        mock_requests.get.assert_called_once_with(
            url=dl.url_path, headers=dl.get_headers(), params=params
        )


def test_hist_data_multiple_pages():

    PAGE_1 = {
        "bars": {
            "AAPL": [
                {
                    "c": 318.92,
                    "h": 319.58,
                    "l": 318.25,
                    "o": 319.0,
                    "v": 103520,
                    "t": "2026-09-08T08:00:00Z",
                }
            ],
            "GOOGL": [
                {
                    "c": 336.71,
                    "h": 338.80,
                    "l": 336.53,
                    "o": 337.39,
                    "v": 129489,
                    "t": "2026-09-08T08:00:00Z",
                }
            ],
            "MSFT": [
                {
                    "c": 496.84,
                    "h": 498.10,
                    "l": 495.37,
                    "o": 497.59,
                    "v": 60638,
                    "t": "2026-09-08T08:00:00Z",
                }
            ],
        },
        "next_page_token": "TOKEN_PAGE_2",
    }

    PAGE_2 = {
        "bars": {
            "AAPL": [
                {
                    "c": 318.50,
                    "h": 318.81,
                    "l": 318.49,
                    "o": 318.73,
                    "v": 10669,
                    "t": "2026-09-08T08:15:00Z",
                }
            ],
            "GOOGL": [
                {
                    "c": 336.85,
                    "h": 337.00,
                    "l": 336.52,
                    "o": 336.82,
                    "v": 8624,
                    "t": "2026-09-08T08:15:00Z",
                }
            ],
            "MSFT": [
                {
                    "c": 496.60,
                    "h": 497.14,
                    "l": 496.47,
                    "o": 497.14,
                    "v": 2992,
                    "t": "2026-09-08T08:15:00Z",
                }
            ],
        },
        "next_page_token": None,
    }

    with patch.object(dl, "requests", autospec=True) as mock_requests:
        lst = []

        def side_effect(*args, **kwargs):
            lst.append(dict(kwargs.get("params")))
            return mock_requests.get.return_value

        mock_requests.get.side_effect = side_effect

        mock_requests.get.return_value.json.side_effect = [PAGE_1, PAGE_2]

        expected = {
            "AAPL": pd.DataFrame(
                {
                    "close": [318.92, 318.50],
                    "high": [319.58, 318.81],
                    "low": [318.25, 318.49],
                    "open": [319.00, 318.73],
                    "volume": [103520, 10669],
                },
                index=pd.DatetimeIndex(
                    ["2026-09-08T08:00:00Z", "2026-09-08T08:15:00Z"], name="time"
                ).tz_convert("America/New_York"),
            ),
            "GOOGL": pd.DataFrame(
                {
                    "close": [336.71, 336.85],
                    "high": [338.80, 337.00],
                    "low": [336.53, 336.52],
                    "open": [337.39, 336.82],
                    "volume": [129489, 8624],
                },
                index=pd.DatetimeIndex(
                    ["2026-09-08T08:00:00Z", "2026-09-08T08:15:00Z"], name="time"
                ).tz_convert("America/New_York"),
            ),
            "MSFT": pd.DataFrame(
                {
                    "close": [496.84, 496.60],
                    "high": [498.10, 497.14],
                    "low": [495.37, 496.47],
                    "open": [497.59, 497.14],
                    "volume": [60638, 2992],
                },
                index=pd.DatetimeIndex(
                    ["2026-09-08T08:00:00Z", "2026-09-08T08:15:00Z"], name="time"
                ).tz_convert("America/New_York"),
            ),
        }

        timeframe = "15Min"
        start = ""
        end = ""
        limit = 1000

        actual = dl.hist_data(selected_tickers, timeframe, start, end, limit)

        final_params = {
            "symbols": selected_tickers,
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": limit,
            "page_token": "TOKEN_PAGE_2",
        }

        for ticker in actual:
            pd.testing.assert_frame_equal(actual[ticker], expected[ticker])

        assert mock_requests.get.call_args_list == [
            call(url=dl.url_path, headers=dl.get_headers(), params=final_params),
            call(url=dl.url_path, headers=dl.get_headers(), params=final_params),
        ]

        assert lst[0] == {
            "symbols": selected_tickers,
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": limit,
        }
        assert lst[1] == {
            "symbols": selected_tickers,
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": limit,
            "page_token": "TOKEN_PAGE_2",
        }


def test_hist_data_mocked_error_body():

    with patch.object(dl, "requests", autospec=True) as mock_requests:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Bad Request"
        )
        mock_response.status_code = 400
        mock_requests.get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            dl.hist_data(
                selected_tickers, timeframe="15Min", start="", end="", limit=1000
            )


def test_read_ticker_dataframe_correct_output():

    apple_price_df = pd.DataFrame(
        {
            "close": [183.20, 182.87, 182.90, 183.00],
            "high": [184.38, 183.22, 183.11, 183.00],
            "low": [183.19, 182.83, 182.87, 182.76],
            "n": [989, 303, 552, 390],
            "open": [183.53, 183.22, 182.87, 182.88],
            "volume": [28293, 10950, 26616, 14111],
            "vw": [183.533394, 183.102701, 182.996462, 182.864072],
        },
        index=pd.DatetimeIndex(
            [
                "2024-01-16T09:00:00Z",
                "2024-01-16T09:15:00Z",
                "2024-01-16T09:30:00Z",
                "2024-01-16T09:45:00Z",
            ],
            name="time",
        ).tz_convert("America/New_York"),
    )

    expected = [
        (1, (pd.Timestamp(2024, 1, 16)).date(), 183.2, None, None),
        (2, (pd.Timestamp(2024, 1, 16)).date(), 182.87, None, None),
        (3, (pd.Timestamp(2024, 1, 16)).date(), 182.9, np.float64(183.035), 182.87),
        (4, (pd.Timestamp(2024, 1, 16)).date(), 183.0, np.float64(182.99), 182.88),
    ]

    cashValue = 10000
    verbose_run = False

    actual = list(dl.read_ticker_dataframe(apple_price_df, cashValue, verbose_run))

    assert expected[0] == actual[0]
    assert expected[1] == actual[1]
    assert expected[2] == actual[2]
    assert expected[3] == actual[3]


def test_read_ticker_dataframe_capsys(capsys):

    cashValue = 10000
    verbose_run = True

    apple_price_df = pd.DataFrame(
        {
            "close": [183.20, 182.87, 182.90, 183.00],
            "high": [184.38, 183.22, 183.11, 183.00],
            "low": [183.19, 182.83, 182.87, 182.76],
            "n": [989, 303, 552, 390],
            "open": [183.53, 183.22, 182.87, 182.88],
            "volume": [28293, 10950, 26616, 14111],
            "vw": [183.533394, 183.102701, 182.996462, 182.864072],
        },
        index=pd.DatetimeIndex(
            [
                "2024-01-16T09:00:00Z",
                "2024-01-16T09:15:00Z",
                "2024-01-16T09:30:00Z",
                "2024-01-16T09:45:00Z",
            ],
            name="time",
        ).tz_convert("America/New_York"),
    )

    list(dl.read_ticker_dataframe(apple_price_df, cashValue, verbose_run))

    captured = capsys.readouterr()

    output = captured.out

    expected = (
        "Position sizing rule: 20% of available cash\n"
        "Fixed bias points model: 0.05% of the execution price\n"
        "Commission model: $0.005 per share (flat)\n"
        "\n"
        "Day 1 | Date: 2024-01-16 | Close: 183.2 | Avg: N/A | Action: NONE | Position: 0 | Cash: 10000 | Equity: 10000\n"
        "\n"
        "\n"
        "Day 2 | Date: 2024-01-16 | Close: 182.87 | Avg: N/A | Action: NONE | Position: 0 | Cash: 10000 | Equity: 10000\n"
        "\n"
        "\n"
    )

    assert output == expected

    verbose_run = False

    list(dl.read_ticker_dataframe(apple_price_df, cashValue, verbose_run))

    output = capsys.readouterr().out

    assert output == ""


def test_read_ticker_dataframe_first_2_days():

    apple_price_df = pd.DataFrame(
        {
            "close": [183.20, 182.87],
            "high": [184.38, 183.22],
            "low": [183.19, 182.83],
            "n": [989, 303],
            "open": [183.53, 183.22],
            "volume": [28293, 10950],
            "vw": [183.533394, 183.102701],
        },
        index=pd.DatetimeIndex(
            [
                "2024-01-16T09:00:00Z",
                "2024-01-16T09:15:00Z",
            ],
            name="time",
        ).tz_convert("America/New_York"),
    )

    cashValue = 10000
    verbose_run = False

    actual = list(dl.read_ticker_dataframe(apple_price_df, cashValue, verbose_run))

    expected = [
        (1, pd.Timestamp(2024, 1, 16).date(), 183.2, None, None),
        (2, pd.Timestamp(2024, 1, 16).date(), 182.87, None, None),
    ]

    assert expected == actual


def test_read_ticker_dataframe_empty_df():

    apple_price_df = pd.DataFrame(
        {
            "close": [],
            "high": [],
            "low": [],
            "n": [],
            "open": [],
            "volume": [],
            "vw": [],
        },
        index=pd.DatetimeIndex([], name="time", tz="America/New_York"),
    )

    cashValue = 10000
    verbose_run = False

    assert list(dl.read_ticker_dataframe(apple_price_df, cashValue, verbose_run)) == []
