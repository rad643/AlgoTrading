import datetime
from unittest.mock import call, patch

from strategies.mean_reversion import signal


def test_mean_rev_step_buy_branch():
    verbose_run = False
    day = 61
    date = datetime.date(2025, 4, 9)
    closingPrice = 198.40
    average = 207.15
    nextDayOpeningPrice = 201.34
    cashValue = 11000
    equity = 13200
    pending_action = "BUY"
    positionSizing = 2800
    flat_fee_per_share = 0.005
    fixed_bps = 0.0005
    positionMeanReversion = 0
    entry_day = 77
    exit_day = 93
    entryPriceMeanReversion = 193.80
    exitPriceMeanReversion = 221.45
    profitMeanReversion = 412.66

    with (
        patch.object(signal, "buy", autospec=True) as mock_buy,
        patch.object(signal, "sell", autospec=True) as mock_sell,
        patch.object(signal, "hold", autospec=True) as mock_hold,
    ):
        mock_buy.return_value = (201.44, 14.0, 7188.32, 9954.06, 19, "SELL")

        expected = (14.0, 412.66, 201.44, 221.45, 7188.32, 9954.06, "SELL", 19, 93)

        actual = signal.mean_rev_step(
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
            positionMeanReversion,
            entry_day,
            exit_day,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
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


def test_mean_rev_step_sell_branch():
    verbose_run = False
    day = 61
    date = datetime.date(2025, 4, 9)
    closingPrice = 198.40
    average = 207.15
    nextDayOpeningPrice = 201.34
    cashValue = 11000
    equity = 13200
    pending_action = "SELL"
    positionSizing = 2800
    flat_fee_per_share = 0.005
    fixed_bps = 0.0005
    positionMeanReversion = 9
    entry_day = 77
    exit_day = 93
    entryPriceMeanReversion = 193.80
    exitPriceMeanReversion = 221.45
    profitMeanReversion = 412.66

    with (
        patch.object(signal, "buy", autospec=True) as mock_buy,
        patch.object(signal, "sell", autospec=True) as mock_sell,
        patch.object(signal, "hold", autospec=True) as mock_hold,
    ):
        mock_sell.return_value = (228.91, 4.0, 10422.77, 11530.55, 655.20, 84, "BUY")

        expected = (4.0, 655.20, 193.80, 228.91, 10422.77, 11530.55, "BUY", 77, 84)

        actual = signal.mean_rev_step(
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
            positionMeanReversion,
            entry_day,
            exit_day,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )

        mock_sell.assert_called_once_with(
            day,
            cashValue,
            nextDayOpeningPrice,
            fixed_bps,
            entryPriceMeanReversion,
            closingPrice,
            flat_fee_per_share,
            verbose_run,
            date,
            average,
            positionMeanReversion,
        )

        mock_buy.assert_not_called()
        mock_hold.assert_not_called()

        assert expected == actual


def test_mean_rev_step_hold_branch():
    verbose_run = False
    day = 61
    date = datetime.date(2025, 4, 9)
    closingPrice = 198.40
    average = 207.15
    nextDayOpeningPrice = 201.34
    cashValue = 11000
    equity = 13200
    pending_action = "BUY"
    positionSizing = 2800
    flat_fee_per_share = 0.005
    fixed_bps = 0.0005
    positionMeanReversion = 12
    entry_day = 77
    exit_day = 93
    entryPriceMeanReversion = 193.80
    exitPriceMeanReversion = 221.45
    profitMeanReversion = 412.66

    with (
        patch.object(signal, "buy", autospec=True) as mock_buy,
        patch.object(signal, "sell", autospec=True) as mock_sell,
        patch.object(signal, "hold", autospec=True) as mock_hold,
    ):
        # BUY signal but a position is already open -> hold
        mock_hold.return_value = (12.0, 5600.10, 7980.90, "HOLD")

        expected = (
            12.0,
            412.66,
            193.80,
            221.45,
            5600.10,
            7980.90,
            "HOLD",
            77,
            93,
        )

        actual = signal.mean_rev_step(
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
            positionMeanReversion,
            entry_day,
            exit_day,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )

        mock_hold.assert_called_once_with(
            cashValue,
            positionMeanReversion,
            closingPrice,
            verbose_run,
            day,
            date,
            average,
        )
        mock_buy.assert_not_called()
        mock_sell.assert_not_called()

        assert expected == actual

        # SELL signal but nothing is held -> hold
        pending_action = "SELL"
        positionMeanReversion = 0

        mock_hold.return_value = (0, 6100.25, 6100.25, "HOLD")

        expected = (
            0,
            412.66,
            193.80,
            221.45,
            6100.25,
            6100.25,
            "HOLD",
            77,
            93,
        )

        actual = signal.mean_rev_step(
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
            positionMeanReversion,
            entry_day,
            exit_day,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )

        assert mock_hold.call_args_list == [
            call(11000, 12, 198.40, False, 61, datetime.date(2025, 4, 9), 207.15),
            call(11000, 0, 198.40, False, 61, datetime.date(2025, 4, 9), 207.15),
        ]
        mock_buy.assert_not_called()
        mock_sell.assert_not_called()

        assert expected == actual

        # explicit HOLD signal
        pending_action = "HOLD"
        positionMeanReversion = 6

        mock_hold.return_value = (6.0, 4900.00, 6100.00, "HOLD")

        expected = (
            6.0,
            412.66,
            193.80,
            221.45,
            4900.00,
            6100.00,
            "HOLD",
            77,
            93,
        )

        actual = signal.mean_rev_step(
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
            positionMeanReversion,
            entry_day,
            exit_day,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )

        assert mock_hold.call_args_list == [
            call(11000, 12, 198.40, False, 61, datetime.date(2025, 4, 9), 207.15),
            call(11000, 0, 198.40, False, 61, datetime.date(2025, 4, 9), 207.15),
            call(11000, 6, 198.40, False, 61, datetime.date(2025, 4, 9), 207.15),
        ]
        mock_buy.assert_not_called()
        mock_sell.assert_not_called()

        assert expected == actual

        # empty signal (warm-up state) -> hold
        pending_action = ""

        mock_hold.return_value = (6.0, 4900.00, 6100.00, "")

        expected = (
            6.0,
            412.66,
            193.80,
            221.45,
            4900.00,
            6100.00,
            "",
            77,
            93,
        )

        actual = signal.mean_rev_step(
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
            positionMeanReversion,
            entry_day,
            exit_day,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )

        assert mock_hold.call_args_list == [
            call(11000, 12, 198.40, False, 61, datetime.date(2025, 4, 9), 207.15),
            call(11000, 0, 198.40, False, 61, datetime.date(2025, 4, 9), 207.15),
            call(11000, 6, 198.40, False, 61, datetime.date(2025, 4, 9), 207.15),
            call(11000, 6, 198.40, False, 61, datetime.date(2025, 4, 9), 207.15),
        ]
        mock_buy.assert_not_called()
        mock_sell.assert_not_called()

        assert expected == actual
