import datetime

import pytest

from strategies.mean_reversion import utils


def test_pending_action_update():
    closingPrice = 4
    average = 9
    assert utils.pending_action_update(closingPrice, average) == "BUY"

    closingPrice = 12
    assert utils.pending_action_update(closingPrice, average) == "SELL"

    closingPrice = 9
    assert utils.pending_action_update(closingPrice, average) == "HOLD"


def test_buy(capsys):
    day = 52
    cashValue = 15000
    nextDayOpeningPrice = 184.20
    fixed_bps = 0.0005
    positionSizing = 3000
    flat_fee_per_share = 0.005
    closingPrice = 179.40
    verbose_run = False
    date = datetime.date(2025, 7, 14)
    average = 188.75

    assert utils.buy(
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
    ) == (184.292, 16.0, 12051.248, 14921.648, 52, "BUY")

    verbose_run = True

    utils.buy(
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

    captured = capsys.readouterr()

    output = captured.out

    expected = "Day 52 | Date: 2025-07-14 | Close: 179.4 | Execution price: 184.292 | Avg: 188.750 | Mean Reversion: BUY | Position: 16.0 | Cash: 12051.248 | Equity: 14921.648\n\n\n"

    assert output == expected


def test_sell(capsys):
    day = 71
    cashValue = 12051.248
    nextDayOpeningPrice = 196.80
    fixed_bps = 0.0005
    entryPriceMeanReversion = 184.292
    closingPrice = 201.35
    flat_fee_per_share = 0.005
    verbose_run = False
    date = datetime.date(2025, 8, 6)
    average = 192.10
    positionMeanReversion = 16.0

    assert utils.sell(
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
    ) == (196.702, 0, 15198.4, 15198.4, 198.56, 71, "SELL")

    verbose_run = True

    utils.sell(
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

    captured = capsys.readouterr()

    output = captured.out

    expected = "Day 71 | Date: 2025-08-06 | Close: 201.35 | Execution price: 196.702 | Avg: 192.100 | Mean Reversion: SELL | Position: 0 | Cash: 15198.4 | Equity: 15198.4 | P&L: 198.560\n\n\n"

    assert expected == output


def test_hold(capsys):
    cashValue = 8320.55
    positionMeanReversion = 7.0
    closingPrice = 163.40
    verbose_run = False
    day = 88
    date = datetime.date(2025, 11, 4)
    average = 170.25

    assert utils.hold(
        cashValue, positionMeanReversion, closingPrice, verbose_run, day, date, average
    ) == (7.0, 8320.55, 9464.35, "BUY")

    verbose_run = True

    utils.hold(
        cashValue, positionMeanReversion, closingPrice, verbose_run, day, date, average
    )

    captured = capsys.readouterr()

    output = captured.out

    expected = "Day 88 | Date: 2025-11-04 | Close: 163.4 | Avg: 170.250 | Mean Reversion: BUY | Position: 7.0 | Cash: 8320.55 | Equity: 9464.35\n\n\n"

    assert expected == output


def test_validation():
    with pytest.raises(TypeError):
        utils.validation([], 1000)

    with pytest.raises(ValueError):
        utils.validation("error", 1000)

    with pytest.raises(TypeError):
        utils.validation("BUY", "string")

    with pytest.raises(ValueError):
        utils.validation("SELL", 0)

    with pytest.raises(ValueError):
        utils.validation("SELL", -10)
