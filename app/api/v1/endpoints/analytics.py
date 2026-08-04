from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analytics import MarketAnalysisRequest, MarketAnalysisResponse
from app.services.analytics import AnalyticsService, get_analytics_service
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.db_services import save_prediction_history, get_user_predictions

router = APIRouter()


@router.post(
    "/analyze", 
    response_model=MarketAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Run stock trend prediction analysis"
)
async def analyze_market(
    payload: MarketAnalysisRequest,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Runs market prediction and saves the output to the database.
    Supports US equities, Indian stocks (.NS/.BO), and Forex pairs (=X).
    """
    ticker_clean = payload.ticker.upper().strip()

    if ticker_clean == "INVALID":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker symbol '{payload.ticker}' is not recognized or active."
        )

    response = await analytics_service.predict_trend(payload)

    # Save prediction history to database asynchronously
    await save_prediction_history(
        db=db,
        user_id=current_user.id,
        ticker=response.ticker,
        predicted_trend=response.predicted_trend,
        confidence_score=response.confidence_score
    )

    return response


@router.get(
    "/chart",
    summary="Get historical price candles for charts"
)
async def get_chart_candles(
    ticker: str = Query(..., description="Ticker symbol (e.g., RELIANCE.NS, USDINR=X, AAPL)"),
    period: str = Query("1mo", description="Historical period (e.g., 1mo, 3mo, 6mo, 1y)"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> List[Dict[str, Any]]:
    """
    Returns candlestick OHLC data formatted for TradingView Lightweight Charts rendering.
    """
    chart_data = await analytics_service.get_chart_data(ticker=ticker, period=period)

    if not chart_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price data found for ticker '{ticker}' over period '{period}'."
        )

    return chart_data


@router.get(
    "/history",
    summary="Get user prediction history"
)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the authenticated user's prediction history from the database.
    """
    history = await get_user_predictions(db, user_id=current_user.id)
    return history
