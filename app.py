import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BullsEye — NSE Trading Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Ultra Premium CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
}

.stApp { background: #050508; }
.main { background: #050508; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0A0A0F !important;
    border-right: 1px solid #00D4FF22;
}
section[data-testid="stSidebar"] * { color: #E0E0E0 !important; }

/* Hide default elements */
#MainMenu, footer, header { visibility: hidden; }

/* Ticker bar */
.ticker-bar {
    background: linear-gradient(90deg, #050508, #0A0A1A, #050508);
    border: 1px solid #00D4FF33;
    border-radius: 12px;
    padding: 12px 20px;
    margin-bottom: 20px;
    overflow: hidden;
    white-space: nowrap;
}
.ticker-content {
    display: inline-block;
    animation: ticker 30s linear infinite;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #00D4FF;
    letter-spacing: 0.5px;
}
@keyframes ticker {
    0% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}

/* Logo */
.logo {
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(135deg, #00D4FF, #00FF88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    margin-bottom: 4px;
}
.logo-sub {
    font-size: 11px;
    color: #404060;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 24px;
}

/* Live dot */
.live-dot {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #00FF8811;
    border: 1px solid #00FF8833;
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 11px;
    color: #00FF88;
    font-weight: 500;
    margin-bottom: 20px;
}
.dot {
    width: 6px;
    height: 6px;
    background: #00FF88;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

/* Glass cards */
.glass-card {
    background: linear-gradient(135deg, #0D0D1A, #0A0A15);
    border: 1px solid #00D4FF18;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    transition: border-color 0.3s;
}
.glass-card:hover { border-color: #00D4FF44; }

/* Metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}
.metric-box {
    background: linear-gradient(135deg, #0D0D1A, #0A0A15);
    border: 1px solid #00D4FF15;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    transition: all 0.3s;
}
.metric-box:hover {
    border-color: #00D4FF44;
    transform: translateY(-2px);
}
.metric-label {
    font-size: 10px;
    color: #404060;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}
.metric-val {
    font-size: 20px;
    font-weight: 700;
    color: #F0F0FF;
    font-family: 'JetBrains Mono', monospace;
}
.metric-up { color: #00FF88 !important; }
.metric-down { color: #FF4466 !important; }

/* Stock header */
.stock-hero {
    background: linear-gradient(135deg, #0D0D1A 0%, #0A0A15 50%, #0D1020 100%);
    border: 1px solid #00D4FF22;
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.stock-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, #00D4FF08, transparent 70%);
    border-radius: 50%;
}
.hero-name { font-size: 13px; color: #404060; text-transform: uppercase; letter-spacing: 2px; margin: 0; }
.hero-company { font-size: 26px; font-weight: 700; color: #F0F0FF; margin: 6px 0; }
.hero-price {
    font-size: 48px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    color: #F0F0FF;
    margin: 10px 0 6px;
    line-height: 1;
}
.hero-change-up { color: #00FF88; font-size: 18px; font-weight: 500; }
.hero-change-down { color: #FF4466; font-size: 18px; font-weight: 500; }

/* Signal badge */
.signal-buy {
    display: inline-block;
    background: linear-gradient(135deg, #00FF8820, #00FF8810);
    border: 1px solid #00FF8866;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 14px;
    font-weight: 700;
    color: #00FF88;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.signal-sell {
    display: inline-block;
    background: linear-gradient(135deg, #FF446620, #FF446610);
    border: 1px solid #FF446666;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 14px;
    font-weight: 700;
    color: #FF4466;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.signal-hold {
    display: inline-block;
    background: linear-gradient(135deg, #FFB30020, #FFB30010);
    border: 1px solid #FFB30066;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 14px;
    font-weight: 700;
    color: #FFB300;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Section titles */
.section-title {
    font-size: 11px;
    color: #00D4FF;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-weight: 600;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #00D4FF22;
}

/* News card */
.news-card {
    background: #0A0A15;
    border: 1px solid #00D4FF15;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: all 0.2s;
}
.news-card:hover { border-color: #00D4FF44; background: #0D0D1A; }
.news-title { font-size: 13px; color: #C0C0D0; line-height: 1.5; margin: 0 0 6px; }
.news-meta { font-size: 11px; color: #404060; }
.sentiment-pos { color: #00FF88; font-weight: 600; }
.sentiment-neg { color: #FF4466; font-weight: 600; }
.sentiment-neu { color: #FFB300; font-weight: 600; }

/* AI prediction */
.pred-card {
    background: linear-gradient(135deg, #0D0D1A, #0A1020);
    border: 1px solid #7C3AED33;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}
.pred-label { font-size: 10px; color: #7C3AED; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 6px; }
.pred-val { font-size: 24px; font-weight: 700; color: #F0F0FF; font-family: 'JetBrains Mono', monospace; }
.pred-conf { font-size: 12px; color: #606080; margin-top: 4px; }

/* Risk meter */
.risk-low { color: #00FF88; font-weight: 700; }
.risk-med { color: #FFB300; font-weight: 700; }
.risk-high { color: #FF4466; font-weight: 700; }

/* Portfolio */
.port-row {
    background: #0A0A15;
    border: 1px solid #00D4FF15;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Page tabs */
div[data-testid="stHorizontalBlock"] { gap: 12px; }

.stTabs [data-baseweb="tab-list"] {
    background: #0A0A15;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #00D4FF15;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #606080;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00D4FF22, #00FF8811) !important;
    color: #00D4FF !important;
    border: 1px solid #00D4FF33 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #050508; }
::-webkit-scrollbar-thumb { background: #00D4FF33; border-radius: 2px; }

/* Dataframe */
.stDataFrame { border: 1px solid #00D4FF15 !important; border-radius: 12px !important; }

/* Input fields */
.stNumberInput input, .stTextInput input {
    background: #0A0A15 !important;
    border: 1px solid #00D4FF22 !important;
    border-radius: 8px !important;
    color: #F0F0FF !important;
}
.stSelectbox > div > div {
    background: #0A0A15 !important;
    border: 1px solid #00D4FF22 !important;
    color: #F0F0FF !important;
}
.stButton button {
    background: linear-gradient(135deg, #00D4FF22, #00FF8811) !important;
    border: 1px solid #00D4FF44 !important;
    color: #00D4FF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton button:hover {
    background: linear-gradient(135deg, #00D4FF33, #00FF8822) !important;
    border-color: #00D4FF88 !important;
}

.footer {
    text-align: center;
    color: #202030;
    font-size: 11px;
    margin-top: 40px;
    padding-top: 16px;
    border-top: 1px solid #00D4FF11;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ── Stock list ────────────────────────────────────────────────────────────────
STOCKS = {
    "L&T Finance": "LTF.NS",
    "City Union Bank": "CUB.NS",
    "Ashok Leyland": "ASHOKLEY.NS",
    "Bharat Electronics Ltd": "BEL.NS",
    "Bank of Maharashtra": "MAHABANK.NS",
    "Coal India Ltd": "COALINDIA.NS",
    "Vedanta Ltd": "VEDL.NS",
    "Hindustan Zinc Ltd": "HINDZINC.NS",
    "ONGC": "ONGC.NS",
    "PowerGrid Corporation": "POWERGRID.NS",
    "Taparia Tools": "TAPARIA.NS",
    "SBI": "SBIN.NS",
    "NTPC Ltd": "NTPC.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Zee Entertainment": "ZEEL.NS",
    "IREDA": "IREDA.NS",
    "IRFC": "IRFC.NS",
    "Motherson Sumi": "MOTHERSON.NS",
    "Rail Vikas Nigam": "RVNL.NS",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo">🎯 BullsEye</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">NSE Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="live-dot"><div class="dot"></div> MARKET LIVE</div>', unsafe_allow_html=True)

    selected_name = st.selectbox("Select Stock", list(STOCKS.keys()), label_visibility="collapsed")
    ticker_symbol = STOCKS[selected_name]

    st.markdown("---")
    st.markdown('<p style="color:#00D4FF;font-size:11px;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;">⚡ Market Alerts</p>', unsafe_allow_html=True)

    # Quick scan all stocks for signals
    alerts = []
    for name, sym in STOCKS.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="3mo")
            if h.empty or len(h) < 20:
                continue
            price = h['Close'].iloc[-1]
            prev = h['Close'].iloc[-2]
            chg_pct = ((price - prev) / prev) * 100

            # RSI
            delta = h['Close'].diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]

            # MA
            ma20 = h['Close'].rolling(20).mean().iloc[-1]
            ma50 = h['Close'].rolling(50).mean().iloc[-1]

            if rsi < 30:
                alerts.append(("🔥 OVERSOLD", name, f"RSI={rsi:.0f} — Strong Buy Zone!", "#00FF88"))
            elif rsi > 75:
                alerts.append(("⚠️ OVERBOUGHT", name, f"RSI={rsi:.0f} — Consider Selling!", "#FF4466"))
            elif chg_pct > 3:
                alerts.append(("🚀 SURGING", name, f"+{chg_pct:.1f}% today — Momentum!", "#00D4FF"))
            elif chg_pct < -3:
                alerts.append(("📉 FALLING", name, f"{chg_pct:.1f}% today — Watch Out!", "#FF4466"))
            elif ma20 > ma50 and abs(ma20 - ma50) / ma50 < 0.01:
                alerts.append(("💡 CROSSOVER", name, "MA20 crossing MA50 — Signal!", "#FFB300"))
        except:
            continue

    if alerts:
        for tag, stock, msg, color in alerts[:5]:
            st.markdown(f"""
            <div style="background:#0A0A15;border:1px solid {color}33;border-left:3px solid {color};
                border-radius:8px;padding:10px 12px;margin-bottom:8px;">
                <div style="font-size:10px;color:{color};font-weight:700;letter-spacing:1px;">{tag}</div>
                <div style="font-size:12px;color:#D0D0E0;font-weight:600;margin:3px 0;">{stock}</div>
                <div style="font-size:11px;color:#606080;">{msg}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#0A0A15;border:1px solid #00D4FF15;border-radius:8px;padding:12px;text-align:center;">
            <div style="font-size:20px;">🔍</div>
            <div style="font-size:11px;color:#404060;margin-top:6px;">Scanning market...<br>No strong signals right now.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    # Market time
    now = datetime.now()
    market_open = now.replace(hour=9, minute=15, second=0)
    market_close = now.replace(hour=15, minute=30, second=0)
    is_open = market_open <= now <= market_close and now.weekday() < 5
    status_color = "#00FF88" if is_open else "#FF4466"
    status_text = "OPEN" if is_open else "CLOSED"
    st.markdown(f"""
    <div style="background:#0A0A15;border:1px solid {status_color}33;border-radius:8px;padding:10px 12px;text-align:center;">
        <div style="font-size:10px;color:#404060;letter-spacing:2px;">NSE MARKET</div>
        <div style="font-size:16px;font-weight:700;color:{status_color};margin-top:4px;">● {status_text}</div>
        <div style="font-size:10px;color:#404060;margin-top:2px;">{now.strftime("%d %b %Y %I:%M %p")}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Fetch data ────────────────────────────────────────────────────────────────
def fetch_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    hist_1y = ticker.history(period="1y")
    hist_1m = ticker.history(period="1mo")
    hist_3m = ticker.history(period="3mo")
    return hist_1y, hist_1m, hist_3m

def compute_indicators(df):
    # RSI
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df['Close'].ewm(span=12).mean()
    ema26 = df['Close'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']

    # Bollinger Bands
    df['BB_Mid'] = df['Close'].rolling(20).mean()
    bb_std = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['BB_Mid'] + 2 * bb_std
    df['BB_Lower'] = df['BB_Mid'] - 2 * bb_std

    # Moving Averages
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()

    return df

def generate_signal(df):
    rsi = df['RSI'].iloc[-1]
    macd = df['MACD'].iloc[-1]
    signal = df['Signal'].iloc[-1]
    close = df['Close'].iloc[-1]
    bb_upper = df['BB_Upper'].iloc[-1]
    bb_lower = df['BB_Lower'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    ma50 = df['MA50'].iloc[-1]

    score = 0
    reasons = []

    if rsi < 35:
        score += 2
        reasons.append("RSI oversold — bullish")
    elif rsi > 65:
        score -= 2
        reasons.append("RSI overbought — bearish")

    if macd > signal:
        score += 1
        reasons.append("MACD bullish crossover")
    else:
        score -= 1
        reasons.append("MACD bearish crossover")

    if close < bb_lower:
        score += 1
        reasons.append("Price below Bollinger lower band")
    elif close > bb_upper:
        score -= 1
        reasons.append("Price above Bollinger upper band")

    if ma20 > ma50:
        score += 1
        reasons.append("MA20 above MA50 — uptrend")
    else:
        score -= 1
        reasons.append("MA20 below MA50 — downtrend")

    if score >= 2:
        return "BUY", score, reasons
    elif score <= -2:
        return "SELL", score, reasons
    else:
        return "HOLD", score, reasons

def ai_predict(df, days=7):
    df = df.copy().dropna()
    df['Day'] = np.arange(len(df))
    X = df[['Day']].values
    y = df['Close'].values

    scaler = MinMaxScaler()
    y_scaled = scaler.fit_transform(y.reshape(-1, 1)).flatten()

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y_scaled)

    future_days = np.arange(len(df), len(df) + days).reshape(-1, 1)
    pred_scaled = model.predict(future_days)
    predictions = scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()

    confidence = min(95, max(55, 85 - (days * 0.5)))
    return predictions, confidence

def get_news(stock_name):
    """Fetch news from Google News RSS + yfinance as fallback"""
    news_items = []

    # Try Google News RSS first
    try:
        import xml.etree.ElementTree as ET
        search_query = stock_name.replace(" ", "+") + "+NSE+stock"
        url = f"https://news.google.com/rss/search?q={search_query}&hl=en-IN&gl=IN&ceid=IN:en"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            for item in root.findall('.//item')[:8]:
                title = item.findtext('title', '')
                link = item.findtext('link', '#')
                pub_date = item.findtext('pubDate', '')
                source = item.findtext('source', 'Google News')
                if title:
                    news_items.append({
                        'title': title,
                        'link': link,
                        'pubDate': pub_date,
                        'source': source,
                    })
    except:
        pass

    # Fallback to yfinance news
    if not news_items:
        try:
            ticker = yf.Ticker(STOCKS[stock_name])
            yf_news = ticker.news
            if yf_news:
                for item in yf_news[:8]:
                    news_items.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', '#'),
                        'pubDate': str(item.get('providerPublishTime', '')),
                        'source': item.get('publisher', 'Yahoo Finance'),
                    })
        except:
            pass

    return news_items


def sentiment_score(title):
    positive = ['gain', 'up', 'rise', 'bull', 'buy', 'growth', 'profit', 'high', 'surge',
                'boost', 'strong', 'record', 'beat', 'rally', 'outperform', 'upgrade',
                'positive', 'revenue', 'expansion', 'contract', 'win', 'order', 'launch']
    negative = ['fall', 'down', 'drop', 'bear', 'sell', 'loss', 'low', 'crash', 'weak',
                'miss', 'cut', 'decline', 'downgrade', 'risk', 'concern', 'probe',
                'penalty', 'fraud', 'debt', 'default', 'layoff', 'resign', 'scam']
    title_lower = title.lower()
    pos = sum(1 for w in positive if w in title_lower)
    neg = sum(1 for w in negative if w in title_lower)
    if pos > neg:
        return "POSITIVE", "sentiment-pos"
    elif neg > pos:
        return "NEGATIVE", "sentiment-neg"
    return "NEUTRAL", "sentiment-neu"

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner(""):
    try:
        hist_1y, hist_1m, hist_3m = fetch_stock_data(ticker_symbol)
        if hist_1y.empty:
            st.error("No data available. Please try another stock.")
            st.stop()
        hist_1y = compute_indicators(hist_1y)
    except Exception as e:
        st.error(f"Could not fetch data: {e}")
        st.stop()

# ── Compute key metrics ───────────────────────────────────────────────────────
current = hist_1y['Close'].iloc[-1]
prev = hist_1y['Close'].iloc[-2]
change = current - prev
change_pct = (change / prev) * 100
week_high = hist_1y['High'].tail(28).max()
week_low = hist_1y['Low'].tail(28).min()
month_high = hist_1m['High'].max() if not hist_1m.empty else current
month_low = hist_1m['Low'].min() if not hist_1m.empty else current
rsi_val = hist_1y['RSI'].iloc[-1]
signal_label, signal_score, signal_reasons = generate_signal(hist_1y)
stop_loss = current * 0.95
target = current * 1.10
risk_reward = round((target - current) / (current - stop_loss), 2)

arrow = "▲" if change >= 0 else "▼"
chg_class = "hero-change-up" if change >= 0 else "hero-change-down"

# ── Ticker bar ────────────────────────────────────────────────────────────────
ticker_items = []
for name, sym in list(STOCKS.items())[:8]:
    try:
        t = yf.Ticker(sym)
        p = t.fast_info.last_price
        if p:
            ticker_items.append(f"{'▲' if p > 0 else '▼'} {name.upper()}: ₹{p:,.2f}")
    except:
        pass

ticker_text = "  ·  ".join(ticker_items) if ticker_items else "NSE LIVE DATA · BULLSEYE PLATFORM · SMART TRADING"
st.markdown(f'<div class="ticker-bar"><div class="ticker-content">{ticker_text}</div></div>', unsafe_allow_html=True)

# ── Stock Hero Header ─────────────────────────────────────────────────────────
signal_html = f'<span class="signal-{signal_label.lower()}">{signal_label}</span>'
st.markdown(f"""
<div class="stock-hero">
    <p class="hero-name">{ticker_symbol} · NSE · {datetime.now().strftime("%d %b %Y %I:%M %p")}</p>
    <p class="hero-company">{selected_name}</p>
    <p class="hero-price">₹{current:,.2f} <span class="{chg_class}" style="font-size:20px;">{arrow} ₹{abs(change):.2f} ({change_pct:+.2f}%)</span></p>
    <div style="margin-top:14px;">{signal_html}</div>
</div>
""", unsafe_allow_html=True)

# ── Metrics row ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="metric-grid">
    <div class="metric-box">
        <div class="metric-label">4W High</div>
        <div class="metric-val metric-up">₹{week_high:,.2f}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">4W Low</div>
        <div class="metric-val metric-down">₹{week_low:,.2f}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">1M High</div>
        <div class="metric-val metric-up">₹{month_high:,.2f}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">1M Low</div>
        <div class="metric-val metric-down">₹{month_low:,.2f}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">RSI (14)</div>
        <div class="metric-val {'metric-up' if rsi_val < 40 else 'metric-down' if rsi_val > 60 else ''}">{rsi_val:.1f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Charts & Indicators",
    "🤖 AI Predictions",
    "📰 News & Sentiment",
    "🎯 Trading Tools",
    "💰 Virtual Portfolio"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Charts & Indicators
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    period_choice = st.radio("", ["1 Month", "3 Months", "1 Year"], horizontal=True, index=1)
    hist_display = hist_1m if period_choice == "1 Month" else hist_3m if period_choice == "3 Months" else hist_1y
    hist_display = compute_indicators(hist_display)

    chart_type = st.radio("", ["Candlestick", "Line"], horizontal=True)
    show_bb = st.checkbox("Bollinger Bands", value=True)
    show_ma = st.checkbox("Moving Averages", value=True)

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=["", "MACD", "RSI"]
    )

    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=hist_display.index,
            open=hist_display['Open'],
            high=hist_display['High'],
            low=hist_display['Low'],
            close=hist_display['Close'],
            name="OHLC",
            increasing_line_color="#00FF88",
            decreasing_line_color="#FF4466",
            increasing_fillcolor="rgba(0,255,136,0.4)",
            decreasing_fillcolor="rgba(255,68,102,0.4)",
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=hist_display.index, y=hist_display['Close'],
            mode="lines", name="Price",
            line=dict(color="#00D4FF", width=2),
            fill="tozeroy",
            fillcolor="rgba(0,212,255,0.05)"
        ), row=1, col=1)

    if show_bb:
        fig.add_trace(go.Scatter(x=hist_display.index, y=hist_display['BB_Upper'],
            mode="lines", name="BB Upper", line=dict(color="#7C3AED", width=1, dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist_display.index, y=hist_display['BB_Lower'],
            mode="lines", name="BB Lower", line=dict(color="#7C3AED", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(124,58,237,0.04)"), row=1, col=1)

    if show_ma:
        fig.add_trace(go.Scatter(x=hist_display.index, y=hist_display['MA20'],
            mode="lines", name="MA20", line=dict(color="#FFB300", width=1.5)), row=1, col=1)
        if len(hist_display) >= 50:
            fig.add_trace(go.Scatter(x=hist_display.index, y=hist_display['MA50'],
                mode="lines", name="MA50", line=dict(color="#FF6B35", width=1.5)), row=1, col=1)

    # MACD
    colors_macd = ["#00FF88" if v >= 0 else "#FF4466" for v in hist_display['MACD_Hist'].fillna(0)]
    fig.add_trace(go.Bar(x=hist_display.index, y=hist_display['MACD_Hist'],
        name="MACD Hist", marker_color=colors_macd, opacity=0.8), row=2, col=1)
    fig.add_trace(go.Scatter(x=hist_display.index, y=hist_display['MACD'],
        mode="lines", name="MACD", line=dict(color="#00D4FF", width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=hist_display.index, y=hist_display['Signal'],
        mode="lines", name="Signal", line=dict(color="#FF6B35", width=1.5)), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=hist_display.index, y=hist_display['RSI'],
        mode="lines", name="RSI", line=dict(color="#7C3AED", width=2)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="rgba(255,68,102,0.3)", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="rgba(0,255,136,0.3)", row=3, col=1)

    fig.update_layout(
        paper_bgcolor="#050508",
        plot_bgcolor="#050508",
        font=dict(family="Space Grotesk", color="#606080", size=11),
        legend=dict(bgcolor="#0A0A15", bordercolor="rgba(0,212,255,0.13)", borderwidth=1, font=dict(size=11)),
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=20, b=0),
        height=620,
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="rgba(0,212,255,0.04)", showgrid=True, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(0,212,255,0.04)", showgrid=True, zeroline=False, tickprefix="₹")
    fig.update_yaxes(tickprefix="", row=2, col=1)
    fig.update_yaxes(tickprefix="", row=3, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # Signal reasons
    st.markdown('<div class="section-title">Signal Analysis</div>', unsafe_allow_html=True)
    for r in signal_reasons:
        icon = "🟢" if "bullish" in r.lower() or "above" in r.lower() or "uptrend" in r.lower() else "🔴"
        st.markdown(f'<div class="news-card"><span style="color:#C0C0D0;font-size:13px;">{icon} {r}</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — AI Predictions
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🤖 AI Price Predictions</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        pred_7, conf_7 = ai_predict(hist_1y, days=7)
        pred_7_final = pred_7[-1]
        change_7 = ((pred_7_final - current) / current) * 100
        st.markdown(f"""
        <div class="pred-card">
            <div class="pred-label">7 Day Prediction</div>
            <div class="pred-val">₹{pred_7_final:,.2f}</div>
            <div class="pred-conf">Expected change: <span class="{'metric-up' if change_7 >= 0 else 'metric-down'}">{change_7:+.2f}%</span></div>
            <div class="pred-conf">Model confidence: {conf_7:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        pred_30, conf_30 = ai_predict(hist_1y, days=30)
        pred_30_final = pred_30[-1]
        change_30 = ((pred_30_final - current) / current) * 100
        st.markdown(f"""
        <div class="pred-card">
            <div class="pred-label">30 Day Prediction</div>
            <div class="pred-val">₹{pred_30_final:,.2f}</div>
            <div class="pred-conf">Expected change: <span class="{'metric-up' if change_30 >= 0 else 'metric-down'}">{change_30:+.2f}%</span></div>
            <div class="pred-conf">Model confidence: {conf_30:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Prediction chart
    st.markdown('<div class="section-title" style="margin-top:20px;">Price Forecast Chart</div>', unsafe_allow_html=True)
    last_30 = hist_1y['Close'].tail(30)
    future_dates_7 = pd.date_range(start=hist_1y.index[-1] + timedelta(days=1), periods=7)
    future_dates_30 = pd.date_range(start=hist_1y.index[-1] + timedelta(days=1), periods=30)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=last_30.index, y=last_30.values,
        mode="lines", name="Historical",
        line=dict(color="#00D4FF", width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=future_dates_7, y=pred_7,
        mode="lines+markers", name="7D Forecast",
        line=dict(color="#00FF88", width=2, dash="dot"),
        marker=dict(size=6, color="#00FF88")
    ))
    fig2.add_trace(go.Scatter(
        x=future_dates_30, y=pred_30,
        mode="lines", name="30D Forecast",
        line=dict(color="#7C3AED", width=2, dash="dot")
    ))
    fig2.update_layout(
        paper_bgcolor="#050508", plot_bgcolor="#050508",
        font=dict(family="Space Grotesk", color="#606080"),
        legend=dict(bgcolor="#0A0A15", bordercolor="rgba(0,212,255,0.13)", borderwidth=1),
        margin=dict(l=0, r=0, t=10, b=0),
        height=350, hovermode="x unified"
    )
    fig2.update_xaxes(gridcolor="rgba(0,212,255,0.04)")
    fig2.update_yaxes(gridcolor="rgba(0,212,255,0.04)", tickprefix="₹")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class="news-card" style="margin-top:8px;">
        <span style="color:#404060;font-size:12px;">⚠️ AI predictions are based on historical price patterns using Random Forest ML model. 
        These are not financial advice. Always do your own research before investing.</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — News & Sentiment
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">📰 Latest News & Sentiment Analysis</div>', unsafe_allow_html=True)

    with st.spinner("Fetching latest news from Google News..."):
        news_items = get_news(selected_name)

    if news_items:
        # Collect sentiments
        sentiments = []
        for item in news_items:
            title = item.get('title', 'No title')
            link = item.get('link', '#')
            pub_date = item.get('pubDate', 'Recent')
            source = item.get('source', 'Unknown')
            sent_label, sent_class = sentiment_score(title)
            sentiments.append(sent_label)

            # Clean pub date
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(pub_date)
                pub_date_str = dt.strftime("%d %b %Y %I:%M %p")
            except:
                pub_date_str = pub_date[:20] if pub_date else "Recent"

            # Sentiment icon
            icon = "🟢" if sent_label == "POSITIVE" else "🔴" if sent_label == "NEGATIVE" else "🟡"

            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">
                    <a href="{link}" target="_blank" style="color:#C0C0D0;text-decoration:none;line-height:1.6;">
                        {icon} {title}
                    </a>
                </div>
                <div class="news-meta" style="margin-top:6px;">
                    📡 {source} &nbsp;·&nbsp; 🕐 {pub_date_str} &nbsp;·&nbsp;
                    Sentiment: <span class="{sent_class}">{sent_label}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Sentiment Summary ──────────────────────────────────────────────
        st.markdown('<div class="section-title" style="margin-top:24px;">📊 Sentiment Summary</div>', unsafe_allow_html=True)
        pos = sentiments.count("POSITIVE")
        neg = sentiments.count("NEGATIVE")
        neu = sentiments.count("NEUTRAL")
        total = len(sentiments)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-box"><div class="metric-label">🟢 Positive</div><div class="metric-val metric-up">{pos}/{total}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><div class="metric-label">🔴 Negative</div><div class="metric-val metric-down">{neg}/{total}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><div class="metric-label">🟡 Neutral</div><div class="metric-val" style="color:#FFB300;">{neu}/{total}</div></div>', unsafe_allow_html=True)

        # ── AI Conclusion ──────────────────────────────────────────────────
        st.markdown('<div class="section-title" style="margin-top:24px;">🤖 AI News Conclusion</div>', unsafe_allow_html=True)

        # Build conclusion based on news + technical signal
        if pos > neg and pos > neu:
            news_mood = "BULLISH"
            news_color = "#00FF88"
            news_icon = "🚀"
        elif neg > pos and neg > neu:
            news_mood = "BEARISH"
            news_color = "#FF4466"
            news_icon = "⚠️"
        else:
            news_mood = "NEUTRAL"
            news_color = "#FFB300"
            news_icon = "⚖️"

        # Combined conclusion
        if signal_label == "BUY" and news_mood == "BULLISH":
            conclusion = f"Strong BUY signal! Both technical indicators and news sentiment are positive for {selected_name}. The stock shows bullish momentum with {pos} positive news articles supporting upward movement."
            conclusion_color = "#00FF88"
            conclusion_icon = "🟢"
        elif signal_label == "SELL" and news_mood == "BEARISH":
            conclusion = f"Strong SELL signal! Both technical indicators and news sentiment are negative for {selected_name}. Consider exiting or avoiding this stock until sentiment improves."
            conclusion_color = "#FF4466"
            conclusion_icon = "🔴"
        elif signal_label == "BUY" and news_mood == "BEARISH":
            conclusion = f"Mixed signals for {selected_name}. Technical indicators suggest BUY but news sentiment is negative. Wait for news to stabilize before entering a position."
            conclusion_color = "#FFB300"
            conclusion_icon = "🟡"
        elif signal_label == "SELL" and news_mood == "BULLISH":
            conclusion = f"Conflicting signals for {selected_name}. News is positive but technical indicators show weakness. Monitor closely — the stock may consolidate before the next move."
            conclusion_color = "#FFB300"
            conclusion_icon = "🟡"
        else:
            conclusion = f"Neutral outlook for {selected_name}. No strong directional bias from news or technical indicators. Wait for a clear breakout before taking a position."
            conclusion_color = "#FFB300"
            conclusion_icon = "🟡"

        st.markdown(f"""
        <div class="glass-card" style="border-color:{conclusion_color}33;margin-top:8px;">
            <div style="display:flex;align-items:flex-start;gap:14px;">
                <div style="font-size:32px;">{conclusion_icon}</div>
                <div>
                    <div style="font-size:11px;color:#404060;text-transform:uppercase;letter-spacing:2px;margin-bottom:6px;">
                        Technical Signal: <span style="color:{('#00FF88' if signal_label=='BUY' else '#FF4466' if signal_label=='SELL' else '#FFB300')}">{signal_label}</span>
                        &nbsp;·&nbsp;
                        News Mood: <span style="color:{news_color}">{news_mood} {news_icon}</span>
                    </div>
                    <div style="font-size:15px;color:#D0D0E0;line-height:1.7;">{conclusion}</div>
                    <div style="font-size:11px;color:#303050;margin-top:10px;">
                        ⚠️ This is AI-generated analysis based on news sentiment + technical indicators. Not financial advice.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="news-card">
            <div style="text-align:center;padding:20px;">
                <div style="font-size:32px;margin-bottom:12px;">📡</div>
                <div style="color:#C0C0D0;font-size:14px;margin-bottom:6px;">Fetching live news for <strong>{selected_name}</strong>...</div>
                <div style="color:#404060;font-size:12px;">If news doesn't load, it may be a network issue. Try refreshing the page.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Trading Tools
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">🎯 Trading Tools</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Stop Loss Calculator**")
        entry_price = st.number_input("Entry Price (₹)", value=float(round(current, 2)), step=0.5)
        sl_pct = st.slider("Stop Loss %", min_value=1, max_value=20, value=5)
        target_pct = st.slider("Target %", min_value=1, max_value=50, value=10)

        sl_price = entry_price * (1 - sl_pct / 100)
        target_price = entry_price * (1 + target_pct / 100)
        rr = round((target_price - entry_price) / (entry_price - sl_price), 2)

        risk_level = "LOW 🟢" if rr >= 3 else "MEDIUM 🟡" if rr >= 1.5 else "HIGH 🔴"

        st.markdown(f"""
        <div class="glass-card" style="margin-top:16px;">
            <div style="display:grid;gap:12px;">
                <div><span style="color:#404060;font-size:12px;">ENTRY</span><br><span style="color:#00D4FF;font-size:20px;font-weight:700;font-family:'JetBrains Mono';">₹{entry_price:,.2f}</span></div>
                <div><span style="color:#404060;font-size:12px;">STOP LOSS</span><br><span style="color:#FF4466;font-size:20px;font-weight:700;font-family:'JetBrains Mono';">₹{sl_price:,.2f}</span></div>
                <div><span style="color:#404060;font-size:12px;">TARGET</span><br><span style="color:#00FF88;font-size:20px;font-weight:700;font-family:'JetBrains Mono';">₹{target_price:,.2f}</span></div>
                <div><span style="color:#404060;font-size:12px;">RISK:REWARD</span><br><span style="color:#FFB300;font-size:20px;font-weight:700;">1 : {rr}</span></div>
                <div><span style="color:#404060;font-size:12px;">RISK LEVEL</span><br><span style="font-size:16px;font-weight:700;">{risk_level}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("**Position Size Calculator**")
        capital = st.number_input("Your Capital (₹)", value=10000.0, step=1000.0)
        risk_amt_pct = st.slider("Risk per trade %", min_value=1, max_value=10, value=2)

        risk_amount = capital * (risk_amt_pct / 100)
        sl_per_share = entry_price - sl_price if entry_price > sl_price else 1
        qty = int(risk_amount / sl_per_share) if sl_per_share > 0 else 0
        total_investment = qty * entry_price
        potential_profit = qty * (target_price - entry_price)
        potential_loss = qty * sl_per_share

        st.markdown(f"""
        <div class="glass-card" style="margin-top:16px;">
            <div style="display:grid;gap:12px;">
                <div><span style="color:#404060;font-size:12px;">RECOMMENDED QTY</span><br><span style="color:#00D4FF;font-size:24px;font-weight:700;font-family:'JetBrains Mono';">{qty} shares</span></div>
                <div><span style="color:#404060;font-size:12px;">TOTAL INVESTMENT</span><br><span style="color:#F0F0FF;font-size:18px;font-weight:700;font-family:'JetBrains Mono';">₹{total_investment:,.2f}</span></div>
                <div><span style="color:#404060;font-size:12px;">POTENTIAL PROFIT</span><br><span style="color:#00FF88;font-size:18px;font-weight:700;font-family:'JetBrains Mono';">₹{potential_profit:,.2f}</span></div>
                <div><span style="color:#404060;font-size:12px;">POTENTIAL LOSS</span><br><span style="color:#FF4466;font-size:18px;font-weight:700;font-family:'JetBrains Mono';">₹{potential_loss:,.2f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Support & Resistance
    st.markdown('<div class="section-title" style="margin-top:20px;">Support & Resistance Levels</div>', unsafe_allow_html=True)
    recent = hist_1y.tail(20)
    resistance = recent['High'].max()
    support = recent['Low'].min()
    pivot = (recent['High'].iloc[-1] + recent['Low'].iloc[-1] + recent['Close'].iloc[-1]) / 3
    r1 = 2 * pivot - recent['Low'].iloc[-1]
    s1 = 2 * pivot - recent['High'].iloc[-1]

    col1, col2, col3, col4, col5 = st.columns(5)
    for col, label, val, cls in [
        (col1, "Strong Support", support, "metric-down"),
        (col2, "S1", s1, "metric-down"),
        (col3, "Pivot", pivot, ""),
        (col4, "R1", r1, "metric-up"),
        (col5, "Strong Resistance", resistance, "metric-up"),
    ]:
        with col:
            st.markdown(f'<div class="metric-box"><div class="metric-label">{label}</div><div class="metric-val {cls}">₹{val:,.2f}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Virtual Portfolio
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">💰 Virtual Portfolio Tracker</div>', unsafe_allow_html=True)

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []

    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        port_stock = st.selectbox("Stock", list(STOCKS.keys()), key="port_stock")
    with col2:
        port_price = st.number_input("Buy Price (₹)", min_value=0.1, value=100.0, step=0.5)
    with col3:
        port_qty = st.number_input("Quantity", min_value=1, value=10, step=1)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add"):
            st.session_state.portfolio.append({
                "stock": port_stock,
                "symbol": STOCKS[port_stock],
                "buy_price": port_price,
                "qty": port_qty
            })

    if st.session_state.portfolio:
        total_invested = 0
        total_current = 0

        for i, item in enumerate(st.session_state.portfolio):
            try:
                t = yf.Ticker(item['symbol'])
                lp = t.fast_info.last_price or item['buy_price']
            except:
                lp = item['buy_price']

            invested = item['buy_price'] * item['qty']
            current_val = lp * item['qty']
            pnl = current_val - invested
            pnl_pct = (pnl / invested) * 100
            total_invested += invested
            total_current += current_val

            pnl_color = "#00FF88" if pnl >= 0 else "#FF4466"
            arrow_p = "▲" if pnl >= 0 else "▼"

            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            with col1:
                st.markdown(f'<div style="color:#F0F0FF;font-weight:600;padding-top:8px;">{item["stock"]}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div style="color:#606080;padding-top:8px;">Qty: {item["qty"]} · Buy: ₹{item["buy_price"]:.2f}</div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div style="color:#F0F0FF;padding-top:8px;">LTP: ₹{lp:,.2f}</div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div style="color:{pnl_color};font-weight:700;padding-top:8px;">{arrow_p} ₹{abs(pnl):,.2f} ({pnl_pct:+.2f}%)</div>', unsafe_allow_html=True)
            with col5:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.portfolio.pop(i)
                    st.rerun()

        # Portfolio summary
        total_pnl = total_current - total_invested
        total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-box"><div class="metric-label">Total Invested</div><div class="metric-val">₹{total_invested:,.2f}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><div class="metric-label">Current Value</div><div class="metric-val">₹{total_current:,.2f}</div></div>', unsafe_allow_html=True)
        with col3:
            pnl_cls = "metric-up" if total_pnl >= 0 else "metric-down"
            st.markdown(f'<div class="metric-box"><div class="metric-label">Total P&L</div><div class="metric-val {pnl_cls}">₹{total_pnl:,.2f} ({total_pnl_pct:+.2f}%)</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="news-card"><span style="color:#404060;">No stocks in portfolio yet. Add your first stock above! 👆</span></div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer">🎯 BULLSEYE · NSE INTELLIGENCE PLATFORM · NOT FINANCIAL ADVICE · DATA FROM YAHOO FINANCE</div>', unsafe_allow_html=True)
