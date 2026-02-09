import trend_signal as ts

def test_trend_signal():
    #day  ,  date ,    closingPrice ,  average , positionTrend.  ,  entryPriceTrend.   ,  exitPriceTrend.   , profitTrend:float
    assert ts.trend_step(8, "2026-05-08", 47.4, 48.8, 1, 49.2, 47.4, 0.0)==(1, -1.8, 49.2, 47.4)

test_trend_signal()