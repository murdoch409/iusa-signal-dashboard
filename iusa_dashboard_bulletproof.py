import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt
import streamlit as st

# Settings
TICKER = 'IUSA.L'
INTERVAL = '1d'
PERIOD = '1y'

# Fetch data
def fetch_data():
    data = yf.download(TICKER, period=PERIOD, interval=INTERVAL)
    data.dropna(inplace=True)
    return data

# Add indicators
def add_indicators(df):
    df['RSI'] = pd.Series(ta.momentum.RSIIndicator(close=df['Close']).rsi(), index=df.index)
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = pd.Series(macd.macd(), index=df.index)
    df['Signal_Line'] = pd.Series(macd.macd_signal(), index=df.index)
    df['50_MA'] = pd.Series(df['Close'].rolling(window=50).mean(), index=df.index)
    df['200_MA'] = pd.Series(df['Close'].rolling(window=200).mean(), index=df.index)
    return df

# Generate signal
def generate_signal(df):
    latest = df.iloc[-1]
    if latest['RSI'] < 30 and latest['MACD'] > latest['Signal_Line']:
        return 'BUY'
    elif latest['RSI'] > 70 and latest['MACD'] < latest['Signal_Line']:
        return 'SELL'
    return 'HOLD'

# Streamlit app
st.set_page_config(page_title="IUSA Signal Bulletproof", layout="wide")
st.title("📈 IUSA Buy/Hold/Sell Signal — Bulletproof Version")

try:
    df = fetch_data()
    st.subheader("📊 Raw Data Snapshot")
    st.write(df.tail())
    st.text(f"✅ Raw data rows: {len(df)}")

    df = add_indicators(df).dropna()
    st.text(f"✅ Cleaned rows with indicators: {len(df)}")

    if df.empty:
        st.warning("Not enough data after applying indicators.")
    else:
        signal = generate_signal(df)
        latest = df.iloc[-1]
        st.metric("Current Price", f"£{latest['Close']:.2f}")
        st.metric("Signal", signal)

        # Price + MA
        fig1, ax1 = plt.subplots(figsize=(12, 4))
        ax1.plot(df.index, df['Close'], label="Price")
        ax1.plot(df.index, df['50_MA'], label="50 MA", linestyle="--")
        ax1.plot(df.index, df['200_MA'], label="200 MA", linestyle="--")
        ax1.legend()
        st.pyplot(fig1)

        # MACD
        fig2, ax2 = plt.subplots(figsize=(12, 3))
        ax2.plot(df.index, df['MACD'], label="MACD")
        ax2.plot(df.index, df['Signal_Line'], label="Signal", linestyle="--")
        ax2.legend()
        st.pyplot(fig2)

        # RSI
        fig3, ax3 = plt.subplots(figsize=(12, 2))
        ax3.plot(df.index, df['RSI'], label="RSI", color='purple')
        ax3.axhline(70, color='red', linestyle='--')
        ax3.axhline(30, color='green', linestyle='--')
        ax3.legend()
        st.pyplot(fig3)

except Exception as e:
    st.error(f"❌ Error: {e}")