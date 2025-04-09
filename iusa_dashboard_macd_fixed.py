
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from ta.trend import MACD
from ta.trend import SMAIndicator

# Load and prepare data
ticker = 'IUSA.L'
df = yf.download(ticker, period='6mo', interval='1d')
df.dropna(inplace=True)
df.columns = [col.strip() for col in df.columns]

# Add indicators
try:
    df['50_MA'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
    df['MACD'] = MACD(close=df['Close'].squeeze()).macd()  # Fix applied here
    indicator_success = True
except Exception as e:
    indicator_success = False
    macd_error = str(e)

# Streamlit display
st.title("IUSA Buy/Hold/Sell Signal — MACD Fixed")

st.subheader("📊 Raw Data Snapshot")
st.write(df.tail())

if indicator_success:
    st.success("Indicators added successfully.")
    st.line_chart(df[['Close', '50_MA']])
    st.line_chart(df[['MACD']])
else:
    st.warning(f"MACD Error: {macd_error}")
