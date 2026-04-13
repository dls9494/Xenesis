import streamlit as st
import requests
import sqlite3
import numpy as np
import uuid
from datetime import datetime
import io
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Xenesis Exchange",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── PREMIUM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Playfair+Display:wght@400;500;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

/* ── RESET & ROOTS ── */
:root {
  --navy:     #080c14;
  --navy2:    #0d1220;
  --navy3:    #111827;
  --navy4:    #1a2235;
  --gold:     #c9a84c;
  --gold2:    #e8c96d;
  --gold3:    #f5e0a0;
  --goldglow: rgba(201,168,76,0.18);
  --teal:     #0ea5a0;
  --teal2:    #14d4ce;
  --green:    #22c55e;
  --red:      #ef4444;
  --amber:    #f59e0b;
  --text:     #e2e8f4;
  --muted:    #64748b;
  --muted2:   #94a3b8;
  --border:   rgba(201,168,76,0.12);
  --border2:  rgba(255,255,255,0.06);
  --glass:    rgba(13,18,32,0.7);
  --shadow:   0 8px 32px rgba(0,0,0,0.5);
  --r:        10px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body { scroll-behavior: smooth; }

/* ── GLOBAL BASE ── */
.stApp {
  background: var(--navy) !important;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(201,168,76,0.06) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 90% 80%, rgba(14,165,160,0.04) 0%, transparent 60%),
    linear-gradient(180deg, #080c14 0%, #06090f 100%) !important;
  min-height: 100vh;
}

[class*="css"], html, body {
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text) !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

[data-testid="stSidebarNav"] { display: none !important; }

/* collapse sidebar completely */
[data-testid="stSidebar"] {
  display: none !important;
}
section[data-testid="stSidebarContent"] { display: none !important; }

/* ── MAIN CONTENT PADDING ── */
.main .block-container {
  padding: 0 2rem 3rem 2rem !important;
  max-width: 1400px !important;
}

/* ── TOPBAR ── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 0 16px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 28px;
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(8,12,20,0.95);
  backdrop-filter: blur(20px);
}
.topbar-logo {
  display: flex;
  align-items: center;
  gap: 14px;
}
.topbar-diamond {
  font-size: 1.6rem;
  color: var(--gold);
  filter: drop-shadow(0 0 8px rgba(201,168,76,0.6));
  animation: pulse-gold 3s ease-in-out infinite;
}
@keyframes pulse-gold {
  0%, 100% { filter: drop-shadow(0 0 6px rgba(201,168,76,0.5)); }
  50% { filter: drop-shadow(0 0 16px rgba(201,168,76,0.9)); }
}
.topbar-name {
  font-family: 'Playfair Display', serif;
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--gold2);
  letter-spacing: 0.02em;
  line-height: 1;
}
.topbar-tag {
  font-size: 0.62rem;
  color: var(--muted);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-top: 2px;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}
.topbar-time {
  font-family: 'DM Mono', monospace;
  font-size: 0.8rem;
  color: var(--muted2);
  letter-spacing: 0.05em;
}
.status-dot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  color: var(--green);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.status-dot::before {
  content: '';
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 8px var(--green);
  animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* ── TICKER BAR ── */
.ticker-wrap {
  background: var(--navy2);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  padding: 8px 0;
  margin-bottom: 28px;
}
.ticker-inner {
  display: flex;
  gap: 48px;
  padding: 0 24px;
  overflow-x: auto;
  scrollbar-width: none;
}
.ticker-inner::-webkit-scrollbar { display: none; }
.ticker-item {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  flex-shrink: 0;
}
.ticker-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.ticker-val {
  font-family: 'DM Mono', monospace;
  font-size: 0.82rem;
  color: var(--text);
  font-weight: 500;
}
.ticker-up { color: var(--green); }
.ticker-down { color: var(--red); }
.ticker-sep { color: var(--border); font-size: 0.9rem; }

/* ── SECTION HEADER ── */
.section-header {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin: 36px 0 20px 0;
}
.section-num {
  font-family: 'Playfair Display', serif;
  font-size: 2.8rem;
  font-weight: 400;
  color: var(--border);
  line-height: 1;
  margin-bottom: -4px;
}
.section-text {}
.section-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--gold2);
  line-height: 1.2;
}
.section-sub {
  font-size: 0.75rem;
  color: var(--muted);
  letter-spacing: 0.04em;
  margin-top: 2px;
}
.section-rule {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--gold) 0%, transparent 100%);
  margin-bottom: 6px;
  opacity: 0.3;
}

/* ── GLASS CARD ── */
.gcard {
  background: linear-gradient(135deg, rgba(13,18,32,0.9) 0%, rgba(17,24,39,0.8) 100%);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 22px 24px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.gcard::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(201,168,76,0.03) 0%, transparent 60%);
  pointer-events: none;
}
.gcard:hover {
  border-color: rgba(201,168,76,0.25);
  box-shadow: 0 0 24px rgba(201,168,76,0.06);
}
.gcard-gold  { border-left: 2px solid var(--gold); }
.gcard-teal  { border-left: 2px solid var(--teal2); }
.gcard-red   { border-left: 2px solid var(--red); }
.gcard-green { border-left: 2px solid var(--green); }
.gcard-amber { border-left: 2px solid var(--amber); }

/* ── STAT CARD ── */
.stat-card {
  background: linear-gradient(145deg, var(--navy3) 0%, var(--navy2) 100%);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 20px 20px 18px;
  position: relative;
  overflow: hidden;
}
.stat-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--gold) 0%, var(--teal) 100%);
  opacity: 0.6;
}
.stat-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 10px;
}
.stat-value {
  font-family: 'DM Mono', monospace;
  font-size: 1.75rem;
  font-weight: 500;
  color: var(--gold2);
  letter-spacing: -0.02em;
  line-height: 1;
}
.stat-value-sm {
  font-family: 'DM Mono', monospace;
  font-size: 1.3rem;
  font-weight: 500;
  color: var(--text);
}
.stat-delta {
  font-size: 0.73rem;
  margin-top: 6px;
  color: var(--muted2);
  font-family: 'DM Mono', monospace;
}
.stat-delta.up { color: var(--green); }
.stat-delta.dn { color: var(--red); }

/* ── PRICE DISPLAY ── */
.price-hero {
  font-family: 'DM Mono', monospace;
  font-size: 2.6rem;
  font-weight: 300;
  color: var(--gold2);
  letter-spacing: -0.03em;
  line-height: 1;
  text-shadow: 0 0 30px rgba(201,168,76,0.3);
}
.price-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--muted);
  margin-bottom: 8px;
}

/* ── TABLE ── */
.x-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}
.x-table th {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  font-weight: 600;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border2);
  text-align: left;
}
.x-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border2);
  font-family: 'DM Mono', monospace;
  font-size: 0.8rem;
  color: var(--text);
}
.x-table tr:last-child td { border-bottom: none; }
.x-table tr:hover td { background: rgba(201,168,76,0.03); }
.x-table .td-muted { color: var(--muted2); }
.x-table .td-gold  { color: var(--gold2); }
.x-table .td-green { color: var(--green); }
.x-table .td-red   { color: var(--red); }

