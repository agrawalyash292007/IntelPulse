import os
import joblib
import traceback
import pandas as pd
from typing import Dict, Any

from app.schemas.analytics import MarketAnalysisRequest, MarketAnalysisResponse
from app.ml.features import fetch_stock_data, calculate_technical_indicators
from app.ml.sentiment import get_news_sentiment

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "model.joblib")


class AnalyticsService:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = None

    async def predict_trend(self, payload: MarketAnalysisRequest) -> MarketAnalysisResponse:
        ticker = payload.ticker.upper()
        days = getattr(payload, "days", 30)

        try:
            # Fix 1: Use valid yfinance period '6mo'
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

            # Fix 2: Match exact field names expected by MarketAnalysisResponse schema
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


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()