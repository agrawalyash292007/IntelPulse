from fastapi import APIRouter, HTTPException, status
from app.schemas.analytics import MarketAnalysisRequest, MarketAnalysisResponse

router = APIRouter()

@router.post(
    "/analyze", 
    response_model=MarketAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Run stock trend prediction analysis"
)
async def analyze_market(payload: MarketAnalysisRequest):
    """
    Simulates non-blocking market analysis for a given stock ticker.
    """
    ticker_clean = payload.ticker.upper()
    
    # Simple mock error handling
    if ticker_clean == "INVALID":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker symbol '{payload.ticker}' is not recognized or active."
        )

    # Mock response data matching our MarketAnalysisResponse schema
    return MarketAnalysisResponse(
        ticker=ticker_clean,
        status="success",
        predicted_trend="BULLISH",
        confidence_score=0.87,
        key_indicators=["RSI_OVERSOLD", "VOLUME_SPIKE"],
        timeframe_days=payload.timeframe_days
    )