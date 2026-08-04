import os
import joblib
import traceback
import pandas as pd
from typing import Dict, Any, List

from app.schemas.analytics import MarketAnalysisRequest, MarketAnalysisResponse
from app.ml.features import fetch_stock_data, calculate_technical_indicators
from app.ml.sentiment import get_news_sentiment

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "model.joblib")


def format_ticker_symbol(ticker: str) -> str:
    """
    Auto-formats incoming ticker symbols for yfinance compatibility.
    - Indian Stocks: Adds '.NS' if an Indian stock name is typed without suffix.
    - Forex Pairs: Appends '=X' for forex conversions (e.g. USDINR -> USDINR=X).
    """
    symbol = ticker.strip().upper()

    # Forex handling (e.g., USDINR, EURUSD, GBPINR)
    forex_pairs = {"USDINR", "EURUSD", "GBPUSD", "USDJPY", "EURINR", "GBPINR"}
    if symbol in forex_pairs or (len(symbol) == 6 and not symbol.endswith(".NS") and not symbol.endswith(".BO")):
        if not symbol.endswith("=X"):
            return f"{symbol}=X"

    # Known Indian tickers without explicit extension
    indian_popular = {"RELIANCE", "TATAMOTORS", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC"}
    if symbol in indian_popular:
        return f"{symbol}.NS"

    return symbol


class AnalyticsService:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = None

    async def predict_trend(self, payload: MarketAnalysisRequest) -> MarketAnalysisResponse:
        # Format ticker for global assets / Indian equities / Forex
        raw_ticker = payload.ticker
        ticker = format_ticker_symbol(raw_ticker)
        days = payload.timeframe_days

        try:
            # Fetch data with standard 6mo window
            df = fetch_stock_data(ticker, period="6mo")
            df = calculate_technical_indicators(df)

            latest_features = df[["SMA_Signal", "RSI_14", "Volatility_20"]].iloc[-1:]
            sentiment_score = get_news_sentiment(ticker)

            if self.model:
                prediction_prob = self.model.predict_proba(latest_features)[0]
                bullish_prob = float(prediction_prob[1])
                adjusted_prob = max(0.0, min(1.0, bullish_prob + (sentiment_score * 0.1)))

                if adjusted_prob >= 0.52:
                    predicted_trend = "BULLISH"
                    confidence = adjusted_prob
                elif adjusted_prob <= 0.48:
                    predicted_trend = "BEARISH"
                    confidence = 1.0 - adjusted_prob
                else:
                    predicted_trend = "NEUTRAL"
                    confidence = 0.50
            else:
                predicted_trend = "NEUTRAL"
                confidence = 0.50

            latest_rsi = float(df["RSI_14"].iloc[-1])
            latest_sma_sig = "BULLISH_CROSS" if df["SMA_Signal"].iloc[-1] == 1 else "BEARISH_CROSS"

            return MarketAnalysisResponse(
                ticker=ticker,
                status="success",
                timeframe_days=days,
                predicted_trend=predicted_trend,
                confidence_score=round(confidence, 4),
                key_indicators={
                    "rsi_14": round(latest_rsi, 2),
                    "sma_signal": latest_sma_sig,
                    "news_sentiment_score": round(sentiment_score, 4)
                },
                analysis_timestamp=pd.Timestamp.now().isoformat()
            )

        except Exception as e:
            print("--- Analytics Prediction Exception Traceback ---")
            traceback.print_exc()
            print("-----------------------------------------------")

            return MarketAnalysisResponse(
                ticker=ticker,
                status="error",
                timeframe_days=days,
                predicted_trend="NEUTRAL",
                confidence_score=0.50,
                key_indicators={
                    "error": str(e),
                    "news_sentiment_score": 0.0
                },
                analysis_timestamp=pd.Timestamp.now().isoformat()
            )

    async def get_chart_data(self, ticker: str, period: str = "1mo") -> List[Dict[str, Any]]:
        """
        Fetches historical daily candle data (Open, High, Low, Close)
        formatted for TradingView Lightweight Charts rendering.
        """
        clean_ticker = format_ticker_symbol(ticker)
        df = fetch_stock_data(clean_ticker, period=period)

        if df.empty:
            return []

        chart_candles = []
        for index, row in df.iterrows():
            date_str = index.strftime("%Y-%m-%d") if isinstance(index, pd.Timestamp) else str(index)[:10]
            chart_candles.append({
                "time": date_str,
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
            })

        return chart_candles


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()
