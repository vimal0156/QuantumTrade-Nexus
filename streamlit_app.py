"""
QuantumTrade Nexus - Advanced Trading Intelligence Platform
A comprehensive financial analysis toolkit combining multiple technical analysis tools
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt
from scipy import stats
from matplotlib import patches
import seaborn as sns

# Page configuration
st.set_page_config(
    page_title="QuantumTrade Nexus",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import utility functions
from utils.data_fetcher import fetch_ohlcv_history
from utils.unified_data_fetcher import fetch_market_data
from utils.indicators import calculate_slope, stochastic_rsi
from utils.risk_calculator import RiskRewardCalculator
from utils.stage_detector import StageDetector, plot_stage_detections
from utils.consecutive_integers import find_consecutive_integers
from utils.scripts_wrapper import (
    run_markov_regime_analysis,
    run_johansen_cointegration,
    get_alpaca_account_info,
    calculate_tail_reaper_signals
)

# Import strategy
from strategy.streamlit_quantumtrend import quantumtrend_page

# Sidebar navigation
st.sidebar.title("⚡ QuantumTrade Nexus")
st.sidebar.markdown("### *Advanced Trading Intelligence*")
st.sidebar.markdown("---")

# Global data source configuration
st.sidebar.subheader("🌐 Data Source")
global_data_source = st.sidebar.selectbox(
    "Select Data Provider",
    ["Yahoo Finance (Free)", "Alpha Vantage API", "Polygon.io API"],
    help="This will be used for all tools"
)

global_api_key = None
if "Alpha Vantage" in global_data_source:
    st.sidebar.info("Get free key: alphavantage.co")
    global_api_key = st.sidebar.text_input("API Key (or leave empty for demo)", type="password", key="global_av_key")
    if not global_api_key:
        global_api_key = "demo"
elif "Polygon" in global_data_source:
    st.sidebar.info("Get free key: polygon.io")
    global_api_key = st.sidebar.text_input("API Key", type="password", key="global_poly_key")

st.sidebar.markdown("---")

# Helper function to get data source
def get_data_source_params():
    """Get current data source and API key from global settings"""
    if "Yahoo" in global_data_source:
        return "yfinance", global_api_key
    elif "Alpha Vantage" in global_data_source:
        return "alphavantage", global_api_key
    else:
        return "polygon", global_api_key

page = st.sidebar.radio(
    "Select Tool",
    [
        "🏠 Home",
        "🔧 System Status",
        "📊 Market Data Explorer",
        "📉 Stock Charts",
        "📈 Moving Averages",
        "📐 Slope Analysis",
        "🎯 Market Stage Detection",
        "💰 Risk/Reward Calculator",
        "📊 Stochastic RSI",
        "🔢 Consecutive Integers",
        "--- ADVANCED TRADING ---",
        "🤖 Markov Regime Model",
        "📈 Johansen Cointegration",
        "🎯 Tail Reaper Strategy",
        "💼 Alpaca Account Info",
        "--- STRATEGIES ---",
        "🌊 QuantumTrend SwiftEdge"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("**QuantumTrade Nexus**\n\nNext-generation trading intelligence platform powered by advanced algorithms and real-time market analysis.")

# Main content area
if page == "🏠 Home":
    st.title("⚡ QuantumTrade Nexus")
    st.markdown("### *Advanced Trading Intelligence Platform*")
    
    st.markdown("""
    This application provides a comprehensive set of tools for technical analysis and trading:
    ### 🛠️ Available Tools:
    
    **📊 Market Analysis Tools:**
    1. **Market Data Explorer** - Download data from Yahoo Finance, Alpha Vantage, or Polygon.io
    2. **Stock Charts** - Interactive candlestick charts with volume
    3. **Moving Averages** - Calculate and visualize SMAs across different timeframes
    4. **Slope Analysis** - Compute trend slopes using linear regression
    5. **Market Stage Detection** - Identify Stan Weinstein's market stages
    6. **Stochastic RSI** - TradingView-compatible Stochastic RSI indicator
    
    **💰 Trading Tools:**
    7. **Risk/Reward Calculator** - Calculate position sizing and R-multiples
    8. **Consecutive Integers** - Utility for finding consecutive integer groups
    
    **🚀 Advanced Trading (Alpaca Integration):**
    9. **Markov Regime Model** - Detect market regime changes
    10. **Johansen Cointegration** - Find cointegrated pairs for pairs trading
    11. **Tail Reaper Strategy** - Automated mean reversion strategy
    12. **Alpaca Account Info** - View your trading account details
    
    **📊 Trading Strategies (NEW!):**
    13. **QuantumTrend SwiftEdge** - Adaptive trend-following with Supertrend, Keltner Channels & EMA
    
    #### 🚀 Getting Started:
    
    Select a tool from the sidebar to begin your analysis. Each tool provides interactive
    controls and real-time calculations based on your inputs.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tools", "15", "Active")
    with col2:
        st.metric("Data Source", "Yahoo Finance", "Real-time")
    with col3:
        st.metric("Status", "Online", "✅")

