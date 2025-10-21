import asyncio
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from scipy import stats
import pytz
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import yaml
import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
import os 
# Configure logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configuration
#config_path = r"C:\Users\Oskar\OneDrive\strategytrader\trader\config\config.yaml.txt"

# Determine the directory of the current script and use a relative path
# Get the parent directory of the 'scripts/' folder
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, ".."))

# Add the root directory to sys.path if not already present
if repo_root not in sys.path:
    sys.path.append(repo_root)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import config_loader from the root directory
from config_loader import get_config

# Use the get_config() function
config = get_config()
print(config)  # For debugging, ensure the config is loaded correctly


# Alpaca credentials
API_KEY = config['alpaca']['api_key']
API_SECRET = config['alpaca']['api_secret']
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# Global Variables
log_returns_spy = None  # Store historical log returns
entry_threshold = None  # Entry threshold at 0.01 quantile
symbol_spy = "SPY"

# Strategy Parameters
quantile = config['strategies']['tail_reaper']['quantile']  # Entry threshold quantile
price_drop_threshold = config['strategies']['tail_reaper']['price_drop_threshold']  # Price drop threshold for entry
lookback_days = 600  # Days to look back for recent high
profit_target = config['strategies']['tail_reaper']['profit_target']  # Profit target for exiting trades
cash_allocation = config['strategies']['tail_reaper']['allocation_percentage']  

current_position = None
trade_entry_price = None
trade_entry_day = None


async def initialize_historical_data():
    """
    Fetch historical data for SPY and calculate log returns.
    """
    global log_returns_spy

    logging.info("Fetching historical SPY data for initialization.")
    try:
        start_date = '1994-01-01'
        end_date = datetime.now(pytz.UTC).strftime('%Y-%m-%d')

        # Fetch historical data
        data_yf = yf.download(
            symbol_spy,
            start=start_date,
            end=end_date,
            interval='1d',
            auto_adjust=False
        )
        data_yf.dropna(inplace=True)

        # Set timezone for Yahoo Finance data
        data_yf.index = data_yf.index.tz_localize('UTC') if data_yf.index.tz is None else data_yf.index.tz_convert('UTC')

        logging.info(f"Data fetched from {data_yf.index.min()} to {data_yf.index.max()}.")
        # Calculate log returns
        data_yf['Log Return'] = np.log(data_yf['Adj Close'] / data_yf['Adj Close'].shift(1))
        data_yf = data_yf.iloc[1:]  # Remove the first row with NaN log return

        # Store log returns globally
        log_returns_spy = data_yf['Log Return'].values
        logging.info(f"Log returns calculated. Total entries: {len(log_returns_spy)}")

    except Exception as e:
        logging.error(f"Error during historical data initialization: {e}")


def fit_t_distribution(log_returns):
    """
    Fit a t-distribution to log returns and calculate the entry threshold.
    """
    global entry_threshold

    try:
        logging.info("Fitting t-distribution to log returns.")
        params = stats.t.fit(log_returns)  # Fit the t-distribution
        quantile = 0.95  # Set the desired quantile (adjust as needed)
        entry_threshold = stats.t.ppf(quantile, *params)  # Calculate the entry threshold
        logging.info(f"Entry threshold at {quantile * 100:.2f}% quantile: {entry_threshold:.4f}")
        return params  # Return the fitted parameters
    except Exception as e:
        logging.error(f"Error fitting t-distribution: {e}")
        return None


async def fetch_live_price():
    """
    Fetch the most recent price for SPY from Alpaca.
    """
    try:
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol_spy,
            timeframe=TimeFrame.Minute,
            limit=2  # Fetch the last 2 minutes
        )
        bars = data_client.get_stock_bars(request_params).df
        if not bars.empty:
            bars = bars[bars.index.get_level_values('symbol') == symbol_spy]
            bars = bars.sort_index()
            current_price = bars['close'].iloc[-1]
            previous_price = bars['close'].iloc[-2]
            return current_price, previous_price
        else:
            logging.warning("No live prices fetched.")
            return None, None
    except Exception as e:
        logging.error(f"Error fetching live price: {e}")
        return None, None



