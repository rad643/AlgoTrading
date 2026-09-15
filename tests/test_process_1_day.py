import datetime
from unittest.mock import patch

import pytest

from engine import process_1_day


def test_process_one_day_trend_branch():

    with patch.object(process_1_day, "trend_signal", autospec=True) as mock_trend:
        verbose_run = False
        day = 5
        date = datetime.date(2025, 2, 21)
        closingPrice = 344.6
        average = 325.67
        nextDayOpeningPrice = 375.23
        cashValue = 8900
        equity = 11000
        pending_action = "BUY"
        positionSizing = 0.2
        flat_fee_per_share = 0.005
        fixed_bps = 0.0005
        positionTrend = 10
        entry_day = 200
        exit_day = 220
        entryPriceTrend = 330.12
        exitPriceTrend = 332.12
        profitTrend = 154.6
        positionMeanReversion = 13
        entryPriceMeanReversion = 431.2
        exitPriceMeanReversion = 433.5
        profitMeanReversion = 220.5
        trendMethod = True

        mock_trend.trend_step.return_value = (
            10,
            154.6,
            330.12,
            332.12,
            8900,
            12346.0,
            "BUY",
            200,
            220,
        )

        process_1_day.process_one_day(
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
            trendMethod,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
            positionMeanReversion,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )

        mock_trend.trend_step.assert_called_once_with(
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


def test_process_one_day_mean_reversion_branch():

    with patch.object(
        process_1_day, "mean_reversion_signal", autospec=True
    ) as mock_mean_rev:
        verbose_run = False
        day = 5
        date = datetime.date(2025, 2, 21)
        closingPrice = 344.6
        average = 325.67
        nextDayOpeningPrice = 375.23
        cashValue = 8900
        equity = 11000
        pending_action = "BUY"
        positionSizing = 0.2
        flat_fee_per_share = 0.005
        fixed_bps = 0.0005
        positionTrend = 10
        entry_day = 200
        exit_day = 220
        entryPriceTrend = 330.12
        exitPriceTrend = 332.12
        profitTrend = 154.6
        positionMeanReversion = 13
        entryPriceMeanReversion = 431.2
        exitPriceMeanReversion = 433.5
        profitMeanReversion = 220.5
        trendMethod = False

        mock_mean_rev.mean_rev_step.return_value = (
            13,
            220.5,
            431.2,
            433.5,
            8900,
            13379.8,
            "SELL",
            200,
            220,
        )

        process_1_day.process_one_day(
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
            trendMethod,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
            positionMeanReversion,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )

        mock_mean_rev.mean_rev_step.assert_called_once_with(
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


def test_process_one_day_errors():

    verbose_run = False
    day = 5
    date = datetime.date(2025, 2, 21)
    closingPrice = 344.6
    average = 325.67
    nextDayOpeningPrice = 375.23
    cashValue = 8900
    equity = 11000
    pending_action = []
    positionSizing = 0.2
    flat_fee_per_share = 0.005
    fixed_bps = 0.0005
    positionTrend = 10
    entry_day = 200
    exit_day = 220
    entryPriceTrend = 330.12
    exitPriceTrend = 332.12
    profitTrend = 154.6
    positionMeanReversion = 13
    entryPriceMeanReversion = 431.2
    exitPriceMeanReversion = 433.5
    profitMeanReversion = 220.5
    trendMethod = False

    with pytest.raises(TypeError):
        process_1_day.process_one_day(
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
            trendMethod,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
            positionMeanReversion,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )

    pending_action = "Wrong"

    with pytest.raises(ValueError):
        process_1_day.process_one_day(
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
            trendMethod,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
            positionMeanReversion,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )

    trendMethod = 25
    pending_action = ""

    with pytest.raises(TypeError):
        process_1_day.process_one_day(
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
            trendMethod,
            positionTrend,
            entry_day,
            exit_day,
            entryPriceTrend,
            exitPriceTrend,
            profitTrend,
            positionMeanReversion,
            entryPriceMeanReversion,
            exitPriceMeanReversion,
            profitMeanReversion,
        )