elif page == "🔧 System Status":
    st.title("🔧 System Status & Backend Verification")
    st.markdown("Check if all backend utilities are properly connected")
    
    st.subheader("📦 Module Import Status")
    
    modules_status = []
    
    # Test each import
    try:
        from utils.data_fetcher import fetch_ohlcv_history
        modules_status.append(("✅", "data_fetcher", "fetch_ohlcv_history", "OK"))
    except Exception as e:
        modules_status.append(("❌", "data_fetcher", "fetch_ohlcv_history", str(e)))
    
    try:
        from utils.indicators import calculate_slope, stochastic_rsi
        modules_status.append(("✅", "indicators", "calculate_slope", "OK"))
        modules_status.append(("✅", "indicators", "stochastic_rsi", "OK"))
    except Exception as e:
        modules_status.append(("❌", "indicators", "calculate_slope/stochastic_rsi", str(e)))
    
    try:
        from utils.risk_calculator import RiskRewardCalculator
        modules_status.append(("✅", "risk_calculator", "RiskRewardCalculator", "OK"))
    except Exception as e:
        modules_status.append(("❌", "risk_calculator", "RiskRewardCalculator", str(e)))
    
    try:
        from utils.stage_detector import StageDetector, plot_stage_detections
        modules_status.append(("✅", "stage_detector", "StageDetector", "OK"))
        modules_status.append(("✅", "stage_detector", "plot_stage_detections", "OK"))
    except Exception as e:
        modules_status.append(("❌", "stage_detector", "StageDetector/plot_stage_detections", str(e)))
    
    try:
        from utils.consecutive_integers import find_consecutive_integers
        modules_status.append(("✅", "consecutive_integers", "find_consecutive_integers", "OK"))
    except Exception as e:
        modules_status.append(("❌", "consecutive_integers", "find_consecutive_integers", str(e)))
    
    # Display status table
    df_status = pd.DataFrame(modules_status, columns=["Status", "Module", "Function", "Message"])
    st.dataframe(df_status, use_container_width=True)
    
    # Count successes
    success_count = sum(1 for s in modules_status if s[0] == "✅")
    total_count = len(modules_status)
    
    if success_count == total_count:
        st.success(f"✅ All {total_count} backend modules loaded successfully!")
    else:
        st.error(f"❌ {total_count - success_count} module(s) failed to load")
    
    st.markdown("---")
    
    st.subheader("🧪 Functional Tests")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test Slope Calculator"):
            try:
                test_series = pd.Series([1, 2, 3, 4, 5])
                result = calculate_slope(test_series)
                st.success(f"✅ Slope calculation works! Result: {result:.2f}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("Test Consecutive Integers"):
            try:
                test_array = [1, 2, 3, 5, 6, 7, 8]
                result = find_consecutive_integers(test_array, min_consec=3)
                st.success(f"✅ Consecutive integers works! Found: {result}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("Test Risk Calculator"):
            try:
                calc = RiskRewardCalculator(
                    total_account_value=10000,
                    entry_point=100,
                    stop_loss=95,
                    risk_rate=0.01
                )
                params = calc.get_risk_parameters()
                st.success(f"✅ Risk calculator works! Amount to risk: ${params.amount_to_risk:.2f}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col4:
        if st.button("Test yfinance Connection"):
            try:
                test_df = yf.download("AAPL", period="5d", progress=False)
                if not test_df.empty:
                    st.success(f"✅ yfinance works! Downloaded {len(test_df)} rows")
                else:
                    st.warning("⚠️ yfinance connected but no data returned")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    st.subheader("📊 Backend Usage Map")
    
    usage_map = {
        "Tool": [
            "Market Data Explorer",
            "Stock Charts",
            "Moving Averages",
            "Slope Analysis",
            "Market Stage Detection",
            "Risk/Reward Calculator",
            "Stochastic RSI",
            "Consecutive Integers"
        ],
        "Backend Module": [
            "yfinance + requests (APIs)",
            "yfinance + mplfinance",
            "fetch_ohlcv_history",
            "calculate_slope",
            "StageDetector + plot_stage_detections",
            "RiskRewardCalculator",
            "stochastic_rsi + fetch_ohlcv_history",
            "find_consecutive_integers"
        ],
        "Status": ["✅"] * 8
    }
    
    df_usage = pd.DataFrame(usage_map)
    st.dataframe(df_usage, use_container_width=True)
    
    st.info("""
    **Backend Architecture:**
    - All tools use utility functions from the `utils/` folder
    - Data fetching: `yfinance`, `requests` (for APIs), `fetch_ohlcv_history`
    - Indicators: `calculate_slope`, `stochastic_rsi`
    - Analysis: `StageDetector`, `RiskRewardCalculator`, `find_consecutive_integers`
    - Visualization: `matplotlib`, `mplfinance`, `plot_stage_detections`
    """)

elif page == "📊 Market Data Explorer":
    st.title("📊 Market Data Explorer")
    st.markdown("Download and explore market data from multiple sources")
    
    # Data source selection
    data_source = st.radio(
        "Select Data Source",
        ["Yahoo Finance (yfinance)", "Alpha Vantage API (Free)", "Polygon.io API (Free)"],
        horizontal=True,
        help="Yahoo Finance is free and doesn't require API key. Alpha Vantage and Polygon offer free tiers with API keys."
    )
    
    # API Key input for Alpha Vantage or Polygon
    api_key = None
    if "Alpha Vantage" in data_source:
        st.info("📝 Get your free API key at: https://www.alphavantage.co/support/#api-key")
        api_key = st.text_input("Alpha Vantage API Key (optional - demo key will be used if empty)", 
                                type="password",
                                help="Free tier: 25 requests/day")
        if not api_key:
            api_key = "demo"  # Alpha Vantage demo key
    elif "Polygon" in data_source:
        st.info("📝 Get your free API key at: https://polygon.io/")
        api_key = st.text_input("Polygon.io API Key", 
                                type="password",
                                help="Free tier: 5 API calls/minute")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "Yahoo Finance" in data_source:
            tickers_input = st.text_input("Enter ticker symbols (comma-separated)", "AAPL")
        else:
            tickers_input = st.text_input("Enter ticker symbol (single only for API sources)", "AAPL")
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    with col2:
        if "Yahoo Finance" in data_source:
            interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)
        else:
            interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0, 
                                   help="Note: API sources may have different interval support")
    
    col3, col4 = st.columns(2)
    
    with col3:
        days_back = st.number_input("Days of history", min_value=30, max_value=3650, value=365)
    
    with col4:
        end_date = st.date_input("End date", datetime.now())
    
    if st.button("Fetch Data", type="primary"):
        with st.spinner("Downloading market data..."):
            start_date = end_date - timedelta(days=days_back)
            
            try:
                # Yahoo Finance
                if "Yahoo Finance" in data_source:
                    if len(tickers) == 1:
                        df = yf.download(
                            tickers=tickers[0],
                            start=start_date,
                            end=end_date,
                            interval=interval,
                            auto_adjust=True,
                            progress=False
                        )
                    else:
                        df = yf.download(
                            tickers=tickers,
                            start=start_date,
                            end=end_date,
                            interval=interval,
                            group_by="ticker",
                            auto_adjust=True,
                            progress=False
                        )
                
                # Alpha Vantage API
                elif "Alpha Vantage" in data_source:
                    import requests
                    ticker = tickers[0]
                    
                    # Map interval to Alpha Vantage function
                    if interval == "1d":
                        function = "TIME_SERIES_DAILY"
                        time_key = "Time Series (Daily)"
                    else:
                        function = "TIME_SERIES_WEEKLY" if interval == "1wk" else "TIME_SERIES_MONTHLY"
                        time_key = f"Weekly Time Series" if interval == "1wk" else "Monthly Time Series"
                    
                    url = f"https://www.alphavantage.co/query?function={function}&symbol={ticker}&apikey={api_key}&outputsize=full"
                    response = requests.get(url)
                    data = response.json()
                    
                    if time_key in data:
                        # Convert to DataFrame
                        df = pd.DataFrame.from_dict(data[time_key], orient='index')
                        df.index = pd.to_datetime(df.index)
                        df = df.sort_index()
                        
                        # Rename columns to match yfinance format
                        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                        df = df.astype(float)
                        
                        # Filter by date range
                        df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]
                    else:
                        st.error(f"API Error: {data.get('Note', data.get('Error Message', 'Unknown error'))}")
                        df = pd.DataFrame()
                
                # Polygon.io API
                elif "Polygon" in data_source:
                    import requests
                    ticker = tickers[0]
                    
                    if not api_key:
                        st.error("Please provide a Polygon.io API key")
                        df = pd.DataFrame()
                    else:
                        # Map interval
                        multiplier = 1
                        timespan = "day" if interval == "1d" else ("week" if interval == "1wk" else "month")
                        
                        from_date = start_date.strftime("%Y-%m-%d")
                        to_date = end_date.strftime("%Y-%m-%d")
                        
                        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}?apiKey={api_key}"
                        response = requests.get(url)
                        data = response.json()
                        
                        if data.get("status") == "OK" and "results" in data:
                            # Convert to DataFrame
                            results = data["results"]
                            df = pd.DataFrame(results)
                            df['Date'] = pd.to_datetime(df['t'], unit='ms')
                            df = df.set_index('Date')
                            
                            # Rename columns to match yfinance format
                            df = df.rename(columns={
                                'o': 'Open',
                                'h': 'High',
                                'l': 'Low',
                                'c': 'Close',
                                'v': 'Volume'
                            })
                            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                        else:
                            st.error(f"API Error: {data.get('error', 'Unknown error')}")
                            df = pd.DataFrame()
                else:
                    df = pd.DataFrame()
                
                if df.empty or len(df) == 0:
                    st.error("No data available for the specified ticker(s) and date range.")
                else:
                    st.success(f"Successfully downloaded {len(df)} rows of data for {len(tickers)} ticker(s)")
                    
                    # Display data structure
                    st.subheader("Data Structure")
                    st.write(f"**Shape:** {df.shape}")
                    st.write(f"**Date Range:** {df.index[0]} to {df.index[-1]}")
                    
                    # Display data
                    st.subheader("Market Data")
                    st.dataframe(df.tail(20), use_container_width=True)
                    
                    # Plot closing prices
                    if len(tickers) > 1:
                        st.subheader("Closing Prices Comparison")
                        fig, ax = plt.subplots(figsize=(12, 6))
                        for ticker in tickers:
                            try:
                                if ticker in df.columns.get_level_values(0):
                                    ax.plot(df.index, df[ticker]["Close"], label=ticker, linewidth=2)
                            except:
                                pass
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Price ($)")
                        ax.set_title("Stock Closing Prices")
                        ax.legend()
                        ax.grid(alpha=0.3)
                        st.pyplot(fig)
                    else:
                        # Single ticker - df has simple column structure
                        st.subheader("Closing Price Chart")
                        fig, ax = plt.subplots(figsize=(12, 6))
                        ticker = tickers[0]
                        ax.plot(df.index, df["Close"], color="blue", linewidth=2)
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Price ($)")
                        ax.set_title(f"{ticker} Closing Price")
                        ax.grid(alpha=0.3)
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Show summary stats
                        st.subheader("Summary Statistics")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Latest Close", f"${df['Close'].iloc[-1]:.2f}")
                        with col2:
                            change = df['Close'].iloc[-1] - df['Close'].iloc[0]
                            pct = (change / df['Close'].iloc[0]) * 100
                            st.metric("Period Change", f"${change:.2f}", f"{pct:.2f}%")
                        with col3:
                            st.metric("High", f"${df['High'].max():.2f}")
                        with col4:
                            st.metric("Low", f"${df['Low'].min():.2f}")
                    
            except Exception as e:
                st.error(f"❌ Error downloading data: {str(e)}")
                import traceback
                with st.expander("Show detailed error"):
                    st.code(traceback.format_exc())

