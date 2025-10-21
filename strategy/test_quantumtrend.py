"""
Test script for QuantumTrend SwiftEdge strategy
Tests the strategy with historical data and displays results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from quantumtrend_swiftedge import QuantumTrendSwiftEdge

# Import unified data fetcher
from utils.unified_data_fetcher import fetch_market_data


def fetch_data(ticker: str, days: int = 365, data_source: str = "yfinance", api_key: str = None) -> pd.DataFrame:
    """Fetch historical data using unified fetcher"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    print(f"Fetching {ticker} data from {start_date.date()} to {end_date.date()}...")
    print(f"Using data source: {data_source}")
    
    try:
        df = fetch_market_data(ticker, start_date, end_date, "1d", data_source, api_key)
        
        if df.empty:
            print(f"⚠️ No data returned. Try different data source or check API key.")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
        print(f"💡 Tip: If using Alpha Vantage/Polygon, make sure API key is provided")
        return pd.DataFrame()


def print_results(results: dict, sensitivity: int):
    """Print backtest results"""
    print("\n" + "="*70)
    print(f"QUANTUMTREND SWIFTEDGE - BACKTEST RESULTS (Sensitivity: {sensitivity})")
    print("="*70)
    
    print(f"\n📊 PERFORMANCE METRICS:")
    print(f"   Total Return:        {results['total_return']:>10.2f}%")
    print(f"   Buy & Hold Return:   {results['buy_hold_return']:>10.2f}%")
    print(f"   Outperformance:      {results['total_return'] - results['buy_hold_return']:>10.2f}%")
    print(f"   Sharpe Ratio:        {results['sharpe_ratio']:>10.2f}")
    print(f"   Max Drawdown:        {results['max_drawdown']:>10.2f}%")
    
    print(f"\n📈 TRADING STATISTICS:")
    print(f"   Total Trades:        {results['num_trades']:>10}")
    print(f"   Buy Signals:         {results['num_buys']:>10}")
    print(f"   Sell Signals:        {results['num_sells']:>10}")
    print(f"   Win Rate:            {results['win_rate']:>10.2f}%")
    print(f"   Average Win:         {results['avg_win']:>10.2f}%")
    print(f"   Average Loss:        {results['avg_loss']:>10.2f}%")
    
    print(f"\n💰 CAPITAL:")
    print(f"   Initial Capital:     ${10000:>10,.2f}")
    print(f"   Final Equity:        ${results['final_equity']:>10,.2f}")
    print(f"   Profit/Loss:         ${results['final_equity'] - 10000:>10,.2f}")
    
    print("\n" + "="*70)


