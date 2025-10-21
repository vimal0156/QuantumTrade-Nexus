import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Load Alpaca API credentials
config_path = r"C:\Users\Oskar\OneDrive\strategytrader\trader\config\config.yaml.txt"

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

API_KEY = config['alpaca']['api_key']
API_SECRET = config['alpaca']['api_secret']
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)

def fetch_account_info():
    """
    Fetch and display Alpaca account information.
    """
    try:
        account = trading_client.get_account()

        # Display account details
        logging.info("=== Account Information ===")
        logging.info(f"Account ID: {account.id}")
        logging.info(f"Status: {account.status}")
        logging.info(f"Cash: ${account.cash}")
        logging.info(f"Buying Power: ${account.buying_power}")
        logging.info(f"Portfolio Value: ${account.portfolio_value}")
        logging.info(f"Equity: ${account.equity}")
        logging.info(f"Last Equity: ${account.last_equity}")
        logging.info(f"Multiplier (Margin Level): {account.multiplier}")
        logging.info(f"Long Market Value: ${account.long_market_value}")
        logging.info(f"Short Market Value: ${account.short_market_value}")
        logging.info(f"Initial Margin: ${account.initial_margin}")
        logging.info(f"Maintenance Margin: ${account.maintenance_margin}")
        logging.info(f"Regulation T Buying Power: ${account.regt_buying_power}")
        logging.info(f"Day Trading Buying Power: ${account.daytrading_buying_power}")

    except Exception as e:
        logging.error(f"Error fetching account information: {e}")

def fetch_open_positions():
    """
    Fetch and display open positions in the account.
    """
    try:
        positions = trading_client.get_all_positions()
        logging.info("=== Open Positions ===")
        if not positions:
            logging.info("No open positions.")
        else:
            for position in positions:
                logging.info(f"Symbol: {position.symbol}")
                logging.info(f"Quantity: {position.qty}")
                logging.info(f"Market Value: ${position.market_value}")
                logging.info(f"Cost Basis: ${position.cost_basis}")
                logging.info(f"Unrealized PL: ${position.unrealized_pl}")
                logging.info(f"Unrealized PL %: {float(position.unrealized_plpc) * 100:.2f}%")
                logging.info("-" * 40)
    except Exception as e:
        logging.error(f"Error fetching open positions: {e}")

def fetch_recent_orders():
    """
    Fetch and display recent orders.
    """
    try:
        open_orders_request = GetOrdersRequest(
            status=QueryOrderStatus.OPEN,
            symbols=None,
            nested=False
        )
        open_orders = trading_client.get_orders(filter=open_orders_request)
        logging.info("=== Recent Orders ===")
        if not open_orders:
            logging.info("No recent orders.")
        else:
            for order in open_orders:
                logging.info(f"Order ID: {order.id}")
                logging.info(f"Symbol: {order.symbol}")
                logging.info(f"Quantity: {order.qty}")
                logging.info(f"Filled Qty: {order.filled_qty}")
                logging.info(f"Order Type: {order.order_type}")
                logging.info(f"Status: {order.status}")
                logging.info(f"Submitted At: {order.submitted_at}")
                logging.info("-" * 40)
    except Exception as e:
        logging.error(f"Error fetching recent orders: {e}")

def calculate_available_funds(account):
    """
    Calculate the available funds for trading based on account details.
    """
    try:
        regt_buying_power = float(account.regt_buying_power)
        margin_multiplier = float(account.multiplier)

        # Calculate funds based on the margin multiplier and RegT buying power
        available_funds = regt_buying_power / margin_multiplier
        logging.info(f"Available Funds for Trading (1x Margin): ${available_funds:.2f}")
        return available_funds

    except Exception as e:
        logging.error(f"Error calculating available funds: {e}")
        return 0.0

def main():
    logging.info("Fetching Alpaca Account Details...")
    account = trading_client.get_account()

    # Fetch account information
    fetch_account_info()

    # Calculate available funds
    calculate_available_funds(account)

    # Fetch open positions
    fetch_open_positions()

    # Fetch recent orders
    fetch_recent_orders()

if __name__ == "__main__":
    main()
