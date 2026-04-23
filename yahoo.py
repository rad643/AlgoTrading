import pandas as pd
import yfinance as yf 


# download GOOGL daily OHLCV data from Yahoo Finance
df_google=yf.download("GOOGL", start="2024-01-16", end="2026-01-12", rounding=True, multi_level_index=False)
# move Date from index into a regular column
df_google=df_google.reset_index()
# reorder columns to match data_loader.py expected format: Date,Open,High,Low,Close,Volume
df_google=df_google.reindex( columns=["Date", "Open", "High", "Low", "Close", "Volume"] )
# save to CSV with 3 decimal places, no row index
df_google.to_csv(path_or_buf="data/google.csv", float_format="%.3f", index=False)

# download MSFT daily OHLCV data from Yahoo Finance
df_microsoft=yf.download("MSFT", start="2024-01-16", end="2026-01-12", rounding=True, multi_level_index=False)
# move Date from index into a regular column
df_microsoft=df_microsoft.reset_index()
# reorder columns to match data_loader.py expected format: Date,Open,High,Low,Close,Volume
df_microsoft=df_microsoft.reindex( columns=["Date", "Open", "High", "Low", "Close", "Volume"] )
# save to CSV with 3 decimal places, no row index
df_microsoft.to_csv(path_or_buf="data/microsoft.csv", float_format="%.3f", index=False)