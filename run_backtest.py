"""
STEP 2: Actual backtest chalana (fetch_historical_data.py chalane ke BAAD).
Portfolio simulation: 40% current cash har trade me, 2% SL, 5% target, compounding.
1 / 3 / 6 saal -- teeno ke result ek saath print karega.
"""

import os
import pandas as pd

import backtest_config as cfg
from backtest_engine import get_trades_for_stock


def load_all_trades():
    all_trades = []
    files = [f for f in os.listdir(cfg.DATA_DIR) if f.endswith(".csv")]
    print(f"{len(files)} stocks ki cached data mili, trades nikal rahe hain...")

    for i, fname in enumerate(files, start=1):
        symbol = fname.replace(".csv", "")
        path = os.path.join(cfg.DATA_DIR, fname)
        try:
            hourly_df = pd.read_csv(path, parse_dates=["timestamp"])
            trades = get_trades_for_stock(hourly_df, symbol)
            all_trades.extend(trades)
        except Exception as e:
            print(f"{symbol}: error - {e}")

        if i % 200 == 0:
            print(f"  ...{i}/{len(files)} stocks process hue")

    return pd.DataFrame(all_trades)


def simulate_portfolio(trades_df, years):
    """Sorted-by-entry-time trades ko chronological cash-flow simulation se chalata hai."""
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=365 * years)
    period_trades = trades_df[trades_df["entry_time"] >= cutoff].copy()
    period_trades = period_trades.sort_values("entry_time").reset_index(drop=True)

    if period_trades.empty:
        return None

    events = []
    for idx, t in period_trades.iterrows():
        events.append((t["entry_time"], "ENTRY", idx))
        events.append((t["exit_time"], "EXIT", idx))
    events.sort(key=lambda e: (e[0], 0 if e[1] == "EXIT" else 1))  # same time: exit pehle process

    cash = cfg.INITIAL_CAPITAL
    open_positions = {}
    realized_trades = []
    equity_curve = [(period_trades["entry_time"].min(), cash)]

    for ts, kind, idx in events:
        trade = period_trades.loc[idx]

        if kind == "ENTRY":
            if cash < cfg.MIN_CASH_TO_TRADE:
                continue
            alloc = cash * cfg.POSITION_PCT
            qty = alloc / trade["entry_price"]
            cash -= alloc
            open_positions[idx] = {"qty": qty, "alloc": alloc}

        elif kind == "EXIT" and idx in open_positions:
            pos = open_positions.pop(idx)
            proceeds = pos["qty"] * trade["exit_price"]
            pnl = proceeds - pos["alloc"]
            cash += proceeds
            realized_trades.append({
                "symbol": trade["symbol"], "entry_time": trade["entry_time"],
                "exit_time": trade["exit_time"], "outcome": trade["outcome"], "pnl": pnl,
            })
            equity_curve.append((ts, cash))

    if not realized_trades:
        return None

    realized_df = pd.DataFrame(realized_trades)
    equity_df = pd.DataFrame(equity_curve, columns=["time", "equity"])

    final_capital = cash
    total_return_pct = (final_capital - cfg.INITIAL_CAPITAL) / cfg.INITIAL_CAPITAL * 100
    win_rate = (realized_df["pnl"] > 0).mean() * 100

    running_max = equity_df["equity"].cummax()
    drawdown = (equity_df["equity"] - running_max) / running_max * 100
    max_drawdown = drawdown.min()

    return {
        "years": years,
        "total_trades": len(realized_df),
        "final_capital": round(final_capital, 2),
        "total_return_pct": round(total_return_pct, 2),
        "win_rate_pct": round(win_rate, 2),
        "max_drawdown_pct": round(max_drawdown, 2),
        "realized_trades_df": realized_df,
    }


def main():
    trades_df = load_all_trades()
    if trades_df.empty:
        print("Koi trade nahi mila. Pehle fetch_historical_data.py chala ke data download karo.")
        return

    trades_df.to_csv(cfg.TRADES_OUTPUT_FILE, index=False)
    print(f"\nTotal {len(trades_df)} trades mile (sabhi saal milake). Saved: {cfg.TRADES_OUTPUT_FILE}\n")

    print(f"{'Period':<10}{'Trades':<10}{'Final Capital':<18}{'Return %':<12}{'Win Rate %':<14}{'Max Drawdown %'}")
    for years in [1, 3, 6]:
        result = simulate_portfolio(trades_df, years)
        if result is None:
            print(f"{years} saal   : is period me trades nahi mile")
            continue
        print(f"{years} saal    {result['total_trades']:<10}"
              f"Rs.{result['final_capital']:<15}{result['total_return_pct']:<12}"
              f"{result['win_rate_pct']:<14}{result['max_drawdown_pct']}")


if __name__ == "__main__":
    main()
