import yfinance as yf
import pandas as pd
import numpy as np


def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetches historical daily market data safely using yfinance."""
    df = yf.download(ticker, period=period, progress=False)
    if df.empty:
        raise ValueError(f"No market data found for ticker: {ticker}")
    
    # Flatten MultiIndex columns if present (common in recent yfinance versions)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    return df


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates RSI, Moving Average Crossovers, and Volatility indicators safely."""
    df = df.copy()

    # Ensure Close column is 1D Series
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    # 1. Simple Moving Averages (20-day vs 50-day)
    df["SMA_20"] = close.rolling(window=20).mean()
    df["SMA_50"] = close.rolling(window=50).mean()
    df["SMA_Signal"] = np.where(df["SMA_20"] > df["SMA_50"], 1, -1)

    # 2. Relative Strength Index (RSI - 14 Days)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df["RSI_14"] = 100 - (100 / (1 + rs))

    # 3. Daily Returns & Volatility (20-day standard deviation)
    df["Daily_Return"] = close.pct_change()
    df["Volatility_20"] = df["Daily_Return"].rolling(window=20).std()

    # Target variable
    df["Target"] = np.where(close.shift(-1) > close, 1, 0)

    # Drop incomplete rows from rolling calculations
    df.dropna(inplace=True)
    return df