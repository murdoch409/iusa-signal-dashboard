import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import mplfinance as mpf
import ta
import datetime

st.set_page_config(layout="wide")
st.title("📈 IUSA Buy/Hold/Sell Signal — Zacks & Candlestick Upgrade")

TICKER = "IUSA.L"
INTERVAL = st.selectbox("Interval", ["1d", "1h"], index=0)
PERIOD = "6mo" if INTERVAL == "1d" else "30d"

# --- Fetch Data ---
df = yf.download(TICKER, period=PERIOD, interval=INTERVAL)
df.dropna(inplace=True)
df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
df.index.name = "Date"

# --- Indicators ---
if len(df) >= 14:
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
if len(df) >= 26:
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['Signal_Line'] = macd.macd_signal()
if len(df) >= 50:
    df['50_MA'] = df['Close'].rolling(50).mean()
if len(df) >= 200:
    df['200_MA'] = df['Close'].rolling(200).mean()

# --- Zacks Rating ---
def get_zacks_rating(ticker='IUSA'):
    try:
        url = f"https://www.zacks.com/funds/etf/{ticker}"
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        rating = soup.find("span", class_="rank_view").get_text(strip=True)
        return rating
    except:
        return "Unavailable"

zacks_rating = get_zacks_rating("IUSA")
st.markdown(f"**Zacks Rank**: {zacks_rating}")

# --- Candlestick Chart ---
st.subheader("📊 Candlestick Chart with MAs")
plot_df = df[-90:] if len(df) > 90 else df
mpf_fig = mpf.plot(plot_df, type='candle', mav=(50,200), volume=True, style='yahoo', returnfig=True)
st.pyplot(mpf_fig[0])

# --- Candlestick Pattern Detection (basic) ---
def detect_pattern(df):
    recent = df.tail(3)
    last_candle = recent.iloc[-1]
    body = abs(last_candle['Close'] - last_candle['Open'])
    candle_range = last_candle['High'] - last_candle['Low']
    
    if body < 0.1 * candle_range:
        return "Doji (Indecision)"
    elif last_candle['Close'] > last_candle['Open'] and last_candle['Open'] < recent.iloc[-2]['Close']:
        return "Bullish Engulfing"
    elif last_candle['Close'] < last_candle['Open'] and last_candle['Open'] > recent.iloc[-2]['Close']:
        return "Bearish Engulfing"
    return "No strong pattern"

pattern = detect_pattern(df)
st.markdown(f"**Latest Pattern:** {pattern}")

# --- Signal Logic ---
st.subheader("📍 Final Signal")
signal = "HOLD"

if pattern == "Bullish Engulfing" and zacks_rating.startswith("1") or zacks_rating.startswith("2"):
    signal = "BUY"
elif pattern == "Bearish Engulfing" and zacks_rating.startswith("4") or zacks_rating.startswith("5"):
    signal = "SELL"

st.header(f"Signal: {signal}")
st.metric("Current Price", f"£{df['Close'].iloc[-1]:.2f}")