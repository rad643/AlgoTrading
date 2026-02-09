import mean_rev_signal as mrv

def test_mean_rev_signal():
    #day  ,  date ,    closingPrice ,  average , positionMeanReversion  ,  entryPriceMeanReversion   ,  exitPriceMeanReversion   , profitMeanReversion
    assert mrv.mean_rev_step(9, "2026-05-09",48.5, 48.5, 0, 0.0, 0.0, 0.0)==(0, 0.5, 0.0, 0.0)

test_mean_rev_signal()