/* ── BADGE ── */
.badge {
  display: inline-flex; align-items: center;
  padding: 3px 9px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.badge-gold  { background: rgba(201,168,76,0.12); color: var(--gold2); border: 1px solid rgba(201,168,76,0.2); }
.badge-green { background: rgba(34,197,94,0.1);   color: var(--green); border: 1px solid rgba(34,197,94,0.2); }
.badge-red   { background: rgba(239,68,68,0.1);   color: var(--red);   border: 1px solid rgba(239,68,68,0.2); }
.badge-teal  { background: rgba(14,165,160,0.1);  color: var(--teal2); border: 1px solid rgba(14,165,160,0.2); }
.badge-amber { background: rgba(245,158,11,0.1);  color: var(--amber); border: 1px solid rgba(245,158,11,0.2); }

/* ── ALERT ── */
.x-alert {
  border-radius: 8px;
  padding: 13px 16px 13px 14px;
  margin: 10px 0;
  font-size: 0.82rem;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  line-height: 1.5;
}
.x-alert-icon { font-size: 1rem; margin-top: 1px; flex-shrink: 0; }
.x-alert-info  { background: rgba(14,165,160,0.07); border: 1px solid rgba(14,165,160,0.2); color: var(--teal2); }
.x-alert-warn  { background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.2); color: var(--amber); }
.x-alert-danger{ background: rgba(239,68,68,0.07);  border: 1px solid rgba(239,68,68,0.2);  color: var(--red); }

/* ── KV ROW ── */
.kv-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 9px 0;
  border-bottom: 1px solid var(--border2);
  font-size: 0.83rem;
}
.kv-row:last-child { border-bottom: none; }
.kv-key   { color: var(--muted2); }
.kv-value { font-family: 'DM Mono', monospace; color: var(--text); }
.kv-gold  { color: var(--gold2); font-weight: 500; }
.kv-green { color: var(--green); }
.kv-red   { color: var(--red); }

/* ── DIVIDER ── */
.x-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--border) 30%, var(--border) 70%, transparent 100%);
  margin: 4px 0 16px;
}

/* ── QUOTE BOX ── */
.quote-doc {
  background: linear-gradient(160deg, #0d1220 0%, #111827 100%);
  border: 1px solid rgba(201,168,76,0.25);
  border-radius: 12px;
  padding: 32px 36px;
  font-family: 'DM Mono', monospace;
  font-size: 0.78rem;
  line-height: 1.9;
  color: var(--text);
  white-space: pre;
  overflow-x: auto;
  box-shadow: inset 0 1px 0 rgba(201,168,76,0.1), 0 8px 32px rgba(0,0,0,0.4);
  position: relative;
}
.quote-doc::before {
  content: 'XENESIS EXCHANGE · OFFICIAL DOCUMENT';
  position: absolute;
  top: 12px; right: 20px;
  font-size: 0.6rem;
  letter-spacing: 0.15em;
  color: rgba(201,168,76,0.4);
}

/* ── STREAMLIT OVERRIDES ── */
hr { border-color: var(--border2) !important; }

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, #1a1e2e 0%, #1e2438 100%) !important;
  color: var(--gold2) !important;
  border: 1px solid rgba(201,168,76,0.35) !important;
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.06em !important;
  padding: 10px 22px !important;
  transition: all 0.25s ease !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #1e2438 0%, #252b42 100%) !important;
  border-color: var(--gold) !important;
  box-shadow: 0 0 16px rgba(201,168,76,0.2), 0 4px 12px rgba(0,0,0,0.4) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Primary CTA button */
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--gold) 0%, #a8832e 100%) !important;
  color: #06090f !important;
  border-color: transparent !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, var(--gold2) 0%, var(--gold) 100%) !important;
  box-shadow: 0 0 20px rgba(201,168,76,0.35), 0 4px 12px rgba(0,0,0,0.4) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
  background: var(--navy3) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 0.85rem !important;
  padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
  border-color: rgba(201,168,76,0.4) !important;
  box-shadow: 0 0 0 2px rgba(201,168,76,0.1) !important;
}

/* Select */
.stSelectbox > div > div {
  background: var(--navy3) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
}

/* Labels */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stTextArea label, .stRadio label, [data-testid="stWidgetLabel"] {
  color: var(--muted2) !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
}

/* Radio */
.stRadio > div { gap: 8px !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: var(--text) !important; font-size: 0.85rem !important; }

/* Metrics */
[data-testid="stMetric"] {
  background: linear-gradient(145deg, var(--navy3), var(--navy2)) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding: 18px 20px !important;
  position: relative;
  overflow: hidden;
}
[data-testid="stMetric"]::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--gold) 0%, var(--teal) 100%);
  opacity: 0.5;
}
[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-size: 0.65rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.12em !important;
  font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
  color: var(--gold2) !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 1.65rem !important;
  font-weight: 400 !important;
  letter-spacing: -0.02em !important;
}
[data-testid="stMetricDelta"] {
  font-family: 'DM Mono', monospace !important;
  font-size: 0.75rem !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
  background: var(--navy2) !important;
  color: var(--muted) !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
}
[data-testid="stDataFrame"] td { font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important; }

/* Expander */
[data-testid="stExpander"] {
  background: var(--navy3) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
}
[data-testid="stExpander"] summary {
  color: var(--muted2) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
}

/* Toggle */
.stToggle { color: var(--text) !important; }

/* Download button */
.stDownloadButton > button {
  background: linear-gradient(135deg, rgba(14,165,160,0.15) 0%, rgba(14,165,160,0.05) 100%) !important;
  color: var(--teal2) !important;
  border: 1px solid rgba(14,165,160,0.3) !important;
  border-radius: 8px !important;
  font-size: 0.8rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.05em !important;
}
.stDownloadButton > button:hover {
  background: rgba(14,165,160,0.2) !important;
  box-shadow: 0 0 16px rgba(14,165,160,0.2) !important;
}

