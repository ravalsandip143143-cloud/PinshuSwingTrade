"""
Saari settings aur secrets yahan se load hote hain.
Local testing ke liye .env file banao (.env.example dekho).
GitHub Actions me ye values "Secrets" se aayengi (environment variables).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Angel One Smart API credentials ---
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")          # login PIN
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")    # base32 2FA secret

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Files ---
WATCHLIST_FILE = os.getenv("WATCHLIST_FILE", "PinshuTrade.txt")
NOTIFIED_LOG_FILE = os.getenv("NOTIFIED_LOG_FILE", "notified_log.csv")
INSTRUMENT_CACHE_FILE = os.getenv("INSTRUMENT_CACHE_FILE", "instruments_cache.csv")

# --- Strategy settings ---
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "5"))

# --- Rate-limit safety ---
# 2376 stocks * 1.5 sec ≈ 59 min. Increase this if Angel One rate-limit errors aayein.
SCAN_DELAY_SECONDS = float(os.getenv("SCAN_DELAY_SECONDS", "1.5"))
