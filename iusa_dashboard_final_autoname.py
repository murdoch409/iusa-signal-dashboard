import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

st.set_page_config(page_title="IUSA AutoFix", layout="wide")
st.title("📈 IUSA Buy/Hold/Sell Signal — Final AutoFix")

TICKER = 'IUSA.L'
PERIOD = '1y'
INTERVAL = '1d'

def fetch_data():
    df = yf.download(TICKER, period=PERIOD, interval=INTERVAL, group_by="column")
    # Flatten any multi-level index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(1)
    df.columns = [str(c) for c in df.columns]

    # Handle duplicate column names
    if len(set(df.columns)) < len(df.columns):
        df.columns = [f"{col}_{i}" for i, col in enumerate(df.columns)]

    df.dropna(inplace=True)
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

def generate_signal(df):
    latest = df.iloc[-1]
    if latest['RSI'] < 30 and latest['MACD'] > latest['Signal_Line']:
        return 'BUY'
    elif latest['RSI'] > 70 and latest['MACD'] < latest['Signal_Line']:
        return 'SELL'
    return 'HOLD'

try:
    df = fetch_data()
    st.subheader("📊 Raw Data Snapshot")
    st.write(df.tail())
    st.text(f"✅ Raw rows: {len(df)} | Columns: {list(df.columns)}")

    df = add_indicators(df).dropna()
    st.text(f"✅ With indicators: {len(df)}")

    if df.empty:
        st.warning("⚠️ Not enough data for indicators.")
    else:
        signal = generate_signal(df)
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
    st.error(f"❌ Final Error: {e}")