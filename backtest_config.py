import os
from dotenv import load_dotenv
load_dotenv()

ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

WATCHLIST_FILE = os.getenv("WATCHLIST_FILE", "PinshuTrade.txt")
DATA_DIR = os.getenv("DATA_DIR", "historical_data")
TRADES_OUTPUT_FILE = os.getenv("TRADES_OUTPUT_FILE", "backtest_trades.csv")

BACKTEST_YEARS_MAX = int(os.getenv("BACKTEST_YEARS_MAX", "6"))   # kitna purana data fetch karna hai
CHUNK_DAYS = int(os.getenv("CHUNK_DAYS", "90"))                  # ek API call me kitne din maangne hain
FETCH_DELAY_SECONDS = float(os.getenv("FETCH_DELAY_SECONDS", "1.0"))

INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "10000"))
POSITION_PCT = float(os.getenv("POSITION_PCT", "0.40"))   # har trade me current cash ka 40%
SL_PCT = float(os.getenv("SL_PCT", "0.02"))
TARGET_PCT = float(os.getenv("TARGET_PCT", "0.05"))

MIN_CASH_TO_TRADE = float(os.getenv("MIN_CASH_TO_TRADE", "500"))  # itne se kam cash ho to naya trade skip
