"""
Kaunse (stock, crossover-date) pairs ka pehle hi notification bhej chuke hain,
uska record rakhta hai (taaki wahi signal dobara na bheja jaye).
Har naye signal ke baad log file ko GitHub repo me commit + push kar deta hai,
taaki data GitHub Actions ke agle run me bhi safe rahe.
"""

import os
import subprocess
from datetime import datetime
import pandas as pd

import config

COLUMNS = ["symbol", "crossover_date", "notified_at"]


def load_notified_log():
    if os.path.exists(config.NOTIFIED_LOG_FILE):
        return pd.read_csv(config.NOTIFIED_LOG_FILE)
    return pd.DataFrame(columns=COLUMNS)


def already_notified(log_df, symbol, crossover_date):
    match = log_df[
        (log_df["symbol"] == symbol)
        & (log_df["crossover_date"] == str(crossover_date.date()))
    ]
    return not match.empty


def append_notification(log_df, symbol, crossover_date):
    new_row = pd.DataFrame([{
        "symbol": symbol,
        "crossover_date": str(crossover_date.date()),
        "notified_at": datetime.now().isoformat(timespec="seconds"),
    }])
    log_df = pd.concat([log_df, new_row], ignore_index=True)
    log_df.to_csv(config.NOTIFIED_LOG_FILE, index=False)
    return log_df


def git_commit_and_push(message="Update signal log"):
    """Log file ko commit+push karta hai. GitHub Actions me ye automatically kaam karta hai."""
    try:
        subprocess.run(["git", "add", config.NOTIFIED_LOG_FILE], check=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode == 0:
            return  # kuch naya change nahi hai
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git commit/push skip ya fail hua: {e}")
