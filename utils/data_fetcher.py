"""
Data fetching utilities for market data
"""

import pandas as pd
import yfinance as yf
from datetime import datetime


def fetch_ohlcv_history(
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        interval: str,
        debug: bool = False
) -> pd.DataFrame:
    """
    Download OHLCV market data for a ticker - returns simple DataFrame
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date for historical data
        end_date: End date for historical data
        interval: Data interval (1d, 1wk, 1mo, etc.)
        debug: If True, print debug information
    
    Returns:
        DataFrame with OHLCV columns and Date index
    """
    try:
        # Download the OHLCV market data for the ticker
        df = yf.download(
            tickers=ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            auto_adjust=True,
            progress=False
        )
        
        if debug:
            print(f"fetch_ohlcv_history: Downloaded {len(df)} rows for {ticker}")
            print(f"Columns: {df.columns.tolist()}")
        
        # For single ticker, yfinance returns a simple DataFrame
        # Just ensure we have the right columns
        if not df.empty:
            # Make sure we have standard column names
            expected_cols = ["Open", "High", "Low", "Close", "Volume"]
            # Check if all expected columns exist
            available_cols = [col for col in expected_cols if col in df.columns]
            if len(available_cols) == len(expected_cols):
                df = df[expected_cols]
            else:
                if debug:
                    print(f"Warning: Missing columns. Available: {df.columns.tolist()}")
        
        return df
    except Exception as e:
        if debug:
            print(f"Error in fetch_ohlcv_history: {str(e)}")
        return pd.DataFrame()
