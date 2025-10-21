"""
Technical indicators and calculations
"""

import pandas as pd
import numpy as np
from scipy import stats
from dataclasses import dataclass


def calculate_slope(series: pd.Series) -> float:
    """
    Calculate the slope of a series using linear regression
    
    Args:
        series: Pandas Series of values
    
    Returns:
        Slope value (float)
    """
    # Check to see if less than two points were provided
    if len(series) < 2:
        return np.nan

    # Check to see if performing linear regression would cause a division by
    # zero error, including (1) *any* of the data points in the series being
    # NaN, or (2) *all* values in the series being equal
    if series.isna().any() or np.all(series == series.iloc[0]):
        return np.nan
    
    # Compute and return the slope for the input data points
    return stats.linregress(np.arange(0, len(series)), series).slope


@dataclass(frozen=True)
class StochasticRSIComputation:
    """Data schema for stochastic RSI computation results"""
    stoch_rsi: pd.Series
    k_line: pd.Series
    d_line: pd.Series


def stochastic_rsi(
        series: pd.Series,
        period: int = 14,
        k_smooth: int = 3,
        d_smooth: int = 3
) -> StochasticRSIComputation:
    """
    Calculate TradingView-compatible Stochastic RSI indicator
    
    Args:
        series: Price series (typically closing prices)
        period: RSI period (default 14)
        k_smooth: K-line smoothing period (default 3)
        d_smooth: D-line smoothing period (default 3)
    
    Returns:
        StochasticRSIComputation with stoch_rsi, k_line, and d_line
    """
    # Check to see if an invalid period value was supplied
    if period <= 0 or period >= len(series):
        raise ValueError(
            f"Period must be greater than 0 and less than the length of the "
            f"series (got period={period}, data length={len(series)})"
        )

    # Calculate the price changes between consecutive periods, dropping any NA rows
    delta = series.diff().dropna()

    # Initialize two series, one for price increases (ups) and another for
    # decreases (downs)
    ups = pd.Series(np.zeros(len(delta)), index=delta.index)
    downs = ups.copy()

    # Fill the ups with positive price changes and the downs with absolute
    # value of negative price changes
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = np.absolute(delta[delta < 0])

    # Set the first usable value as the average of the gains, removing the
    # first period minus one values that aren't used
    ups[ups.index[period - 1]] = np.mean(ups[:period])
    ups = ups.drop(ups.index[:period - 1])

    # Do the same for the downs, setting the first usable value as the average
    # of initial losses, removing any values that were not computed for a full
    # period worth of data
    downs[downs.index[period - 1]] = np.mean(downs[:period])
    downs = downs.drop(downs.index[:period - 1])

    # Compute the exponential moving average of the ups
    ups_ewm = ups.ewm(
        com=period - 1,
        min_periods=0,
        adjust=False,
        ignore_na=False
    ).mean()

    # Do the same for the downs
    downs_ewm = downs.ewm(
        com=period - 1,
        min_periods=0,
        adjust=False,
        ignore_na=False
    ).mean()

    # Compute the relative strength (RS) as the average gains divided by the
    # average losses, then construct the relative strength index (RSI) by
    # scaling RS to the range [0, 100]
    rs = ups_ewm / downs_ewm
    rsi = 100 - (100 / (1.0 + rs))

    # Compute the stochastic RSI values using min-max scaling across the period
    rsi_min = rsi.rolling(period).min()
    rsi_max = rsi.rolling(period).max()
    stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min)

    # Construct two smoothed values, including (1) the K-line, which is a
    # smoothing of the raw stochastic RSI values, and (2) the D-line which
    # is a smoothing of the K-line
    k_line = stoch_rsi.rolling(k_smooth).mean()
    d_line = k_line.rolling(d_smooth).mean()

    # Construct and return the stochastic RSI values
    return StochasticRSIComputation(
        stoch_rsi=stoch_rsi,
        k_line=k_line,
        d_line=d_line
    )
