# ONLY SHOWING MODIFIED + INSERTED PARTS
# (Everything else in your file remains SAME)

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
