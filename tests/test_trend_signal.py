import datetime
from unittest.mock import call, patch

from strategies.trend import signal


def test_trend_step_buy_branch():

    verbose_run = False
    day = 34
    date = datetime.date(2025, 6, 21)
    closingPrice = 344.6
    average = 357.7
    nextDayOpeningPrice = 359.76
    cashValue = 9500
    equity = 11500
    pending_action = "BUY"
    positionSizing = 2000
    flat_fee_per_share = 0.005
    fixed_bps = 0.0005
    positionTrend = 0
    entry_day = 431
    exit_day = 454
    entryPriceTrend = 444.6
    exitPriceTrend = 465.12
    profitTrend = 300.43

    with (
        patch.object(signal, "buy", autospec=True) as mock_buy,
        patch.object(signal, "sell", autospec=True) as mock_sell,
        patch.object(signal, "hold", autospec=True) as mock_hold,
    ):
        mock_buy.return_value = (188.25, 8.0, 5310.44, 6890.12, 27, "BUY")

        expected = (8.0, 300.43, 188.25, 465.12, 5310.44, 6890.12, "BUY", 27, 454)

        actual = signal.trend_step(
            verbose_run,
            day,
            date,
            closingPrice,
            average,
            nextDayOpeningPrice,
            cashValue,
            equity,
            pending_action,
            positionSizing,
            flat_fee_per_share,
            fixed_bps,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
        )

        mock_buy.assert_called_once_with(
            day,
            cashValue,
            nextDayOpeningPrice,
            fixed_bps,
            positionSizing,
            flat_fee_per_share,
            closingPrice,
            verbose_run,
            date,
            average,
        )

        mock_sell.assert_not_called()
        mock_hold.assert_not_called()

        assert expected == actual


def test_trend_step_sell_branch():

    verbose_run = False
    day = 34
    date = datetime.date(2025, 6, 21)
    closingPrice = 344.6
    average = 357.7
    nextDayOpeningPrice = 359.76
    cashValue = 9500
    equity = 11500
    pending_action = "SELL"
    positionSizing = 2000
    flat_fee_per_share = 0.005
    fixed_bps = 0.0005
    positionTrend = 12
    entry_day = 431
    exit_day = 454
    entryPriceTrend = 444.6
    exitPriceTrend = 465.12
    profitTrend = 300.43

    with (
        patch.object(signal, "buy", autospec=True) as mock_buy,
        patch.object(signal, "sell", autospec=True) as mock_sell,
        patch.object(signal, "hold", autospec=True) as mock_hold,
    ):
        mock_sell.return_value = (276.40, 3.0, 8671.19, 9705.99, 812.55, 52, "SELL")

        expected = (3.0, 812.55, 444.6, 276.40, 8671.19, 9705.99, "SELL", 431, 52)

        actual = signal.trend_step(
            verbose_run,
            day,
            date,
            closingPrice,
            average,
            nextDayOpeningPrice,
            cashValue,
            equity,
            pending_action,
            positionSizing,
            flat_fee_per_share,
            fixed_bps,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
        )

        mock_sell.assert_called_once_with(
            day,
            cashValue,
            nextDayOpeningPrice,
            fixed_bps,
            entryPriceTrend,
            closingPrice,
            flat_fee_per_share,
            verbose_run,
            date,
            average,
            positionTrend,
        )

        mock_buy.assert_not_called()
        mock_hold.assert_not_called()

        assert expected == actual


