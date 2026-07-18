"""EMA 50/200 calculate karna aur Golden Cross (BUY signal) detect karna."""

from datetime import datetime, timedelta

import config


def add_emas(df):
    df = df.copy()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()
    return df


def find_recent_golden_cross(df, lookback_days=config.LOOKBACK_DAYS):
    """
    Agar EMA50 ne EMA200 ko neeche se upar cross kiya ho (Golden Cross),
    aur ye cross pichle `lookback_days` calendar din ke andar hua ho,
    to us crossover ka timestamp return karta hai. Warna None.
    """
    if df is None or len(df) < 210:
        # EMA200 bharosemand banne ke liye kaafi history chahiye
        return None

    df = add_emas(df)
    cutoff = datetime.now() - timedelta(days=lookback_days)
    recent = df[df["timestamp"] >= cutoff].reset_index(drop=True)

    for i in range(1, len(recent)):
        prev_row = recent.iloc[i - 1]
        curr_row = recent.iloc[i]
        crossed_up = (
            prev_row["ema50"] <= prev_row["ema200"]
            and curr_row["ema50"] > curr_row["ema200"]
        )
        if crossed_up:
            return curr_row["timestamp"]

    return None
