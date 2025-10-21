"""
Streamlit page for QuantumTrend SwiftEdge strategy
Add this to the main streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import os

# Import from same directory
from .quantumtrend_swiftedge import QuantumTrendSwiftEdge


def quantumtrend_page(get_data_source_params):
    """
    QuantumTrend SwiftEdge strategy page
    
    Args:
        get_data_source_params: Function to get global data source and API key
    """
    st.title("🌊 QuantumTrend SwiftEdge Strategy")
    st.markdown("### Adaptive Trend-Following with Precision Signals")
    
    st.info("""
    **QuantumTrend SwiftEdge** combines Supertrend, Keltner Channels, and 100-period EMA 
    to generate high-probability buy/sell signals for trend-following and breakout trading.
    """)
    
    # Strategy explanation
    with st.expander("📚 How It Works"):
        st.markdown("""
        ### Strategy Components:
        
        1. **Supertrend** - ATR-based trend direction indicator
           - Green line below price = Uptrend
           - Red line above price = Downtrend
           - Only visible when price is close to the line
        
        2. **Keltner Channels** - Volatility-based breakout detection
           - Upper/lower bands adjust to market volatility
           - Breakouts signal potential trend changes
        
        3. **100-Period EMA** - Long-term trend filter
           - Filters signals to align with broader trend
           - Reduces false signals in choppy markets
        
        ### Signal Logic:
        
        **BUY Signal** (All conditions must be met):
        - ✅ Price above 100-EMA (bullish market)
        - ✅ Price breaks above Keltner upper band
        - ✅ Supertrend switches to uptrend
        
        **SELL Signal** (All conditions must be met):
        - ✅ Price below 100-EMA (bearish market)
        - ✅ Price breaks below Keltner lower band
        - ✅ Supertrend switches to downtrend
        """)
    
    # Configuration
    st.subheader("⚙️ Strategy Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", "SPY", key="qt_ticker").upper()
        lookback_days = st.slider("Backtest Period (days)", 30, 730, 365)
    
    with col2:
        use_manual = st.checkbox("Use Manual Settings", value=False)
        
        if not use_manual:
            sensitivity = st.select_slider(
                "Signal Sensitivity",
                options=[1, 2, 3, 4, 5],
                value=3,
                help="1=Conservative (fewer signals), 5=Aggressive (more signals)"
            )
        else:
            sensitivity = 3  # Default, will be overridden by manual settings
    
    # Manual settings
    if use_manual:
        st.markdown("#### Manual Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            atr_period = st.number_input("ATR Period", 5, 20, 10)
            atr_multiplier = st.number_input("ATR Multiplier", 1.0, 5.0, 3.0, 0.5)
        
        with col2:
            keltner_length = st.number_input("Keltner Length", 10, 50, 20)
            keltner_multiplier = st.number_input("Keltner Multiplier", 0.5, 3.0, 1.5, 0.25)
        
        with col3:
            keltner_atr_length = st.number_input("Keltner ATR Length", 5, 20, 10)
            ema_length = st.number_input("EMA Length", 50, 200, 100)
    
    # Additional options
    col1, col2 = st.columns(2)
    
    with col1:
        initial_capital = st.number_input("Initial Capital ($)", 1000, 100000, 10000, 1000)
    
    with col2:
        use_simple_atr = st.checkbox("Use Simple ATR", value=False, help="Use SMA instead of EMA for ATR")
    
    # Run backtest button
    if st.button("🚀 Run Backtest", type="primary"):
        with st.spinner(f"Running QuantumTrend SwiftEdge backtest for {ticker}..."):
            try:
                # Get data source and API key from global settings
                source, api_key = get_data_source_params()
                
                # Fetch data
                from utils.unified_data_fetcher import fetch_market_data
                
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback_days)
                
                df = fetch_market_data(ticker, start_date, end_date, "1d", source, api_key)
                
                if df.empty:
                    st.error(f"❌ No data available for {ticker}")
                    return
                
                st.success(f"✅ Loaded {len(df)} days of data")
                
                # Initialize strategy
                if use_manual:
                    strategy = QuantumTrendSwiftEdge(
                        use_manual_settings=True,
                        atr_period=atr_period,
                        atr_multiplier=atr_multiplier,
                        keltner_length=keltner_length,
                        keltner_multiplier=keltner_multiplier,
                        keltner_atr_length=keltner_atr_length,
                        ema_length=ema_length,
                        use_simple_atr=use_simple_atr
                    )
                else:
                    strategy = QuantumTrendSwiftEdge(
                        sensitivity=sensitivity,
                        use_simple_atr=use_simple_atr
                    )
                
                # Run backtest
                results = strategy.backtest(df, initial_capital)
                
                # Display results
                st.subheader("📊 Backtest Results")
                
                # Performance metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Return", f"{results['total_return']:.2f}%")
                
                with col2:
                    st.metric("Buy & Hold", f"{results['buy_hold_return']:.2f}%")
                
                with col3:
                    st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
                
                with col4:
                    st.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
                
                # Trading statistics
                st.subheader("📈 Trading Statistics")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Total Trades", results['num_trades'])
                
                with col2:
                    st.metric("Buy Signals", results['num_buys'])
                
                with col3:
                    st.metric("Sell Signals", results['num_sells'])
                
                with col4:
                    st.metric("Win Rate", f"{results['win_rate']:.1f}%")
                
                with col5:
                    st.metric("Final Equity", f"${results['final_equity']:,.0f}")
                
                # Current signal
                current = strategy.get_current_signal(df)
                
                st.subheader("📡 Current Signal")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    signal_color = "🟢" if current['signal'] == "BUY" else ("🔴" if current['signal'] == "SELL" else "⚪")
                    st.metric("Signal", f"{signal_color} {current['signal']}")
                
                with col2:
                    st.metric("Position", current['position'])
                
                with col3:
                    st.metric("Trend", current['st_direction'])
                
                # Charts
                st.subheader("📉 Strategy Visualization")
                
                result_df = results['data']
                
                # Chart 1: Price with indicators
                fig1, ax1 = plt.subplots(figsize=(14, 8))
                
                ax1.plot(result_df.index, result_df['Close'], label='Close Price', linewidth=2, color='black', alpha=0.7)
                
                # Supertrend (only visible)
                visible_up = result_df[(result_df['st_visible']) & (result_df['st_direction'] == 1)]
                visible_down = result_df[(result_df['st_visible']) & (result_df['st_direction'] == -1)]
                
                ax1.scatter(visible_up.index, visible_up['supertrend'], color='green', s=15, alpha=0.6, label='Supertrend (Up)')
                ax1.scatter(visible_down.index, visible_down['supertrend'], color='red', s=15, alpha=0.6, label='Supertrend (Down)')
                
                # Keltner Channels
                ax1.plot(result_df.index, result_df['kelt_upper'], 'b--', alpha=0.5, linewidth=1, label='Keltner Upper')
                ax1.plot(result_df.index, result_df['kelt_lower'], 'b--', alpha=0.5, linewidth=1, label='Keltner Lower')
                ax1.fill_between(result_df.index, result_df['kelt_upper'], result_df['kelt_lower'], alpha=0.1, color='blue')
                
                # EMA
                ax1.plot(result_df.index, result_df['ema_100'], 'orange', linewidth=2, alpha=0.7, label='100-EMA')
                
                # Signals
                buy_signals = result_df[result_df['signal'] == 1]
                sell_signals = result_df[result_df['signal'] == -1]
                
                ax1.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', s=150, label='BUY', zorder=5)
                ax1.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', s=150, label='SELL', zorder=5)
                
                ax1.set_title(f'{ticker} - QuantumTrend SwiftEdge', fontsize=14, fontweight='bold')
                ax1.set_xlabel('Date')
                ax1.set_ylabel('Price ($)')
                ax1.legend(loc='best', fontsize=9)
                ax1.grid(True, alpha=0.3)
                
                st.pyplot(fig1)
                
                # Chart 2: Equity curve
                fig2, (ax2, ax3) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
                
                ax2.plot(result_df.index, result_df['equity'], label='Strategy Equity', linewidth=2, color='blue')
                ax2.plot(result_df.index, initial_capital * result_df['cumulative_returns'], 
                        label='Buy & Hold', linewidth=2, color='gray', alpha=0.7)
                ax2.set_ylabel('Equity ($)')
                ax2.set_title('Equity Curve Comparison')
                ax2.legend(loc='best')
                ax2.grid(True, alpha=0.3)
                ax2.axhline(y=initial_capital, color='black', linestyle='--', alpha=0.5)
                
                # Drawdown
                cumulative = result_df['cumulative_strategy_returns']
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max * 100
                
                ax3.fill_between(result_df.index, 0, drawdown, color='red', alpha=0.3)
                ax3.plot(result_df.index, drawdown, color='red', linewidth=1)
                ax3.set_ylabel('Drawdown (%)')
                ax3.set_xlabel('Date')
                ax3.set_title('Strategy Drawdown')
                ax3.grid(True, alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig2)
                
                # Trade log
                with st.expander("📋 Trade Log"):
                    trades = result_df[result_df['signal'] != 0][['Close', 'signal', 'st_direction', 'position']]
                    trades['Signal'] = trades['signal'].map({1: 'BUY', -1: 'SELL'})
                    trades = trades.rename(columns={'Close': 'Price', 'st_direction': 'Trend', 'position': 'Position'})
                    st.dataframe(trades[['Price', 'Signal', 'Trend', 'Position']], use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error running backtest: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
