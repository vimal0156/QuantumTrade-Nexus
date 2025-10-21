# Import necessary libraries
import asyncio
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta, timezone
import yfinance as yf
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
import pytz
from asyncio import Lock
import os
import asyncpg
import yaml
from pandas.tseries.offsets import BDay
import sys

# Import Alpaca Market Data API modules
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_loader import get_config

config = get_config()
# Get API credentials from config
API_KEY = config['alpaca']['api_key']
API_SECRET = config['alpaca']['api_secret']


# Alpaca API credentials
API_KEY = config['alpaca']['api_key']
API_SECRET = config['alpaca']['api_secret']

# Database connection parameters
DB_USER = 'postgres.dceaclimutffnytrqtfb'
DB_PASSWORD = 'Porsevej7!'  # Replace with your actual password
DB_HOST = 'aws-0-eu-central-1.pooler.supabase.com'
DB_PORT = '5432'
DB_NAME = 'postgres'

# Initialize Alpaca clients
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# Global variables
symbol_spy = "SPY"          # Symbol to fit the model on
symbol_trade = "SPXL"       # Symbol to trade
log_returns_spy = []
fitted_model = None
positive_regime = 0
last_p0 = None
last_p0_timestamp = None
ENTRY_THRESHOLD = config['strategies']['regime_switching']['entry_threshold']
TRADE_PERCENTAGE = config['strategies']['regime_switching']['allocation_percentage']
eastern = pytz.timezone('US/Eastern')
current_position = None

def is_market_open():
    try:
        clock = trading_client.get_clock()
        return clock.is_open
    except Exception as e:
        logging.error(f"Error checking market status: {e}")
        return False

async def insert_probability(timestamp, last_p0_val):
    logging.info(f"Inserting P0: {last_p0_val} at {timestamp}")
    
    # Construct connection string
    conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        # Connect using the connection string
        conn = await asyncpg.connect(conn_str)
        await conn.execute(
            "INSERT INTO msmdata (timestamp, last_p0, ENTRY_THRESHOLD) VALUES ($1, $2, $3)",
            timestamp, last_p0_val, ENTRY_THRESHOLD
        )
        logging.info("Insert successful.")
    except Exception as e:
        logging.error(f"Database insert failed: {e}")
    finally:
        if conn:
            await conn.close()



async def initialize_historical_data():
    global fitted_model, log_returns_spy, positive_regime, last_p0, last_p0_timestamp

    logging.info("Fetching historical SPY data for initialization.")
    try:
        start_date = '1990-01-01'
        end_date = datetime.now(pytz.UTC).strftime('%Y-%m-%d')
        data_yf = yf.download(
            symbol_spy,
            start=start_date,
            end=end_date,
            interval='1d',
            group_by='ticker',
            auto_adjust=False
        )
        data_yf.dropna(inplace=True)

        if isinstance(data_yf.columns, pd.MultiIndex):
            data_yf.columns = data_yf.columns.get_level_values(-1)

        data_yf.index = data_yf.index - pd.Timedelta(days=1)
        if data_yf.index.tz is None:
            data_yf.index = data_yf.index.tz_localize('UTC')
        else:
            data_yf.index = data_yf.index.tz_convert('UTC')

        logging.info(f"YFinance Data Date Range: {data_yf.index.min()} to {data_yf.index.max()}")

        recent_start_date = datetime.now(pytz.UTC) - timedelta(days=5)
        recent_end_date = datetime.now(pytz.UTC)

        request_params = StockBarsRequest(
            symbol_or_symbols=symbol_spy,
            timeframe=TimeFrame.Day,
            start=recent_start_date,
            end=recent_end_date,
            feed='iex'
        )

        bars = data_client.get_stock_bars(request_params).df

        if bars.empty:
            logging.warning("No recent data fetched from Alpaca API.")
            data_alpaca = pd.DataFrame()
        else:
            bars = bars.reset_index()
            data_alpaca = bars[bars['symbol'] == symbol_spy].copy()
            data_alpaca.set_index('timestamp', inplace=True)
            data_alpaca.drop(columns=['symbol'], inplace=True)

            if data_alpaca.index.tz is None:
                data_alpaca.index = data_alpaca.index.tz_localize('UTC')
            else:
                data_alpaca.index = data_alpaca.index.tz_convert('UTC')

            data_alpaca = data_alpaca[['close']]
            data_alpaca.rename(columns={'close': 'Adj Close'}, inplace=True)
            data_alpaca.sort_index(inplace=True)

            data_alpaca_dates = data_alpaca.index.date
            data_yf_dates = data_yf.index.date
            data_alpaca = data_alpaca[~np.isin(data_alpaca_dates, data_yf_dates)]

        data_combined = pd.concat([data_yf, data_alpaca])
        data_combined.sort_index(inplace=True)
        data_combined = data_combined[~data_combined.index.duplicated(keep='first')]
        
        if data_combined['Adj Close'].isnull().any():
            null_rows = data_combined[data_combined['Adj Close'].isnull()]
            logging.error(f"Null values in 'Adj Close':\n{null_rows.index}")
            return

        data_combined['Log Return'] = np.log(data_combined['Adj Close'] / data_combined['Adj Close'].shift(1))
        data_combined = data_combined.iloc[1:]
        data_combined.index = data_combined.index.tz_convert(eastern)
        data_combined.index = data_combined.index.map(lambda dt: dt.replace(hour=16, minute=0, second=0, microsecond=0))

        if data_combined.empty:
            logging.error("No data after processing. Cannot fit model.")
            return

        log_returns_spy = data_combined['Log Return'].values
        if len(log_returns_spy) == 0:
            logging.error("Log returns array is empty.")
            return
        
        fitted_model = fit_markov_model(log_returns_spy)
        positive_regime = 0
        logging.info(f"Positive regime: {positive_regime}")

        smoothed_probs = fitted_model.smoothed_marginal_probabilities[:, positive_regime]
        last_five_dates = data_combined.index[-5:]
        last_five_probs = smoothed_probs[-5:]
        for date, prob in zip(last_five_dates, last_five_probs):
            logging.info(f"Smoothed probability {date}: {prob:.6f}")

        last_p0 = smoothed_probs[-1]
                
        if data_combined.index[-1].date() != datetime.now(eastern).date():
            last_p0_timestamp = data_combined.index[-1]
        else: 
            last_p0_timestamp = data_combined.index[-2]
            
        logging.info(f"Initial P0: {last_p0:.6f} at {last_p0_timestamp}")

    except Exception as e:
        logging.error(f"Error fetching historical data: {e}")
        raise e

