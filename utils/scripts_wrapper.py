"""
Wrapper module to integrate scripts folder functionality into Streamlit
Maintains original code while providing Streamlit-compatible interface
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .unified_data_fetcher import fetch_market_data

# Add scripts folder to path
scripts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
sys.path.insert(0, scripts_path)


def run_markov_regime_analysis(ticker: str, lookback_days: int, data_source: str = "alphavantage", api_key: str = None):
    """
    Run Markov Regime Switching analysis
    
    Args:
        ticker: Stock ticker symbol
        lookback_days: Number of days of historical data
        data_source: Data source ("alphavantage", "polygon", or "yfinance")
        api_key: API key for data source (required for alphavantage/polygon)
    
    Returns:
        dict with regime probabilities and analysis
    """
    try:
        from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
        
        # Fetch data using unified fetcher
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        # Use unified data fetcher with API support
        df = fetch_market_data(ticker, start_date, end_date, "1d", data_source, api_key)
        
        if df.empty:
            return {"error": f"No data available for {ticker}. Try different data source or check API key."}
        
        # Calculate log returns
        df['Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df = df.dropna()
        
        if len(df) < 50:
            return {"error": "Insufficient data for analysis"}
        
        # Fit Markov Switching Model (2 regimes)
        model = MarkovRegression(
            df['Returns'],
            k_regimes=2,
            trend='c',
            switching_variance=True
        )
        
        results = model.fit()
        
        # Get regime probabilities
        smoothed_probs = results.smoothed_marginal_probabilities
        
        # Determine which regime is "bull" (higher mean return)
        regime_means = results.params.groupby(level=0).mean()
        bull_regime = 0 if regime_means[0] > regime_means[1] else 1
        bear_regime = 1 - bull_regime
        
        # Current regime probability
        current_bull_prob = smoothed_probs.iloc[-1, bull_regime]
        current_bear_prob = smoothed_probs.iloc[-1, bear_regime]
        
        # Determine current regime
        if current_bull_prob > 0.7:
            current_regime = "Bull Market"
            confidence = current_bull_prob
        elif current_bear_prob > 0.7:
            current_regime = "Bear Market"
            confidence = current_bear_prob
        else:
            current_regime = "Transitional"
            confidence = max(current_bull_prob, current_bear_prob)
        
        return {
            "success": True,
            "ticker": ticker,
            "current_regime": current_regime,
            "confidence": confidence,
            "bull_probability": current_bull_prob,
            "bear_probability": current_bear_prob,
            "regime_probabilities": smoothed_probs,
            "model_results": results,
            "data": df
        }
        
    except Exception as e:
        return {"error": str(e)}


def run_johansen_cointegration(tickers: list, lookback_days: int = 252, data_source: str = "alphavantage", api_key: str = None):
    """
    Run Johansen Cointegration test on multiple tickers
    
    Args:
        tickers: List of ticker symbols
        lookback_days: Number of days of historical data
        data_source: Data source ("alphavantage", "polygon", or "yfinance")
        api_key: API key for data source (required for alphavantage/polygon)
    
    Returns:
        dict with cointegration results
    """
    try:
        from statsmodels.tsa.vector_ar.vecm import coint_johansen
        
        if len(tickers) < 2:
            return {"error": "Need at least 2 tickers for cointegration analysis"}
        
        # Fetch data for each ticker using unified fetcher
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        prices_dict = {}
        for ticker in tickers:
            try:
                df = fetch_market_data(ticker, start_date, end_date, "1d", data_source, api_key)
                if df.empty:
                    return {"error": f"No data available for {ticker}. Try different data source or check API key."}
                prices_dict[ticker] = df['Close']
            except Exception as e:
                return {"error": f"Error fetching data for {ticker}: {str(e)}"}
        
        prices = pd.DataFrame(prices_dict)
        prices = prices.dropna()
        
        if len(prices) < 50:
            return {"error": "Insufficient data for analysis"}
        
        # Run Johansen test
        result = coint_johansen(prices, det_order=0, k_ar_diff=1)
        
        # Extract results
        trace_stats = result.lr1
        critical_values = result.cvt
        
        # Find cointegrated pairs
        cointegrated_pairs = []
        for i in range(len(trace_stats)):
            if trace_stats[i] > critical_values[i, 1]:  # 5% significance
                cointegrated_pairs.append(i)
        
        return {
            "success": True,
            "tickers": tickers,
            "trace_statistics": trace_stats.tolist(),
            "critical_values_5pct": critical_values[:, 1].tolist(),
            "cointegrated_ranks": cointegrated_pairs,
            "eigenvectors": result.evec.tolist(),
            "data": prices
        }
        
    except Exception as e:
        return {"error": str(e)}


def get_alpaca_account_info(api_key: str, api_secret: str, paper: bool = True):
    """
    Get Alpaca account information
    
    Args:
        api_key: Alpaca API key
        api_secret: Alpaca API secret
        paper: Use paper trading (default True)
    
    Returns:
        dict with account information
    """
    try:
        from alpaca.trading.client import TradingClient
        
        if not api_key or not api_secret:
            return {"error": "API credentials required"}
        
        trading_client = TradingClient(api_key, api_secret, paper=paper)
        account = trading_client.get_account()
        
        return {
            "success": True,
            "account_id": account.id,
            "status": account.status,
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
            "equity": float(account.equity),
            "last_equity": float(account.last_equity),
            "multiplier": account.multiplier,
            "long_market_value": float(account.long_market_value),
            "short_market_value": float(account.short_market_value),
            "initial_margin": float(account.initial_margin),
            "maintenance_margin": float(account.maintenance_margin),
            "daytrade_count": account.daytrade_count,
            "pattern_day_trader": account.pattern_day_trader
        }
        
    except Exception as e:
        return {"error": str(e)}


def calculate_tail_reaper_signals(ticker: str, lookback_days: int = 90, z_threshold: float = 2.0, data_source: str = "alphavantage", api_key: str = None):
    """
    Calculate Tail Reaper mean reversion signals
    
    Args:
        ticker: Stock ticker symbol
        lookback_days: Number of days for analysis
        z_threshold: Z-score threshold for signals
        data_source: Data source ("alphavantage", "polygon", or "yfinance")
        api_key: API key for data source (required for alphavantage/polygon)
    
    Returns:
        dict with signals and analysis
    """
    try:
        # Fetch data using unified fetcher
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        df = fetch_market_data(ticker, start_date, end_date, "1d", data_source, api_key)
        
        if df.empty:
            return {"error": f"No data available for {ticker}. Try different data source or check API key."}
        
        # Calculate rolling statistics
        window = 20
        df['MA'] = df['Close'].rolling(window=window).mean()
        df['STD'] = df['Close'].rolling(window=window).std()
        df['Z_Score'] = (df['Close'] - df['MA']) / df['STD']
        
        df = df.dropna()
        
        # Current values
        current_price = df['Close'].iloc[-1]
        current_ma = df['MA'].iloc[-1]
        current_z = df['Z_Score'].iloc[-1]
        
        # Generate signal
        if current_z > z_threshold:
            signal = "SELL (Overbought)"
            signal_type = "short"
        elif current_z < -z_threshold:
            signal = "BUY (Oversold)"
            signal_type = "long"
        else:
            signal = "NEUTRAL"
            signal_type = "neutral"
        
        return {
            "success": True,
            "ticker": ticker,
            "current_price": current_price,
            "moving_average": current_ma,
            "z_score": current_z,
            "signal": signal,
            "signal_type": signal_type,
            "threshold": z_threshold,
            "data": df
        }
        
    except Exception as e:
        return {"error": str(e)}
