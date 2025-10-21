import yaml
import requests

# Load configuration from config.yaml
config_path = r"C:\Users\Oskar\OneDrive\strategytrader\trader\config\config.yaml.txt"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Get API credentials from config
API_KEY = config['alpaca']['api_key']
API_SECRET = config['alpaca']['api_secret']

# Define URL and headers
url = "https://paper-api.alpaca.markets/v2"
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET
}

# Make DELETE request
response = requests.delete(url, headers=headers)

# Print the response
print(response.text)