def fit_markov_model(log_returns):
    logging.info("Fitting Markov Model...")
    model = MarkovRegression(log_returns, k_regimes=2, trend='c', switching_variance=True)
    fitted_model = model.fit(em_iter=1000, cov_type='robust')
    logging.info("Model fitted.")
    return fitted_model

async def check_and_cancel_conflicting_orders(direction):
    try:
        open_orders_request = GetOrdersRequest(
            status=QueryOrderStatus.OPEN,
            symbols=[symbol_trade],
            nested=False
        )
        open_orders = trading_client.get_orders(filter=open_orders_request)
        for order in open_orders:
            if order.side != direction.upper():
                trading_client.cancel_order_by_id(order.id)
                logging.info(f"Cancelled conflicting order: {order.id}")
    except Exception as e:
        logging.error(f"Error cancelling orders: {e}")

async def enter_position():
    global current_position
    if not is_market_open():
        logging.info("Market closed, cannot enter.")
        return

    await check_and_cancel_conflicting_orders("BUY")
    account = trading_client.get_account()
    current_buying_power = float(account.buying_power)

    request_params = StockBarsRequest(
        symbol_or_symbols=symbol_trade,
        timeframe=TimeFrame.Minute,
        limit=1,
        feed="iex"
    )
    bars = data_client.get_stock_bars(request_params).df

    if bars.empty:
        logging.error(f"No price for {symbol_trade}.")
        return

    latest_price = bars['close'].iloc[-1]
    position_value = current_buying_power * TRADE_PERCENTAGE
    max_shares = int(position_value / latest_price)
    if max_shares <= 0:
        logging.info("Not enough buying power.")
        return

    current_positions = trading_client.get_all_positions()
    for position in current_positions:
        if position.symbol == symbol_trade:
            current_quantity = int(float(position.qty))
            if current_quantity * latest_price >= position_value * 0.95:
                logging.info("Already fully invested.")
                current_position = "long"
                return

    # Create a unique client_order_id
    client_order_id = f"markovswitcher_entry_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    order_data = MarketOrderRequest(
        symbol=symbol_trade,
        qty=max_shares,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
        client_order_id=client_order_id
    )
    trading_client.submit_order(order_data=order_data)
    logging.info(f"Bought {max_shares} shares of {symbol_trade}. Order ID: {client_order_id}.")
    current_position = "long"


