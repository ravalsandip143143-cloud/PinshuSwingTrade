"""Poori history me saare Golden Cross signal dhoondhna + har trade ka outcome (SL/Target/Timeout) nikalna."""

import pandas as pd
import backtest_config as cfg


def add_emas(df):
    df = df.copy()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()
    return df


def resample_to_4hour(hourly_df):
    df = hourly_df.set_index("timestamp")
    ohlc = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    resampled = df.resample("4h", origin="start_day", offset="9h15min").agg(ohlc)
    return resampled.dropna(subset=["close"]).reset_index()


def find_all_golden_crosses(df):
    """Poori history me jitni bhi baar 50EMA ne 200EMA ko neeche se upar cross kiya, unke indices."""
    cross_indices = []
    for i in range(1, len(df)):
        prev_row, curr_row = df.iloc[i - 1], df.iloc[i]
        if prev_row["ema50"] <= prev_row["ema200"] and curr_row["ema50"] > curr_row["ema200"]:
            cross_indices.append(i)
    return cross_indices


def simulate_trade(df, entry_idx):
    """
    Entry candle ke AGLE candle ke open par trade lete hain (real-world realistic --
    signal current candle band hone ke baad hi confirm hota hai, usi candle pe entry
    lena look-ahead bias hoga).
    SL / Target jo pehle hit ho, wahi exit maana jata hai. Data khatam ho jaye aur
    kuch hit na ho to last available price par 'TIMEOUT' exit.
    """
    if entry_idx + 1 >= len(df):
        return None

    entry_row = df.iloc[entry_idx + 1]
    entry_price = entry_row["open"]
    entry_time = entry_row["timestamp"]

    sl_price = entry_price * (1 - cfg.SL_PCT)
    target_price = entry_price * (1 + cfg.TARGET_PCT)

    for j in range(entry_idx + 1, len(df)):
        row = df.iloc[j]
        hit_sl = row["low"] <= sl_price
        hit_target = row["high"] >= target_price

        if hit_sl:
            # dono ek hi candle me hit ho sakte hain -- conservative: SL pehle maante hain
            return {"entry_time": entry_time, "entry_price": entry_price,
                    "exit_time": row["timestamp"], "exit_price": sl_price, "outcome": "SL"}
        elif hit_target:
            return {"entry_time": entry_time, "entry_price": entry_price,
                    "exit_time": row["timestamp"], "exit_price": target_price, "outcome": "TARGET"}

    last_row = df.iloc[-1]
    return {"entry_time": entry_time, "entry_price": entry_price,
            "exit_time": last_row["timestamp"], "exit_price": last_row["close"], "outcome": "TIMEOUT"}


def get_trades_for_stock(hourly_df, symbol):
    """Ek stock ke liye saare non-overlapping trades (jab tak ek trade khula hai, naya nahi lete)."""
    df_4h = resample_to_4hour(hourly_df)
    if len(df_4h) < 210:
        return []

    df_4h = add_emas(df_4h)
    cross_indices = find_all_golden_crosses(df_4h)

    trades = []
    last_exit_time = None

    for idx in cross_indices:
        candle_time = df_4h.iloc[idx]["timestamp"]
        if last_exit_time is not None and candle_time <= last_exit_time:
            continue  # pichla trade abhi khula hai, isko skip karo

        trade = simulate_trade(df_4h, idx)
        if trade is None:
            continue

        trade["symbol"] = symbol
        trades.append(trade)
        last_exit_time = trade["exit_time"]

    return trades
