"""
Unified data fetcher that supports multiple data sources
"""

import pandas as pd
import yfinance as yf
import requests
from datetime import datetime
from typing import Optional


def fetch_market_data(
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
        data_source: str = "yfinance",
        api_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Unified function to fetch market data from multiple sources
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date for historical data
        end_date: End date for historical data
        interval: Data interval (1d, 1wk, 1mo)
        data_source: "yfinance", "alphavantage", or "polygon"
        api_key: API key for Alpha Vantage or Polygon (optional for yfinance)
    
    Returns:
        DataFrame with OHLCV columns and Date index
    """
    
    if data_source == "yfinance":
        return _fetch_yfinance(ticker, start_date, end_date, interval)
    elif data_source == "alphavantage":
        return _fetch_alphavantage(ticker, start_date, end_date, interval, api_key)
    elif data_source == "polygon":
        return _fetch_polygon(ticker, start_date, end_date, interval, api_key)
    else:
        raise ValueError(f"Unknown data source: {data_source}")


def _fetch_yfinance(ticker: str, start_date: datetime, end_date: datetime, interval: str) -> pd.DataFrame:
    """Fetch data from Yahoo Finance"""
    try:
        df = yf.download(
            tickers=ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            auto_adjust=True,
            progress=False
        )
        
        if not df.empty and "Close" in df.columns:
            expected_cols = ["Open", "High", "Low", "Close", "Volume"]
            available_cols = [col for col in expected_cols if col in df.columns]
            if len(available_cols) == len(expected_cols):
                df = df[expected_cols]
        
        return df
    except Exception as e:
        print(f"yfinance error: {str(e)}")
        return pd.DataFrame()


def _fetch_alphavantage(ticker: str, start_date: datetime, end_date: datetime, interval: str, api_key: str) -> pd.DataFrame:
    """Fetch data from Alpha Vantage API"""
    try:
        if not api_key:
            api_key = "demo"
        
        # Map interval to Alpha Vantage function
        if interval == "1d":
            function = "TIME_SERIES_DAILY"
            time_key = "Time Series (Daily)"
        elif interval == "1wk":
            function = "TIME_SERIES_WEEKLY"
            time_key = "Weekly Time Series"
        else:  # 1mo
            function = "TIME_SERIES_MONTHLY"
            time_key = "Monthly Time Series"
        
        url = f"https://www.alphavantage.co/query?function={function}&symbol={ticker}&apikey={api_key}&outputsize=full"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if time_key in data:
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data[time_key], orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns to match standard format
            column_mapping = {
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            }
            df = df.rename(columns=column_mapping)
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df = df.astype(float)
            
            # Filter by date range
            df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]
            
            return df
        else:
            print(f"Alpha Vantage error: {data.get('Note', data.get('Error Message', 'Unknown error'))}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Alpha Vantage exception: {str(e)}")
        return pd.DataFrame()


def _fetch_polygon(ticker: str, start_date: datetime, end_date: datetime, interval: str, api_key: str) -> pd.DataFrame:
    """Fetch data from Polygon.io API"""
    try:
        if not api_key:
            return pd.DataFrame()
        
        # Map interval
        multiplier = 1
        timespan = "day" if interval == "1d" else ("week" if interval == "1wk" else "month")
        
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}?apiKey={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("status") == "OK" and "results" in data:
            # Convert to DataFrame
            results = data["results"]
            df = pd.DataFrame(results)
            df['Date'] = pd.to_datetime(df['t'], unit='ms')
            df = df.set_index('Date')
            
            # Rename columns to match standard format
            df = df.rename(columns={
                'o': 'Open',
                'h': 'High',
                'l': 'Low',
                'c': 'Close',
                'v': 'Volume'
            })
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            return df
        else:
            print(f"Polygon error: {data.get('error', 'Unknown error')}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Polygon exception: {str(e)}")
        return pd.DataFrame()