async def exit_position():
    global current_position
    if not is_market_open():
        logging.info("Market closed, cannot exit.")
        return

    await check_and_cancel_conflicting_orders("SELL")
    current_positions = trading_client.get_all_positions()
    for position in current_positions:
        if position.symbol == symbol_trade:
            current_quantity = int(float(position.qty))
            if current_quantity > 0:
                # Create a unique client_order_id
                client_order_id = f"markovswitcher_exit_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                order_data = MarketOrderRequest(
                    symbol=symbol_trade,
                    qty=current_quantity,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                    client_order_id=client_order_id
                )
                trading_client.submit_order(order_data=order_data)
                logging.info(f"Sold {current_quantity} shares of {symbol_trade}. Order ID: {client_order_id}.")
                current_position = None
            return
    logging.info("No position to close.")
    current_position = None

from pandas.tseries.offsets import BDay

async def refit_markov_model():
    global fitted_model, log_returns_spy, positive_regime, last_p0, last_p0_timestamp

    while True:
        now = datetime.now(eastern)
        next_hour = (now + timedelta(hours=1)).replace(minute=5, second=0, microsecond=0)
        sleep_duration = (next_hour - now).total_seconds()
        logging.info(f"Sleeping {sleep_duration / 60:.2f} minutes before refit.")
        await asyncio.sleep(sleep_duration)

        try:
            async with update_lock:
                logging.info("Refitting model...")

                # Ensure the end_date is the last completed business day
                end_date = (datetime.now(pytz.UTC) - BDay(1)).strftime('%Y-%m-%d')
                start_date = '1990-01-01'
                logging.info(f"Fetching data from {start_date} to {end_date}")

                # Fetch data
                data_yf = yf.download(symbol_spy, start=start_date, end=end_date, interval='1d')
                data_yf.dropna(inplace=True)

                if data_yf.index.tz is None:
                    data_yf.index = data_yf.index.tz_localize('UTC')
                else:
                    data_yf.index = data_yf.index.tz_convert('UTC')

                # Process and combine data
                data_combined = data_yf.copy()  # Assume no Alpaca data merging needed for simplicity
                data_combined['Log Return'] = np.log(data_combined['Adj Close'] / data_combined['Adj Close'].shift(1))
                data_combined = data_combined.iloc[1:]  # Drop the first row with NaN log return
                data_combined.index = data_combined.index.tz_convert(eastern)
                data_combined.index = data_combined.index.normalize() + pd.Timedelta(hours=16)

                if data_combined.empty:
                    logging.warning("No data available after processing.")
                    continue

                log_returns_spy = data_combined['Log Return'].values
                if len(log_returns_spy) == 0:
                    logging.warning("No log returns available after processing.")
                    continue

                # Fit the Markov model
                fitted_model = fit_markov_model(log_returns_spy)
                positive_regime = 0
                smoothed_probs = fitted_model.smoothed_marginal_probabilities[:, positive_regime]

                # Always use the last available probability (P0_{t-1}) and its timestamp
                last_p0 = smoothed_probs[-1]
                if data_combined.index[-1].date() != datetime.now(eastern).date():
                    last_p0_timestamp = data_combined.index[-1]
                else: 
                    last_p0_timestamp = data_combined.index[-2]

                logging.info(f"Updated last_p0: {last_p0:.6f} at {last_p0_timestamp}")

        except Exception as e:
            logging.error(f"Error refitting model: {e}")





# Lock
update_lock = Lock()

async def trading_logic():
    global last_p0, last_p0_timestamp

    while True:
        await asyncio.sleep(5)
        try:
            async with update_lock:
                current_last_p0 = last_p0
                current_last_p0_timestamp = last_p0_timestamp


            if current_last_p0 is not None and current_last_p0_timestamp is not None:
                ts_utc = current_last_p0_timestamp.astimezone(timezone.utc)
                await insert_probability(ts_utc, current_last_p0)

            current_positions = trading_client.get_all_positions()
            position_info = next((p for p in current_positions if p.symbol == symbol_trade), None)
            if position_info:
                position_qty = float(position_info.qty)
                position_side = "long" if position_qty > 0 else "none"
            else:
                position_qty = 0
                position_side = "none"

            p0_time_str = current_last_p0_timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') if current_last_p0_timestamp else 'N/A'
            logging.info(f"Position: {position_side}, Qty: {position_qty}, P0: {current_last_p0:.6f} at {p0_time_str}, threshold: {ENTRY_THRESHOLD}")

            if current_last_p0 > ENTRY_THRESHOLD:
                if position_side != "long":
                    logging.info("Entering position.")
                    await enter_position()
            else:
                if position_side == "long":
                    logging.info("Exiting position.")
                    await exit_position()

        except Exception as e:
            logging.error(f"Error in trading logic: {e}")

async def main():
    await initialize_historical_data()

    tasks = [
        asyncio.create_task(trading_logic()),
        asyncio.create_task(refit_markov_model()),
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
    except Exception as e:
        logging.error(f"Runtime Error: {e}")
