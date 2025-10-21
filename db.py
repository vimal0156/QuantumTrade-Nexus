import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, date

from alpaca.trading.client import TradingClient
import requests
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.data.timeframe import TimeFrame

import asyncio
import asyncpg
import yaml
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import t
import sys
import os

# If you use anything from statsmodels.stats, import the submodule you need
# e.g. from statsmodels.stats.weightstats import DescrStatsW

# -------------------------
# Import local script
# -------------------------
# Rather than relying on __file__, we just assume 'scripts' is in the same directory.
# Adjust if your folder structure is different.
scripts_path = os.path.join(os.getcwd(), "scripts")
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

from tailreaper import fit_t_distribution  # Ensure your tailreaper.py is in the 'scripts' folder

# -------------------------
# Load config
# -------------------------
config_path = r"C:\Users\Oskar\OneDrive\strategytrader\trader\config\config.yaml.txt"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Alpaca API credentials
API_KEY = config['alpaca']['api_key']
API_SECRET = config['alpaca']['api_secret']

# Database URL
DATABASE_URL = "postgres://postgres.dceaclimutffnytrqtfb:Porsevej7!@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

# Initialize Alpaca clients
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

symbol_spy = "SPY"
symbol_trade = "SPXL"

# --------------------------------------
# Streamlit Page Configuration & Styling
# --------------------------------------
st.set_page_config(page_title="Trading Dashboard", layout="wide")

