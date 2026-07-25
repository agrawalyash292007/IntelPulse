from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
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
    """
    ticker_clean = payload.ticker.upper()

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