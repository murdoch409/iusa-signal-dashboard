
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
from textblob import TextBlob
from bs4 import BeautifulSoup
import requests
import re
import pytz
import matplotlib.pyplot as plt
import streamlit as st

# CONFIG
TICKER = 'IUSA.L'
INTERVAL = '1h'
TRIGGER_WORDS = ['recession', 'inflation', 'rate hike', 'crisis', 'strong earnings', 'bull market', 'bear market', 'volatility']
NEWS_URLS = [
    'https://www.bbc.com/news/business',
    'https://www.reuters.com/business',
    'https://www.cnbc.com/world/?region=world',
    'https://finance.yahoo.com',
    'https://www.ft.com/markets'
]

# Fetch Data
def fetch_data(ticker=TICKER, interval=INTERVAL, period='60d'):
    data = yf.download(ticker, period=period, interval=interval)
    data.dropna(inplace=True)
    if data.empty or 'Close' not in data.columns or data['Close'].dropna().empty:
        raise ValueError("Price data could not be loaded or is empty.")
    return data

# Add Indicators
def add_indicators(df):
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['Signal_Line'] = macd.macd_signal()
    df['50_MA'] = df['Close'].rolling(window=50).mean()
    df['200_MA'] = df['Close'].rolling(window=200).mean()
    return df.dropna(subset=['RSI', 'MACD', 'Signal_Line', '50_MA', '200_MA'])

# Generate Technical Signal
def generate_tech_signal(df):
    latest = df.iloc[-1]
    signal = 'Hold'
    if pd.notna(latest['RSI']) and pd.notna(latest['MACD']) and pd.notna(latest['Signal_Line']):
        if latest['RSI'] < 30 and latest['MACD'] > latest['Signal_Line']:
            signal = 'Buy'
        elif latest['RSI'] > 70 and latest['MACD'] < latest['Signal_Line']:
            signal = 'Sell'
        elif latest['50_MA'] > latest['200_MA']:
            signal = 'Buy (Momentum)'
    return signal

# News Sentiment Scraper
def get_news_sentiment():
    headers = {'User-Agent': 'Mozilla/5.0'}
    sentiment_score = 0
    trigger_hits = 0
    headlines_checked = 0
    for url in NEWS_URLS:
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            headlines = soup.find_all(['h1', 'h2', 'h3'])
            for tag in headlines[:5]:
                text = tag.get_text()
                blob = TextBlob(text)
                sentiment_score += blob.sentiment.polarity
                headlines_checked += 1
                if any(re.search(rf'\b{word}\b', text.lower()) for word in TRIGGER_WORDS):
                    trigger_hits += 1
        except Exception:
            continue
    if headlines_checked == 0:
        return 0, 0
    return sentiment_score / headlines_checked, trigger_hits

# Final Decision
def final_signal(tech_signal, news_score, trigger_count):
    if tech_signal.startswith('Buy') and news_score > 0 and trigger_count == 0:
        return 'BUY'
    elif tech_signal == 'Sell' or news_score < -0.2 or trigger_count >= 2:
        return 'SELL'
    else:
        return 'HOLD'

# Streamlit Dashboard
st.set_page_config(page_title='IUSA Signal Dashboard', layout='wide')
st.title('IUSA Buy/Hold/Sell Signal')

try:
    with st.spinner('Fetching data and calculating...'):
        df = fetch_data()
        df = add_indicators(df)
        if df.empty:
            st.warning("Not enough data to calculate indicators. Try changing interval or period.")
        else:
            tech = generate_tech_signal(df)
            news_score, triggers = get_news_sentiment()
            action = final_signal(tech, news_score, triggers)
            latest = df.iloc[-1]

            st.metric("Current Price", f"£{latest['Close']:.2f}")
            st.metric("Signal", action)
            st.metric("News Score", f"{news_score:.2f}", help=">0 = Positive; <0 = Negative")

            # Plot Price with MAs
            if all(col in df.columns for col in ['Close', '50_MA', '200_MA']):
                fig, ax = plt.subplots(figsize=(14, 6))
                ax.plot(df.index, df['Close'], label='Price')
                ax.plot(df.index, df['50_MA'], label='50 MA', linestyle='--')
                ax.plot(df.index, df['200_MA'], label='200 MA', linestyle='--')
                ax.set_title('IUSA Price with Moving Averages')
                ax.legend()
                st.pyplot(fig)

            # Plot MACD
            if all(col in df.columns for col in ['MACD', 'Signal_Line']):
                fig2, ax2 = plt.subplots(figsize=(14, 4))
                ax2.plot(df.index, df['MACD'], label='MACD')
                ax2.plot(df.index, df['Signal_Line'], label='Signal Line')
                ax2.set_title('MACD Indicator')
                ax2.legend()
                st.pyplot(fig2)

            # Plot RSI
            if 'RSI' in df.columns:
                fig3, ax3 = plt.subplots(figsize=(14, 2))
                ax3.plot(df.index, df['RSI'], label='RSI', color='purple')
                ax3.axhline(70, color='red', linestyle='--')
                ax3.axhline(30, color='green', linestyle='--')
                ax3.set_title('RSI Indicator')
                ax3.legend()
                st.pyplot(fig3)

            st.success("Dashboard updated successfully!")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