async def validate_existing_orders():
    """
    Validate and track existing orders and positions to avoid duplicates.
    If no relevant position exists, reset state to allow entry.
    """
    global current_position, trade_entry_price, trade_entry_day
    try:
        # Check for existing open positions
        positions = trading_client.get_all_positions()
        found_position = False
        for position in positions:
            if position.symbol == symbol_spy:
                logging.info(f"Existing position detected: {position.qty} shares at ${position.avg_entry_price}.")
                current_position = "long"
                trade_entry_price = float(position.avg_entry_price)
                trade_entry_day = datetime.now()  # Approximate as actual timestamp isn't available
                found_position = True

        if not found_position:
            logging.info("No existing position detected. Resetting strategy state.")
            current_position = None
            trade_entry_price = None
            trade_entry_day = None

    except Exception as e:
        logging.error(f"Error validating existing orders: {e}")


async def trading_logic():
    """
    Live trading logic with dynamically updated log returns and entry/exit conditions.
    Continuously ensures the desired position is maintained.
    """
    await initialize_historical_data()
    fit_t_distribution(log_returns_spy)

    while True:
        try:
            # Validate existing orders and positions
            await validate_existing_orders()

            # Fetch live price
            current_price, previous_price = await fetch_live_price()
            if current_price is None or previous_price is None:
                await asyncio.sleep(2)
                continue

            # Calculate current log return
            current_log_return = np.log(current_price / previous_price)

            # Calculate recent high (optional: adjust dynamically if needed)
            recent_high = max(log_returns_spy[-lookback_days:])
            #recent_high = 8000
            # Calculate percentage price drop from recent high
            price_drop = 1 - (current_price / recent_high)

            # Log key metrics
            logging.info(
                f"Current Price: {current_price:.2f}, Previous Price: {previous_price:.2f}, "
                f"Log Return: {current_log_return:.4f}, Recent High: {recent_high:.2f}, "
                f"Price Drop: {price_drop:.4f}, Entry Threshold: {entry_threshold:.4f}"
            )

            # Check if entry criteria are met and position is missing
            if current_position is None and current_log_return < entry_threshold and price_drop >= price_drop_threshold:
                logging.info("Entry criteria met, and no position exists. Entering trade.")
                await enter_trade(current_price)
                continue

            await asyncio.sleep(2)  # Run every 2 seconds
        except Exception as e:
            logging.error(f"Error in trading logic: {e}")


async def enter_trade(latest_price):
    """
    Place a buy bracket order with a take profit and a unique client_order_id for tracking.
    """
    global current_position, trade_entry_price, trade_entry_day
    try:
        account = trading_client.get_account()
        cash = float(account.cash) * cash_allocation
        quantity = int(cash // latest_price)  # Calculate the number of shares to buy

        if quantity > 0:
            # Define take profit level
            take_profit_price = round(latest_price * (1 + profit_target), 2)

            # Bracket order with take profit and stop loss
            bracket_order_data = MarketOrderRequest(
                symbol=symbol_spy,
                qty=quantity,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                order_class=OrderClass.BRACKET,
                take_profit=TakeProfitRequest(limit_price=take_profit_price),
                stop_loss=StopLossRequest(stop_price=0.01),  # Example stop loss, can adjust as needed
                client_order_id=f"tailreaper_order_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            )

            # Submit the bracket order
            trading_client.submit_order(order_data=bracket_order_data)

            # Update strategy state
            current_position = "long"
            trade_entry_price = latest_price
            trade_entry_day = datetime.now()

            logging.info(
                f"Entered position with qty {quantity} at price ${latest_price:.2f}. "
                f"Take profit set at ${take_profit_price:.2f}. Order ID: {bracket_order_data.client_order_id}."
            )
    except Exception as e:
        logging.error(f"Error entering trade: {e}")
        await asyncio.sleep(60)  # Wait before retrying to avoid repeated errors


async def main():
    logging.info("Starting live trading strategy.")
    await trading_logic()


if __name__ == "__main__":
    asyncio.run(main())