st.markdown(
    """
    <style>
    /* Center the main header */
    .main > div:first-child {
        padding-top: 2rem;
    }

    /* General text styling */
    .stMarkdown h1, h2, h3, h4 {
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        color: #222;
    }

    /* Metric label styling */
    .metric-label {
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------
# Helper Functions
# --------------------------------------
def fetch_account_info():
    """Retrieve account info from Alpaca (paper trading)."""
    account = trading_client.get_account()
    balance = float(account.cash)
    buying_power = float(account.buying_power)
    equity = float(account.equity)
    last_equity = float(account.last_equity)
    portfolio_value = float(account.portfolio_value)
    return balance, buying_power, equity, last_equity, portfolio_value


def fetch_portfolio_history_from_api():
    """Get historical portfolio data from Alpaca to display equity curve."""
    url = "https://paper-api.alpaca.markets/v2/account/portfolio/history?intraday_reporting=market_hours&pnl_reset=per_day"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.warning(f"Unable to fetch portfolio history. Status code: {response.status_code}")
        return pd.DataFrame()

    data = response.json()
    if "timestamp" not in data or "equity" not in data:
        st.warning("Unexpected portfolio history format.")
        return pd.DataFrame()

    df = pd.DataFrame({
        "timestamp": data["timestamp"],
        "equity": data["equity"],
        "profit_loss": data["profit_loss"],
        "profit_loss_pct": data["profit_loss_pct"]
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
    df.set_index("timestamp", inplace=True)
    return df


async def fetch_last_p0_data_async():
    """Get the most recent p0 value from your 'msmdata' table."""
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT timestamp, last_p0 FROM msmdata ORDER BY timestamp DESC LIMIT 1;")
    await conn.close()
    if row:
        timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S %Z')
        last_p0_val = float(row['last_p0'])
        return timestamp_str, last_p0_val
    return None, None

def fetch_last_p0_data():
    """Sync wrapper around the async function to fetch the latest p0."""
    return asyncio.run(fetch_last_p0_data_async())


async def fetch_entry_threshold_async():
    """Get the most recent entry threshold from your 'msmdata' table."""
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("""
        SELECT MAX(entry_threshold) AS max_entry_threshold
        FROM msmdata
        WHERE timestamp = (SELECT MAX(timestamp) FROM msmdata);
    """)
    await conn.close()

    if row and row['max_entry_threshold'] is not None:
        return float(row['max_entry_threshold'])
    else:
        return None

def fetch_entry_threshold():
    """Sync wrapper around the async function to fetch the entry threshold."""
    return asyncio.run(fetch_entry_threshold_async())


async def fetch_historical_p0_data_async():
    """Fetch daily last_p0 from your 'msmdata' table."""
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("""
        SELECT date(timestamp) AS day,
               CAST((array_agg(last_p0 ORDER BY timestamp DESC))[1] AS FLOAT) AS daily_last_p0
        FROM msmdata
        GROUP BY date(timestamp)
        ORDER BY day;
    """)
    await conn.close()

    if rows:
        df = pd.DataFrame(rows, columns=["day", "daily_last_p0"])
        df.set_index("day", inplace=True)
        return df
    else:
        return pd.DataFrame(columns=["day", "daily_last_p0"])

def fetch_historical_p0_data():
    """Sync wrapper to fetch historical p0 daily data."""
    df = asyncio.run(fetch_historical_p0_data_async())
    if df.empty:
        st.write("Fetched historical P0 data is empty in the cloud.")
    else:
        st.write("Sample fetched historical P0 data:", df.head())
    return df


def fetch_current_positions():
    """Fetch the current position(s) for your symbol from Alpaca."""
    positions = trading_client.get_all_positions()
    data = []
    for pos in positions:
        if pos.symbol == symbol_trade:
            qty = float(pos.qty)
            entry_price = float(pos.avg_entry_price)

            try:
                latest_trade_req = StockLatestTradeRequest(symbol_or_symbols=[symbol_trade])
                latest_trade = data_client.get_stock_latest_trade(latest_trade_req)
                current_price = latest_trade[symbol_trade].price
            except Exception as e:
                st.warning(f"Could not fetch current price for {symbol_trade}: {e}")
                current_price = entry_price

            unrealized_pnl = (current_price - entry_price) * qty
            data.append([pos.symbol, qty, entry_price, current_price, unrealized_pnl])

    if data:
        position_df = pd.DataFrame(
            data,
            columns=["Symbol", "Quantity", "Entry Price", "Current Price", "Unrealized PnL"]
        ).astype({
            "Quantity": float,
            "Entry Price": float,
            "Current Price": float,
            "Unrealized PnL": float
        })
    else:
        position_df = pd.DataFrame(
            columns=["Symbol", "Quantity", "Entry Price", "Current Price", "Unrealized PnL"]
        )
    return position_df


def fetch_historical_data(symbol, start_dt, end_dt):
    """Fetch daily historical price data from Yahoo Finance and compute log-returns."""
    data = yf.download(symbol, start=start_dt, end=end_dt, interval="1d")
    if 'Adj Close' in data.columns:
        data['Log Return'] = np.log(data['Adj Close'] / data['Adj Close'].shift(1))
        data.dropna(inplace=True)
    return data


# =================================
# Streamlit Layout & Tabs
# =================================
st.markdown("<h1 style='text-align: center;'>Trading Dashboard</h1>", unsafe_allow_html=True)

tabs = st.tabs(["Account Overview", "Regime Switching trader", " Tail Reaper"])

# ---------------------- ACCOUNT OVERVIEW ----------------------
with tabs[0]:
    st.markdown("## Account Overview")
    balance, buying_power, equity, last_equity, portfolio_value = fetch_account_info()

    st.write("General account information and portfolio overview:")
    colA, colB, colC, colD, colE = st.columns(5)
    colA.metric(label="**Account Balance (USD)**", value=f"${balance:,.2f}")
    colB.metric(label="**Buying Power (USD)**", value=f"${buying_power:,.2f}")
    colC.metric(label="**Equity (USD)**", value=f"${equity:,.2f}")
    delta_equity = equity - last_equity
    colD.metric(label="**Last Equity (USD)**", value=f"${last_equity:,.2f}", delta=f"${delta_equity:,.2f}")
    colE.metric(label="**Portfolio Value (USD)**", value=f"${portfolio_value:,.2f}")

    st.markdown("---")
    st.markdown("**Historical Account Performance**")

    ph_df = fetch_portfolio_history_from_api()
    if not ph_df.empty:
        ph_df['cumulative_profit_loss'] = ph_df['profit_loss'].cumsum()
        ph_df['cumulative_profit_loss_pct'] = ph_df['profit_loss_pct'].cumsum()

        pl_data = ph_df[['profit_loss', 'cumulative_profit_loss']]
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Equity (USD)**")
            st.line_chart(ph_df['equity'], use_container_width=True)

        with col2:
            st.markdown("**Profit/Loss (USD)**")
            st.line_chart(pl_data, use_container_width=True)

        with col3:
            st.markdown("**Cumulative Profit/Loss Percentage**")
            st.line_chart(ph_df['cumulative_profit_loss_pct'], use_container_width=True)
    else:
        st.write("No historical equity data available.")


# ---------------------- REGIME SWITCHING TRADER ----------------------
with tabs[1]:
    st.markdown("## Regime Switching trader")

    # Fetch threshold and latest p0 from DB
    entry_threshold = fetch_entry_threshold()
    timestamp_str, last_p0_val = fetch_last_p0_data()
    balance, buying_power, equity, last_equity, portfolio_value = fetch_account_info()

    # Define the allocation percentage (from config)
    allocation_percentage = config['strategies']['regime_switching']['allocation_percentage']
    allocated_capital = equity * allocation_percentage

    # Display P(X(t+1)), Threshold, and Allocated Capital
    if last_p0_val is not None and entry_threshold is not None:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="P(X(t+1)) of Positive Regime", value=f"{last_p0_val:.2%}")
        col2.metric(label="Entry/Exit Threshold", value=f"{entry_threshold:.2f}")
        col3.metric(label="Allocated Percentage", value=f"{allocation_percentage:,.2f}")
        col4.metric(label="Allocated Capital", value=f"${allocated_capital:,.2f}")
    else:
        st.write("No data available for P(X(t+1)) or entry threshold. Ensure the required processes are running.")

    # Historical P0 Plot
    historical_p0_df = fetch_historical_p0_data()
    if not historical_p0_df.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Historical P0 (Daily)")
        st.line_chart(historical_p0_df['daily_last_p0'], use_container_width=True)
    else:
        st.write("No historical P0 data available. Ensure the database is populated.")

    st.markdown("---")

    st.markdown("**Current Position**")
    position_df = fetch_current_positions()
    if position_df.empty:
        st.write("No current positions for this strategy.")
    else:
        st.dataframe(
            position_df.style.format({
                "Quantity": "{:,.0f}",
                "Entry Price": "{:,.2f}",
                "Current Price": "{:,.2f}",
                "Unrealized PnL": "{:,.2f}"
            }),
            use_container_width=True
        )

    st.markdown("---")

    st.markdown("**Historical Data & Log Returns**")
    today = date.today()
    default_start = today.replace(year=today.year - 1)
    chosen_start = st.date_input("Start Date:", default_start)
    chosen_end = st.date_input("End Date:", today)

    if chosen_start > chosen_end:
        st.error("Start date must be before the end date.")
    else:
        historical_data = fetch_historical_data(symbol_spy,
                                               chosen_start.strftime("%Y-%m-%d"),
                                               chosen_end.strftime("%Y-%m-%d"))
        if not historical_data.empty and 'Adj Close' in historical_data.columns:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Historical Prices (Adj Close)**")
                st.line_chart(historical_data['Adj Close'], use_container_width=True)
            with col2:
                st.markdown("**Log Returns**")
                st.line_chart(historical_data['Log Return'], use_container_width=True)
        else:
            st.write("No historical data available for the given date range.")

    if st.button("Refresh Data"):
        st.experimental_rerun()


# ---------------------- TAIL REAPER STRATEGY ----------------------
with tabs[2]:
    st.markdown("## Tail Reaper")

    # Fetch historical data from 1994-01-01 to today for fitting
    start_date = "1994-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')
    historical_data = fetch_historical_data(symbol_spy, start_date, end_date)

    if historical_data.empty:
        st.error("No data fetched for SPY from Yahoo Finance. Check your internet or symbol.")
        st.stop()

    log_returns = historical_data['Log Return']

    allocation_percentage_tr = config['strategies']['tail_reaper']['allocation_percentage']
    quantile_threshold = config['strategies']['tail_reaper']['quantile']
    price_drop_threshold = config['strategies']['tail_reaper']['price_drop_threshold']
    profit_target = config['strategies']['tail_reaper']['profit_target']
    latest_log_return = log_returns.iloc[-1] if len(log_returns) > 0 else None

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(label="Allocation Percentage", value=f"{allocation_percentage_tr:.2%}")
    col2.metric(label="Quantile Threshold", value=f"{quantile_threshold:.2}")
    col3.metric(label="Price Drop Threshold", value=f"{price_drop_threshold:.2%}")
    col4.metric(label="Profit Target", value=f"{profit_target:.2}")
    if latest_log_return is not None:
        col5.metric(label="Last log-return", value=f"{latest_log_return:.6f}")
    else:
        col5.metric(label="Last log-return", value="N/A")

    # Fit t-distribution to log returns
    fitted_params = fit_t_distribution(log_returns)
    if fitted_params is None:
        st.error("Failed to fit t-distribution to log returns.")
        st.stop()

    # Compute the quantile value for highlighting
    df_ = fitted_params  # (df, loc, scale)
    quantile_value = t.ppf(quantile_threshold, *df_)

    # Create side-by-side plots
    fig = plt.figure(figsize=(12, 6))

    # Plot 1: t-Distribution PDF
    ax1 = fig.add_subplot(1, 2, 1)
    x = np.linspace(log_returns.min(), log_returns.max(), 1000)
    pdf = t.pdf(x, *fitted_params)

    ax1.plot(pdf, x, color="red", label="Fitted t-Distribution")
    ax1.fill_betweenx(x, 0, pdf, where=(x <= quantile_value), color="green", alpha=0.3,
                      label=f"{quantile_threshold:.2%} Quantile")
    ax1.set_xlabel("Probability Density", color="red")
    ax1.set_ylabel("Log Returns")
    ax1.tick_params(axis="x", labelcolor="red")
    ax1.grid(alpha=0.3)
    ax1.set_title("Fitted t-Distribution with Highlighted Quantile")
    ax1.legend(loc="upper right")

    # Plot 2: Log Returns Timeseries
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(historical_data.index, log_returns, label="Log Returns", color="blue", linewidth=0.5)
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Log Returns", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")
    ax2.set_title("Log Returns Over Time")
    ax2.grid(alpha=0.3)
    ax2.legend(loc="upper right")

    plt.tight_layout()
    st.pyplot(fig)
