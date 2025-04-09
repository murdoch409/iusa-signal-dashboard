
import pandas as pd
import yfinance as yf
import ta
import streamlit as st

# Load data
df = yf.download("IUSA.L", period="6mo", interval="1d")

# Ensure proper formatting
df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
df.dropna(inplace=True)

# Clean column names
df.columns = [col.strip() for col in df.columns]

# Add indicators
try:
    df['50_MA'] = ta.trend.sma_indicator(df['Close'])
except Exception as e:
    st.warning(f"50 MA Error: {e}")

try:
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.squeeze()
    df['MACD'] = ta.trend.macd(close_series)
except Exception as e:
    st.warning(f"MACD Error: {e}")

# Display
st.title("MACD Fix Test")
st.dataframe(df.tail(10))