/* Success / error messages */
[data-testid="stSuccess"] { background: rgba(34,197,94,0.08) !important; border: 1px solid rgba(34,197,94,0.2) !important; border-radius: 8px !important; color: var(--green) !important; }
[data-testid="stError"]   { background: rgba(239,68,68,0.08) !important; border: 1px solid rgba(239,68,68,0.2) !important; border-radius: 8px !important; color: var(--red) !important; }
[data-testid="stWarning"] { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.2) !important; border-radius: 8px !important; color: var(--amber) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--navy2); }
::-webkit-scrollbar-thumb { background: var(--navy4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(201,168,76,0.4); }

/* Caption */
.stCaption { color: var(--muted) !important; font-size: 0.72rem !important; }

/* Number input buttons */
.stNumberInput [data-testid="stNumberInputDecrementButton"],
.stNumberInput [data-testid="stNumberInputIncrementButton"] {
  color: var(--gold) !important;
  background: var(--navy4) !important;
  border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────────────────────────
@st.cache_resource
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

# ── Binance P2P ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
    def fetch_binance_p2p_filtered(side: str, min_usdt: float = 5000):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    payload = {
        "asset": "USDT",
        "fiat": "INR",
        "merchantCheck": False,
        "page": 1,
        "payTypes": [],
        "publisherType": None,
        "rows": 50,
        "tradeType": side
    }

    try:
        r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
        data = r.json().get("data", [])

        ads = []
        total_value = 0
        total_qty = 0

        for ad in data:
            adv = ad["adv"]

            price = float(adv["price"])
            available = float(adv.get("surplusAmount", 0))
            tradable = float(adv.get("tradableQuantity", 0))
            quantity = max(available, tradable)

            if quantity >= min_usdt:
                total_value += price * quantity
                total_qty += quantity

                ads.append({
                    "Trader": ad["advertiser"]["nickName"],
                    "Price": price,
                    "USDT": quantity,
                    "Min INR": adv.get("minSingleTransAmount"),
                    "Max INR": adv.get("maxSingleTransAmount"),
                })

        weighted_avg = round(total_value / total_qty, 2) if total_qty > 0 else None

        ads = sorted(ads, key=lambda x: x["USDT"], reverse=True)

        for i, ad in enumerate(ads):
            ad["Tag"] = "🐋 WHALE" if i < 3 else ""

        return ads, weighted_avg

    except Exception:
        return [], None

CITY_PREMIUM = {
    "Hyderabad": 0.003, "Mumbai": 0.005, "Delhi": 0.004,
    "Bangalore": 0.003, "Chennai": 0.004, "Kolkata": 0.002,
    "Pune": 0.003, "Ahmedabad": 0.002, "Jaipur": 0.001, "Lucknow": 0.001,
}

def predict_spread():
    rows = db.execute("SELECT ts, spread FROM market_history ORDER BY id DESC LIMIT 30").fetchall()
    if len(rows) < 5:
        return None, f"Building model… ({len(rows)}/5 samples)"
    ts_list = [datetime.fromisoformat(r["ts"]).timestamp() for r in rows][::-1]
    sp_list = [r["spread"] for r in rows][::-1]
    t0 = ts_list[0]
    x = np.array([(t - t0) / 60 for t in ts_list])
    y = np.array(sp_list)
    try:
        coeffs = np.polyfit(x, y, 2)
        poly = np.poly1d(coeffs)
        predicted = round(float(poly(x[-1] + 10)), 4)
        return predicted, None
    except Exception as e:
        return None, str(e)

# ── Session state ─────────────────────────────────────────────────────────────
if "trader_name" not in st.session_state:
    st.session_state.trader_name = "Desk Officer"
if "city" not in st.session_state:
    st.session_state.city = "Hyderabad"
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

# ── Fetch market data ─────────────────────────────────────────────────────────
buy_prices  = fetch_binance_p2p("BUY")
sell_prices = fetch_binance_p2p("SELL")

buy_avg  = round(np.average(buy_prices),  2) if buy_prices  else None
sell_avg = round(np.average(sell_prices), 2) if sell_prices else None

city    = st.session_state.city
premium = CITY_PREMIUM.get(city, 0.003)

our_buy = our_sell = spread = spread_pct = None
if buy_avg and sell_avg:
    our_buy     = round(sell_avg * (1 - premium * 0.5), 2)
    our_sell    = round(buy_avg  * (1 + premium), 2)
    spread      = round(our_sell - our_buy, 2)
    spread_pct  = round(spread / our_buy * 100, 3)
    db.execute("INSERT INTO market_history (ts, buy_avg, sell_avg, spread) VALUES (?,?,?,?)",
               (datetime.now().isoformat(), our_buy, our_sell, spread))
    db.commit()

# ── TOP BAR ───────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y  %H:%M:%S")
conn_status = "LIVE" if buy_avg else "OFFLINE"
conn_color  = "var(--green)" if buy_avg else "var(--red)"

st.markdown(f"""
<div class="topbar">
  <div class="topbar-logo">
    <div class="topbar-diamond">◈</div>
    <div>
      <div class="topbar-name">Xenesis Exchange</div>
      <div class="topbar-tag">OTC · F2F · USDT/INR · Institutional Desk</div>
    </div>
  </div>
  <div class="topbar-right">
    <div class="topbar-time">IST {now_str}</div>
    <div style="width:1px;height:20px;background:var(--border2);"></div>
    <div class="status-dot">BINANCE P2P {conn_status}</div>
    <div style="width:1px;height:20px;background:var(--border2);"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── CONTROL ROW ──────────────────────────────────────────────────────────────
cc1, cc2, cc3, cc4 = st.columns([2, 2, 1, 1])
with cc1:
    st.session_state.trader_name = st.text_input("Trader / Officer", value=st.session_state.trader_name, label_visibility="visible")
with cc2:
    st.session_state.city = st.selectbox("Operating City", list(CITY_PREMIUM.keys()),
                                          index=list(CITY_PREMIUM.keys()).index(st.session_state.city))
with cc3:
    st.session_state.auto_refresh = st.toggle("Auto-Refresh", value=st.session_state.auto_refresh)
with cc4:
    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    if st.button("⟳  Refresh Now"):
        st.cache_data.clear()
        st.rerun()

trader_name = st.session_state.trader_name
city        = st.session_state.city
premium     = CITY_PREMIUM.get(city, 0.003)

# ── TICKER BAR ───────────────────────────────────────────────────────────────
buy_str   = f"₹{our_buy:,.2f}"  if our_buy  else "—"
sell_str  = f"₹{our_sell:,.2f}" if our_sell else "—"
sprd_str  = f"₹{spread:,.2f}"  if spread   else "—"
sprdp_str = f"{spread_pct}%"   if spread_pct else "—"
mkt_b     = f"₹{buy_avg:,.2f}" if buy_avg  else "—"
mkt_s     = f"₹{sell_avg:,.2f}" if sell_avg else "—"

st.markdown(f"""
<div class="ticker-wrap">
  <div class="ticker-inner">
    <div class="ticker-item">
      <span class="ticker-label">Market Buy</span>
      <span class="ticker-val">{mkt_b}</span>
    </div>
    <span class="ticker-sep">·</span>
    <div class="ticker-item">
      <span class="ticker-label">Market Sell</span>
      <span class="ticker-val">{mkt_s}</span>
    </div>
    <span class="ticker-sep">·</span>
    <div class="ticker-item">
      <span class="ticker-label">Desk Buy Rate</span>
      <span class="ticker-val ticker-up">{buy_str}</span>
    </div>
    <span class="ticker-sep">·</span>
    <div class="ticker-item">
      <span class="ticker-label">Desk Sell Rate</span>
      <span class="ticker-val ticker-down">{sell_str}</span>
    </div>
    <span class="ticker-sep">·</span>
    <div class="ticker-item">
      <span class="ticker-label">Spread</span>
      <span class="ticker-val">{sprd_str}</span>
    </div>
    <span class="ticker-sep">·</span>
    <div class="ticker-item">
      <span class="ticker-label">Spread %</span>
      <span class="ticker-val">{sprdp_str}</span>
    </div>
    <span class="ticker-sep">·</span>
    <div class="ticker-item">
      <span class="ticker-label">City</span>
      <span class="ticker-val">{city} +{premium*100:.1f}%</span>
    </div>
    <span class="ticker-sep">·</span>
    <div class="ticker-item">
      <span class="ticker-label">Asset</span>
      <span class="ticker-val">USDT / INR</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — LIVE MARKET
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="section-num">01</div>
  <div class="section-text">
    <div class="section-title">Live Market Intelligence</div>
    <div class="section-sub">Binance P2P · USDT/INR · Weighted Average · Real-time</div>
  </div>
  <div class="section-rule"></div>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    delta_b = f"Market: ₹{sell_avg}" if sell_avg else None
    st.metric("Desk Buy Rate", buy_str, delta=delta_b)
with m2:
    delta_s = f"Market: ₹{buy_avg}" if buy_avg else None
    st.metric("Desk Sell Rate", sell_str, delta=delta_s)
with m3:
    st.metric("Spread (INR)", sprd_str)
with m4:
    st.metric("Spread %", sprdp_str)

if not buy_avg:
    st.markdown("""<div class="x-alert x-alert-warn">
      <span class="x-alert-icon">⚠</span>
      <span>Binance P2P data unavailable. Check your internet connection or try refreshing.</span>
    </div>""", unsafe_allow_html=True)

with st.expander("View Full Order Book — Binance P2P"):
    if buy_prices and sell_prices:
        ob1, ob2 = st.columns(2)
        with ob1:
            st.markdown("""
            <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--green);font-weight:600;margin-bottom:12px;">
              ▲ BUY ORDERS (Market Buying USDT)
            </div>""", unsafe_allow_html=True)
            rows_html = "".join([f"""
              <tr>
                <td class="td-muted">#{i}</td>
                <td class="td-gold">₹{p:,.2f}</td>
                <td><div style="height:6px;background:rgba(34,197,94,{0.6-i*0.05:.2f});border-radius:3px;width:{100-i*8}%;"></div></td>
              </tr>""" for i, p in enumerate(buy_prices, 1)])
            st.markdown(f'<table class="x-table"><thead><tr><th>#</th><th>Price</th><th>Depth</th></tr></thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)
        with ob2:
            st.markdown("""
            <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--red);font-weight:600;margin-bottom:12px;">
              ▼ SELL ORDERS (Market Selling USDT)
            </div>""", unsafe_allow_html=True)
            rows_html = "".join([f"""
              <tr>
                <td class="td-muted">#{i}</td>
                <td class="td-gold">₹{p:,.2f}</td>
                <td><div style="height:6px;background:rgba(239,68,68,{0.6-i*0.05:.2f});border-radius:3px;width:{100-i*8}%;"></div></td>
              </tr>""" for i, p in enumerate(sell_prices, 1)])
            st.markdown(f'<table class="x-table"><thead><tr><th>#</th><th>Price</th><th>Depth</th></tr></thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — AI PREDICTION
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="section-num">02</div>
  <div class="section-text">
    <div class="section-title">AI Spread Prediction Engine</div>
    <div class="section-sub">Polynomial Regression (Degree 2) · 10-minute forward projection · SQLite history</div>
  </div>
  <div class="section-rule"></div>
</div>
""", unsafe_allow_html=True)

pred_spread, pred_err = predict_spread()
hist_count = db.execute("SELECT COUNT(*) FROM market_history").fetchone()[0]

ai1, ai2, ai3, ai4 = st.columns(4)
with ai1:
    st.metric("Current Spread", sprd_str)
with ai2:
    if pred_spread is not None:
        delta_pred = round(pred_spread - spread, 4) if spread else None
        st.metric("Predicted (T+10m)", f"₹{pred_spread:,.4f}", delta=f"Δ ₹{delta_pred}" if delta_pred else None)
    else:
        st.metric("Predicted (T+10m)", "Building…")
with ai3:
    if pred_spread and spread:
        direction = "Rising ▲" if pred_spread > spread else "Falling ▼"
        st.metric("Trend Signal", direction)
    else:
        st.metric("Trend Signal", "Pending")
with ai4:
    st.metric("History Samples", str(hist_count))

if pred_err and not pred_spread:
    st.markdown(f"""<div class="x-alert x-alert-info">
      <span class="x-alert-icon">ℹ</span>
      <span>{pred_err} — Model trains automatically as market data accumulates.</span>
    </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — F2F DEAL ENGINE
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="section-num">03</div>
  <div class="section-text">
    <div class="section-title">F2F Deal Execution Engine</div>
    <div class="section-sub">Optimal strategy calculator for face-to-face USDT trading</div>
  </div>
  <div class="section-rule"></div>
</div>
""", unsafe_allow_html=True)

de1, de2 = st.columns([1, 1], gap="large")
with de1:
    st.markdown('<div class="gcard gcard-gold">', unsafe_allow_html=True)
    capital   = st.number_input("Capital (INR ₹)", min_value=1000.0, value=100000.0, step=5000.0, format="%.0f")
    deal_type = st.radio("Transaction Mode", ["◈  Buy USDT from counterparty", "◈  Sell USDT to counterparty"], horizontal=False)
    st.markdown('</div>', unsafe_allow_html=True)

with de2:
    if our_buy and our_sell:
        is_buy = "Buy" in deal_type
        if is_buy:
            qty       = round(capital / our_buy, 4)
            sell_val  = round(qty * our_sell, 2)
            est_profit = round(sell_val - capital, 2)
            rate_label = "Recommended Buy Rate"
            rate_val   = our_buy
        else:
            qty        = round(capital / our_sell, 4)
            cost_basis = round(qty * our_buy, 2)
            est_profit = round(capital - cost_basis, 2)
            rate_label = "Recommended Sell Rate"
            rate_val   = our_sell

        profit_color = "kv-green" if est_profit >= 0 else "kv-red"
        inr_recv = f"₹{capital:,.2f}" if not is_buy else f"₹{sell_val:,.2f}"

        st.markdown(f"""
        <div class="gcard gcard-gold">
          <div class="price-label">{rate_label}</div>
          <div class="price-hero">₹{rate_val:,.2f}</div>
          <div style="margin-top:4px;margin-bottom:16px;">
            <span class="badge badge-gold">{city}</span>
            &nbsp;<span class="badge badge-teal">+{premium*100:.1f}% Premium</span>
          </div>
          <div class="x-divider"></div>
          <div class="kv-row"><span class="kv-key">USDT Quantity</span><span class="kv-value">{qty:,.4f} USDT</span></div>
          <div class="kv-row"><span class="kv-key">{"INR to Receive" if not is_buy else "Current Value @ Sell"}</span><span class="kv-value kv-gold">{inr_recv}</span></div>
          {'<div class="kv-row"><span class="kv-key">Cost Basis</span><span class="kv-value">₹'+f'{capital:,.2f}'+'</span></div>' if not is_buy else ''}
          <div class="kv-row" style="border:none;margin-top:6px;padding-top:10px;border-top:1px solid var(--border);">
            <span class="kv-key" style="font-weight:600;">Estimated Profit</span>
            <span class="kv-value {profit_color}" style="font-size:1.1rem;">₹{est_profit:,.2f}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""<div class="x-alert x-alert-warn">
          <span class="x-alert-icon">⚠</span>
          <span>Market data unavailable — cannot compute optimal deal parameters.</span>
        </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — TRADE LOGGER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="section-num">04</div>
  <div class="section-text">
    <div class="section-title">Trade Ledger</div>
    <div class="section-sub">Immutable SQLite record · Every deal logged with UUID · Compliance-ready</div>
  </div>
  <div class="section-rule"></div>
</div>
""", unsafe_allow_html=True)

with st.expander("＋  Log New Trade", expanded=False):
    st.markdown('<div class="gcard">', unsafe_allow_html=True)
    lg1, lg2, lg3 = st.columns(3)
    with lg1:
        log_buy  = st.number_input("Buy Price (₹)", value=float(our_buy or 84.0), step=0.01, format="%.2f", key="lb")
        log_sell = st.number_input("Sell Price (₹)", value=float(our_sell or 85.5), step=0.01, format="%.2f", key="ls")
    with lg2:
        log_usdt   = st.number_input("USDT Amount", min_value=1.0, value=100.0, step=10.0, key="lu")
        log_profit = round((log_sell - log_buy) * log_usdt, 2)
        profit_col = "var(--green)" if log_profit >= 0 else "var(--red)"
        st.markdown(f"""
        <div style="margin-top:6px;">
          <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);font-weight:600;margin-bottom:6px;">Calculated Profit</div>
          <div style="font-family:'DM Mono',monospace;font-size:1.5rem;color:{profit_col};">₹{log_profit:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with lg3:
        log_trader = st.text_input("Officer Name", value=trader_name, key="lo")
        log_city2  = st.selectbox("City", list(CITY_PREMIUM.keys()), key="lc")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✦  Commit Trade to Ledger"):
        deal_id = str(uuid.uuid4())[:12].upper()
        db.execute(
            "INSERT INTO trades (ts, trader, buy_price, sell_price, usdt_amount, profit, city, deal_id) VALUES (?,?,?,?,?,?,?,?)",
            (datetime.now().isoformat(), log_trader, log_buy, log_sell, log_usdt, log_profit, log_city2, deal_id)
        )
        db.commit()
        st.success(f"✦ Trade committed — Deal ID: {deal_id}")

trades = db.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 20").fetchall()
if trades:
    import pandas as pd
    df = pd.DataFrame([dict(t) for t in trades])
    df["ts"] = pd.to_datetime(df["ts"]).dt.strftime("%d %b %H:%M")
    df = df[["ts", "deal_id", "trader", "city", "buy_price", "sell_price", "usdt_amount", "profit"]]
    df.columns = ["Timestamp", "Deal ID", "Officer", "City", "Buy ₹", "Sell ₹", "USDT", "Profit ₹"]
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.markdown("""<div class="x-alert x-alert-info">
      <span class="x-alert-icon">ℹ</span>
      <span>No trades recorded yet. Use the form above to log your first deal.</span>
    </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — COMPLIANCE
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="section-num">05</div>
  <div class="section-text">
    <div class="section-title">Compliance & Risk Monitor</div>
    <div class="section-sub">Tax estimation · Profit tracking · Risk level · KYC flags</div>
  </div>
  <div class="section-rule"></div>
</div>
""", unsafe_allow_html=True)

all_trades   = db.execute("SELECT * FROM trades").fetchall()
total_profit = sum(t["profit"] for t in all_trades) if all_trades else 0
total_volume = sum(t["usdt_amount"] * t["sell_price"] for t in all_trades) if all_trades else 0
total_deals  = len(all_trades)
tax_30       = round(total_profit * 0.30, 2)
cess_4       = round(tax_30 * 0.04, 2)
total_tax    = round(tax_30 + cess_4, 2)
net_after    = round(total_profit - total_tax, 2)

cp1, cp2, cp3, cp4 = st.columns(4)
with cp1: st.metric("Cumulative Profit", f"₹{total_profit:,.2f}")
with cp2: st.metric("Total Deals", str(total_deals))
with cp3: st.metric("Gross Volume", f"₹{total_volume:,.0f}")
with cp4: st.metric("Est. Tax Liability", f"₹{total_tax:,.2f}", delta=f"Net: ₹{net_after:,.2f}")

# Risk alerts
st.markdown("""<div style="margin-top:16px;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);font-weight:600;margin-bottom:10px;">Risk Indicators</div>""", unsafe_allow_html=True)
if total_profit > 500000:
    st.markdown("""<div class="x-alert x-alert-danger">
      <span class="x-alert-icon">🔴</span>
      <span><strong>CRITICAL:</strong> Profit exceeds ₹5,00,000. Mandatory ITR filing under Section 115BBH. Engage a Chartered Accountant immediately.</span>
    </div>""", unsafe_allow_html=True)
elif total_profit > 100000:
    st.markdown("""<div class="x-alert x-alert-warn">
      <span class="x-alert-icon">⚠</span>
      <span><strong>ADVISORY:</strong> Profit exceeds ₹1,00,000. Consider consulting a CA. Keep all trade documentation ready.</span>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div class="x-alert x-alert-info">
      <span class="x-alert-icon">✦</span>
      <span><strong>CLEAR:</strong> Current profit levels within low-risk threshold. Maintain ongoing documentation.</span>
    </div>""", unsafe_allow_html=True)

if total_deals > 50:
    st.markdown("""<div class="x-alert x-alert-warn">
      <span class="x-alert-icon">⚠</span>
      <span><strong>HIGH FREQUENCY:</strong> Trade count exceeds 50. Ensure full KYC documentation for all counterparties.</span>
    </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6 — TAX REPORT
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="section-num">06</div>
  <div class="section-text">
    <div class="section-title">India Tax Report — FY Computation</div>
    <div class="section-sub">Section 115BBH · 30% flat tax + 4% health & education cess · April–March</div>
  </div>
  <div class="section-rule"></div>
</div>
""", unsafe_allow_html=True)

now      = datetime.now()
fy_start = datetime(now.year if now.month >= 4 else now.year - 1, 4, 1)
fy_end   = datetime(fy_start.year + 1, 3, 31)

fy_trades  = db.execute("SELECT * FROM trades WHERE ts >= ? AND ts <= ?",
                         (fy_start.isoformat(), fy_end.isoformat())).fetchall()
fy_profit  = sum(t["profit"] for t in fy_trades) if fy_trades else 0
fy_volume  = sum(t["usdt_amount"] * t["sell_price"] for t in fy_trades) if fy_trades else 0
fy_tax     = round(fy_profit * 0.30, 2)
fy_cess    = round(fy_tax * 0.04, 2)
fy_total   = round(fy_tax + fy_cess, 2)
fy_net     = round(fy_profit - fy_total, 2)

tx1, tx2 = st.columns([3, 2], gap="large")
with tx1:
    st.markdown(f"""
    <div class="gcard gcard-gold">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <div>
          <div class="price-label">Financial Year</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.2rem;color:var(--gold2);">
            FY {fy_start.year}–{str(fy_end.year)[2:]}
          </div>
        </div>
        <span class="badge badge-gold">Section 115BBH</span>
      </div>
      <div class="x-divider"></div>
      <div class="kv-row"><span class="kv-key">Trades in FY</span><span class="kv-value">{len(fy_trades)}</span></div>
      <div class="kv-row"><span class="kv-key">Gross Volume</span><span class="kv-value">₹{fy_volume:,.2f}</span></div>
      <div class="kv-row"><span class="kv-key">Gross Profit</span><span class="kv-value kv-green">₹{fy_profit:,.2f}</span></div>
      <div class="x-divider"></div>
      <div class="kv-row"><span class="kv-key">Base Tax @ 30%</span><span class="kv-value">₹{fy_tax:,.2f}</span></div>
      <div class="kv-row"><span class="kv-key">H&E Cess @ 4%</span><span class="kv-value">₹{fy_cess:,.2f}</span></div>
      <div class="kv-row" style="border:none;padding-top:12px;border-top:1px solid var(--border);margin-top:4px;">
        <span class="kv-key" style="font-weight:600;color:var(--text);">Total Tax Payable</span>
        <span class="kv-value kv-red" style="font-size:1.15rem;">₹{fy_total:,.2f}</span>
      </div>
      <div class="kv-row" style="border:none;">
        <span class="kv-key" style="font-weight:600;color:var(--text);">Net After Tax</span>
        <span class="kv-value kv-green" style="font-size:1.15rem;">₹{fy_net:,.2f}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with tx2:
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="x-alert x-alert-warn">
      <span class="x-alert-icon">⚠</span>
      <span>Estimates only. Consult a Chartered Accountant for official ITR filing.</span>
    </div>""", unsafe_allow_html=True)

    tax_txt = f"""XENESIS EXCHANGE — TAX REPORT
{'═'*48}
Financial Year : {fy_start.year}–{fy_end.year}
Generated On   : {datetime.now().strftime('%d %b %Y %H:%M IST')}
Officer        : {trader_name}
{'═'*48}

SUMMARY
  Total Trades         : {len(fy_trades)}
  Gross Volume (INR)   : ₹{fy_volume:,.2f}
  Gross Profit         : ₹{fy_profit:,.2f}

TAX COMPUTATION (Sec. 115BBH)
  Base Tax @ 30%       : ₹{fy_tax:,.2f}
  H&E Cess @ 4%        : ₹{fy_cess:,.2f}
  Total Tax Payable    : ₹{fy_total:,.2f}

NET INCOME AFTER TAX   : ₹{fy_net:,.2f}

{'═'*48}
Note: Consult a qualified CA for official filing.
Xenesis Exchange · OTC Desk · India
"""
    st.download_button("⬇  Download Tax Report (.txt)", data=tax_txt.encode(),
                       file_name=f"xenesis_tax_{fy_start.year}_{fy_end.year}.txt", mime="text/plain")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 7 — DEAL QUOTE + PDF
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="section-num">07</div>
  <div class="section-text">
    <div class="section-title">Deal Quote & Invoice Generator</div>
    <div class="section-sub">UUID-backed deal IDs · Signature fields · Professional PDF export</div>
  </div>
  <div class="section-rule"></div>
</div>
""", unsafe_allow_html=True)

qf1, qf2 = st.columns(2, gap="large")
with qf1:
    st.markdown('<div class="gcard">', unsafe_allow_html=True)
    buyer_name  = st.text_input("Buyer Full Name", value="", placeholder="As per KYC document")
    seller_name = st.text_input("Seller Full Name", value=trader_name, placeholder="As per KYC document")
    q_usdt = st.number_input("USDT Quantity", min_value=1.0, value=500.0, step=10.0, key="qq")
    st.markdown('</div>', unsafe_allow_html=True)

with qf2:
    st.markdown('<div class="gcard">', unsafe_allow_html=True)
    q_price = st.number_input("Agreed Rate (₹ / USDT)", value=float(our_sell or 85.0), step=0.01, format="%.2f", key="qp")
    q_type  = st.radio("Transaction Type", ["BUY — Buyer acquires USDT", "SELL — Seller acquires INR"], horizontal=False)
    q_city2 = st.selectbox("Meeting Location", list(CITY_PREMIUM.keys()), key="qcity")
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("◈  Generate Deal Quote & PDF Invoice"):
    deal_id   = str(uuid.uuid4()).upper()[:16]
    q_total   = round(q_usdt * q_price, 2)
    q_time    = datetime.now().strftime("%d %B %Y, %H:%M IST")
    q_type_str = "BUY" if "BUY" in q_type else "SELL"

    # ── Formatted Quote ──
    WIDE = 56
    def pad(text, width): return str(text)[:width].ljust(width)

    quote = (
        f"╔{'═'*WIDE}╗\n"
        f"║{'XENESIS EXCHANGE  ·  OFFICIAL DEAL QUOTE'.center(WIDE)}║\n"
        f"╠{'═'*WIDE}╣\n"
        f"║  {'DEAL ID':12}: {pad(deal_id, WIDE-16)}║\n"
        f"║  {'DATE':12}: {pad(q_time, WIDE-16)}║\n"
        f"║  {'LOCATION':12}: {pad(q_city2, WIDE-16)}║\n"
        f"║  {'TYPE':12}: {pad(q_type_str + ' USDT', WIDE-16)}║\n"
        f"╠{'═'*WIDE}╣\n"
        f"║  {'BUYER':12}: {pad(buyer_name or 'Not specified', WIDE-16)}║\n"
        f"║  {'SELLER':12}: {pad(seller_name or 'Not specified', WIDE-16)}║\n"
        f"╠{'═'*WIDE}╣\n"
        f"║  {'USDT QTY':12}: {pad(f'{q_usdt:,.4f} USDT', WIDE-16)}║\n"
        f"║  {'RATE':12}: {pad('₹' + f'{q_price:,.2f}' + ' per USDT', WIDE-16)}║\n"
        f"║  {'TOTAL':12}: {pad('₹' + f'{q_total:,.2f}', WIDE-16)}║\n"
        f"╠{'═'*WIDE}╣\n"
        f"║{'':WIDE}║\n"
        f"║  BUYER SIGNATURE  : {'_'*34}  ║\n"
        f"║{'':WIDE}║\n"
        f"║  SELLER SIGNATURE : {'_'*34}  ║\n"
        f"║{'':WIDE}║\n"
        f"║  WITNESS          : {'_'*34}  ║\n"
        f"║{'':WIDE}║\n"
        f"╠{'═'*WIDE}╣\n"
        f"║  {'Valid 15 minutes from issue time.':WIDE-2}  ║\n"
        f"║  {'Xenesis Exchange · OTC Desk · India':WIDE-2}  ║\n"
        f"╚{'═'*WIDE}╝"
    )

    st.markdown(f'<div class="quote-doc">{quote}</div>', unsafe_allow_html=True)

    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button("⬇  Download Quote (.txt)", data=quote.encode(),
                           file_name=f"xenesis_quote_{deal_id}.txt", mime="text/plain")

    # ── PDF ──
    with dl2:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                             Table, TableStyle, HRFlowable)
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4,
                                    leftMargin=2.2*cm, rightMargin=2.2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)
            styles = getSampleStyleSheet()

            C_NAVY  = colors.HexColor("#080c14")
            C_NAVY2 = colors.HexColor("#0d1220")
            C_NAVY3 = colors.HexColor("#111827")
            C_GOLD  = colors.HexColor("#c9a84c")
            C_GOLD2 = colors.HexColor("#e8c96d")
            C_MUTED = colors.HexColor("#64748b")
            C_TEXT  = colors.HexColor("#e2e8f4")
            C_GREEN = colors.HexColor("#22c55e")
            C_RED   = colors.HexColor("#ef4444")
            C_TEAL  = colors.HexColor("#0ea5a0")

            def sty(name, **kw):
                s = ParagraphStyle(name, parent=styles["Normal"], **kw)
                return s

            s_hero   = sty("hero",   fontSize=20, textColor=C_GOLD2,  fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2)
            s_sub    = sty("sub",    fontSize=8,  textColor=C_MUTED,  alignment=TA_CENTER, spaceAfter=14, leading=12)
            s_sec    = sty("sec",    fontSize=8,  textColor=C_GOLD,   fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4, letterSpacing=1.5)
            s_body   = sty("body",   fontSize=9,  textColor=C_TEXT,   spaceAfter=3, leading=13)
            s_foot   = sty("foot",   fontSize=7,  textColor=C_MUTED,  alignment=TA_CENTER, spaceBefore=6)
            s_total  = sty("total",  fontSize=12, textColor=C_GOLD2,  fontName="Helvetica-Bold", alignment=TA_CENTER)

            story = []

            # Header
            story.append(Paragraph("◈  XENESIS EXCHANGE", s_hero))
            story.append(Paragraph("OTC CRYPTOCURRENCY TRADING DESK  ·  INDIA  ·  USDT / INR", s_sub))
            story.append(HRFlowable(width="100%", thickness=1.2, color=C_GOLD, spaceAfter=12))

            # Deal meta table
            meta = [
                [Paragraph("<b>Deal ID</b>", sty("m1", fontSize=8, textColor=C_MUTED, fontName="Helvetica-Bold")),
                 Paragraph(deal_id, sty("m2", fontSize=8, textColor=C_GOLD2, fontName="Courier-Bold")),
                 Paragraph("<b>Date</b>", sty("m3", fontSize=8, textColor=C_MUTED, fontName="Helvetica-Bold")),
                 Paragraph(q_time, sty("m4", fontSize=8, textColor=C_TEXT))],
                [Paragraph("<b>Buyer</b>", sty("m5", fontSize=8, textColor=C_MUTED, fontName="Helvetica-Bold")),
                 Paragraph(buyer_name or "N/A", sty("m6", fontSize=8, textColor=C_TEXT)),
                 Paragraph("<b>Seller</b>", sty("m7", fontSize=8, textColor=C_MUTED, fontName="Helvetica-Bold")),
                 Paragraph(seller_name or "N/A", sty("m8", fontSize=8, textColor=C_TEXT))],
                [Paragraph("<b>Location</b>", sty("m9", fontSize=8, textColor=C_MUTED, fontName="Helvetica-Bold")),
                 Paragraph(q_city2, sty("m10", fontSize=8, textColor=C_TEXT)),
                 Paragraph("<b>Type</b>", sty("m11", fontSize=8, textColor=C_MUTED, fontName="Helvetica-Bold")),
                 Paragraph(q_type_str + " USDT", sty("m12", fontSize=8, textColor=C_TEAL, fontName="Helvetica-Bold"))],
            ]
            meta_tbl = Table(meta, colWidths=[2.5*cm, 6.5*cm, 2.5*cm, 5*cm])
            meta_tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,-1), C_NAVY3),
                ("ROWBACKGROUNDS", (0,0), (-1,-1), [C_NAVY3, C_NAVY2]),
                ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#1a2235")),
                ("BOTTOMPADDING",(0,0),(-1,-1), 7),
                ("TOPPADDING",  (0,0),(-1,-1), 7),
                ("LEFTPADDING", (0,0),(-1,-1), 8),
                ("ROUNDEDCORNERS", [4]),
            ]))
            story.append(meta_tbl)
            story.append(Spacer(1, 0.4*cm))

            # Transaction table
            story.append(Paragraph("TRANSACTION DETAILS", s_sec))
            tx_data = [
                [Paragraph("<b>USDT QUANTITY</b>", sty("h1", fontSize=8, textColor=C_GOLD, fontName="Helvetica-Bold", alignment=TA_CENTER)),
                 Paragraph("<b>RATE (INR/USDT)</b>", sty("h2", fontSize=8, textColor=C_GOLD, fontName="Helvetica-Bold", alignment=TA_CENTER)),
                 Paragraph("<b>TOTAL AMOUNT (INR)</b>", sty("h3", fontSize=8, textColor=C_GOLD, fontName="Helvetica-Bold", alignment=TA_CENTER))],
                [Paragraph(f"{q_usdt:,.4f} USDT", sty("v1", fontSize=11, textColor=C_TEXT, fontName="Courier-Bold", alignment=TA_CENTER)),
                 Paragraph(f"₹ {q_price:,.2f}", sty("v2", fontSize=11, textColor=C_TEXT, fontName="Courier-Bold", alignment=TA_CENTER)),
                 Paragraph(f"₹ {q_total:,.2f}", sty("v3", fontSize=13, textColor=C_GOLD2, fontName="Courier-Bold", alignment=TA_CENTER))],
            ]
            tx_tbl = Table(tx_data, colWidths=[5.5*cm, 5.5*cm, 6*cm])
            tx_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,0), C_NAVY2),
                ("BACKGROUND",    (0,1), (-1,1), C_NAVY3),
                ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#1a2235")),
                ("LINEABOVE",     (0,0), (-1,0), 1.5, C_GOLD),
                ("BOTTOMPADDING", (0,0), (-1,-1), 10),
                ("TOPPADDING",    (0,0), (-1,-1), 10),
            ]))
            story.append(tx_tbl)
            story.append(Spacer(1, 0.5*cm))

            # Signatures
            story.append(Paragraph("SIGNATURES", s_sec))
            sig_data = [
                [Paragraph("<b>BUYER SIGNATURE</b>", sty("s1", fontSize=7, textColor=C_MUTED, fontName="Helvetica-Bold", alignment=TA_CENTER)),
                 Paragraph("<b>SELLER SIGNATURE</b>", sty("s2", fontSize=7, textColor=C_MUTED, fontName="Helvetica-Bold", alignment=TA_CENTER)),
                 Paragraph("<b>WITNESS</b>", sty("s3", fontSize=7, textColor=C_MUTED, fontName="Helvetica-Bold", alignment=TA_CENTER))],
                [Paragraph("\n\n\n_______________________", sty("sg1", fontSize=9, textColor=C_TEXT, alignment=TA_CENTER)),
                 Paragraph("\n\n\n_______________________", sty("sg2", fontSize=9, textColor=C_TEXT, alignment=TA_CENTER)),
                 Paragraph("\n\n\n_______________________", sty("sg3", fontSize=9, textColor=C_TEXT, alignment=TA_CENTER))],
                [Paragraph(buyer_name or "Full Name", sty("sn1", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)),
                 Paragraph(seller_name or "Full Name", sty("sn2", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)),
                 Paragraph("Full Name", sty("sn3", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER))],
            ]
            sig_tbl = Table(sig_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
            sig_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,-1), C_NAVY3),
                ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#1a2235")),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("TOPPADDING",    (0,0), (-1,-1), 8),
                ("ROWBACKGROUNDS",(0,0), (-1,-1), [C_NAVY2, C_NAVY3, C_NAVY2]),
            ]))
            story.append(sig_tbl)
            story.append(Spacer(1, 0.4*cm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1a2235"), spaceAfter=6))
            story.append(Paragraph(
                f"This document is generated by Xenesis Exchange OTC Desk. "
                f"Valid for 15 minutes from {q_time}. "
                f"Consult a Chartered Accountant for tax compliance. "
                f"© {datetime.now().year} Xenesis Exchange · India",
                s_foot
            ))

            doc.build(story)
            buf.seek(0)
            st.download_button("⬇  Download PDF Invoice", data=buf.read(),
                               file_name=f"xenesis_invoice_{deal_id}.pdf",
                               mime="application/pdf")

        except ImportError:
            st.warning("Install ReportLab: pip install reportlab")
        except Exception as e:
            st.error(f"PDF error: {e}")
            url = f"https://wa.me/?text={quote}"

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:60px;padding-top:24px;border-top:1px solid rgba(201,168,76,0.1);
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <span style="color:var(--gold);font-size:1.1rem;">◈</span>
    <span style="font-family:'Playfair Display',serif;color:var(--gold2);font-size:0.9rem;">Xenesis Exchange</span>
    <span style="color:var(--muted);font-size:0.75rem;">OTC · F2F · USDT/INR</span>
  </div>
  <div style="color:var(--muted);font-size:0.7rem;letter-spacing:0.05em;">
    For authorised desk use only · Tax figures are estimates only · Consult a CA for compliance
  </div>
  <div style="font-family:'DM Mono',monospace;font-size:0.7rem;color:var(--muted);">
    Powered by Binance P2P API
  </div>
</div>
""", unsafe_allow_html=True)

# ── Auto-refresh ──────────────────────────────────────────────────────────────
if st.session_state.auto_refresh:
    time.sleep(10)
    st.rerun()
    score = (predicted_spread - current_spread) * volume

# ── Database ────────────────────────────────────────────────────────────────
@st.cache_resource
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

    # ✅ NEW TABLE
    c.execute("""CREATE TABLE IF NOT EXISTS trader_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        trader TEXT,
        side TEXT,
        price REAL,
        quantity REAL
    )""")

    conn.commit()
    return conn


# ── NEW FETCH FUNCTION ──────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def fetch_binance_p2p_filtered(side: str, min_usdt: float = 5000):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    payload = {
        "asset": "USDT",
        "fiat": "INR",
        "merchantCheck": False,
        "page": 1,
        "payTypes": [],
        "publisherType": None,
        "rows": 50,
        "tradeType": side
    }

    try:
        r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
        data = r.json().get("data", [])

        ads = []
        total_value = 0
        total_qty = 0

        for ad in data:
            adv = ad["adv"]

            price = float(adv["price"])
            available = float(adv.get("surplusAmount", 0))
            tradable = float(adv.get("tradableQuantity", 0))
            quantity = max(available, tradable)

            if quantity >= min_usdt:
                total_value += price * quantity
                total_qty += quantity

                ads.append({
                    "Trader": ad["advertiser"]["nickName"],
                    "Price": price,
                    "USDT": quantity,
                    "Min INR": adv.get("minSingleTransAmount"),
                    "Max INR": adv.get("maxSingleTransAmount"),
                })

        weighted_avg = round(total_value / total_qty, 2) if total_qty else None

        ads = sorted(ads, key=lambda x: x["USDT"], reverse=True)

        for i, ad in enumerate(ads):
            ad["Tag"] = "🐋 WHALE" if i < 3 else ""

        return ads, weighted_avg

    except Exception:
        return [], None


# ── NEW TRACKING ────────────────────────────────────────────────────────────
def save_tracking(db, ads, side):
    for ad in ads:
        db.execute(
            "INSERT INTO trader_tracking (ts, trader, side, price, quantity) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), ad["Trader"], side, ad["Price"], ad["USDT"])
        )
    db.commit()


def detect_whale_alerts(db, threshold=0.2):
    rows = db.execute("SELECT trader, price FROM trader_tracking ORDER BY id DESC").fetchall()

    alerts = []
    last_seen = {}

    for r in rows:
        trader = r["trader"]
        price = r["price"]

        if trader in last_seen:
            change = price - last_seen[trader]
            if abs(change) >= threshold:
                alerts.append({
                    "Trader": trader,
                    "Old": last_seen[trader],
                    "New": price,
                    "Δ": round(change, 2)
                })

        last_seen[trader] = price

    return alerts


# ── REPLACE MARKET FETCH ────────────────────────────────────────────────────
buy_ads, buy_wavg = fetch_binance_p2p_filtered("BUY", 5000)
sell_ads, sell_wavg = fetch_binance_p2p_filtered("SELL", 5000)

# keep compatibility
buy_prices  = [a["Price"] for a in buy_ads]
sell_prices = [a["Price"] for a in sell_ads]

buy_avg  = round(np.average(buy_prices),  2) if buy_prices  else None
sell_avg = round(np.average(sell_prices), 2) if sell_prices else None

# save tracking
save_tracking(db, buy_ads, "BUY")
save_tracking(db, sell_ads, "SELL")


# ═════════════════════════════════════════════════════════════════════════════
# 🔥 ADD AFTER SECTION 1
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("## 🧠 Institutional Liquidity (≥ 5000 USDT)")

c1, c2 = st.columns(2)
with c1:
    st.metric("BUY Weighted Avg", f"₹{buy_wavg}" if buy_wavg else "—")
with c2:
    st.metric("SELL Weighted Avg", f"₹{sell_wavg}" if sell_wavg else "—")

import pandas as pd

if buy_ads:
    st.markdown("### 🔼 BUY Side (Whales First)")
    st.dataframe(pd.DataFrame(buy_ads), use_container_width=True)

if sell_ads:
    st.markdown("### 🔽 SELL Side (Whales First)")
    st.dataframe(pd.DataFrame(sell_ads), use_container_width=True)


# 🚨 Alerts
alerts = detect_whale_alerts(db)
if alerts:
    st.markdown("## 🚨 Whale Alerts")
    st.dataframe(pd.DataFrame(alerts), use_container_width=True)


# 📊 Dominance
st.markdown("## 🧠 Market Dominance")

rows = db.execute("""
SELECT trader, SUM(quantity) as total_volume
FROM trader_tracking
GROUP BY trader
ORDER BY total_volume DESC
LIMIT 10
""").fetchall()

if rows:
    df_dom = pd.DataFrame([dict(r) for r in rows])
    st.bar_chart(df_dom.set_index("trader"))


# 📈 Trader Intelligence
st.markdown("## 📈 Trader Intelligence")

rows = db.execute("""
SELECT trader, side, price, quantity, ts
FROM trader_tracking
ORDER BY id DESC
LIMIT 200
""").fetchall()

if rows:
    df = pd.DataFrame([dict(r) for r in rows])
    df["ts"] = pd.to_datetime(df["ts"])

    trader = st.selectbox("Select Trader", df["trader"].unique())
    st.line_chart(df[df["trader"] == trader].set_index("ts")["price"])
