import numpy as np
import pandas as pd
import pytz
import yaml
from datetime import datetime, timedelta
from statsmodels.tsa.vector_ar.vecm import coint_johansen

from alpaca.trading.client import TradingClient
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame


def analyze_cointegration(symbols, k=2.5, lookback=60):
    """
    Fetches historical data for the given symbols from Alpaca, 
    performs the Johansen cointegration test, computes the spread, 
    and calculates the current Z-score. 

    Parameters:
    -----------
    symbols : list of str
        List of ticker symbols to analyze.
    k : float, optional
        Multiplier for standard deviation bands when computing the Z-score. Default is 2.5.
    lookback : int, optional
        Rolling window size for mean and std calculations. Default is 60.

    Returns:
    --------
    current_spread : float
        The most recent value of the spread.
    current_z : float
        The most recent Z-score of the spread.
    beta_vector : np.ndarray
        The first cointegration vector from the Johansen test.
    is_cointegrated : bool
        True if the set is cointegrated at the 95% confidence level, False otherwise.
    """

    # Load config
    config_path = r"C:\Users\Oskar\OneDrive\strategytrader\trader\config\config.yaml.txt"
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    # Alpaca credentials
    API_KEY = config['alpaca']['api_key']
    API_SECRET = config['alpaca']['api_secret']

    # Initialize clients
    trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
    data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

    # Choose a sufficiently long time period to establish cointegration
    days_to_fetch = 252 * 7  # ~7 years
    recent_start_date = datetime.now(pytz.UTC) - timedelta(days=days_to_fetch)
    recent_end_date = datetime.now(pytz.UTC)

    request_params = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Day,
        start=recent_start_date,
        end=recent_end_date,
        feed='iex'
    )

    bars = data_client.get_stock_bars(request_params).df
    close_prices = bars[['close']].unstack(level='symbol')
    close_prices.columns = close_prices.columns.droplevel(0)

    close_prices = close_prices.sort_index().dropna()

    # Perform the Johansen cointegration test
    result = coint_johansen(close_prices, det_order=1, k_ar_diff=2)
    beta_vector = result.evec[:, 0]

    # Determine cointegration at 95% level
    rank = 0
    for i in range(len(result.lr1)):
        if result.lr1[i] > result.cvt[i, 0]:  # Compare trace stat to 95% CV
            rank = i + 1

    is_cointegrated = rank > 0

    # Compute the spread using the first beta vector
    spread = pd.Series(np.dot(close_prices, beta_vector), index=close_prices.index)

    # Compute rolling stats
    rolling_mean = spread.rolling(lookback).mean()
    rolling_std = spread.rolling(lookback).std()

    # Compute z-score of the spread
    z_spread = (spread - rolling_mean) / rolling_std

    # Current values
    current_spread = spread.iloc[-1]
    current_z = z_spread.iloc[-1]

    return current_spread, current_z, beta_vector, is_cointegrated

