import streamlit as st
import requests
import sqlite3
import numpy as np
import json
import uuid
from datetime import datetime, timedelta
import io
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Xenesis Exchange",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:       #08090d;
    --surface:  #0f111a;
    --card:     #141722;
    --border:   #1e2235;
    --accent:   #00e5b0;
    --accent2:  #7b5ea7;
    --warn:     #f5a623;
    --danger:   #e03c3c;
    --text:     #e8eaf0;
    --muted:    #6b7394;
    --green:    #00e5b0;
    --red:      #e03c3c;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

/* Headers */
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; letter-spacing: -0.02em; }

/* Metric cards */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'Space Mono', monospace !important; font-size: 1.6rem !important; }
[data-testid="stMetricDelta"] { font-family: 'Space Mono', monospace !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #00b88a) !important;
    color: #08090d !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    letter-spacing: 0.04em;
    transition: all 0.2s ease;
}
.stButton > button:hover { opacity: 0.85; transform: translateY(-1px); }

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
}

/* Dataframe */
.stDataFrame { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Card component */
.xcard {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.xcard-accent { border-left: 3px solid var(--accent); }
.xcard-warn   { border-left: 3px solid var(--warn); }
.xcard-danger { border-left: 3px solid var(--danger); }

/* Badge */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.badge-green { background: rgba(0,229,176,0.15); color: var(--green); }
.badge-red   { background: rgba(224,60,60,0.15);  color: var(--red); }
.badge-warn  { background: rgba(245,166,35,0.15); color: var(--warn); }

/* Logo */
.logo-block { display:flex; align-items:center; gap:10px; margin-bottom:28px; }
.logo-hex { font-size:2rem; color:var(--accent); }
.logo-text { font-family:'Syne',sans-serif; font-weight:800; font-size:1.3rem; letter-spacing:-0.03em; }
.logo-sub  { font-size:0.65rem; color:var(--muted); letter-spacing:0.12em; text-transform:uppercase; }

/* Quote box */
.quote-box {
    background: linear-gradient(135deg, #0f111a 0%, #141722 100%);
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: 12px;
    padding: 28px;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.9;
    white-space: pre;
}

/* Section title */
.sec-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}
.sec-sub { color: var(--muted); font-size: 0.8rem; margin-bottom: 18px; }

/* Alert */
.alert { border-radius: 8px; padding: 12px 16px; margin: 8px 0; font-size: 0.85rem; }
.alert-warn   { background: rgba(245,166,35,0.12); border-left: 3px solid var(--warn); color: var(--warn); }
.alert-danger { background: rgba(224,60,60,0.12);  border-left: 3px solid var(--danger); color: var(--red); }
.alert-info   { background: rgba(0,229,176,0.08);  border-left: 3px solid var(--accent); color: var(--accent); }

/* Mono value */
.mono { font-family: 'Space Mono', monospace; }
.price-big { font-family:'Space Mono',monospace; font-size:2.2rem; font-weight:700; color:var(--accent); }
</style>
""", unsafe_allow_html=True)


# ── Database ──────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect("xenesis.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, trader TEXT, buy_price REAL, sell_price REAL,
        usdt_amount REAL, profit REAL, city TEXT, deal_id TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS market_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, buy_avg REAL, sell_avg REAL, spread REAL
    )""")
    conn.commit()
    return conn


db = get_db()


# ── Binance P2P API ───────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def fetch_binance_p2p(side: str):
    """side: 'BUY' or 'SELL' (from user perspective: BUY=we buy USDT, SELL=we sell USDT)"""
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT", "fiat": "INR", "merchantCheck": False,
        "page": 1, "payTypes": [], "publisherType": None,
        "rows": 10, "tradeType": side,
    }
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=8)
        data = r.json()
        prices = [float(ad["adv"]["price"]) for ad in data.get("data", [])]
        return prices
    except Exception:
        return []


def weighted_avg(prices):
    if not prices:
        return None
    return round(np.average(prices), 2)


