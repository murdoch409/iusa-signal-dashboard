
import streamlit as st
import pandas as pd
import yfinance as yf
from ta.trend import MACD, SMAIndicator

st.set_page_config(layout="wide")
st.title("📈 IUSA Buy/Hold/Sell Signal — MACD Fix")

ticker = "IUSA.L"
interval = st.selectbox("Select interval", ["1d", "1wk", "1mo"], index=0)
df = yf.download(ticker, period="6mo", interval=interval)

if df.empty:
    st.error("No data found.")
    st.stop()

df.dropna(inplace=True)

# Flatten column names if they are tuples (MultiIndex)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = ['_'.join([str(c) for c in col]).strip() for col in df.columns]
else:
    df.columns = [str(col).strip() for col in df.columns]

st.subheader("📊 Raw Data Snapshot")
st.dataframe(df.tail())

# Add indicators
try:
    df["50_MA"] = SMAIndicator(close=df["Close"], window=50).sma_indicator()
    macd = MACD(close=df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()

    st.success("✅ Indicators added")
except Exception as e:
    st.warning(f"⚠️ MACD Error: {e}")

# Signal logic (simplified)
try:
    latest_macd = df["MACD"].iloc[-1]
    latest_signal = df["MACD_Signal"].iloc[-1]
    signal = "BUY" if latest_macd > latest_signal else "SELL" if latest_macd < latest_signal else "HOLD"
    st.subheader("Signal")
    st.markdown(f"**{signal}**")
except:
    st.error("❌ Could not determine signal")

# Show current price
current_price = df["Close"].iloc[-1]
st.metric("Current Price", f"£{current_price:,.2f}")

# Optional: plot
import matplotlib.pyplot as plt

try:
    fig, ax = plt.subplots()
    df["Close"].plot(ax=ax, label="Price")
    df["50_MA"].plot(ax=ax, label="50 MA")
    ax.legend()
    st.pyplot(fig)
except:
    st.warning("⚠️ Chart could not be rendered.")
