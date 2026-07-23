"""
MAIN SCANNING SCRIPT.
Ye roz 9:30 AM ko GitHub Actions se automatically trigger hota hai.
Poori watchlist ko ek-ek karke scan karta hai, aur jaise hi koi naya
Golden Cross (BUY) signal milta hai, USI WAQT Telegram notification
bhej deta hai (sab scan hone ka wait nahi karta).
"""

import time
from datetime import datetime

import config
from angel_api import login, load_instrument_master, get_symbol_token, fetch_hourly_candles, resample_to_4hour
from ema_scanner import find_recent_golden_cross
from telegram_notify import send_telegram_message
from github_logger import load_notified_log, already_notified, append_notification, git_commit_and_push


def load_watchlist():
    with open(config.WATCHLIST_FILE, "r") as f:
        symbols = [line.strip().upper().replace(".NS", "") for line in f if line.strip()]
    return symbols


def main():
    print(f"Scan shuru hua: {datetime.now()}")

    smart_api = login()
    instrument_df = load_instrument_master()
    watchlist = load_watchlist()
    notified_log = load_notified_log()

    print(f"{len(watchlist)} stocks watchlist se load hue")

    for symbol in watchlist:
        token, tradingsymbol = get_symbol_token(instrument_df, symbol)
        if token is None:
            print(f"{symbol}: token nahi mila, skip")
            continue

        try:
            hourly_df = fetch_hourly_candles(smart_api, token, days_back=200)
            if hourly_df is None or hourly_df.empty:
                print(f"{symbol}: data nahi mila")
                time.sleep(config.SCAN_DELAY_SECONDS)
                continue

            df_4h = resample_to_4hour(hourly_df)
            cross_time = find_recent_golden_cross(df_4h)

            if cross_time is not None and not already_notified(notified_log, symbol, cross_time):
                message = (
                    f"🟢 <b>BUY Signal</b>\n"
                    f"Stock: <b>{symbol}</b>\n"
                    f"Golden Cross (50EMA &gt; 200EMA) - 4Hr chart\n"
                    f"Crossover time: {cross_time}\n"
                    f"Detect hua: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                send_telegram_message(message)
                notified_log = append_notification(notified_log, symbol, cross_time)
                git_commit_and_push(message=f"Signal: {symbol} @ {cross_time}")
                print(f"{symbol}: NAYA BUY signal bheja gaya")
            else:
                print(f"{symbol}: koi naya signal nahi")

        except Exception as e:
            print(f"{symbol}: error - {e}")

        time.sleep(config.SCAN_DELAY_SECONDS)

    print(f"Scan khatam hua: {datetime.now()}")


if __name__ == "__main__":
    main()
