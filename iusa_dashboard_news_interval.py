import yfinance as yf
import pandas as pd
import ta
import streamlit as st
import matplotlib.pyplot as plt
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
import numpy as np

st.set_page_config(page_title="IUSA AI Dashboard", layout="wide")
st.title("📈 IUSA Buy/Hold/Sell Signal — News & Interval Aware")

TICKER = 'IUSA.L'
INTERVAL_OPTIONS = {'Daily': '1d', 'Hourly': '1h'}
selected_interval = st.selectbox("Select Timeframe", list(INTERVAL_OPTIONS.keys()))
INTERVAL = INTERVAL_OPTIONS[selected_interval]

TRIGGER_WORDS = ['recession', 'inflation', 'crash', 'rate hike', 'interest rates', 'bear market']
NEWS_SOURCES = [
    'https://www.bbc.com/news/business',
    'https://www.reuters.com/finance',
    'https://www.cnbc.com/world/?region=world',
    'https://finance.yahoo.com',
    'https://www.ft.com/markets'
]

def fetch_data():
    df = yf.download(TICKER, period='60d', interval=INTERVAL)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)
    if len(df.columns) == 6:
        df.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    return df

def flatten_series(col):
    return pd.Series(np.ravel(col.values), index=col.index)

def add_indicators(df):
    df['RSI'] = flatten_series(ta.momentum.RSIIndicator(close=df['Close']).rsi())
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = flatten_series(macd.macd())
    df['Signal_Line'] = flatten_series(macd.macd_signal())
    df['50_MA'] = flatten_series(df['Close'].rolling(window=50).mean())
    df['200_MA'] = flatten_series(df['Close'].rolling(window=200).mean())
    return df

def generate_signal(df, sentiment_score):
    latest = df.iloc[-1]
    if latest['RSI'] < 30 and latest['MACD'] > latest['Signal_Line'] and sentiment_score > 0:
        return 'BUY'
    elif latest['RSI'] > 70 and latest['MACD'] < latest['Signal_Line'] and sentiment_score < 0:
        return 'SELL'
    return 'HOLD'

def fetch_news_sentiment():
    sentiment_score = 0
    headlines = []

    for url in NEWS_SOURCES:
        try:
            page = requests.get(url, timeout=5)
            soup = BeautifulSoup(page.text, 'html.parser')
            titles = soup.find_all(['h2', 'h3'])

            for title in titles:
                text = title.get_text(strip=True)
                if any(word in text.lower() for word in TRIGGER_WORDS):
                    headlines.append(text)
                    sentiment_score += TextBlob(text).sentiment.polarity
        except Exception:
            continue

    sentiment_label = "Positive" if sentiment_score > 0.2 else "Negative" if sentiment_score < -0.2 else "Neutral"
    return sentiment_score, sentiment_label, headlines[:5]

try:
    df = fetch_data()
    st.subheader("📊 Raw Data Snapshot")
    st.write(df.tail())
    st.text(f"✅ Rows: {len(df)} | Columns: {list(df.columns)} | Interval: {INTERVAL}")

    sentiment_score, sentiment_label, news = fetch_news_sentiment()
    st.subheader("🗞️ News Sentiment")
    st.text(f"Sentiment Score: {sentiment_score:.2f} — {sentiment_label}")
    for headline in news:
        st.write(f"• {headline}")

    df = add_indicators(df).dropna()
    st.text(f"✅ With indicators: {len(df)}")

    if df.empty:
        st.warning("⚠️ Not enough data.")
    else:
        signal = generate_signal(df, sentiment_score)
        st.metric("Current Price", f"£{df.iloc[-1]['Close']:.2f}")
        st.metric("Signal", signal)

        fig1, ax1 = plt.subplots(figsize=(12, 4))
        ax1.plot(df.index, df['Close'], label="Price")
        ax1.plot(df.index, df['50_MA'], label="50 MA", linestyle="--")
        ax1.plot(df.index, df['200_MA'], label="200 MA", linestyle="--")
        ax1.legend()
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(12, 3))
        ax2.plot(df.index, df['MACD'], label="MACD")
        ax2.plot(df.index, df['Signal_Line'], label="Signal", linestyle="--")
        ax2.legend()
        st.pyplot(fig2)

        fig3, ax3 = plt.subplots(figsize=(12, 2))
        ax3.plot(df.index, df['RSI'], label="RSI", color='purple')
        ax3.axhline(70, color='red', linestyle='--')
        ax3.axhline(30, color='green', linestyle='--')
        ax3.legend()
        st.pyplot(fig3)

except Exception as e:
    st.error(f"❌ Error: {e}")