def plot_results(results: dict, ticker: str, sensitivity: int):
    """Plot strategy results"""
    df = results['data']
    
    fig = plt.figure(figsize=(16, 12))
    
    # Plot 1: Price with Supertrend and Keltner Channels
    ax1 = plt.subplot(4, 1, 1)
    ax1.plot(df.index, df['Close'], label='Close Price', linewidth=2, color='black', alpha=0.7)
    
    # Plot Supertrend (only when visible)
    visible_up = df[(df['st_visible']) & (df['st_direction'] == 1)]
    visible_down = df[(df['st_visible']) & (df['st_direction'] == -1)]
    
    ax1.scatter(visible_up.index, visible_up['supertrend'], color='green', s=20, alpha=0.6, label='Supertrend (Up)')
    ax1.scatter(visible_down.index, visible_down['supertrend'], color='red', s=20, alpha=0.6, label='Supertrend (Down)')
    
    # Plot Keltner Channels
    ax1.plot(df.index, df['kelt_upper'], 'b--', alpha=0.5, linewidth=1, label='Keltner Upper')
    ax1.plot(df.index, df['kelt_lower'], 'b--', alpha=0.5, linewidth=1, label='Keltner Lower')
    ax1.fill_between(df.index, df['kelt_upper'], df['kelt_lower'], alpha=0.1, color='blue')
    
    # Plot EMA
    ax1.plot(df.index, df['ema_100'], 'orange', linewidth=2, alpha=0.7, label='100-EMA')
    
    # Plot buy/sell signals
    buy_signals = df[df['signal'] == 1]
    sell_signals = df[df['signal'] == -1]
    
    ax1.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', s=200, label='BUY', zorder=5)
    ax1.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', s=200, label='SELL', zorder=5)
    
    ax1.set_title(f'{ticker} - QuantumTrend SwiftEdge (Sensitivity: {sensitivity})', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price ($)')
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Gradient Color Indicator
    ax2 = plt.subplot(4, 1, 2, sharex=ax1)
    gradient_colors = plt.cm.RdYlGn(df['gradient'])
    for i in range(len(df)-1):
        ax2.plot(df.index[i:i+2], df['gradient'].iloc[i:i+2], color=gradient_colors[i], linewidth=2)
    
    ax2.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    ax2.fill_between(df.index, 0, df['gradient'], alpha=0.3, color='green', where=df['gradient']>0.5)
    ax2.fill_between(df.index, 0, df['gradient'], alpha=0.3, color='red', where=df['gradient']<=0.5)
    ax2.set_ylabel('Trend Gradient')
    ax2.set_ylim(0, 1)
    ax2.set_title('Gradient Trend Indicator (Green=Bullish, Red=Bearish)')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Equity Curve
    ax3 = plt.subplot(4, 1, 3, sharex=ax1)
    ax3.plot(df.index, df['equity'], label='Strategy Equity', linewidth=2, color='blue')
    ax3.plot(df.index, 10000 * df['cumulative_returns'], label='Buy & Hold', linewidth=2, color='gray', alpha=0.7)
    ax3.set_ylabel('Equity ($)')
    ax3.set_title('Equity Curve Comparison')
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=10000, color='black', linestyle='--', alpha=0.5)
    
    # Plot 4: Drawdown
    ax4 = plt.subplot(4, 1, 4, sharex=ax1)
    cumulative = df['cumulative_strategy_returns']
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100
    
    ax4.fill_between(df.index, 0, drawdown, color='red', alpha=0.3)
    ax4.plot(df.index, drawdown, color='red', linewidth=1)
    ax4.set_ylabel('Drawdown (%)')
    ax4.set_xlabel('Date')
    ax4.set_title('Strategy Drawdown')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def test_sensitivity_levels(ticker: str, days: int = 365, data_source: str = "yfinance", api_key: str = None):
    """Test all sensitivity levels"""
    df = fetch_data(ticker, days, data_source, api_key)
    
    if df.empty:
        print("\n❌ No data available. Cannot run tests.")
        print("💡 Try:")
        print("   - Different ticker symbol")
        print("   - Different data source (yfinance, alphavantage, polygon)")
        print("   - Provide API key if using alphavantage or polygon")
        return 3  # Return default sensitivity
    
    print(f"\n{'='*70}")
    print(f"TESTING ALL SENSITIVITY LEVELS FOR {ticker}")
    print(f"{'='*70}\n")
    
    results_summary = []
    
    for sensitivity in range(1, 6):
        print(f"\n🔍 Testing Sensitivity Level {sensitivity}...")
        
        strategy = QuantumTrendSwiftEdge(sensitivity=sensitivity)
        results = strategy.backtest(df.copy())
        
        results_summary.append({
            'Sensitivity': sensitivity,
            'Total Return': results['total_return'],
            'Win Rate': results['win_rate'],
            'Sharpe Ratio': results['sharpe_ratio'],
            'Max Drawdown': results['max_drawdown'],
            'Num Trades': results['num_trades']
        })
        
        print(f"   Return: {results['total_return']:.2f}% | Win Rate: {results['win_rate']:.2f}% | Trades: {results['num_trades']}")
    
    # Print summary table
    print(f"\n{'='*70}")
    print("SENSITIVITY COMPARISON SUMMARY")
    print(f"{'='*70}")
    
    summary_df = pd.DataFrame(results_summary)
    print(summary_df.to_string(index=False))
    
    # Find best sensitivity
    best_idx = summary_df['Total Return'].idxmax()
    best_sensitivity = summary_df.loc[best_idx, 'Sensitivity']
    
    print(f"\n🏆 BEST SENSITIVITY: {int(best_sensitivity)} (Return: {summary_df.loc[best_idx, 'Total Return']:.2f}%)")
    
    return int(best_sensitivity)


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("QUANTUMTREND SWIFTEDGE - STRATEGY TESTER")
    print("="*70)
    
    # Test configuration
    ticker = "SPY"  # S&P 500 ETF
    days = 365  # 1 year of data
    
    # Data source configuration
    print("\n📊 DATA SOURCE CONFIGURATION:")
    print("   1. yfinance (default, free, no API key)")
    print("   2. alphavantage (requires API key)")
    print("   3. polygon (requires API key)")
    
    # Use yfinance by default (can be changed)
    data_source = "yfinance"
    api_key = None
    
    print(f"\n✅ Using: {data_source}")
    print("💡 To use Alpha Vantage or Polygon, edit the main() function")
    
    # Test all sensitivity levels
    best_sensitivity = test_sensitivity_levels(ticker, days, data_source, api_key)
    
    # Run detailed test with best sensitivity
    print(f"\n\n{'='*70}")
    print(f"DETAILED BACKTEST WITH BEST SENSITIVITY ({best_sensitivity})")
    print(f"{'='*70}")
    
    df = fetch_data(ticker, days, data_source, api_key)
    
    if df.empty:
        print("\n❌ Cannot run detailed backtest - no data available")
        return
    strategy = QuantumTrendSwiftEdge(sensitivity=best_sensitivity)
    results = strategy.backtest(df)
    
    print_results(results, best_sensitivity)
    
    # Get current signal
    current = strategy.get_current_signal(df)
    print(f"\n📡 CURRENT SIGNAL:")
    print(f"   Price:           ${current['price']:.2f}")
    print(f"   Supertrend:      ${current['supertrend']:.2f} ({current['st_direction']})")
    print(f"   EMA 100:         ${current['ema_100']:.2f}")
    print(f"   Signal:          {current['signal']}")
    print(f"   Position:        {current['position']}")
    
    # Plot results
    print("\n📊 Generating charts...")
    plot_results(results, ticker, best_sensitivity)
    
    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()
