import datetime

import pytest

from strategies.trend import utils


def test_pending_action_update():

    closingPrice = 10
    average = 5
    assert utils.pending_action_update(closingPrice, average) == "BUY"

    closingPrice = 4
    assert utils.pending_action_update(closingPrice, average) == "SELL"

    closingPrice = 5
    assert utils.pending_action_update(closingPrice, average) == "HOLD"


def test_buy(capsys):

    day = 47
    cashValue = 12000
    nextDayOpeningPrice = 212.40
    fixed_bps = 0.0005
    positionSizing = 2400
    flat_fee_per_share = 0.005
    fixed_bps = 0.0005
    positionSizing = 2400
    flat_fee_per_share = 0.005
    closingPrice = 218.75
    verbose_run = False
    date = datetime.date(2025, 9, 3)
    average = 205.30

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
    ) == (212.506, 11.0, 9662.379, 12068.629, 47, "BUY")

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

    expected = "Day 47 | Date: 2025-09-03 | Close: 218.75 | Execution price: 212.506 | Avg: 205.300 | Trend: BUY | Position: 11.0 | Cash: 9662.379 | Equity: 12068.629\n\n\n"

    assert output == expected


def test_sell(capsys):

    day = 63
    cashValue = 9662.379
    nextDayOpeningPrice = 243.10
    fixed_bps = 0.0005
    entryPriceTrend = 212.506
    closingPrice = 239.85
    flat_fee_per_share = 0.005
    verbose_run = False
    date = datetime.date(2025, 9, 24)
    average = 228.40
    positionTrend = 11.0

    assert utils.sell(
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
    ) == (242.978, 0, 12335.082, 12335.082, 335.192, 63, "BUY")

    verbose_run = True

    utils.sell(
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

    captured = capsys.readouterr()

    output = captured.out

    expected = "Day 63 | Date: 2025-09-24 | Close: 239.85 | Execution price: 242.978 | Avg: 228.400 | Trend: BUY | Position: 0 | Cash: 12335.082 | Equity: 12335.082 | P&L: 335.192\n\n\n"

    assert expected == output


def test_hold(capsys):

    cashValue = 7418.62
    positionTrend = 9.0
    closingPrice = 251.30
    verbose_run = False
    day = 78
    date = datetime.date(2025, 10, 15)
    average = 244.05

    assert utils.hold(
        cashValue, positionTrend, closingPrice, verbose_run, day, date, average
    ) == (9.0, 7418.62, 9680.32, "BUY")

    verbose_run = True

    utils.hold(cashValue, positionTrend, closingPrice, verbose_run, day, date, average)

    captured = capsys.readouterr()

    output = captured.out

    expected = "Day 78 | Date: 2025-10-15 | Close: 251.3 | Avg: 244.050 | Trend: BUY | Position: 9.0 | Cash: 7418.62 | Equity: 9680.32\n\n\n"

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