elif page == "📉 Stock Charts":
    st.title("📉 Stock Charts with mplfinance")
    st.markdown("Interactive candlestick charts with volume")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", "AAPL").upper()
    
    with col2:
        days_back = st.number_input("Days of history", min_value=30, max_value=365, value=90)
    
    col3, col4 = st.columns(2)
    
    with col3:
        chart_type = st.selectbox("Chart Type", ["candle", "ohlc", "line"], index=0)
    
    with col4:
        show_volume = st.checkbox("Show Volume", value=True)
    
    if st.button("Generate Chart", type="primary"):
        with st.spinner(f"Fetching data from {global_data_source}..."):
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            try:
                source, api_key = get_data_source_params()
                st.info(f"📡 Fetching {ticker} data using {source}...")
                
                df = fetch_market_data(ticker, start_date, end_date, "1d", source, api_key)
                
                st.write(f"Debug: Downloaded dataframe shape: {df.shape}")
                
                if df.empty or len(df) == 0:
                    st.error(f"❌ No data available for ticker '{ticker}'")
                    st.warning("**Try:**\n- Different ticker symbol\n- Different data source (use sidebar)\n- Alpha Vantage with API key")
                else:
                    st.success(f"✅ Loaded {len(df)} days of data from {source}")
                    
                    # Create the chart
                    fig, axes = mpf.plot(
                        df,
                        type=chart_type,
                        style="yahoo",
                        volume=show_volume,
                        figsize=(14, 8),
                        title=f"{ticker} - {chart_type.capitalize()} Chart",
                        returnfig=True
                    )
                    
                    st.pyplot(fig)
                    
                    # Display summary statistics
                    st.subheader("Summary Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}")
                    with col2:
                        change = df['Close'].iloc[-1] - df['Close'].iloc[0]
                        pct_change = (change / df['Close'].iloc[0]) * 100
                        st.metric("Period Change", f"${change:.2f}", f"{pct_change:.2f}%")
                    with col3:
                        st.metric("High", f"${df['High'].max():.2f}")
                    with col4:
                        st.metric("Low", f"${df['Low'].min():.2f}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "📈 Moving Averages":
    st.title("📈 Simple Moving Averages (SMAs)")
    st.markdown("Calculate and visualize moving averages across different timeframes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", "AAPL").upper()
    
    with col2:
        timeframe = st.selectbox("Timeframe", ["Daily", "Weekly", "Monthly"], index=0)
    
    # MA parameters
    st.subheader("Moving Average Parameters")
    col3, col4 = st.columns(2)
    
    with col3:
        if timeframe == "Daily":
            ma1 = st.number_input("Fast MA Period", min_value=5, max_value=200, value=50)
            ma2 = st.number_input("Slow MA Period", min_value=5, max_value=500, value=200)
            days_back = 730
        elif timeframe == "Weekly":
            ma1 = st.number_input("Fast MA Period", min_value=5, max_value=100, value=10)
            ma2 = st.number_input("Slow MA Period", min_value=5, max_value=100, value=40)
            days_back = 1095
        else:  # Monthly
            ma1 = st.number_input("Fast MA Period", min_value=5, max_value=50, value=10)
            ma2 = 0
            days_back = 1825
    
    if st.button("Calculate Moving Averages", type="primary"):
        with st.spinner("Calculating..."):
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            interval_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
            interval = interval_map[timeframe]
            
            try:
                source, api_key = get_data_source_params()
                df = fetch_market_data(ticker, start_date, end_date, interval, source, api_key)
                
                if df.empty:
                    st.error(f"❌ No data available for {ticker} from {source}")
                else:
                    # Calculate MAs
                    df[f"{ma1}MA"] = df["Close"].rolling(window=ma1).mean()
                    
                    if ma2 > 0:
                        df[f"{ma2}MA"] = df["Close"].rolling(window=ma2).mean()
                    
                    # Create plot
                    addt_plots = [
                        mpf.make_addplot(df[f"{ma1}MA"], color="blue", width=1.5, label=f"{ma1}MA")
                    ]
                    
                    if ma2 > 0:
                        addt_plots.append(
                            mpf.make_addplot(df[f"{ma2}MA"], color="red", width=1.5, label=f"{ma2}MA")
                        )
                    
                    fig, axes = mpf.plot(
                        df,
                        type="candle",
                        style="yahoo",
                        addplot=addt_plots,
                        figsize=(14, 8),
                        title=f"{ticker} - {timeframe} with Moving Averages",
                        returnfig=True
                    )
                    
                    st.pyplot(fig)
                    
                    # Display data
                    st.subheader("Data with Moving Averages")
                    st.dataframe(df.tail(20), use_container_width=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "📐 Slope Analysis":
    st.title("📐 Slope Analysis")
    st.markdown("Compute trend slopes using linear regression")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", "AAPL").upper()
    
    with col2:
        days_back = st.number_input("Days of history", min_value=30, max_value=365, value=90)
    
    if st.button("Calculate Slope", type="primary"):
        with st.spinner("Calculating slope..."):
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            try:
                source, api_key = get_data_source_params()
                df = fetch_market_data(ticker, start_date, end_date, "1d", source, api_key)
                
                if df.empty:
                    st.error(f"❌ No data available for {ticker} from {source}")
                else:
                    # Calculate slope
                    slope = calculate_slope(df["Close"])
                    
                    st.success(f"Slope calculated: {slope:.4f}")
                    
                    # Determine trend
                    if slope > 0.5:
                        trend = "📈 Strong Uptrend"
                        color = "green"
                    elif slope > 0:
                        trend = "📊 Weak Uptrend"
                        color = "lightgreen"
                    elif slope > -0.5:
                        trend = "📉 Weak Downtrend"
                        color = "orange"
                    else:
                        trend = "📉 Strong Downtrend"
                        color = "red"
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Slope Value", f"{slope:.4f}")
                    with col2:
                        st.markdown(f"**Trend:** :{color}[{trend}]")
                    
                    # Plot with slope line
                    start_price = df["Close"].iloc[0]
                    end_price = start_price + (slope * (len(df) - 1))
                    
                    fig, axes = mpf.plot(
                        df,
                        type="candle",
                        style="yahoo",
                        figsize=(14, 7),
                        title=f"{ticker} (Slope={slope:0.2f})",
                        alines=dict(
                            alines=[(df.index[0], start_price), (df.index[-1], end_price)],
                            colors=["purple"],
                            linewidths=2,
                            alpha=0.75
                        ),
                        returnfig=True
                    )
                    
                    st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "🎯 Market Stage Detection":
    st.title("🎯 Market Stage Detection")
    st.markdown("Identify Stan Weinstein's market stages using moving averages")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", "SPY").upper()
    
    with col2:
        years_back = st.slider("Years of history", min_value=1, max_value=5, value=4)
    
    st.subheader("Stage Detection Parameters")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        fast_ma = st.number_input("Fast MA", min_value=5, max_value=50, value=10)
    with col4:
        slow_ma = st.number_input("Slow MA", min_value=20, max_value=100, value=40)
    with col5:
        min_consec = st.number_input("Min Consecutive", min_value=2, max_value=10, value=4)
    
    if st.button("Detect Stages", type="primary"):
        with st.spinner("Detecting market stages..."):
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * years_back)
            
            try:
                source, api_key = get_data_source_params()
                df = fetch_market_data(ticker, start_date, end_date, "1wk", source, api_key)
                
                if df.empty:
                    st.error(f"❌ No data available for {ticker} from {source}")
                else:
                    # Apply stage detection
                    stage_detector = StageDetector(
                        df.copy(),
                        fast_ma_size=fast_ma,
                        slow_ma_size=slow_ma,
                        min_consec=min_consec
                    )
                    result = stage_detector.detect()
                    
                    st.success("Stage detection complete!")
                    
                    # Display stage summary
                    st.subheader("Detected Stages")
                    for stage, periods in result.stages.items():
                        if len(periods) > 0:
                            st.write(f"**{stage.value.replace('_', ' ').title()}**: {len(periods)} period(s)")
                    
                    # Plot stages
                    fig = plot_stage_detections(result, f"{ticker} Market Stages")
                    st.pyplot(fig)
                    
                    # Display current stage
                    current_stage = stage_detector.what_stage(result.df.index[-1])
                    if current_stage:
                        st.info(f"**Current Stage:** {current_stage.value.replace('_', ' ').title()}")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "💰 Risk/Reward Calculator":
    st.title("💰 Risk/Reward Calculator")
    st.markdown("Calculate position sizing and R-multiples for your trades")
    
    trade_type = st.radio("Trade Type", ["Long", "Short"], horizontal=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        account_value = st.number_input("Total Account Value ($)", min_value=1000.0, value=25000.0, step=1000.0)
        entry_point = st.number_input("Entry Point ($)", min_value=0.01, value=100.0, step=0.01)
    
    with col2:
        risk_rate = st.slider("Risk Rate (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1) / 100
        stop_loss = st.number_input("Stop Loss ($)", min_value=0.01, value=95.0, step=0.01)
    
    if st.button("Calculate", type="primary"):
        try:
            is_short = (trade_type == "Short")
            
            # Validate inputs
            if is_short and entry_point >= stop_loss:
                st.error("For short trades, entry point must be less than stop loss")
            elif not is_short and entry_point <= stop_loss:
                st.error("For long trades, entry point must be greater than stop loss")
            else:
                calc = RiskRewardCalculator(
                    total_account_value=account_value,
                    entry_point=entry_point,
                    stop_loss=stop_loss,
                    risk_rate=risk_rate,
                    is_short=is_short
                )
                
                risk_params = calc.get_risk_parameters()
                
                st.success("Calculation complete!")
                
                # Display risk parameters
                st.subheader("Risk Parameters")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Amount to Risk", f"${risk_params.amount_to_risk:.2f}")
                with col2:
                    st.metric("Risk % of Account", f"{risk_params.percent_risk:.2f}%")
                with col3:
                    st.metric("Shares to Trade", f"{risk_params.shares_to_trade:.2f}")
                with col4:
                    st.metric("Total Investment", f"${risk_params.total_investment:.2f}")
                
                # Display R-levels
                st.subheader("R-Levels")
                r_levels = calc.r_levels()
                
                df_r = pd.DataFrame({
                    "R-Level": [r.r_level for r in r_levels],
                    "Potential P&L": [f"${r.potential_pl:.2f}" for r in r_levels],
                    "Price at R": [f"${r.price:.2f}" for r in r_levels]
                })
                
                st.dataframe(df_r, use_container_width=True)
                
                # Custom price R-level calculator
                st.subheader("Calculate R-Level at Custom Price")
                custom_price = st.number_input("Enter Price ($)", min_value=0.01, value=entry_point * 1.1, step=0.01)
                r_at_price = calc.r_level_at_price(custom_price)
                st.info(f"R-Level at ${custom_price:.2f}: **{r_at_price:.2f}R**")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif page == "📊 Stochastic RSI":
    st.title("📊 Stochastic RSI Indicator")
    st.markdown("TradingView-compatible Stochastic RSI implementation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", "RSI").upper()
    
    with col2:
        days_back = st.number_input("Days of history", min_value=100, max_value=500, value=250)
    
    st.subheader("Stochastic RSI Parameters")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        period = st.number_input("RSI Period", min_value=5, max_value=30, value=14)
    with col4:
        k_smooth = st.number_input("K Smoothing", min_value=1, max_value=10, value=3)
    with col5:
        d_smooth = st.number_input("D Smoothing", min_value=1, max_value=10, value=3)
    
    if st.button("Calculate Stochastic RSI", type="primary"):
        with st.spinner("Calculating..."):
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            try:
                source, api_key = get_data_source_params()
                df = fetch_market_data(ticker, start_date, end_date, "1d", source, api_key)
                
                if df.empty:
                    st.error(f"❌ No data available for {ticker} from {source}")
                else:
                    # Calculate 50MA
                    df["50MA"] = df["Close"].rolling(window=50).mean()
                    
                    # Calculate Stochastic RSI
                    stoch_result = stochastic_rsi(df["Close"], period, k_smooth, d_smooth)
                    
                    # Add to dataframe
                    df["KLine"] = stoch_result.k_line
                    df["DLine"] = stoch_result.d_line
                    df = df.dropna()
                    
                    st.success("Stochastic RSI calculated!")
                    
                    # Create plot
                    addt_plots = [
                        mpf.make_addplot(df["50MA"], color="blue", width=1.5, label="50MA"),
                        mpf.make_addplot(df["KLine"], panel=1, color="blue", ylabel="Stoch RSI"),
                        mpf.make_addplot(df["DLine"], panel=1, color="orange"),
                        mpf.make_addplot([0.2] * len(df), panel=1, color="red", linestyle="--"),
                        mpf.make_addplot([0.8] * len(df), panel=1, color="green", linestyle="--"),
                    ]
                    
                    fig, axes = mpf.plot(
                        df,
                        type="candle",
                        style="yahoo",
                        addplot=addt_plots,
                        figsize=(14, 8),
                        title=f"{ticker} - Stochastic RSI",
                        returnfig=True
                    )
                    
                    st.pyplot(fig)
                    
                    # Display current values
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current K-Line", f"{df['KLine'].iloc[-1]:.4f}")
                    with col2:
                        st.metric("Current D-Line", f"{df['DLine'].iloc[-1]:.4f}")
                    with col3:
                        k_val = df['KLine'].iloc[-1]
                        if k_val < 0.2:
                            signal = "🟢 Oversold"
                        elif k_val > 0.8:
                            signal = "🔴 Overbought"
                        else:
                            signal = "⚪ Neutral"
                        st.metric("Signal", signal)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "🔢 Consecutive Integers":
    st.title("🔢 Consecutive Integer Groups")
    st.markdown("Find groups of consecutive integers in an array")
    
    st.subheader("Input Array")
    array_input = st.text_area(
        "Enter integers (comma-separated)",
        "3, 4, 5, 6, 9, 10, 15, 16, 17, 18, 19, 25, 30, 31, 32, 40, 42, 44, 50, 51, 52, 53"
    )
    
    min_consec = st.number_input("Minimum Consecutive Count", min_value=2, max_value=20, value=3)
    
    if st.button("Find Groups", type="primary"):
        try:
            # Parse input
            array = [int(x.strip()) for x in array_input.split(",")]
            array = np.array(array)
            
            st.write(f"**Input Array:** {array.tolist()}")
            
            # Find consecutive groups
            groups = find_consecutive_integers(array, min_consec=min_consec)
            
            if len(groups) > 0:
                st.success(f"Found {len(groups)} group(s) with at least {min_consec} consecutive integers")
                
                # Display results
                st.subheader("Results")
                for i, (start, end) in enumerate(groups, 1):
                    st.write(f"**Group {i}:** [{start}, {end}] - Length: {end - start + 1}")
                
                # Visualize
                st.subheader("Visualization")
                fig, ax = plt.subplots(figsize=(12, 4))
                
                # Plot all points
                ax.scatter(array, [0] * len(array), s=100, c='lightgray', zorder=2, label='All values')
                
                # Highlight consecutive groups
                colors = plt.cm.Set3(np.linspace(0, 1, len(groups)))
                for (start, end), color in zip(groups, colors):
                    group_vals = array[(array >= start) & (array <= end)]
                    ax.scatter(group_vals, [0] * len(group_vals), s=200, c=[color], zorder=3, alpha=0.7)
                    ax.plot([start, end], [0, 0], linewidth=4, color=color, alpha=0.5)
                
                ax.set_ylim(-0.5, 0.5)
                ax.set_xlabel("Value")
                ax.set_title(f"Consecutive Integer Groups (min={min_consec})")
                ax.grid(True, alpha=0.3)
                ax.set_yticks([])
                st.pyplot(fig)
                
            else:
                st.warning(f"No groups found with at least {min_consec} consecutive integers")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif page == "--- ADVANCED TRADING ---":
    st.title("🚀 Advanced Trading Tools")
    st.markdown("### Professional Trading Strategies & Analysis")
    
    st.info("⚠️ These tools require Alpaca API credentials for live/paper trading")
    
    st.markdown("""
    The following advanced tools are available:
    
    - **🤖 Markov Regime Model** - Detect market regime changes using Markov switching models
    - **📈 Johansen Cointegration** - Find cointegrated pairs for pairs trading
    - **🎯 Tail Reaper Strategy** - Automated mean reversion strategy
    - **💼 Alpaca Account Info** - View your Alpaca trading account details
    
    Select a tool from the sidebar to get started.
    """)
    
    st.warning("**Note:** These tools integrate with the `scripts/` folder and require additional setup including Alpaca API keys.")

elif page == "🤖 Markov Regime Model":
    st.title("🤖 Markov Regime Switching Model")
    st.markdown("Detect market regime changes using statistical models")
    
    st.info("📊 This tool uses Markov Regime Switching to identify bull/bear market regimes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", "SPY", key="markov_ticker").upper()
    
    with col2:
        lookback_days = st.number_input("Lookback Days", min_value=100, max_value=1000, value=252)
    
    if st.button("Run Markov Analysis", type="primary"):
        with st.spinner(f"Running Markov Regime analysis for {ticker}..."):
            try:
                # Get data source and API key from global settings
                source, api_key = get_data_source_params()
                results = run_markov_regime_analysis(ticker, lookback_days, source, api_key)
                
                if "error" in results:
                    st.error(f"❌ Error: {results['error']}")
                    st.info("Make sure `statsmodels` is installed: `pip install statsmodels`")
                else:
                    st.success(f"✅ Analysis complete for {ticker}")
                    
                    # Display current regime
                    st.subheader("Current Market Regime")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Regime", results['current_regime'])
                    
                    with col2:
                        st.metric("Confidence", f"{results['confidence']:.1%}")
                    
                    with col3:
                        bull_prob = results['bull_probability']
                        st.metric("Bull Probability", f"{bull_prob:.1%}")
                    
                    # Plot regime probabilities over time
                    st.subheader("Regime Probabilities Over Time")
                    
                    fig, ax = plt.subplots(figsize=(14, 6))
                    
                    probs = results['regime_probabilities']
                    ax.plot(probs.index, probs.iloc[:, 0], label='Regime 0', linewidth=2)
                    ax.plot(probs.index, probs.iloc[:, 1], label='Regime 1', linewidth=2)
                    ax.axhline(y=0.7, color='r', linestyle='--', alpha=0.5, label='High Confidence')
                    ax.axhline(y=0.3, color='r', linestyle='--', alpha=0.5)
                    
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Probability")
                    ax.set_title(f"{ticker} - Markov Regime Probabilities")
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    st.pyplot(fig)
                    
                    # Plot price with regime overlay
                    st.subheader("Price with Regime Overlay")
                    
                    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
                    
                    # Price plot
                    ax1.plot(results['data'].index, results['data']['Close'], label='Close Price', linewidth=2)
                    ax1.set_ylabel("Price ($)")
                    ax1.set_title(f"{ticker} Price")
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                    
                    # Regime plot
                    ax2.plot(probs.index, probs.iloc[:, 0], label='Bull Regime Prob', linewidth=2, color='green')
                    ax2.plot(probs.index, probs.iloc[:, 1], label='Bear Regime Prob', linewidth=2, color='red')
                    ax2.fill_between(probs.index, 0, probs.iloc[:, 0], alpha=0.3, color='green')
                    ax2.fill_between(probs.index, 0, probs.iloc[:, 1], alpha=0.3, color='red')
                    ax2.set_xlabel("Date")
                    ax2.set_ylabel("Probability")
                    ax2.set_title("Regime Probabilities")
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    st.pyplot(fig2)
                    
                    # Model summary
                    with st.expander("📊 Model Details"):
                        st.write("**Model Summary:**")
                        st.text(str(results['model_results'].summary()))
                        
            except Exception as e:
                st.error(f"❌ Error running analysis: {str(e)}")
                st.info("Make sure all required packages are installed: `pip install -r requirements.txt`")

elif page == "📈 Johansen Cointegration":
    st.title("📈 Johansen Cointegration Test")
    st.markdown("Find cointegrated pairs for statistical arbitrage")
    
    st.info("🔍 Identifies pairs of stocks that move together for pairs trading strategies")
    
    tickers_input = st.text_area(
        "Enter ticker symbols (one per line)",
        "AAPL\nMSFT\nGOOG\nAMZN\nMETA",
        height=150
    )
    
    lookback = st.slider("Lookback Period (days)", 30, 365, 90)
    
    if st.button("Find Cointegrated Pairs", type="primary"):
        tickers = [t.strip().upper() for t in tickers_input.split('\n') if t.strip()]
        
        if len(tickers) < 2:
            st.error("❌ Please enter at least 2 tickers")
        else:
            with st.spinner(f"Running Johansen cointegration test on {len(tickers)} tickers..."):
                try:
                    # Get data source and API key from global settings
                    source, api_key = get_data_source_params()
                    results = run_johansen_cointegration(tickers, lookback, source, api_key)
                    
                    if "error" in results:
                        st.error(f"❌ Error: {results['error']}")
                        st.info("Make sure `statsmodels` is installed: `pip install statsmodels`")
                    else:
                        st.success(f"✅ Cointegration analysis complete")
                        
                        st.subheader("Test Results")
                        
                        # Display test statistics
                        st.write("**Trace Statistics:**")
                        trace_df = pd.DataFrame({
                            'Rank': range(len(results['trace_statistics'])),
                            'Trace Statistic': results['trace_statistics'],
                            'Critical Value (5%)': results['critical_values_5pct'],
                            'Cointegrated': ['✅ Yes' if ts > cv else '❌ No' 
                                           for ts, cv in zip(results['trace_statistics'], 
                                                           results['critical_values_5pct'])]
                        })
                        st.dataframe(trace_df, use_container_width=True)
                        
                        # Cointegration summary
                        if results['cointegrated_ranks']:
                            st.success(f"Found {len(results['cointegrated_ranks'])} cointegration relationship(s)")
                            st.write(f"**Cointegrated at ranks:** {results['cointegrated_ranks']}")
                        else:
                            st.warning("No significant cointegration relationships found")
                        
                        # Plot price series
                        st.subheader("Price Series")
                        fig, ax = plt.subplots(figsize=(14, 6))
                        
                        for ticker in tickers:
                            if ticker in results['data'].columns:
                                normalized = results['data'][ticker] / results['data'][ticker].iloc[0] * 100
                                ax.plot(normalized.index, normalized, label=ticker, linewidth=2)
                        
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Normalized Price (Base=100)")
                        ax.set_title("Normalized Price Series")
                        ax.legend()
                        ax.grid(True, alpha=0.3)
                        st.pyplot(fig)
                        
                        # Show eigenvectors
                        with st.expander("📊 Cointegration Vectors (Eigenvectors)"):
                            eigenvec_df = pd.DataFrame(
                                results['eigenvectors'],
                                columns=[f"Vector {i+1}" for i in range(len(results['eigenvectors'][0]))],
                                index=tickers
                            )
                            st.dataframe(eigenvec_df, use_container_width=True)
                            st.caption("These vectors show the weights for creating cointegrated portfolios")
                        
                except Exception as e:
                    st.error(f"❌ Error running analysis: {str(e)}")
                    st.info("Make sure all required packages are installed: `pip install -r requirements.txt`")

elif page == "🎯 Tail Reaper Strategy":
    st.title("🎯 Tail Reaper Mean Reversion Strategy")
    st.markdown("Automated mean reversion trading strategy")
    
    st.info("📉 Trades extreme price movements with mean reversion logic")
    
    st.warning("⚠️ This is an automated trading strategy - use with caution!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Strategy Parameters")
        ticker = st.text_input("Ticker Symbol", "SPY", key="tail_ticker").upper()
        position_size = st.number_input("Position Size ($)", min_value=100, max_value=10000, value=1000)
        z_threshold = st.number_input("Z-Score Threshold", min_value=1.0, max_value=3.0, value=2.0, step=0.1)
    
    with col2:
        st.subheader("Risk Management")
        stop_loss_pct = st.number_input("Stop Loss %", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
        take_profit_pct = st.number_input("Take Profit %", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
    
    lookback_days = st.slider("Lookback Days", 30, 180, 90)
    
    if st.button("Analyze Tail Reaper Signals", type="primary"):
        with st.spinner(f"Analyzing {ticker} for mean reversion signals..."):
            try:
                # Get data source and API key from global settings
                source, api_key = get_data_source_params()
                results = calculate_tail_reaper_signals(ticker, lookback_days, z_threshold, source, api_key)
                
                if "error" in results:
                    st.error(f"❌ Error: {results['error']}")
                else:
                    st.success(f"✅ Analysis complete for {ticker}")
                    
                    # Current signal
                    st.subheader("Current Signal")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Price", f"${results['current_price']:.2f}")
                    
                    with col2:
                        st.metric("20-Day MA", f"${results['moving_average']:.2f}")
                    
                    with col3:
                        st.metric("Z-Score", f"{results['z_score']:.2f}")
                    
                    with col4:
                        signal_color = "🟢" if results['signal_type'] == "long" else ("🔴" if results['signal_type'] == "short" else "⚪")
                        st.metric("Signal", f"{signal_color} {results['signal']}")
                    
                    # Calculate position sizing
                    if results['signal_type'] != "neutral":
                        st.subheader("Position Sizing")
                        
                        shares = int(position_size / results['current_price'])
                        
                        if results['signal_type'] == "long":
                            stop_price = results['current_price'] * (1 - stop_loss_pct/100)
                            target_price = results['current_price'] * (1 + take_profit_pct/100)
                        else:
                            stop_price = results['current_price'] * (1 + stop_loss_pct/100)
                            target_price = results['current_price'] * (1 - take_profit_pct/100)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Shares", shares)
                        
                        with col2:
                            st.metric("Stop Loss", f"${stop_price:.2f}")
                        
                        with col3:
                            st.metric("Take Profit", f"${target_price:.2f}")
                    
                    # Plot price with Z-score
                    st.subheader("Price & Z-Score Analysis")
                    
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
                    
                    # Price plot
                    ax1.plot(results['data'].index, results['data']['Close'], label='Close Price', linewidth=2)
                    ax1.plot(results['data'].index, results['data']['MA'], label='20-Day MA', linewidth=2, linestyle='--')
                    ax1.set_ylabel("Price ($)")
                    ax1.set_title(f"{ticker} Price & Moving Average")
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                    
                    # Z-score plot
                    ax2.plot(results['data'].index, results['data']['Z_Score'], label='Z-Score', linewidth=2, color='purple')
                    ax2.axhline(y=z_threshold, color='r', linestyle='--', label=f'Threshold (+{z_threshold})')
                    ax2.axhline(y=-z_threshold, color='g', linestyle='--', label=f'Threshold (-{z_threshold})')
                    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                    ax2.fill_between(results['data'].index, z_threshold, 3, alpha=0.2, color='red')
                    ax2.fill_between(results['data'].index, -z_threshold, -3, alpha=0.2, color='green')
                    ax2.set_xlabel("Date")
                    ax2.set_ylabel("Z-Score")
                    ax2.set_title("Z-Score (Mean Reversion Indicator)")
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Strategy explanation
                    with st.expander("📚 Strategy Explanation"):
                        st.markdown("""
                        **Tail Reaper Mean Reversion Strategy:**
                        
                        1. **Z-Score Calculation**: Measures how many standard deviations the price is from its moving average
                        2. **Entry Signals**:
                           - **BUY (Long)**: When Z-Score < -threshold (oversold)
                           - **SELL (Short)**: When Z-Score > +threshold (overbought)
                        3. **Exit Strategy**: Mean reversion to MA or hit stop-loss/take-profit
                        4. **Risk Management**: Defined stop-loss and take-profit levels
                        
                        **Note**: This is for educational purposes. Always test strategies in paper trading first!
                        """)
                    
            except Exception as e:
                st.error(f"❌ Error running analysis: {str(e)}")

elif page == "💼 Alpaca Account Info":
    st.title("💼 Alpaca Trading Account Information")
    st.markdown("View your Alpaca account details and positions")
    
    st.info("🔐 Requires Alpaca API credentials")
    
    # API Key input
    st.subheader("API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_key = st.text_input("Alpaca API Key", type="password", key="alpaca_key")
    
    with col2:
        api_secret = st.text_input("Alpaca API Secret", type="password", key="alpaca_secret")
    
    paper_trading = st.checkbox("Paper Trading (Recommended)", value=True)
    
    if st.button("Fetch Account Info", type="primary"):
        if not api_key or not api_secret:
            st.error("❌ Please provide both API Key and API Secret")
            st.info("Get your free API keys at: https://alpaca.markets/")
        else:
            st.warning("⚠️ This feature requires the Alpaca Trading API")
            st.info("""
            **To enable this feature:**
            1. Sign up at https://alpaca.markets/
            2. Get your API keys (paper or live)
            3. Install: `pip install alpaca-py`
            4. The tool will display:
               - Account balance
               - Buying power
               - Portfolio value
               - Open positions
               - Recent orders
            """)
            
            st.code("""
# From scripts/account_info.py
from alpaca.trading.client import TradingClient

trading_client = TradingClient(api_key, api_secret, paper=True)
account = trading_client.get_account()

# Display account information
print(f"Cash: ${account.cash}")
print(f"Buying Power: ${account.buying_power}")
print(f"Portfolio Value: ${account.portfolio_value}")
            """, language="python")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📚 Alpaca Resources
    - [Alpaca Documentation](https://alpaca.markets/docs/)
    - [Paper Trading](https://app.alpaca.markets/paper/dashboard/overview)
    - [API Reference](https://alpaca.markets/docs/api-references/trading-api/)
    """)

elif page == "--- STRATEGIES ---":
    st.title("📊 Trading Strategies")
    st.markdown("### Professional Trading Strategy Implementations")
    
    st.info("⚠️ These are complete trading strategies with backtesting capabilities")
    
    st.markdown("""
    The following strategies are available:
    
    - **🌊 QuantumTrend SwiftEdge** - Adaptive trend-following combining Supertrend, Keltner Channels, and EMA
    
    Select a strategy from the sidebar to get started.
    """)
    
    st.warning("**Note:** Always backtest strategies thoroughly before live trading!")

elif page == "🌊 QuantumTrend SwiftEdge":
    quantumtrend_page(get_data_source_params)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**QuantumTrade Nexus** v2.1.0")
st.sidebar.markdown("*Powered by:* Streamlit • yfinance • Alpaca • QuantumTrend")
st.sidebar.markdown("⚡ *Next-Gen Trading Intelligence*")
