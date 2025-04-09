
import streamlit as st
import pandas as pd
import yfinance as yf
from ta import momentum, trend
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
st.set_page_config(layout="wide")
TICKER = 'IUSA.L'
TRIGGER_WORDS = ['recession', 'inflation', 'rate hike', 'bear market']
NEWS_SOURCES = {
    'BBC': 'https://www.bbc.com/news/business',
    'Reuters': 'https://www.reuters.com/finance',
    'CNBC': 'https://www.cnbc.com/world/',
    'Yahoo Finance': 'https://finance.yahoo.com',
    'FT': 'https://www.ft.com/markets'
}

# --- INTERFACE ---
st.title("📈 IUSA Buy/Hold/Sell Signal — Fallback Edition")
mode = st.selectbox("Interval", options=["1d", "1h"], index=0)
st.markdown("---")

# --- LOAD DATA ---
df = yf.download(TICKER, period="6mo", interval=mode)
df = df.dropna()
st.subheader("📊 Raw Data Snapshot")
st.dataframe(df.tail(), use_container_width=True)

# --- INDICATOR FALLBACK ---
row_count = len(df)
st.markdown(f"✅ Rows: {row_count}")
available_indicators = []

if row_count >= 14:
    df['RSI'] = momentum.RSIIndicator(df['Close'], window=14).rsi()
    available_indicators.append('RSI')
if row_count >= 26:
    macd = trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['Signal'] = macd.macd_signal()
    available_indicators.append('MACD')
if row_count >= 50:
    df['MA50'] = df['Close'].rolling(50).mean()
    available_indicators.append('50 MA')
if row_count >= 200:
    df['MA200'] = df['Close'].rolling(200).mean()
    available_indicators.append('200 MA')

st.markdown(f"✅ With indicators: {len(available_indicators)} — {', '.join(available_indicators) if available_indicators else 'None'}")

# --- NEWS SENTIMENT ---
st.subheader("📰 News Sentiment")
sentiment_total = 0
sentiment_count = 0

def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

for source, url in NEWS_SOURCES.items():
    try:
        html = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            title = link.get_text(strip=True)
            if any(word in title.lower() for word in TRIGGER_WORDS):
                score = get_sentiment(title)
                sentiment_total += score
                sentiment_count += 1
                st.write(f"**{source}** — {title} ({round(score, 2)})")
    except:
        continue

sentiment_score = sentiment_total / sentiment_count if sentiment_count else 0
sentiment_label = "Positive" if sentiment_score > 0.2 else "Negative" if sentiment_score < -0.2 else "Neutral"
st.markdown(f"**Sentiment Score:** {round(sentiment_score, 2)} — {sentiment_label}")

# --- SIGNAL LOGIC ---
st.subheader("📍 Signal")

signal = "HOLD"
if 'RSI' in df.columns and df['RSI'].iloc[-1] < 30 and sentiment_score > 0.2:
    signal = "BUY"
elif 'RSI' in df.columns and df['RSI'].iloc[-1] > 70 and sentiment_score < -0.2:
    signal = "SELL"

st.header(f"Signal: {signal}")
