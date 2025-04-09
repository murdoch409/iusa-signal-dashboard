import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

st.set_page_config(page_title="IUSA Debug Mode", layout="wide")
st.title("📈 IUSA Diagnostic Mode — Debugging Shape Error")

TICKER = 'IUSA.L'
PERIOD = '1y'
INTERVAL = '1d'

def fetch_data():
    df = yf.download(TICKER, period=PERIOD, interval=INTERVAL)
    df.dropna(inplace=True)
    return df

def add_indicators(df):
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close']).rsi()
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['Signal_Line'] = macd.macd_signal()
    df['50_MA'] = df['Close'].rolling(window=50).mean()
    df['200_MA'] = df['Close'].rolling(window=200).mean()
    return df

try:
    df = fetch_data()
    st.subheader("Raw Data")
    st.write(df.tail())

    df = add_indicators(df).dropna()
    st.text(f"✅ Rows after indicator calculation: {len(df)}")

    # Display the shape of all relevant columns
    st.subheader("🧪 Column Shapes")
    for col in ['Close', 'RSI', 'MACD', 'Signal_Line', '50_MA', '200_MA']:
        st.write(f"{col}: {df[col].shape} | dtype: {df[col].dtype}")
        if isinstance(df[col].values[0], (np.ndarray, list)):
            st.error(f"⚠️ {col} contains array-like elements!")

    # Try plotting the first chart only
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df.index, df['Close'], label="Price")
    ax.plot(df.index, df['50_MA'], label="50 MA", linestyle="--")
    ax.plot(df.index, df['200_MA'], label="200 MA", linestyle="--")
    ax.legend()
    st.pyplot(fig)

except Exception as e:
    st.error(f"❌ Debug Error: {e}")