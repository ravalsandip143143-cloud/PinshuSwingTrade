# EMA 50/200 Golden Cross Scanner (4Hr) — Angel One + Telegram + GitHub Actions

## Strategy
- Timeframe: 4Hr (Angel One API me native 4Hr interval nahi hai, isliye 1Hour candles ko
  4Hr me resample kiya jata hai — code me `resample_to_4hour()` dekho)
- Signal: 50 EMA neeche se upar 200 EMA cross kare (Golden Cross) → BUY
- Lookback: Aaj se pichle 5 calendar din ke andar hua cross bhi valid
- Sirf BUY signal (SELL/Short nahi)

## Files
| File | Kaam |
|---|---|
| `main_scan.py` | Main script — poori watchlist scan karta hai |
| `angel_api.py` | Angel One login + historical data fetch |
| `ema_scanner.py` | EMA calculation + crossover detect |
| `telegram_notify.py` | Telegram alert bhejna |
| `github_logger.py` | Duplicate-signal avoid + GitHub auto-commit |
| `streamlit_app.py` | Dashboard (signals dekhne ke liye) |
| `.github/workflows/scan.yml` | Daily 9:30 AM auto-trigger |
| `PinshuTrade.txt` | Tumhari watchlist (isko apni asli 2376 stocks wali file se replace karo) |

## Setup Steps

### 1. GitHub repo banao
Ye poora folder apne GitHub repo me push karo.

### 2. GitHub Secrets add karo
Repo → Settings → Secrets and variables → Actions → "New repository secret":
- `ANGEL_API_KEY`
- `ANGEL_CLIENT_CODE`
- `ANGEL_PASSWORD` (login PIN)
- `ANGEL_TOTP_SECRET` (SmartAPI 2FA setup ke waqt jo QR/base32 secret milta hai)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID` (apne Telegram bot ko ek message bhejo, phir
  `https://api.telegram.org/bot<TOKEN>/getUpdates` khol ke chat_id nikal lo)

### 3. GitHub Actions ke liye push permission
Repo → Settings → Actions → General → "Workflow permissions" → **"Read and write permissions"** select karo.
(Isse `github_logger.py` ka auto git-push kaam karega.)

### 4. PinshuTrade.txt replace karo
Apni asli 2376 stocks wali file (ek symbol per line, jaise `RELIANCE`, `TCS`) se
sample file replace kar do.

### 5. Test run
Repo → Actions tab → "EMA Golden Cross Scanner" workflow → "Run workflow" button
se manually ek baar chala ke test kar lo, taaki 9:30 AM ka wait na karna pade.

### 6. Streamlit dashboard (optional)
`streamlit_app.py` ko Streamlit Cloud pe deploy kar do (repo connect karke).
Ye sirf results dikhayega — scanning se iska koi lena dena nahi, wo GitHub Actions
khud automatic karta hai.

## Important Notes
- Scan roz 9:30 AM IST (04:00 UTC) pe GitHub Actions se apne aap start hoga —
  koi bhi cheez khulni/open hone ki zaroorat nahi.
- `SCAN_DELAY_SECONDS` (config.py me) rate-limit se bachne ke liye delay control karta hai.
  Agar Angel API se rate-limit error aaye to isko badha dena (jaise 2 ya 3 second).
- NSE holidays wale din bhi cron trigger hoga (ye handle nahi kiya gaya), script
  bas "no data" dekh ke aage badh jayega — koi nuksaan nahi hoga.