# ── City premiums ─────────────────────────────────────────────────────────────
CITY_PREMIUM = {
    "Hyderabad": 0.003, "Mumbai": 0.005, "Delhi": 0.004,
    "Bangalore": 0.003, "Chennai": 0.004, "Kolkata": 0.002,
    "Pune": 0.003, "Ahmedabad": 0.002, "Jaipur": 0.001, "Lucknow": 0.001,
}


# ── AI Prediction ─────────────────────────────────────────────────────────────
def predict_spread():
    rows = db.execute(
        "SELECT ts, spread FROM market_history ORDER BY id DESC LIMIT 30"
    ).fetchall()
    if len(rows) < 5:
        return None, "Insufficient data (need ≥5 samples)"
    ts_list = [datetime.fromisoformat(r["ts"]).timestamp() for r in rows][::-1]
    sp_list = [r["spread"] for r in rows][::-1]
    t0 = ts_list[0]
    x = np.array([(t - t0) / 60 for t in ts_list])
    y = np.array(sp_list)
    try:
        coeffs = np.polyfit(x, y, 2)
        poly = np.poly1d(coeffs)
        x_next = x[-1] + 10
        predicted = round(float(poly(x_next)), 4)
        return predicted, None
    except Exception as e:
        return None, str(e)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-block">
        <div class="logo-hex">⬡</div>
        <div>
            <div class="logo-text">Xenesis</div>
            <div class="logo-sub">OTC Exchange Desk</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    trader_name = st.text_input("👤 Trader Name", value="Desk Officer", key="trader")
    city = st.selectbox("📍 City", list(CITY_PREMIUM.keys()), index=0)
    st.markdown("---")

    auto_refresh = st.toggle("⚡ Auto Refresh (10s)", value=True)
    if auto_refresh:
        st.caption("Dashboard refreshes every 10 seconds.")
        time.sleep(0.1)  # allow render

    st.markdown("---")
    st.markdown("""
    <div style="color:var(--muted);font-size:0.72rem;line-height:1.8;">
    <b style="color:var(--accent);">XENESIS EXCHANGE</b><br>
    OTC Crypto Trading Desk<br>
    Powered by Binance P2P<br><br>
    <span style="color:var(--danger);">⚠ For authorised use only</span>
    </div>
    """, unsafe_allow_html=True)

# ── Main header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin-bottom:8px;">
    <span style="font-size:2.5rem;color:var(--accent);">⬡</span>
    <div>
        <h1 style="margin:0;font-size:2rem;">Xenesis Exchange</h1>
        <span style="color:var(--muted);font-size:0.85rem;letter-spacing:0.08em;">
            FACE-TO-FACE OTC USDT TRADING DESK · INDIA
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

ts_now = datetime.now().strftime("%d %b %Y, %H:%M:%S IST")
st.caption(f"🕐 Last updated: {ts_now}")

# ── Fetch market data ─────────────────────────────────────────────────────────
buy_prices  = fetch_binance_p2p("BUY")   # prices traders offer when buying USDT
sell_prices = fetch_binance_p2p("SELL")  # prices traders offer when selling USDT

buy_avg  = weighted_avg(buy_prices)   # avg at which market buys USDT (our sell)
sell_avg = weighted_avg(sell_prices)  # avg at which market sells USDT (our buy)

premium = CITY_PREMIUM.get(city, 0.003)

if buy_avg and sell_avg:
    our_buy  = round(sell_avg * (1 - premium * 0.5), 2)   # we buy at slight discount
    our_sell = round(buy_avg  * (1 + premium), 2)          # we sell at premium
    spread   = round(our_sell - our_buy, 2)
    spread_pct = round(spread / our_buy * 100, 3)

    # Store in history
    db.execute(
        "INSERT INTO market_history (ts, buy_avg, sell_avg, spread) VALUES (?,?,?,?)",
        (datetime.now().isoformat(), our_buy, our_sell, spread)
    )
    db.commit()
else:
    our_buy = our_sell = spread = spread_pct = None

# ── Section 1: Live Market Data ───────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="sec-title">📡 Live Market Data</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sec-sub">Binance P2P · USDT/INR · {city} Premium Applied</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("🟢 Our Buy Rate", f"₹{our_buy:,.2f}" if our_buy else "N/A",
              delta=f"Market: ₹{sell_avg}" if sell_avg else None)
