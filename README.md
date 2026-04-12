# ⬡ Xenesis Exchange — OTC Crypto Trading Desk

A professional web-based F2F (face-to-face) USDT/INR OTC trading dashboard built with Streamlit.

## Features

| Module | Description |
|--------|-------------|
| 📡 Live Market Data | Real-time Binance P2P USDT/INR pricing with weighted averages |
| 🏙 City Pricing | City-based premium engine for 10 Indian cities |
| 🤖 AI Prediction | Polynomial regression spread predictor (next 10 min) |
| 💼 Deal Engine | Optimal F2F buy/sell price suggestions with profit calc |
| 📒 Trade Logger | SQLite-backed trade history with full details |
| 🛡 Compliance | Total profit, tax estimate, risk alerts |
| 📑 Tax Report | India FY (Apr–Mar), 30% + 4% cess, downloadable TXT |
| 📋 Deal Quotes | Professional formatted quotes with UUID deal IDs |
| 📄 PDF Invoice | ReportLab-generated downloadable invoices |

## Quick Start

```bash
# 1. Clone / navigate to folder
cd xenesis_exchange

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

App opens at **http://localhost:8501**

## Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **SQLite** — Local database for trades & market history
- **NumPy** — Polynomial regression for AI prediction
- **ReportLab** — PDF invoice generation
- **Binance P2P API** — Real-time USDT/INR pricing (public endpoint)

## Database

Two SQLite tables are auto-created in `xenesis.db`:

- `trades` — All logged OTC deals
- `market_history` — Timestamped price snapshots (feeds AI model)

## Disclaimer

This tool is for **authorised OTC trading desk use only**. Tax figures are estimates — consult a Chartered Accountant for official filing. Xenesis Exchange does not hold, custody, or transfer any crypto assets.

---
*Xenesis Exchange · OTC Desk · India*
