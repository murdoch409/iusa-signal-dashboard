
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf
from ta.trend import MACD, SMAIndicator
from ta.momentum import RSIIndicator
from textblob import TextBlob

# Load data
ticker = "IUSA.L"
interval = "1d"
period = "6mo"

df = yf.download(ticker, period=period, interval=interval)
df.dropna(inplace=True)

# Clean columns
df.columns = [col.strip() for col in df.columns]

# Add indicators safely
indicators_added = []
if 'Close' in df.columns and len(df) >= 50:
    try:
        df['50_MA'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
        indicators_added.append('50 MA')
    except Exception:
        pass

if 'Close' in df.columns and len(df) >= 200:
    try:
        df['200_MA'] = SMAIndicator(close=df['Close'], window=200).sma_indicator()
        indicators_added.append('200 MA')
    except Exception:
        pass

if 'Close' in df.columns and len(df) >= 30:
    try:
        df['MACD'] = MACD(close=df['Close']).macd()
        df['Signal'] = MACD(close=df['Close']).macd_signal()
        indicators_added.append('MACD')
    except Exception:
        pass

if 'Close' in df.columns and len(df) >= 14:
    try:
        df['RSI'] = RSIIndicator(close=df['Close']).rsi()
        indicators_added.append('RSI')
    except Exception:
        pass

# UI
st.title("IUSA Buy/Hold/Sell Signal — Ultimate")
st.subheader("Raw Data Snapshot")
st.dataframe(df.tail())

# Show indicators
st.markdown(f"✅ Rows: {len(df)}")
st.markdown(f"✅ With indicators: {len(indicators_added)} — {', '.join(indicators_added) if indicators_added else 'None'}")

# Current price
if 'Close' in df.columns:
    current_price = df['Close'].iloc[-1]
    st.subheader("Current Price")
    st.metric("£", f"{current_price:,.2f}")

# Signal logic
signal = "Hold"
if '50_MA' in df.columns and '200_MA' in df.columns:
    if df['50_MA'].iloc[-1] > df['200_MA'].iloc[-1]:
        signal = "Buy"
    elif df['50_MA'].iloc[-1] < df['200_MA'].iloc[-1]:
        signal = "Sell"
st.subheader("Signal")
st.write(signal)

# Candlestick chart
st.subheader("Candlestick Chart")
mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
s = mpf.make_mpf_style(marketcolors=mc)
mpf.plot(df[-60:], type='candle', style=s, volume=True, mav=(50,200), show_nontrading=False)

# News Sentiment (placeholder headlines)
news_data = [
    {"headline": "IUSA stock underperforms amid market uncertainty", "source": "Reuters"},
    {"headline": "Investors eye upcoming Fed decision", "source": "Bloomberg"},
    {"headline": "ETF flows signal shift in market sentiment", "source": "CNBC"}
]
sentiment_score = 0
for item in news_data:
    blob = TextBlob(item['headline'])
    sentiment_score += blob.sentiment.polarity

overall_sentiment = sentiment_score / len(news_data)
sentiment_label = "Neutral"
if overall_sentiment > 0.1:
    sentiment_label = "Positive"
elif overall_sentiment < -0.1:
    sentiment_label = "Negative"

st.subheader("News Sentiment")
st.write(f"Sentiment Score: {overall_sentiment:.2f} — {sentiment_label}")
for item in news_data:
    st.markdown(f"- *{item['headline']}* — **{item['source']}**")

# Zacks rating placeholder
st.subheader("Zacks Rating")
st.write("Zacks Rating for IUSA: **Hold** (placeholder)")