def test_trend_step_hold_branch():

    verbose_run = False
    day = 34
    date = datetime.date(2025, 6, 21)
    closingPrice = 344.6
    average = 357.7
    nextDayOpeningPrice = 359.76
    cashValue = 9500
    equity = 11500
    pending_action = "BUY"
    positionSizing = 2000
    flat_fee_per_share = 0.005
    fixed_bps = 0.0005
    positionTrend = 20
    entry_day = 431
    exit_day = 454
    entryPriceTrend = 444.6
    exitPriceTrend = 465.12
    profitTrend = 300.43

    with (
        patch.object(signal, "buy", autospec=True) as mock_buy,
        patch.object(signal, "sell", autospec=True) as mock_sell,
        patch.object(signal, "hold", autospec=True) as mock_hold,
    ):
        mock_hold.return_value = (6.0, 4128.73, 7395.28, "HOLD")

        expected = (6.0, 300.43, 444.6, 465.12, 4128.73, 7395.28, "HOLD", 431, 454)

        actual = signal.trend_step(
            verbose_run,
            day,
            date,
            closingPrice,
            average,
            nextDayOpeningPrice,
            cashValue,
            equity,
            pending_action,
            positionSizing,
            flat_fee_per_share,
            fixed_bps,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
        )

        mock_hold.assert_called_once_with(
            cashValue, positionTrend, closingPrice, verbose_run, day, date, average
        )
        mock_sell.assert_not_called()
        mock_buy.assert_not_called()

        assert expected == actual

        pending_action = "SELL"
        positionTrend = 0

        mock_hold.return_value = (8, 5245.73, 8945.28, "HOLD")
        expected = (8, 300.43, 444.6, 465.12, 5245.73, 8945.28, "HOLD", 431, 454)

        actual = signal.trend_step(
            verbose_run,
            day,
            date,
            closingPrice,
            average,
            nextDayOpeningPrice,
            cashValue,
            equity,
            pending_action,
            positionSizing,
            flat_fee_per_share,
            fixed_bps,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
        )

        assert mock_hold.call_args_list == [
            call(9500, 20, 344.6, False, 34, datetime.date(2025, 6, 21), 357.7),
            call(9500, 0, 344.6, False, 34, datetime.date(2025, 6, 21), 357.7),
        ]
        mock_sell.assert_not_called()
        mock_buy.assert_not_called()

        assert expected == actual

        pending_action = "HOLD"
        positionTrend = 15
        mock_hold.return_value = (5, 6000, 7000, "HOLD")
        expected = (5, 300.43, 444.6, 465.12, 6000, 7000, "HOLD", 431, 454)

        actual = signal.trend_step(
            verbose_run,
            day,
            date,
            closingPrice,
            average,
            nextDayOpeningPrice,
            cashValue,
            equity,
            pending_action,
            positionSizing,
            flat_fee_per_share,
            fixed_bps,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
        )

        assert mock_hold.call_args_list == [
            call(9500, 20, 344.6, False, 34, datetime.date(2025, 6, 21), 357.7),
            call(9500, 0, 344.6, False, 34, datetime.date(2025, 6, 21), 357.7),
            call(9500, 15, 344.6, False, 34, datetime.date(2025, 6, 21), 357.7),
        ]
        mock_sell.assert_not_called()
        mock_buy.assert_not_called()

        assert expected == actual

        pending_action = ""
        mock_hold.return_value = (5, 6000, 7000, "")
        expected = (5, 300.43, 444.6, 465.12, 6000, 7000, "", 431, 454)

        actual = signal.trend_step(
            verbose_run,
            day,
            date,
            closingPrice,
            average,
            nextDayOpeningPrice,
            cashValue,
            equity,
            pending_action,
            positionSizing,
            flat_fee_per_share,
            fixed_bps,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
        )

        assert mock_hold.call_args_list == [
            call(9500, 20, 344.6, False, 34, datetime.date(2025, 6, 21), 357.7),
            call(9500, 0, 344.6, False, 34, datetime.date(2025, 6, 21), 357.7),
            call(9500, 15, 344.6, False, 34, datetime.date(2025, 6, 21), 357.7),
            call(9500, 15, 344.6, False, 34, datetime.date(2025, 6, 21), 357.7),
        ]
        mock_sell.assert_not_called()
        mock_buy.assert_not_called()

        assert expected == actual
