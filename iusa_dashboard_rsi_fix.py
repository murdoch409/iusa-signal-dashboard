import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📈 IUSA Buy/Hold/Sell — RSI Fix Edition")

TICKER = "IUSA.L"
INTERVAL = "1d"
PERIOD = "6mo"

# Load data
df = yf.download(TICKER, period=PERIOD, interval=INTERVAL)
df.dropna(inplace=True)

# Ensure single level column names
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[-1] if isinstance(col, tuple) else col for col in df.columns]

# Show snapshot
st.subheader("Raw Data")
st.dataframe(df.tail())

# Fix RSI input shape
try:
    close_series = df["Close"]
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    elif close_series.ndim > 1:
        close_series = close_series.squeeze()
    df["RSI"] = ta.momentum.RSIIndicator(close=close_series).rsi()
    st.success("RSI calculated successfully.")
except Exception as e:
    st.error(f"Failed to compute RSI: {e}")

# Plot Close and RSI
if "RSI" in df.columns:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    df["Close"].plot(ax=ax1, title="Close Price")
    df["RSI"].plot(ax=ax2, title="RSI")
    st.pyplot(fig)