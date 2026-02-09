import process_1_day as pd

def test_process_1_day()->None:
    
    trend=True
    if(trend):
        #for trend: day,date,closingPrice,average,positionTrend, entryPriceTrend, exitPriceTrend, profitTrend
        #day,date,closingPrice,average,trendMethod,positionTrend, entryPriceTrend, exitPriceTrend, profitTrend, positionMeanReversion, entryPriceMeanReversion,exitPriceMeanReversion, profitMeanReversion
        assert pd.process_one_day(4, "2026-05-04", 47, 46.17, True, 1, 48, 47.5, 0, 0, 44, 45.8, 0)==(1, 0, 48, 47.5)
    else:
        assert pd.process_one_day(4, "2026-05-04", 47, 46.17, False, 1, 48, 47.5, 0, 0, 44, 45.8, 0)==(0, 0, 44, 45.8)

test_process_1_day()