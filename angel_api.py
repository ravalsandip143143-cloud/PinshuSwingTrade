"""
Angel One Smart API helper functions:
- login / session generation (TOTP based)
- instrument master download + local caching (symbol -> token)
- 1-Hour historical candle fetch

IMPORTANT: Angel One Smart API me native "4 Hour" interval available NAHI hai
(sirf ONE_MINUTE ... ONE_HOUR ... ONE_DAY milte hain). Isliye hum ONE_HOUR
candles fetch karke unhe khud 4-Hour candles me resample karte hain
(resample_to_4hour function), NSE market open 9:15 AM se align karke.
"""

import os
import time
import pyotp
import requests
import pandas as pd
from datetime import datetime, timedelta
from SmartApi import SmartConnect

import config

INSTRUMENT_MASTER_URL = "https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json"


def login():
    """Angel One ke saath authenticated session banata hai."""
    smart_api = SmartConnect(api_key=config.ANGEL_API_KEY)
    totp = pyotp.TOTP(config.ANGEL_TOTP_SECRET).now()
    session = smart_api.generateSession(
        config.ANGEL_CLIENT_CODE,
        config.ANGEL_PASSWORD,
        totp
    )
    if not session or not session.get("status"):
        raise RuntimeError(f"Angel One login fail hua: {session}")
    return smart_api


def load_instrument_master():
    """
    NSE equity ka symbol -> token mapping download/cache karta hai.
    24 ghante tak cache use hoga taaki roz roz bada file download na karna pade.
    """
    if os.path.exists(config.INSTRUMENT_CACHE_FILE):
        cache_age = time.time() - os.path.getmtime(config.INSTRUMENT_CACHE_FILE)
        if cache_age < 24 * 3600:
            return pd.read_csv(config.INSTRUMENT_CACHE_FILE)

    resp = requests.get(INSTRUMENT_MASTER_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame(data)

    df = df[(df["exch_seg"] == "NSE") & (df["symbol"].str.endswith("-EQ"))]
    df = df[["symbol", "token", "name"]]
    df.to_csv(config.INSTRUMENT_CACHE_FILE, index=False)
    return df


def get_symbol_token(instrument_df, stock_symbol):
    """Plain symbol jaise 'RELIANCE' ko Angel ke token + tradingsymbol se map karta hai."""
    candidate = f"{stock_symbol.upper()}-EQ"
    row = instrument_df[instrument_df["symbol"] == candidate]
    if row.empty:
        return None, None
    return row.iloc[0]["token"], candidate


def fetch_hourly_candles(smart_api, token, days_back=90):
    """Pichle `days_back` din ka 1-Hour candle data fetch karta hai."""
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days_back)

    params = {
        "exchange": "NSE",
        "symboltoken": str(token),
        "interval": "ONE_HOUR",
        "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
        "todate": to_date.strftime("%Y-%m-%d %H:%M"),
    }

    response = smart_api.getCandleData(params)
    if not response or not response.get("status") or not response.get("data"):
        return None

    df = pd.DataFrame(
        response["data"],
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def resample_to_4hour(hourly_df):
    """1-Hour candles ko 4-Hour candles me convert karta hai (market open 9:15 se aligned)."""
    df = hourly_df.set_index("timestamp")
    ohlc = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    resampled = df.resample("4h", origin="start_day", offset="9h15min").agg(ohlc)
    resampled = resampled.dropna(subset=["close"])
    return resampled.reset_index()
