import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

st.set_page_config(page_title="IUSA Debug — Deep", layout="wide")
st.title("🧪 IUSA Deep Diagnostic — Column Shape Debugging")

TICKER = 'IUSA.L'
PERIOD = '1y'
INTERVAL = '1d'

def fetch_data():
    df = yf.download(TICKER, period=PERIOD, interval=INTERVAL)
    df.dropna(inplace=True)
    return df

def flatten_series(col):
    if isinstance(col, pd.Series):
        return pd.Series(np.ravel(col.values), index=col.index)
    return pd.Series(np.ravel(col), index=col.index)

try:
    df = fetch_data()
    st.subheader("📊 Raw Data")
    st.write(df.tail())

    # Add and flatten indicators
    df['RSI'] = flatten_series(ta.momentum.RSIIndicator(close=df['Close']).rsi())
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = flatten_series(macd.macd())
    df['Signal_Line'] = flatten_series(macd.macd_signal())
    df['50_MA'] = flatten_series(df['Close'].rolling(window=50).mean())
    df['200_MA'] = flatten_series(df['Close'].rolling(window=200).mean())

    # Drop NaNs
    df.dropna(inplace=True)

    st.subheader("🔬 Column Diagnostics")
    for col in ['RSI', 'MACD', 'Signal_Line', '50_MA', '200_MA']:
        st.write(f"**{col}**")
        st.code(f"Shape: {df[col].shape}, Type of first element: {type(df[col].values[0])}, Dtype: {df[col].dtype}")
        if isinstance(df[col].values[0], (np.ndarray, list)):
            st.error(f"⚠️ {col} still contains array-like values!")

    st.success("✅ All columns flattened. No plotting attempted.")

except Exception as e:
    st.error(f"❌ Debug Error: {e}")