with c2:
    st.metric("🔴 Our Sell Rate", f"₹{our_sell:,.2f}" if our_sell else "N/A",
              delta=f"Market: ₹{buy_avg}" if buy_avg else None)
with c3:
    st.metric("📊 Spread (INR)", f"₹{spread:,.2f}" if spread else "N/A")
with c4:
    st.metric("📈 Spread %", f"{spread_pct}%" if spread_pct else "N/A")

if buy_prices and sell_prices:
    with st.expander("🔍 Raw Binance P2P Order Book"):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**BUY orders (top 10)**")
            for i, p in enumerate(buy_prices, 1):
                st.markdown(f'`#{i}` <span class="mono">₹{p:,.2f}</span>', unsafe_allow_html=True)
        with col_b:
            st.markdown("**SELL orders (top 10)**")
            for i, p in enumerate(sell_prices, 1):
                st.markdown(f'`#{i}` <span class="mono">₹{p:,.2f}</span>', unsafe_allow_html=True)
else:
    st.markdown('<div class="alert alert-warn">⚠ Could not fetch Binance P2P data. Check internet connection.</div>', unsafe_allow_html=True)

# ── Section 2: AI Prediction ──────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="sec-title">🤖 AI Spread Prediction</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Polynomial Regression (degree 2) · Next 10 minutes</div>', unsafe_allow_html=True)

pred_spread, pred_err = predict_spread()

p1, p2, p3 = st.columns(3)
with p1:
    st.metric("Current Spread", f"₹{spread:,.2f}" if spread else "N/A")
with p2:
    if pred_spread is not None:
        delta_spread = round(pred_spread - spread, 4) if spread else None
        st.metric("Predicted Spread (10 min)", f"₹{pred_spread:,.4f}", delta=f"₹{delta_spread}" if delta_spread else None)
    else:
        st.metric("Predicted Spread", "Calculating…")
        st.caption(pred_err or "")
with p3:
    if pred_spread and spread:
        trend = "📈 Rising" if pred_spread > spread else "📉 Falling"
        conf  = "HIGH" if abs(pred_spread - spread) > 0.05 else "LOW"
        st.metric("Trend Signal", trend)
        st.caption(f"Confidence: {conf}")

# ── Section 3: F2F Deal Engine ────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="sec-title">💼 F2F Deal Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Optimal pricing strategy for face-to-face USDT trades</div>', unsafe_allow_html=True)

d1, d2 = st.columns([1, 1])
with d1:
    capital = st.number_input("Capital (INR ₹)", min_value=1000.0, value=100000.0, step=1000.0)
    deal_type = st.radio("Deal Type", ["Buy USDT", "Sell USDT"], horizontal=True)

