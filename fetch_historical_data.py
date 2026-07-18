"""
STEP 1: Historical data download (backtest se PEHLE ek baar chalana hai).
2376 stocks * kai saal ka data -- isme KAAFI TIME lagega (ghanton mein, shayad
1-2 session bhi lag sakte hain). Isliye ye script RESUMABLE hai -- jitna data
ek baar mil chuka hai wo agli baar automatically skip ho jayega, tum isko
beech me Ctrl+C se rok ke baad me dobara chala sakte ho.
"""

import os
import time
from datetime import datetime, timedelta
import pandas as pd

import backtest_config as cfg
from angel_api import login, load_instrument_master, get_symbol_token


def load_watchlist():
    with open(cfg.WATCHLIST_FILE, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]


def fetch_chunked_hourly(smart_api, token, years_back):
    """Bade date-range ko chhote chunks me todke 1-Hour candles fetch karta hai."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years_back)

    all_chunks = []
    chunk_end = end_date

    while chunk_end > start_date:
        chunk_start = max(start_date, chunk_end - timedelta(days=cfg.CHUNK_DAYS))
        params = {
            "exchange": "NSE",
            "symboltoken": str(token),
            "interval": "ONE_HOUR",
            "fromdate": chunk_start.strftime("%Y-%m-%d %H:%M"),
            "todate": chunk_end.strftime("%Y-%m-%d %H:%M"),
        }
        try:
            response = smart_api.getCandleData(params)
            if response and response.get("status") and response.get("data"):
                df = pd.DataFrame(
                    response["data"],
                    columns=["timestamp", "open", "high", "low", "close", "volume"]
                )
                all_chunks.append(df)
        except Exception as e:
            print(f"    chunk error ({chunk_start.date()} - {chunk_end.date()}): {e}")

        chunk_end = chunk_start
        time.sleep(cfg.FETCH_DELAY_SECONDS)

    if not all_chunks:
        return None

    full_df = pd.concat(all_chunks, ignore_index=True)
    full_df["timestamp"] = pd.to_datetime(full_df["timestamp"])
    full_df = full_df.drop_duplicates(subset="timestamp").sort_values("timestamp")
    return full_df.reset_index(drop=True)


def main():
    os.makedirs(cfg.DATA_DIR, exist_ok=True)

    smart_api = login()
    instrument_df = load_instrument_master()
    watchlist = load_watchlist()

    print(f"{len(watchlist)} stocks ke liye {cfg.BACKTEST_YEARS_MAX} saal ka data fetch hoga")

    for idx, symbol in enumerate(watchlist, start=1):
        out_path = os.path.join(cfg.DATA_DIR, f"{symbol}.csv")
        if os.path.exists(out_path):
            print(f"[{idx}/{len(watchlist)}] {symbol}: pehle se fetched, skip")
            continue

        token, _ = get_symbol_token(instrument_df, symbol)
        if token is None:
            print(f"[{idx}/{len(watchlist)}] {symbol}: token nahi mila, skip")
            continue

        print(f"[{idx}/{len(watchlist)}] {symbol}: fetching...")
        df = fetch_chunked_hourly(smart_api, token, cfg.BACKTEST_YEARS_MAX)
        if df is None or df.empty:
            print(f"    {symbol}: data nahi mila")
            continue

        df.to_csv(out_path, index=False)
        print(f"    {symbol}: {len(df)} candles saved")

    print("Data fetching complete (ya jitna is session me ho paya).")


if __name__ == "__main__":
    main()
