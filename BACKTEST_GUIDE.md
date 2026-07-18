# Backtest — Laptop pe Step by Step (Hindi)

## ⚠️ Pehle ye samajh lo
2376 stocks * 6 saal ka 1-Hour data Angel One API se download karna **kaafi time
lega** — rate-limit ki wajah se ghanton lag sakte hain (kabhi kabhi ek din se zyada
bhi). Isliye ye 2 alag steps me tod diya hai:
- **Step A** = data download (ek baar karna hai, resumable hai — beech me rok sakte ho)
- **Step B** = actual backtest calculation (ye fast hai, sirf 2-3 minute)

---

## Step 0: Python install karo
1. https://www.python.org/downloads/ se Python 3.11 download karo, install karte
   waqt **"Add Python to PATH"** checkbox zaroor tick karna
2. Verify karne ke liye laptop pe Command Prompt (Windows) ya Terminal (Mac) khol ke likho:
   ```
   python --version
   ```

## Step 1: Project folder taiyar karo
1. Zip file ko kahin extract karo, jaise `C:\ema_scanner\`
2. Us folder ke andar `PinshuTrade.txt` ko apni asli 2376 stocks wali file se replace karo
3. Terminal me us folder ke andar jao:
   ```
   cd C:\ema_scanner
   ```

## Step 2: Virtual environment banao (recommended)
```
python -m venv venv
venv\Scripts\activate        (Windows)
source venv/bin/activate     (Mac/Linux)
```

## Step 3: Dependencies install karo
```
pip install -r requirements.txt
```

## Step 4: `.env` file banao
`.env.example` ko copy karke naam `.env` rakho, aur usme apni real values daalo:
```
ANGEL_API_KEY=xxxx
ANGEL_CLIENT_CODE=xxxx
ANGEL_PASSWORD=xxxx
ANGEL_TOTP_SECRET=xxxx
```
(Telegram wale fields backtest ke liye zaroori nahi hain, khali chhod sakte ho)

## Step 5 (Step A): Historical data download karo
```
python fetch_historical_data.py
```
- Ye chalte rehne do. Progress terminal me dikhega (`[45/2376] TCS: fetching...`)
- **Beech me rokna ho** to Ctrl+C dabao — jo data mil chuka hai wo `historical_data/`
  folder me save rahega
- **Dobara chalane** pe already-downloaded stocks automatically skip ho jayenge,
  bas bache hue stocks fetch honge — isliye kai sessions me complete kar sakte ho

## Step 6 (Step B): Backtest chalao
Jab data download poora (ya kaafi zyada) ho jaye:
```
python run_backtest.py
```
Kuch minute me result table print hoga:
```
Period    Trades    Final Capital     Return %    Win Rate %    Max Drawdown %
1 saal    ...       Rs.xxxxx          xx.xx       xx.xx         -xx.xx
3 saal    ...       Rs.xxxxx          xx.xx       xx.xx         -xx.xx
6 saal    ...       Rs.xxxxx          xx.xx       xx.xx         -xx.xx
```

Har trade ka detail `backtest_trades.csv` file me bhi save ho jayega — Excel me
khol ke dekh sakte ho kaunsa stock kab profit/loss me raha.

## Yaad rakhna
- Result **sirf historical hai** — future guarantee nahi deta
- Real trading me brokerage, taxes (STT, STCG), aur slippage bhi lagte hain jo
  isme count nahi hue — asli return isse thoda kam hi milega
- Agar `fetch_historical_data.py` chalate waqt "rate limit" jaisa error aaye,
  to `.env` me `FETCH_DELAY_SECONDS=2` ya `3` set kar dena
