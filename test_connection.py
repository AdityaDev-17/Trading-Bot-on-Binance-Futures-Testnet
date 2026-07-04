import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Load environment variables
load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Create Binance client
client = Client(API_KEY, API_SECRET)

# Use Binance Futures Testnet
client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"

try:
    # Fetch Futures account information
    account_info = client.futures_account()

    print("=" * 50)
    print("✅ Successfully connected to Binance Futures Testnet!")
    print("=" * 50)

    print(f"Can Trade : {account_info['canTrade']}")
    print(f"Total Wallet Balance : {account_info['totalWalletBalance']} USDT")
    print(f"Total Unrealized Profit : {account_info['totalUnrealizedProfit']} USDT")
    print(f"Available Balance : {account_info['availableBalance']} USDT")

except BinanceAPIException as e:
    print("❌ Binance API Error")
    print(f"Code    : {e.code}")
    print(f"Message : {e.message}")

except BinanceRequestException as e:
    print("❌ Network Error")
    print(e)

except Exception as e:
    print("❌ Unexpected Error")
    print(e)