with d2:
    if our_buy and our_sell:
        if deal_type == "Buy USDT":
            usdt_qty = round(capital / our_buy, 4)
            est_sell_val = round(usdt_qty * our_sell, 2)
            est_profit   = round(est_sell_val - capital, 2)
            rec_price    = our_buy
            st.markdown(f"""
            <div class="xcard xcard-accent">
                <div style="color:var(--muted);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;">Deal Summary</div>
                <div class="price-big">₹{our_buy:,.2f}</div>
                <div style="color:var(--muted);font-size:0.82rem;">Recommended Buy Rate</div>
                <hr style="border-color:var(--border);margin:12px 0;">
                <div class="mono" style="font-size:0.85rem;">
                USDT Qty  : <b>{usdt_qty:,.4f}</b><br>
                If sold @ : ₹{our_sell:,.2f}<br>
                Est Profit: <span style="color:var(--green);">₹{est_profit:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            usdt_qty   = round(capital / our_sell, 4)
            cost_basis = round(usdt_qty * our_buy, 2)
            est_profit = round(capital - cost_basis, 2)
            rec_price  = our_sell
            st.markdown(f"""
            <div class="xcard xcard-accent">
                <div style="color:var(--muted);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;">Deal Summary</div>
                <div class="price-big">₹{our_sell:,.2f}</div>
                <div style="color:var(--muted);font-size:0.82rem;">Recommended Sell Rate</div>
                <hr style="border-color:var(--border);margin:12px 0;">
                <div class="mono" style="font-size:0.85rem;">
                INR Received : ₹{capital:,.2f}<br>
                USDT Qty     : <b>{usdt_qty:,.4f}</b><br>
                Cost Basis   : ₹{cost_basis:,.2f}<br>
                Est Profit   : <span style="color:var(--green);">₹{est_profit:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert alert-warn">⚠ Market data unavailable — cannot compute deal.</div>', unsafe_allow_html=True)

# ── Section 4: Trade Logger ───────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="sec-title">📒 Trade Logger</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Record every OTC deal for compliance and tax tracking</div>', unsafe_allow_html=True)

with st.expander("➕ Log a New Trade", expanded=False):
    l1, l2, l3 = st.columns(3)
    with l1:
        log_buy  = st.number_input("Buy Price (₹)", value=float(our_buy or 84.0), step=0.01, key="lb")
        log_sell = st.number_input("Sell Price (₹)", value=float(our_sell or 85.0), step=0.01, key="ls")
    with l2:
        log_usdt   = st.number_input("USDT Amount", min_value=1.0, value=100.0, step=1.0)
        log_profit = round((log_sell - log_buy) * log_usdt, 2)
        st.metric("Calculated Profit", f"₹{log_profit:,.2f}")
    with l3:
        log_trader = st.text_input("Trader", value=trader_name, key="lt")
        log_city   = st.selectbox("City", list(CITY_PREMIUM.keys()), key="lc")

    if st.button("✅ Log Trade"):
        deal_id = str(uuid.uuid4())[:12].upper()
        db.execute(
            "INSERT INTO trades (ts, trader, buy_price, sell_price, usdt_amount, profit, city, deal_id) VALUES (?,?,?,?,?,?,?,?)",
            (datetime.now().isoformat(), log_trader, log_buy, log_sell, log_usdt, log_profit, log_city, deal_id)
        )
        db.commit()
        st.success(f"✅ Trade logged! Deal ID: {deal_id}")

# Show recent trades
trades = db.execute(
    "SELECT * FROM trades ORDER BY id DESC LIMIT 20"
).fetchall()

if trades:
    import pandas as pd
    df = pd.DataFrame([dict(t) for t in trades])
    df["ts"] = pd.to_datetime(df["ts"]).dt.strftime("%d %b %H:%M")
    df = df[["ts", "deal_id", "trader", "city", "buy_price", "sell_price", "usdt_amount", "profit"]]
    df.columns = ["Time", "Deal ID", "Trader", "City", "Buy ₹", "Sell ₹", "USDT", "Profit ₹"]
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.markdown('<div class="alert alert-info">ℹ No trades logged yet.</div>', unsafe_allow_html=True)

# ── Section 5: Compliance Dashboard ──────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="sec-title">🛡 Compliance Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Tax estimates · Risk alerts · Trading activity</div>', unsafe_allow_html=True)

all_trades = db.execute("SELECT * FROM trades").fetchall()
total_profit   = sum(t["profit"] for t in all_trades) if all_trades else 0
total_volume   = sum(t["usdt_amount"] * t["sell_price"] for t in all_trades) if all_trades else 0
total_deals    = len(all_trades)
tax_30         = round(total_profit * 0.30, 2)
cess_4         = round(tax_30 * 0.04, 2)
total_tax      = round(tax_30 + cess_4, 2)
net_after_tax  = round(total_profit - total_tax, 2)

cp1, cp2, cp3, cp4 = st.columns(4)
with cp1: st.metric("💰 Total Profit", f"₹{total_profit:,.2f}")
with cp2: st.metric("📦 Total Deals", str(total_deals))
with cp3: st.metric("📊 Volume (INR)", f"₹{total_volume:,.0f}")
with cp4: st.metric("🧾 Est. Tax (30%+4%)", f"₹{total_tax:,.2f}", delta=f"Net: ₹{net_after_tax:,.2f}")

# Risk alerts
st.markdown("**Risk Alerts**")
if total_profit > 500000:
    st.markdown('<div class="alert alert-danger">🚨 HIGH PROFIT: Mandatory tax filing required above ₹5L</div>', unsafe_allow_html=True)
elif total_profit > 100000:
    st.markdown('<div class="alert alert-warn">⚠ Profit exceeds ₹1L — recommend consulting a CA</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="alert alert-info">✅ Profit within low-risk range</div>', unsafe_allow_html=True)

if total_deals > 50:
    st.markdown('<div class="alert alert-warn">⚠ High trade frequency — ensure KYC documentation is complete</div>', unsafe_allow_html=True)

# ── Section 6: Tax Report ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="sec-title">📑 Auto Tax Report · India FY</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Financial Year April–March · 30% flat + 4% cess on crypto gains</div>', unsafe_allow_html=True)

now = datetime.now()
fy_start = datetime(now.year if now.month >= 4 else now.year - 1, 4, 1)
fy_end   = datetime(fy_start.year + 1, 3, 31)

fy_trades = db.execute(
    "SELECT * FROM trades WHERE ts >= ? AND ts <= ?",
    (fy_start.isoformat(), fy_end.isoformat())
).fetchall()

fy_profit  = sum(t["profit"] for t in fy_trades) if fy_trades else 0
fy_volume  = sum(t["usdt_amount"] * t["sell_price"] for t in fy_trades) if fy_trades else 0
fy_tax     = round(fy_profit * 0.30, 2)
fy_cess    = round(fy_tax * 0.04, 2)
fy_total   = round(fy_tax + fy_cess, 2)
fy_net     = round(fy_profit - fy_total, 2)

t1, t2 = st.columns(2)
with t1:
    st.markdown(f"""
    <div class="xcard xcard-accent">
    <div style="font-size:0.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;">
        FY {fy_start.year}–{fy_end.year} Summary
    </div>
    <table style="width:100%;margin-top:12px;border-collapse:collapse;font-family:'Space Mono',monospace;font-size:0.82rem;">
    <tr><td style="color:var(--muted);padding:4px 0;">Total Trades</td><td style="text-align:right;">{len(fy_trades)}</td></tr>
    <tr><td style="color:var(--muted);padding:4px 0;">Gross Volume</td><td style="text-align:right;">₹{fy_volume:,.2f}</td></tr>
    <tr><td style="color:var(--muted);padding:4px 0;">Gross Profit</td><td style="text-align:right;color:var(--green);">₹{fy_profit:,.2f}</td></tr>
    <tr><td colspan="2"><hr style="border-color:var(--border);margin:6px 0;"></td></tr>
    <tr><td style="color:var(--muted);padding:4px 0;">Tax @ 30%</td><td style="text-align:right;">₹{fy_tax:,.2f}</td></tr>
    <tr><td style="color:var(--muted);padding:4px 0;">Cess @ 4%</td><td style="text-align:right;">₹{fy_cess:,.2f}</td></tr>
    <tr><td style="color:var(--muted);padding:4px 0;font-weight:700;">Total Tax</td><td style="text-align:right;color:var(--danger);">₹{fy_total:,.2f}</td></tr>
    <tr><td style="color:var(--muted);padding:4px 0;font-weight:700;">Net After Tax</td><td style="text-align:right;color:var(--green);">₹{fy_net:,.2f}</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

with t2:
    tax_report_text = f"""XENESIS EXCHANGE — TAX REPORT
{'='*45}
Financial Year : {fy_start.year}–{fy_end.year}
Generated On   : {datetime.now().strftime('%d %b %Y %H:%M')}
Trader         : {trader_name}
{'='*45}

SUMMARY
  Total Deals        : {len(fy_trades)}
  Gross Volume (INR) : ₹{fy_volume:,.2f}
  Gross Profit       : ₹{fy_profit:,.2f}

TAX COMPUTATION (Section 115BBH)
  Base Tax @ 30%     : ₹{fy_tax:,.2f}
  Health & Ed Cess 4%: ₹{fy_cess:,.2f}
  Total Tax Payable  : ₹{fy_total:,.2f}

NET INCOME AFTER TAX: ₹{fy_net:,.2f}

{'='*45}
Note: Consult a qualified CA for filing.
Xenesis Exchange · OTC Desk · India
"""
    st.download_button(
        "⬇ Download Tax Report (.txt)",
        data=tax_report_text.encode(),
        file_name=f"xenesis_tax_{fy_start.year}_{fy_end.year}.txt",
        mime="text/plain",
    )
    st.markdown('<div class="alert alert-warn">⚠ This is an estimate only. Consult a Chartered Accountant for official filing.</div>', unsafe_allow_html=True)

# ── Section 7: Deal Quote Generator ──────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="sec-title">📋 Deal Quote Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Generate professional F2F deal quotes with unique IDs</div>', unsafe_allow_html=True)

q1, q2 = st.columns(2)
with q1:
    buyer_name  = st.text_input("Buyer Name", value="", placeholder="Full legal name")
    seller_name = st.text_input("Seller Name", value=trader_name, placeholder="Full legal name")
    q_usdt      = st.number_input("USDT Quantity", min_value=1.0, value=500.0, step=10.0, key="qq")
with q2:
    q_price = st.number_input("Agreed Price (₹/USDT)", value=float(our_sell or 85.0), step=0.01, key="qp")
    q_type  = st.radio("Transaction Type", ["BUY (Buyer purchases USDT)", "SELL (Seller purchases USDT)"], horizontal=False)
    q_city  = st.selectbox("Meeting City", list(CITY_PREMIUM.keys()), key="qcity")

if st.button("🖨 Generate Deal Quote"):
    deal_id   = str(uuid.uuid4()).upper()[:16]
    q_total   = round(q_usdt * q_price, 2)
    q_time    = datetime.now().strftime("%d %B %Y, %H:%M IST")
    q_type_str = "BUY" if "BUY" in q_type else "SELL"

    quote = f"""
╔══════════════════════════════════════════════════════╗
║           XENESIS EXCHANGE — F2F DEAL QUOTE          ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  DEAL ID    : {deal_id:<38}║
║  DATE/TIME  : {q_time:<38}║
║  LOCATION   : {q_city:<38}║
║  TYPE       : {q_type_str} USDT{' '*34}║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  BUYER      : {(buyer_name or 'N/A'):<38}║
║  SELLER     : {(seller_name or 'N/A'):<38}║
╠══════════════════════════════════════════════════════╣
║  USDT QTY   : {str(q_usdt) + ' USDT':<38}║
║  RATE       : ₹{str(q_price) + '/USDT':<37}║
║  TOTAL      : ₹{str(f'{q_total:,.2f}'):<37}║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  BUYER SIGNATURE  : ____________________________     ║
║                                                      ║
║  SELLER SIGNATURE : ____________________________     ║
║                                                      ║
║  WITNESS NAME     : ____________________________     ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  This quote is valid for 15 minutes from issue time. ║
║  Xenesis Exchange · OTC Desk · India                 ║
╚══════════════════════════════════════════════════════╝
""".strip()

    st.markdown(f'<div class="quote-box">{quote}</div>', unsafe_allow_html=True)

    st.download_button(
        "⬇ Download Quote (.txt)",
        data=quote.encode(),
        file_name=f"xenesis_quote_{deal_id}.txt",
        mime="text/plain",
    )

    # PDF Invoice
    st.markdown("---")
    st.markdown("**📄 PDF Invoice**")
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()

        BG   = colors.HexColor("#08090d")
        ACC  = colors.HexColor("#00e5b0")
        DARK = colors.HexColor("#0f111a")
        MUTED= colors.HexColor("#6b7394")
        WHITE= colors.white

        title_s = ParagraphStyle("title", parent=styles["Title"],
                                 fontSize=22, textColor=ACC, spaceAfter=4,
                                 fontName="Helvetica-Bold", alignment=TA_CENTER)
        sub_s   = ParagraphStyle("sub", parent=styles["Normal"],
                                 fontSize=9, textColor=MUTED, alignment=TA_CENTER, spaceAfter=16)
        head_s  = ParagraphStyle("head", parent=styles["Normal"],
                                 fontSize=10, textColor=ACC, fontName="Helvetica-Bold", spaceAfter=6)
        body_s  = ParagraphStyle("body", parent=styles["Normal"],
                                 fontSize=9, textColor=WHITE, spaceAfter=4)
        small_s = ParagraphStyle("small", parent=styles["Normal"],
                                 fontSize=8, textColor=MUTED, alignment=TA_CENTER)

        story = []
        story.append(Paragraph("⬡ XENESIS EXCHANGE", title_s))
        story.append(Paragraph("OTC CRYPTO TRADING DESK · INDIA", sub_s))
        story.append(HRFlowable(width="100%", thickness=1, color=ACC))
        story.append(Spacer(1, 0.4*cm))

        info_data = [
            ["Deal ID:", deal_id,          "Date:", q_time],
            ["Buyer:",  buyer_name or "N/A", "Seller:", seller_name or "N/A"],
            ["City:",   q_city,             "Type:", q_type_str],
        ]
        it = Table(info_data, colWidths=[3*cm, 6.5*cm, 2.5*cm, 5*cm])
        it.setStyle(TableStyle([
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("TEXTCOLOR",  (0,0), (0,-1), MUTED),
            ("TEXTCOLOR",  (2,0), (2,-1), MUTED),
            ("TEXTCOLOR",  (1,0), (1,-1), WHITE),
            ("TEXTCOLOR",  (3,0), (3,-1), WHITE),
            ("FONTNAME",   (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME",   (2,0), (2,-1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story.append(it)
        story.append(Spacer(1, 0.4*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED))
        story.append(Spacer(1, 0.4*cm))

        story.append(Paragraph("TRANSACTION DETAILS", head_s))
        deal_data = [
            ["USDT Quantity", "Rate (INR/USDT)", "Total (INR)"],
            [f"{q_usdt:,.4f} USDT", f"₹{q_price:,.2f}", f"₹{q_total:,.2f}"],
        ]
        dt = Table(deal_data, colWidths=[5*cm, 5*cm, 7*cm])
        dt.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), DARK),
            ("TEXTCOLOR",     (0,0), (-1,0), ACC),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 10),
            ("BACKGROUND",    (0,1), (-1,-1), BG),
            ("TEXTCOLOR",     (0,1), (-1,-1), WHITE),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("GRID",          (0,0), (-1,-1), 0.5, MUTED),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [BG, DARK]),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
        ]))
        story.append(dt)
        story.append(Spacer(1, 0.6*cm))

        story.append(Paragraph("SIGNATURES", head_s))
        sig_data = [
            ["Buyer Signature", "Seller Signature", "Witness"],
            ["\n\n______________________", "\n\n______________________", "\n\n______________________"],
            [buyer_name or "Name: ___________", seller_name or "Name: ___________", "Name: ___________"],
        ]
        st_tbl = Table(sig_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
        st_tbl.setStyle(TableStyle([
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("TEXTCOLOR",     (0,0), (-1,0), MUTED),
            ("TEXTCOLOR",     (0,1), (-1,-1), WHITE),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("GRID",          (0,0), (-1,-1), 0.3, MUTED),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
        ]))
        story.append(st_tbl)
        story.append(Spacer(1, 0.6*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(
            "This invoice is generated by Xenesis Exchange OTC Desk. Valid for 15 minutes from issue time. "
            "Consult a CA for tax compliance. © Xenesis Exchange · India",
            small_s
        ))

        doc.build(story)
        buf.seek(0)
        st.download_button(
            "⬇ Download PDF Invoice",
            data=buf.read(),
            file_name=f"xenesis_invoice_{deal_id}.pdf",
            mime="application/pdf",
        )
        st.success("✅ PDF invoice ready for download!")
    except ImportError:
        st.warning("ReportLab not installed. Run: pip install reportlab")
    except Exception as ex:
        st.error(f"PDF generation error: {ex}")

# ── Auto-refresh ──────────────────────────────────────────────────────────────
if auto_refresh:
    st.markdown("---")
    st.caption("⚡ Auto-refresh active · Updates every 10 seconds")
    time.sleep(10)
    st.rerun()
